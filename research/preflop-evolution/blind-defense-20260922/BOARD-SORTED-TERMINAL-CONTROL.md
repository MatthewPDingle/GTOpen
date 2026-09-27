# Fixed-board terminal arithmetic control

The compact float64 terminal calculation agrees with explicit compatible-hand
pair sums in all 24 fixtures. This qualifies one arithmetic component for a
future board-first evaluator; it does not qualify full tree propagation,
chance weighting, range accuracy, or a production deployment.

Four physical river boards were ranked using the native seven-card evaluator.
Each has 1,081 legal private holdings. Fixtures cover uniform, random, actual
BB, actual BTN, one-hand, and zero opponent reach. Each also checks unequal,
reordered holding lists, omitting zero opponent weights. One board is a royal
flush, so every legal pair must tie. An identical private holding cannot be
its own opponent.

The independent reference constructs every compatible pair explicitly and
compares native ranks. The candidate instead uses sorted rank prefixes and
per-card subtraction. Both return unnormalized opponent masses, preserving
card removal. Maximum errors:

| Quantity | Absolute error |
| --- | ---: |
| Win/lose/tie/valid mass | 1.43e-12 |
| Arbitrary terminal payout | 1.64e-10 |
| Constant fold payout | 1.10e-11 |
| Unequal/reordered lists | 1.43e-12 |

Ten malformed-input checks passed. The v2 adapter adds consistent strength
checks for holdings present in both lists and rejects negative ranks; v1 stays
unchanged to preserve source bindings. The result binds the executable, native
source, evaluator, context and Python sources by SHA-256.

The control took 0.30 seconds on one CPU thread, with no GPU use. Recorded
component timings are not a comparative whole-solver benchmark: the dense
reference preconstructs its matrices, while the compact call includes prefix
construction and validation. A performance claim needs an equivalent workload
with tree propagation and repeated policy evaluation.

Next: preserve the private-first chance law and own-hand/public-history policy
inputs while testing fixed-policy tree propagation. Do not replace the current
registered study or present this control as playing-strength evidence.

## Resource use and current study

Both registered stratified training arms completed 78 updates on September 27.
The first full independent audit passed; the second is running with its
registered four workers. Complete-bank evaluation and the two-worker CPU
trajectory diagnostic are queued. Training completion alone does not qualify
the model's accuracy.

The user's hardware is a 16-core/32-thread Ryzen 5950X, 128 GB RAM and a 24 GB
RTX 3090. Resource admission must check competing work, production activity,
available RAM/VRAM and free disk. Use independent CPU work alongside GPU work
when it actually reduces elapsed time. Preserve the ongoing audit rather than
restart it to change worker counts. Previously qualified eight-worker audit,
bulk checkpoint restoration and faster directory scanning remain candidates
for the next registered pipeline; none is silently patched into this study.

At this handoff, a three-second sample showed 18.7% CPU and 104.5 GiB available
RAM. Free disk was about 59.5 GiB on T and 262.3 GiB on S. These are snapshots,
not resource reservations or future guarantees. Avoid new large archives on T.

Evidence: `board-sorted-terminal-control-v1-result.json` and
`weighted-stratified-study-v1-training-result.json`.
