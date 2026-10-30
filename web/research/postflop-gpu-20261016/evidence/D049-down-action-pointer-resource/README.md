# D049: selected actor-side reach-map pointer

Preparation only against accepted E020. D048 identified that common down-action PTX keeps selected reach-slot map loads and actor branches inside hand loops even where child IDs are hoisted. This one candidate selects the immutable map pointer once and substitutes the original source/child indices. It adds no restrict promise, explicit child-load hoist, guard, float operation, cache, table, launch or host change. Actor zero selects rsrc0; every other value selects rsrc1, exactly as before.

The prospective prerequisite has two parts. Registers and local bytes must not increase; theoretical128-thread occupancy must not decrease, with128 threads supported. Independently, each commonNA2/3/4 compiled path must show actual actor-selection branch removal and/or selected slot-load hoisting, with unchanged ABI, guards and floating dependencies. The other eight complete PTX entry bodies must be byte-identical. Static total opcode counts cannot establish the mechanism. The runner leaves this PTX gate pending even when resources pass; no rescue variant or native candidate is automatic.

The standalone Rust probe narrowly adapts completed D046. It compiles baseline and this one candidate with production architecture-only options, in one CUDA context, loads down_action and queries attributes/occupancy. It has no kernel-launch, arena, stream or solver path. Exactly four markers are expected: device, two resource rows, complete. Full PTX entries/diff and scoped static opcode inventories are retained for independent review.

Root executes only after frozen source/script review. The runner pins E025 terminal rejection/restoration and verifies all162 accepted source identities under the shared lock before compilation and after the probe. It refuses active live solves, requires50GiB free plus1GiB output reserve, uses600seconds per stage, preserves native stdout/stderr and failures, heartbeats every10seconds, and cleans up only its owned child tree on error/interruption. Telemetry is pre/post, never polled during the child.

Root command, from this directory after review:

`python -B run.py --execute --prepared-manifest-sha256 SHA256`

commands.json records complete future commands/dependencies. No Cargo or checkout changes are needed. Preparation has not executed rustc, NVRTC, CUDA or the solver. The initial text-written patch had CRLF context and failed read-only apply-check; the preserved draft and note document re-emitting identical candidate content as an LF byte diff before sealing. The final apply-check passed.

D045 event intervals are selected perturbed launches, not family or whole-solve shares. No speed/headroom claim follows. Uniform map loads may already be cheap; live-address pressure or scheduling could offset a compiler reduction. D048 found no equivalent in its scoped history search, not an exhaustive novelty proof. Any later native experiment requires separate root authorization and exact controls.
