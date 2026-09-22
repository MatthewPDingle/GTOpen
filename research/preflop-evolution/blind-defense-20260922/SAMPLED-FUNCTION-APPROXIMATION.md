# Candidate after the exact-key growth screen

The [growth measurements](SAMPLED-GROWTH-RESULT.md) show that faster tree
traversal does not supply enough repeated observations of individual turn and
river decisions. Exact suit sharing alone has little effect on the occupied
river keys at this sample count. This motivates testing generalization, not
loosening selected preflop hands to resemble Wizard.

The [finite convergence baseline](SAMPLED-CONVERGENCE-CONTROL.md) has now passed
for exact full traversal and four sampled seeds under both payoff settings.
Its independently checked evaluator is available for the approximation candidate.
This small nonphysical game is a method control, not the actual poker target.

## Published route worth a controlled test

Deep CFR predicts action advantages from observable game information, using
samples gathered by external-sampling traversals. It keeps training samples in
bounded reservoirs instead of a growing regret row for every observation. Its
strategy estimate must account for averaging across iterations; the latest
network alone is not the average policy. Approximation error matters, and the
paper's theory concerns two-player zero-sum games. Our action-dependent rake
still requires independent deviation checks.
[Brown et al., ICML 2019, sections 4-5](https://proceedings.mlr.press/v97/brown19b/brown19b.pdf).

Single Deep CFR avoids a separate average-policy network by retaining prior
advantage models. That trades one approximation source for a growing collection
of models. Querying a particular reached decision requires the appropriate
reach-weighted mixture; uniformly averaging output probabilities is not enough.
[Steinberger, 2019, sections 5.1-5.2](https://arxiv.org/pdf/1901.07621).

These are candidate methods, not claims that neural training has already
improved GTOpen, matched Wizard or resolved the wide study's resource demands.

## Implementation and evidence requirements

1. Use the completed exact-update and physical-poker implementations as
   reference oracles. First add a tractable independently evaluated convergence
   control. It is a test of implementation quality, not a substitute game whose
   ranges would be promoted to production.
2. Capture per-iteration sampled advantage targets and visitation-weighted
   strategy examples. Do not train from the terminal accumulated checkpoint
   as if its rows were equally supported labels. Freeze sampler, batch/update
   order, reservoir selection, weighting and evaluation seeds.
3. Model inputs may contain own cards, public cards and complete public betting
   history/configuration. They may not contain the other player's private cards,
   future public cards or sampled showdown rank. Keep every legal action and
   preserve all original supported entering hands. Suit symmetries can be
   represented without using hidden information.
4. Verify reservoir inclusion weights, repeated samples, zero-own-reach actions,
   legal-action masks and the average-policy contract on finite controls before
   fitting a real-poker model. Keep target generation and inference snapshots
   fixed within their registered batches.
5. Separate prediction fit from strategic accuracy. Measure independently
   evaluated best-response gains, important call/fold/raise value differences,
   and results across fixed seeds. Prediction error averaged over common folds
   must not conceal errors in rare but important calling hands.
6. Only after control and capacity gates, compare the full BB target with its
   registered ranges, action menu and training coverage. Keep the original
   inspected 190-board result for diagnosis; a new strategic claim needs fresh
   evaluation. Broader flop coverage is a separate controlled change.

Avoid silently choosing hand-strength buckets, permanently deleting unusual
examples, resetting difficult branches, or treating low neural training loss
as convergence. A bounded model introduces approximation; the acceptance test
is better independently measured decisions at practical cost. It is not a
smaller memory footprint by itself.
