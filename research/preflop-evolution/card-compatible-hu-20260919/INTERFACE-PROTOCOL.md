# Test the existing experimental interface against the independent LP

19 September 2026, fixed before execution. Reuse the 16 September frozen
`learned-interface-20260916/interface.cu` through the existing research hook,
with learned pricing **disabled**. No new application code or kernel changes.

Repeat the four native push/fold fixtures (posts 1/2, stacks 3/10/50/200) at
1,000 and 10,000 iterations. The interface owns all fold and showdown terminals
from the two-player root. Skip the redundant ordinary terminal calculation using
the existing research optimization. CPU query outputs retain the old independent
model and must not be mistaken for the corrected GPU model's evaluation.

Require the independently reconstructed compatible-game values and summed
best-response gaps to match GPU exports within 0.0001 chip. Require gap <=0.001
at 10,000 iterations, and independent LP primal/dual difference <=0.000001.
Retain failed outcomes without changing the gate. Save no experimental game
files, because current save metadata cannot identify these changed semantics.

This adds an independent equilibrium certificate to earlier fixed-policy
interface checks. It does not newly invent the legal-pair interface, validate
its multiway chance reset, add rake support, or establish postflop accuracy.
No timing acceptance gate or production deployment is implied.
