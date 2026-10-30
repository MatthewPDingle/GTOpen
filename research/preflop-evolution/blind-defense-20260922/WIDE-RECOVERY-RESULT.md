# Full-support GPU recovery control

**Passed, with no production changes.** All eight player sweeps returned
bit-identical values and complete checkpoint bytes compared with a continuously
resident reference. This is an engineering result, not evidence of improved
preflop strategy or convergence.

## What was tested

The qualified BB-versus-BTN context retained all 169 BB classes and the same
96 BTN classes above the previously registered entry threshold. On KsQd9d,
these become 1,176 and 535 physical hands. The call continuation has a 4.5 bb
pot, 198 bb remaining stack, and 5% rake capped at 2 bb. Its unchanged three
street menu uses 50% bets/leads, pot-sized raises and one raise per street.

The reference ran four iterations, with two alternating player sweeps each.
After the reference and its GPU workspace were destroyed, the candidate
reconstructed its GPU state before every sweep and restored the previous
checkpoint. Both received the same changing reaches, including zero BB reach
at iteration two and subsequent reentry. Every candidate checkpoint was
compared byte-for-byte with its corresponding reference. The external review
also compared all 16 file SHA-256 hashes in pairs.

## Measurements

| Measurement | Result |
|---|---:|
| Exact player-update comparisons | 8 / 8 |
| Canonical state per checkpoint, excluding 72-byte header | 3,440,369,296 bytes |
| Total immutable checkpoint writes | 55,045,909,888 bytes |
| Largest shared GPU workspace | 15,750,056,040 bytes |
| Candidate reconstruction and checkpoint import | 51.02 seconds |
| Candidate sweeps | 6.11 seconds |
| Candidate checkpoint exports | 129.40 seconds |
| Entire native control | 332.53 seconds |
| Guarded elapsed time | 334.50 seconds |

These are eight-sweep control timings, including deliberately frequent durable
snapshots. They are not production solver throughput. The guard sampled at
least 93.21 GB free host RAM and 7.03 GB free VRAM, checked production idleness,
and terminated successfully. Independent review revalidated 115 frozen source,
executable and input hashes. No retries were needed.

## Consequence

An individual wide continuation can fit and can be unloaded without changing
its state. The full 112-board, three-branch study still requires about 1.105 TB
of canonical state under the current design. This test neither admits that
forest nor qualifies other boards/branches. Existing reload/export overhead is
also substantial. The next investigation must address persistent state and
runtime, rather than treating this pass as a new accurate blind-defense model.

Evidence: `wide-cold-replay-v1-registration.json`,
`wide-cold-replay-v1-review.json`, `hu-wide-cold-replay-v1.log`, and the adjacent
guard resource/status/freeze records. The 16 raw snapshots remain local at
`S:/GTOpen-research/hu-wide-cold-replay-v1`; they are not added to Git.

Registration SHA-256:
`ccc006708cbbd59e1b976e8f1432b6b81a5779b5636f1bd6aac7df765af3471f`.
Native result SHA-256:
`cbc64dd80c831101ff721fa68e31163ecd6e13c314a4388cff9e85ffafc4a384`.

Production port 56708 remains untouched. The broader study is active.
