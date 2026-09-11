# Frozen128 native policy and latency queue

Registered after the frozen128 terminal checks and before native128 trajectories. Preserve `frozen-herding128-a.json`, all indices, original gates and raw evidence. Native identity is `coupled_preview128_v1`. This queue requires the native identity/save/pot/tie/CPU-GPU tests to pass first; it does not offer128 as a production default.

Root owns all hardware and scheduling. Run sequentially through the existing guarded runner, which stops its owned child if the user's solve/report starts or the2026-09-11 03:03:27UTC deadline expires. Do not begin a job without enough remaining window for its bounded cap. Never overwrite an existing run ID/output. A canceled, unsupported or capped run remains explicitly incomplete; no threshold or action-menu adjustment follows it.

## Inputs and interpretation

- Lab: `T:/Dev/GTOpen/target/autoresearch/preflop-interactive-20260911`.
- Equity cache: lab `cache/preflop_eq169.bin`, header20000. Pin its full SHA and realization fit; guard now derives the sample environment from the root cache header. Check root/lab cache and fit equality before jobs. Do not mix API-a's regenerated1024 cache with these results.
- Small fixture definitions: the unchanged original `quality-gates/corpus.json`. Development3 is selection/development evidence. Four-seat fixed/frozen and three-seat adaptive fixtures were reserved for the earlier64 candidate but their outcomes are now seen; for128 label them **cross-model constraint/generalization regressions**, not a newly blind confirmation. Only the separately reserved128 physical corpus has that fresh confirmation status.
- Primary full references already exist: development `reference-development-a/checkpoint-020.gtop` (gap0.00145374), fixed/frozen `small-four-fixed-frozen-holdout-coupled_deck_v1-a/checkpoint-420.gtop` (0.00498081), adaptive `small-three-adaptive-holdout-coupled_deck_v1-a/checkpoint-040.gtop` (0.00381040), all under lab `target/research-preview/`.
- Fixed-iteration development reference: `fixed-development-coupled_deck_v1-a/checkpoint-500.gtop`. Keep this separate from primary early-stop results.
- Large config: `T:/Dev/GTOpen/research/autoresearch/passes/03-preflop-20260910/user-session.json` (1,567,754 nodes). It is a reused development/workflow fixture, not held-out policy evidence.
- Large quality reference: `T:/Dev/GTOpen/target/autoresearch/preflop-20260910/target/research-convergence/extended-convergence-eight-compatible-a.gtop`, full1024 iteration1024, SHA `4bc33937a5a8602fb204c8f2b211294f72f34f0859c989e3071cf014abbb5bab`. This resumed reference is valid for the policy comparison after native/config/fit checks, but its past runtime is not a fresh matched-speed baseline.

## Exact queue commands

PowerShell setup (does not start a job). Root should build/freeze the example executables before the queue, and record the frozen128 manifest/cache/fit/native hashes externally. The runner records executable/source/environment provenance and creates logs exclusively.

```powershell
$pass128 = 'T:/Dev/GTOpen/research/autoresearch/passes/04-preflop-interactive-20260911'
$lab128 = 'T:/Dev/GTOpen/target/autoresearch/preflop-interactive-20260911'
$bin128 = "$lab128/target/release/examples"
$gates128 = "$pass128/proposals/quality-gates"
$smallCorpus128 = "$gates128/corpus.json"
$cache128 = "$lab128/cache/preflop_eq169.bin"
$guard128 = "$pass128/guarded_run.py"
$largeConfig128 = 'T:/Dev/GTOpen/research/autoresearch/passes/03-preflop-20260910/user-session.json'
$largeReference128 = 'T:/Dev/GTOpen/target/autoresearch/preflop-20260910/target/research-convergence/extended-convergence-eight-compatible-a.gtop'
```

1. Primary small trajectories. These retain the registered own-model0.005/check10/reference500/candidate100 protocol. Candidate saves2,10,30,50,100 plus its final early-stop checkpoint. No early-stop outcome is silently replaced by fixed iterations.

```powershell
python $guard128 --timeout 180 small128-development-primary-a "$bin128/preflop_preview_small.exe" $smallCorpus128 three-solver-development coupled_preview128_v1 $cache128 target/research-preview/small128-development-primary-a 4
python $guard128 --timeout 300 small128-fixed-frozen-primary-a "$bin128/preflop_preview_small.exe" $smallCorpus128 four-fixed-frozen-holdout coupled_preview128_v1 $cache128 target/research-preview/small128-fixed-frozen-primary-a 4
python $guard128 --timeout 300 small128-adaptive-primary-a "$bin128/preflop_preview_small.exe" $smallCorpus128 three-adaptive-holdout coupled_preview128_v1 $cache128 target/research-preview/small128-adaptive-primary-a 4
```

Evaluate every actually saved primary checkpoint; skip none because its strategy looks poor. The following loop resolves existing saved files, never inventing an expected early-stop iteration. Development paths are the existing `[[],[1],[2],[2,1]]`. The fixed/adaptive root/limp/raise paths use the preregistered companion file `[[],[1],[2]]`; forced/frozen-node flags are preserved and are not counted as passes.

```powershell
$smallRuns128 = @(
  @{Run='small128-development-primary-a'; Ref='reference-development-a/checkpoint-020.gtop'; Paths="$lab128/target/research-preview/development-paths.json"},
  @{Run='small128-fixed-frozen-primary-a'; Ref='small-four-fixed-frozen-holdout-coupled_deck_v1-a/checkpoint-420.gtop'; Paths="$gates128/herding128-native-constraint-paths.json"},
  @{Run='small128-adaptive-primary-a'; Ref='small-three-adaptive-holdout-coupled_deck_v1-a/checkpoint-040.gtop'; Paths="$gates128/herding128-native-constraint-paths.json"}
)
foreach ($item128 in $smallRuns128) {
  foreach ($save128 in Get-ChildItem -LiteralPath "$lab128/target/research-preview/$($item128.Run)" -Filter 'checkpoint-*.gtop' | Sort-Object Name) {
    python $guard128 --timeout 120 "quality-$($item128.Run)-$($save128.BaseName)" "$bin128/preflop_preview_quality.exe" $save128.FullName "$lab128/target/research-preview/$($item128.Ref)" $cache128 4 $item128.Paths
  }
}
```

2. Supplemental fixed500 development control, for direct comparison with the previously run64/32 fixed trajectories. Evaluate its100 and500 checkpoints against the same full500 reference. This is explicitly supplemental, irrespective of primary results; record both.

```powershell
python $guard128 --timeout 180 small128-development-fixed500-a "$bin128/preflop_preview_small.exe" $smallCorpus128 three-solver-development coupled_preview128_v1 $cache128 target/research-preview/small128-development-fixed500-a 4 --fixed-iterations=500
foreach ($it128 in @('100','500')) {
  python $guard128 --timeout 120 "quality-small128-fixed-$it128-a" "$bin128/preflop_preview_quality.exe" "$lab128/target/research-preview/small128-development-fixed500-a/checkpoint-$it128.gtop" "$lab128/target/research-preview/fixed-development-coupled_deck_v1-a/checkpoint-500.gtop" $cache128 4 "$lab128/target/research-preview/development-paths.json"
}
```

3. Large latency probe, fixed50, preview every10 with initial iteration2 publication. This measures initialization, per-iteration cost, publication, final own-model check and save/roundtrip. It has no early gap stopping and no automatic quality claim.

```powershell
python $guard128 --timeout 240 preview128-eight-050-a "$bin128/preflop_interactive_bench.exe" $largeConfig128 coupled_preview128_v1 50 target/research-preview/preview128-eight-050-a.gtop 10
python $guard128 --timeout 180 quality-large128-050-a "$bin128/preflop_preview_quality_gpu.exe" "$lab128/target/research-preview/preview128-eight-050-a.gtop" $largeReference128 $cache128 23000
```

4. If the remaining window supports the whole bounded job, run the **predeclared fixed1000** large trajectory and global quality evaluation. This is the comparable iteration budget to the64 initializer candidate; it does not become a convergence claim if its own or full gap remains above0.005. No intermediate success is used to shorten this fixed run.

```powershell
python $guard128 --timeout 1200 preview128-eight-1000-a "$bin128/preflop_interactive_bench.exe" $largeConfig128 coupled_preview128_v1 1000 target/research-preview/preview128-eight-1000-a.gtop 10
python $guard128 --timeout 180 quality-large128-1000-a "$bin128/preflop_preview_quality_gpu.exe" "$lab128/target/research-preview/preview128-eight-1000-a.gtop" $largeReference128 $cache128 23000
```

Do not queue this long job if it would displace final safety/restore checks. If only one large quality evaluation fits, prioritize1000; record50 quality as not run rather than infer it. Do not run a fresh full1000 simply to manufacture a speed ratio. An optional fresh full50 timing repeat under the exact same binary/inputs/cadence can measure implementation throughput, but cannot prove time-to-quality speedup against a1000-iteration candidate. The existing full50 timing is separately labeled historical timing if reused.

## Gates and reporting

Keep all numerical/native/constraint gates: frozen indices; finite normalized legal probabilities; coherent pot/tie invariants; native model mismatch rejection; unchanged frozen/forced/hero semantics; source arenas/cache/native files unchanged after evaluation; exact save roundtrip. Quality comparisons must rebuild/evaluate candidate averages under full payoffs, never relabel native headers or resume approximate regrets under full payoffs.

Global gates: reference learning gap<=0.005; candidate excess full-reference gap<=0.02; unilateral positive mean loss<=0.01 and max<=0.03bb/hand. Negative losses do not cancel positive losses. A candidate's own-model gap is distinct. Local gate: for hand mass>=0.0025, probability on actions losing>0.1bb under the fixed original reference continuation must be<=0.1. Keep rare-node failures and forced/unreachable/unsupported statuses explicit. A global pass is not a local or physical pass. Conditional self-play refinement, if measured elsewhere, does not waive the original-continuation gate.

The physical128 checks are already recorded separately. Native quality failures cannot be removed by those terminal results. Report cold initialization, publication, iteration/check, solver total, save/roundtrip, and research evaluation overhead separately. A10x claim requires matched-input time to the same passed usable-quality condition including any required refinement;8x fewer particles or an early publish alone is insufficient.
