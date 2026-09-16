# N06: bounded nonlinear correction to the existing predictor

Specified 16 September before fitting. Research only; preserve port 56708.

The fixed linear feature extensions and conservation-aware fit did not pass
training-family screens. Test whether a small nonlinear residual can represent
interactions that those linear functions miss. Retain the ordinary shape/0.1
ridge prediction as the base; learn only a correction, projected to zero
compatible-mass mean separately for each two-player context. This preserves
pot accounting. No per-hand lookup table or player-behavior model is trained.

Use the original 24 training cases plus two N01 development cases. Exclude one
whole source family at a time, including its development cases. No N01 test or
N03 reserved evaluation labels enter training or selection. Four fixed choices:
8 or 16 ReLU hidden units, output-weight penalty 0.01 or 0.1. Average two fixed
seeds, 90210 and 20260916, per choice. Standardize the 104 input features with
the training fold's existing ridge statistics; clip network inputs at +/-6
standard deviations. The ridge base is unchanged. Record clipped mass.

Train on CPU only, two threads, binary64, 500 full-batch Adam steps at learning
rate 0.01. Input weights use normal initialization scaled by 1/sqrt(104);
biases and output weights start at zero, so the initial predictor is exactly
the base. Loss is compatible-mass-weighted squared value error plus the fixed
output penalty times squared output weights and 0.001 times mean squared input
weights/biases. There is no validation-based early stopping or expanded grid.

Select by equal-family mean weighted hand-value MAE. Require at least 5% lower
mean error than the ordinary shape/0.1 control on the same 26 cases, with no
family more than 5% worse. Freeze only an eligible candidate. Any prospective
evaluation needs its own new-board protocol and must follow the freeze. Do not
use previously inspected evaluation data for a second selection.

The ensemble has 16 or 32 hidden units at inference and adds computation;
accuracy alone cannot justify adoption. A surviving model needs an independent
GPU implementation oracle and repeated matched timing against both its base
and ordinary Balanced, with the night-shift <=10% overhead target. Report
failures honestly. Nothing here alters the ongoing N03 protocol.
