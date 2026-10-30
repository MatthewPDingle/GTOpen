# Stratified study launched

The registered study is now training the two candidate arms. It reuses the
completed baseline arms, with matched settings and seed identities; see
WEIGHTED-STRATIFIED-STUDY-PLAN.md for fixed endpoints and interpretation limits.
No claim of improved ranges is available yet.

The first invocation completed two real-budget generations in 23.812 and23.657
seconds, with512 Adam steps per player,512 physical deals and all169 BB hand
classes covered. A second invocation restored the generation-two checkpoint and
completed generation three in27.563 seconds. These are early timings before the
262144-visit reservoirs fill; do not extrapolate them as final throughput.

The accelerated weighted policy-bank reader separately matched the reference
CPU average and a scalar own-history calculation on14549 actual pilot decision
points. Model chunk sizes1,2,8 all had maximum policy error3.33e-16 and reach
error4.44e-16. Reordered, incomplete, unplayed models and invalid root ancestry
were rejected. This qualifies the tested two-generation bank, not automatically
a full78-generation bank or independent poker evaluation.

Evidence:

- weighted-stratified-study-v1-registration.json
- weighted-bank-control-v1-registration.json
- weighted-bank-control-v1-result.json

Raw training evidence and atomic progress pointers live in
T:/GTOpen-research/weighted-stratified-study-v1. The mutable status and log in this
directory are convenient observations; verify the actual process before claiming
the job is live. A partial generation is never treated as a completed checkpoint.
To resume a terminal invocation, use weighted_stratified_study_20260927.py --resume
after checking resources and locks. Do not start a second copy of a live job.

Remaining gates are independent training readback, full-bank equivalence, fixed
65536-deal crossed-policy evaluation, independent evaluation readback, and a
complete stability/strength analysis. Broad preflop accuracy remains unproven.
