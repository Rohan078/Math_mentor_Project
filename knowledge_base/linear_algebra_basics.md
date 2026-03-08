# Linear Algebra – Basics

## Vectors
- Addition and scalar multiplication component-wise.
- Dot product: a·b = a₁b₁ + a₂b₂ + ... ; a·b = |a||b|cos θ.
- Two vectors orthogonal iff a·b = 0.

## Matrices
- Multiplication: (AB)_{ij} = sum_k A_{ik} B_{kj}. Order matters: AB ≠ BA in general.
- Identity I: AI = IA = A. Inverse A⁻¹ when it exists: A A⁻¹ = A⁻¹ A = I.

## Determinants (2×2 and 3×3)
- 2×2: det [[a,b],[c,d]] = ad - bc. A invertible iff det(A) ≠ 0.
- 3×3: use Sarrus or cofactor expansion.

## Linear systems
- Ax = b has unique solution iff A is invertible: x = A⁻¹ b.
- If det(A) = 0, system may have no solution or infinitely many (use row reduction to decide).

## Eigenvalues (brief)
- λ is eigenvalue of A if Av = λv for some v ≠ 0. Solve det(A - λI) = 0.

## Common mistakes
- Treating matrix multiplication as commutative.
- Forgetting to check dimensions (m×n times n×p gives m×p).
- Sign errors in determinants and cofactors.
