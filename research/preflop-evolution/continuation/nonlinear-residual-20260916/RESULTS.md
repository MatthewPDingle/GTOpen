# Small nonlinear residual: useful mean gain, rejected by consistency gate

No fixed candidate passed both requirements. The best mean error was 6.423%
of pot versus 6.889% for the ridge control: a 6.77% improvement. However, its
worst training family was 5.044% worse, exceeding the predefined 5% allowance.
The threshold is not rounded down or relaxed. No candidate was frozen.

| Hidden units per seed | Output penalty | MAE (% pot) | Mean improvement | Worst family error ratio |
|---|---:|---:|---:|---:|
| Ridge control | — | 6.889 | — | 1.0000 |
| 8 | 0.01 | 6.572 | 4.61% | 1.1347 |
| 8 | 0.1 | 6.423 | 6.77% | 1.0504 |
| 16 | 0.01 | 6.686 | 2.96% | 1.1614 |
| 16 | 0.1 | 6.489 | 5.81% | 1.0531 |

Each network result averages two predefined seeds, so inference would use
16 or 32 hidden units total. Training ran on CPU only in binary64. The
independent NumPy/PyTorch forward comparison, pot-conservation check,
exact-zero initial correction and deterministic CPU initialization tests passed.
No inference timing or full-game strategy improvement is claimed.

The worst validation case had 30.1% of compatible hand mass with at least one
network input clipped by the predefined +/-6-standard-deviation bound. This
is a warning about distribution transfer, not a measured real-player frequency.
The ridge base is never clipped. All per-case details are retained.

This is training-family selection, not prospective evaluation. No test labels
were read. A separately specified repeat may use the upcoming N03 training
data, keeping the same candidate set and independent evaluation requirement.

See [protocol](README.md), [implementation freeze](implementation-freeze.json)
and [complete scores](training-screen.json).
