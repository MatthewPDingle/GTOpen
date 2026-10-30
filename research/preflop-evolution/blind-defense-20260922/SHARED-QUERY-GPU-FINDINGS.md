# Shared-query GPU evaluation control

The candidate passed exact output comparison and a separate CPU semantic readback. On the two reused 32-deal batches, run in original/shared/shared/original order, sharing the common query preparation across four policy banks reduced full-batch time from **22.999s to 20.094s**, a **1.145x speedup / 12.63% time reduction**.

Timing includes query generation, common preparation, GPU prediction and ordered averaging, native evaluation, serialization, gzip publication and verified scratch release. It excludes initial bank loading and the separate reader. There are 64 distinct previously inspected deals and eight batch replays; this is a small implementation control, not a full-study performance guarantee or new poker-quality evidence.

All policy probabilities, own-action reaches, transported policies and native payoffs were byte-identical to the authenticated original control. The separate CPU child checked all eight archives and 116,248 policy observations. It passed in 114.81s. Complete control time, including loading, identity checks and review, was 620.28s. Source hashing and loading remain substantial costs, so do not apply the measured batch ratio to that total.

The candidate is qualified for use in a separately registered research runner with the same semantics and guards. No production solver, trained model or live strategy was updated. The stopped production service was restarted using the previously deployed binary, with its original SHA-256 verified, so the activity checks could protect user solves; there was no rebuild or experimental deployment.

Admission retained the 800GB combined research ceiling, 2GB reserve, 100MB output cap, 30-minute deadline and activity/resource checks. The prior offline launch refused before registration; this completed attempt began only after the existing server reported empty/idle sessions and no running reports.

The next range-quality diagnostic can reuse archived policy transport without neural inference at all. Keep the shared-query improvement for later experiments that actually require inference; avoid paying the loading cost unnecessarily.

Evidence:

- `shared-query-gpu-control-v1-registration.json`
- `shared-query-gpu-control-v1-result.json`
- `shared-query-gpu-control-v1-independent-review.json`
- `shared-query-gpu-control-v1-status.json`

The fixed-batch speed result is separate from the inconclusive later-action training study. Faster evaluation does not make its learned ranges more accurate.
