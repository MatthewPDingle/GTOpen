# Fixed-continuation root estimator precision

This is an exploratory follow-up to the completed later-action matched study. Its confirmatory 65,536-deal results and intervals will not be extended, replaced or relabeled. We reuse already inspected archives and freeze all four complete self-play policy pairs: first-old, first-new, replication-old and replication-new. No network fitting, policy selection or fresh physical deals are involved.

## Question

With both players' continuation policies held constant, how much do private cards and runouts move the BB's estimated call-minus-fold and raise-minus-call values for each of the 169 hand classes? Does dividing the archived sample into fixed halves change the preferred non-jam action? This separates fixed-policy estimator variability from the policy movement observed in training, but does not quantify every source of training error.

## Implementation control

Reuse the earlier two 32-deal implementation batches. For each of the four frozen self-play pairs, reproduce the original profile and create four copies with only the root changed to pure fold, call, raise or jam (20 profiles, within the native evaluator's limit). Keep all later probabilities and legal-action metadata exactly unchanged. Verify:

- Original self-play payoffs reproduce the authenticated archive exactly.
- Every non-root row is identical to the original, and root rows retain their visible identity and legal menu.
- For every physical deal and both players, the original root mixture of the four forced values reconstructs the original payoff and expected rake within 1e-10.
- Folding loses exactly the existing BB contribution and incurs no rake.
- Native forward/backward payoff accounting, conservation and terminal mass checks pass.
- A separate CPU process rereads and verifies the saved transports and outputs.

The small control requires idle production, no competing research owner, 20GB RAM reserve, 40GB free on its output drive, the existing 800GB combined evidence ceiling with 2GB reserve, a 400MB output cap and a 10-minute bound. It preserves all generated control inputs and outputs and does not initialize CUDA.

## Archived-population pass, only after the control

Use all 2,048 batches / 65,536 deals in the completed compact evaluation, in original order. The archived policy transports provide inference results directly. Reconstruct forced-root transports; native evaluation needs no new model loading or GPU calls.

Store native outputs and source/transport digests in bounded compressed records. Preserve and authenticate the original source archives. Temporary reconstructed transport files may be removed only after verified durable publication of the corresponding result and regeneration metadata. First measure one control batch's bytes and elapsed time, then register a full-pass storage/time projection including scratch space and an adequate margin. Do not copy the entire policy transport into every durable batch, which would needlessly duplicate the existing evidence.

Report per bank and per native hand class:

- Sample count; mean call-minus-fold and raise-minus-call; paired standard deviation and descriptive standard error.
- Predetermined even/odd global deal halves (index, not payoff), their means and non-jam maximizing actions.
- Exact incoming-mass-weighted RMS per-class errors and half-sample action disagreement, alongside all class results.
- Between-bank paired differences on common deals as descriptive comparisons, without selecting a winning bank.

Interpret small counts honestly. Do not report zero uncertainty for an unobserved class, turn exploratory standard errors into simultaneous confidence guarantees, or infer a training budget directly from these fixed-policy measurements. Do not change the original study's statistical method or stopping rule.

## Limits

This is the value of a forced first action followed by the frozen continuation. Low-reach or unvisited later branches can retain weak fallback play. Maximizing these values is therefore not a proof of best response or accurate poker play. Only call/fold/raise estimator precision is the primary subject. The native conditional-private-pair jam calculation is retained to validate the root mixture, but is not the same estimator as training's exact integration over all compatible private hands; do not attribute its variance to the training jam target.

The analysis does not expand coverage to other stacks, positions, sizes or multiway pots. Its purpose is to choose the next learning experiment based on measured uncertainty rather than prettier ranges.
