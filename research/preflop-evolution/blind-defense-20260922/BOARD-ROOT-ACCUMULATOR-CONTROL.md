# Board-root state: mechanical control passed

This is an isolated research component, not a trainer or production model.
It implements the expected weighted root increment from the complete mean of
registered board contributions plus separate exact terms. No physical visits
are invented; the state records completed board draws and generation evidence.

Three synthetic cases use physical-budget scales 1, 512 and 4,096 and board
counts 1, 4 and 16, each continued for three generations. Independent scalar
arithmetic reconstructed every increment and accumulated regret, with maximum
discrepancy 4.547e-13. All 108 malformed-target attempts left the state and next
board plan unchanged. Fifteen corrupted checkpoint attempts were rejected.
The existing weighted-state reader rejected the new type in all nine checks.
Six subsequent updates after JSON recovery matched uninterrupted execution
exactly, including the next board plan and resulting root probabilities.

Chance uses explicit PCG64 seeded by the registered seed and generation.
Preparing a plan does not consume mutable randomness; publishing a complete
generation advances its counter. The component has no access to the separate
physical sampler. Repeated sampled boards are legal outcomes, while repeated
draw indices, missing draws and stale parent-state identities are rejected.

Evidence identities are integrity bindings, not independent proof that a
native worker used the right model. Native-output admission/readback, a full
training transaction and checkpoint, a distinct model reader, both network
fits and the exact BTN update remain necessary. This control does not claim
any of those integrations or qualify training, accuracy or performance.

Files: board_root_accumulator_v1.py, board_root_accumulator_control_v1.py and
board-root-accumulator-control-v1-{registration,result}.json. Runtime: 0.625 s,
CPU only. Registered sources remain unchanged for future reproducibility.
