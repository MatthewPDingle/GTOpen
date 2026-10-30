# Complete preflop learning cycles: integration, 2 October 2026

The experimental trainer now has a separate complete-round checkpoint and a shared-network fitting objective that uses accumulated evidence at every supported preflop decision. Published synthetic CPU and CUDA controls pass. The authenticated native collection workers and complete scientific runner are still to be connected and qualified. No new scientific comparison has started, and this does not establish accurate poker ranges or production readiness.

## What changes

At fitted stacks, the typed played policy already uses cumulative preflop regrets instead of letting a single retained hand visit dictate a later decision. The new fitting path teaches the shared network those complete supported preflop targets as well. This matters because predictions at withheld stacks depend on that network rather than a fitted-stack table.

For each supported hand class, the target is cumulative regret divided by the generation scale, original actor class mass, completed updates and starting stack. Original class mass then weights the loss once. It does not multiply an already weighted target a second time. A class with no supported counterfactual generation is excluded from training truth. No premium-hand action floor or invented observations are added.

Postflop uses retained importance-weighted physical-visit advantages in the same stack-normalized units. Each fitted context has an explicit positive loss weight, and its preflop/postflop proportions are explicit. **The 25%/75% proportions, four fitting steps, two board draws and seven-visit reservoirs here are synthetic software-control settings, not a selected scientific recipe or a sufficient sampling budget.** Changing these choices in a future study requires prospective declaration.

The network and Adam optimizer start fresh from the declared seed for each actor fit. Only complete rounds can be restored; an unfinished optimizer step is not a restart boundary.

## Complete rounds and restoration

The checkpoint includes both newly fitted networks, every fitted context's cumulative preflop state, class-stratified deal sampler, action RNG, both postflop retention RNGs/data, and the ordered played-model bank. Every collection must identify the same frozen played model. Board contributions are replayed from the previous state and frozen recipe before accepting the staged cumulative update. Both fit receipts bind the actual dense/sampled target calculation, context mixture, networks, generation and registered numeric path.

Saved cumulative histories must extend the previous histories and identify the model that actually played that generation. The model produced at the end remains outside the played bank until it has generated a subsequent round. Canonical array types/shapes, unused tails, public action geometry, card visibility, iteration bounds and fixed configuration are checked on publication/restoration. A deliberately interrupted publication leaves the previous checkpoint usable; orphan immutable objects are not a resume pointer. The eventual runner must publish that pointer only after complete collection/fit metrics exist.

Checkpoint validation reuses the qualified visible-input checks without constructing all fitted preflop policies merely to check a postflop row. Full state, model and catalog authentication remains mandatory. This removes unnecessary preparation; the small-control timings below are not a production speed benchmark.

## Actual software evidence

The [published CPU control](preflop-expected-training-checkpoint-check-v1-result.json) completed in 349.891 seconds. It covers 362 and 387 input representations, both players, fitting at 20/40/100/200/400bb, and registry-only withheld 60/150bb contexts. It executes three complete synthetic rounds for 362 inputs and one for 387. Restoration reproduces the next source deals, board plans, action draws, retained visits and retention RNG state exactly, including reservoir overflow.

An independent scalar reference checks 9206 legal preflop target entries per representation plus the weighted postflop grouped targets, context proportions and within-observation variance. Maximum target/weight error is 5.55e-17; maximum chunked-versus-direct CPU gradient error is 1.25e-16. All 31 invalid/interrupted cases are refused, including partial contexts, mixed collection models, missing boards/fits, changed target/objective/network identities, preflop visits in the postflop reservoir, noncanonical arrays, changed boundary labels and detached/rewritten histories.

The [published CUDA control](preflop-expected-training-cuda-check-v1-result.json) completed in 65.641 seconds on the RTX 3090, Torch 2.6.0+cu126 / CUDA 12.6, with TF32 disabled. Both representations and both actors fit all five contexts using four synthetic steps each. Captured fitting agrees with an independent eager CUDA loss/backward/Adam implementation: maximum parameter difference 0, maximum final-loss difference 1.4e-09. All four synthetic fits reduce their declared objective. Actual returned fits publish and restore complete joint checkpoints. Peak allocated CUDA tensors: 44894720 bytes; this excludes desktop allocations and says nothing about full native-board memory requirements.

Initial passed source/evidence is preserved separately before the history/allocation hardening and redundant preparation removal. The initial sandbox invocation could not access existing user-site NumPy and stopped before fixture/test execution; its environment failure remains recorded. Owner-account execution used the existing packages without installation. Final staging and published controls are separate evidence. None invokes native poker exports, fits scientific weights or changes production.

## What this does not establish

The contexts/public trees and compatible entry law are real preserved inputs, but all-in strengths, board payoffs and physical-visit targets in these tests are invented. Synthetic fit loss and exact restoration do not certify equilibrium, action values, improved AA decisions, agreement with GTO Wizard, multiway behavior, stack-specific opening ranges or generalization accuracy. The existing inherited BTN opening range and restricted preflop tree are not expanded by this integration.

The checkpoint/receipt components cannot authenticate a native process merely from a tree hash. The next work is to connect typed native board and physical/posterior-river workers, retain executable/request/process provenance and insert only postflop physical visits, then profile a representative full round against the hardware/memory/disk reserves. After that qualification, register a genuinely adequate board budget and independent stability/payoff comparison before consuming scientific training/test data.

The read-only drive inventory during preparation showed about 282 GB free on S and 13 GB on T. Future native-board/training artifacts should use S, with reserves rechecked at admission; do not place a large store on the nearly full repository drive or delete preserved failed evidence to make it fit. These are a current inventory observation, not a reserved storage allocation.

The original comparison, failed improvement criterion, models, budgets and failures remain unchanged. Production on 56708 is untouched. No GitHub push or deployment. The broad goal of accurate flexible preflop ranges remains open.
