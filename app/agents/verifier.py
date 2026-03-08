"""Verifier / Critic Agent: checks correctness, units, domain, edge cases; can trigger HITL."""
from app.agents.parser import ParsedProblem
from app.agents.solver import SolverResult
from app.llm import chat_json


class VerificationResult:
    def __init__(self, is_correct: bool, confidence: float, issues: list[str], hitl_required: bool):
        self.is_correct = is_correct
        self.confidence = confidence
        self.issues = issues
        self.hitl_required = hitl_required


def verify_solution(parsed: ParsedProblem, solver_result: SolverResult) -> VerificationResult:
    """Verify solution correctness, units, domain; set hitl_required if confidence low."""
    prompt = f"""You are a math verifier. Check the following solution for correctness, units, and domain constraints.

Problem: {parsed.problem_text}
Topic: {parsed.topic}
Constraints: {parsed.constraints}

Solution steps:
{solver_result.steps}

Final answer: {solver_result.answer}

Respond with exactly 4 lines (no markdown):
is_correct: true or false
confidence: a number between 0 and 1 (e.g. 0.85)
issues: comma-separated list of issues found, or "none"
hitl_required: true if confidence < 0.7 or you are unsure about domain/units/edge cases; otherwise false"""

    try:
        out = chat_json([{"role": "user", "content": prompt}])
        lines = [l.strip() for l in out.strip().split("\n") if l.strip()]
        is_correct = True
        confidence = 0.8
        issues = []
        hitl_required = False
        for line in lines:
            if line.lower().startswith("is_correct:"):
                is_correct = "true" in line.split(":", 1)[1].strip().lower()
            elif line.lower().startswith("confidence:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                    confidence = max(0, min(1, confidence))
                except ValueError:
                    pass
            elif line.lower().startswith("issues:"):
                part = line.split(":", 1)[1].strip().lower()
                if part != "none" and part:
                    issues = [s.strip() for s in part.split(",") if s.strip()]
            elif line.lower().startswith("hitl_required:"):
                hitl_required = "true" in line.split(":", 1)[1].strip().lower()
        if confidence < 0.7:
            hitl_required = True
        return VerificationResult(is_correct=is_correct, confidence=confidence, issues=issues, hitl_required=hitl_required)
    except Exception:
        return VerificationResult(is_correct=True, confidence=0.5, issues=["Verification inconclusive"], hitl_required=True)
