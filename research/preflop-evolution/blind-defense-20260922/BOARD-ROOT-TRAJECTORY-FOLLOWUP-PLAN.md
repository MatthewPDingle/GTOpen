# Follow-up: when do the remaining range disagreements develop?

This is an exploratory analysis chosen after the completed board-root comparison.
It cannot change that experiment's outcome or promote a model. No new deals,
fitting, new payoff tests, checkpoint selection, or production changes are involved.

Inspect all 79 saved root states (initial state and 78 updates) for both board-root
candidates. Authenticate each model against the complete evaluated bank and its
already completed training audit. Independently reproduce the root regret-matching
probabilities and compare with the existing runtime. For the initial generation,
check the actual CPU model inference rather than assume its fallback policy.

Reproduce the evaluated played average using generations 0-77, weights 1-78, and
the original incoming class masses. The root has no prior own actions. Exclude
unplayed generation 78 from this average; label it as diagnostic only elsewhere.
Report every class, every transition, the final current policy versus the played
average, and first/middle/last windows 0-25, 26-51, 52-77, using the same original
generation weights normalized inside each window. Include cumulative-average
cross-seed disagreement for all 78 played prefixes and all three windows.

Compare movement summaries with the already authenticated stratified-control
trajectory. Verify that its model references and evaluated root averages match
the controls used in this completed experiment. Do not silently use another bank.

Report retained cumulative regrets and root probabilities without presenting
training-regret differences as stationary action-value estimates or independent
samples. Shared boards and evolving opponents correlate the observations. Any
hand examples are descriptive and must accompany the complete 169-class output.

Use two CPU workers with one BLAS thread each and no GPU. Require available RAM
and idle production, admit light desktop use, and keep the run bounded to 30
minutes and 32 MB of new output. Existing research evidence is read-only. A control
must verify weighting, deterministic tie handling, malformed-policy rejection,
and exclusion of the unplayed endpoint before inspecting the candidate history.

The decision afterward is whether to investigate continuing movement or early
divergence. Stronger-play claims still require a fresh, appropriately designed
action-value or payoff test of the complete averaged policies.
