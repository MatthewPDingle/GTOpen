# Heads-up rake accounting and position sizes

New UI scenarios use **Balanced (approx.)**. Existing saves keep the model that generated their regrets and strategy sums. To change an old game, select Balanced, **Build Game**, and solve afresh. Re-solve alone does not change its model.

## What changed

Legacy calibration multiplied each player's equity by a separately fitted realization factor. Those factors came from raked postflop values. Even at zero configured rake, the two players' continuation values could add up to less than the pot.

Balanced instead uses those hand-class factors as relative weights. For an OOP class `h` and IP class `j`, with pairwise equity `e`:

```
a = e * class_weight[h] * 0.92
b = (1 - e) * class_weight[j] * 1.08
OOP share = a / (a + b)
IP share = 1 - OOP share
```

As the remaining stack approaches zero, these relative shares blend back toward raw equity using the existing SPR positional attenuation. All-in pots use raw equity. Equity sampling noise is symmetrized, including 50/50 equity for identical classes, so it cannot manufacture or remove chips. Range averages are taken over the same pairwise shares on CPU and GPU.

Each player's gross value is their share of `pot - configured rake`; net EV subtracts their invested chips. A common scale in the old weights cancels. Rake is charged once on the starting continuation pot: `pot * rake_pct / 100`, capped when `rake_cap > 0`. A zero rate means zero rake; a zero cap with a positive rate means uncapped rake. The existing no-flop-no-drop rule still controls fold-win pots.

## What this does not establish

The fit has **not** been retrained on rake-free solves. Hand-dependent distortions in its relative weights can remain. The model does not simulate future postflop bets, their rake, or full multiway postflop strategy. Pots with three or more live players still use the selected multiway approximation. Conserving the pot fixes the accounting defect; it does not establish agreement with GTO Wizard or real-game accuracy.

If the fit is unavailable, Balanced falls back to raw equity and reports that limitation. Old calibrated saves keep their legacy fallback and payoff semantics. New Balanced saves use format v4 so older binaries cannot silently continue them under another model.

## Sizes by position

The global menus are opening raise-to sizes in bb, 3-bet multipliers, and 4-bet+ multipliers. Expand **Sizes by position** to override each menu for a seat. Multiple comma-separated values offer multiple legal actions; blank cells inherit the corresponding default. Squeezes use the 3-bet menu. Re-raise multipliers apply to the previous total raise-to amount, not the extra chips added.

For example, against a 6bb open, a default 3-bet multiplier of 3 offers 18bb. SB=4, BB=4.5, and the straddler=5 instead offer 24bb, 27bb, and 30bb. With a separate 4-bet multiplier of 2.5, a 4-bet facing 24bb goes to 60bb. Minimum-raise and all-in rules still apply. Sizes remain in the original big blind when a straddle is active.

API fields: `open_raises_by_seat`, `raise_mults_by_seat`, `fourbet_mults`, and `fourbet_mults_by_seat`. Seat lists follow `positions`; an empty inner list inherits its default. Omitting the new four-bet fields preserves the old behavior where the re-raise menu applied at every depth. UI-loaded old games preserve that inheritance explicitly.

## Validation

Regression tests cover all 169×169 complementary hand-class shares, pot accounting under asymmetric solved ranges with zero/uncapped/capped rake, position and round-specific legal sizes, saved-game round trips, and CPU/GPU strategy and EV agreement. These are correctness checks for the approximation, not empirical validation of its poker ranges.
