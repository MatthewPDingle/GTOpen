# Showdown correction now passes research training integration

The correction has been exercised in the research learner. Two new-seed CUDA updates completed, followed by a deterministic restart and replay. The live application and production solver remain unchanged. This establishes implementation readiness for a matched experiment, not improved preflop ranges.

## What was checked

- Two updates of 64 fresh physical deals each, with the existing 512-step CUDA fitter. All coefficients were frozen before sampling.
- A distinct version-8 model/checkpoint and separately typed root accumulator preserve the coefficient identity. Older model/checkpoint readers reject this format.
- The original root targets remain saved. Only call/raise learning targets receive the correction; fold and exact initial-jam action values remain unchanged. No showdown information enters current-policy features.
- Native showdown scores match the independent five-card reference for all 128 deals. A separate reader reconstructs the corrected action targets, advantages, class counts, and accumulated root regrets with zero numeric discrepancy. The largest expected advantage correction, integrated over the exact conditional outcome probabilities, is 2.05e-15 or less.
- Restoring the first checkpoint and repeating the second update reproduces the final checkpoint, model, exact BTN state, root state, action RNG, reservoirs, and native subbatch artifacts. Incomplete generations and foreign coefficients are rejected without partially updating the accumulator.
- Current CPU/GPU policy differences are below 2.14e-14. A separate complete played-bank check covers 29,019 existing native observations: averaged probabilities differ by at most 3.74e-14 and own-action reaches by 1.55e-14. It excludes the final unplayed model and rejects reordered/incomplete history.

## Cost and limits

The two small updates took 12.17 and 10.16 seconds. The control including replay and its internal checks took 54.39 seconds, excluding admission inventory. It retained 113.1 MB, including replay evidence; 7.4 MB was checkpoint/model objects. The independent scalar reader took 2.48 seconds and the played-bank check 10.72 seconds. These are tiny-run integration timings, not evidence of faster full training or improved convergence.

The prior archived diagnostic reduced call/fold variance by about 30%, raise/fold by 23–29%, and raise/call by only 6–11%. That remains exploratory evidence from old fixed policies. This control does not repeat or upgrade that statistical claim.

## Next experiment

Compare the corrected learner against the otherwise identical postflop-integrated baseline on fresh matched training seeds, then evaluate on separate unseen deals using unchanged game payoffs. Test stability across seeds as well as payoff differences. Do not reuse coefficient-fitting outcomes as confirmatory evaluation data, clip corrected targets, select the best diagnostic bank, or deploy on the basis of this gate.

Before launching that larger experiment, qualify compact retention for newly generated evidence and admit the full projected storage cost. The inventory before this control was 793.32 GB against the existing 800 GB allocated limit, with a further 2 GB metadata reserve. Keeping all new raw transports would not scale safely. No older evidence was deleted or compressed during this control.

Evidence: `showdown-training-integration-control-v1-{registration,result,status,independent-review}.json` and `showdown-policy-bank-control-v1-result.json`; full new control files are in `S:/GTOpen-research/showdown-training-integration-control-v1`.
