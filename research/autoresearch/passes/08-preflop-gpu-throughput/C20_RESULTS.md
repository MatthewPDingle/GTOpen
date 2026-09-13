# C20: exact-zero bypass rejected at compiler-cost screen

Standalone GPU qualification passed all 1,008 cases, including signed zeros,
positive subnormals, sparse tiny values, aliases, compact/noncompact layouts,
zero mass, gates, sample offsets and partial batches. Every output bit and
untouched guard matches the retained writer. The guarded run took 132.594
seconds including compilation; device test time was 2.61 seconds.

| Property | Retained writer | Sparse writer |
|---|---:|---:|
| Registers | 26 | 26 |
| Local spill bytes | 0 | 0 |
| Shared bytes | 0 | 0 |
| Static PTX instructions | 324 | 408 |

All 20 original compiled kernel entries remain identical. The new sparse
entry contains six actual warp votes and branches; each branch skips exactly
five shuffle/add steps (36 or 37 static instructions including setup/moves).
However, its total static code expands by 25.93%, exceeding the registered
20% gate. C20 is rejected before full solver integration or timing.

This is not a measured slowdown. Static PTX is a screening proxy, not native
instruction timing; D17's 33.64% empty learning tiles remain valid. The compiled
nonempty branches repeat lane tests and shuffle setup. A different, explicitly
qualified instruction sequence may reduce that overhead; do not relax C20's
gate or claim the present implementation is faster.

Evidence: `raw/c20-screen-verified.json`, `raw/c20-prefix-v1/`, guarded exit/log,
source archives and `check_c20_screen.py`. Frozen diagnostic executable SHA256:
`155a201ef020187258d5a89835b07d99520c4f3e61c6c9d2a1ead1f27544c1f9`.

Only a manual test module remains. No runtime dispatch, production build or
port 56708 changed. Four prior improvements remain retained; this result adds
no speedup to the progress graph and does not resolve the convergence goal.
