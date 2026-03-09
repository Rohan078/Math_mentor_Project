# Calculus – Derivatives (JEE)

## Definition
- f'(x) = lim_{h→0} (f(x+h) - f(x))/h. Slope of tangent line at x. Use this when asked for derivative from first principles.

## Sum, product, quotient rules
- (u ± v)' = u' ± v'. (cu)' = c u' (c constant).
- Product: (uv)' = u'v + uv'. Quotient: (u/v)' = (u'v - uv')/v², v ≠ 0.

## Chain rule (essential)
- (f(g(x)))' = f'(g(x)) · g'(x). Differentiate outer function, keep inner; multiply by derivative of inner.
- Example: d/dx sin(x²) = cos(x²) · 2x. d/dx e^(3x) = e^(3x) · 3.
- Never forget the inner derivative g'(x).

## Standard derivatives
- d/dx x^n = n x^(n-1), n real. d/dx e^x = e^x. d/dx a^x = a^x ln(a). d/dx ln|x| = 1/x.
- d/dx sin x = cos x, d/dx cos x = -sin x, d/dx tan x = sec² x.
- d/dx sec x = sec x tan x, d/dx csc x = -csc x cot x, d/dx cot x = -csc² x.
- d/dx arcsin x = 1/√(1-x²), d/dx arccos x = -1/√(1-x²), d/dx arctan x = 1/(1+x²).

## Applications
- Tangent line at x = a: y - f(a) = f'(a)(x - a). Normal line: slope = -1/f'(a) when f'(a) ≠ 0.
- Critical points: solve f'(x) = 0 or where f' undefined. First derivative test: sign of f' changes at critical point. Second derivative test: f''(c) > 0 ⇒ local min, f''(c) < 0 ⇒ local max; f''(c) = 0 inconclusive.
- Concavity: f'' > 0 ⇒ concave up, f'' < 0 ⇒ concave down. Inflection: f''(c) = 0 and f'' changes sign at c.

## Optimization (JEE-style)
- Identify quantity Q to maximize or minimize; write constraint(s); express Q as function of one variable; state domain (e.g. x > 0); find critical points (Q' = 0); compare Q at critical points and at boundary of domain; state answer with units.
