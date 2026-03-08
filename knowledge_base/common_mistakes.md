# Common Mistakes and Pitfalls (JEE-Style Math)

## Algebra
- Dividing both sides by an expression that could be zero (e.g. x) without checking x = 0 separately.
- √(x²) = |x|, not x. When solving x² = k, write x = ±√k.
- In inequalities, multiplying/dividing by a negative number reverses the inequality.

## Probability
- P(A|B) ≠ P(B|A) in general. Use Bayes’ theorem when flipping condition.
- Assuming independence without checking P(A∩B) = P(A)P(B).
- Forgetting that probabilities must sum to 1 over all outcomes.

## Calculus
- Chain rule: derivative of f(g(x)) is f'(g(x))·g'(x); do not forget g'(x).
- In L’Hôpital, differentiate numerator and denominator separately; do not use quotient rule.
- For limits at ±∞, divide numerator and denominator by the highest power of x.

## Linear algebra
- AB ≠ BA in general. Check dimensions: (m×n)(n×p) = m×p.
- det(A+B) ≠ det(A) + det(B). Use determinant properties (e.g. det(AB) = det(A)det(B)).

## Units and domain
- Always state domain (e.g. x > 0) when it affects the answer.
- Check that final answer satisfies constraints (e.g. length > 0, 0 ≤ P ≤ 1).
