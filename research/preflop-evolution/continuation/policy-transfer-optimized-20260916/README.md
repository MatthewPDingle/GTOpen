# Policy transfer for optimized N15 implementations

Apply the unchanged four-context, 200-reference protocol in
[the original policy-transfer study](../policy-transfer-20260916/README.md)
to a qualified N16 or N17 implementation of the same frozen N15 model.

Require N15's registered accuracy pass, the selected implementation's GPU oracle
pass and its completed three-repeat runtime target. Choose N17's faster double
or mixed variant by measured median runtime alone. N16 uses the variant already
selected in its timing record. Freeze that choice, all model/implementation
evidence, this adapter and the original protocol before resuming policies.

Resume repeat-zero ordinary and selected policies from 150 to 500 iterations.
Freeze both BB-call leaves from each, then solve 50 newly reserved stratified
flops per context. All four contexts must improve weighted value error at least
15% versus Balanced and regress at most 10% versus the previous conditional
predictor. No refitting, threshold changes or dropping contexts. The same
reference-quality checks, range-cleaning disclosure, approximate multiway
scope, source-scenario limitation and deadline apply.

Successful prediction and runtime screens do not automatically qualify the
resulting policy. No deployment or live-app changes are authorized by this study.
