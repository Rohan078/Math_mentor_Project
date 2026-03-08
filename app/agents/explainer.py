"""Explainer / Tutor Agent: produces step-by-step, student-friendly explanation."""
from app.agents.parser import ParsedProblem
from app.agents.solver import SolverResult
from app.llm import chat


class ExplainerResult:
    def __init__(self, explanation: str):
        self.explanation = explanation


def explain_solution(parsed: ParsedProblem, solver_result: SolverResult) -> ExplainerResult:
    """Produce a clear, step-by-step explanation suitable for a student."""
    prompt = f"""You are a friendly math tutor. Turn this solution into a clear, step-by-step explanation for a JEE-level student.

Problem: {parsed.problem_text}

Solution steps:
{solver_result.steps}

Final answer: {solver_result.answer}

Write a short explanation that:
1) Restates what we are finding
2) Walks through each step with a brief reason (e.g. "We use the quadratic formula because...")
3) Highlights the final answer
4) Mentions any common pitfall or tip if relevant

Keep it concise and educational. Use simple language. Format with clear step numbers."""

    explanation = chat([
        {"role": "system", "content": "You are a patient math tutor. Explain clearly with step numbers. No markdown code blocks."},
        {"role": "user", "content": prompt},
    ])
    return ExplainerResult(explanation=explanation or solver_result.steps)
