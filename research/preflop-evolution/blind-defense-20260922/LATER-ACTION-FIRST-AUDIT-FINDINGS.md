# First later-action training history independently verified

The recovered CPU audit passed on September 25 after 7,257.422 seconds.
It reconstructed the full original 78-update training history from generation
zero. No training refit or GPU computation was performed by this audit.
The earlier interrupted audit remains preserved separately.

| Check | Result |
| --- | ---: |
| Training updates | 78 / 78 |
| BB roots reconstructed | 39,936 |
| Postflop targets reconstructed | 883,514 |
| BB / BTN reservoir insertions | 814,687 / 132,196 |
| Maximum root-state difference | 2.73e-12 |
| Maximum target difference | 5.69e-14 |
| Maximum policy difference | 1.22e-12 |

The successful review is bound to the recovery registration, unchanged
training-result alias, and independent readback registration. Those identity
bindings, all 78 completed updates, and the matching final checkpoint were
checked again after the audit exited. The final checkpoint remains
`b63320661a9485b3adf150d11cfc8ed9ca51854abd6c038dd98daadb2c126690`.

This verifies the training implementation and recorded history. It does not
establish stronger play, better preflop ranges, convergence, or agreement with
GTO Wizard. The second trial's full audit was still running when this note was
written. The registered full-bank control and fresh complete-policy comparison
remain outstanding. Production was unchanged.

Evidence prefix: `later-action-first-audit-recovery-v1`.
Independent-review SHA-256:
`6e49c766053b2acb288a7076c4f0d4e8b3ba31a811a50bfa7f6f563d6a8bd34e`.
Source-result SHA-256:
`5bd374e44a85ec65bba9f09926c7533ff3c65eadbc969ae305c708b0a82f2f66`.
