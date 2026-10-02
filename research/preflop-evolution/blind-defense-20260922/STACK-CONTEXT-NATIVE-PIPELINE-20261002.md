# Native preflop training pipeline: 2 October 2026

The new cumulative preflop learner now completes a genuine native collection,
two-network CUDA fit, and authenticated checkpoint restoration. A bounded
20bb software/resource profile passed in **91.531 seconds**. The independent
retained-artifact audit passed in **27.968 seconds**. This establishes that the
components work together on this small case; it does not establish good poker
ranges, convergence, an improvement over the old learner, or production readiness.

## What ran

The profile used the existing BB-versus-BTN entry at 20bb, the inherited BTN
opening range and the previously qualified native executables/all-in cache.
It collected two declared random full boards, evaluating all 1,081 legal
private holdings per actor. Every supported preflop decision uses the cumulative
expected-target state. Separately, 169 class-stratified physical deals in thirteen
ordered subbatches supplied postflop targets with the existing posterior64 river
method. Sampled preflop visits were excluded from retention: 226 for BB and 77
for BTN. Postflop visit counts were 1,952 and 389, with reservoir capacities 512.

Two board workers and three physical-deal workers ran concurrently on the CPU;
the parent used four BLAS/Torch threads and CUDA policy inference/fitting.
TF32 stayed off. Both fits used four steps, with the explicitly declared test
preflop loss fraction 0.25. These small software-control budgets were not
selected as sufficient scientific training budgets.

The initial uniform model was the only played model. The newly fitted model
was retained for the next cycle, rather than incorrectly included in the played
average. The complete checkpoint restored cumulative regrets/targets, both
networks, the played bank, sampler state, action RNG and both retention RNGs.
The run released its owned lock and did not change production on port 56708.

The one-shot registration, original attempt, raw exports, immutable objects,
metrics and terminal result remain under
`S:\GTOpen-research\preflop-expected-native-cycle-profile-v1`.
The source was run from the preserved workspace staging directory. Publishing
the same source in the repository does not authorize rerunning that attempt;
the profile CLI refuses a started attempt.

## Verification and preserved failures

Software controls cover both 362/387-input coordinators, all five fitting
depths and two withheld registry depths, complete-cycle publication/restoration,
partial-context/partial-fit rejection, source/native receipt binding, and ordered
postflop-only admission. There were six coordinator refusals per representation.
Board admission accepted one valid result and refused 52 altered cases, including
finite values rehashed to look authentic; a genuine raw-tree replay rejected them.
The owned subprocess fixture accepted two real Python child launches and refused
17 invalid/failed cases. These are software fixtures, not poker accuracy tests.

The independent actual-run audit verified all 127 registered source/executable/
input pins, both full board requests and native-tree target replays, all thirteen
physical batches/169 deals, and all 117 native receipts. It reconstructed the
final reservoir arrays, weighted cumulative targets, RNG states, objective
bindings, network hashes and complete checkpoint/metrics/release. Its retained
manifest covers all 809 files. It shares qualified target components and the
native payoff oracle with the runner; it is not a second poker-payoff implementation.

The first coordinator control reached the complete cycle and rejection checks,
then failed while writing its summary because Registry has no heldout_contexts
attribute. A separate corrected control derives those names from the manifest.
The failed control source and its completed artifacts remain preserved.

The first independent audit used one BLAS thread and failed on the exact-term
hash in the generation envelope. A separate diagnosis found that replaying the
declared four-thread parent runtime reproduces the entire envelope exactly.
The separately qualified v2 audit kept the exact gates and original input data.
The v1 failure/source and diagnosis remain preserved; no native profile or
scientific attempt was retried. Bitidentical replay requires the same floating
reduction runtime. This must be pinned in a future resumable study.

Before admission, source review found and corrected two resource safeguards:
launch now rechecks the recorded storage snapshot's identity/freshness/global
cap, and nested pools propagate one shared cancellation event. Failed parent
guards cancel queued work and active native operations stop at cooperative
checks. The actual spawn cancellation tests passed for both workers and the
parent pool wrapper. GPU checks verify the registered 3090 and probe external
load while the parent's GPU work is quiescent, preserving light video/desktop
sharing. CPU reduction cancellation remains cooperative at operation boundaries.

## Measured resources

| Quantity | Measured value |
| --- | ---: |
| Full bounded cycle | 91.531 s |
| Physical targets complete, from run start | 74.266 s |
| Context targets and readback complete | 83.750 s |
| Two fits, internal summed time | 3.063 s |
| Peak own CUDA tensor allocation | 28,576,768 bytes |
| Lowest sampled available system RAM | 86,686,003,200 bytes |
| Retained files | 809 |
| Retained logical bytes | 1,278,992,546 |

These are workload-specific software/resource measurements, without a matched
old-runner speed benchmark. GPU fitting was a small part of this case; maximizing
GPU utilization alone would not accelerate its dominant CPU target preparation.
River worker target phases summed to 137.140 seconds across overlapping jobs;
river native subprocess wall times summed to 32.144 seconds. Their difference
also includes Python inference/posterior work, parsing, validation, hashing and
I/O; it is not a separate measured CPU-only time.

## Storage findings and next admission

The refreshed pre-run inventory measured 778,101,470,861 named allocated-file
bytes against the 800GB allowance. After this profile, approximately 20.62GB
remains under that accounting rule, before small publication files.

The profile stores 76 hash-verified pairs of identical river stdout/JSON bytes.
Those duplicate copies total **588,895,857 bytes**, about 46% of the profile.
River exports across both names account for 92% of its retained bytes. No
historical file or completed profile was compressed, linked, removed or altered.

Read-only, in-memory zlib controls on predetermined first/middle/last river
exports and both board trees passed exact decompression/SHA checks. River
samples compressed to about 5.5% of raw bytes; board samples to 2.2-2.8%.
Those figures are indications, not measured NTFS/WOF ratios, whole-store
compression estimates, or storage-admission credits.

The next preparation should qualify lossless retention for new artifacts and
its allocated/logical accounting, then run one genuine cycle across all five
fitting depths. A static public-state geometry proxy projects about 18GB of raw
duplicated retention for that cycle, rather than a simple fivefold extrapolation.
This is a planning proxy, not a measured footprint or guaranteed upper bound.

Current guards poll store size; they are not filesystem quotas. The subprocess
stdout cap does not cover JSON written to separate CLI output-path arguments.
A larger admission must explicitly bound those outputs and reserve overshoot
space. Existing 64MB/60-second river-export limits also remain in force;
compression cannot relax their raw logical limits. Deeper exports have not
yet been profiled and may require separately qualified grouping.

After representative resource qualification, register a stability comparison
with sufficient board sampling, independent runs, supported-hand diagnostics
and fresh payoff evaluation. The current K2/F4 profile is insufficient for that
claim. Five-bet expansion, stack-appropriate opening ranges, other positions,
multiway accuracy and matched GTO Wizard comparisons remain outstanding.
The original failed improvement finding and all original scientific evidence
remain unchanged. The broad research goal remains active.
