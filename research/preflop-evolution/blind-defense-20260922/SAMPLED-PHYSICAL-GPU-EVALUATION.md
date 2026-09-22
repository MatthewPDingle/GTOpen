# Faster evaluation of the same frozen pilot

The physical pilot's accuracy evaluation is now running through a persistent
CUDA model bank. This changes evaluation execution, not the training algorithm,
incoming ranges, betting tree, sample plan or candidate selection. It is not a
production preflop-solver speedup or evidence of better poker ranges.

## Why change execution

The original two-thread CPU evaluator repeatedly encoded visible observations,
loaded 78 model pairs and evaluated them for every 16-deal batch. Early throughput
would not complete the registered 1,536 batches within two hours. No test outcomes
were inspected to make the execution decision.

The new bank keeps all played models on the GPU, encodes features once per batch
and evaluates eight models together. It still computes each model's own prior
action reach, weights that model's strategy by that reach, and accumulates models
in order. Network arithmetic is float32 with TF32 disabled; regret matching and
reach accumulation use float64. The result is numerically comparable, not
bit-for-bit identical to the CPU implementation.

## Numerical and timing evidence

The predeclared control used the old 16-deal fixture and all 78 played models:

| Measurement | Result |
|---|---:|
| Decision observations | 7,277 |
| CPU averaging | 11.328 seconds |
| GPU bank loading, once | 1.750 seconds |
| GPU averaging, eight-model chunks | 0.547 seconds |
| GPU averaging, one-model chunks | 0.750 seconds |
| Largest CPU/GPU policy difference | 0.000014281 absolute probability |
| Largest CPU/GPU payoff difference | 0.000043910 bb |
| Peak allocated CUDA tensors | 86.54 MB |

The averaging step was about 20.7 times faster in this single control. It ran
alongside the two-thread CPU study, so this is not an isolated repeated benchmark
or a claim about end-to-end solve speed. Tensor allocation excludes CUDA context
overhead. Zero-support states matched and both CPU/CUDA RNG states were preserved.
Independent readback reconstructed the policy and all five paired payoff-profile
differences from saved artifacts.

Before admitting the GPU test stream, a further gate compared the first **256
responder-training deals** with their completed CPU counterparts: **116,404
decision observations**, maximum policy difference **0.000066690** (0.006669
percentage points), maximum payoff difference **0.000125379 bb**. Both fit the
unchanged tolerances of 0.0001 probability and 0.001 bb, set before the old-fixture
control. These checks concern numerical execution, not model strength.

## Unchanged statistical study

The GPU registration inherits the exact frozen pilot checkpoint, played
generations 0–77, 8,192 responder-training deals, 16,384 separate test deals,
minimum 16 training observations per class and seeds 49101/49102. Generation 78
is unused and excluded. The five comparisons and one final statistical look
remain unchanged. Using the same deal streams makes the CPU/GPU executions
comparable; they are not independent confirmations.

The GPU controller retains a two-hour limit, production-idle checks, 20 GB free
host RAM, 40 GB free SSD and a 30 GB study-storage limit, and adds 3 GB free VRAM
and the shared GPU research lock. It stops its own worker on a failure or
production activity. There is no automatic retry, extension, or partial-result
accuracy claim. Production and the range preview remain untouched.

After the numerical gates passed, the slower duplicate CPU worker was manually
stopped. Its controller recorded `Evaluation worker failed: 15`; this was the
requested termination, not an unexplained numerical failure. Its **87 completed
batches / 1,392 training deals** were verified and preserved, with no published
responder and no test stream. The unfinished next batch is excluded. The GPU run
starts its own complete deterministic stream; no partial CPU results are spliced
into its estimates.

## Evidence and implementation

- `sampled-physical-gpu-bank-v1-registration.json`, `-result.json`,
  `-review.json` and `-independent-review.json`: old-fixture control.
- `sampled-physical-root-study-gpu-v1-registration.json` and
  `-cpu-comparison-review.json`: frozen study and 256-deal numerical gate.
- `sampled-physical-root-study-v1-supersession-intent.json`,
  `-supersession-review.json` and terminal `-status.json`: CPU disposition.
- `sampled_physical_gpu_bank_v1.py`: persistent inference and averaging.
- `sampled_physical_root_evaluation_cuda_v1.py`: separate GPU evaluation path.
- `hu_sampled_physical_root_gpu_study_20260922.py`: preparation and guarded run.

No completed poker-accuracy result is available at this point. The original
limitations still apply: fixed incoming ranges, two live players, restricted
postflop betting, no earlier folded-card information, and a root-only deviation
test rather than an unrestricted best-response upper bound.
