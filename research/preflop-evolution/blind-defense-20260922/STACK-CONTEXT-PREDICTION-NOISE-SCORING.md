# Separating prediction error from label noise

The native control showed that short sampled labels can differ substantially,
even with exactly the same teacher and information state. Comparing a prediction
to one such label mixes two things: how wrong the prediction is, and how noisy
the label happens to be. The separate prediction diagnostic now has a qualified
scoring building block to keep those quantities distinct.

For the same information state, compute two equal-budget labels from independent
conditional chance streams. Both use the same frozen teacher, legal actions,
opponent posterior and original teacher baseline. If the prediction is `p` and
the two advantage labels are `y1` and `y2`, score each legal action using:

    observed error = ((p - y1)^2 + (p - y2)^2) / 2
    label noise    = (y1 - y2)^2 / 2
    corrected error = (p - y1) * (p - y2)

Observed error minus label noise equals corrected error exactly. With unbiased,
independent labels and a prediction frozen independently of them, the corrected
score's expectation is the true squared prediction error. A finite estimate can
be negative; clamping it to zero would add bias. The expectation identity is a
conditional mathematical result, not evidence that future scientific data meet
the required independence and freezing conditions.

Both candidate predictors use the same labels. Their difference in corrected
error also equals their difference in observed error: the common noise term
cancels. Report absolute prediction quality and the paired representation
comparison separately. Average over legal actions only; illegal output slots
contribute neither values nor denominator, even if padding contains NaN.

## Bounded predictions and decision scores

The actual native chip ledger bounds conditional action values by `[-S, S+D]`,
where `S` is the original stack and `D` is dead money. Normalized advantages
therefore lie in `[-B, B]`, with `B = 2 + D/S`. This implementation explicitly
clips legal predictions to that interval and records how many outputs were
clipped. Its error metric describes clipped predictions, not unbounded raw
network output. That choice must be declared in the future protocol.

The implemented decision rule chooses the largest clipped legal prediction,
splitting exact ties uniformly. It does not consult evaluation labels. The
paired payoff score uses the two policies' difference against the common
conditional Q means, normalized by the original stack. Its expectation is
their decision-payoff difference under the fixed teacher, not optimal-action
regret or a best-response certificate. A scientific protocol must freeze this
rule before labels, prediction selection or results are observed.

Conservative row bounds are derived from the ledger: observed loss `[0, 4B^2]`,
noise `[0, 2B^2]`, corrected loss `[-B^2, 4B^2]`, paired error improvement
`[-4B^2, 4B^2]` and decision improvement `[-B, B]`.

## Uncertainty follows source clusters

Several hands or decisions from one parent hand or board share information and
are dependent. They cannot become independent observations merely by appearing
on different action rows. `ClusterEvaluation` takes one complete block of
dependent descendants, computes its prospectively weighted convex row average,
then adds one observation for that source cluster. It averages source clusters
equally; it does not pool all rows and let larger trees count more heavily.

Cluster sampling, row weights and the resulting estimand must be declared in
advance. The reused empirical-Bernstein interval requires IID parent draws from
the frozen declared source distribution, frozen predictions and independent
label streams. Unique identifiers do not prove those assumptions. All dependent
descendants must share their declared parent cluster. Duplicate and overlapping
cluster batches are refused. Stratified context or actor/street scores need
their declared weights; this helper does not invent population weights.

The caller explicitly supplies every stratum, permitted sample-count look,
family error probability and conservative maximum ledger span. The interval
family includes all seven metrics in every declared stratum and every declared
look, using the existing qualified bounded paired interval implementation.
Confidence counts source clusters, not descendant rows. A canonical-flop
training/test split is a separate requirement, not an uncertainty calculation.
Preflop still needs a distinct holdout unit.

## Qualification retained locally

The CPU check passed in 0.046 seconds without native calls, fits, CUDA or new
scientific samples. It enumerated all 16 independent combinations of a finite
zero-mean label-noise distribution with a known conditional truth. Corrected
losses reproduced the known errors 0.62 and 0.005 exactly within tolerance;
observed losses included the known noise variance 0.02285. The independently
chosen policies' expected paired payoff difference was 0.5 starting-stack units
in this synthetic control. These numbers are not scores for learned models.

Additional controls preserved a negative corrected estimate, ignored illegal
outputs, checked clipping, verified 108 endpoint bound cases, reproduced merged
and sequential statistics, and counted four source clusters rather than their
138 dependent rows. All 19 corruption/refusal cases passed. The check also
recomputed metric arithmetic on the 16 retained native label pairs with clearly
synthetic predictions; no confidence or accuracy claim was made on those fixtures.

Independent readback authenticated all nine consumed source/evidence identities,
recomputed the finite-control truth and all seven clustered interval means,
variances, radii and family allocation without calling the scoring implementation.
Sources/evidence use the `stack_context_prediction_noise_scores` and
`stack-context-prediction-noise-scores` prefixes.

The helpers are not imported by the live study. No prediction diagnostic has
been admitted or completed. Actual complete A-baseline teacher inference,
splits, unsupported-state rules, source sampling, budgets/seeds, fitting and
selection, scoring-rule adoption and statistical registration remain required.
The original four-arm training and its complete-bank gate, fresh evaluation and
independent analysis sequence remain unchanged. This qualification establishes
scoring arithmetic and refusal behavior, not improved preflop accuracy.
