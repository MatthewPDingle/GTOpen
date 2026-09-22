# Wide blind defense needs a different storage path

The exact BB export passed its accounting checks, but directly applying the
previous 112-board implementation would exceed both VRAM and available storage.
This is a resource-planning result, not a failed solve or a strategic result.
No CUDA allocation or new preflop solve was attempted.

The previous study retained 56 versus 19 hand classes at entry. The new case
retains all 169 BB classes versus 96 BTN classes and has three postflop branches
instead of two. The single-raised pot also has a much larger stack-to-pot ratio.
These are important differences in the intended game, not options to remove
merely to obtain a passing resource check.

## Exact panel accounting

The CPU planner used the previous study's unchanged 112-board training manifest
for a resource comparison. This is not registration of a new strategic test or
permission to reuse the old 190-board evaluation outcomes for fitting.

| Payload | Three texture probes | Existing 112-board panel |
|---|---:|---:|
| Postflop games | 9 | 336 |
| Canonical parked strategy state | 24.87 GB | 1,105.40 GB |
| Retained host structures | 0.87 GB | 32.49 GB |
| Retained device structures | 0.93 GB | 34.84 GB |
| Shared GPU workspace | 15.91 GB | 16.24 GB |
| Steady device payload | 16.83 GB | 51.08 GB |
| Conservative construction peak | 30.61 GB | 66.09 GB |

GB here means decimal billions of bytes. The machine has 25.77 GB of physical
VRAM (24 GiB). At the review, 23.17 GB VRAM, 102.73 GB RAM and 273.71 GB on S:
were free. The admission review preserves 3 GiB VRAM, 20 GiB RAM and 32 GiB SSD
reserves. It does not add S: and T: free space together.

The existing design retains device structures for every game even when strategy
state is parked in RAM or on SSD. Its **34.84 GB of retained device structures
alone exceed the GPU**, before adding the workspace. Consequently, freeing more
SSD space cannot by itself make this forest fit.

Even assigning all usable RAM to the payload leaves an optimistic single-state
spill lower bound of 1,056.63 GB. Available SSD after its reserve is about
239.35 GB. This bound excludes checkpoints, temporary copies and process
overhead, so the state-storage problem is separate from the VRAM problem.
No prior checkpoints or research evidence were deleted.

The construction figure is a conservative admission bound from simultaneous
old/new workspace allocation, not a measured allocation failure. By contrast,
the steady payload already gives sufficient reason to reject a full resident
112-board device forest. `capacity-review.json` records exact byte counts,
resource snapshot, input hashes and all three failed admission conditions.

## Next engineering experiment

Preserve the full BB support and all three branches. Investigate bounded
residency of per-game device structures, separate from the shared compute
workspace. The workspace itself fits with reserves; retaining every game's
device structures does not. A new construction path must also avoid holding
two large workspaces at once.

In parallel with that design work, measure whether lossless parked-state
compression provides enough real savings on learned CFR states. The useful
quantity is compression of trained arrays together with encode/decode time,
not compression of freshly initialized zero arrays. Any compression research
must verify exact byte restoration, preserve checkpoint recovery, and benchmark
the additional transfer cost. Current storage is not sufficient without a
substantial reduction, and compression must not be assumed to achieve it.

Start qualification with individual full-support continuations and exact
round-trip/control checks, then reassess admission for the intended panel.
Smaller controls are engineering tests only; they do not replace the full
blind-defense comparison. If exact storage remains impractical, an explicitly
different approximation would require its own accuracy study rather than a
silent reduction of ranges, branches or test scope.

Production 56708 and the completed 570-evaluation study remain unchanged.
