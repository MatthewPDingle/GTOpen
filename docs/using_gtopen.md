# Using GTOpen

The details behind the [README](../README.md)'s tour: units, preflop sizes and values, player models, reports, and how far to trust each kind of result.

## Units

- **Preflop:** every amount is in big blinds, the blinds too. For $2/$5, enter a small blind of `0.4` and a big blind of `1`.
- **Postflop bet sizes** are percentages of the pot. `33 75` offers two sizes, `a` means all-in, and `2.5x` means a raise multiple.
- **Preflop Lab action labels** read in bb: "Raise 4 bb", "Call 3 bb", "3-bet 11 bb (2.75x)". A raise shows the total it goes to, a call shows what you add.

## Preflop Lab

**Ranges from.** Leave this on **GTOpen's solver (Leafnet model)** to work out the ranges for the game you set up. The other choice, **Pre-solved GTO charts**, shows ready-made charts in place of a solve. The chart files are not part of GTOpen, so that choice only works if you have them on your computer.

### Raise sizes

**Sizes by seat.** Expand **Sizes by seat** to override opens, 3-bets, and 4-bets or later raises for each seat. Blank cells inherit the defaults above. A 3-bet multiplier of `4` facing a 6bb open raises to 24bb. Build a fresh game after changing sizes.

**Sizes that follow the action.** `+ per limper (bb)` adds that many big blinds to an open for each limper already in. `re-raises add the callers' money` adds what the callers of a raise put in to a 3-bet or 4-bet over them (3x an open of 3 is 9; over two callers it is 15). The `out of position` boxes give 3-bets and 4-bets their own multipliers for a player who will act before the raiser on the flop. The built-in scenarios use all three. They are off in scenarios and games saved before version 1.2.0. [Raise sizing details](preflop_balanced_model.md#sizes-that-follow-the-action).

### Antes and straddles

**Ante.** The **Paid by** choice beside the Ante box says who pays it: each seat, or the big blind for the whole table, as in most tournaments. The ante is paid on top of the stack either way.

**UTG straddle.** Enable **UTG straddle** and enter its size (default **2 bb**, tables of 3 to 9 players). The next seat acts first and the straddler keeps the final check/raise option. All sizes stay in the original big blind: a 2 bb straddle needs an ordinary opening raise of at least 4 bb. [Straddle rules and model limitations](utg-straddles.md).

### How hands are valued

The Preflop Lab does not play out the flop, turn and river. It estimates what each hand is worth once the flop comes:

- **Two-player flops** use **learned flop values**: a neural net (the leaf net, `cache/leaf_net_v4.bin`) trained on exact flop solves. It values hands by how they play after the flop and counts rake on the final pot.
- **Pots with three or more players, all-in pots and games with tournament payouts** use a simpler estimate.
- **Blockers** are on for every new cash game: each hand accounts for the cards it takes away from the other players' ranges.

There is no switch for any of this. The small tag under **4 · MODEL** says what a game used. A game can still ask for the simpler estimate alone through the API (`realization: "balanced"`, about twice as fast). [What the net is and how it was checked](technical_reference.md#preflop-continuation-model) · [The simpler estimate and rake](preflop_balanced_model.md).

**Rake.** Set rake to `0` for no rake. With a positive rake, a cap of `0` means uncapped. With tournament payouts on, the rake boxes are greyed out: a tournament game has no rake.

**Older saves** keep the model they were solved with. **Re-solve** continues that model; save your work, then **Build game → Solve** to use the current model in a fresh game.

### Memory, GPU and CPU

Before you build, the lab shows how much RAM and GPU memory the game needs and whether it will solve on the GPU or the CPU. A game too big for the GPU all at once is solved on the GPU a part at a time (large-game mode), with the same answer. Games that are still too big, and a few game types large-game mode does not cover yet, solve on the CPU.

### Tournament payouts (ICM)

Tick **tournament payouts (ICM)** under the rake boxes and choose the stage. The rest (players at other tables, their stacks, your own payout list) sits under **Advanced tournament settings**. Games solve on the GPU or CPU, from final tables to a 1,000-player bubble. A flop sent to the postflop solver from a tournament game keeps its payouts, and the Postflop Setup & Solve page has the same tick box, for two or three players. [ICM details](technical_reference.md#icm-payoffs-tournaments).

### Player models

Use **Manage models** to create, edit, copy, or remove models from the menus. Assign models to seats, then apply them and re-solve. The **Evidence** link distinguishes measured hand policies and sizing from estimates and fallbacks.

The library includes Ignition NL10 and CoinPoker NL10/NL25/NL50/NL100 models. Coverage differs by dataset, position, and situation; saved or edited models keep their own settings. [Player types](player_types.md) · [Ignition](ignition_models.md) · [CoinPoker](coinpoker_models.md) · [Evidence labels](model_evidence.md).

With a hero seat chosen, the **trust** slider sets how far to trust your read on the other players, from fully exploiting them to playing it safe.

### Lines the solution never plays

The solver works on a spot in proportion to how often hands reach it. The ranges behind an action the solution almost never takes (shown as `<0.1%` in the action strip) are not a strategy, and two solves of the same game can disagree completely there. The Preflop Lab marks these spots and says which action led off the solution.

To study such a line, give that seat a player model that takes the action, then solve again. **How to study this line**, beside the title of such a spot, lists the steps for that exact action: which player type to pick, which tab and brush of its editor to use, then RE-SOLVE. The result is how to play against that player, not the equilibrium of the original game.

## Browse

- **Lock box.** Click or drag hands in the grid (none picked means the whole range), type how often they take each action, and press **LOCK**. For a whole range, **Scale**, **Least EV loss** and **Least exploitable** are three ways to choose which hands shift; hover each to read what it does.
- **Lock by group.** Set FILTERS (top pair, flush draws, one suit) and choose "the hands your filters show".
- **Locks list.** Above the grid, each lock says who, where and what. Click one to go there, or remove it. Undo and redo lock edits with the buttons or Ctrl+Z / Ctrl+Shift+Z.
- **After a lock,** an amber **OLD SOLVE** line reminds you the strategy on screen is from before the lock, until you press **RE-SOLVE** (both players adjust) or **EXPLOIT** (the best reply, at once).
- **Play as model.** With a flop sent from the Preflop Lab, a seat's player model can be locked onto every one of its postflop decisions.
- **Find best size** (Actions panel, at OOP's first flop decision or IP's after a check) searches for the best single bet size on the current board.

## Reports

Reports use the configuration in **Postflop Setup & Solve** and solve each flop independently. You do **not** need to build a tree or solve first just to generate a report.

- **Standard report sizes** replaces Setup's bet menu with a shared report menu. Turn it off to use your Setup sizes.
- **Vs modeled villain** applies one available player model from the Preflop export. It does not copy Browse's manual locks or lock both players. The current selection prefers OOP when both players have models.
- **Compare** reads a second report at the same point of the action line, over the flops both reports share. Each step of the line is matched by action label, or by the same kind of action at the nearest pot-relative size (within 5% of the pot), so a 50% bet in a 10bb pot matches a 50% bet in a 20bb pot. When the starting pots differ, EV is shown as a share of the pot. IP's EV change mirrors OOP's, so only OOP's is listed per flop.
- **Best size sweep** finds the best single size for one bet: IP's flop bet after a check, or OOP's first flop bet. Each flop is solved once per candidate size (default 25 / 33 / 50 / 75 / 125% pot, to 0.15% pot), then up to 3 more times between the best size's neighbours. The **Best size** view shows the best size per flop, the tie band (sizes whose EV gap is within the solves' combined exploitability, which the solves cannot separate), the best size mix by texture, and the EV lost by always using one size. Each candidate size is also kept as an ordinary report you can browse by node. A sweep costs about (sizes + 3) solves per flop.
- **Open in Browse** rebuilds and solves the selected report spot; it does not load a stored full solve. Match the board, action line, sizes, and modeling assumptions when comparing frequencies. Different convergence targets can still produce differences.

Use **Group by → High card** in Chart or Table, click column headings to sort, or switch to Hand classes and Textures. Hover a strategy bar for every action's frequency, including zeroes. Search and delete completed reports from the library.

## Saving

Files stay in the repository's `saves/` directory:

| Folder | Contents |
| --- | --- |
| `saves/` | Postflop solve sessions |
| `saves/preflop/` | Preflop game sessions |
| `saves/scenarios/` | Preflop Lab scenarios |
| `saves/profiles/` | Saved player models |
| `saves/reports/` | Reports and their per-node summaries |
| `saves/3way/` | Three-player postflop solves (they show in the same saved-solves list, marked "3 players") |

Saved solves use GTOpen's own format.

## What the results mean

- **Postflop** solves the configured tree to the target you set. Results depend on the ranges, sizes, rake, locks, and convergence target you choose.
- **Preflop** uses an approximate continuation model (see [How hands are valued](#how-hands-are-valued)). It does not solve the full multiway game through the river, and overlapping tight ranges in pots of three or more can still expose card-removal errors. [Model details](technical_reference.md#preflop-continuation-model).
- **Rare preflop lines are not solved**; see [Lines the solution never plays](#lines-the-solution-never-plays).
- **Player models** combine observations and inference. Sparse or unsupported situations need estimates; a dataset label is not proof that every displayed hand frequency was observed.
- **3-way postflop** is in beta. Set **Players** to 3 on the Postflop Setup & Solve page. Node locking, find best size, the runouts report and Reports are for two players only for now.
