# Supplemental fixed-iteration trajectory control

Declared after the initial20-iteration global/local results, before running this supplement. It does not replace or alter the registered primary convergence experiment or any quality threshold.

The small-tree driver additionally accepts `--fixed-iterations=N`, N=1..500, for either full or preview model. It runs a **fresh game** in a new output directory, always performing exactly N iterations unless an error/cancellation occurs. Own-model gaps are measured and reported but do not stop the run. Final status is `fixed_iteration_complete`, never a convergence certification. This option cannot be combined with the separate candidate-cap positional argument.

Planned supplement: compare100 and500 iteration checkpoints against the same full-reference500 state. Its purpose is to determine whether the SB conditional action tails are learning lag, weak reference continuation, or persistent approximation differences. Keep global and local gates unchanged, retain rare-branch results, and report this as supplemental because it was motivated by the initial failures.

The driver preserves actual native model identity, fixed/frozen/profile initialization and existing save protections. It never resumes candidate regret arenas under the reference model.
