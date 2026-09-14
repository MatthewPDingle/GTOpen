# Live UTG straddles

The implementation adds a live post on the first seat without renumbering
seats. Preflop action starts on the next seat; the straddler's option and
ordinary postflop order are preserved. Scenarios, the action ribbon, postflop
exports and versioned game saves carry the setting.

The checkbox enables one normal UTG straddle, default 2 bb, on tables with at
least three players. The first seat is immediately left of BB; three-handed
this is also the button. Action proceeds clockwise from the next seat. This
does not implement Mississippi/button priority, re-straddles or sleeper bets.

Amounts remain in the original big blind: at $2/$5, a 2 bb straddle is $10,
a 200 bb stack is still $1,000, and a raise to 5 bb is $25. The straddle is a
live post, not a voluntary raise or a limper. A normal first raise must be at
least twice the straddle (except a shorter all-in); later minimum raises use
the preceding raise increment. Invalid opening sizes are reported explicitly.

API: `utg_straddle: true` plus the amount in `posts[0]`; remaining posts are
SB/BB in the last two seats. Omitted/false keeps the existing behavior. Seat
identities, profile indices and postflop position remain fixed. Scenarios store
`straddle` as an amount in bb (zero/off). Straddled game saves use
`GTOPREFLOP3` so an older binary cannot rebuild them in the wrong action order;
existing unstraddled saves retain their format and remain readable.

History models were measured without straddles. Transfers must be labeled as
extrapolated; the contextual re-raise model already rejects straddled formats.
No new straddle-specific player model is being trained by this feature.
Newly generated BB entry ranges use aggregate stats, because the source's
unopened BB free-check placeholder is not a paid calling range. Existing saved
or manually painted profiles retain their chosen probabilities; regenerate
them explicitly when transferring a model to a straddled game. Solver seats
solve the actual configured straddled tree.

To use it:

1. Set the player count and original SB/BB stakes in Preflop Lab.
2. Enable **UTG straddle** and enter its size in original bb (at least 2).
3. Set legal open sizes, such as `4,5,6` for a 2 bb straddle. The estimate
   explains invalid sizes before building. An empty menu allows only any
   separately enabled all-in option.
4. **Build game**, then **Solve**. The ribbon identifies the forced straddle;
   follow actions normally. A heads-up postflop export retains the original
   pot/stack units, physical positions, and the straddle in the action history.

Turning the checkbox off returns to ordinary blinds. It is unavailable
heads-up. New straddled saves require an updated GTOpen; unstraddled saves
remain compatible with their existing format.

Rule reference: [WSOP live-action rules](https://assets.wsopcdn.com/wsop/853ee602-e1e9-4019-a0cf-381419d805c6.pdf)
describe a live straddle's last preflop action and a minimum raise of double
the straddle. This implementation uses that conventional rule, not every
possible house-rule variant.

## Validation (14 September 2026)

- Full release solver suite passed, including eight straddle regressions:
  3/4/6/9-player action order, last option, folds, reopening/minimum raises,
  post accounting, postflop export, estimation, data-model routing and saves.
- GPU straddle paths matched each other exactly. Separate 3/4-player tests
  matched the CPU traversal and converged decisions using the established
  numerical tolerances. Existing native preflop/postflop and server tests passed.
- Browser walkthrough: invalid 2 bb open rejected against a 2 bb straddle;
  legal tree built and solved; SB completed 1.5 bb, BB faced 1 bb, and the
  straddler retained Check/Raise. A heads-up export retained SB OOP, straddler
  IP, 5 bb pot and 8 bb remaining from 10 bb stacks.
- Scenario save/selection, game save/load and page reload retained the straddle.
  Switching to heads-up disabled it; selecting the saved scenario restored it.

Re-run the feature checks with `node tools/test_preflop_blinds.mjs` and
`cargo test --release -p solver --test preflop_straddle`. On a CUDA machine,
also run `cargo test --release -p solver --features gpu --test preflop_gpu
--test preflop_straddle -- --test-threads=1` with NVRTC on PATH.
