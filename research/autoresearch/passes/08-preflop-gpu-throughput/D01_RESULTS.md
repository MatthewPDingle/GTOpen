# Exact distribution inventory: prototype admitted

The read-only GPU normalization inventory passes and preserves every regret
and average entry and the saved iteration. The classifier test proves full
bit equality after hash lookup, including deliberately colliding hashes,
single-bit differences, signed zero, opponent order and repeated opponents.
An initial compile failure (ambiguous literal type) remains in raw evidence;
the corrected classifier and both inventories pass.

| Native saved state | Policy | Active CDF slots | Unique distributions | Exact duplicate fraction | Weighted terminal duplicate fraction |
|---|---|---:|---:|---:|---:|
| Small, 23,038 nodes, age 1000 | Current | 19,498 | 15,021 | 22.96% | 3.31% |
| Small | Average | 31,094 | 29,004 | 6.72% | 0.033% |
| Large, 1,567,754 nodes, age 1050 | Current | 1,290,128 | 862,854 | 33.12% | 2.84% |
| Large | Average | 2,635,602 | 2,419,347 | 8.21% | 0.319% |

Counts sum traverser-local work. No cross-traverser persistence is assumed.
The large game uses the unchanged batch32 CDF allocation (8,444,664,320 bytes)
and 262,343,432 normalized bytes. No CDF/terminal kernel was bypassed in an
actual solve; these counts are not measured speed or memory improvements.

The registered 20% duplicate gate admits a device-side exact CDF deduplication
prototype. Terminal equity caching does not clear its corresponding gate and
is not pursued here. Dense average checks offer less reuse than learning.

## C01 registered prototype

Build a temporary per-traverser open-address table over immutable normalized
vectors. Hashes locate candidates; compare all 169 float bit patterns before
aliasing. Keep opponent order, all1024 samples, original batch32, scan and
terminal arithmetic. Clear the table each invocation, including repeated
checks after learning; no lifetime across different normalized scratch states.
Each alias references an inserted representative, never an alias chain.
Bound probing; collision overflow safely computes the original independent
CDF. Exact duplicates skip only their CDF writer, and terminal readers follow
the alias. Preserve true-zero/own-zero behavior and minimum-memory fallback.

Keep production dispatch unchanged and the prototype research-only. First
prove exact terminal and full-arena equivalence on small fixtures including
fixed policies, current/average sources, graph replay and positive/zero
transitions. Then compare the mature large saved game and small control at
fixed iterations against the same executable with reuse disabled. Failures
or regressions stop the candidate; do not compensate with fewer particles or
changed accuracy checks. Subsequent retention needs the paired/full-suite
gates in program.md.
