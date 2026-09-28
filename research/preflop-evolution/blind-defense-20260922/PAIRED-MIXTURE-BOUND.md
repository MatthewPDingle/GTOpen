# Shared-policy mixture bound for a future comparison

Prepared and checked 2026-09-28. This is a prospective evaluation improvement,
not a changed analysis of the running river pilot. It uses no new poker deals.

## Argument

For one player, let policy component i have fixed positive weight w_i and own
realization probability q_i(h) at a decision history h. The implemented average
uses sum(w_i q_i(h) sigma_i(a|h)) / sum(w_i q_i(h)). By induction over that
player's own earlier actions, the resulting realization probability of any own
action sequence equals sum(w_i q_i(sequence)) / sum(w_i). If the denominator
is zero, that sequence has zero own reach; its fallback cannot affect payoff.

For a fixed opponent policy and physical deal, expected payoff is linear in
the player's realization probabilities. Thus this behavioral average has the
same payoff as selecting one complete component at the start using normalized
w_i, retaining that component for all of the player's actions. This needs the
actual own-history weighting; ordinary independent per-node averaging is not
an adequate substitute.

Let two such mixtures have common normalized component mass c, calculated as
the sum of the minimum old/new coefficient for each identical component. The
common contribution cancels from their paired payoff difference. Each remaining
mixture has mass 1-c, and its normalized expected payoff lies in [L,U]. Therefore
the absolute gain from replacing ONE player's mixture is at most (1-c)(U-L),
against any fixed opponent. Opponent mixtures and conditional chance averages
preserve the argument. Replacing both players at once is not this contrast.

Component identities must bind the same game, policy implementation and entire
policy. Content hashes alone are not evidence of a correct inference engine.
Identical whole-model hashes are a sufficient conservative way to identify
shared components when the inference and context are already verified. Different
models can implement the same policy, but treating them as distinct only loosens
the bound. Positive integer weights are handled as exact rational numbers by
paired_policy_mixture_bound_v1.py, with its final floating bound rounded outward.

## Relevance to the current pilot

If the registered common bank prefix 0..78 is verified, and only played model 79
differs, the changed mixture mass is 80/sum(1..80) = 2/81. Terminal payoff spans
400.5 bb in this context. The paired gain bound is consequently 89/9 = 9.8889 bb
per entry, instead of the generic 400.5 bb bound. This is a bound on the complete
paired payoff, not on every conditional decision probability or best-response
exploitability. A larger continuation needs its own actual shared-mass bound.

The running pilot retains its original registered intervals. Before adopting
this tighter bound in a future fresh evaluation, freeze the bank identities,
exact weights, common context, and qualified own-history inference. Specify how
numerical error is handled prospectively. Do not infer a universal numeric
error allowance from a few observed discrepancies or tune the bound on test
outcomes. A smaller bound reduces the conservative interval's additive term;
it does not establish a fixed end-to-end speedup or remove sampling variance.

## Control evidence and limits

paired-policy-mixture-bound-control-v1-result.json passes 128 independent fixed-
seed toy trees with five alternating decisions and zero-probability branches:

- 256 paired gains respect the cancellation bound.
- 1,210 unreachable rows exercise zero-reach fallback.
- Exhaustive component-mixture payoffs and behavioral own-reach averages agree
  to a maximum absolute error of 8.88e-16.
- Identical, duplicate-component, disjoint and unequal-weight mixtures pass;
  six invalid-weight cases are rejected.
- The structural pilot example has exactly 2/81 changed mass and bound 89/9.

The control takes about 0.23 seconds, uses no GPU and consumes no poker test
data. Its source hashes match the prospective registration. These small-tree
checks supplement the argument; they do not newly qualify native poker,
neural inference or current pilot accuracy. No production or registered pilot
source has been changed.
