"""Parser Agent: cleans OCR/ASR output and converts to structured problem."""
import json
import re
from typing import Optional

from pydantic import BaseModel

from app.llm import chat_json


class ParsedProblem(BaseModel):
    problem_text: str
    topic: str
    variables: list[str] = []
    constraints: list[str] = []
    needs_clarification: bool = False
    clarification_reason: Optional[str] = None


def parse_problem(raw_text: str, source_hint: str = "text") -> ParsedProblem:
    raw_text = (raw_text or "").strip()
    if not raw_text:
        return ParsedProblem(
            problem_text="",
            topic="algebra",
            variables=[],
            constraints=[],
            needs_clarification=True,
            clarification_reason="Empty input.",
        )

    prompt = f"""You are a math problem parser. Clean and structure the following math problem.
Input source hint: {source_hint}. If OCR/ASR, fix obvious typos and math symbols (e.g. "square root of" -> √, "raised to" -> ^).

Raw input:
---
{raw_text}
---

Output a single JSON object with exactly these keys (no markdown, no code block):
- "problem_text": cleaned, clear problem statement (string)
- "topic": one of "algebra", "probability", "calculus", "linear_algebra"
- "variables": list of variable names that appear (e.g. ["x", "n"])
- "constraints": list of constraints if any (e.g. ["x > 0", "n is natural number"])
- "needs_clarification": true only if the problem is ambiguous, has missing info, or is unreadable; otherwise false
- "clarification_reason": if needs_clarification is true, short reason; else null

Return only the JSON object, nothing else."""

    try:
        out = chat_json([{"role": "user", "content": prompt}])
        out = re.sub(r"^```\w*\n?", "", out).strip()
        out = re.sub(r"\n?```\s*$", "", out).strip()
        data = json.loads(out)
        topic = data.get("topic")
        if topic is None or not isinstance(topic, str):
            topic = "algebra"
        topic = topic.strip().lower()
        if topic not in ("algebra", "probability", "calculus", "linear_algebra"):
            topic = "algebra"
        problem_text = data.get("problem_text") or raw_text
        if not isinstance(problem_text, str):
            problem_text = str(problem_text) if problem_text else raw_text
        def _list(val):
            return list(val) if isinstance(val, list) else []

        return ParsedProblem(
            problem_text=problem_text,
            topic=topic,
            variables=_list(data.get("variables")),
            constraints=_list(data.get("constraints")),
            needs_clarification=bool(data.get("needs_clarification", False)),
            clarification_reason=data.get("clarification_reason"),
        )
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        return ParsedProblem(
            problem_text=raw_text,
            topic="algebra",
            variables=[],
            constraints=[],
            needs_clarification=True,
            clarification_reason=f"Parse failed: {e!s}",
        )
