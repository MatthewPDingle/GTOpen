# Native full-action river bridge controls

Prepared 2026-09-28 before the new native exporter is first executed. This is
implementation qualification, not training or a fresh strategic comparison.
The broader BOARD-RIVER-FULL-ACTION-BRIDGE-PLAN.md remains the governing plan.

## Frozen inputs and case selection

Use eight existing TRAINING positions selected by legal geometry, not values:
both actors facing an ordinary bet with a raise, both with no further raise,
both with a free check, and both facing an all-in. Source identities are frozen
in river_full_action_control_v1.py and recorded with exact requests before any
native execution. Facing-bet cases come from the original target-learning
selection; free-check cases use its deal-000 query archive. The two all-in
cases extend the initial six-case design to exercise stack limits explicitly.
No held-out final data is used or opened.

Run one additional zero-rake version of the first case to exercise both zero
and the context's configured capped rake. This is a declared context variant,
not a change to archived observations or production settings.

## Identity and resource contract

Record SHA256 hashes of native sources, built executable, local imported Python
modules, context, old selections, query file and selected old archives/manifests
before the first export. Verify old ZIP member bytes and hashes before use and
recheck all source/input hashes at the end. Use fresh output names, retain
failures and version any subsequent corrections.

CPU-only, one native request at a time, 60 seconds per request, 600 seconds
overall, at least 24 GiB free RAM, at least 2 GB free destination disk. Native
limits: 250,000 queries, 500,000 nodes and 64 MB per output. Reserve the full
native output allowance before each request and cap all new evidence at
100 MB. No GPU allocation, historical archive deletion or production mutation.
The existing research ownership lock prevents overlapping research jobs.

## Predeclared checks

- Every one of the 990 compatible opponent pairs, exact visible keys, active
  features, actual own histories, public tree identity and postorder links.
- Legal actions, incremental commitments, stack-limit/all-in flags, terminal
  folds and unmatched-bet refunds, losses, wins, ties, rake/cap and one offset.
- Outcomes agree with the existing independently checked exporter. Its
  Call-minus-Fold values are reconciled here using the
  original posterior helper with the same policy probabilities for every key.
- Uniform and deterministic positive visible-key policies, shared between
  history likelihoods and all future branches; no private-card policy input.
- Full action values agree between postorder propagation and independent
  terminal-path sums. Opponent history conditions entry weights; own history
  does not. Regrets share one policy-weighted value baseline.
- Making an actual earlier own action impossible preserves the supported
  target and its full action vector. Empty opponent support is reported
  explicitly, without normalized values.
- Reject wrong context, current-policy identity, query hash, changed
  probability bytes, illegal-action mass and unnormalized probabilities.
  Native requests reject unknown fields, invalid cards and terminal histories.

Tolerance: 1e-9 bb for values/terminal accounting, 1e-12 for probabilities and
posterior differences. All positive controls and every deliberate rejection
must pass; failures remain failures. These checks cannot establish native
self-play estimator correctness or poker range accuracy. A current-policy
inference/cost pilot and visit-preserving walker integration still follow.
