# Rank-event controls: partial variance reduction, below the fixed gate

The exact rank-event expectations passed independent physical enumeration:
17,296 possible flops for each of four concrete private-card fixtures. The
conditional range-moment reduction test passed as well.

The proposed controls reduced historical subset dispersion, but failed the
predefined requirement of at least 20% reduction in every training family.
No existing reference label, fitting target or candidate was changed.

| Withheld source family | Reduction at 20 boards | Reduction at 50 boards |
|---|---:|---:|
| Eight-player equal blinds | 6.8% | 6.0% |
| Eight-player straddled | 17.9% | 17.5% |
| Seven-player open | 13.7% | 12.3% |
| Six-player modeled | 21.4% | 20.9% |

This compares each subset to the corresponding estimator on its containing
100-board sample. It is not an accuracy comparison against exact all-flop
values. Other training families share historical board identities; slopes
and the historical board population are not independent.

The largest full-100-board label shift was 1.536% of pot in weighted hand MAE.
The largest adjusted two-player pot-sum discrepancy was 2.287% of pot. Exact
feature expectations do not make a finite-sample ratio estimator conserve the
pot, and the separately fitted player corrections can add sampling error to
that identity. The diagnostic deliberately did not hide it with recentering.
This is another reason to require fresh reference validation before adopting
such adjusted labels.

The ordinary [sampling diagnostic](../night-shift-20260916/label-precision.md)
still indicates that 20-board labels can be noisy. The simple rank controls
tested here do not remove enough of that variation to replace more reference
coverage. N03 continues on its original protocol.

See [fixed protocol](README.md), [implementation freeze](implementation-freeze.json)
and [complete results and fitted slopes](diagnostic.json).
