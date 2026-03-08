"""Intent Router Agent: classifies problem type and routes workflow."""
from app.agents.parser import ParsedProblem
from app.llm import chat_json


class IntentResult:
    def __init__(self, intent: str, strategy: str, reasoning: str):
        self.intent = intent
        self.strategy = strategy
        self.reasoning = reasoning


def route_intent(parsed: ParsedProblem) -> IntentResult:
    """Classify problem and suggest solution strategy."""
    prompt = f"""You are an intent router for a math mentor. Given this structured problem, classify intent and suggest a solution strategy.

Structured problem:
- problem_text: {parsed.problem_text}
- topic: {parsed.topic}
- variables: {parsed.variables}
- constraints: {parsed.constraints}

Respond in exactly 3 short lines, one per field (no markdown):
intent: [one of: algebra, probability, calculus, linear_algebra]
strategy: [one sentence: e.g. "Use quadratic formula", "Apply Bayes' theorem", "Differentiate and find critical points"]
reasoning: [one sentence why this strategy]"""

    try:
        out = chat_json([{"role": "user", "content": prompt}])
        lines = [l.strip() for l in out.strip().split("\n") if l.strip()]
        intent = "algebra"
        strategy = "Solve step by step using standard methods."
        reasoning = "Default routing."
        for line in lines:
            if line.lower().startswith("intent:"):
                intent = line.split(":", 1)[1].strip().lower()
                if intent not in ("algebra", "probability", "calculus", "linear_algebra"):
                    intent = parsed.topic or "algebra"
            elif line.lower().startswith("strategy:"):
                strategy = line.split(":", 1)[1].strip()
            elif line.lower().startswith("reasoning:"):
                reasoning = line.split(":", 1)[1].strip()
        return IntentResult(intent=intent, strategy=strategy, reasoning=reasoning)
    except Exception:
        return IntentResult(
            intent=parsed.topic or "algebra",
            strategy="Solve step by step using standard methods.",
            reasoning="Default routing.",
        )
