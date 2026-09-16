# GPU paired blend settling control (N35)

Registered after N34 selected alpha=0.25 and before GPU blend output. Uses the
unchanged frozen full N15 model and N20 full-double interface. Preserve N20's
zero-range guard; this experiment is independent of N32's uniform-prior change.
At eligible learned leaves blend 75% paired Balanced and 25% learned gross share.
Other leaves, legal-pair accounting, chip investment and output mass stay fixed.

First evaluate original paired Balanced, full learned and blended values on the
same N19 1500-step saved average policy. Every inspected hand/action value must
match 0.75*Balanced + 0.25*learned within 2e-6 bb. Also run the existing sparse
2/3/8-player safety fixtures, requiring finite outputs and chip conservation.

Both arms start from the exact same N24 paired-Balanced 500-step save. Continue
for 250 steps each (control then blend), then another 250 each (blend then
control), no warmup. Preserve intermediate saves and snapshots. Record the
750-to-1000 change at the same 17 decisions, gaps and learning seconds.

Exploratory settling success requires the blend's final gap <=0.005 bb, every
selected action-frequency change <=0.01, and own-range weighted hand total
variation <=0.01. A missing range is not a pass. Desired learning-time overhead
is <=10%, but one ordered comparison is not a repeated timing qualification or
a full cold-start time-to-target measurement. Do not loosen these thresholds.

No prospective accuracy claim follows from N34, and no deployment follows from
this test. New ranges require separately frozen fresh-reference validation.
Run only after N32 is terminal and all GPU work has exited; reserve at least
30 minutes before starting. Fixed night deadline: 2026-09-16 20:49:02 UTC.
