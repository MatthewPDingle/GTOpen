# Configured rake in the card-compatible heads-up research path

19 September 2026. Frozen before execution. Production 56708 stays unchanged.

Extend the existing research-only interface with a separate, explicitly two-player
entry point. Learned pricing stays disabled. Supply each terminal's configured
net pot, using the existing rake cap and no-flop-no-drop accounting. Keep the old
zero-rake interface and its kernel ABI unchanged. Reject larger games and antes.
No experimental saves: ordinary CPU queries and save metadata still describe the
independent-class model.

Run six fresh fixtures at 1,000 and 10,000 iterations:

1. Push/fold, stack 10, posts 1/2, zero rake (old-interface regression).
2. Push/fold, stack 10, posts 1/2, 4% rake capped at 6.
3. Push/fold, stack 200, posts 1/2, 4% rake capped at 6.
4. Push/fold, stack 50, posts 1/2, 5% uncapped rake, including folded pots.
5. Full HU preflop tree, stack 40, posts 0.5/1, limps, open to 2.5,
   re-raises x3, maximum three raises, all-ins; 4% rake capped at 6.
6. Same full tree, with folded pots raked too (uncalled chips excluded).

The default is no-flop-no-drop except where explicitly stated. Export every
action policy and terminal's pot, investments, kind and realization weights.
An independent Python evaluator builds the exact compatible 169-class chance
matrix by enumerating physical hand pairs. Reconstruct fold/showdown chip values,
fixed Balanced continuation shares, complete-tree average values, and both best
responses. Include expected rake in the conservation check. No learned model is
being validated; non-all-in leaves still use the existing approximation.

Accounting gates: GPU root EV and summed best-response gap agree with independent
reconstruction within 0.0001 configured chip; independent net EVs plus expected
rake sum to zero within 0.00001 chip. Every policy must be finite and normalized.
Also independently reproduce every hand/action counterfactual value at every
decision node within 0.0001 chip, including rare and unreachable branches.
Reading those values must leave stored regrets and average strategies unchanged.
Report the independently measured gap after 10,000 iterations; a <=0.001-chip
gap would support an approximate equilibrium of this fixed-payoff class game.
Because rake makes utility non-constant-sum, do not use the zero-rake minimax LP
certificate or assume CFR convergence. Preserve failures and do not tune gates.

Verify the original interface still rejects nonzero rake; the new hook rejects
three-player games; and the zero-rake 10bb policies match the previous run.
Check ordinary GPU behavior with research disabled and relevant regression tests.
This is an accounting/integration experiment, not a production candidate or a
claim to match Wizard. CPU queries, save semantics and multiway chance remain
separate deployment gaps.
