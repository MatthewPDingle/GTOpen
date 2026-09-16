# Longer exact-interface diagnostic

Registered after the fixed5000-step experiments. Their outcomes are retained:
full CFR0.002759, robust exact cutoff0.007225, zero-probability-completed exact
cutoff0.005163 chips NashConv. The latter two missed0.005 but were still falling.
This extension separates slow convergence from a persistent residual. It is
not a retroactive pass for the original iteration budget.

Same complete miniature game, numerical backend, vanilla CFR, pure-response
enumeration and original0.005 threshold. Run full CFR, original exact cutoff
and zero-probability-completed cutoff from scratch through20000 iterations,
with checkpoints100,500,2000,5000,10000,20000. Compare the repeated5000-step
policies to archived runs. Final policies of both cutoff arms are completed
with the same original robust exact oracle at their averaged upper ranges;
this avoids confounding upper-policy differences with different reconstruction.

Only if all three arms pass0.005 at20000, train and run the originally fixed
surrogate through the same checkpoints. Training remains512 range pairs per
context, seed20260917; held-out128 per context, seed20260918; unchanged RBF
settings and physical projection. No model selection on search results.
Prediction final NashConv must be<=0.005 and<=0.002 above original exact cutoff.
No additional extension, threshold change or deployment follows automatically.

This study is a miniature design test, not the GTOpen GPU implementation.
Production uses alternating discounted CFR; this harness initially uses
simultaneous vanilla CFR to separate design correctness from those choices.
Timing is local diagnostic cost, not production performance.
