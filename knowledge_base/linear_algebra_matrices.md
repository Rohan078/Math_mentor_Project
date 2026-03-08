# Linear Algebra – Matrix Operations and Systems

## Row operations
- Swap rows; multiply row by nonzero scalar; add multiple of one row to another.
- Use to get row-echelon or reduced row-echelon form.

## Solving Ax = b
- Augmented matrix [A|b]. Row reduce. If pivot in last column ⇒ no solution. If rank(A) = rank([A|b]) = n ⇒ unique solution; if rank < n ⇒ infinitely many (free variables).

## Inverse of 2×2
- [[a,b],[c,d]]⁻¹ = (1/(ad-bc)) [[d,-b],[-c,a]], provided ad - bc ≠ 0.

## Cramer’s rule (2×2)
- For ax + by = e, cx + dy = f: x = (ed - bf)/(ad - bc), y = (af - ec)/(ad - bc), when ad - bc ≠ 0.

## Domain/constraints
- Solutions may be required to be integers or positive; check after solving.
- Parameter constraints (e.g. for consistency) often come from denominator ≠ 0 or rank conditions.
