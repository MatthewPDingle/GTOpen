# Paired continuation: completed development screen

**No candidate passed. The existing production model is unchanged.**

All 60 new postflop reference solves passed the CPU and GPU accuracy limits.
Maximum gaps: 0.09965% and 0.09972% of pot.
Recorded solver time: 16.7 minutes, excluding pauses and process overhead.

The frozen screen compared 72 corrections, leaving each of four policy families
out in turn. The unchanged baseline was retained for every comparison. The
original and shallow-policy audits were development data in this experiment.
Two new synthetic policies added coherent reaching ranges across called opens,
called 3-bets and called 4-bets. They are not claimed GTO or real-player policies.

## Result

Mean adjusted call-versus-3-bet error: baseline 0.2117bb; best screened mean 0.2080bb.
That is only 1.74% improvement, below the required 5%.
The same choice worsened its weakest family by 7.84% and failed the leaf-error guard.
The best choice satisfying both nonregression guards was slightly worse than
baseline overall (0.2126bb, 0.43% worse).

| Family held out | Baseline adjusted MAE | Best-mean correction (rejected) | Qualified classes | Decision mass |
|---|---:|---:|---:|---:|
| original | 0.2072bb | 0.2039bb | 30 | 19.5% |
| shallow | 0.2053bb | 0.1797bb | 41 | 25.8% |
| linear | 0.2140bb | 0.2307bb | 169 | 100.0% |
| polar | 0.2203bb | 0.2178bb | 169 | 100.0% |

No choice reached the required 5% improvement. Fourteen satisfied the
per-family action guard and 46 satisfied the leaf guard, but none passed all
requirements. No new candidate was exported and no prospective test or native
integration was launched. The original compact candidate remains only as a
record of the earlier failed screen.

## Interpretation and next step

Broader development data filled the action-support gaps in the synthetic
families: all 169 classes qualified there. This did not produce a correction
that transferred reliably across families. Stronger fitting or more features
alone was insufficient in this bounded experiment.

This is not proof that learned continuation values cannot work. There are
only four related policy families, and each new family uses ten stratified
boards per branch. Development selection is not an independent accuracy test.
The two older audits have different coverage and more boards; family averages
are weighted equally, not in proportion to sample count or a real-game mix.
Sampling noise, limited range diversity and the shared residual form remain
plausible explanations. This screen does not establish which dominates.

The recommended next experiment is an uncertainty audit before another model
search: quantify paired board-sampling variation in the action-value targets,
then preregister one independent panel repeat for the unstable contexts.
If discrepancies persist beyond that noise, test a representation with
explicit interactions between both complete ranges rather than another
global hand-feature correction. That is a new study; do not reinterpret
additional samples as a way to turn this failed screen into a pass.

Port 56708 remains the existing build. Serena automatic dashboard opening
was disabled separately at the user's request. See completion.json for label
hashes, training-screen.json for every result and PROTOCOL.md for frozen gates.
