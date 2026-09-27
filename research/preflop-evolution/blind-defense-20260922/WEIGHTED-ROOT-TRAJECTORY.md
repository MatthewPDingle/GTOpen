# Complete-history range stability analysis

The fixed stratified study requires coverage and movement checks as well as
the fresh-deal payoff comparison. `weighted_root_trajectory_v1.py` supplies
the coverage and movement checks after both 78-update arms and the complete
bank control have passed their independent reviews.

Run with Python 3.12 from the repository root:

```text
python tools/research/weighted_root_trajectory_v1.py
```

This is a separate CPU-only diagnostic, not an additional stage in the already
registered evaluation queue. It can run alongside the GPU evaluation once its
prerequisites exist. It uses two worker processes, checks available resources,
and does not change production or acquire the GPU. Do not run it on unfinished
training banks or substitute mutable progress files for completed results.

For both new arms it checks all 169 root classes across all 78 updates:

- Actual class visits and importance mass, kept distinct.
- At least three deals for every class in every update.
- Policy movement between successive updates, weighted by the original entry
  distribution; aggregate action frequencies and per-class final averages.
- Movement between the first, middle and final 26-update windows.
- The difference between the last current policy and the complete played
  average. Generation 78 is unplayed and appears only in this diagnostic.

The reported played strategy uses generations 0-77 with weights 1-78. At this
root there is no own-action ancestry, so the scalar weighted average must
match the separately checked complete bank. The implementation also compares
every reconstructed policy with the typed CPU policy reader. Existing baseline
diagnostics are reused only after binding their registered inputs, model
references and root probabilities to the new comparison's identical baselines.

The helper control passed three known-answer trajectories, five rejection
cases and readback of 507 policies from the completed pre-study pilot. Maximum
scalar policy discrepancy was 2.22e-16. This qualifies the helper, not the
unfinished study: full-bank analysis remains pending.

The output is descriptive. Reduced policy movement or better coverage alone
does not prove stronger poker play. No intermediate checkpoint is selected,
no new training or evaluation deals are drawn, and this does not establish
accuracy beyond the restricted BB-versus-BTN study.

## Resource snapshot during preparation

A 15-sample read-only measurement found system CPU use averaging 12.6%, GPU
use averaging 40.9% (7-93%), maximum observed VRAM use 2493 MiB, and about
113 GB available system RAM. These short samples are not a full-run profile.
The trainer remained live and reached generation 69 while the helper was
prepared and tested. The queued four-worker audits can overlap the next
training arm; the eight-worker final scalar review follows GPU evaluation.
Worker counts in the current registered experiments remain unchanged.
