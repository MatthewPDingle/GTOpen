# Independent repeat of the board precision pilot

The completed 32-board pilot measured lower variance per work-time for all
three comparisons. It also had substantial class mean discrepancies and noisy
variance estimates. Repeat the same estimator comparison with new chance seeds
and four times as many samples. Do not pool this repeat with the pilot when
reporting its outcome.

Freeze the same first audited arm's played generation-77 policy and original
BB/BTN context. Use 128 uniform boards, seed 9279801, and 128 conditional
private-first deals per class (21,632 deals), seed 9279802. Retain all 169 classes,
original chance weights and exact preflop components. The complete old pilot
registration and review are dependencies. No further training or policy
selection occurs.

Keep the original three comparisons and definitions: primary raise minus call;
secondary call minus fold and raise minus fold. Report entry-weighted RMS
standard errors, variance times summed worker wall-time ratios, every class's
means/variances, regressions, and descriptive standardized mean discrepancies.
Use 127 degrees of freedom for sample variance and divide by 128 for variance
of each sample mean. Shared-board class errors remain correlated. No formal
confidence, playing-strength or 10x solver-speed claim follows from this repeat.

The arithmetic tests already passed on full supported private ranges. This
repeat asks whether the pilot's precision/cost direction persists with new
samples and whether large mean discrepancies shrink. If the primary cost ratio
is not below one, do not describe the method as more efficient based on the
pilot alone. If discrepancies remain concerning, investigate estimator bias or
tail behaviour before training integration. Do not select a favourable subset
of classes, stop early, extend sample counts, or switch policies after looking.

Use the qualified CPU job implementations with four workers and one math thread
each; no GPU. Admit jobs only when production is idle, at least 24 GiB RAM and
40 GiB S space remain, and observed CPU utilization is below 65%. Starting
requires 28 GiB RAM and CPU below 50%. Running bounded jobs may finish if
admission pauses. Preserve the main study's priority. One-hour run bound;
180-second job bound; failed/incomplete evidence remains separate.

Interleave the 128 board jobs and 338 private batches (466 jobs). Retain the
same reproducible compact board evidence and private transports as the pilot.
Require full job coverage and input-hash verification before running analysis.
Do not promote the method into training automatically.
