# GTOpen change log

What changed in GTOpen, newest first, in plain words. The version you are running shows at the right end of the app's top bar.

## 1.0.2 - 2026-11-18

- Preflop Lab now says in plain words how much memory a game needs, in RAM and on the graphics card, and whether it will solve on the graphics card (GPU) or the processor (CPU), before you build it. When it will be the processor it says why, and the "?" beside it explains how to make the game fit the card. The words "CPU arenas" are gone.
- The bubbles under SOLVE no longer repeat the progress bar. While a solve runs you see only GPU or CPU there; when it ends you see how it ended and its gap, once.

## 1.0.1 - 2026-11-18

- Preflop Lab's results area carries fewer messages. The "Target reached" line is gone. "Not solved from here on" is now a small warning icon before the spot's title, and Evidence is a small link at the end of that row. Hover or click either one to read the same text as before.

## 1.0.0 - 2026-11-18

The first numbered version. From here on, every change to the app gets a version number and a line in this file.

- The app shows its version and release date at the right end of the top bar. Click it to open this change log.

## Before version numbers

GTOpen had no version numbers before 18 November 2026. This is a short history of what shipped up to then.

### November 2026

Preflop Lab

- **Learned flop values.** Preflop solutions now value each hand by how it plays after the flop, using a neural net trained on many thousands of exact flop solves, and they count rake on the final pot. This is the default for new games. The current net (v3) also covers common live and online games: higher rake, bigger opens, straddles and deeper stacks.
- **Blockers.** The solver accounts for the cards in your hand making some of your opponents' hands less likely. On for every new game.
- **Unequal stacks and side pots.** Each seat can have its own stack.
- **Tournament payouts (ICM).** Enter the payouts and the stacks at the other tables, from a final table to a 1,000-player bubble.
- **Trust the read.** With a hero seat chosen, a slider sets how far to trust your read on the other players, from fully exploiting them to playing it safe.
- **Lines the solution never plays are marked "not solved"**, so you don't read a strategy off a spot the solver never worked on.
- Blinds are entered in big blinds like every other amount, and the build progress bar only moves forward.

Postflop

- **3-way postflop solving** in its own tab, from the flop to the river.
- **Tournament payouts (ICM)** in heads-up and 3-way postflop solves. A flop sent over from a tournament game in the Preflop Lab keeps its payouts.
- **Trust the read** in Browse and in reports: choose how much the solution leans on a player model, and see what it costs if the read is wrong.
- **Least-exploitable locking.** Lock a spot to an overall frequency ("bet a quarter of the time here") and let the solver pick which hands, in the way that gives up the least.
- **Best bet size.** A report that finds the best single size for a flop bet on every board, and **Find best size** in Browse for the board you are on.

The app

- A strip under the top bar shows the loaded spot and whether it is built or solved. Errors show in one bar with a retry button, and the screens carry less explanatory text.
- **Contribute compute.** Anyone with an NVIDIA graphics card can help make the training data behind learned flop values. [How to contribute](docs/contribute-compute.md).

### October 2026

- **Compare two reports** side by side, and **undo and redo for lock edits** in Browse (Ctrl+Z, Ctrl+Shift+Z).
- **Canonical GTO charts in the Preflop Lab.** If you have the chart files on your computer, the Preflop Lab can show them in place of a solve. The charts themselves are not part of GTOpen.
- Fixes for the all-in option: the all-in threshold is read correctly, and CPU solves with all-in sizes converge again.

### Earlier

The app as it stood by September 2026:

- **Heads-up postflop solver** for the flop, turn and river, on the CPU or an NVIDIA graphics card, with any bet sizes, rake, and locks on a hand or a whole range.
- **Preflop Lab** for 2 to 9 players, with limps, your own raise sizes for each position, rake, antes and a UTG straddle.
- **Player models** built from real online hands (Ignition and CoinPoker), to solve against how people actually play.
- **Reports** that solve one setup across up to 1,755 flops and compare the results by board, high card, hand class or texture.
- A Windows launcher that builds the app, starts it and opens the browser.
