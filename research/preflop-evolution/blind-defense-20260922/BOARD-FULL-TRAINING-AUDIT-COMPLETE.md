# Complete training audit passed

Both board-root candidate runs passed the complete saved-state audit on
2026-09-28. Each run contains the fixed 78 updates. The audit checked all 156
updates, 624 public boards, 79,872 physical roots and 1,674,217 postflop training
targets. It took 14,513.172 seconds (about 4 hours 2 minutes).

The first arm, `9266201-board-root`, contributed 827,394 checked targets; the
replication, `9266301-board-root`, contributed 846,823. Both final checkpoints
match the completed training result and audit registration. The source and
artifact registration contains 16,948 input bindings, which the audit verified
before and after the numerical checks.

Maximum discrepancies across both runs were:

| Check | Largest discrepancy | Audit threshold |
| --- | ---: | ---: |
| Root state | 3.638e-12 | 1e-8 |
| Exact preflop terms | 2.842e-14 | 1e-10 |
| Board calculation | 1.421e-13 | 1e-9 |
| Postflop target | 5.684e-14 | 1e-9 |
| Policy | 2.061e-12 | 1e-10 |

The audit used the qualified version-2 reader, eight physical workers and four
board workers. It performed no refit, used no GPU and made no production
changes. It shares the native engine, feature encoder, sampler and reservoir;
it verifies saved training mechanics, not playing strength or an independent
poker implementation.

## Evidence

- `board-matched-complete-readback-v1-registration.json`
  SHA-256: `c48da395a1a4ce0ff5a17006a22aac9a5358fc49d38c347610bf2faa0f41b5a7`
- `board-matched-complete-readback-v1-result.json`
  SHA-256: `c02cbe5cab18793915f902058ce734ae37414ac556e209b62e07c6f6863d9382`
- Completed training result: `board-root-matched-continuation-v1-result.json`
  SHA-256: `9de1f05ac213c408c2c79f083f5c98d86f35c4bb2f8adae94b81718c40613e2d`

After completion, a separate metadata read checked these hash links, both
checkpoint identities, the complete counts and every reported error against its
threshold in the registered audit code.

## Next stage

The existing follow-up queue advanced automatically to the complete-bank
CPU/GPU numerical control. Its wrapper was verified live as PID 76536, creation
time 1790543939.8537767 (06:48:59 Adelaide). This is a historical launch snapshot;
check the queue's current stage and process identity before taking recovery
action. No duplicate stage was launched.

The control and its readback must pass before the fixed 65,536-deal evaluation
(seed 9281101). The evaluation then requires complete readback, the all-outcomes
report, visual review and scientific interpretation. No payoff result was
opened for this audit note, and no deployment or accuracy claim follows from
the audit passing.
