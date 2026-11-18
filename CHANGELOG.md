# GTOpen change log

What changed in GTOpen, newest first, in plain words. The version you are running shows at the right end of the app's top bar.

## 1.2.0 - 2026-11-18

- Preflop Lab can size raises the way players do. Three new settings sit beside the sizes they change: an extra amount per limper when raising over limps, a tick box that adds the callers' money to a 3-bet or 4-bet (3 times an open of 3 is 9, and over two callers it becomes 15), and separate 3-bet and 4-bet sizes out of position. Out of position means acting before the raiser on the flop.
- The built-in scenarios use these sizes: 1 bb more per limper, callers' money added, and 3-bets of 3 times the raise in position and 4 times out of position. The three 8-max scenarios had two 3-bet sizes to choose from and now have one for each position, which makes them about a third to a half smaller.
- Scenarios and games you saved are unchanged: the new settings stay off in them until you fill them in. The game does not get bigger when you turn them on, because each spot keeps the same number of raise sizes.
- "Sizes by position" is now called "Sizes by seat", so that "position" only means in or out of position.
- The bigger squeezes make some flop pots larger than the leaf net was trained on. It values them the same as the same spot in smaller chips (checked: its values move about 0.2% of the pot), so the learned flop values hold there too.
- Close GTOpen and start it again after updating: until then the header shows "restart GTOpen" and the new sizes cannot be built.

## 1.1.5 - 2026-11-18

- STOP answers at once. The button turns to "STOPPING…" and the progress line says "stopping" from the click until the solve has really ended, in the Preflop Lab and in the postflop Solve tab. Before, nothing changed for a few seconds and the click looked lost.
- A stopped Preflop Lab solve says how accurate it is. It ends with one last accuracy check, so the line under SOLVE reads "stopped · iter 110" and "gap 0.5712 → 0.0050": the gap of the strategy on screen, next to the target. Before, a stopped solve showed no gap at all.
- That last check is why STOP takes a few seconds on a big game. The progress line says "checking final accuracy…" while it runs. Pressing STOP during an accuracy check no longer throws that check away and repeats the work.
- A stopped postflop solve also measures its accuracy once more, so the exploitability it shows belongs to the iteration it stopped at, not to an earlier check.

## 1.1.4 - 2026-11-18

- The "?" beside the Preflop Lab title now names the leaf net: a neural net trained on real flop solves that values each hand on a two-player flop. It also says that other pots, and games without learned flop values, use a simpler estimate.
- Sizes by position explains itself. Each empty box shows in grey the main size that seat will use, a line on top says what to type (for example 4 or 4,6), and each column heading has a tooltip.

## 1.1.3 - 2026-11-18

- Preflop Lab's memory lines say "GPU" and "CPU" plainly, and "GPU memory" for what the game needs on the card. The last line now says what a solve uses: a GPU solve uses both the RAM and the GPU memory, a CPU solve uses the RAM only.

## 1.1.2 - 2026-11-18

- Preflop Lab's memory lines are clearer. RAM and the graphics card each get their own line, with what the game needs and what is there: "RAM: needs about 18.8 GB, fits" and "Graphics card: needs 31.5 GB, has 31.4 GB, too big". Before, "18.8 GB of RAM fits" sat next to "too big for the graphics card" and read like a contradiction.
- The "?" beside those lines now says why a game needs more memory on the graphics card than in RAM.
- The "Show early strategy previews" checkbox under SOLVE is gone. Previews are always on; the gold line above the hand grid already says when you are looking at one.

## 1.1.1 - 2026-11-18

- Preflop Lab's tooltips and help text are shorter and in plain words, and the ones that had gone out of date are fixed. The "?" beside the panel title now says what the screen does in three sentences, and the title reads "Preflop game · 2 to 9 players".
- The help no longer says only two-player flops can be sent to the postflop solver. Three-player flops can be sent too, and the SEND box now says so.
- The small labels under MODEL say "learned flop values", "3+ players · estimate" and "blockers" instead of internal names.
- Tournament payouts: an empty stack-off rate showed "off" but used 0.4. It now shows 0.4.

## 1.1.0 - 2026-11-18

- Preflop Lab: a spot that is not solved now has a **How to study this line** button beside its title. It lists the steps for that exact action: which player type to give the seat, where to check or change its hands, and to solve again. "Show me" points at each control. The old advice mentioned a lock, which Preflop Lab has no control for; that is gone.

## 1.0.4 - 2026-11-18

- If you update GTOpen's files without restarting it, the page now says so: a "restart GTOpen" note shows at the top right until you close GTOpen and start it again. Before, parts of the page could just go blank, such as Preflop Lab's memory line.
- Preflop Lab's memory line never goes blank. If it cannot work something out, it says what is missing and why.

## 1.0.3 - 2026-11-18

- The ready-made preflop charts are now called "Canonical GTO charts" everywhere in the app.
- "Ranges from" in the Preflop Lab says what each choice is: GTOpen's solver works out the ranges for your exact game, the canonical GTO charts are ready-made for a few standard games with nothing to solve. A line under the choice says the same.
- When the charts fold a seat for you, that seat now reads "no chart" and "Auto-fold" instead of "Fold 100%". Hover it to see why: the charts only cover the common lines.
- The second chart under a solved hand grid is gone.

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
