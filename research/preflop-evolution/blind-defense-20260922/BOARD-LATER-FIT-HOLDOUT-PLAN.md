# Proposed next diagnostic: more fitting on fixed later-play data

The saved metrics show a consistent decline in the fraction of grouped training
error removed as the candidate datasets grow. This warrants checking fitting
capacity, but does not prove that optimization is the main source of range error.
Interpret the completed root-action audit and policy-effect analysis alongside
this diagnostic. Do not extend or alter the finished board-root experiment.

## Fixed comparison

Use generation 77 from both board-root candidate runs, separately for BB and BTN:
four already retained reservoirs. Generation 77 supplied a played policy;
generation 78 did not. Bind original checkpoint, reservoir, context and metric
hashes. Read the original files without rewriting them or creating new deals.

Compare the current 512 optimizer steps with 2,048 and 8,192, holding architecture
(302 / 64 / 64 / 4), loss, learning rate (0.003), initialization seed, data and
optimizer trajectory fixed within each dataset. Record checkpoints from one
continuous trajectory rather than comparing different random starts. Preserve
the qualified CUDA gradient calculation and disable TF32 as in the source fits.

## Honest holdout

Partition by identical visible input, before training. Every row with the same
canonical active-feature vector must stay in the same split even if native
observation keys differ. The additional visible poker features are deterministic
functions of those active features. Do not split merely by row or by native key;
that could place identical model inputs on both sides. Player datasets remain
separate. Record input collisions and legal-menu coverage.

Use a fixed salted hash split of 70% training, 15% validation and 15% final test.
Register the salt before fitting. Derive normalization only from training targets;
apply that unchanged scale to validation and test. Preserve source importance
weights and legal-action masks. Validate the objective against a direct weighted
calculation, with controls for duplicated inputs and differing legal menus.

Use validation loss to compare the three fixed fit budgets. Examine final-test
loss once, for the 512-step baseline and the validation-selected budget. Keep all
four datasets and all results, including worse fits. Report normalized loss,
raw-scale loss, sample weights, runtime and GPU allocation. Do not convert loss
into an alleged probability of correct poker play or a preflop EV guarantee.

If longer fitting lowers training error but not held-out error, avoid simply
increasing production fit time. If it helps both, test the change in a separately
specified full training comparison with new evaluation deals. A width or feature
change would be a later, explicit experiment; it is not part of this first test.

## Resource and execution requirements

No training is started by this plan. Implement and qualify the data split and
loss calculation first. Wait for the current CPU audit to release its research
ownership lock. Use CUDA for the fits and bounded CPU preparation, respecting
production activity and heavier competing workloads. Light desktop/browser/video
activity is allowed under the user's approved sharing preference; do not copy
the old near-idle 10% GPU start threshold into this new study.

Proposed run bounds: 30 minutes, 500 MB additional retained output, 8 GB maximum
device allocation, no new solver/game trees, no production deployment. Admit
against a fresh storage/resource check and retain checkpoints, split identities,
metrics and source hashes. No automatic sample extension or outcome-driven
changes to the three registered fit budgets.
