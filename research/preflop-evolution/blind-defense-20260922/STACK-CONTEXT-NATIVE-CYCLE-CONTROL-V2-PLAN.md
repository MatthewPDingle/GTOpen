# Native cycle implementation recovery after the V1 logging failure

V1 is terminal, failed and preserved. It finished all14cached CPU/CUDA/reference
checks and saved its initial checkpoint, but stopped with FileExistsError while
writing the next progress message. The native cycle had not been invoked, and
no cycle directory exists. Its one-time saved-array readback independently passed
all14cases with maximum discrepancy2.221e-16. No fitting or target collection ran.

V2 changes progress publication to the helper's explicit replace=True mode and
reuses the independently reviewed parity arrays. The old registration, failure,
parity proof and arrays are pinned inputs. It does not retry the V1 invocation,
overwrite its evidence or repeat its completed GPU checks. The V1 driver and all
previously executed source files remain unchanged.

The actual native cycle protocol, seeds, context set, objective, 16-step fits,
posterior64 targets, numeric tolerances, workers, 40-minute/4GB/2GB bounds and
quality limitations are exactly those in STACK-CONTEXT-NATIVE-CYCLE-CONTROL-PLAN.md.
V2 uses its own case/output identity. This is an implementation control, not a
repeat or revision of any scientific learning comparison. Preserve a terminal
V2 failure; no automatic retry. Production56708, scientific gates and prior
rejected learning evidence remain unchanged. No push or deployment.
