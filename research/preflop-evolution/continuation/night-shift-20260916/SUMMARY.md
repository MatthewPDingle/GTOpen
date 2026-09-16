# Preflop accuracy research: night-shift findings

**No candidate is ready to replace the live version.** The research produced better hand-value estimates, but the tested alternatives did not establish both improved accuracy and practical solve performance. The app on port 56708 was not deployed or restarted by this research.

## What improved

The strongest predictor reduced hand-value error by **31–43%** in the latest fresh-flop comparison, including a wider flop bet menu. All eight comparisons passed their accuracy screens. These are errors in estimated hand values, not a measured percentage improvement in full-game ranges. Some hand groups still regress.

## What prevents deployment

The full predictor's solve measure stayed near **0.078 bb** after 1,500 iterations, versus **0.00062 bb** for ordinary Balanced. The same additional 1,000 iterations took **18.2 minutes versus 13.0 minutes** (39.8% longer). A short iteration benchmark had looked better, which is why the longer test mattered.

Keeping only 25% of the learned prediction did not pass the fixed practical screen either: its 1,000-iteration gap was **0.01514 bb**, and the same amount of learning work took **10.6% longer** than the paired-accounting control in one ordered comparison. That control also remained slightly above the gap target; it is distinct from ordinary production Balanced.

A separately registered extension kept the blend unchanged and reached iteration **1500**, with gap **0.00792 bb**, still missing the registered settling screen. Its cumulative learning work from the common 500-step starting point was **18.8 minutes**. This extra work is charged to the blend; different final iteration counts do not make it a fair throughput comparison. No fresh-range accuracy result exists for this blend, because the prerequisite test failed.

## Most useful new lead

The full predictor's current and averaged hand ranges differ much more deep in the tree than the visible charts suggest: **8.3% versus 0.7%** on the registered weighted diagnostic. This suggests investigating the inputs seen during search. It is not proof of the cause or a measurement of range error. The empty-range fallback change did not help.

**Recommended next step:** compare a full small game with the same game using directly solved continuation values. Then introduce prediction. This separates prediction error from search integration and checks whether our stopping measure tracks true improvement in that controlled game. [Concrete follow-up](NEXT-STEPS.md).

## Scope and retained evidence

The accuracy tests use fresh boards in familiar range contexts and restricted postflop trees. They do not establish full-game equilibrium accuracy, unseen-family generalization, or exact multiplayer card removal. Frozen-value gaps are not full-game exploitability. Training screens, prospective tests and runtime checks remain separate.

The failed compile and process-identity attempts are preserved, with separately recorded repairs and unchanged model settings. Research policy files stay local and must not be loaded into the ordinary app.

[Detailed results](RESULTS.md) · [Experiment ledger](ledger.json) · [Accuracy/settling figure](accuracy-and-settling.png)
