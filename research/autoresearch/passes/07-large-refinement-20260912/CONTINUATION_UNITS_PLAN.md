# Next correctness experiment: conditional/full-game history units

Source observation: `research_refine_branch_gpu` normalizes each incoming seat
range, starts learning-node histories at zero, solves a compact subtree, and
copies its regret/average arrays into the corresponding parent nodes. It
correctly labels that research artifact as not supporting normal global resume.
The earlier ancestor-only updates never tested coherent updates throughout the
remaining full tree; the full restart experiment instead discarded all history.

Before another learning variant, test the mathematical conversion on a small
GPU fixture. If incoming seat q has mass m_q and normalized range r_q/m_q, the
candidate relation for traverser p is:

- Full-game counterfactual action-value/regret increments equal conditional
  increments multiplied by the product of incoming m_q for q != p.
- Own-reach-weighted average increments equal conditional increments times m_p.

These are hypotheses to verify in the actual implementation, including rake,
folded seats, investment accounting, calibrated HU continuation and coupled
multiway leaves. They must not be assumed true from textbook CFR alone. Use
nonuniform, unequal-mass input ranges, multiple depths, locks and frozen seats.
Compare values immediately before scratch reuse. Verify all relevant hands and
actions; CPU may provide an independent correctness reference, never a speed
trial. Include zero/unsupported incoming mass refusal and finite scaling.

First deliverable is a numerical identity test and evidence, not a newly claimed
resume format. Even if the identity holds, local iteration age/discount schedule
and cumulative-history magnitude still need an explicit warm-start design.
Per-seat scalar rescaling preserves normalized policy only away from numerical
fallback thresholds; test that boundary instead of assuming invariance.

Only then define a separate research continuation entry point with explicit
synthetic-history metadata, non-overlapping branch ownership, preservation of
all untouched/fixed data, save/reload checks, and full unrestricted GPU updates
to ancestors and neighboring branches. Do not silently change the existing
compact API or assert production continuation compatibility.

Any continuation experiment must retain the native 0.005-bb global gate and all
27 conditioned local gates simultaneously. Neither a low global gap alone nor
26/27 local passes qualifies deployment. Freeze its schedule and runtime gate
before learning runs. Keep port 56708 untouched and push research evidence.
