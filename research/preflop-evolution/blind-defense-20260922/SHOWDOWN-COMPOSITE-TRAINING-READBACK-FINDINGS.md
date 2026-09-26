# Completed independent readback of the recovered fourth arm

The independent composite reader passed all 78 updates of `9266301-corrected`.
It reconstructed 39,936 BB root states and 872,066 postflop targets in 4,319.922
seconds without GPU use. Maximum errors were 4.093e-12 for root state,
5.685e-14 for targets, and 1.770e-12 for policy probabilities.

The reader joined original updates 1–48 with continuation updates 49–78 and
checked policy, chance/action streams, targets, root/exact state, and checkpointed
reservoir reconstruction. It did not independently refit the neural models or
reimplement the native poker evaluator. No poker-strength or accuracy conclusion
follows from this readback.

Authoritative result:
`showdown-training-readback-composite-v1-9266301-corrected-0078-result.json`
has SHA-256 `8cf9a046e0adaf95441d9a1c58528b71ad55c4b59fb947a9cf046f8ebb70ce9f`.
Its readback registration is
`7551cd75ea21aaeb6c1576d1f0a5d43db83ec726782a21c72aca852ad3c857b8`;
the continuation result remains
`f49fe9c8ea418340fb71f86f00ef691fb7897c2821da05cd2728498e903689e2`.
The original four-arm controller's storage failure remains preserved.

The v2 audit handoff exited successfully. The separately registered next-stage
supervisor has launched the complete-bank implementation control on 64 reused
deals. That control and its independent review must pass before fresh evaluation
is admitted. All four arms now have completed training and full independent
training readbacks; full-bank GPU equivalence, fresh-payoff results, and their
independent review remain outstanding. Production was not changed.
