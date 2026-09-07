# GPU pass 2 handoff

Retained source: `d3ff6d69969e13939e3ff7e1f43f6d9616ce24f3` in the isolated research worktree.
The registered solver source was published on master in commit `8ff89f4`.
The shared checkout retains those implementation bytes; subsequent commits update documentation and UI wording.
The patch is `patches/gpu-pass-retained.patch`; its SHA256 is attested by
`gpu-validation.json`. No live application restart or session replacement occurred.

Final controls: B034 (fresh original preflop and postflop targets), B035
(fresh original postflop fixed-step/lifecycle/checks). Final runs G001-G005.
CPU124/GPU42/server1 main suites passed; G004 also runs the ignored report
benchmark. Full saved state, query, resume, lock and target comparisons passed.
`verify_gpu_pass.py` is the current audit; `verify_final.py` is pass 1 only.

Four rejected families: E031 universal shared terminal uniforms, E034
postflop card-run loops, E036 explicit equity-dot unrolling, E038 parallel
compressed upload decoding. E033B all-seat direct specialization and universal
64-thread E037C were also superseded. Proposal files preserve old snapshots;
do not apply one over current code without rebasing its exact changes.

Compiler-input timestamps must be refreshed after restoring older files.
`lab.py` hashes inputs and refreshes changed ones before cargo. E026's initial
stale-artifact measurement remains invalidated. Never change frozen numerical
workloads or assertions to manufacture gains. Tight preflop cache budgets are
550/1350 MB now, because earlier 700/1600 budgets no longer force the fallback.

Useful next starting points, not measured improvements:
- Postflop: G005 synchronized diagnostic profile assigns rainbow up_show
  18.34 ms, up_action 17.01 ms and down_action 10.38 ms. Two-tone counterparts
  are 11.66/10.11/5.62 ms. These profiles include synchronization overhead;
  prioritize those kernels but score ordinary iterations and target time.
- Preflop: identify the next limiting kernel after launch tuning. The current
  256-thread narrow / 64-thread wide launch policy was measured on RTX3090;
  keep the reach-mass reduction explicitly at128 to preserve addition order.
- GPU memory: rainbow action packing saves little, while the two-tone case
  saves much more. Profile remaining immutable tables and live reach storage
  before proposing another layout; preserve inactive CPU materialization bits.

The next run should begin with a fresh control of this retained source, keep
hardware benchmarks serial, and continue the global metric sequence. The user
asked for about three hours with updates for this pass; a later pass is separate.
