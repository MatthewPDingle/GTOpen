# E016 finite-extension terminal audit

**Reject E016.** The sealed amendment required both the new-six and pooled-nine cohorts to pass. The new-six cohort passes; pooled-nine fails the river regression guard. No further extension is permitted.

| Cohort | Baseline score ms | Candidate score ms | Aggregate gain | River median regression | River pairs >3% | Required | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| initial three | 11386.98130 | 10009.49030 | 12.0971% | +15.8921% | 3/3 | 2 | Fail |
| new six | 11442.33150 | 9966.96495 | 12.8939% | -2.3697% | 2/6 | 4 | Pass |
| pooled nine | 11448.19290 | 9984.28880 | 12.7872% | +3.7093% | 5/9 | 5 | Fail |

Verified the unchanged sealed protocol/script, all 12 new runs in prescribed alternating order, successful serialized execution, raw stdout/report equality, preserved binaries/build manifests and archived E016 source identity. All 36 new and 54 pooled complete non-timing records match exactly, including full state fingerprints, workload/configuration, exploitability bits and stopping iterations. Prior primary/broader review files remain unchanged.

All original observations are retained, with no timing exclusions. D028 is excluded as originally designated diagnostic. The initial failure remains failed; the favorable new subset cannot substitute for the pooled result. The amendment was explicitly outcome-triggered and makes no significance claim.

Pooled river medians are 108.5058→112.5306ms. Its separate initialization median rises 89.4131→94.1708ms, while solve falls 18.0553→17.0935ms. These medians are nonadditive and do not identify a cause. Rejection is a performance-rule outcome; no numerical mismatch was found.

This audit uses preserved run/build/source archives, so restoring the accepted E015 checkout does not alter the evidence. No builds, GPU execution, production edits or dashboard writes were performed.
