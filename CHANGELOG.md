# GTOpen change log

What changed in GTOpen, newest first, in plain words. The version you are running shows at the right end of the app's top bar.

## 1.6.0 - 2026-11-19

- The Solve page is now part of the Setup page. The tab is called "01 · Postflop Setup & Solve": set the spot up in steps 01 to 04, then build and solve it in step 05 on the same page, with the progress numbers, the chart and your saved solves beside it. On a wide window everything fits on one screen.
- SOLVE builds the tree for you, so BUILD TREE is now optional. STOP takes SOLVE's place while a solve runs, as in the Preflop Lab. A new BROWSE button under them opens the tree as soon as it is built.
- The amber "SETUP changed" bar across the top of the page is gone. The line under the buttons says it instead, BUILD TREE turns amber, and hovering the line explains it.
- The other tabs are renumbered: 02 · Browse and 03 · Reports. The 3-way tab is now called "Beta 3-Way" and stays last.
- Nothing was removed. The RE-SOLVE and STOP buttons in the top bar work as before, from any page.

## 1.5.4 - 2026-11-19

- The Browse tab now says, right at the grid, when what it shows is older than your locks. After a lock change an amber line above the grid reads OLD SOLVE and names the two ways on: RE-SOLVE to solve with the locks, or EXPLOIT to see the best reply at once. The action tiles carry the same OLD SOLVE tag, and both buttons turn amber until you use one. It used to be a small note at the far end of the LOCKS row.
- The two buttons that lock a player to a saved player model now sit under the caption PLAY AS MODEL and read "BB = My Response". They lock every decision of that player after the flop, which is separate from the lock box (one decision). Nothing is locked until you press one, and a model that is on shows in LOCKS.

## 1.5.3 - 2026-11-19

- The "learned flop values" tick box is gone from the Preflop Lab. Every new cash game uses learned flop values, and games with tournament payouts use the simpler estimate, as before.
- The small tag under 4 · MODEL still says which one a game used. Hover it to read what the leaf net is and where the simpler estimate applies.
- A cash game you saved with the box unticked loads as it was solved, and RE-SOLVE continues it. BUILD GAME starts a new game with learned flop values.

## 1.5.2 - 2026-11-19

- The logo in the top left has room to breathe: the bottom of the "p" in "GTOpen" no longer drops into "open-source solver" under it.

## 1.5.1 - 2026-11-19

- Tournament payouts are now a tick box in the Preflop Lab's scenario form, right under the rake boxes, so you can see and switch them without opening anything. Ticking it shows one more choice: the stage of the tournament.
- The rest (players at other tables, their stack, stack-off rate, your own payout list and the prize-pool read-out) sits under "Advanced tournament settings", closed until you open it. Nothing was removed. Choosing the Custom stage opens it for you.
- With tournament payouts on, the two rake boxes are greyed out at 0 and their tooltip says why: a tournament game has no rake. The cramped "ICM · 0" labels are gone. Your own rake numbers come back when you turn tournament payouts off.
- The explanation of tournament payouts moved into a small "?" beside the tick box.
- The Setup and 3-Way tabs got the same tick box and greyed rake boxes.

## 1.5.0 - 2026-11-19

- Preflop Lab has a big blind ante. A new "Paid by" choice beside the Ante box says who pays it: each seat, as before, or the big blind for the whole table, as in most tournaments.
- The ante is paid on top of the stack either way, so every seat still plays the stack you set. To make the big blind shorter by its ante, give it its own stack under Stacks by seat.
- A 1 bb ante from the big blind makes the same pot over the same stacks as 0.125 bb from each of 8 seats, so the ranges come out close to the same. The results per seat differ, because the big blind paid for everyone.
- Scenarios and games you saved are unchanged: their ante is still paid by each seat.
- Close GTOpen and start it again after updating. Until then the header shows "restart GTOpen" and a game with a big blind ante will not build.

## 1.4.3 - 2026-11-19

- The BEST REPLY button is gone from the list of locks in the Browse tab. It did the same as EXPLOIT: pick whose hands to show under HANDS OF, then press EXPLOIT.

## 1.4.2 - 2026-11-19

- The small hand tiles in the Browse tab (HANDS, lower right) now say how often each action is taken. Each action has its own row: name, "how often" in bold, then EV, with the two column names right above the numbers.
- The popup that shows when you hover a hand in the grid has the same two columns, and it is now as wide as it needs to be, so a raise no longer gets its name cut off.
- A tile grows when a spot has many actions, so no row is hidden.

## 1.4.1 - 2026-11-19

- The three ways to shift a whole range in the Browse lock box are called Scale, Least EV loss and Least exploitable again. Hover one to read what it does in plain words.

## 1.4.0 - 2026-11-19

- Node locking in the Browse tab is reworked to take a few clicks. Nothing it could do before is gone.
- One lock box. Click the hands you want in the grid (drag to pick several), type how often they take each action, and press LOCK. With no hand picked, the lock is for the whole range. What you typed stays when you change anything else in the box, and "always" sets an action to 100%. The three ways to shift a whole range now read "every hand a little", "the cheapest hands" and "hardest to punish".
- Lock by hand group or by suit: set FILTERS (top pair, flush draws, one suit) and choose "the hands your filters show".
- A list of locks sits above the grid. Each says who, where and what ("BTN · after Check · 9 hands set · 59% Check, 41% All-in"). Click one to go there, the x removes it, and "clear all" removes them all (Undo brings them back). After a lock, the list offers the two next steps: BEST REPLY shows at once how the other player should answer, and RE-SOLVE lets both players adjust.
- EXPLOIT shows every hand in the player's range, also the hands the solve rarely takes down this line (they are faded). The small hand tiles show the best reply too, with what each action is worth. When it is the other player's turn the grid says so, and hands with nothing to gain are grey, not red.
- Each action tile has an arrow that follows that action. A click on the rest of the tile still only filters the grid.
- Fixed: on a spot with tournament payouts the app always said Setup had changed and offered only REBUILD & SOLVE, which threw the locks away. It now offers RE-SOLVE and keeps them. Building a new tree also says how many locks it would throw away.
- Changed: "keep earlier decisions as solved" now holds only the locked player's own earlier decisions on the line, so the other player stays free to answer the lock. It used to hold both players'.
- Close GTOpen and start it again after updating. Until then the header shows "restart GTOpen", the list of locks has no click-to-go or remove buttons, and "keep earlier decisions" works the old way.

## 1.3.1 - 2026-11-18

- Preflop Lab now shows every size in bb. Raises used to read as multiples ("3-bet 2.75x") beside calls in bb ("Call 3 bb"). A raise now shows the total it goes to, and a re-raise adds its multiple in brackets: "Raise 4 bb", "3-bet 11 bb (2.75x)", "Call 3 bb". A call still shows what you add.
- When a re-raise adds the callers' money, the brackets say so: "3-bet 15 bb (3x + callers)".
- The same wording is used in the action strip, the spot title, the colour key under the grid and the hand tooltips.

## 1.3.0 - 2026-11-18

- Bigger Preflop Lab games can solve on the GPU. A game too big for the GPU all at once used to go to the CPU. Now the GPU takes it a part at a time ("large-game mode"), which needs roughly 40% less GPU memory, so games up to about 1.7 times as big fit. The answer is the same.
- Tested on an RTX 5090: an 8-max 150bb game with two open sizes, limps and the all-in option took about 7 minutes a step on the CPU and now takes about 7 seconds on the GPU.
- Games that already fit the GPU solve exactly as before, at the same speed. Large-game mode is used only when the normal solve has no room, and the "Solves on" line says when it is.
- Not covered yet, so these still go to the CPU when too big: tournament payouts, the trust dial, unequal stacks and the exact 3-way table.

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
