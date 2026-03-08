# Probability – Definitions and Basic Rules

## Sample space and events
- Sample space S: set of all outcomes. Event: subset of S.
- P(S) = 1, P(∅) = 0, 0 ≤ P(E) ≤ 1 for any event E.

## Addition rule
- P(A ∪ B) = P(A) + P(B) - P(A ∩ B).
- If A and B are mutually exclusive: P(A ∪ B) = P(A) + P(B).

## Conditional probability
- P(A|B) = P(A ∩ B) / P(B), provided P(B) > 0.
- Rearranged: P(A ∩ B) = P(B) P(A|B) = P(A) P(B|A).

## Independence
- A and B are independent iff P(A ∩ B) = P(A) P(B), equivalently P(A|B) = P(A) when P(B) > 0.

## Bayes’ theorem
- P(A|B) = P(B|A) P(A) / P(B), where P(B) = P(B|A)P(A) + P(B|A')P(A') when using partition by A.

## Common pitfalls
- Confusing P(A|B) with P(B|A).
- Using addition rule without subtracting P(A ∩ B) when events are not mutually exclusive.
- Assuming independence without justification.
