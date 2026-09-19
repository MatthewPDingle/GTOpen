# AA: connected continuation sensitivity

This checks the call and called-4-bet continuations together. The postflop estimates use each branch's own prepared ranges. The saved opponent response frequencies, other preflop branches, and all-in values remain fixed. This is an exploratory sensitivity analysis, not a new solved strategy.

| Menu | Estimate | Call EV | 4-bet EV | Jam EV | 4-bet minus call [paired 95% interval] |
|---|---|---:|---:|---:|---:|
| half | direct | 53.50 | 42.94 | 40.10 | -10.56 [-16.46, -4.80] |
| half | equity_control | 53.86 | 43.56 | 40.10 | -10.30 [-16.15, -4.62] |
| large | direct | 55.78 | 43.09 | 40.10 | -12.69 [-19.35, -6.13] |
| large | equity_control | 56.14 | 43.71 | 40.10 | -12.43 [-18.94, -5.97] |

Values are bb relative to folding at the original decision. Calling subtracts the additional 12bb from its postflop continuation. The 4-bet replaces only the fast called-branch price difference, weighted by LJ's saved call probability. Bootstrap draws are shared across both branches and menus; overlapping marginal intervals are not used to judge their difference.

The direct estimate is primary. Equity control uses a sampled cache and its intervals omit cache uncertainty. Both omit model uncertainty. A switch in the preferred action under frozen ranges would change those ranges and the opponent's behavior in a re-solve. Thus a favorable number here is not proof of improved full-game play or agreement with Wizard.
