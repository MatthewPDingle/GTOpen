# Can a smaller benchmark speed up screening?

Yes, potentially, but the existing small fixture is unsuitable as a mandatory
speed-gain gate. Retrospective paired results show it would discard two of the
four retained changes if we required a 1% small-game improvement before testing
the large game. Ratios below are candidate time divided by that experiment's
own control; each is the median of three paired runs.

| Change | Small runtime ratio | Large runtime ratio | Retained |
|---|---:|---:|---|
| C01 | 1.0081 | 0.9600 | Yes |
| C03 | 1.0238 | 0.9813 | No |
| C07 | 0.9637 | 0.9233 | Yes |
| C09 | 1.0177 | 0.9579 | Yes |
| C10 | 0.9509 | 0.9853 | No |
| C13 | 1.0367 | 0.9370 | No |
| C14 | 0.9467 | 0.9356 | Yes |

C01 and C09 are the missed retained wins. C10 also illustrates the opposite
problem: its small-game benefit does not meet the required large-game gain.
C13's large gain accompanied an unacceptable small regression; C14 fixed its
construction overhead. These are different workload responses, not proof that
all small-fixture timing is noise.

This table is selected: candidates already rejected on the large fixture often
have no small result. It cannot establish general correlation or predictive
accuracy. No medium fixture has yet been calibrated.

Recommended sequence: retain cheap adversarial correctness checks; calibrate a
medium fixture against known winners and losers (then held-out candidates);
use it to prioritize large trials rather than automatically reject absent small
gains. Keep full large-game paired timing and final regressions for retention.
Compilation and implementation costs remain even when a benchmark is smaller.

Evidence: `audit_small_screen.py` and `raw/small-screen-audit.json`. This audit
reads existing results and does not consume GPU time or change the live app.
