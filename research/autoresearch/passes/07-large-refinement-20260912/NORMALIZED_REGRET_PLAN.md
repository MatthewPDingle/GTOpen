# Global GPU learning with normalized regret increments

Independent branch, ancestor, and root repair have failed the joint accuracy
gates. The root-only experiment confirms that better root responses expose
large errors in later responses. Test a learning-rate change during the full
global solve so rare decisions can adapt before a separate repair is needed.

The research kernel divides each learning-node regret increment by the product
of the other seats' reach masses at that decision, floored at 1e-12. It leaves
the counterfactual values propagated upward, payoff model, strategy-sum
weights, fixed policies, and discount schedule unchanged. It does not invent
positive reach in an unreachable branch. This is a changed optimizer with no
claimed CFR convergence guarantee; success requires the original final gates.

Before execution:

1. Verify a single GPU sweep against independently scaled native increments,
   unchanged upward values/strategy sums, fixed constraints, and zero reach.
   Verify eager/captured learning equality and native CPU/GPU final evaluation.
2. On the existing six-player fixture, run gamma15/64 with seeds 42 and 314159,
   normalization off/on, limit 1,000, full checks every 25 iterations, and the
   same 0.005-bb target twice. Each process has a 600-second cap. Continue to
   large only if both candidates meet the global target and their total times
   are at most twice their same-seed fresh control's total time.
3. If that screen passes, run the canonical eight-player user-session fixture
   from scratch, gamma15/64 seed 42, limit 1,500, full checks every 50, target
   unchanged, cap 1,200 seconds. Save/reload and audit all 27 registered paths.
   No local failure is overridden by global convergence.
4. Any promising large result still needs a current control and additional
   seed/constraint qualification before adoption. This is not deployment.

All timed learning is GPU. CPU is only an independent correctness reference.
No workload overlaps another, and live work on 56708 stops owned research.
