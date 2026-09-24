# Range stability across the two training seeds

Prepared during replication training, before its endpoint output is available.
Use only each run's full, predeclared linear/linear average of generations 0–77,
after its independent training and endpoint audits. Do not select a seed or
checkpoint based on the resulting chart.

Report the BB initial fold/call/raise/jam frequencies in both runs, their signed
differences, and all 169 classes' action probabilities. Weight aggregate results
by the exact incoming hand mass, including card removal from the fixed BTN range.

Also report the incoming-mass-weighted total variation: half the summed absolute
action-frequency difference per hand, then averaged across hands. This measures
how much probability would need to move between actions to turn one run's range
into the other's. It can reveal large hand-allocation changes even when overall
fold/call/raise frequencies look similar. Keep units as probabilities in the
artifact; use percentage points in the written interpretation.

These are descriptive differences between two independently trained instances
of the same algorithm. There is no confidence interval or pass threshold, and
small differences would not prove that either range is accurate. Explain the
calling-range limitations alongside the restricted endpoint gains. Report
instability plainly, without averaging the two models together to conceal it.
