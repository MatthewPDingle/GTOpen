# Bomb pot net: the research loop

A loop of trials on one machine. Each trial trains a heads-up bomb pot net
by self-play on a small game and is judged by one number. This file is the
whole brief for whoever runs the loop.

## Goal

One net that plays flops it never practised on. The measure is exact: the
share of the starting pot a perfect opponent gains against the net
(`bombpot score`), lower is better. A trial's score is the average of that
over 24 flops the net never plays (`unseen` in `trial.py`'s result).

Where it stands (40 rounds, the 95 flop set, 16 walks a flop, 20 hours):
6.7% on flops it trains on, 11.2% on flops it never played. The target for
the full-size run is 3% on never-played flops. More rounds alone do not
close the gap: between rounds 30 and 40 the trained flops improved and the
never-played ones did not. On more flops the same net looks a little
better: 9.8 on three further never-played flops and 8.6 on the eight test
flops, scored once before the loop.

## A trial

    python tools/bombpot/trial.py --config tools/bombpot/research/NAME.json
        --work WORK --exe target/release/bombpot --threads 10 --gpu-free-gb 2

`research/base.json` is the starting recipe on the small game: the 47 flop
set, 8 walks a flop, 15 rounds. It takes about 3.1 hours beside the
generator, and 3.6 with the scoring of 24 unseen flops. A new idea is a
copy of the best config so far with one change and a new `name`. Results
add up in `WORK/trials.jsonl`.

Keep the cost of a trial level: an idea that makes a trial slower than
about 1.3 times the base has to pay for it (say so in the notes), and
nothing may take over five hours.

## Rules of evidence

1. **Noise first.** Run the base with `seed` 1, 2 and 3 before any idea.
   The spread of `unseen` over the three seeds (highest minus lowest) is
   the noise, and their average is the base's score. Measured on 25 Nov:
   20.6, 21.5 and 22.6, so the base is 21.6 and the spread 2.0. On the
   first eight unseen flops alone the spread was 3.7, because single flops
   move 3 to 8 points between seeds; that is why a trial scores 24. A
   longer base was not tried: it would have cost twelve hours, and the
   loop is after gains of several points.
2. **Keep rule.** An idea is kept when its `unseen` beats the best so far
   by more than two spreads. Between one and two spreads, run it with a
   second seed and keep it only if the average still wins by a spread.
   Under one spread it is dropped.
   `trained` may get up to 2 points worse for a kept idea, not more (its
   own spread over the three seeds is 1.6).
   `trained` only compares between trials that score the same trained
   flops. The base scores QcTc9d, Qc8c6c and Qc4d3h, the three flops the
   47 and 95 sets share, so trials on those two sets compare; the 184 set
   shares none of them, so a trial on it names trained flops of its own
   and is judged on `unseen` alone. `trial.py` refuses a config whose
   trained flops are not in its spec, or whose unseen flops are.
3. **One change per trial.** Two ideas that each help are then tried
   together as their own trial.
4. **The test flops are not yours.** `specs/flop_AcKd5d`, `KdKc9c`,
   `Kc8c3c`, `Qc9d4h`, `Jc9d6d`, `Tc8c5d`, `9c3d2h` and `6c3d3c` are never
   practised on and never scored in the loop. They are scored once, at the
   end, by whoever started the loop. No practice set may contain an unseen
   or a test flop (`Jc8d4h` is in the 184 set and is in neither list).
5. Write down every trial, kept or not, in `WORK/notes.md`: the idea in a
   sentence, the two numbers, the minutes, kept or not, and why you think
   it went that way.

## Ideas, roughly in the order I would try them

- **More flops for the same work.** The 95 set at 4 walks
  (`specs/95_flops_4_walks.json`) or the 184 set at 2
  (`specs/184_flops_2_walks.json`) against 47 at 8. Not
  `95_flops_river_solved.json`: that is the full-size run with 16 walks,
  four times the work. Run G says fewer walks per flop learn slower; the
  question is which side wins for never-played flops at equal cost.
- **A net that is told what a flop is.** Inputs for the situation side and
  the hand side that do not depend on the exact cards: paired or trips,
  how many of one suit, how connected, the high card's rank. Today the
  only link between two flops is the card embeddings and ten hand-strength
  numbers.
- **Rank and suit embeddings** added up in place of one embedding per
  card, so that a nine is a nine on every flop.
- **Size and training time.** Hand side or situation side 512 wide; 6,000
  or 8,000 steps per half round. The trained flops got one point worse
  from 6 to 95 flops at the same size and steps.
- **Random suit renaming on standard-suit flops** (drop `fixed-suits`):
  the net then sees each practice flop in all its suit forms. It cost fit
  on one flop; with many flops it may pay.
- **Round weights** (`power`, `avg-power` 1.5 or 2): faster on plain
  tables, worse with noisy examples in earlier tests on one flop.
- **Dropout or weight decay on the situation side**, if the trained score
  keeps falling while the unseen one stalls inside a trial.

Inputs and embeddings live in `crates/solver/src/bombpot/net.rs` and
`tools/bombpot/train.py` and must stay in step (`bombpot netcheck` and
`train.py --check` compare the two). A change to the inputs changes the
example and net files, so it needs a rebuild and fresh trials.

## The machine

The loop runs on Pan's desktop beside his own work. These are his rules.

- Work only in `X:\Dev\GTOpen-bombpot` (code) and
  `X:\Dev\GTOpen-bombpot-work` (output). Never change, build in or write
  to `X:\Dev\GTOpen` or `X:\Dev\GTOpen-datagen`, and never touch the
  generator, validator or uploader windows, any `solve-cli`, his GTOpen
  app, or other programs of his.
- At most 10 engine threads, below normal priority (`low-priority` is in
  the base config). Always `in-ram`: the trainer then holds under 1 GB of
  the graphics card.
- Run every trial under the guard (`run_i95_guard3.ps1` is the pattern):
  freeze the trial when the card passes 31.8 of 32.6 GB or a program of
  Pan's other than his GTOpen app passes 2 GB (a game, ComfyUI), continue
  after five clear minutes. The project's own leaf-net jobs do not count.
- Run detached with logs to files, so a trial survives a restart of the
  session, and read `WORK/trials.jsonl` and `notes.md` first on every wake.
- If the generator's jobs get clearly slower than they are without us,
  drop to 8 threads and say so.

## Reporting and stopping

- After the noise test, and then once a day, send a short report: trials
  run, the best `unseen` so far against the base, what was kept, what is
  next. Plain sentences, few numbers.
- Stop after three days, or when three ideas in a row fail to beat the
  best, or when `unseen` on the small game is within one noise spread of
  `trained`. Then stop everything of ours and report. Do not start the
  full-size run or score the test flops: that is decided with Pan.
