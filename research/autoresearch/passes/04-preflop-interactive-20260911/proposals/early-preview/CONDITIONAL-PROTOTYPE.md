# Research-only conditional CPU prototype

Source delivered; parent builds/tests/runs serially after the API queue. No implementation has been deployed and no hardware validation has been performed by this agent.

- Worktree module: `crates/solver/src/preflop/conditional_research.rs`.
- Example: `crates/solver/examples/preflop_conditional_research.rs`.
- Frozen development paths: `conditional-development-paths.json` contains`[1]`, `[2]`, `[2,1]`, previously observed problem branches in the small full-reference500 snapshot. They are development cases, not held-out validation.
- Optional separate four-player fixed/frozen control: `conditional-frozen-control-paths.json` contains the root path.

Build/test commands (root executes only):

```text
cargo test -p solver --lib conditional_research::tests -- --test-threads=1
cargo build -p solver --release --example preflop_conditional_research
```

The example takes`INPUT.gtop PATHS.json OUTPUT.json [SECONDS<=120]`. Use a new output file and the existing small native reference500 fixture. Parent should freeze the inputnative/cache/fit/binary/source hashes in the ordinary guarded-run protocol; the JSON records full source config/profile/lock metadata, exact source/normalized ranges, sample count, resolved fit coefficient representation, path IDs and local policies. It does not write a native file. Cache samples are read from the actualcacheheader, and any cache change during load is rejected.

The module refuses a full tree above20,000nodes or128MiB arenas, a selected subtree above500action/1000terminalnodes, zero arriving rows, unsolved/unreachable prefix decisions, and non-full-reference models. It runs the existing CPUtraversal at the selectednode with every originalseat's row normalized. Learning descendants start fresh with a separate local discountclock and pruning disabled. Forced/frozen blocks remain untouched. Root/action comparison values are measured against the original fixed continuation. All sourcearena/counter/pruning/stop-flag state is restored on return or panic; source metadata and arena bits are rechecked. Interior inference caches may become populated, but native state/policies remain unchanged.

Only completed checkpoints2/10/30/100 publish ephemeral policyvectors. Timeout may leave a partial local iteration internally; that state is discarded, the last completed checkpoint remains the only reported policy, and the source is restored. The overall example shares its120second cap across selected paths; if an earlier path consumes the budget, later rows explicitly report exhaustion. A cooperative timer cancels traversals at existing fan-out boundaries. Root's external process guard should remain enabled because an individual terminal/kernel-free CPU evaluation, initial loading, serialization or restoration can extend slightly beyond the requested cooperative deadline.

Reports contain baseline and checkpoint conditional learning gaps/EVs, fixed-source one-action loss and worst relevant inferior-action probability, full relative-path policies, and exact outside/forced/frozen/source preservation flags. This is neither global convergence nor model accuracy evidence. Improvement must be assessed on the preregistered development paths; no automatic promotion or parent policy merge occurs.

Independent-review corrections: the cancellation bridge now polls the caller's original external stopatomic and the local deadline every10ms, while the completionchannel wakes it immediately. It only sets the local cancellationflag and restores the originalArc without changing its value, so external cancellation raised during the run remains raised afterward. Unevaluated nonlearning-seat EVs are`null` with an explicit`ev_evaluated_seats`mask. Three additional focused tests cover external propagation/restoredArcidentity, deadline/completionwake and absent-flag restoration, and nullunevaluatedEVs. These source changes await the parent's next build/test run.
