# Trained pilot-bank and archive integration control

The CPU-only September 25 control passed using the already audited two-update later-action pilot. It is an implementation fixture, not an effectiveness test or a substitute for the two complete 78-update trials.

The new loader authenticates the completed training and independent-review identities, validates the typed checkpoint and its referenced objects, and returns only played generations with fixed linear weights. For the pilot, that means generations 0 and 1 with weights 1 and 2, excluding the unplayed generation 2. Version-7 models are explicitly adapted to the already qualified complete-bank policy evaluator. The loader does not rescan all raw training batches, which are not inputs to policy inference; their completed audit remains bound by its saved identity.

On one previously inspected physical deal, the control compared the pilot's two-model average with its original initial model as an integration fixture. It duplicated this pair in both seed slots and checked that the duplicate full-profile results matched exactly. A separate scalar accumulation of each model's probabilities and the player's own earlier-action reach matched all 455 averaged query rows and their supports exactly: maximum policy and reach differences were both zero.

The entire native batch was then archived through the existing owned-scratch workflow. All seven evidence files were read back with identical hashes and byte lengths after release of the verified temporary copies. The retained archive and ownership records use 122,845 bytes. The complete control took 6.719 seconds, used no GPU and drew no fresh evaluation samples. It coexisted with the GPU training job without changing its files or production.

This small pilot fixture does not establish the eventual full-study archive size. Before admitting the final held-out evaluation, measure a representative batch using the four final complete policy banks and preserve a storage margin. The full training audits, two-seed stability calculation, final held-out registration and independent statistical readback remain outstanding.

Evidence: `crossed-trained-bank-control-v1-registration.json` (SHA-256 `97dcc5644a4e0b4f90ec299e18c3ea9ec26410c5819bca41cfca72e699d30f40`) and `crossed-trained-bank-control-v1-result.json`.
