# Relative hand inputs help, but the accuracy gate still fails

The registered 362-versus-387-input comparison finished successfully, and its
independent CPU readback passed. Giving the model explicit facts about what its
hole cards add to the visible board reduced fresh-test average decision loss by
46.11% and 23.87% in the two paired seeds. Both clear the predeclared 20% relative
improvement requirement. Neither meets the separate absolute accuracy limit.
Preserve these findings as a useful representation result, not a promoted model.

## What was tested

The candidate adds 25 visible-card facts: the board's own hand category and
tiebreak ranks, whether the player merely plays the board or improves it, and
whether zero, one or two private cards are needed. These inputs contain no
opponent cards, equities or target labels. They add 3,200 trainable parameters
across the two player networks; this is not an equal-parameter-count comparison.

Both arms used the same 512 fitting boards, 8,192 updates, optimizer, batches,
targets and two 64/64 networks. Extra input weights started at zero; initial
predictions and common batch draws were exactly paired. Model selection used
only 32 fresh validation boards. All four checkpoint identities were frozen
before labels were prepared for the 64 fresh final-test boards. The 96 new board
groups exclude all 692 earlier groups; all 608 fitting/validation/test groups
are distinct within this comparison.

The reference is a terminal river Fold/Call decision against a uniform legal
opponent hand distribution. It prices the call exactly for this restricted
situation. Depths 20/40/100/200/400bb were fitted; 60/150bb were excluded from
fitting and selection, but their geometries had been studied previously.
Decision rows are correlated combinations of board, hand and public price;
their large count is not a count of independent poker hands or board samples.

## Predeclared outcome

The primary mean weights 60bb and 150bb equally after dividing decision loss by
starting stack. Lower is better. The combined gate also requires mean loss at
most 0.1% of starting stack at each excluded depth.

| Seed | Baseline loss / stack | Candidate loss / stack | Reduction | Combined gate |
| --- | ---: | ---: | ---: | --- |
| 9296901 | 0.28564% | 0.15394% | 46.11% | Fail |
| 9296902 | 0.25450% | 0.19374% | 23.87% | Fail |

| Seed | Depth, bb | Baseline mean loss, bb | Candidate mean loss, bb | Required maximum, bb |
| --- | ---: | ---: | ---: | ---: |
| 9296901 | 60 | 0.15898 | 0.09453 | 0.060 |
| 9296901 | 150 | 0.45946 | 0.22549 | 0.150 |
| 9296902 | 60 | 0.14728 | 0.11629 | 0.060 |
| 9296902 | 150 | 0.39530 | 0.29050 | 0.150 |

These are losses per evaluated terminal decision under the diagnostic's sampling
distribution, not a preflop win rate, bb/100, or whole-game exploitability.
The candidate remains approximately 1.50-1.94 times the absolute error budget.
No threshold, checkpoint selection rule or training budget was changed after
seeing these final results.

## Remaining weaknesses and adverse evidence

At 150bb, the candidate's 99th-percentile losses are 6.72/8.42bb and maxima are
63.62/42.73bb. These improve on the paired baseline tails but remain substantial.
The average improvement does not establish reliable decisions for every hand.

Pair, high-card and two-pair hands contribute most of the remaining aggregate
loss. The second seed's high-card contribution is essentially unchanged, and
some less common categories (including flushes and straights) worsen. These
unfavorable slices remain in the original result and the analysis JSON. Both
actors and all populated price bands improve in aggregate; price bands requiring
40% equity or more have no rows in the two held-out geometries and provide no
support for generalizing to those prices.

The selected candidate has worse validation mean than the selected baseline in
both seeds, despite its improvement on these fresh final boards. The first
baseline selected step4096; the other three selected step8192. This difference
between validation and final-test outcomes, the limited board sample and only
two seeds argue against calling the improvement universal or statistically
settled. Absolute numbers from earlier studies used different fresh boards and
seeds and must not be treated as a paired regression comparison.

## Verification and cost

Independent NumPy CPU inference checked 1,419 file
identities and reconstructed 185,966,592 final decision rows.
Maximum CPU/CUDA context-mean difference was
1.1939674e-06bb, below the unchanged
0.0001bb tolerance. The readback also verified board separation, exact paired
initialization and batch generators, validation-only model selection, the frozen
selection before test labels, and both final gate outcomes. It recomputed
context means and gates; it checked partition row coverage but did not
independently recompute every reported tail percentile or subgroup mean.

Main work took 491.719 seconds, including
56.047s of earlier CPU preparation and
435.672s for the GPU-stage invocation. The latter includes
inventory, fitting, validation, final-test preparation and evaluation. Independent
readback took 191.391s. The preceding GPU admission wait is not
included in those work times.

Baseline fits totaled 137.640s; candidate fits totaled
161.500s, approximately 17.3% more. These sequential single runs
include validation/checkpoints and are not an isolated speed benchmark. Peak
CUDA allocation was 1044.03MB, with
1107.30MB reserved. Main-run evidence used
6.52MB allocated and
7.19MB logical storage, before this readback
and analysis. Production on56708 was not changed.

## Implication and recommended next work

Explicit hand-versus-board information is a promising component: it improved
the paired fresh-test average in both runs, whereas merely extending training
did not consistently help in the earlier budget comparison. It is still not
accurate enough to serve as a general continuation model. These diagnostic
weights cover only terminal Fold/Call and must not be installed as an all-street
strategy or described as improved preflop ranges.

The next proposed study should improve and balance training/validation coverage
of hand-versus-board relationships, with particular attention to ordinary
high-card and pair situations as well as rare board-made hands. Keep the two
representations paired and retain independent fresh boards and the original
absolute accuracy target. This is a proposal; no new study has been launched.
This completed final test must remain a test, not become the tuning set.

Only after resolving that accuracy gap should a separately registered comparison
test multiple decisions and realistic action-conditioned opponent ranges, using
the independently checked weighted terminal reference. Demonstrating better
preflop ranges still requires all-street policies, legal betting options,
stack/rake/position variation, and independent whole-game evaluation. This result
does not complete that broader goal.

Evidence: `stack-board-relative-learning-v1-result.json`, `stack-board-relative-learning-v1-readback-v1.json`,
`stack-board-relative-learning-v1-analysis-v1.json`, the unchanged registration and frozen selection.
No new experiment, GitHub push or deployment was performed for this analysis.
