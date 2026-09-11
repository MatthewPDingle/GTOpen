# Large full-model warm-start results

This exploratory development experiment seeds a fresh full1024 solver from a completed64-particle average policy. It does not copy approximate regrets, learning averages, or iteration count into the full model. Positive regrets use scale0.01 (stored f32 value0.009999999776482582); learning averages start at zero and target iteration starts at0. Before a full iteration, those averages are untrained. HERO sources are unsupported; the tested eight-seat fixture has no forced/frozen nodes. Existing constraint-preservation semantics remain part of the implementation contract, not newly exercised modeled-seat evidence here.

## Source64 iteration50, scale0.01: completed, failed accuracy gate

`raw/warmstart-large64-50-scale-0p01-a-result.json` records returncode0, no cancellation reason, source`6a7b4842798f84e97dcdc956333123d429be6731`,781.375s guarded process time. Its log contains all five registered full-model checkpoints, each with exact native save/reload verification:

| Fresh full iterations | Full-model learning gap bb/hand | Gap available, cumulative seconds | Through native audit, cumulative seconds | Cumulative iteration compute seconds |
|---:|---:|---:|---:|---:|
|2|8.64459309|27.15588|35.19496|14.87642|
|10|12.05366270|101.54426|108.07186|73.73519|
|30|3.13492153|256.54653|263.13751|214.65640|
|50|1.41180538|411.92482|419.07034|355.94996|
|100|0.42837396|773.79314|780.45132|703.16912|

All gaps remain far above the0.005 target. At100, the gap excess over the registered converged full reference0.004783754646191074 is0.42359020, already above the0.02 global excess gate. A unilateral or local audit could not turn that failing conjunction into a pass; those other metrics have not been evaluated and are not asserted. The early gap increase from2 to10 is retained rather than hidden; the initializer does not guarantee monotonic learning.

Final check costs7.50123s. Source load is1.22320s; GPU initialization is1.27523s, with initialized cumulative time4.67907s. The reported780.45132s includes initialization, full iterations, all registered checks, saves and reload audits, but **excludes creation of the64 source**. Source-creation cost must be added for any end-to-end comparison. This is not evidence of a speedup over a fresh full100 solve: no matched fresh100 timing/quality baseline was measured, and the existing resumed full1024 reference has different timing history.

Native roundtrip success establishes persistence consistency, not decision quality. This source50/scale0.01 candidate did not achieve the target or global tolerance within the registered100 full-iteration cap. It is not promoted as a qualified warm start, does not remove64's physical rejection, and does not demonstrate10x time to usable accuracy.

## Source64 iteration1000, scale0.01: completed, also failed accuracy gate

`raw/warmstart-large64-1000-scale-0p01-a-result.json` records returncode0, no cancellation reason, the same source commit, and773.125s guarded process time. All five registered checkpoints again verify exact native roundtrip:

| Fresh full iterations | Full-model learning gap bb/hand | Gap available, cumulative seconds | Through native audit, cumulative seconds | Cumulative iteration compute seconds |
|---:|---:|---:|---:|---:|
|2|15.56737270|26.89656|33.46503|14.36384|
|10|11.05933978|98.55016|105.36816|71.94326|
|30|2.89062266|252.82705|261.88470|211.88138|
|50|1.96852607|409.64132|416.41070|352.13084|
|100|0.51658592|765.16337|772.05666|693.37091|

The final gap0.51658592 misses the0.005 target; excess over the registered full reference is0.51180217, failing the0.02 excess gate. Final check takes7.51003s. Source load is1.26214s, GPU initialization1.39746s, and cumulative initialized time4.89435s. Total772.05666s includes initialization,100 full iterations, five checks and native audits, **excluding the creation of the1000-iteration64 source**. No matching fresh full100 runtime/quality control is available, so neither relative speed nor benefit is established.

The source64 iteration1000 average policy previously passed its full-reference global relative evaluation. That success does not transfer automatically to this conversion into positive initial regrets followed by zero-initialized average accumulation. This particular conversion/run fails the gate despite the better source. The findings reject these two tested large scale0.01 warm-start outcomes at their registered100-iteration cap; they do not prove every possible initializer or scale would fail. Unilateral/local/physical audits of these resulting full policies are still unmeasured, rather than presumed passing.

Large scales0.1 and1 remain unrun in the evidence reviewed; their previously recorded small development results are not substitutes. All remaining runs are bounded by the pass deadline and production-validation priority.
