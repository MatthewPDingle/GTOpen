# Tree audit before interpreting the baseline

19 September 2026. This baseline matches the six recorded decision menus,
stacks, posts, opening size and stated rake. It does **not** reproduce Wizard's
entire tree. Residual differences cannot all be attributed to continuation EVs.

Wizard's visible solution preview confirms `200 bb (100str)` and `4% 6BB CAP`.
GTOpen uses no-flop-no-drop; that Wizard convention remains unverified.

## Inspected raise line

Wizard: UTG raises6, LJ raises18, HJ/CO/BTN/SB/BB/STR fold, UTG responds with
fold/call/raise45/jam200. After UTG raises45, LJ can fold/call/jam200. The last
menu was inspected directly in the browser on 19 September:

https://app.gtowizard.com/solutions?soltab=strategy&solution_type=gwiz&gmfs_solution_tab=ai_sols&gametype=SingleStraddleNoAnteGeneral_8mNL25R6&depth=200&gmff_depth=200&gmff_type=general&gmff_rake=NL25&gmff_opening_size=6bb&history_spot=9&preflop_actions=R6-R18-F-F-F-F-F-F-R45

GTOpen's maximum-raise setting counts the open. `max_raises=3` would remove
the 5-bet jam. This baseline therefore uses four raises and `allin_threshold=0.4`:
the permitted non-jam 4-bets range from 40.5 to 75bb; the smallest subsequent
multiplier raise is 91.125bb. The 80bb conversion boundary leaves those 4-bets
unchanged and makes 5-bets jams. This is an action-menu construction choice,
not a player tendency or a fitted parameter. Production settings are unchanged.

The inspected UTG 4-bet is 2.5 times LJ's 18bb. Cold IP 4-bets shown in Wizard
are 40.5bb; blind cold 4-bets are 45bb. Per-seat overrides reproduce that line.

## Known differences

- Wizard's HJ/CO/BTN/SB/BB/STR responses to UTG6/LJ18 show fold/4-bet/jam,
  without a cold call. GTOpen permits the call. Record its frequencies after
  the solve to establish whether the extra branch is used.
- Wizard permits SB completions in unopened pots. GTOpen's global no-limp
  setting also removes that completion. All six selected paths begin with
  UTG's decision, but the missing branch can affect upstream values.
- GTOpen's 4-bet sizing overrides are seat-specific, not conditional on which
  seat opened. Matching UTG's response does not match every later opener.
- Wizard's postflop bet abstraction and solution accuracy are not reproduced;
  GTOpen uses Balanced HU continuation and coupled-deck-v1 multiway approximation.

## Fixed run plan

Use the existing GPU production executable in a separate process on 56710.
Run to total internal BR gap below 0.005bb, checking every50 iterations, at
most3000. Save all six nodes. Then run250 additional iterations with early
stopping disabled, save the nodes again, and measure strategy/diagnostic-score
drift. A small internal gap certifies neither exact poker equilibrium nor a
rare individual branch. Both checkpoints and timings must be reported.

The 100bb reserved reference situations remain unopened. No model training,
parameter fitting, production deployment or live-session replacement is part
of this run.
