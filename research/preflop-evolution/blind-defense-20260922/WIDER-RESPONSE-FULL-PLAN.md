# Fixed wider evaluation of the later-weighted candidate

Prepared after the audited averaging screen passed and before new response
training or population testing. One fixed candidate: the complete fresh
78-generation linear-weighted bank, excluding unused generation 78. The
200 bb BB-versus-BTN game and incoming ranges remain unchanged.

## Sample plan

- Train a class-only BB root response on exactly 256 conditionally sampled deals
  for each of 169 classes: 43,264 deals, seed 224331, 64-deal batches.
- Use exact population fold/shove values for this same frozen opponent and
  sampled call/ordinary-raise values. Minimum class support is 16; otherwise
  retain baseline. Choose the first maximizing legal action. Do not select
  based on test outcomes. Preserve two 128-per-class training halves only as
  a disagreement diagnostic.
- Save and hash the responder and residual bounds before creating the separate
  population sampler. Test exactly 131,072 IID full-population deals, seed
  224332. The prior numeric-control seed 224231 is separate and excluded.
- Evaluate the trained response and always-fold/call/raise/shove alternatives.
  Keep downstream play frozen. Exact fold/shove offsets plus uncentred
  call/raise residuals retain the original estimand.
- Physical bounds are computed from the frozen candidate, alternative, stack
  and dead money before test sampling. Use the already controlled bounded
  empirical-Bernstein calculation, family error .025 across all five
  alternatives, with one final look at the fixed test count.

No early stopping on apparent gain, checkpoint selection, or automatic budget
extension. Preserve and report all alternatives and stability results regardless
of sign. Negative fitted gain is not an upper bound on the best response;
wide intervals are inconclusive.

## Admission and resources

The complete-bank 64-deal numeric control must pass CPU/CUDA probabilities,
own-reach weights and native integrated root payoffs across all four streets.
Its policies are given unlabelled visible queries; labels only enter terminal
valuation. Verify its immutable source/model/cache identities before launch.

Use a newly NTFS-compressed output directory. Require current free SSD space
to cover 1.5 times the control's allocated bytes per deal for all 174,336 deals,
plus the 40 GB reserve. Keep all decoded artifacts and hashes. Compression does
not change the transport or mathematics. Flushing precedes final allocation
measurement; buffered writes can temporarily consume extra space.

Evaluation has a hard parent-process cap of 12 hours, followed by at most two
hours for independent readback. Maintain 20 GB free host memory, 3 GB VRAM and
40 GB free SSD. Stop for production activity, resource breach, numeric/integrity
failure or deadline. The parent monitors wall time, host and disk every five
seconds; the worker additionally checks GPU availability during inference.
Final retained output caps are 44 GB allocated and 120 GB logical; live free
space checks protect the drive throughout. Preserve partial evidence on failure.
Do not restart a partial run as if it were complete.

The separate readback replays both chance streams, all class response choices,
both training halves, native payoff files and all residuals/intervals with
scalar arithmetic. It verifies model/input identities but does not retrain
networks or independently rerun native poker traversal.

## Interpretation

This measures specified profitable deviations at BB's first decision, including
ordinary calls and raises and their frozen postflop continuations. It does not
cover arbitrary changes to downstream play, all positions or stack sizes, or
establish full-game convergence. The already exact BTN fold/call test remains
separate. No deployment follows automatically from this run.
