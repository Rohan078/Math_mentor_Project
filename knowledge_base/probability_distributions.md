# Probability – Discrete and Continuous Distributions

## Discrete: Binomial
- n trials, success probability p. P(X = k) = C(n,k) p^k (1-p)^(n-k), k = 0,1,...,n.
- E(X) = np, Var(X) = np(1-p).

## Discrete: Poisson (limit of binomial, rare events)
- P(X = k) = λ^k e^(-λ) / k!, k = 0,1,2,... . E(X) = Var(X) = λ.

## Continuous: Normal
- Mean μ, variance σ². Standardize: Z = (X - μ)/σ.
- 68–95–99.7 rule: ≈ 68% within 1σ, 95% within 2σ, 99.7% within 3σ.

## JEE-style constraints
- Probabilities must sum to 1 for all outcomes of a discrete distribution.
- Density f(x) ≥ 0 and ∫ f(x)dx = 1 for continuous; P(a ≤ X ≤ b) = ∫_a^b f(x)dx.
- Check support: e.g. binomial k ∈ {0,...,n}; Poisson k ≥ 0.
