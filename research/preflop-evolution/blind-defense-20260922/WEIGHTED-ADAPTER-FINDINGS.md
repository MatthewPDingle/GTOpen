# Stratified training adapters: root, table and native visits

The separately typed adapters passed their bounded controls on 27 September
2026. They are research components, not a deployed model or evidence of stronger
poker play. The original production code and unweighted trainer are unchanged.

## What passed

- Complete 512-deal source generations are checked against the original game's
  physical range support, class masses and sampling-weight formula. Each native
  subbatch is bound to its physical cards, source offsets and query digest.
- Two synthetic root updates matched direct weighted sums exactly. Restoring
  after the first update and continuing reproduced the uninterrupted state and
  policy exactly. Reordering paired subbatches agreed within 1e-12.
- Preflop table weighted means differed from direct per-visit arithmetic by at
  most 1.055e-15. Unit weights reproduced the old table's scores and probabilities.
  Public checkpoint and table formats distinguish weighted from unweighted data.
- The native traversal control processed the first 32 deals of a fresh 512-deal
  stratified generation using the existing native binaries and a uniform policy.
  There were 661 BB and 110 BTN learning visits across all four streets. A
  97-entry reservoir per player forced replacement. Retained weights matched an
  independent mapping through the native trace's explicit deal indices exactly.
  Target values, retained row selection and RNG states matched the old ingester;
  the independent target oracle had zero maximum error.
- Nineteen source/root/table rejection checks and five native-ingestion checks
  passed. Misplaced weights, wrong source slices and corrupted late targets did
  not mutate the checked accumulators/reservoirs or consume their RNG draws.

Weights multiply fitting losses and root contribution sums. They do not also
scale the stored target values. Preflop tables use weighted means and retain
actual visit counts separately from accumulated importance mass. The exact BTN
population-matrix update remains outside sampling weights.

## Resources and evidence

The published root/table control took 1.44 seconds; native ingestion took 6.25
seconds and wrote 10,331,753 bytes. These are small serial CPU checks, with no GPU
allocation, application restart or production solve. The same-size development
fixture is retained separately (about another 10MB). No large study was started.

Registered outputs:

- `weighted-root-table-control-v1-registration.json` and `-result.json`
- `weighted-native-ingest-control-v1-registration.json` and `-result.json`
- Native inputs/trace and weight audit under
  `T:/GTOpen-research/weighted-native-ingest-control-v1/`

The registration files bind exact source and input bytes; the native result also
binds every generated fixture. Root target transport tests used explicitly
synthetic values, not fabricated poker outcomes. The native visit test uses real
traversal output but covers one 32-deal slice, not a full training generation.

## Remaining work

Connect these components through a separately versioned model/checkpoint and
policy reader. The trainer must sample a full 512-deal generation once, then
slice into native subbatches without losing weights. Reuse the qualified weighted
GPU objective, update the exact BTN matrix once per generation, and preserve the
played-policy averaging rules. Verify restart and a complete small training run
before a matched baseline/stratified poker experiment.

For the pilot, measure native generation versus GPU fitting time and size any
worker pool against current host load, memory and user activity. Faster coverage
is the hypothesis; improved ranges and wall-clock convergence remain unproven.
