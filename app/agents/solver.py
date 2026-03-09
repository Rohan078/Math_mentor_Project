"""Solver Agent: solves using RAG context and optional Python execution."""
import re
from typing import List, Optional

from app.agents.parser import ParsedProblem
from app.agents.router import IntentResult
from app.llm import chat
from app.rag import retrieve


class SolverResult:
    def __init__(self, answer: str, steps: str, context_used: List[dict], tool_used: bool = False):
        self.answer = answer
        self.steps = steps
        self.context_used = context_used
        self.tool_used = tool_used


def _safe_python_calc(expr: str) -> str:
    """Safely evaluate a simple numeric/math expression. Returns result or error string."""
    import math
    allowed = set("0123456789.+-*/().%e ^")
    expr_clean = expr.replace("**", "^").replace(" ", "")
    for c in expr_clean:
        if c not in allowed and c not in "sqrtabsincoxptanlog":
            return ""
    try:
        safe = {"sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan, "log": math.log, "log10": math.log10, "exp": math.exp, "abs": abs, "pi": math.pi, "e": math.e}
        expr_eval = expr.replace("^", "**")
        if any(f in expr_eval for f in ["sqrt", "sin", "cos", "tan", "log", "exp"]):
            for name, fn in safe.items():
                expr_eval = expr_eval.replace(name, f"safe['{name}']")
            safe["safe"] = safe
            result = eval(expr_eval, {"__builtins__": {}}, safe)
        else:
            result = eval(expr_eval)
        return str(result)
    except Exception:
        return ""


def _format_memory_context(similar_sessions: Optional[List[dict]] = None, correction_rules: Optional[List[dict]] = None) -> str:
    """Format similar past sessions and past corrections for the solver prompt."""
    parts = []
    if correction_rules:
        parts.append("Past corrections (user said the model was wrong; use these to avoid repeating mistakes):")
        for i, r in enumerate(correction_rules[-5:], 1):
            snippet = (r.get("problem_snippet") or "").strip() or "(similar problem)"
            orig = r.get("original_answer") or ""
            corr = r.get("corrected_answer") or ""
            comment = r.get("user_comment") or ""
            line = f"- Problem like: \"{snippet[:120]}...\". Model had said: {orig[:80]}. Correct answer: {corr[:80]}." + (f" User note: {comment[:60]}." if comment else "")
            parts.append(line)
        parts.append("")
    if similar_sessions:
        parts.append("Similar past problems (for reference; match method and style when appropriate):")
        for s in similar_sessions[:3]:
            pt = (s.get("parsed_question") or {}).get("problem_text", "")[:150]
            ans = s.get("final_answer", "")[:100]
            fb = s.get("user_feedback", "")
            if pt or ans:
                parts.append(f"- Past: \"{pt}...\" → Answer: {ans}. Feedback: {fb or 'stored'}.")
        parts.append("")
    return "\n".join(parts) if parts else ""


def solve_problem(
    parsed: ParsedProblem,
    intent: IntentResult,
    top_k: int = 5,
    similar_sessions: Optional[List[dict]] = None,
    correction_rules: Optional[List[dict]] = None,
) -> SolverResult:
    """Solve using RAG retrieval + LLM. Uses past similar sessions and correction rules to learn from feedback."""
    context_chunks = retrieve(parsed.problem_text, top_k=top_k)
    context_used = context_chunks
    context_str = "\n\n".join([c["content"] for c in context_chunks]) if context_chunks else "No retrieved context."

    memory_block = _format_memory_context(similar_sessions=similar_sessions, correction_rules=correction_rules)
    memory_section = f"\nLearning from past feedback (use to avoid repeating mistakes):\n{memory_block}\n" if memory_block else ""

    user_msg = f"""Solve this math problem. Use the retrieved knowledge below only when relevant; do not cite if not used.{memory_section}

Retrieved knowledge:
{context_str}

Problem: {parsed.problem_text}
Topic: {parsed.topic}
Suggested strategy: {intent.strategy}
Variables: {parsed.variables}
Constraints: {parsed.constraints}

Provide:
1) Final answer (clearly stated, with units if applicable).
2) Step-by-step solution (brief steps with justification).
If you need to compute a number, you can output a line like: CALC: <expression> and the system will substitute the result. Otherwise solve symbolically."""

    response = chat([
        {"role": "system", "content": "You are a precise math tutor. Give correct, step-by-step solutions. Use the retrieved context only when it applies; do not invent citations. When past corrections or similar problems are provided, avoid repeating past mistakes and align with user-corrected answers when the problem is similar."},
        {"role": "user", "content": user_msg},
    ])

    tool_used = False
    if "CALC:" in response:
        for m in re.finditer(r"CALC:\s*([^\n]+)", response):
            expr = m.group(1).strip()
            res = _safe_python_calc(expr)
            if res:
                response = response.replace(m.group(0), f"Computed: {expr} = {res}")
                tool_used = True

    lines = response.strip().split("\n")
    answer = ""
    steps = response
    for i, line in enumerate(lines):
        if any(k in line.lower() for k in ("final answer", "answer is", "therefore", "result:")):
            answer = line
            steps = "\n".join(lines[:i] + lines[i + 1 :]).strip()
            break
    if not answer and lines:
        answer = lines[-1]
        steps = "\n".join(lines[:-1]).strip()

    return SolverResult(answer=answer or response, steps=steps or response, context_used=context_used, tool_used=tool_used)
