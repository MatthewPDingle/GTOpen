# CPU qualification of an arbitrary-range river reference

The queued relative-feature learning experiment is unchanged. This separate
mathematical control extends the restricted uniform-opponent reference to a
fixed nonnegative vector of opponent hand weights. It prepares a later
range-conditioned test; it does not train, choose or promote a policy.

For one fully visible river board, form disjoint win/tie/loss masks for every
board-legal hero and opponent holding. Remove every pair sharing either hero
card. Multiply each outcome mask by the opponent's entry-times-history reach
vector. Sum only nonnegative terms, avoiding cancellation when most opponent
mass is blocked. Normalize separately for each hero holding. Zero compatible
mass is explicitly unsupported and has no equity/payoff, never a uniform fallback.

The reach vector must be fixed for the public state and independent of the
hero's private cards before card removal. A complete integration must establish
that factorization from actual policy/history queries; this control does not
assume it for arbitrary correlated models. It also does not solve betting or
compute equilibrium. The payoff reference is HU terminal river Fold/Call only.

Use the 12 old probe boards from the already qualified exact-rank reference.
Do not inspect the queued trial's new validation/test labels. Existing native
ranks were checked against independent five-card subset enumeration. Reuse
their immutable files and hashes rather than repeat rank generation.

Six fixed weight cases per board: all ones, deterministic lognormal weights,
zero mass, one supported holding, a sparse deterministic range, and a range
with a large weight plus tiny surviving weights. Seed9297001. Compare every
output against independent direct filtered summation, and scalar math.fsum
for selected hero rows. Uniform mass must reproduce all original integer
win/tie/loss counts exactly. Compare terminal cashflows at the first and last
eligible states of the five existing fitting depths. No new strategic fitting.

Required controls: scale invariance, hole/suit relabeling with corresponding
weight mapping, explicit unsupported rows, overlapping-card exclusion, ties,
and rejection of malformed hands, ranks, weights and public geometry. Fix
normalized mass tolerance1e-12, equity tolerance1e-12 and payoff tolerance1e-9bb.
Retain failures; do not adjust tolerances after execution.

CPU only, at most four workers and one BLAS thread per worker, 600 seconds,
16 MB retained evidence plus16 MB reserve under the800 GB allocated budget.
Admission: CPU below50%, RAM28 GB available, S free40 GB; during work CPU below75%,
RAM24 GB, S free40 GB. Production/other research has priority. Acquire the
existing research lock so the GPU admission helper cannot start concurrently.
No production change, no model changes, no performance or accuracy claim.
