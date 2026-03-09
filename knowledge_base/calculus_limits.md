# Calculus – Limits (JEE)

## Definition and properties
- lim_{x→c} f(x) = L means f(x) → L as x → c. One-sided: lim_{x→c⁻} and lim_{x→c⁺}; limit exists iff both exist and are equal.
- Limit laws: limit of sum, product, quotient (limit of denominator ≠ 0) equals sum, product, quotient of limits. Same for one-sided.

## Limits at infinity (rational functions)
- For lim_{x→∞} P(x)/Q(x) with polynomials P, Q: divide numerator and denominator by x^(max degree). Result: 0 if deg P < deg Q; ratio of leading coefficients if deg P = deg Q; ∞ or -∞ if deg P > deg Q (sign from leading terms).
- Example: lim_{x→∞} (3x² + 1)/(2x² - x) = 3/2. lim_{x→∞} (x + 1)/x² = 0.

## Standard limits (memorize)
- lim_{x→0} sin(x)/x = 1 (x in radians). lim_{x→0} tan(x)/x = 1.
- lim_{x→0} (e^x - 1)/x = 1. lim_{x→0} (a^x - 1)/x = ln(a).
- lim_{x→0} (1 + x)^(1/x) = e. lim_{n→∞} (1 + 1/n)^n = e.

## Indeterminate forms 0/0 and ∞/∞
- Simplify first (factor, cancel, substitute). If still 0/0 or ∞/∞, L’Hôpital’s rule: lim f(x)/g(x) = lim f'(x)/g'(x) provided the right limit exists (may apply repeatedly).
- Do not use L’Hôpital for forms that are not 0/0 or ∞/∞ (e.g. 0·∞: rewrite as 0/0 or ∞/∞ first).

## Common mistakes
- Using L’Hôpital when limit is not indeterminate (e.g. 1/0 is not 0/0).
- Forgetting to check both left and right limits when limit is at a point (e.g. |x|/x at 0).
- For rational functions at ∞: always divide by highest power of x in the denominator.
