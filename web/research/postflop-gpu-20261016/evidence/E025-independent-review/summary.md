# E025 independent terminal review

**Confirmed rejected.** The fixed primary score is 9,920.3617 → 10,013.3950 ms, a gain of −0.9378014917%. It fails the unchanged 2% aggregate gate. No fixture trips the repeated material regression guard.

The file-only audit passed 919 assertions over 103 pinned inputs. All 18 complete non-timing result objects and 138 convergence checks agree exactly; the full non-timing stage trajectories agree too. The ordinary unit screen was 84 passed, 4 ignored, with the unchanged 88-test inventory. All seven processes follow the frozen order: V025-unit, B083, E025R1, E025R2, B084, B085, E025R3. No sample was excluded, replaced or extended.

Fresh isolated build artifacts, correct package/source paths, source-map equality, complete unchanged CUDA embedded in both executables, authorization/review precedence, binary and raw-log hashes, and the actual E025R1 patch alias were verified. Active candidate custody captured all 162 hashes before restoration; precisely plan.rs and game.rs differed from accepted E020. The additive cleanup supplement pins the root restoration record.

| Fixture | Baseline median ms | Candidate median ms | Gain | Pairs >3% slower |
|---|---:|---:|---:|---:|
| rainbow | 5873.1075 | 5894.5188 | -0.3646% | 0/3 |
| two-tone | 3929.0673 | 4026.4652 | -2.4789% | 1/3 |
| river | 118.1869 | 92.4110 | 21.8094% | 0/3 |

The three paired whole-suite gains were −0.9693%, +0.5172%, and −1.5719%. Component median differences below are candidate minus baseline; per-component medians do not add to the median complete-cycle delta.

| Fixture | Build ms | Init ms | Solve ms | Readback ms | Full cycle ms |
|---|---:|---:|---:|---:|---:|
| rainbow | +3.7731 | -5.1269 | +12.4275 | +24.5641 | +21.4113 |
| two-tone | -13.5720 | +49.8843 | +46.4562 | +3.4656 | +97.3979 |
| river | +0.0008 | -24.0255 | -1.6766 | +0.0557 | -25.7759 |

River’s observed 21.8094% improvement is descriptive. Its median initialization was 24.0255 ms lower and solve time 1.6766 ms lower. Two-tone was already stride-aligned, yet its complete cycle was 2.4789% slower in this cohort. These observations do not isolate padding as the cause of any component change, establish statistical significance, or justify retaining a selectively scoped version. The unchanged whole-suite gate rejects E025.

No broader original F32/state/menu/resume/continuation, wide-turn holdout or cumulative qualification was run after the failed screen. The compressed primary matches and candidate-shared unit checks do not establish universal raw-F32 or capacity behavior.

The first file-audit attempt reached the final chronology check and failed because the inherited reviewer expected `authorization.authorized_at`; the actual sealed schema uses `authorization.at`. The original script, invocation, error and exit remain preserved. Additive `audit-primary-r2.py` changes only that field and passes. This was a reviewer repair, with no native rerun or changed measurement.

The registered timing boundary includes runtime NVRTC/JIT and readback; Cargo compilation, correctness hashing, final destruction, browser/API work and disk persistence are excluded. No speedup or acceptance is claimed.

Sealed validation: `validation.json`; exact source custody: `source-custody.json`; additive root cleanup check: `cleanup-supplement.json`.
