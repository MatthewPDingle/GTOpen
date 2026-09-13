# D14: warp-local rank sharing execution screen

Registered before the census. D13 schedule B remains unimplemented. C18's
cross-warp implementation was exact but slower; do not repeat that campaign.
GPU preflop research only, retained C14/R03 and port 56708 unchanged.

Consider one leader per identical (lower,upper) pair within each original
contiguous 32-hand warp. Keep all 169 hand accumulators, 1024 samples, ordered
opponents and quadrature additions. No cross-warp compaction. Test the claimed
mechanisms: fewer original arithmetic instruction slots at warp granularity,
or fewer distinct CDF load sectors. Additional election/shuffle instructions
are excluded, favoring the proposal. This is a source/architecture model, not
compiled instruction counts, hardware counters, cache misses or timing.

Use D13's hashed exact rank table and D11's opponent-count census. For all six
warps in each sample, elect first leaders using a set; independently elect last
leaders by pair comparison. For lower and upper loads separately, compare the
distinct word addresses and 32-byte sectors at all eight float-aligned base
offsets modulo 32. Include the partial nine-lane warp and synthetic all-equal,
all-distinct, alternating and boundary-spanning groups. Do not merge lower and
upper load instructions, opponents, samples or warps in transaction accounting.

Count original arithmetic source slots per nonempty warp as O+3*Q*O+2*Q,
Q=(O+2)//2; an FMA is two source operations, not two native instructions.
Original ordered accumulations still require all hands. If every warp retains
a leader, its original product arithmetic path remains needed. Compute both
saved-game learning/check histograms, and reconcile D13's active-lane savings.

Admission requires at least 10% fewer modeled original warp arithmetic slots
or modeled requested sectors in both large learning and checks. Otherwise
decline this particular prototype before GPU implementation. This gate does
not prove runtime improvement impossible: compiler/register effects and
sub-warp hardware behavior are outside the model and would need a separate
mechanism and proposal. A pass would still require exactness and full timings.

One guarded host census, cap 180 seconds; immutable input/script hashes and
independent verifier. No new GPU build, driver changes or runtime modifications.

Architecture basis: NVIDIA CUDA Best Practices Guide, sections Coalesced Access
to Global Memory and Branch Predication, accessed 2026-09-14:
https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html#coalesced-access-to-global-memory
https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html#branch-predication
For compute capability 6+, accesses are served in 32-byte units; duplicate
addresses do not require an additional sector. Predication disables lane work
without skipping scheduling of the instruction itself.
