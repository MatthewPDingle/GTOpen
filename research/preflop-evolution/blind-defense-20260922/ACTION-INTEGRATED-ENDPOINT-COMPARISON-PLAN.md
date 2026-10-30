# Action-integrated root training: endpoint and stability comparison

Prepared 25 September 2026, before either complete matched training output
exists. Implements the comparison already specified in
ROOT-ACTION-INTEGRATED-TRAINING-PLAN.md. No outcome-dependent selection.

After each complete 78-update training audit, evaluate its complete played bank
(generations 0 through 77; exclude generation 78) with all four BB/BTN combinations
of equal and linear averaging. Linear/linear is the primary comparison throughout.

Use the unchanged complete physical-private-card population and all-in runout
cache, configured rake and chip accounting. The new policy adapter reads only
the explicitly typed action-integrated models. Check CPU/CUDA policy agreement
on all supported initial observations. Preserve both complete initial policy
tables, including all 169 BB classes and supported BTN classes.

Compute the BB improvement possible by reallocating only its existing fold/jam
probability; leave call and raise probabilities unchanged. Independently compute
the BTN improvement from changing its response to the initial BB jam. Gains are
in bb per incoming entry, integrated over the full private-card population.
They are restricted endpoint diagnostics, not full best-response gaps.

The first matched trial's baseline is `root-retained-exact-v1`; the second is
`root-retained-replication-exact-v1`. Report all four pairings, both players'
gains, and primary differences from the corresponding old-estimator run.
Do not select the better seed or pairing.

`hu_action_integrated_exact_20260925.py first` (or `replication`) requires the
complete training readback before running. Its separate reader reconstructs
the policy tables and outcome-wise chip accounting for every canonical private
pair, all 169 classes and all four pairings. It does not call the endpoint
response/gain computation routines used by the producer. Policy-model loading
and inference remain shared; this is not a second neural implementation.

Each endpoint producer and reader has a 1,200-second ceiling. Producer outputs
are capped at 10 MB, compressed from creation. Before either producer, measure
all three research roots and require current allocation + 10 MB + 2 GB reserve
to fit within 800 GB. Keep 40 GB disk, 20 GB host RAM and 3 GB GPU reserves.
Hold the shared research lock for GPU execution. Do not overlap training or
change production 56708. No newly sampled holdout is used here.

After both endpoint readers pass, `hu_action_integrated_seed_comparison_20260925.py`
reports every hand class for four comparisons: old first-versus-repeat,
integrated first-versus-repeat, and old-versus-integrated within each matched
seed. Use the same incoming class mass, including opponent-range card removal.
For each comparison report mass-weighted action frequencies and total variation
(half the sum of absolute action-probability differences). Retain all classes,
not just examples that visually agree with expectations.

Compare the new cross-seed variation with the old pair's approximately 46.32
percentage points. Report increases as well as decreases; attach no confidence
interval or significance claim from only two chosen-in-advance training seeds.
Lower variation would show more reproducible training in this fixed setting,
not proof that call/raise ranges are strategically correct. Any wider response
evaluation still requires a separate prospective protocol and resource check.
