# Paired-accounting value blend (N34)

This replaces the failed N33 accounting assumption, before any blend scores.
The baseline endpoint is the legal-pair Balanced formula used by N20's paired
interface, evaluated with symmetric equity, the unchanged relative class priors,
OOP/IP weights 0.92/1.08, and the existing SPR/8 realization blend. Opponent
classes are conditioned on compatible cards for each hero hand. Its total
compatible-mass gross pot share must be one, without post-hoc centering.

Reproduce N15's four whole-family held-out fits on the original 26 training
contexts. For each context predict `(1-alpha)*paired_Balanced + alpha*N15`.
Fixed alpha grid: 0, 0.125, 0.25, 0.5, 1. Keep all N15 settings unchanged and
require all 26 alpha=1 errors to reproduce within 1e-9. Compare paired Balanced
against the historical ordinary comparator transparently.

Choose the smallest nonzero tested alpha improving mean family error at least
15% over paired Balanced and every family at least 5%. This is a registered
accuracy/settling tradeoff screen, not N15's predictor-selection gate. Report
the accuracy loss relative to full N15. No extra strengths or altered gates.

A selected blend is only a lead: it requires GPU formula parity, fresh references
and end-to-end convergence/runtime testing. No speed claim follows from blending;
the predictor still runs. No evaluation labels are read, no app model changes,
and no CPU fitting during N32's controlled GPU run.
