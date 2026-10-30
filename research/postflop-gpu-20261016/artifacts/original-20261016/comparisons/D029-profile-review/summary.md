# D029 independent profile review

All nine complete non-timing states exactly match the frozen original/E015 records. Raw logs, stages, fixed launch counts, 201/201/61 diagnostic iterations and preserved E015 binary/build provenance verify.

| Fixture | up_action median ms | up_show median ms | down_action median ms |
|---|---:|---:|---:|
| rainbow | 8.8736 | 6.8973 | 4.0923 |
| two-tone | 5.0736 | 4.2892 | 2.5411 |
| river | 0.7421 | 0.3903 | 0.6741 |

Both flop fixtures retain the same top-three rank in every repeat. Rainbow up_action spans8.8501–8.9257ms; two-tone5.0732–5.9419ms. River up_action varies0.2208–0.8880ms, so its fine-grained rank is unstable.

These are synchronized eager host spans with launch/wait overhead, not normal graph device-time shares. The diagnostic is one extra iteration after scoring and fingerprinting. All complete-cycle times from these profiled runs remain excluded from acceptance. No speedup is claimed.

The executed source is frozen E015 from the executable/build manifest, regardless of contemporaneous research checkout state. No builds, GPU runs or production edits were performed for this audit.
