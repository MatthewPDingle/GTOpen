# N02b: hand-specific corrections

Specified before its first fit. The original-24-case curvature pilot reduced
equal-family CV MAE only from 6.9675 to 6.9270 percent pot (about 0.6%), missing
the predefined 5% improvement gate. This motivates testing greater hand identity
flexibility while keeping per-terminal inference cheap.

Retain the 104 shape features. Add either a per-hand constant, a per-hand
constant and equity coefficient, or those two plus a per-hand IP coefficient.
Each hand activates only its own one to three coefficients; GPU inference can
use constant-table lookups rather than evaluating a dense one-hot vector.
No runtime speed is claimed until exact parity and timing are measured.

Fixed candidates: these three variants crossed with ridge penalties
0.03, 0.1, 0.3 and 1.0. All use the existing mass-weighted standardization and
compatible-mass centering. Select by leave-one-training-source-family-out
error, requiring at least 5% better equal-family mean than shape/0.1 and no
more than 5% worse in any training family. All related cases remain in the same
fold. The original 24-case pilot is diagnostic; repeat the frozen selection on
26 cases when the additional development references finish. Do not use any
evaluation labels for fitting, selection or coefficient changes.

If both curvature and hand-offset variants are eligible in the final 26-case
comparison, choose the lower family-CV error across them before prospective
evaluation. Freeze one candidate, then use new evaluation boards, separate from
all N01 and older boards. Preserve original predictions and artifacts. Passing
training CV is only an eligibility screen, not accuracy validation.
