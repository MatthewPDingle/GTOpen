# N16: lower-cost arithmetic for the frozen N15 model

This changes numerical implementation only. N15's fitted model, inputs,
probabilities and acceptance criteria remain frozen. No training or refitting.

Compute the original 104 features and their standardization/clipping in double
precision. Convert each clipped standardized feature to float32, then accumulate
the 16 neural hidden units and their output in float32. Retain the original
double-precision linear model, range summaries, compatible-mass centering,
probability normalization and pot accounting. This avoids casting raw features
before potentially sensitive standardization. Do not use fast-math compilation.

Prepare both serial and parallel range summaries. The independent 12-case
physical-hand oracle must pass each variant's existing 0.0002 bb action-value
tolerance, pot accounting and finite-value checks. Direct action values must
also match the corresponding double-precision N15 GPU oracle within 0.0002 bb.
Neither CPU simulation nor compilation alone is GPU evidence.

Execute only after N15 passes its separately registered fresh accuracy screen
and its double-precision oracle. Choose the range-summary layout having the
lower N15 double-precision median runtime, using timing only. Then run three
interleaved original/mixed-precision repeats: 50 warm-up iterations and 100 timed
iterations on the unchanged benchmark tree. All original saved arenas must
equal the independently recorded ordinary baselines, and mixed-precision repeats
must be deterministic. Report complete arena differences versus double precision
as a diagnostic, together with inspected strategy and EV changes. Do not impose
unchanged arenas on a deliberately changed numerical implementation.

Additional acceptance limits after 150 iterations: inspected per-hand strategy
differences <=0.001 absolute probability and player EV differences <=0.001 bb
versus double precision. These do not bound uninspected strategy differences;
report full-arena discrepancies as well. Runtime target remains at most 10%
overhead versus ordinary Balanced. A passing fixed-work test still needs changed-
policy validation and does not authorize deployment or claim faster convergence.

One GPU controller at a time, no CPU numerical workloads during timing, live-app
idleness checks and the fixed 20:49:02 UTC deadline all apply. Port 56708 and
production files stay untouched. Experimental saves must not enter the live app.
