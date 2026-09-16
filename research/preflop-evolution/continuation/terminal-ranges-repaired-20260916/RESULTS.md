# N37: deeper current and average ranges differ

The corrected diagnostic completed all eight registered snapshots. Its only Rust source repair spelled `.5` as `0.5`; the failed original source and build log are retained with hashes. Two numerical tests passed. All old N31 counts and every flipped terminal reproduced exactly.

| Case | Defined / all pairs | Mean conditional range TV | Opponent-weighted TV | Diagnostic weight above 10% TV |
|---|---:|---:|---:|---:|
| eight-original | 10976/13170 | 6.171% | 0.666% | 0.154% |
| eight-candidate | 11501/13170 | 10.438% | 8.321% | 18.202% |
| hu40-original | 10/10 | 1.956% | 1.419% | 0.000% |
| hu40-balanced | 10/10 | 2.132% | 1.278% | 0.000% |
| hu40-candidate | 10/10 | 4.759% | 1.751% | 2.267% |
| hu100-original | 12/12 | 2.385% | 2.224% | 7.802% |
| hu100-balanced | 12/12 | 2.285% | 1.623% | 0.000% |
| hu100-candidate | 12/12 | 4.366% | 2.756% | 8.576% |

In the large game the learned current/average terminal-range discrepancy is 8.321% on the fixed opponent-weighted measure, versus 0.666% for ordinary Balanced. N28 found small current/average strategy differences at seventeen selected visible decisions; those checks did not cover these deep conditional ranges. This provides a more specific input-distribution hypothesis to investigate.

Empty own ranges have undefined conditional TV and are explicitly counted separately. Opponent products are independent-class diagnostic weights, not legal-card probabilities, hand frequencies, prediction error or additive attribution of the solve gap. These are single checkpoints; they do not establish cycling over time or prove the cause. No model or game was changed by this scan.
