# Frozen 32-v2 holdout and AA supplement results

Sources: `raw/independent32-physical-a.log` and `raw/supplement-aa-nine-{herding64,exchange32-v2}-a.log`. Parent executed the jobs. This review changes no candidate or gate.

## Nine-way AA uncertainty resolved

Both supplemental runs used the exact same 1,000,000 compatible physical deals, seed2026091199. Physical AA equity is34.6251444%, with recorded95% half-width0.0930161pp. Full1024 is38.2106590%, error3.5855145pp.

| Frozen model | Equity | Physical error | Distance below7pp gate |
|---|---:|---:|---:|
|64-v1|39.6972605%|5.0721160pp|1.9278840pp|
|32-v2|41.0737974%|6.4486529pp|0.5513471pp|

Both distances exceed twice the reference half-width,0.1860322pp. The originally borderline32-v2 seen-case worst-hand boundary is now a pass for this supplemental reference. Original logs remain intact, and this does not remove failures elsewhere.

## Independent32 results

All24 physical references have100,000 accepted deals. The three core cases pass the registered per-case mean<=4pp and worst<=7pp bounds; their pooled mean is also below3pp. Sparse-six KK is the largest core error6.1498pp; its margin0.8502pp below7 exceeds twice its0.2918pp half-width.

| Case |32-v2 physical mean / worst | Full1024 mean / worst |
|---|---:|---:|
|Asymmetric3|1.5996 /2.6750pp|1.1200 /1.6836pp|
|Mixed4|1.3915 /3.4318pp|1.0183 /2.4411pp|
|Sparse6|2.2368 /6.1498pp|1.2164 /2.3405pp|
|Overlap asymmetric4, stress|2.8455 /8.5864pp|1.2455 /3.8714pp|

**32-v2 fails the independent overlap stress guard.** Additional mean error is1.6000pp against the+1pp limit; additional worst error is4.7151pp against the+2pp limit. KJo is the worst for both models, and both estimates are above the same physical mean, so their4.7151pp error difference does not inherit two independent reference errors. Its0.1765pp physical half-width cannot explain the2.7151pp excess over the permitted worsening. This failure is not averaged into the core cases, waived because absolute mean is small, or repaired by the AA supplement.

Rebuilt BB32-v2 mean error1.4789pp, worst2.8405pp: passes the existing BB limits. KQo equity25.6849% versus physical23.3060%, yielding call-minus-fold surplus+0.9521bb versus+0.7713bb; the cheap-call correction persists. Original BB already passed its seen audit.

Recorded rebuilt-context CPU terminal speedup is16.50x (0.04245ms versus0.70063ms). This is terminal-only, and the failed stress guard precludes calling it a universally accepted preview or claiming10x faster usable decisions.

64-v1's prior independent overlap result remains borderline/inconclusive pending the separately registered six-hand million-deal overlap supplement. Primary and supplemental policy trajectory results are separate gates and remain for the parent to assess.

## Completed 64 overlap supplement: mean guard fails

The later `raw/supplement-overlap-herding64-a.log` completes all six preregistered1,000,000-deal references, with the specified seeds and unchanged10,000,000-attempt cap. Attempts range2,506,244 to7,649,964. The original100k results above remain intact.

Candidate mean absolute error is2.4428664pp versus full1024's1.2981633pp: additional mean error **1.1447031pp**. Using the preregistered common-reference interval propagation at each reference mean +/- twice its recorded95% half-width gives **[1.0580214,1.1933884]pp**. This entire conservative propagated interval exceeds the+1pp guard. The prior borderline mean result therefore resolves to **failure**, without changing a threshold or candidate.

| Hand | Additional absolute error, point | Propagated interval (pp) |
|---|---:|---:|
|A5s|3.4875530|[3.3194909,3.4875530]|
|KJo|1.1537096|[1.1537096,1.1537096]|
|QJs|2.7053461|[2.4132344,2.9974578]|
|T9s|1.1584960|[1.1584960,1.1584960]|
|55|0.0299581|[-0.0299581,0.0299581]|
|KK|-1.6668441|[-1.6668441,-1.6668441]|

Worst absolute error remains KJo for both models throughout these physical-reference intervals: candidate5.1139903pp versus full3.9602808pp. Its worsening1.1537096pp is below the+2pp worst guard and is constant because both estimates lie above the common physical mean. Passing this worst guard does not cancel the failed mean guard. Both frozen compressed candidates consequently fail at least one independent overlap guard. This is terminal-model evidence; warm-start learning under full payoffs is a separate candidate that requires its own policy and performance validation.
