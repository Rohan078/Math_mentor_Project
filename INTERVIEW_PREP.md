# Math Mentor – Interview Preparation Guide

Use this to explain the project, architecture, workflow, and complex code in interviews.

---

## 1. What the Project Does (Elevator Pitch)

**Math Mentor** is a **JEE-style math tutoring app** that:

- Accepts **three input modes**: typed text, uploaded image (OCR), or audio (ASR).
- Runs a **RAG (Retrieval-Augmented Generation)** pipeline over a curated math knowledge base (Algebra, Probability, Calculus, Linear Algebra).
- Uses a **multi-agent pipeline**: Parser → Intent Router → Solver → Verifier → Explainer.
- Supports **Human-in-the-Loop (HITL)** when confidence is low (OCR/ASR, parser ambiguity, or verifier).
- Stores **memory** of solved problems and user feedback (correct/incorrect + corrections) for similar-problem retrieval.

**Tech stack:** Streamlit UI, Groq LLM (chat + embeddings + vision), ChromaDB for RAG, EasyOCR + Whisper for multimodal, Pydantic for structured outputs.

---

## 2. High-Level Architecture & Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INPUT LAYER                                    │
│  Text (direct) │ Image (OCR: Vision LLM → EasyOCR → LLM fix) │ Audio (Whisper)│
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  EXTRACTION PREVIEW + HITL CHECK (low OCR/ASR confidence → ask user to edit) │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PARSER AGENT (LLM) → ParsedProblem: problem_text, topic, variables,          │
│  constraints, needs_clarification → HITL if ambiguous                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  MEMORY (optional): retrieve_similar(problem_text) → past solutions for hint  │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  INTENT ROUTER (LLM) → intent (algebra/probability/calculus/linear_algebra),  │
│  strategy (e.g. "Use quadratic formula")                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SOLVER AGENT: RAG retrieve(problem_text) → top-k chunks from ChromaDB       │
│  → LLM with context + optional CALC: <expr> → _safe_python_calc              │
│  → SolverResult (answer, steps, context_used)                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  VERIFIER AGENT (LLM) → correctness, confidence, issues, hitl_required       │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  EXPLAINER AGENT (LLM) → student-friendly step-by-step explanation           │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  UI: show trace, RAG sources, answer, confidence, explanation, feedback      │
│  FEEDBACK: Correct / Incorrect → store() in memory (memory.jsonl + embeddings)│
└─────────────────────────────────────────────────────────────────────────────┘
```

**Data flow in one sentence:** Raw input → multimodal extraction → parsed problem → (optional similar memory) → intent → RAG + solver → verification → explanation → display and feedback storage.

---

## 3. What Works, How, and Why

### 3.1 Multimodal Input

| Mode   | How it works | Why this design |
|--------|--------------|------------------|
| **Text** | User types; no processing. | Direct path; no noise. |
| **Image** | 1) Try **Groq Vision** first (good at math symbols Σ, √, ∫). 2) If none/empty, **EasyOCR** (English). 3) If OCR garbles math, **LLM fix** prompt to reconstruct notation. Confidence: 0.9 for vision, else mean of EasyOCR per-word confidences. | Vision handles symbols; EasyOCR is fallback; LLM fixes OCR output. |
| **Audio** | **Whisper** (base model) on WAV; optional resampling to 16 kHz. Confidence proxy from presence of segments + text length. **Phrase normalization**: "square root of" → sqrt, "squared" → ^2, etc. | Whisper is robust; normalization helps downstream parser/solver. |

**Interview point:** "We use a vision model first for images because math notation (roots, integrals, summations) is hard for traditional OCR; we only fall back to EasyOCR when vision isn’t available or fails."

### 3.2 RAG Pipeline

- **Indexing (`build_rag.py` / `app/rag.py`):** All `.md`/`.txt` under `knowledge_base/` are loaded, chunked with **overlapping sliding window** (chunk_size=512, overlap=64), embedded (Groq `nomic-embed-text-v1.5` or fallback `sentence-transformers`), stored in **ChromaDB** with metadata `source`, `chunk_id`.
- **Retrieval:** Query is embedded; Chroma returns **top-k** (default 5) by vector similarity. Results are passed to the solver as "Retrieved knowledge"; **sources are shown in the UI** so we don’t cite something we didn’t retrieve.
- **Why chunking with overlap:** Prevents cutting formulas in the middle; overlap keeps context across boundaries.
- **Why Chroma:** Persistent, in-process, no extra server; good for a single-user or small-team app.

**Interview point:** "RAG reduces hallucination by grounding the solver in our curated docs; we only show citations from actual retrieved chunks."

### 3.3 Agent Pipeline

| Agent | Input | Output | Role |
|-------|--------|--------|------|
| **Parser** | Raw text + source_hint (text/ocr/asr) | `ParsedProblem`: cleaned problem_text, topic, variables, constraints, needs_clarification | Normalize and structure; detect ambiguity. |
| **Router** | ParsedProblem | IntentResult: intent, strategy, reasoning | Classify and pick solution strategy. |
| **Solver** | ParsedProblem + IntentResult | SolverResult: answer, steps, context_used | RAG retrieve + LLM; optional CALC tool. |
| **Verifier** | ParsedProblem + SolverResult | VerificationResult: is_correct, confidence, issues, hitl_required | Sanity-check answer and flag low confidence. |
| **Explainer** | ParsedProblem + SolverResult | ExplainerResult: explanation | Turn steps into student-friendly explanation. |

**Why separate agents:** Single responsibility; we can swap models or add tools per stage; clear trace for debugging and for the UI ("Agent trace").

### 3.4 Human-in-the-Loop (HITL)

**Conditions (`app/hitl.py`):**

- User clicked "Request re-check".
- Parser set `needs_clarification`.
- OCR confidence < 0.6.
- ASR confidence < 0.7.
- Verifier confidence < 0.7 or `hitl_required=True`.

When triggered, the UI asks the user to confirm or edit the extracted text and run again; we don’t block the pipeline forever. Verifier can also set `hitl_required` for domain/units/edge cases.

**Interview point:** "HITL is used at input (OCR/ASR, ambiguity) and after verification so we don’t present high-stakes answers with low confidence without human review."

### 3.5 Memory

- **Storage:** On feedback (Correct / Incorrect), we call `store()`: append a JSON line to `data/memory.jsonl` (input, parsed question, context, answer, steps, verifier outcome, user_feedback, comment, corrected_answer). We also append an embedding of `problem_text + final_answer` to `memory_embeddings.json` (one JSON object per line: id, embedding).
- **Retrieval:** `retrieve_similar(problem_text, top_k)` loads memory lines and embedding file, computes **cosine similarity** (dot product / (norm_q * norm_e)) between query embedding and each stored embedding, returns top-k records. Used to show "similar past solutions" in the trace and could be used to inject hints (currently trace-only).
- **Why separate embeddings file:** Keeps memory.jsonl human-readable; embeddings are append-only and matched by id.

**Interview point:** "Memory gives us similar-problem retrieval and stores corrections for future use; we’re not retraining a model, just reusing patterns and correction rules."

---

## 4. Complex Code an Interviewer Might Ask About

### 4.1 RAG Chunking (`app/rag.py` – `_chunk_text`)

```python
def _chunk_text(text: str, chunk_size: int = RAG_CHUNK_SIZE, overlap: int = RAG_CHUNK_OVERLAP) -> List[str]:
    # ...
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if end < len(text):
            last_break = max(chunk.rfind("\n"), chunk.rfind(". "), chunk.rfind(" "))
            if last_break > chunk_size // 2:
                chunk = chunk[: last_break + 1]
                end = start + last_break + 1
        # ...
        start = end - overlap if end < len(text) else len(text)
```

**What it does:** Splits text into chunks of ~`chunk_size`. Prefers to break at newline, ". ", or space so we don’t cut mid-sentence. Next chunk starts at `end - overlap` so consecutive chunks overlap.

**Why:** Overlap avoids losing context at boundaries; breaking at sentence/paragraph boundaries keeps chunks coherent for embedding and retrieval.

---

### 4.2 Safe Python Calculator (`app/agents/solver.py` – `_safe_python_calc`)

```python
def _safe_python_calc(expr: str) -> str:
    allowed = set("0123456789.+-*/().%e ^")
    expr_clean = expr.replace("**", "^").replace(" ", "")
    for c in expr_clean:
        if c not in allowed and c not in "sqrtabsincoxptanlog":
            return ""
    safe = {"sqrt": math.sqrt, "sin": math.sin, ...}
    result = eval(expr_eval, {"__builtins__": {}}, safe)
```

**What it does:** Only allows a whitelist of characters and a fixed set of function names; runs `eval` with **no builtins** and only a small `safe` dict of math functions. So the LLM can output `CALC: 2**10` or `CALC: sqrt(2)` and we substitute the result.

**Why:** Prevents code injection (no `open`, `os`, `__import__`, etc.); gives the solver a way to compute numeric values without external APIs.

**Interview follow-up:** "How do you avoid injection?" → "We whitelist characters and symbol names and pass `__builtins__={}` and only a limited `safe` namespace to `eval`."

---

### 4.3 Parser: Structured Output from LLM (`app/agents/parser.py`)

The parser asks for **one JSON object** with fixed keys. It then:

- Strips markdown code fences (```) from the response.
- Uses `json.loads` and maps keys to `ParsedProblem` (Pydantic).
- Validates `topic` against allowed list; defaults to `"algebra"`.
- On any parse/validation error, returns a `ParsedProblem` with `needs_clarification=True` and `clarification_reason` set.

**Why:** Ensures a single, consistent structure for the rest of the pipeline; failure is handled by flagging clarification instead of crashing.

---

### 4.4 OCR: Vision First, Then EasyOCR + LLM Fix (`app/multimodal/ocr.py`)

- **Vision:** Image → base64 data URL → Groq vision model with a prompt that asks for exact math notation (Σ, √, ∫, ^, etc.). If we get non-empty text and it’s not "no math problem found", we return that with confidence 0.9.
- **EasyOCR:** If vision fails or no key: EasyOCR returns a list of (bbox, text, confidence); we concatenate text and average confidence.
- **LLM fix:** We send the OCR text with a prompt that says "this came from OCR, reconstruct the correct math expression" and return the corrected string (keeping the original OCR confidence).

**Interview point:** "We prefer vision for math images because it understands notation; EasyOCR is for when vision isn’t available; the LLM fix cleans OCR’s typical symbol errors."

---

### 4.5 Memory Similarity (`app/memory.py` – `retrieve_similar`)

We don’t use Chroma here. We load `memory.jsonl` and `memory_embeddings.json`, embed the query once, then **manually** compute cosine similarity:

```python
dot = sum(a * b for a, b in zip(q_emb, e))
norm_q = sum(x * x for x in q_emb) ** 0.5
norm_e = sum(x * x for x in e) ** 0.5
scores.append((ids[i], dot / (norm_q * norm_e)))
scores.sort(key=lambda x: -x[1])
```

**Why:** Memory is a separate store from the RAG index; keeping a simple, separate embedding list avoids coupling to Chroma and keeps the memory format transparent (JSONL + JSONL embeddings).

---

### 4.6 Verifier and HITL

Verifier uses an LLM to output four lines: `is_correct`, `confidence`, `issues`, `hitl_required`. We parse these and **force** `hitl_required=True` if `confidence < 0.7`. So even if the model forgets to set `hitl_required`, we still trigger HITL when confidence is low.

**Interview point:** "Verifier adds a second check on the solver’s answer and can request human review; we enforce a confidence threshold in code so HITL is consistent."

---

## 5. Configuration and Environment

- **`app/config.py`:** Paths (knowledge_base, data, Chroma, memory), `GROQ_API_KEY` (cleaned of quotes/non-printable), model names (chat, vision, embedding), RAG (top_k, chunk_size, overlap), OCR/ASR thresholds, Chroma collection name.
- **`.env`:** Only `GROQ_API_KEY` is required; optional overrides for chat/vision models.
- **Why Groq:** Fast inference, free tier; one provider for chat, embeddings, and vision simplifies setup.

---

## 6. Deployment Note

The app is **Streamlit (long-running server)**. README says it’s not suitable for Vercel (serverless); use **Streamlit Community Cloud** or **Hugging Face Spaces**. Secrets (e.g. `GROQ_API_KEY`) go in the platform’s secrets; main file is `streamlit_app.py`.

---

## 7. Quick Q&A for Interview

1. **What is RAG and why use it here?**  
   Retrieval-Augmented Generation: we retrieve relevant chunks from the knowledge base and pass them to the LLM so answers are grounded in our docs and we can show real sources.

2. **Why multiple agents instead of one big prompt?**  
   Separation of concerns (parse → route → solve → verify → explain), easier to debug and trace, and we can tune or replace one stage without rewriting everything.

3. **How do you handle low confidence?**  
   HITL: we trigger on low OCR/ASR confidence, parser ambiguity, or verifier confidence < 0.7; user can edit input or confirm before we treat the answer as final.

4. **How is memory used?**  
   We store each feedback (correct/incorrect + optional correction) with an embedding; we retrieve similar past problems by cosine similarity and show them in the trace (and could feed them as hints to the solver).

5. **How do you avoid hallucinated citations?**  
   We only show sources that were actually retrieved (from `context_used`); the solver prompt says "do not cite if not used."

6. **Why Vision first for images?**  
   Math notation (√, Σ, ∫, fractions, exponents) is hard for standard OCR; vision models understand layout and symbols better, so we use them first and fall back to EasyOCR + LLM fix when needed.

Use this doc to walk through the project and the code; it should cover most “how does it work?” and “why did you do it this way?” questions in an interview.
