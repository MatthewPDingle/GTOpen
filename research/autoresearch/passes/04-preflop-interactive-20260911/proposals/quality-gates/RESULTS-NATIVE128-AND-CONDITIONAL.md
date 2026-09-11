# Native128 small policy and conditional refinement results

Only completed records whose companion `*-result.json` has `returncode: 0` are summarized. All four small trajectory jobs, thirteen small quality jobs, and both conditional jobs below completed successfully. Numerical execution success is distinct from quality acceptance. Source commit in the small quality records is `6a7b4842798f84e97dcdc956333123d429be6731`, with an empty working diff; cache sample count is20000. Inputs, thresholds and labeling remain those in `HERDING128-NATIVE-PROTOCOL.md`.

## Native128: global improvement, remaining local failures

The three small scenarios are development/cross-model constraint regressions, not a newly blind policy confirmation. References are the pre-existing full1024 checkpoints registered in the protocol. The independent128 physical result remains separate; its pass does not override these native policy failures.

Global gates are reference gap<=0.005, excess full-reference gap<=0.02, mean positive unilateral loss<=0.01, maximum positive unilateral loss<=0.03bb/hand. Every saved primary checkpoint was evaluated, including failures.

| Case / iteration | Full-reference candidate gap | Excess gap | Mean positive loss | Maximum positive loss | Global gates |
|---|---:|---:|---:|---:|---|
| Development3 /2 |0.45811023|0.45665649|0.13047733|0.23287313|Fail|
| Development3 /10 |0.01066196|0.00920823|0.00278207|0.00539219|Pass|
| Development3 /20 |0.00227661|0.00082287|0.00010794|0.00014730|Pass|
| Fixed/frozen4 /2 |1.84201443|1.83703362|0.61156333|0.63308254|Fail|
| Fixed/frozen4 /10 |1.67885132|1.67387050|0.56310530|0.58970402|Fail|
| Fixed/frozen4 /30 |0.56011885|0.55513804|0.21524623|0.23891319|Fail|
| Fixed/frozen4 /50 |0.16464991|0.15966910|0.06958305|0.07881938|Fail|
| Fixed/frozen4 /100 |0.02855315|0.02357233|0.01024952|0.01164134|Fail: excess and mean|
| Adaptive3 /2 |0.97809529|0.97428489|0.13496749|0.17768052|Fail|
| Adaptive3 /10 |0.03836107|0.03455067|0.00919458|0.01533297|Fail: excess|
| Adaptive3 /30 |0.00492713|0.00111673|0.00043719|0.00049174|Pass|
| Supplemental development /100 vs full500 |0.00075740|0.00075588|0.00011254|0.00014437|Pass|
| Supplemental development /500 vs full500 |0.00075573|0.00075421|0.00011208|0.00014114|Pass|

Primary own-model stopping: development stopped20 with gap0.00180540 and elapsed0.02830s; adaptive stopped30 with gap0.00450013 and elapsed0.06073s. Fixed/frozen reached100 cap with own gap0.02777290, not converged, elapsed0.39565s. Supplemental fixed500 completed its explicit iteration count, own gap0.00031877, elapsed0.25156s. These tiny-tree times include their reported initialization/check/publication phases and are not a large-game latency or10x result.

The unchanged local gate evaluates one action followed by the original full reference continuation at its fixed arriving ranges: hand mass>=0.0025, action loss>0.1bb, at most10% probability on those actions. Final checkpoint results:

| Case | Path/seat | Worst relevant inferior-action probability | Local gate |
|---|---|---:|---|
| Development20 |root BTN|0.014610|Pass|
| Development20 |[1] SB|0.456348|Fail|
| Development20 |[2] SB|0.317052|Fail|
| Development20 |[2,1] BB|0.000174|Pass|
| Fixed/frozen100 |root CO|not applicable|Forced; not counted as pass|
| Fixed/frozen100 |[1] BTN|0.997023|Fail|
| Fixed/frozen100 |[2] BTN|0.029356|Pass|
| Adaptive30 |root BTN|not applicable|Forced; not counted as pass|
| Adaptive30 |[1] SB|0.499953|Fail|
| Adaptive30 |[2]|not applicable|Unreachable under reference; unverified|
| Supplemental500 |root BTN|0.00000100|Pass|
| Supplemental500 |[1] SB|0.456348|Fail|
| Supplemental500 |[2] SB|1.000000|Fail|
| Supplemental500 |[2,1] BB|0.00000001196|Pass|

The development[1] reference joint reach is1.43306e-8, with reference weighted local regret0.0562581bb; candidate500 regret0.0502366bb. That weak, rarely reached continuation explains why a globally small error can coexist with local failures, but does not waive the gate. Development[2] has reference reach0.00531269, candidate500 weighted local loss0.00180673 versus reference0.00006126bb; it is also a retained failure. More iterations do not establish that these tails disappear. Supplemental100 already has[2] bad mass0.9999985.

Raw evidence: `raw/small128-{development-primary,fixed-frozen-primary,adaptive-primary,development-fixed500}-a.log`; `raw/quality-small128-*-primary-a-checkpoint-*.log`; `raw/quality-small128-fixed-{100,500}-a.log`. Primary and supplemental reference definitions stay separate.

## Full-payoff conditional refinement of64 previews

Completed inputs: `raw/conditional-preview64-50-full-a.json` and `raw/conditional-preview64-1000-full-a.json`, with corresponding successful runner result records. Both use the same three registered development BB paths. They capture the source prefix/reaches before switching to full1024 continuation payoffs. Source-model and full-model baseline comparisons are reported separately; retention uses the **full-payoff** baseline.

Each method attempts100 local iterations. It retains the last completed finite refined policy only when its summed full-payoff conditional-game gap strictly improves; otherwise it keeps the exact baseline. This rule certifies only the conditional self-game comparison. It does not qualify the source prefix, physical model, whole-game strategy, or original-continuation local tails.

|64 source iterations|BB spot|Full baseline conditional gap|Retained gap|Retained policy|Compute seconds|
|---:|---|---:|---:|---|---:|
|50|BTN raise6, SB fold|0.28110363|0.00111021|Refinement100|0.26799|
|50|BTN raise10, SB fold|0.31899149|0.00073032|Refinement100|0.29104|
|50|CO raise6, BTN call, SB fold|0.11262841|0.00110741|Refinement100|0.60175|
|1000|BTN raise6, SB fold|0.00039414|0.00039414|Exact baseline|0.31403|
|1000|BTN raise10, SB fold|0.03953934|0.00308129|Refinement100|0.31597|
|1000|CO raise6, BTN call, SB fold|0.13399997|0.00174580|Refinement100|0.60348|

The already-good1000/BTN-raise6 baseline is correctly preserved: the attempted refinement gap0.00089900 is worse than0.00039414. Its fixed-source weighted loss would also worsen0.00034924→0.00064371 and bad-action mass0.011161→0.040619. Retention prevents this particular regression without asserting that all other quality metrics improve.

The three-way CO-raise source-model gap differs from its full-payoff evaluation: source50 gives0.11236874 versus full0.11262841; source1000 gives0.12469323 versus full0.13399997. The retained comparison correctly uses the latter values. The first two paths end in heads-up continuations, so their source/full baselines match.

Original source-continuation action-loss tails remain a separate diagnostic:

|64 source iterations|BB spot|Old bad-action mass|Retained bad-action mass|Old weighted loss bb|Retained weighted loss bb|
|---:|---|---:|---:|---:|---:|
|50|BTN raise6|0.878197|0.999991|0.240918|0.089819|
|50|BTN raise10|0.917737|0.998737|0.292116|0.052636|
|50|CO raise6/call|0.975084|0.757381|0.089602|0.004358|
|1000|BTN raise6|0.011161|0.011161|0.000349|0.000349|
|1000|BTN raise10|0.799648|0.947867|0.028419|0.017887|
|1000|CO raise6/call|0.940519|0.999487|0.102909|0.035012|

Changing the whole conditional continuation can lower its self-game gap and weighted action loss while increasing mass on actions inferior under the *old* future policy. These measurements are not interchangeable. They do not satisfy or supersede the separately registered original full-reference local gate. All six cases explicitly retain `prefix_unvalidated: true` and `quality_qualified: false`.

All six source arenas, source model identities and outside/forced/frozen arenas restore exactly; neither source native file was written. Whole three-case runtime was4.89887s for source50 (load1.49506s) and4.77693s for source1000 (load1.26166s). Individual compute0.268–0.603s excludes preparation, backups, audits and restoration; full per-case hybrid cost is0.892–1.323s. Prefix-generation time is additional. There is no end-to-end10x or full-quality claim.
