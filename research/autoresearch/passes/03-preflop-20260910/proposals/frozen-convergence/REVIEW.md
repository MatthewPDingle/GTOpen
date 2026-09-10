# Independent source review and paired trajectory recommendation

Reviewed 2026-09-10, after compatibility planner b7e8583. Proposal only; no compilation, GPU jobs or active edits.

## Verdict

Stopping and save lifecycle are suitable for a controlled **bounded convergence trajectory** comparison. Apply `provenance-v2.patch` after the original harness patch (or copy `preflop_convergence_control_v2.rs` to the same example path). The additional delta closes calibration provenance and avoids dumping the entire modeled profile into the log. Neither change touches solver arithmetic.

The important limitation: native `.gtop` serializes the realization mode but not the fitted realization table or equity table. `load_game` calls `PreflopSolver::new`; that constructor calls `RealizationFit::load_default`, which honors `REALIZATION_FIT`, otherwise tries two CWD-relative paths. Merely checking `fit.is_some()` proves a fit loaded, not which one. V2 therefore requires an explicit frozen `REALIZATION_FIT`, validates it, logs its canonical path and fingerprint, and checks its bytes after final reload. Use an absolute path in the paired environment. Public state equality after reload does not compare private fitted coefficients; the frozen artifact check supplies that missing provenance.

The equity cache is length-validated before `load_or_build` and its sample header supplied back unchanged. Under the source's loader rules that takes the read path. No cache rebuild is intended. Preserve this artifact throughout both processes, and freeze its SHA256 externally. The coupled rank table is generated in memory from fixed source constants, 1024 particles and seed90210, rather than an external disk cache; pin multiway/evaluator source and executable as well. No model override or refit belongs in a paired run.

V2's start summary records config, native iteration/model, hero/frozen/learning masks, and a typed-profile JSON fingerprint/length. The original start_state included the full profiles, which for this fixture can create a many-megabyte log entry. Full typed state is still retained internally for the roundtrip equality check. This avoids noisy logs without removing the persistence check.

## Validation boundaries

- Native server checkpoint ordering and strict learning-gap sum were verified in source, including adaptive/partial profiles and hero/frozen seats. Do not substitute total unrestricted modeled-player bleed for that sum.
- GPU failure intentionally aborts; a benchmark that silently falls back CPU is invalid for this comparison.
- No startup gap check, no warmup that mutates only one candidate, no resetting iteration on a resumed fixture. Both load the same exact native input.
- The stop condition accepts only a finite positive target and applies strict `<`. Equality continues. Every final-limit iteration is checked even off cadence.
- A zero-learning-seat run can meet the target at the first check without demonstrating unrestricted equilibrium; that flag is logged. It is not the primary modeled fixture here: adaptive responses keep its modeled seats learning.
- Safe publication uses a new staging directory and hard-link creation, so an existing OUTPUT cannot be silently replaced. Staged data remains available on errors. A filesystem without hard links fails explicitly.
- Arena fingerprints are practical regression checks, not mathematical proof or cryptographic collision resistance. Use the existing full saved-game comparator after both trajectories for arena/effective-policy equality. Private point-lock and hero-backup fields are serialized by native save/load but not independently compared by this example's public-state JSON.
- Per-checkpoint times include gaps and CPU sync separately. End-of-run disk/hash work is excluded from trajectory time. Compare like categories and report end-to-end separately if desired.

## Fixed paired plan

Freeze these values **before running either trajectory**, as requested by the parent. They are evaluation settings, not claims that either fixture is known to converge within the chosen bound.

| Fixture | Starting state | Budget (decimal MB) | Additional limit | Target learning-gap sum | Check interval |
|---|---|---:|---:|---:|---:|
| Modeled six-seat | `target/fixtures/fresh-coupled-validated.gtop`, native iteration0 | 19000 | 250 | 0.004 bb | 10 |
| Unmodeled eight-seat | Same frozen coupled native input as previous baseline-eight runs, native iteration74 | 23000 | 100 | 0.005 bb | 10 |

Verify the second native input is indeed the same iteration74 file and freeze its SHA256; do not silently use the iteration80 benchmark output or a later resumed save. If the intended input differs, identify and freeze that as a distinct experiment before either run.

Run original and compatibility-optimized implementations sequentially from each identical input. Use distinct never-existing OUTPUT files. Record final constructor batch and HU-cache mode for each. At19000MB the measured original modeled fixture uses **batch23**, so the compatibility candidate should report23; at23000MB the measured eight-seat fixture uses32. Remove the optional diagnostic batch-cap environment variable. The comparison must exercise the production compatibility planner, not force30 from a separate experiment.

The old modeled source is legacy_product at iteration100. Its previous apparent convergence is not evidence that a fresh coupled run will converge in100 iterations: the payoff model and starting arenas differ. Likewise, the observed coupled six-seat gap after6 iterations is about0.47135bb, which gives no trustworthy convergence-rate estimate. The eight-seat baseline gap after80 iterations is about0.60140bb. Both fixed limits may miss their targets. If so, report not-converged at250 or native174 and compare the same checkpoint trajectory. Do not call iteration-count exhaustion convergence or change the target to make the candidate pass.

A separate seven-seat coupled fixture reached0.0048167bb at iteration578 (`research/multiway-equity-audit/resolved-result.json`). This supports using a small bb target as a meaningful application-scale criterion, but does **not** justify extrapolating a completion iteration for these different six/eight-seat trees. The proposed0.004/0.005 thresholds are fixed in advance from the requested accuracy scale, not fit to candidate results.

## Time allocation from existing logs only

Using median iteration time times the limit, plus one measured check+sync per10iterations:

- Modeled original19000: 6.589s/iteration, 7.556s/check+sync → approximately30.6minutes for250.
- Optimized matched30 control: 3.635s/iteration, 5.385s/check+sync → approximately17.4minutes for250. **This is a planning proxy, not a measured forecast for the new compatibility batch23 path.** Allow25minutes rather than promising17.4.
- Eight-seat original: 9.802s/iteration, 12.183s/check+sync → approximately18.4minutes for100.
- Eight-seat optimized: 5.482s/iteration, 7.498s/check+sync → approximately10.4minutes for100.

Sources are `raw/budget-original-19000-a.log`, `raw/modeled-opt-batch30-a.log`, `raw/baseline-eight-a.log`, and `raw/opponents-eight-b.log`. Include constructor, final persistence, comparator and rebuild time separately. Reserve roughly100minutes for the two pairs plus a reasonable operational buffer, comfortably within14:51–21:34UTC. Existing evidence does not require using the near-full23000MB modeled case: the19000 control reduces memory-pressure ambiguity.

At matched batch boundaries, earlier full-state comparisons were exact. Predeclare checkpoint gaps/EVs and final full arenas/effective policies as exact regression checks for these compatibility pairs. If any mismatch occurs, investigate it and retain outputs; do not switch to a looser tolerance to keep the experiment going. Time-to-target comparison is only available if targets are actually reached; otherwise report time for the fixed trajectory and final residual gap.

Do not start an automatic extension after a miss. A later paired continuation can be a separately declared experiment from the two saved endpoints with another fixed additional limit, preserving the first result. The present pair already tests hundreds of captured/replayed iterations, adaptive modeled paths and repeated checks; that is meaningful even without target attainment.
