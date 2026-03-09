# Calculus – Integrals (JEE)

## Definitions
- Indefinite integral: ∫ f(x) dx = F(x) + C where F'(x) = f(x). C is constant of integration.
- Definite integral: ∫_a^b f(x) dx = F(b) - F(a) (Fundamental Theorem). f must be continuous on [a,b] or at least integrable.

## Basic rules
- ∫ (f(x) ± g(x)) dx = ∫ f(x) dx ± ∫ g(x) dx.
- ∫ c f(x) dx = c ∫ f(x) dx.
- ∫_a^b f(x) dx = -∫_b^a f(x) dx; ∫_a^a f(x) dx = 0.
- ∫_a^b f(x) dx + ∫_b^c f(x) dx = ∫_a^c f(x) dx.

## Standard indefinite integrals (must know)
- ∫ x^n dx = x^(n+1)/(n+1) + C, n ≠ -1.
- ∫ 1/x dx = ln|x| + C.
- ∫ e^x dx = e^x + C. ∫ a^x dx = a^x/ln(a) + C.
- ∫ sin x dx = -cos x + C. ∫ cos x dx = sin x + C.
- ∫ sec² x dx = tan x + C. ∫ csc² x dx = -cot x + C.
- ∫ sec x tan x dx = sec x + C. ∫ csc x cot x dx = -csc x + C.
- ∫ 1/(1+x²) dx = arctan x + C. ∫ 1/√(1-x²) dx = arcsin x + C.

## Substitution (u-substitution)
- If ∫ f(g(x)) g'(x) dx, let u = g(x), du = g'(x) dx; then ∫ f(u) du. After integrating, substitute back u = g(x).
- For definite integrals: change limits to u(a) and u(b), or integrate in u and then substitute back before evaluating.
- Choose u so that du appears in the integrand (up to a constant).

## Integration by parts
- ∫ u dv = uv - ∫ v du. Choose u so that u' is simpler; choose dv so that v is easy to integrate.
- LIATE (priority for u): Logarithm, Inverse trig, Algebraic, Trig, Exponential. Often u = ln x, arctan x, or polynomial; dv = rest.

## Definite integral properties
- If f is even: ∫_{-a}^a f(x) dx = 2∫_0^a f(x) dx. If f is odd: ∫_{-a}^a f(x) dx = 0.
- ∫_0^a f(x) dx = ∫_0^a f(a-x) dx (substitution x → a-x).
- Average value of f on [a,b]: (1/(b-a)) ∫_a^b f(x) dx.

## Common mistakes
- Forgetting + C in indefinite integrals.
- Wrong limits after substitution: either change limits to u-values or substitute back to x before evaluating.
- Sign errors when splitting integrals or using |x| in ln|x|.
- Using integration by parts when a simple substitution would work.

## JEE-style procedure for ∫ f(x) dx
1. Check if it is a standard form (list above).
2. If product of two types (e.g. x·e^x, x·sin x): try integration by parts.
3. If composition (e.g. f(g(x)) with g'(x) present): try substitution u = g(x).
4. Simplify algebraically first (expand, partial fractions for rational functions).
5. For definite integrals: state antiderivative, then F(b) - F(a); check continuity on [a,b].
