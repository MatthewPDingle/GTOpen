# Next native bridge: complete conditional river action values

Prepared 2026-09-28 after river-conditional-estimator-synthetic-v1 passed.
This plan is not an executed or qualified native implementation. The broader
goal is useful preflop ranges through better self-play learning, not local
regression scores. This bridge supplies the missing legal action vector.

## Required native export

Create a new research example rather than modifying the registered
hu_river_conditional_queries_v1.rs. Accept an exact visible river information
set and context. Enumerate all 990 legal opponent private pairs, retain their
full actual earlier action histories, and export the complete downstream river
action tree for every pair. Include Check, Fold, Call, Raise and all-in choices
where legal, terminal values, branch offsets, and policy-query identities.

Deduplicate visible observations by canonical information key. Opponent private
cards belong in enumeration metadata, never the updating player's features.
Every query's own-history ancestors must exist with matching actor/action/arity.
Retain a postorder tree so value propagation can use children before parents.
Do not prune according to the updater's current strategy or own reach.

Each policy result must identify the exact immutable current policy and context
used for BOTH history likelihoods and continuation values. A frozen average is
allowed as a test policy; it cannot silently replace a different per-iteration
self-play policy. Branch offsets are added once and all action values share
the same utility convention before one policy-weighted regret subtraction.

## Bounded controls before learned inference or training

Use old TRAINING deals only. Freeze deterministic case identities before
scoring: include both actors, at least one Check-first and Fold/Call/Raise
target each, and a no-further-raise target. Select from the existing old query
exports by public/legal geometry, never by payoff or learned prediction.

For uniform and deterministic hand/history-dependent test policies:

1. Reconstruct terminal utilities independently from commitments, showdown
   result, fold actor, configured rake/cap and branch offset. Check ties and
   unmatched-bet refunds. Reconcile the Fold/Call contrast with the existing
   independently verified exporter on facing-bet cases.
2. Recompute all continuation action values by two independent traversal
   formulations. Verify all 990 pair identities, compatible cards, visible
   features, full histories, action order, finite probabilities and support.
3. Weight by target entry mass times the CURRENT opponent-history likelihood;
   include zero-own-reach supported branches. Verify normalized posterior,
   complete action centering, and strict rejection of mismatched context/policy.
4. Preserve malformed-request, wrong-policy and illegal-action negative controls.
   Limit the declared qualification to tested contexts and geometry; do not
   claim an integrated self-play estimator from exporter tests alone.

Preflight the public river subtree size before multiplying by 990. Use explicit
query/node/output bounds and a per-case timeout. Proposed caps are 250,000
observations, 500,000 tree nodes, 100 MB new evidence total and 60 seconds per
native request. If geometry exceeds a cap, record the limitation; do not silently
truncate actions/pairs. Register exact scripts, binary, inputs and caps before
execution. Preserve failures and version any correction after registration.

## Following steps

After native controls, profile full-vector inference against a fixed current
research policy. Use qualified shared preparation only where its input contract
matches. Compare exact conditional target variance and total cost with the
unchanged sampled traversal on a bounded, registered training-only pilot.

Then integrate visit-preserving replacement in a new native research walker,
reconcile original/candidate visits and complete returned values, and only then
register bounded self-play with fresh full-policy evaluation. The gated learned
correction remains experimental because inaccurate baselines worsened variance
in the synthetic controls. No production deployment or fresh final-set tuning.
