"""Memory layer: store sessions, retrieve similar solved problems."""
import json
import uuid
from pathlib import Path
from typing import Optional

from app.config import MEMORY_DB_PATH, DATA_DIR
from app.embeddings import embed_query

DATA_DIR.mkdir(exist_ok=True)
MEMORY_PATH = MEMORY_DB_PATH
MEMORY_EMBEDDINGS_PATH = DATA_DIR / "memory_embeddings.json"


def _load_memory_lines() -> list[dict]:
    if not MEMORY_PATH.exists():
        return []
    lines = []
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    lines.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return lines


def _append_memory(record: dict) -> None:
    with open(MEMORY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def store(
    input_type: str,
    raw_input: str,
    parsed_question: dict,
    retrieved_context: list[dict],
    final_answer: str,
    steps: str,
    verifier_outcome: dict,
    user_feedback: Optional[str] = None,
    user_comment: Optional[str] = None,
    corrected_answer: Optional[str] = None,
) -> str:
    record_id = str(uuid.uuid4())
    record = {
        "id": record_id,
        "input_type": input_type,
        "raw_input": raw_input[:2000],
        "parsed_question": parsed_question,
        "retrieved_context": [{"source": c.get("source"), "content": (c.get("content") or "")[:500]} for c in retrieved_context],
        "final_answer": final_answer,
        "steps": steps[:3000],
        "verifier_outcome": verifier_outcome,
        "user_feedback": user_feedback,
        "user_comment": user_comment,
        "corrected_answer": corrected_answer,
    }
    _append_memory(record)
    try:
        q = f"{parsed_question.get('problem_text', '')} {final_answer}"
        emb = embed_query(q)
        idx = {"id": record_id, "embedding": emb}
        with open(MEMORY_EMBEDDINGS_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(idx, ensure_ascii=False) + "\n")
    except Exception:
        pass
    return record_id


MIN_SIMILARITY_THRESHOLD = 0.55


def retrieve_similar(problem_text: str, top_k: int = 3, min_similarity: float = MIN_SIMILARITY_THRESHOLD) -> list[dict]:
    """Return past sessions whose embedding similarity to problem_text is >= min_similarity. Avoids showing 'similar' for unrelated queries."""
    mem_lines = _load_memory_lines()
    if not mem_lines:
        return []
    try:
        embs = []
        ids = []
        if MEMORY_EMBEDDINGS_PATH.exists():
            with open(MEMORY_EMBEDDINGS_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        obj = json.loads(line)
                        ids.append(obj["id"])
                        embs.append(obj["embedding"])
        if not embs or not ids:
            return []
        q_emb = embed_query(problem_text)
        scores = []
        for i, e in enumerate(embs):
            dot = sum(a * b for a, b in zip(q_emb, e))
            norm_q = sum(x * x for x in q_emb) ** 0.5
            norm_e = sum(x * x for x in e) ** 0.5
            if norm_q and norm_e:
                sim = dot / (norm_q * norm_e)
                scores.append((ids[i], sim))
            else:
                scores.append((ids[i], 0))
        scores.sort(key=lambda x: -x[1])
        top_ids = [s[0] for s in scores[:top_k] if s[1] >= min_similarity]
        by_id = {r["id"]: r for r in mem_lines}
        return [by_id[i] for i in top_ids if i in by_id]
    except Exception:
        return []


def get_correction_rules(limit: int = 20) -> list[dict]:
    """Past cases where user said incorrect and gave correction. Used at runtime to apply known OCR/audio correction rules and avoid repeating mistakes. No retraining — pattern reuse only."""
    mem_lines = _load_memory_lines()
    rules = []
    for r in mem_lines:
        if r.get("user_feedback") == "incorrect" and (r.get("user_comment") or r.get("corrected_answer")):
            rules.append({
                "problem_snippet": (r.get("parsed_question") or {}).get("problem_text", "")[:200],
                "original_answer": r.get("final_answer", ""),
                "corrected_answer": r.get("corrected_answer"),
                "user_comment": r.get("user_comment"),
                "input_type": r.get("input_type", "text"),
            })
    return rules[-limit:]
