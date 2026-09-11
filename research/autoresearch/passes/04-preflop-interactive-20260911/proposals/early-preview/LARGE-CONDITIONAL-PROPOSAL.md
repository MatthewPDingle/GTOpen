# Bounded conditional refinement on the actual large game

Source implementation prepared during the running large64 benchmark; no hardware or tree inspection was executed by this agent.

The current method's actual algorithm already starts at an arbitrary selectednode; its small-only limits and whole-arena audit copies are the blockers. Selected late-position branches in the1.568million-node eight-seat game are likely tiny. The attached path candidates come from the exact savedconfig plus the existing legal-action ordering, not from observed outcomes. A later readonly inspector should confirm actor/live seats/pot/action labels, positive source reaches and subtreecounts before running any refinement.

## Simplest safe research implementation

Add a separately named large entry point/example with hard limits2,000,000source nodes and3GiB total regret+strategy arrays; retain the existing500action/1000terminal descendant caps. Keep source fullreference only in the first experiment. The small method continues to enforce its old limits.

Use **one complete original arena backup** for this research pass. Remove the existing second`after` snapshot and third`restored` snapshot, and avoid an arena-lengthbooleanmask. Sort the <=500writable block intervals, validate their bounds/non-overlap, and compare each outside interval directly against the original backup using f32`to_bits`. After the run/error, restore original arrays and compare directly again. This needs at most3GiB incremental backup memory, not three additional full copies, and preserves a true bitwise outside-state audit without introducing a new digestdependency. Nodes/config/profiles remain untouched. A root memory guard should confirm sufficient headroom before execution; estimated peak is existing tree/arenas plus onebackup and small policy/checkpointpayloads, not a measured RSS claim.

Record load/build time, backup allocation/copy time, baseline local evaluation, each completed local checkpoint, outsideaudit, restoration and total walltime separately. The user-visible latency must include preparation; reporting only a tiny descendantiteration would overstate practical performance. Cap conditional work120seconds, and keep a bounded external guard with a separately stated cleanup allowance. No native writes, appAPI, sourcefile mutation or parent policy merge.

A later optimized variant can back up only writable blocks (worst-case500*16*169*8≈10.8MB) and hash unchanged intervals before/after. That would reduce copy cost, but the project currently has no SHAdependency. For this bounded research iteration the onebackup approach is simpler, auditable, and comfortably below the64GB machine's total capacity; actual concurrent free memory must still be checked. The hash-based variant should describe its invariant as a fingerprint match rather than literal byte-by-byte equality unless it also retains the bytes.

## Source-derived path candidates

For postsSB=BB=1, stack150, opens6/10, reraises3/5/7, maxraises2:

- `[0,0,0,0,0,2,0]`: UTG throughCO fold, BTN raises to6, SB folds; BB acts atpot8 withBTN/BB live. Expected small HU continuation, roughly five actionnodes and ten terminals from menu counting.
- `[0,0,0,0,0,3,0]`: same withBTNraise10; BB acts atpot12.
- `[0,0,0,0,2,1,0]`: UTG throughHJ fold, CO raises to6, BTN calls, SB folds; BB acts atpot14 withCO/BTN/BB live. Expected roughly thirteen actionnodes and eighteen terminals, exercising full1024particle three-player payoffs as well as HU continuations.

These counts are provisional source reasoning, not verified inspector results. Nativepaths must not be transplanted to a different config/menu. Zero/unlearned source support must reject; do not silently select another path after seeing a failed outcome. Any accepted replacement needs a new frozendevelopmentmanifest.

## Pairwise-cache provenance is mandatory

Nativepreflop headers store the multiway model but **not** the pairwise equitycache hash/samplecount. An oldAPIreference source was solved with a regenerated1024sample cache; loading it with the current20000samplecache changes HU terminal payoffs even though`coupled_deck_v1` remains unchanged. For a trajectory-preserving conditional experiment, stage the matching private1024cache with that source, freeze/cachecheck its actual hash and header, and pin the resolved realizationfit. Alternatively use the newly qualified20000reference source with its matching20000cache. Do not mix them.

## Preview64 source: proposed only, not part of the first implementation

A fastsource could provide useful prefix ranges quickly, followed by fullreference local refinement, but it must be an explicitly different research case. Freeze prefix ranges **before** any payoffchange and label them approximate64-source ranges. On an owned snapshot, retain the original`Arc<CoupledDeck>` and iteration, temporarily install the full table only for the conditional subtree, start local learnable blocks fresh, then restore the originalArc/model/counter/arenas exactly on all exits. The existing public setter correctly refuses changing nonzero-iteration savedgames; do not weaken it or use it to relabel the parent. A research-only scopedpayoffguard could support this later after review.

Such a result means “fullreference continuation conditional on ranges inferred by the fastsource,” not a fullreference whole-game strategy. Baseline local values should be evaluated under both originalfast and fullreference payoffs so the modelchange is not confused with learning improvement. Require unchanged prefix support/lock semantics, matchedHUcache, exact parent restoration and no native save. This extension should follow explicit parent approval; it is not implemented here.


## Implemented source interface and execution gate

`preflop_conditional_large_research` is a separate research example:

```
preflop_conditional_large_research INPUT.gtop REGISTERED_PATHS.json OUTPUT.json inspect [120] [100]
preflop_conditional_large_research INPUT.gtop REGISTERED_PATHS.json OUTPUT.json refine [120] [100]
```

Run each in a private directory containing the matching frozen `cache/preflop_eq169.bin` and realization-fit cache. Pin the input, executable, path manifest, cache and fit hashes in the external protocol. The example reads and preserves the actual pairwise cache sample header; it never regenerates a different sample configuration deliberately. Output must not exist. Native input is read-only. The native file itself is capped at 3 GiB plus a 32 MiB metadata allowance; loaded arrays are separately capped at 3 GiB and source topology at 2 million nodes.

First run `inspect` using `conditional-large-proposed-paths.json`. It returns labels, actor, live seats, pot, support status and descendant counts, without publishing strategy frequencies, EVs or gap outcomes. Freeze the input/hash/manifest and retain all three registered rows before running `refine`. Refinement requires the expected actor, live positions and pot to match exactly, and rejects missing positive learned prefix support. A rejected row is retained, never replaced by an outcome-selected alternative. Max local iterations is one of 2, 10, 30, 100; available completed checkpoints are reported and a timed-out partial iteration is never published.

The 120-second shared work allowance includes between-case elapsed overhead. Each case's cancellation clock starts after mandatory backup; its exact audit/restoration also runs outside that clock. Therefore the external process guard must include a separately stated cleanup allowance, for example 180 seconds after loading, and must record total wall time. Do not advertise the iteration-only timing as first usable latency. New result fields identify source size, backup bytes/time, preparation time, outside audit, restore, restore audit and total method time.

The parent's selected original full-reference source uses 1,024 coupled particles and a **20,000-sample pairwise equity cache**, not the distinct API trial that accidentally rebuilt a 1,024-sample pairwise cache. The newly qualified full-reference 50-iteration source also uses the 20,000-sample cache. This source distinction must remain explicit in the execution manifest.

Source-only checks added: direct outside-slice audit ignores only sorted non-overlapping writable intervals, rejects invalid bounds, distinguishes signed zero and preserves exact NaN bits; structural inspection leaves source arrays/metadata unchanged; the large wrapper restores the exact source after refinement. Root owns compilation and execution of these tests.


## Separately authorized preview-prefix / full-local experiment

The previous preview-source proposal is now implemented as a distinct mode, authorized after build e completed. The ordinary `refine` path still requires a full-reference source.

```
preflop_conditional_large_research PREVIEW_INPUT.gtop REGISTERED_PATHS.json OUTPUT.json refine-preview-full 120 100
```

Freeze the exact input and executable hashes before running. Intended separately registered sources are the preview64 1,000-iteration large input and preview64 50-iteration input, with the same existing development paths and 20,000-sample pairwise cache. The 50-iteration case tests a cheaper initial setup; neither case is holdout validation. Root owns execution and staging; this documentation records no execution outcome.

The wrapper freezes every seat's raw arriving ranges under the original preview source, including folded-seat chance factors. It evaluates the unchanged source strategy's local gap under preview payoffs with cancellation, then temporarily installs the full coupled table. The full-local method checks that the original walk is still bitwise identical and explicitly consumes those frozen rows. It starts local learning blocks fresh while preserving frozen/model-forced/point-locked policies. The source Arc is restored even on error/panic; all source arenas and metadata are restored by the bounded method. No public native-model setter is relaxed, and no native save or app/API integration is added.

Outputs distinguish `baseline_source_model_conditional`, `baseline_full_model_conditional`, and each learned full-payoff local checkpoint. The first difference measures the payoff-model change; compare full-before with full-after to measure local learning. `prefix_unvalidated=true` is mandatory: the method cannot recover hands excluded by an inaccurate earlier preview policy, and it does not correct earlier-seat actions. There is no whole-game convergence claim. Research publication is labeled `has_completed_learned_snapshot`, with `quality_qualified=false`; two completed local iterations alone are not usable-quality evidence.

`source_baseline_seconds` and `total_hybrid_method_seconds` include the extra source-model baseline. Its evaluation consumes the same work allowance; remaining local iterations may be reduced or no checkpoint may finish. Full table payload is roughly 1.98 MiB and is normally already resident because preview construction itself reads the full table. Arena copying/auditing and full local multiway evaluation remain the material costs.

Two focused tests additionally cover original Arc identity after error/panic, frozen source prefix and policy preservation, exact arena/metadata restoration, correct model annotations and invalid-path rejection. These are source additions only until root compiles and executes them.


## Keep-better-baseline research output safeguard

The local refinement output now separately reports a safeguarded policy while retaining every original baseline, completed checkpoint and last candidate policy unchanged. `retained_policies` is the safeguarded output; the existing `policies` array remains the unfiltered last completed candidate for research evidence.

The rule uses only the **same full-payoff conditional game's summed learning gap**. A completed finite candidate replaces the source baseline only when its gap is strictly smaller; ties, missing checkpoints and invalid metrics retain the exact original source policy. `retained_policy_source`, `retained_local_iteration`, `retained_conditional` and `retention` explain the choice. This protects a baseline such as0.0002749bb against a later0.0009287bb candidate even though both are below0.005bb.

Fixed-source continuation action loss and bad-action tail remain separate reported diagnostics/failures and explicitly do not select the retained policy. They evaluate continuation against the old opponents' policy and could veto a better conditional equilibrium simply because all local players changed strategies. Original full-reference, physical and local-tail promotion gates remain unchanged and must still be checked; `quality_qualified=false` and `retention_scope="conditional self-game only"` prevent a retention decision being presented as quality acceptance. Preview-prefix/full-local retention compares against the full-payoff baseline, never against the preview payoff's baseline gap. Its prefix remains unvalidated.

No parent session is modified: source arenas and model are restored exactly, and retained policies are ephemeral research output. The rule currently compares the last completed candidate with baseline, not an outcome-selected best checkpoint. A focused test records the concrete regression, strict improvement, ties, unavailable metrics, and the intentional separation of tail diagnostics from selection.
