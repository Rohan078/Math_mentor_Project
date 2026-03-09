# Calculus – When to Use What (JEE)

## Limits
- Limit at a finite point: plug in c; if 0/0 or ∞/∞ use L’Hôpital or simplify (factor, cancel).
- Limit at ∞ (rational function): divide numerator and denominator by x^(highest power in denominator); then take limit term by term.
- Standard limits: sin(x)/x → 1, (e^x - 1)/x → 1, (1+1/x)^x → e as x→∞. Use when expression can be rewritten to match.

## Derivatives
- From first principles: use definition f'(x) = lim_{h→0} (f(x+h)-f(x))/h only if asked.
- Polynomials/powers: use d/dx x^n = n x^(n-1).
- Product of two functions: product rule (uv)' = u'v + uv'.
- Quotient: quotient rule (u/v)' = (u'v - uv')/v².
- Composition f(g(x)): chain rule — differentiate outer, keep inner, multiply by derivative of inner.
- Tangent/normal line: slope = f'(a); tangent y - f(a) = f'(a)(x-a); normal slope = -1/f'(a).

## Critical points and optimization
- Find f'(x); set f'(x) = 0 and find where f' undefined; these are critical points.
- First derivative test: check sign of f' on left and right of each critical point. Second derivative test: f''(c) > 0 ⇒ min, f''(c) < 0 ⇒ max.
- Word problems: write quantity Q as function of one variable using constraint; domain (e.g. x > 0); critical points; compare Q at critical points and boundaries; answer with units.

## Integrals
- Match to standard form first (x^n, 1/x, e^x, sin, cos, 1/(1+x²), etc.).
- If integrand has f(g(x)) and g'(x) present (up to constant): substitution u = g(x).
- If product (e.g. x e^x, x sin x): integration by parts ∫ u dv = uv - ∫ v du; choose u that simplifies when differentiated.
- Definite: always end with F(b) - F(a); after substitution either change limits to u or substitute back to x.

## Consistency checks
- Derivative of constant is 0. Integral of 0 is C. ∫_a^a f = 0.
- Units: if problem has meters, seconds, etc., answer must have correct units (e.g. m², m/s).
