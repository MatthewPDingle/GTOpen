# Heads-up rake accounting and position sizes

New games built in the UI use **Balanced (approx.)** with a learned correction at heads-up flops on top ("learned flop values", every new game since 2026-11; see `leafnet` in the [technical reference](technical_reference.md)). This page describes Balanced itself, which prices every multiway and all-in pot, every game with ICM payouts, and everything in a game that asks for `balanced` through the API (the box that switched learned flop values off was removed in 1.5.1; a save made with it off keeps Balanced until **Build Game**). The model selector has been removed. Scenario presets supply the game settings, and their historical model choices no longer affect fresh builds.

Existing solved saves keep the model that generated their regrets and strategy sums. To update an old game, **Build Game** and solve afresh. Re-solve with unchanged settings continues the saved game under its original model. Changing game settings creates a fresh game when Solve is pressed; choosing a scenario also starts afresh if the loaded game uses an older model. Legacy calculations remain available internally for save compatibility and research. This UI simplification does not introduce a new or more accurate model.

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

## Sizes by seat

The global menus are opening raise-to sizes in bb, 3-bet multipliers, and 4-bet+ multipliers. Expand **Sizes by seat** (called "Sizes by position" before version 1.2.0) to override each menu for a seat. Multiple comma-separated values offer multiple legal actions; blank cells inherit the corresponding default. Squeezes use the 3-bet menu. Re-raise multipliers apply to the previous total raise-to amount, not the extra chips added.

For example, against a 6bb open, a default 3-bet multiplier of 3 offers 18bb. SB=4, BB=4.5, and the straddler=5 instead offer 24bb, 27bb, and 30bb. With a separate 4-bet multiplier of 2.5, a 4-bet facing 24bb goes to 60bb. Minimum-raise and all-in rules still apply. Sizes remain in the original big blind when a straddle is active.

API fields: `open_raises_by_seat`, `raise_mults_by_seat`, `fourbet_mults`, and `fourbet_mults_by_seat`. Seat lists follow `positions`; an empty inner list inherits its default. Omitting the new four-bet fields preserves the old behavior where the re-raise menu applied at every depth. UI-loaded old games preserve that inheritance explicitly.

## Sizes that follow the action

Three optional settings change raise amounts with the action so far. Each spot keeps the same number of raise sizes, so the tree does not grow (a bigger raise can reach the all-in threshold sooner, which makes it slightly smaller).

- `limper_extra` (bb, default 0): every open size grows by this for each limper already in, the small blind completing included. Open 3 with two limpers and 1 here offers 5. A seat's own open sizes grow the same way.
- `caller_extra` (default 0; the UI tick box sends 1): a re-raise is the multiple of the raise it faces plus this share of what the callers of that raise have put in. 3x an open of 3 is 9; with two callers and 1 here it is 9 + 3 + 3 = 15. A call all-in for less counts for what it put in. Limpers who have not called the raise are not callers. 4-bets over callers of a 3-bet work the same way.
- `raise_mults_oop` and `fourbet_mults_oop` (default absent): the 3-bet and 4-bet+ multipliers for a seat that is out of position to the raiser it faces, meaning it acts before that seat on the flop (`PreflopConfig::postflop_order`: small blind, big blind, then the other seats in order; heads-up the big blind acts first). Absent uses the in-position menu. A seat's own list in `raise_mults_by_seat` or `fourbet_mults_by_seat` wins in and out of position. With `fourbet_mults` absent too, an out-of-position 4-bet uses the out-of-position 3-bet menu.

Example, 6-max with open 3, 3-bet 3 in position and 4 out, callers' money on: UTG opens 3, HJ and CO call. The BTN's 3-bet is 15 and the SB's is 18.

Games using any of these save as format v7, which older binaries refuse; with all of them off the config and the save are byte-for-byte what they were. The UI's built-in scenarios turn them on (1 bb per limper, callers' money, 3x in position and 4x out); saved scenarios without the keys keep them off.

Leaf net coverage: the net was trained on 3-bet pots up to about 104 bb (26 bb at up to four times the usual table scale). Squeezes over several callers of a large open, and raises over many limpers, build heads-up flop pots past that (about 300 bb with 10 bb opens). Flop play does not depend on the chip scale once the stack and the rake cap are given per pot, and the net follows that: given the same leaves at 0.7 of the top of its trained range, with the same stack-to-pot ratio and rake cap per pot, its per-hand values move 0.21% of the pot on average (0.30% at the 90th percentile), no more than leaves inside the range halved the same way (0.24%). Checked 2026-11-18 with net v3 on the 6-max built-in scenario and on a 150 bb version of it with 7.5 and 10 bb opens, at the starting ranges. This shows the net does not go wrong because a pot is large; it is not a comparison with exact solves of those pots.

## Validation

Regression tests cover all 169×169 complementary hand-class shares, pot accounting under asymmetric solved ranges with zero/uncapped/capped rake, position and round-specific legal sizes, saved-game round trips, and CPU/GPU strategy and EV agreement. These are correctness checks for the approximation, not empirical validation of its poker ranges.
