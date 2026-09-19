# Existing research interface passes independent equilibrium check

The earlier legal-pair interface passes the new independent LP certificate on all four heads-up push/fold fixtures. No application changes were needed. Learned continuation pricing was disabled.

| Stack | Iterations | Independently measured gap | GPU value reconstruction error | GPU gap reconstruction error |
|---|---:|---:|---:|---:|
| 3 | 1000 | 0.00000000 | 0.00000012 | 0.00000000 |
| 3 | 10000 | 0.00000000 | 0.00000012 | 0.00000000 |
| 10 | 1000 | 0.00000043 | 0.00000023 | 0.00000000 |
| 10 | 10000 | 0.00000003 | 0.00000011 | 0.00000000 |
| 50 | 1000 | 0.00000004 | 0.00000024 | 0.00000000 |
| 50 | 10000 | 0.00000000 | 0.00000020 | 0.00000000 |
| 200 | 1000 | 0.00001867 | 0.00000003 | 0.00000001 |
| 200 | 10000 | 0.00000007 | 0.00000001 | 0.00000000 |

Every 10,000-iteration result passes the preregistered 0.001-chip gap gate. Native GPU values and gaps agree with independent reconstruction within 0.0001 chip. Total net utility is conserved within that tolerance.

This validates the existing GPU down/up traversal with card-compatible fold and showdown values in this restricted two-player game. It is stronger than simply verifying a fixed terminal equity calculation. It does not validate earlier multiplayer actions, the heads-up chance reset inside a larger tree, nonzero rake, learned continuation values, or general full-game convergence.

The ordinary CPU query functions still use independent-class chance. Their outputs are deliberately marked as belonging to a different model. Experimental saves would also retain ordinary metadata; none were written. These are concrete integration gaps that must be resolved before deployment.

[Protocol](INTERFACE-PROTOCOL.md) · [Input hashes](interface-freeze.json) · [GPU output](interface-policies.json) · [Independent review](interface-review.json)
