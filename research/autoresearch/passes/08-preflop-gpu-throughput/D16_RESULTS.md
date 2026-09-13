# D16: conservative support-only screen is insufficient

The independent six-tile capacity enumeration and per-seat accounting pass.
The guarded host run finished in 1.047 seconds without changing solver state.

| Fixture | Guaranteed empty tiles | Optimistic empty tiles |
|---|---:|---:|
| Small learning | 13.41% | 80.08% |
| Large learning | 8.97% | 78.88% |

The >=20% guaranteed-fraction gate fails. No GPU prototype is admitted by D16.
This is an inconclusive interval for the mechanism, not evidence that its
actual empty fraction is 8.97%. A separate D17 measurement will extract actual
support masks and intersect them with all fixed sampled tile permutations.
It does not change this gate, extend this run, or claim a speed improvement.
Loads, voting, carries, stores and all check work remain even if tiles are empty.

Evidence: `raw/d16-learning-bound.json`, guarded exit/log and
`raw/d16-verified.json`; independently reproduced by `check_d16.py`.
