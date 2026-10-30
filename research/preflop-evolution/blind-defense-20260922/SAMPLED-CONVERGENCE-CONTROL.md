# Finite-game convergence control passed

Both full traversal and external sampling reached the registered independent
deviation target in the existing finite imperfect-information control. All ten
runs stopped after two consecutive successful checks, before the 16,000-update
maximum. This verifies a self-updating learning loop, beyond the earlier
fixed-policy update identities. It does **not** establish convergence or useful
speed on the full BB poker study.

## Controlled game and measurement

This is the same nonphysical four-card game used by the exact rational oracle:
24 distinct private/public deals, 19 public nodes, 60 information sets and 128
action entries. Opponent cards are hidden throughout; the public card is hidden
at preflop decisions. It includes early folds, calling, raising, later decisions,
dead money and a very rare private hand. Its payoff ranking is synthetic; it
must not be described as a miniature physical hold'em solve.

Two payoff settings were registered: constant-sum without rake and
action-dependent rake. The latter is an empirical control, not a general
convergence theorem for raked games. The full reference enumerates every deal
and action. Four sampled seeds (17, 31, 47, 71) each use batches of 512 player
traversals, split equally between players. All runs use ordinary signed-regret
matching, simultaneous frozen-policy updates, and properly accumulated average
strategies. Regrets are not clipped, and a latest-iteration policy is not passed
off as the average strategy.

At the registered checkpoints, the evaluator calculates the exact finite
chance sum and both best responses. It groups hidden states belonging to the
same information set **before choosing a maximizing action**. The stop target
is summed best-response gain <=0.01 in this control's payoff units, achieved at
two successive checkpoints. This is not 0.01 bb in the real poker study, nor an
estimate from sampled terminal payoffs. Checkpoint spacing can delay a stop.

## Results

| Payoffs | Method / seed | Stop update | Final exact gap | Run seconds |
|---|---|---:|---:|---:|
| No rake | Full traversal | 4,000 | 0.003399 | 0.156 |
| No rake | Sampled 17 | 4,000 | 0.003357 | 1.328 |
| No rake | Sampled 31 | 2,000 | 0.005628 | 0.659 |
| No rake | Sampled 47 | 4,000 | 0.003687 | 1.309 |
| No rake | Sampled 71 | 4,000 | 0.004442 | 1.298 |
| Rake | Full traversal | 4,000 | 0.003640 | 0.158 |
| Rake | Sampled 17 | 4,000 | 0.004032 | 1.289 |
| Rake | Sampled 31 | 4,000 | 0.003462 | 1.278 |
| Rake | Sampled 47 | 4,000 | 0.004451 | 1.290 |
| Rake | Sampled 71 | 4,000 | 0.004704 | 1.290 |

Uniform initial strategy gaps were 2.633197 (no rake) and 2.534313 (rake).
Most runs first crossed the target at update 2,000 and confirmed it at 4,000;
sampled seed 31 without rake first crossed at 1,000 and confirmed at 2,000.

Full traversal was faster on this small problem, where it only needs 24 deals
per update. The sampled batch intentionally contains more draws than that.
These single-run timings include the update loop and checkpoint evaluation,
exclude initial compilation, and are not a hardware benchmark or evidence of
a speedup on a large tree. Sampled update counts are not equivalent to full
traversal work. The useful result is the correctly evaluated decline in gap
across fixed seeds, not a claimed sampling speed advantage.

## Independent checks

- A separate Python evaluator recomputed every checkpoint's policy values,
  legal best responses and summed gap. Maximum difference was 8.89e-16.
- That evaluator reconstructs each selected best-response policy and evaluates
  it forward to verify the reported best-response payoff.
- An intentionally clairvoyant maximization gives a substantially larger gap
  for the uniform strategy (4.086407 / 3.989046). This negative control catches
  choosing different actions for indistinguishable hidden states.
- The full reference's first ten updates and every sampled seed's first update
  were independently replayed, including deal/action randomness, signed regret,
  average accumulation and next policy. Maximum state difference was 7.11e-15.
- Normalization, stopping streaks, registered maximums and frozen source hashes
  were verified. No run was extended or retuned after seeing its result.

The aggregate criterion does not ensure a very rare information set has an
accurate individual strategy. Nor does this control address large-state reuse,
which the [fresh-deal growth test](SAMPLED-GROWTH-RESULT.md) showed to be poor.

## Next use

Keep this exact evaluator as an acceptance test for the bounded approximation
candidate. A learned representation must produce policies whose independently
evaluated gap improves; low supervised training loss alone is insufficient.
Then qualify it on actual poker before making any new claim about BB defenses,
UTG calling hands or similarity to Wizard. The full target remains unchanged.

Artifacts use prefix `sampled-convergence-v1`. Registration SHA256:
`d24cb9b472dd01e2b88dd944044cc71d38a7d16010a1cd3644ca19475bbf94a3`.
Result SHA256:
`c9653a2a02227a3e08130f7803b1c5276cd0194044d454735854bc0894524330`.
All eleven registered inputs matched afterward. The guarded job exited normally
in 12.344 seconds. No production solver, session, player model or preview range
was modified.
