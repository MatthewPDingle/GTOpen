# First stratified arm: complete independent readback

The first arm, `9266201-stratified`, completed all 78 planned updates and passed
its full four-worker audit. The audit ran alongside the second training arm,
used no GPU, and did not change production.

| Check | Result |
| --- | ---: |
| Completed updates | 78 |
| Reconstructed BB root decisions | 39,936 |
| Reconstructed postflop targets | 917,503 |
| BB / BTN inserted training visits | 835,988 / 147,926 |
| Maximum root-state discrepancy | 4.55e-12 |
| Maximum target discrepancy | 5.68e-14 |
| Maximum policy discrepancy | 9.63e-13 |
| Audit elapsed time | 2,473.281 seconds (41.22 minutes) |

The completion record was checked against the source-registration hash, the
audit-registration hash, the completed arm's exact checkpoint reference and
all bound Python source hashes. All numerical discrepancies are below the
registered thresholds. This was a full readback, not an extrapolation from
the two-update control.

The audit reconstructs scalar targets, policies, sample weights and complete
checkpoint state. It shares the sampler/reservoir implementation and native
evaluator and does not independently reimplement poker or certify strategy
quality. No model is promoted on this basis. The second arm, its full audit,
complete-bank controls and fresh-deal payoff comparison remain required.

## Evidence identities

- Training registration:
  `b5210fd30c9a9033de38c3fee7bddf4b735a8807230f344ff6b132c761154f4c`
- Audit registration:
  `84a342fbe42942b8c597ff32eeeed394e988ae827c2d78f581e6f2752e1e1d2a`
- Completed checkpoint:
  `2b18bcce29162988c5672e8e9f50b688f1a561595fd823dc7181ffae96ce8636`

Full results and source bindings are in
`weighted-training-readback-parallel-v1-w4-9266201-stratified-0078-result.json`
and its corresponding registration.

## Execution outlook

Overlapping this audit with the second training arm avoided adding its entire
41-minute duration to the end of training. The current registered second audit
still begins at that arm's completed endpoint. Future execution versions should
consider checkpointed, incremental auditing of immutable completed generations
so the final audit can also overlap training; this requires separate qualification
of state continuity and source binding, not skipping any checked generations.
The qualified batched restore and faster storage scan are additional candidates
for that next version. The current queues and their source identities remain
unchanged.
