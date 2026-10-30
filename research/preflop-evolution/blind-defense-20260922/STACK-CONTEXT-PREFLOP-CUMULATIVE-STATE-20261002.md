# Retaining expected preflop evidence across learning rounds

The next isolated component is implemented and its published software checks pass. It retains expected targets for every preflop decision across learning rounds. This addresses the retention part of the diagnosed AA problem: the old learner could keep one unlucky outcome and let that single observation completely override its neural prediction. The new component combines successive rounds of evidence. **It has not yet been connected to native poker calculations or used to train a scientific model.**

## What it retains

For every decision, hand class and legal action, the component stores cumulative regrets: the accumulated advantage of that action over the supplied frozen policy. Each round adds the exact fold/all-in contribution and the mean of its declared board contributions. The update multiplies by the original private-card-compatible class mass and a fixed common generation scale. Opponent history remains weighted; the acting player's earlier action probabilities do not suppress learning at its later decisions.

All decisions and declared board draws must be present before an update is accepted. The component checks context, terminal matrix, policy, model, board order and target identities before changing its in-memory state. Serialized restoration also checks the complete state and generation history. Checkpoint restoration produces the same subsequent plans and results as an uninterrupted calculation. This qualifies the in-memory update and serialized format; an atomic on-disk transaction with the actual training cycle is still outstanding.

The state records board draws and supported learning rounds separately. It explicitly records zero sampled hand-history visits, because these calculated targets are not additional observed hands. Classes absent from the original entry population, and branches never entered by the opponent, retain their supplied fallback policy. There is no premium-hand calling floor. Stored board sums and squared sums span changing policies; they are descriptive records, **not confidence intervals or independent samples from one fixed policy**.

## What the checks establish

The two published controls ran independently in parallel. The basic control used four rounds and twelve declared synthetic board contributions. It reproduced the previous BB-root update exactly and matched an independent scalar calculation within 2.84e-14. Twenty-six malformed, changed, replayed, incomplete or overflowing cases were refused without altering the current state or next plan.

The extended control checked the existing 20, 40, 100, 200 and 400bb geometries. Three rounds per depth matched independent scalar updates within 5.69e-14, with exact restart agreement at every depth. An additional synthetic sequence showed that later favorable targets can overturn one initial unfavorable target. **This is a retention-mechanism check, not evidence that real AA calling ranges have improved.**

An earlier software check incorrectly required bit identity between two different floating-point addition orders for the stored moments. The maximum difference was 8.89e-16. Its failing source and diagnosis are preserved; only that independent reference check was corrected to a tight tolerance. Checkpoint bit identity remains required, and the learner did not change after its first successful control. Original scientific inputs, results and decision rules remain unchanged.

## Next work and limits

Next is an authenticated producer of native/current-policy targets and integration with complete on-disk training cycles, followed by representative resource measurements and a prospectively specified stability comparison. Averaging compatible opponent holdings helps reduce noise, but public-board sampling still needs enough representative draws. Keeping every old sampled visit alone was already shown to be insufficient.

This remains preparation for the current heads-up BB-versus-BTN continuation context. It does not establish improved poker accuracy, stack-specific opening ranges, five-bet support, multiway play or agreement with GTO Wizard. The original comparison did not pass its improvement criterion. No training run is active, no production behavior changed, and nothing was deployed on port 56708.

Evidence: [component](../../../tools/research/preflop_expected_regret_accumulator_v1.py), [five-stack controls](../../../tools/research/preflop_expected_regret_accumulator_check_v2.py), [published result](preflop-expected-regret-accumulator-check-v2-result.json), [review receipt](preflop-expected-regret-accumulator-review-v1.json), [expected-target derivation](STACK-CONTEXT-PREFLOP-EXPECTED-TARGETS-20261002.md), and [AA diagnosis](STACK-CONTEXT-AA-DIAGNOSIS-20261002.md).
