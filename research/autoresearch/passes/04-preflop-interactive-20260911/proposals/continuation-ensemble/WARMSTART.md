# Fresh full-model policy initialization — unrun research family

The32/64-particle development solves passed the global gates at500 iterations but still failed selected local-tail checks. This follow-up does not loosen those gates. It asks whether a cheap approximate average can initialize a new full-model solve more efficiently than a uniform start.

`research_full_policy_warmstart(scale)` accepts a completed versioned preview and creates a **new** full1,024-particle solver. Approximate regret values are never read/copied. Full-model iteration starts at0; learning averages start at0. At each unconstrained learning node, initial regrets are the source's effective average probabilities multiplied by one of three predeclared positive scales:0.01,0.1 or1. No action probability floor or hand-specific correction is added. Frozen raw strategy sums are copied exactly, their regrets remain0, and current non-HERO profile/lock/fit/cache constraints are retained. This is a regret-policy prior, not an inherited average or a resumed approximate solve.

The initial unconstrained average is untrained until full-model iterations accumulate it. HERO sessions are rejected, including either pre-HERO frozen metadata or a HERO undo backup without an active HERO seat. This prevents returning a saveable full-model solver with incomplete undo state or carrying old-model backup regrets. Non-HERO frozen seats, profiles and point locks remain supported. This is not a general application warmstart command.

Source:

- `crates/solver/src/preflop/preview_warmstart.rs` — root must declare this module.
- `crates/solver/examples/preflop_preview_warmstart.rs` — CPU-only bounded harness.

```text
preflop_preview_warmstart SOURCE.gtop FULL_REFERENCE.gtop CACHE NEW_OUTPUT_DIRECTORY THREADS [PATHS.json]
```

The harness always runs all three scales and evaluates after50,100 and500 full-model iterations. Inputs must fit the existing20k-node/128MiB-arena quality boundary; output must be a new directory under the lab's `target/research-preview`. It validates source/reference compatibility before running. Every checkpoint records unchanged global gates and optional supplied local paths, with separate full-iteration and quality/save timings. Include source-preview creation time when comparing total time to useful quality; this harness only measures the new full stage.

Each output is a new correctly identified full-model native save with roundtrip verification and an accompanying provenance JSON. The sidecar identifies source model/iteration/path, scale, resets and constraints. Native inputs are never rewritten or relabelled. Pin source SHA256 externally; the benchmark does not claim it independently hashes native inputs. Preserve provenance sidecars with exported research saves.

Tests: `warmstart_resets_learning_state_and_retains_fixed_policies` checks each predeclared scale, negative source regrets not carried over, zero learning averages, exact frozen sums, point locks, source immutability, invalid scale rejection and cancellation. `warmstart_rejects_hero_and_undo_state_without_mutating_source` checks each HERO-state marker independently and verifies unchanged arenas, iteration, model, frozen flags and undo state. No result or acceleration claim is made before root runs the registered experiments and full/local quality evaluations.

## Separate large GPU protocol

`research_large_full_policy_warmstart` shares the same private initialization routine, with explicit fixed limits of2million nodes and3GiB combined regret/strategy arenas. The original small method still enforces20k nodes/128MiB. Both reject HERO and perform identical resets; the unit test compares their resulting learning state on the same small fixture for all three scales.

New GPU-only example, to be registered by root:

```text
preflop_preview_warmstart_gpu SOURCE.gtop CACHE NEW_OUTPUT_DIRECTORY GPU_BUDGET_MB SCALE
```

One scale per process permits independent external limits. The predeclared family remains0.01/0.1/1, with checkpoints at2, 10, 30, 50 and100 full-model iterations and a hard iteration limit of100. This schedule is frozen before any large warmstart outcomes and measures time to the fixed full-model gap target; it does not change the learning mathematics. Root must apply an external wall-clock guard of at most1,800 seconds; the harness also refuses to start another iteration after that elapsed time. Unrun scales remain unrun, not implicitly passed.

Each checkpoint reports full-model gaps/EVs, iteration timing, setup/check/save timing, and a new native save with provenance sidecar. `research_warmstart_roundtrip_matches` compares metadata and all regret/strategy bits directly without allocating large snapshots. The approximate source is dropped after initialization; the only live GPU engine belongs to the fresh full model. Native reload verification temporarily holds one additional host solver. Source size/mtime and cache bytes are checked, while source SHA256 must be pinned externally. No source native is overwritten or relabelled.

These large checkpoints still require independent full-reference/global and selected-local quality audits. Source-preview generation time must be included in any end-to-end warmstart speed comparison.


### Registered large-source cases and latency accounting

Before observing any large warmstart outcome, register both source cases separately:

- Preview source at **50 iterations**: exploratory development case for fast initial setup.
- Preview source at **1,000 iterations**: mature development source whose global behavior has already been tested; this does not establish local-tail correctness.

The large GPU harness requires source iteration50 or1000. The external execution protocol must pin exact source model/path/SHA256, executable/source hashes, pairwise cache sample count/hash and realization fit for each case. Do not choose between sources or scales using test outcomes and then present the selected combination as preregistered. Both use the same predeclared scales0.01,0.1,1, full checkpoints2/10/30/50/100 and maximum100 full iterations. Missing/time-limited cases remain explicitly unrun or incomplete. No deployment or quality promotion follows merely from passing the global gap.

The harness separately reports equity load, source load, fresh initialization transfer, GPU initialization, cumulative full iteration work, checkpoint gap evaluation, device synchronization, native save, roundtrip load and bitwise roundtrip verification. A `gap` event publishes `gap_published_elapsed_seconds` immediately after evaluating each full-model checkpoint, before native save/roundtrip work. That is the primary observed time-to-gap for the new full stage. Later checkpoints' wall time includes earlier checkpoint storage overhead; report that honestly rather than subtracting selectively. Add the source's original preview construction/solve latency to compare total initial-setup workflows.

Five native checkpoints are retained per source/scale, instead of two. Reserve disk space before launch: approximately five times the fresh native size per case, plus staging and sources; for a2.5GB native this is approximately12.5GB per run. Do not silently skip checkpoint saves or weaken roundtrip verification to fit storage. Existing older CPU research protocols/results keep their original50/100/500 schedule and are not rewritten by this amendment.
