# Resume after the authorized reboot

The user requested a pause and then explicitly requested resumption on 23 September. The original trial completed 48 of its fixed 78 updates before the deliberate stop. This continuation completes the remaining 30 updates; it does not choose a new checkpoint, change the candidate, or enlarge the training budget.

The original store, stopped statuses, partial iteration 49, registrations and source files remain unchanged. A separate `sampled-visible-hybrid-resume-pilot-v1` store imports only the complete prefix and its referenced immutable objects. Those files are hard links, checked against the prefix audit and never written by the continuation. Mutable progress pointers and all new iterations belong to the new store.

The restored checkpoint includes both reservoirs, sampler state, action random state, the complete played model bank, the next model and its preflop tables. The original iteration loop is structurally identical after normalizing the starting iteration and preserving the original batch identifiers. Training environment versions must match. Before training, the next 512 deals and eight action seeds must reproduce the preserved partial iteration, and restored CUDA inference must reproduce its first saved batch.

The original three-hour execution allowance is reduced by the 5,981.375 seconds already consumed. Reboot downtime and offline correctness checks do not count as training. Production activity, insufficient resources, a deadline or an integrity failure still stop the run. There is no automatic retry.

After a full replay audit, evaluation retains the original seeds 99101/99102, 8,192 response-training deals, 16,384 held-out deals, complete played generations 0–77, the CPU/CUDA equivalence check, and the predeclared BB and BTN comparison families. Only artifact names and continuation provenance change. This remains one fixed candidate evaluation, not an additional model selection attempt.

The post-reboot app has no preflop session. The new activity probe accepts that state only when status reports empty state and zero iterations and the session endpoint independently returns HTTP 400 with the exact absence message. Running solves, reports, unknown states and connection failures continue to block research. The existing production binary was restarted; no experimental model was deployed.

Strategic conclusions require completed evaluations and both independent reviews. Finishing training or reproducing a checkpoint does not establish accurate ranges, equilibrium, cross-stack generalization or GTO Wizard equivalence.
