# Behavioral pretraining followed by native GPU finishing: rejected

The four registered cases completed and their evidence verified. Neither pretrained candidate passes both unrestricted global accuracy and all six conditional per-hand checks. No second seed, sampled comparison or large run is admitted by this experiment. Port 56708 is unchanged.

## Matched results

All cases use the same 23,038-node six-player fixture, full 1024 samples, seed 42, gamma 15/horizon 1000. Each continues an immutable age-1000 save for at most 1000 additional native iterations, with combined checks every 25. Times include the original pretraining and complete finishing work.

| Pretraining epsilon | Averages at transition | Total seconds | Final unrestricted gap (bb) | Conditional checks | Qualified |
|---|---|---:|---:|---:|---|
| 0.0 | keep | 128.171 | 0.000388282 | 4/6 | No |
| 0.0 | reset | 127.353 | 0.000388312 | 4/6 | No |
| 0.01 | reset | 156.910 | 0.000514657 | 3/6 | No |
| 0.05 | reset | 163.026 | 0.000887572 | 3/6 | No |

All cases end at age 2000. No candidate reaches two consecutive combined passes. The ordinary keep/reset controls are essentially identical. Resetting averages does not explain a hidden speed benefit. The positive-epsilon candidates cost more and finish with fewer passing branches. No qualified speedup ratio exists.

## What failed

The earlier fixed 5% perturbation passed all six conditional checks but violated unrestricted global accuracy. Removing the perturbation recovers a small global gap, while coverage falls to three of six. This is a failed transfer of the branch-quality benefit, not a deployable improvement.

Both positive-epsilon candidates fail the same final paths: SB after open/fold/fold/call `[2,0,0,1]`, BB after another call `[2,0,0,1,1]`, and BB after limp/fold/fold/fold/fold `[1,0,0,0,0]`. All are evaluated with positive arriving mass. Thus the final rejection is not merely a zero-reach display or missing-range issue; individual relevant hands still put excessive probability on materially inferior actions.

The 5% candidate has worst relevant inferior-action probabilities of 61.7%, 62.8%, and 30.7% at those paths, respectively. The fixed gate is at most 10% probability on actions losing more than 0.1 bb for each hand with at least 0.25% conditional mass. These are one-action deviations under the existing coupled-deck continuation, not physical-deal or full-subgame accuracy claims.

## Correctness and preservation

Two transition numerical tests pass: exact preservation of every regret, age, configuration, locks and frozen averages; clearing only learning averages; independent native replay; captured/eager equivalence; immutable input save and roundtrip; cancellation; invalid-input rejection before mutation. Retained regrets are explicitly a warm-start initializer, not a claimed exact conversion of constrained regret history.

Full default release solver tests and the 6 postflop / 13 preflop GPU regression tests pass. Independent saved-file audits agree with the final benchmark checks. `check_behavioral_finish.py` verifies source/input/executable hashes, archived result hashes, schedules, timing, checkpoint gates and saved-file agreement. The transition API and executable remain research-only.

## Decision

Stop this registered transition without extending its iteration budget or tuning history scales. Record the useful mechanism evidence (fixed support improves branch learning), but do not promote a method that requires that support to maintain its apparent quality. A distinct next design must address persistent conditional learning while controlling unrestricted global loss, or reduce work through a different solver architecture. No large-game acceleration is qualified.
