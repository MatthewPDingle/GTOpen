# Root-retained policy: next independent evaluation

Prepared during the fixed 78-update root-retention trial, before its final
quality results. This document does not authorize bypassing storage or
integrity gates. The existing continuation watcher runs training readback
only; no full evaluation is automatically queued.

## Question

Does preserving every sampled BB first-decision advantage improve the policy
that a fresh self-play run produces, relative to the prior exact-initial
pilot that kept those rows only in the shared reservoir?

The intended change is retention of the sampled BB root advantages. The
exact BTN initial jam response, training budgets, update count and prior
training seed schedule remain fixed. A post-hoc readout of the old trajectory
is not a substitute for this new training run.

## Admission

1. All 78 training updates and the independent raw-target/checkpoint audit
   must pass. Use all played generations 0 through 77 with the registered
   linear weights; exclude the unplayed generation 78.
2. Evaluate the complete exact all-in endpoint and independently reconstruct
   it. Report its changes whether favorable or unfavorable; there is no
   quality threshold used to select this candidate for the wider test.
3. `hu_root_retained_wider_admission_20260924.py --run` compares the complete
   CPU and CUDA banks on 64 independent control deals (seed 356231), including
   nonempty own-action histories across all four phases. Policy/reach tolerance
   is 1e-10 and payoff tolerance is 1e-8 bb. These are numerical controls, not
   strategic holdout results. The optional two-model fixture uses seed 356031
   and cannot satisfy full-candidate admission.
4. The completed two-model CPU transport/readback fixture has reconstructed
   six intervals and all 169 class choices. Existing corruption-rejection
   controls remain required.
5. Complete and verify the byte-preserving compression recovery first. It
   must recover at least 40 GB without deleting files. The new evaluation's
   allocation cap is the smaller of 50 GB and verified space recovered.
6. Project both logical bytes and actual file allocation from the candidate's
   admission batch with a 50% margin. The projections must fit a 120 GB
   logical cap and the allocation cap above. The full allocation cap plus
   40 GB reserve must be available at launch. A failed admission is not
   permission to raise the cap or silently reduce the evaluation sample.

No GPU admission or evaluation starts while the active training trial owns
the research GPU lock. Production activity prevents launch and stops a run.

## Fixed comparison

Use `hu_root_retained_wider_study_20260924.py --run` only after admission.

- Same BB-versus-BTN 2 bb open, 200 bb, 5% rake capped at 2 bb context as the
  prior pilot. This remains a single context, not general preflop validation.
- 256 training observations per starting-hand class, 43,264 total;
  response-training seed 356331.
- 131,072 independent incoming-population evaluation deals; seed 356332.
- Batch size 64; no data-dependent stopping or extra draws.
- Six reported alternatives: newly trained class response, always fold,
  always call, always raise, always jam, and the previous frozen response
  from `exact-initial-wider-study-v1/evaluation/response.json`.
- Exact fold/jam contributions and sampled residual call/raise contributions
  use the existing evaluator. Subsequent play remains frozen.
- Report all simultaneous intervals at family error probability 0.025.
  Reconstruct them independently from saved native payoffs.
- Report split-half response stability and frequencies. Do not choose a
  training half, weighting schedule or checkpoint after viewing results.

The old and new newly trained responses and evaluation samples differ.
Side-by-side estimates alone do not prove a statistically significant change.
The old frozen response is a fixed diagnostic, not a full best-response oracle.

## Storage and stopping

The output directory is new and inherits NTFS compression. Logical hashes
remain valid for the unmodified native readers. The controller checks actual
allocation and logical size during execution; volume free space is checked
separately. All completed files must be compressed at final verification.

Preserve 20 GB available host RAM and 3 GB available GPU memory. Evaluation
deadline is 12 hours and independent readback deadline is 2 hours. Stop on
the first resource, integrity, deadline or production-activity failure;
preserve evidence. No automatic retry, budget extension or deployment.

## Interpretation and subsequent decisions

A positive lower interval for a tested alternative demonstrates a remaining
weakness in this context. An interval containing zero does not establish
equilibrium. Exact all-in improvements cannot establish accurate calling
ranges. Numerical controls and storage savings are not poker-strength results.

After the complete evaluation and analysis, decide whether the retention
change warrants another independently seeded replication or whether the
larger remaining error is downstream continuation learning. Only then choose
the next experiment. Generalization to stack depths, other opening sizes,
other seats and multiway play remains outstanding. Do not deploy this
single-spot research policy as a general preflop model.
