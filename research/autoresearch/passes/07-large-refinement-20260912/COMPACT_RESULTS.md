# Compact GPU refinement v1

Both registered large inputs completed with canonical 1024-particle GPU branch
learning and independent final conditioned audits. Neither qualifies for deployment.

| Input | Process time | Final branch gates | Global gap (bb) |
| --- | ---: | ---: | ---: |
| sampled | 230.469 s | 26 / 27 | 0.02953004 |
| native | 362.078 s | 26 / 27 | 0.00877509 |

The global target is 0.005 bb. The sampled run failed final path `[3,0,0,0,0]`;
the native run failed `[1,1,0,0,0]`. Native here names the input snapshot, not
the execution device: both runs use GPU refinement.

The completed sampled CPU experiment took 3165.984 seconds. GPU v1 is about
13.7 times faster end-to-end for that registered adaptive experiment, but
floating-point differences produce different refinement decisions; these are
not identical iteration schedules or bit-identical output policies. Both fail
the same final global qualification. This is a research timing result, not an
accepted user-facing solve speedup.

The 24,192-node three-limper subtree used about 286 MB GPU memory; its first
1000-iteration sampled-input refinement passed in 48.8898 seconds. Other selected
branches still required escalation. Independent final audits remain mandatory.

Small numerical tests passed for CPU/GPU conditional policies, Q values, EV/gap
weighting, frozen and locked policies, and unchanged parent arenas. Full default
and GPU regression suites remain pending. Follow-up: a fresh global GPU solve
seeded from the refined average policy, with fresh regret/averaging ages, followed
by the same final global and conditional gates. Preserve failures; do not loosen
targets. Port 56708 remains unchanged.

Evidence: `raw/large-eight-{sampled,native}-compact-v1-{exit,result,broad}.json`,
`raw/research-constraints-tests-v1.log`, and `raw/cv-numerical-v2.log`.
