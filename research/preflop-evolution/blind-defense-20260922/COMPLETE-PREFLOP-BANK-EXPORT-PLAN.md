# Frozen complete-bank preflop export

This bounded control extracts the existing A/B baseline/river policies. It does
not train, draw new poker deals, reinterpret the historical test, or change the app.

Bind the completed continuation, independent readback and four bank identities.
For each bank, read and validate all 110 played models, generations 0..109, from
the original checkpoint. Exclude unplayed generation 110. Keep the original
265-row model catalog metadata and original inference code. Use the separately
qualified 699-query complete preflop catalog across all five decisions, including
each decision's own-action history. Retained reservoir restoration is unnecessary
for this read-only inference operation; the completed study already checked it.

Use weights 1..110 for both players. Compare original scalar-model CPU inference
with the original four-model-chunk CUDA bank on every supported query. Acceptance
uses the completed study's thresholds: absolute policy error below 1e-10 and
own-reach error below 1e-8, finite normalized legal policies, nonnegative reach.
Persist both CPU/CUDA policies and own reach. These observed differences are not
a universal numerical error bound. No new payoff estimator is qualified here.

Run up to four CPU reference jobs, each with single-thread numerical libraries,
overlapping the single GPU coordinator. Shared inputs are read-only. Reference
jobs check cancellation/deadline between models; only the coordinator uses CUDA
and probes external resources. On failure preserve partial artifacts and stop.

Admission retains the existing safeguards: exclusive research lock, no active
production solve, light desktop sharing below 65% idle GPU use, a combined 4GB
CUDA cap with 2GB external headroom, at least 28GB free RAM at admission (24GB
during work), and at least 40GB free on S. One fresh global allocated-storage
inventory must fit the 800GB cap plus this control's 16MB output budget and 16MB
reserve. No second whole-store inventory is required: research is exclusively
locked and the final new directory is measured against its reservation. Deadline
30 minutes including admission inventory. No automatic retry of a started run.

If this passes, independently verify native preflop reach/terminal decomposition
and cheaply calculate the proposed reach-weighted evaluation envelope before
committing to a new expensive poker evaluation. If the precision opportunity is
weak, record that and return to broader stack/context research.
