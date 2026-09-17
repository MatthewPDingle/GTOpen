# Initial board-sampling audit

The small gains in the failed model screen are not well resolved by the existing
board samples. This does not reverse that screen or establish that sampling is
the only problem. No model has been promoted.

The audit resamples whole boards, paired across all three connected branches.
This matters: board effects cancel substantially in a call-versus-raise comparison.
For the linear family, ignoring that covariance would imply a target standard
error of 0.349bb, compared with the paired estimate of 0.125bb.

| Family | Boards per branch | Adjusted target SE, weighted mean | Fixed control MAE reduction | Conditional 95% interval |
|---|---:|---:|---:|---:|
| Original | 50 | 0.1452bb | +0.0033bb | -0.0125 to +0.0275bb |
| Shallow | 50 | 0.1408bb | +0.0256bb | +0.0031 to +0.0355bb |
| Linear | 10 | 0.1255bb | -0.0168bb | -0.0263 to +0.0001bb |
| Polar | 10 | 0.1125bb | +0.0025bb | -0.0054 to +0.0046bb |

Positive reduction means less error. The control is the previous rejected
best-mean configuration, with its original leave-family-out fits reconstructed
and frozen. These intervals hold those coefficients fixed. They do not account
for choosing the configuration on development data or uncertainty in fitting it.
The apparent shallow-family gain therefore does not qualify a candidate.

The two new families have only two boards per texture stratum; bootstrap intervals
from that small sample can themselves be unstable. Their lower SE than the older
families does not imply better estimates: ranges and qualified hand weights differ.
Do not divide SE by model MAE and call it the fraction of error caused by sampling.

The predeclared rule selects **linear**, the noisier of the two new families.
The registered repeat draws 50 boards across the same five strata and solves all
three branches (150 labels). Its panel has no incidental overlap with the old ten
boards. No seed searching, model changes or pass-criterion changes were made.

See audit.json for full direct/adjusted diagnostics, PROTOCOL.md for limits and
manifest.json for frozen inputs. The background runner writes REPORT.md after
all reference solves and validation finish. Production on port 56708 is unchanged.
