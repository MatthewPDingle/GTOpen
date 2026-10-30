# Evaluation routing after the storage stop

This amendment is prepared before drawing the sealed heldout seed. It changes
input identities, storage location, and scheduling only. It does not choose a
checkpoint by results or introduce another candidate-selection opportunity.

| Policy bank | Original identity | Evaluation identity |
| --- | --- | --- |
| First old | action-integrated-fresh-pilot-v1 | unchanged |
| First new | later-action-matched-first-v1 | later-action-first-audit-recovery-v1 |
| Replication old | action-integrated-replication-v1 | unchanged |
| Replication new | later-action-matched-replication-v1 | later-action-replication-volume-continuation-v1 |

The first new identity is a metadata alias for the unchanged completed training
files, with a separately recorded independent audit after its earlier audit was
interrupted. The replication new identity combines the original 52-update
prefix on T: and unchanged remaining updates on S:. Both must have complete
78-update independent audits before evaluation. In both cases, use played
generations 0 through 77, linearly weighted by generation plus one; exclude the
unplayed generation 78.

The new output prefixes are `later-action-recovered-evaluation-control-v1` and
`later-action-recovered-evaluation-study-v1`, stored on S:. Refuse to launch if
the originally named heldout study has already been registered. The control
still uses the same 64 previously inspected deals and compares all four complete
CPU/CUDA banks, including their root rows. Its independent reader must pass.

The study still uses seed **382921**, **65,536** new physical deals, **32** deals
per batch, all **eight** crossed complete-policy profiles, and all **eight**
paired contrasts. Keep the single final look, simultaneous two-sided 95%
bounded empirical-Bernstein intervals with the same multiplicity correction,
and the separate two-seed root-stability diagnostic. Do not claim Nash accuracy
or general range quality from this fixed-profile comparison.

Fresh admission accounts for all generated research roots under the 800 GB
budget. The small control reserves a further 8 GB for evaluation and 2 GB for
metadata. The study uses the original control-based storage projection rule.
S: retains its 40 GB free-volume floor; T: receives small metadata only and has
a 1 GB floor. Original trial limits and original failed records remain intact.

The recovered supervisor observes the existing training and first-audit
processes without owning or terminating them. After training completes, it
starts the replication's full audit while the first audit may still run. Both
full audits gate control, control readback, heldout study, and study readback.
Owned child failures stop the sequence without retries or automatic deployment.

Preparation checks passed: the evaluation worker's syntax tree is identical to
the original; its launch body differs only in the declared storage volume. The
independent readback calculations are identical, with only the output-prefix
literal changed. Six existing semantic corruption checks were rerun against
the recovered reader and passed, alongside those two source-equivalence checks
(eight tests, 1.672 seconds). The full-bank 64-deal control remains a separate
mandatory runtime gate after both training audits finish.
