# Player types: the scheme, the data behind it, and what each one costs you

*2026-09-06. Companion to `docs/preflop_modeling_research.md` (the dataset,
the pipeline, the GTO Wizard validation). This note answers three
questions Matthew asked: why were the archetype categories what they were,
how many categories does the data actually support, and which ones are worth
telling apart when the goal is exploiting live players.*

## 1. The scheme that ships

Seven preflop buckets on VPIP bands (14 / 24 / 48) and **one aggression
rule** you can read at the table — *aggressive = raises at least 60% of
the hands he plays* (50% in the 48+ band, where limping half the deck is
the whale's whole identity):

| type | VPIP | PFR | 3-bet | first-in: raise / limp | vs limpers: iso / limp behind | folds to a raise: cold / after limping | folds to 3-bet (as raiser) | c-bet F | folds to flop bet | players |
|---|---|---|---|---|---|---|---|---|---|---|
| Nit | 10.5 | 7.1 | 3.0 | 10 / 2 | 7 / 7 | 93 / 58 | 47 | 72 | 72 | 3,287 |
| Tight-passive | 18.8 | 7.2 | 2.2 | 10 / 10 | 7 / 21 | 87 / 58 | 50 | 67 | 64 | 4,115 |
| TAG | 18.3 | 13.9 | 4.7 | 20 / 1 | 15 / 9 | 87 / 62 | 56 | 69 | 64 | 4,408 |
| Loose-passive fish | 33.4 | 10.1 | 3.1 | 14 / 25 | 11 / 36 | 74 / 48 | 47 | 66 | 56 | 9,861 |
| LAG | 29.9 | 21.6 | 7.2 | 29 / 6 | 21 / 15 | 76 / 51 | 49 | 67 | 56 | 1,566 |
| Whale | 56.5 | 12.5 | 4.8 | 16 / 52 | 14 / 58 | 52 / 35 | 40 | 69 | 49 | 2,284 |
| Maniac | 56.3 | 37.1 | 13.5 | 33 / 55 | 34 / 29 | 48 / 43 | 38 | 64 | 46 | 743 |

All percentages; 25–50NL online cash, July 2009 (HandHQ via the U of
Toronto PHH dataset), every player with 300+ hands, 6-max and full ring
pooled (a type's numbers were within a couple of points across table
sizes). *Players* is the count in that bucket; by hands dealt the regs
weigh more and the whales less.

Each type also ships with up to two **postflop modifiers**, split on the
one postflop stat with the most exploit value and the least preflop
predictability: `· station` folds to a flop bet under 45% of the time,
`· folder` over 65%. A station's numbers are its own measured subgroup —
stations are also a little looser preflop and fold less to 3-bets (a
TAG station folds 41% to 3-bets, a TAG folder 60%).

In the Preflop Lab these are the `Data · <type>` entries of the seat
dropdown. Every one carries the first-in and vs-limpers rates the engine
now uses for the entry buckets (a 17/12 TAG open-limps 1%, not the 5% that
VPIP − PFR implied), both fold-vs-raise numbers, size bands, and the
postflop block.

## 2. Why these cuts: what the data supports

Unsupervised clustering of 2,942 full-ring players with 1,500+ hands
(14.5M hands) on 11 preflop and postflop stats (`cluster_types.py`, in the
data folder):

- **Player stats are a continuum, not clusters.** K-means silhouette peaks
  at k=2 (tight vs loose, 0.25 on all features, 0.43 on VPIP/PFR alone)
  and is flat at ~0.12 from k=4 upward; GMM BIC keeps improving to k≈9
  without a knee. Any category count is a modelling choice.
- **The VPIP/PFR type explains preflop behaviour and almost nothing
  postflop.** Share of variance explained by the nine old bands: VPIP 0.89,
  open-limp 0.74, fold-vs-raise 0.72, PFR 0.41 — but fold-to-flop-bet 0.26,
  fold-to-turn-bet 0.21, c-bet 0.03, raise-vs-bet 0.05, fold-to-3-bet 0.03.
  Hence the separate postflop axis.
- **The 6-max / full-ring split was noise** (same type, same numbers ±2).
- **Survivorship caveat:** among 1,500+-hand players only 6% are loose.
  Your live pool by hands dealt is far looser, and the loose types are the
  ones worth exploiting; their numbers here come from the 300+-hand set.

So: cut for the two things categories are for. *Exploitation* — the
stats that change the max-exploit strategy are range width (VPIP), how he
enters (limp vs raise), what he does after limping when raised, fold to
3-bet, and fold to flop bet. *Learnability* — what you can observe in an
hour: how often he plays, whether he limps or raises, whether limps fold to
raises, and how he reacts to c-bets.

## 3. Reading players live: the cues that separate the buckets

1. **Does he limp first-in?** Regs (TAG, LAG, Nit) essentially never (1–6%).
   Tight-passives limp about as often as they raise; fish limp twice as
   often as they raise; whales limp half of everything.
2. **How often does he voluntarily play?** Under one hand in seven = nit;
   one in five = tight; one in three = loose; every other hand = whale /
   maniac.
3. **When he plays, is it a raise?** Raises most of what he plays =
   aggressive (TAG / LAG / maniac); limps or calls most of it = passive
   (tight-passive / fish / whale).
4. **What happens when his limp gets raised?** Regs and nits fold ~60%;
   fish fold about half; whales fold a third. The limper who "always sees
   the flop" is the whale, and he is the reason iso-raising limpers prints.
5. **Postflop modifier:** count his folds to flop c-bets over a session.
   Under half = station (bet for value thinner, bluff less); over two thirds
   = folder (c-bet everything, barrel when the turn misses him).

## 4. What each type costs you: the cross-exploit study

Method (`xev_study.py`): for each type A, every seat but the BTN plays the
measured type-A profile (position-aware), hero on the BTN solves its
maximum-exploit strategy (300 iterations, GPU); that strategy is then
frozen and evaluated against a table of every other type B. The loss of
using A's counter-strategy against type B is `EV[B][B] − EV[A][B]` in
bb/100. A GTO row (hero's strategy from an unruled equilibrium of the
same table) shows what exploiting gains over playing "correctly". Two
games: 8-max 150bb $2/2 (opens 7.5x/10x, limps, 10% rake capped 8.5bb)
and 8-max 200bb $2/5 (opens 3x/4x, 5% rake capped 2.2bb).

### 4.1 What the BTN makes against a table of each type (bb/100)

| | Nit | Tight-passive | TAG | Loose-passive fish | LAG | Whale | Maniac |
|---|---|---|---|---|---|---|---|
| **$2/2** GTO strategy | +14 | +14 | +18 | +15 | +20 | +19 | +22 |
| **$2/2** max-exploit | +77 | +69 | +95 | +56 | +61 | +99 | +81 |
| **$2/5** GTO strategy | +24 | +19 | +21 | +15 | +19 | +16 | +18 |
| **$2/5** max-exploit | +80 | +74 | +90 | +62 | +65 | +69 | +57 |

The equilibrium BTN already beats every measured type (they all bleed
preflop); knowing the type and exploiting it adds 40–80 bb/100 on top.
Hero's best-response gap was 0.000 on every ruled table, 0.001 on the
unruled one.

### 4.2 The cost of the wrong read (loss in bb/100)

Rows: the counter-strategy hero plays. Columns: what the table actually is.

**8-max 150bb $2/2, 7.5x/10x opens, 10% rake**

| counter for → / table ↓ | Nit | Tight-passive | TAG | LP fish | LAG | Whale | Maniac |
|---|---|---|---|---|---|---|---|
| GTO | 63 | 54 | 78 | 41 | 41 | 80 | 59 |
| Nit | 0 | 126 | 194 | 187 | 270 | 287 | 461 |
| Tight-passive | 202 | 0 | 6 | 5 | 17 | 18 | 48 |
| TAG | 216 | 24 | 0 | 31 | 18 | 39 | 88 |
| Loose-passive fish | 203 | 4 | 12 | 0 | 9 | 6 | 38 |
| LAG | 237 | 40 | 23 | 16 | 0 | 12 | 22 |
| Whale | 227 | 42 | 57 | 7 | 17 | 0 | 32 |
| Maniac | 231 | 52 | 63 | 26 | 20 | 37 | 0 |

**8-max 200bb $2/5, 3x/4x opens, 5% rake**

| counter for → / table ↓ | Nit | Tight-passive | TAG | LP fish | LAG | Whale | Maniac |
|---|---|---|---|---|---|---|---|
| GTO | 57 | 56 | 69 | 46 | 46 | 53 | 39 |
| Nit | 0 | 55 | 87 | 82 | 116 | 110 | 184 |
| Tight-passive | 80 | 0 | 2 | 3 | 7 | 13 | 52 |
| TAG | 82 | 12 | 0 | 20 | 7 | 27 | 65 |
| Loose-passive fish | 80 | 2 | 5 | 0 | 5 | 5 | 45 |
| LAG | 83 | 10 | 5 | 12 | 0 | 9 | 32 |
| Whale | 111 | 34 | 42 | 10 | 14 | 0 | 29 |
| Maniac | 134 | 61 | 64 | 39 | 31 | 28 | 0 |

### 4.3 What it means for the number of categories

- **Nits are the must-identify type, in both directions.** Every other
  counter-strategy loses 80–460 bb/100 against a nit table (it keeps
  paying off raises that only ever come from premiums; the 10x opens at
  $2/2 double the damage), and the nit counter-strategy folds far too much
  against everyone else. One tight, big-raising, never-limping player at
  the table changes what you do more than any other read.
- **Maniacs are the second must-identify type.** Any other counter loses
  22–88 bb/100 against them ($2/2), and theirs loses 20–63 elsewhere.
- **The middle five collapse from the exploitation side.** The
  loose-passive-fish counter-strategy loses at most 12 bb/100 against
  tight-passives, TAGs, LAGs and whales at $2/2, and at most 5 at $2/5.
  The collapse is one-directional: the TAG and whale counters are fragile
  (24–57 bb/100 when the read is wrong), the fish counter is robust.
- **So three counter-strategies** — nit, fish (the default), maniac —
  get within ~12 bb/100 of perfect information on single-type tables; a
  fourth, TAG-tuned one is worth ~12 bb/100 more when the table really is
  all regs at $2/2. For *recognition*, keep all seven: whale vs
  tight-passive vs TAG changes where the money comes from (limp-raising,
  iso-raising, 3-betting) even when the counter-strategy is similar, and
  the seven are what the live cues in §3 actually distinguish.

Caveats: BTN only, tables of a single type, and the preflop model's EV
with calibrated postflop realization — the postflop modifiers do not enter
these numbers at all (that is a postflop-solver study, next). Profiles are
rigid rule-followers who never adapt, so the absolute EVs are ceilings;
the *relative* losses are the point. Mixed tables will be milder.

### 4.4 Next

1. Postflop cross-exploit: station vs folder through the report engine
   (c-bet / barrel / fold-to-bet), which is where the modifiers pay.
2. Mixed tables: your actual seat map (two fish, a nit, four TAGs) rather
   than seven copies of one type.
3. A live read-training drill built on §3's cues, scored against these
   loss numbers (a wrong nit read costs you more than a wrong TAG read, so
   it should cost more in the drill).
