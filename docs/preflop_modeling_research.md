# Preflop modeling: data-grounded player types, engine validation, and the road to "accurate and flexible"

*2026-09-06. Companion to the Preflop Lab. Numbers marked **[PHH]** come from
the analysis in `T:\Dev\poker-data\phh\analyze_phh.py` over the HandHQ
July-2009 real-money cash hands in the U of Toronto PHH dataset (Kim,
doi 10.5281/zenodo.13997158, CC-BY 4.0); everything else is cited inline.*

## 1. What we wanted to know

Modeling a live $2/2 table needs ~20 numbers per player (VPIP, PFR, 3-bet,
fold-to-3-bet, squeeze, fold-vs-raise cold and after limping, size
sensitivity, fold-vs-squeeze, c-bet/barrel by street, fold-vs-bet by street,
raise-vs-bet, stab, sizes). Guessing them is hopeless; published sources give
a few pool averages and everything else is folklore. Three things were done:

1. **Published population stats** were collected (section 2).
2. **A public hand-history dataset** (21.6M real-money NLHE hands) was
   re-analyzed to get the *conditional* numbers nobody publishes and to
   derive player types from clusters of real players (section 3).
3. **The engine was validated against GTO Wizard** on a configuration both
   can solve, to see which of its answers to trust (section 4).

## 2. Published population numbers (online; live shifts noted)

| stat | value | population / source |
|---|---|---|
| fold to 3-bet (as raiser) | 55–65% | low-stakes online cash NL10–NL50; 60–70% NL100–200; 65–75% fast-fold — VIP-Grinders 3-bet guide (2026) |
| 3-bet frequency by matchup (GTO) | BTN vs CO ~12%, CO vs UTG ~6%, SB vs BTN 10–12%, BB vs BTN 8–10% (+25–35% flats) | same source, solver-derived |
| fold to flop / turn / river c-bet | 45% / 34% / 37% | ~400k hands, NL10 pool (2+2 theory thread, quoted via search) |
| fold to c-bet, overall | ~48% | micro-stakes pool (2+2 population-tendencies thread) |
| fold to turn bet by size | 36% vs 33–50% pot, 47% vs 67–75% pot | micro-stakes pool (2+2) — size sensitivity is real |
| balanced c-bet frequency | 50–55% | BlackRain79 (micros); "bet everything small" still works at NL2–5 |
| recreational player stat shapes | passive fish 56/5 or 40/8-ish; "aggro fish"/maniac 52/37; VPIP > 40 = fish | BlackRain79 |
| winning 6-max reg | 20–28% VPIP; VPIP–PFR gap ≤ 5–7 pts | deepfold / pokercopilot / vip-grinders |
| solid full-ring reg | 14–20% VPIP / 12–18% PFR | pokercopilot |
| live vs online | live VPIP ≈ online + 5–8 pts; far more limping, fewer 3-bets, more multiway flops | freebetrange / pokerarticles |
| GTO RFI 6-max 100bb, 2.5x | UTG 17, HJ 21, CO 28, BTN 43, SB ~35–45 (raise-or-fold) | nlh.poker / preflopwizard (solver-derived) |
| GTO RFI 9-max 100bb | UTG 9–12, UTG+1 11–14, LJ 14–17, HJ 19–22, CO 25–28, BTN 44–48, SB 44–50 | preflopwizard.app |
| BB defence vs BTN (GTO) | 35–40% | preflopwizard.app |

Nobody publishes limp-then-fold-to-raise, cold-facing-a-3-bet, or
size-banded fold rates; those come from section 3.

## 3. The dataset re-analysis [PHH]

*Method.* Every hand is replayed by a state machine that classifies each
decision the way the GTOpen profile buckets do — UNOPENED / VS LIMPS /
VS RAISE / SQUEEZE / VS 3-BET+, split by whether the player had already
voluntarily invested (cold vs after limping/calling) and by the size faced
(raise TO ≤2.5 / ≤3.5 / ≤5 / >5 bb) — and, postflop, c-bet opportunities
(initiative = last aggressor, checks don't pass it), stab opportunities, and
fold/call/raise when facing a bet, per street. Counters are kept per
anonymized player id, players with enough hands are clustered by VPIP/PFR,
and the conditional stats are pooled per cluster (each player weighted by
its decisions). Full-ring (7–9 dealt) and 6-max (4–6 dealt) are kept apart;
full-ring 25–100NL is the closest public analogue to a live $2/2 table.

*Results:* see section 3.1 (filled in by the run).

### 3.1 Pool and type tables

The run covered **21.56 million hands** in three stake groups: micro
(25–50NL: 8.09M hands, 190k players), low (100–200NL: 5.64M, 63k players)
and mid (400–1000NL: 7.82M, 55k players). Full per-group reports are in
`docs/phh_reports/`; the scripts are in `tools/phh/`. "n" is the number of
decisions; type rows pool players with ≥300 hands, each weighted by its hands.

**Micro stakes (25–50NL), the closest analogue to a live $2/2 table**

**Full ring (7-9 dealt)** — 25,391,718 player-hands
- VPIP 21.6% · PFR 8.4% · limp (open-limp or limp-behind) 10.0%
- unopened (first in) (n=12,155,978): fold 76.2% · call 12.5% · raise 11.3% · check 0.0%
- BB option (no raise) (n=1,119,978): check 89.5% · raise 9.6% · fold 0.9%
- vs limps (cold) (n=4,793,316): fold 70.2% · call 21.0% · raise 8.8% · check 0.0%
- vs raise, cold (n=5,515,884): fold 85.1% · call 11.8% · raise 3.1%
- vs raise after LIMPING (n=445,023): call 50.7% · fold 46.4% · raise 2.9%
- squeeze spot, cold (raise + callers in front) (n=1,136,412): fold 81.4% · call 15.8% · raise 2.8%
- vs squeeze / raise after calling (n=206,459): call 62.0% · fold 35.6% · raise 2.4%
- vs 3-bet as the RAISER (n=288,135): call 45.7% · fold 44.1% · raise 10.2%
- vs 3-bet COLD (n=346,414): fold 94.7% · call 4.0% · raise 1.3%
- vs 4-bet+ (invested) (n=53,123): call 61.4% · fold 26.6% · raise 12.0%
- vs raise cold, by raise size — TO le2.5: fold 77% / call 19% / raise 4% (n=772,255); TO le3.5: fold 83% / call 13% / raise 3% (n=1,996,816); TO le5: fold 88% / call 9% / raise 3% (n=2,394,490); TO gt5: fold 92% / call 6% / raise 2% (n=352,323)
- vs raise after limping, by raise size — TO le2.5: fold 6% / call 90% / raise 4% (n=32,887); TO le3.5: fold 21% / call 76% / raise 3% (n=59,996); TO le5: fold 45% / call 51% / raise 3% (n=226,710); TO gt5: fold 71% / call 27% / raise 2% (n=125,430)
- flop: bet with initiative 70.3% (n=773,653) · bet without initiative 25.6% (n=3,164,236) · vs bet: fold 59.1% / call 31.2% / raise 9.7% (n=2,431,527)
- turn: bet with initiative 60.0% (n=654,546) · bet without initiative 24.8% (n=1,468,240) · vs bet: fold 47.2% / call 43.1% / raise 9.8% (n=1,133,511)
- river: bet with initiative 55.6% (n=478,924) · bet without initiative 26.5% (n=872,466) · vs bet: fold 53.5% / call 36.4% / raise 10.2% (n=663,533)

**6-max (4-6 dealt)** — 21,714,032 player-hands
- VPIP 28.1% · PFR 12.9% · limp (open-limp or limp-behind) 9.8%
- unopened (first in) (n=10,633,654): fold 67.4% · raise 18.6% · call 14.0% · check 0.0%
- BB option (no raise) (n=1,146,422): check 85.3% · raise 13.3% · fold 1.4%
- vs limps (cold) (n=2,678,426): fold 62.2% · call 24.1% · raise 13.7% · check 0.0%
- vs raise, cold (n=5,314,130): fold 77.8% · call 17.7% · raise 4.5%
- vs raise after LIMPING (n=416,717): call 58.1% · fold 39.0% · raise 3.0%
- squeeze spot, cold (raise + callers in front) (n=1,048,703): fold 74.8% · call 21.2% · raise 4.0%
- vs squeeze / raise after calling (n=162,450): call 62.6% · fold 34.9% · raise 2.5%
- vs 3-bet as the RAISER (n=369,379): fold 47.3% · call 43.8% · raise 8.9%
- vs 3-bet COLD (n=315,601): fold 92.9% · call 5.5% · raise 1.7%
- vs 4-bet+ (invested) (n=60,792): call 50.7% · fold 34.9% · raise 14.4%
- vs raise cold, by raise size — TO le2.5: fold 68% / call 26% / raise 6% (n=571,402); TO le3.5: fold 75% / call 20% / raise 5% (n=1,916,527); TO le5: fold 81% / call 15% / raise 4% (n=2,632,039); TO gt5: fold 88% / call 10% / raise 2% (n=194,162)
- vs raise after limping, by raise size — TO le2.5: fold 5% / call 91% / raise 4% (n=29,337); TO le3.5: fold 19% / call 78% / raise 3% (n=49,967); TO le5: fold 39% / call 58% / raise 3% (n=249,562); TO gt5: fold 61% / call 36% / raise 3% (n=87,851)
- flop: bet with initiative 67.3% (n=1,094,266) · bet without initiative 25.4% (n=3,231,454) · vs bet: fold 55.6% / call 33.9% / raise 10.6% (n=2,443,080)
- turn: bet with initiative 55.9% (n=832,941) · bet without initiative 25.6% (n=1,630,153) · vs bet: fold 46.2% / call 43.8% / raise 10.0% (n=1,214,657)
- river: bet with initiative 52.0% (n=598,512) · bet without initiative 27.7% (n=1,004,978) · vs bet: fold 53.9% / call 36.3% / raise 9.8% (n=740,813)

### Player types — full ring (players with ≥300 hands, weighted by hands)

| type | n | hands | VPIP | PFR | open-limp | limp-behind | iso | 3-bet | fold v raise (cold) | fold v raise (limped) | limp-raise | squeeze | fold v squeeze | fold to 3-bet | 4-bet | fold v 3-bet cold | fold v ≤2.5x | fold v ≤3.5x | fold v >5x | c-bet F | barrel T | barrel R | fold v bet F | T | R | raise v bet F | stab F |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Nit / OMC | 2,940 | 9,119,539 | 10 | 7 | 2 | 7 | 7 | 3 | 93 | 58 | 3 | 3 | 41 | 46 | 16 | 98 | 90 | 92 | 96 | 73 | 52 | 45 | 72 | 63 | 64 | 10 | 15 |
| TAG reg | 1,030 | 2,388,226 | 17 | 12 | 2 | 9 | 13 | 4 | 89 | 61 | 2 | 3 | 45 | 55 | 8 | 97 | 83 | 87 | 95 | 71 | 46 | 40 | 65 | 56 | 58 | 12 | 20 |
| Tight-passive | 2,945 | 4,855,222 | 18 | 7 | 11 | 21 | 7 | 2 | 88 | 59 | 2 | 2 | 44 | 50 | 8 | 97 | 79 | 87 | 95 | 68 | 55 | 49 | 65 | 54 | 58 | 9 | 22 |
| LAG reg | 90 | 88,264 | 27 | 20 | 3 | 12 | 20 | 6 | 83 | 25 | 0 | 4 | 35 | 53 | 6 | 95 | 74 | 80 | 93 | 71 | 47 | 43 | 58 | 49 | 52 | 13 | 25 |
| Loose-passive (semi) | 2,671 | 2,384,292 | 28 | 9 | 19 | 31 | 9 | 2 | 81 | 54 | 2 | 2 | 41 | 49 | 6 | 94 | 69 | 78 | 92 | 68 | 58 | 52 | 59 | 48 | 55 | 9 | 27 |
| Loose-aggressive fish | 97 | 65,064 | 39 | 25 | 9 | 22 | 27 | 6 | 72 | 64 | 0 | 5 | – | 42 | 7 | 94 | 59 | 67 | 84 | 71 | 60 | 57 | 49 | 40 | 51 | 16 | 36 |
| Loose-passive fish | 1,824 | 1,165,835 | 40 | 9 | 33 | 43 | 10 | 3 | 72 | 47 | 2 | 3 | 39 | 46 | 5 | 92 | 57 | 68 | 88 | 69 | 64 | 58 | 54 | 43 | 52 | 9 | 31 |
| Whale (VPIP 48+) | 826 | 431,641 | 57 | 11 | 51 | 58 | 13 | 4 | 55 | 37 | 3 | 4 | 32 | 36 | 7 | 86 | 41 | 49 | 80 | 70 | 69 | 63 | 49 | 38 | 50 | 9 | 34 |
| Maniac (VPIP 48+, aggressive) | 35 | 20,905 | 58 | 34 | 18 | 31 | 38 | 10 | 52 | 41 | 5 | 9 | 44 | 33 | 6 | 88 | 38 | 45 | 72 | 76 | 66 | 65 | 45 | 38 | 50 | 15 | 47 |

### Player types — 6-max (players with ≥300 hands, weighted by hands)

| type | n | hands | VPIP | PFR | open-limp | limp-behind | iso | 3-bet | fold v raise (cold) | fold v raise (limped) | limp-raise | squeeze | fold v squeeze | fold to 3-bet | 4-bet | fold v 3-bet cold | fold v ≤2.5x | fold v ≤3.5x | fold v >5x | c-bet F | barrel T | barrel R | fold v bet F | T | R | raise v bet F | stab F |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Nit / OMC | 318 | 971,652 | 13 | 9 | 2 | 8 | 9 | 4 | 91 | 47 | 3 | 3 | 36 | 50 | 11 | 97 | 86 | 89 | 95 | 67 | 48 | 40 | 70 | 61 | 63 | 10 | 15 |
| TAG reg | 3,332 | 7,820,082 | 19 | 14 | 1 | 9 | 15 | 5 | 86 | 64 | 2 | 4 | 49 | 56 | 9 | 96 | 79 | 85 | 93 | 68 | 45 | 39 | 64 | 57 | 60 | 12 | 18 |
| Tight-passive | 1,106 | 1,760,379 | 20 | 8 | 10 | 21 | 8 | 3 | 85 | 53 | 2 | 2 | 41 | 49 | 8 | 96 | 75 | 82 | 92 | 64 | 52 | 46 | 62 | 52 | 57 | 10 | 20 |
| LAG reg | 723 | 1,052,246 | 27 | 20 | 2 | 12 | 21 | 7 | 79 | 57 | 3 | 5 | 48 | 51 | 9 | 94 | 69 | 77 | 89 | 68 | 45 | 40 | 58 | 52 | 57 | 13 | 21 |
| Loose-passive (semi) | 2,450 | 2,313,924 | 29 | 11 | 17 | 30 | 11 | 3 | 77 | 47 | 2 | 3 | 38 | 47 | 6 | 93 | 64 | 74 | 89 | 65 | 55 | 49 | 57 | 48 | 55 | 10 | 24 |
| Loose-aggressive fish | 312 | 267,615 | 39 | 25 | 8 | 23 | 25 | 8 | 68 | 44 | 3 | 6 | 28 | 43 | 7 | 92 | 54 | 63 | 85 | 65 | 49 | 47 | 52 | 44 | 53 | 14 | 26 |
| Loose-passive fish | 2,469 | 1,679,778 | 40 | 11 | 31 | 43 | 12 | 4 | 68 | 41 | 3 | 3 | 38 | 44 | 7 | 91 | 52 | 64 | 85 | 66 | 61 | 55 | 53 | 43 | 54 | 10 | 28 |
| Whale (VPIP 48+) | 1,247 | 716,043 | 56 | 12 | 49 | 57 | 15 | 5 | 52 | 34 | 3 | 5 | 32 | 43 | 6 | 85 | 37 | 46 | 75 | 69 | 66 | 60 | 48 | 40 | 53 | 9 | 32 |
| Maniac (VPIP 48+, aggressive) | 111 | 78,289 | 55 | 33 | 16 | 32 | 36 | 10 | 50 | 43 | 4 | 8 | 40 | 34 | 7 | 81 | 33 | 44 | 74 | 69 | 59 | 52 | 45 | 40 | 53 | 14 | 34 |

**Low stakes (100–200NL), full ring — for comparison (tighter, more regs)**

**Full ring (7-9 dealt)** — 9,239,853 player-hands
- VPIP 18.8% · PFR 9.2% · limp (open-limp or limp-behind) 6.5%
- unopened (first in) (n=4,711,055): fold 79.4% · raise 12.8% · call 7.8%
- BB option (no raise) (n=252,081): check 89.7% · raise 10.2% · fold 0.1%
- vs limps (cold) (n=1,234,876): fold 71.9% · call 18.7% · raise 9.4%
- vs raise, cold (n=2,353,324): fold 86.7% · call 9.7% · raise 3.6%
- vs raise after LIMPING (n=124,649): fold 49.6% · call 46.7% · raise 3.7%
- squeeze spot, cold (raise + callers in front) (n=413,615): fold 82.0% · call 14.9% · raise 3.1%
- vs squeeze / raise after calling (n=46,602): call 59.2% · fold 37.9% · raise 2.9%
- vs 3-bet as the RAISER (n=127,822): fold 54.7% · call 36.2% · raise 9.1%
- vs 3-bet COLD (n=161,949): fold 96.8% · call 2.2% · raise 1.0%
- vs 4-bet+ (invested) (n=19,079): call 58.6% · fold 32.0% · raise 9.4%
- vs raise cold, by raise size — TO le2.5: fold 79% / call 16% / raise 5% (n=319,961); TO le3.5: fold 87% / call 10% / raise 4% (n=1,391,158); TO le5: fold 90% / call 7% / raise 3% (n=566,949); TO gt5: fold 93% / call 6% / raise 2% (n=75,256)
- vs raise after limping, by raise size — TO le2.5: fold 5% / call 90% / raise 5% (n=4,508); TO le3.5: fold 23% / call 72% / raise 4% (n=15,400); TO le5: fold 48% / call 48% / raise 4% (n=72,327); TO gt5: fold 72% / call 25% / raise 3% (n=32,414)
- flop: bet with initiative 63.5% (n=285,032) · bet without initiative 24.8% (n=818,671) · vs bet: fold 61.2% / call 28.9% / raise 9.9% (n=656,216)
- turn: bet with initiative 44.2% (n=214,425) · bet without initiative 25.5% (n=378,987) · vs bet: fold 52.3% / call 38.7% / raise 9.0% (n=278,851)
- river: bet with initiative 48.0% (n=121,190) · bet without initiative 28.7% (n=196,603) · vs bet: fold 55.8% / call 36.0% / raise 8.2% (n=144,287)

### Player types — full ring (players with ≥300 hands, weighted by hands)

| type | n | hands | VPIP | PFR | open-limp | limp-behind | iso | 3-bet | fold v raise (cold) | fold v raise (limped) | limp-raise | squeeze | fold v squeeze | fold to 3-bet | 4-bet | fold v 3-bet cold | fold v ≤2.5x | fold v ≤3.5x | fold v >5x | c-bet F | barrel T | barrel R | fold v bet F | T | R | raise v bet F | stab F |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Nit / OMC | 792 | 3,756,566 | 11 | 8 | 1 | 7 | 8 | 4 | 93 | 66 | 6 | 3 | 46 | 55 | 13 | 98 | 87 | 93 | 95 | 62 | 33 | 41 | 69 | 63 | 62 | 11 | 17 |
| TAG reg | 413 | 1,480,216 | 17 | 13 | 1 | 10 | 13 | 4 | 89 | 67 | 4 | 4 | 46 | 60 | 9 | 98 | 82 | 88 | 93 | 66 | 39 | 38 | 65 | 59 | 60 | 11 | 20 |
| Tight-passive | 855 | 1,597,755 | 19 | 7 | 10 | 23 | 7 | 2 | 87 | 58 | 4 | 2 | 43 | 59 | 6 | 98 | 76 | 87 | 94 | 63 | 44 | 42 | 65 | 57 | 59 | 9 | 24 |
| LAG reg | 29 | 28,281 | 27 | 19 | 2 | 19 | 18 | 6 | 81 | – | – | 5 | – | 55 | 7 | 99 | 72 | 81 | 90 | 62 | 45 | 52 | 61 | 53 | 55 | 13 | 24 |
| Loose-passive (semi) | 772 | 714,849 | 28 | 9 | 18 | 31 | 9 | 3 | 79 | 52 | 3 | 3 | 40 | 55 | 5 | 96 | 66 | 79 | 92 | 60 | 47 | 48 | 59 | 51 | 57 | 10 | 27 |
| Loose-aggressive fish | 21 | 12,387 | 39 | 24 | 9 | 24 | 26 | 5 | 70 | 51 | 6 | 4 | – | 53 | 4 | 91 | 55 | 70 | – | 62 | 51 | 38 | 53 | 47 | 55 | 14 | 31 |
| Loose-passive fish | 375 | 261,285 | 39 | 11 | 28 | 42 | 12 | 3 | 70 | 49 | 2 | 3 | 39 | 53 | 5 | 95 | 55 | 69 | 87 | 64 | 52 | 50 | 56 | 47 | 56 | 9 | 30 |
| Whale (VPIP 48+) | 112 | 62,581 | 55 | 13 | 43 | 52 | 16 | 4 | 54 | 35 | 2 | 4 | 19 | 34 | 5 | 97 | 38 | 52 | 86 | 68 | 55 | 57 | 50 | 43 | 54 | 9 | 32 |
| Maniac (VPIP 48+, aggressive) | 6 | 2,737 | 54 | 31 | 13 | 32 | 33 | 4 | 54 | – | – | 2 | – | 53 | 3 | – | 47 | 53 | – | 57 | 52 | 52 | 49 | 40 | 48 | 11 | 25 |

**Mid stakes (400–1000NL), 6-max — the reg-heavy end**

### Player types — 6-max (players with ≥300 hands, weighted by hands)

| type | n | hands | VPIP | PFR | open-limp | limp-behind | iso | 3-bet | fold v raise (cold) | fold v raise (limped) | limp-raise | squeeze | fold v squeeze | fold to 3-bet | 4-bet | fold v 3-bet cold | fold v ≤2.5x | fold v ≤3.5x | fold v >5x | c-bet F | barrel T | barrel R | fold v bet F | T | R | raise v bet F | stab F |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Nit / OMC | 27 | 128,599 | 13 | 11 | 1 | 9 | 10 | 7 | 89 | 50 | 13 | 5 | – | 49 | 22 | 97 | 86 | 90 | 93 | 50 | 29 | 41 | 66 | 56 | 56 | 12 | 16 |
| TAG reg | 2,173 | 14,655,544 | 21 | 17 | 0 | 11 | 17 | 7 | 84 | 67 | 7 | 6 | 52 | 59 | 13 | 96 | 80 | 85 | 90 | 65 | 41 | 39 | 59 | 56 | 59 | 14 | 19 |
| Tight-passive | 460 | 964,749 | 21 | 9 | 9 | 23 | 8 | 3 | 82 | 44 | 4 | 3 | 35 | 55 | 8 | 96 | 74 | 83 | 91 | 59 | 46 | 46 | 58 | 53 | 58 | 11 | 19 |
| LAG reg | 1,426 | 6,459,560 | 27 | 21 | 1 | 13 | 21 | 9 | 78 | 56 | 9 | 7 | 56 | 57 | 11 | 95 | 73 | 79 | 88 | 68 | 44 | 41 | 54 | 52 | 57 | 14 | 22 |
| Loose-passive (semi) | 2,018 | 3,012,444 | 29 | 14 | 11 | 29 | 13 | 4 | 73 | 44 | 4 | 4 | 33 | 51 | 7 | 94 | 63 | 75 | 88 | 59 | 45 | 43 | 53 | 49 | 56 | 12 | 22 |
| Loose-aggressive fish | 763 | 1,014,498 | 39 | 25 | 6 | 26 | 24 | 8 | 65 | 47 | 6 | 7 | 38 | 48 | 8 | 92 | 55 | 66 | 85 | 61 | 47 | 46 | 48 | 46 | 54 | 14 | 22 |
| Loose-passive fish | 2,110 | 2,080,645 | 40 | 14 | 25 | 39 | 15 | 5 | 62 | 36 | 4 | 5 | 30 | 48 | 6 | 91 | 51 | 64 | 84 | 59 | 50 | 49 | 49 | 45 | 55 | 11 | 26 |
| Whale (VPIP 48+) | 955 | 734,581 | 56 | 15 | 42 | 52 | 19 | 5 | 46 | 28 | 4 | 5 | 24 | 46 | 6 | 85 | 34 | 46 | 74 | 64 | 55 | 52 | 46 | 41 | 54 | 10 | 31 |
| Maniac (VPIP 48+, aggressive) | 232 | 221,783 | 55 | 32 | 10 | 31 | 37 | 9 | 46 | 36 | 5 | 9 | 34 | 41 | 6 | 87 | 35 | 47 | 78 | 62 | 53 | 50 | 45 | 44 | 54 | 12 | 29 |

### 3.2 What the data says (the numbers you were guessing)

- **Limpers are sticky, but size matters enormously.** Facing a raise after
  limping, micro full-ring players fold 46% overall — but only 6% vs a raise
  to ≤2.5 bb, 21% vs ≤3.5 bb, 45% vs ≤5 bb and 71% vs >5 bb. Cold, the same
  pool folds 85% (77% → 92% by size). Any profile that folds the same
  amount to every raise size is wrong in the direction that made BTN
  "raise 98% into three limpers".
- **Whales (VPIP 48+, passive)** at micro full ring: 57/11, open-limp 51%,
  limp-behind 58%, fold to a cold raise 55% (37% after limping), fold to a
  3-bet as raiser 36%, fold to a flop bet 49%, stab 34% without initiative.
- **Passive fish (VPIP 34–48)**: 40/9, open-limp 33%, limp-behind 43%, fold
  to raise cold 72% / limped 47%, fold to 3-bet 46%.
- **Regs** (TAG 17/12 full ring, 19/14 6-max): fold to 3-bet 55–60%, 4-bet
  8–9%, c-bet 68–71% flop / 45% turn / 40% river, fold to flop bet 64%.
- **Nobody 3-bets much**: 3–5% for regs, 3–4% for fish, 10% for maniacs;
  squeezes are 2–5% everywhere.
- **Cold-calling a 3-bet is rare for everyone**: 93–98% fold — which is why
  the engine's cold-vs-3-bet rule was changed to "continue only with the
  hands you would 3-bet with".
- **Postflop, the pool folds to a flop bet 55–59%, turn 46–47%, river 54%;
  c-bets 67–70% on the flop; stabs ~25% without initiative** — the
  published NL10 numbers (fold to c-bet 45/34/37) are in the same family
  once you note those count only c-bets, not all bets.

### 3.3 The archetypes that ship

`cache/archetypes.json` (loaded by the engine; "measured player types" in
the seat dropdown) carries the **seven preflop types** of the 25–50NL pool,
table sizes pooled (the 6-max and full-ring numbers of a type were within a
couple of points, so the split was noise), each with every field the
editor takes — including the first-in rates (open-raise / open-limp) and
the vs-limpers rates (iso-raise / limp-behind) that the generator now uses
for the entry buckets instead of VPIP/PFR — plus a provenance note, and
each with up to two **postflop modifiers** (`· station` = folds to a flop
bet under 45%, `· folder` = over 65%), because postflop style is an
independent axis: the VPIP/PFR type explains 89% of the variance in VPIP
and 72% of fold-vs-raise but 3% of c-bet and 26% of fold-to-flop-bet.
The scheme (VPIP bands 14 / 24 / 48, "aggressive" = raises 60%+ of the
hands he plays; 50% in the 48+ band) and the clustering that motivated it
are written up in `docs/player_types.md`. Naiveté is the one value not
measurable from stats; it is set by type (whale 0.75, maniac 0.6, fish
0.55, tight-passive 0.35, nit 0.3, LAG 0.2, TAG 0.15). Regenerate with
`python tools/derive_archetypes.py <types_micro.json>` after re-running
the analysis (the 1.9 GB dataset lives in `T:\Dev\poker-data\phh\`,
outside the repo).

*Caveat that matters:* this is online play from July 2009. Live $2/2 in
2026 is looser and stickier still (more limping, fewer 3-bets, less
folding to small raises), so treat the fish/whale rows as a floor on
looseness and nudge VPIP and the fold numbers in the "stickier" direction
when you know the room.

## 4. Engine validation against GTO Wizard (100bb, 2.5x opens, no limps, 5%/3bb rake)

The lab was solved to a <0.008 bb BR gap and compared with published GTO
Wizard frequencies. All numbers are % of the acting player's range.

**6-max, one 3-bet size (3.5x), 3-raise cap — the standard solver setup**

| spot | GTOpen (calibrated) | GTO Wizard |
|---|---|---|
| RFI UTG / HJ / CO / BTN | 20.6 / 23.3 / 30.0 / 43.9 | ~17 / 21 / 28 / 43 |
| BB vs BTN 2.5x: fold / call / 3-bet | 62.8 / 25.8 / 11.5 | ~62 / 25–35 / 8–10 |
| BTN vs CO 2.5x: call / 3-bet | 4.5 / 8.0 | ~10 / ~12 |
| HJ vs UTG 2.5x: call / 3-bet | 2.7 / 4.7 | ~5 / ~6 |
| UTG vs HJ 3-bet: fold / call / 4-bet | 61.0 / 26.0 / 13.0 | ~55–60 / ~30 / ~10 |
| same, with two 3-bet sizes (3x + 4x) | 55.7 / 29.3 / 15.0 (3-bets go 4x) | |

**9-max, same setup**

| spot | GTOpen (calibrated) | GTO Wizard |
|---|---|---|
| RFI UTG / UTG+1 / MP / LJ / HJ / CO / BTN / SB | 14.1 / 16.3 / 18.1 / 20.6 / 23.1 / 29.8 / 44.4 / 60.3 | 9–12 / 11–14 / – / 14–17 / 19–22 / 25–28 / 44–48 / 44–50 |
| BB vs BTN 2.5x: fold / call / 3-bet | 62.6 / 25.9 / 11.4 | ~62 / 25–35 / 8–10 |
| BTN vs UTG 2.5x: call / 3-bet | 3.1 / 3.8 | ~8 / ~5 |
| UTG vs BTN 3-bet: fold / call / 4-bet | 53.9 / 31.0 / 15.0 | ~55–60 / ~30 / ~10 |
| CO vs BB 3-bet: fold / call / 4-bet | 55.9 / 26.0 / 18.1 | ~50–55 / ~35 / ~12 |

Reading: opening ranges, blind defence and 3-bet-pot defence all land
within a few points of a full solver. The systematic deviations: early
positions open 3–4 points wider than Wizard at 9-max, **in-position
cold-calls are under-used** (BTN flats an open ~4% where a solver flats
~10%) with 3-bets a little light to match, and the SB raises very wide
(60%, raise-or-fold) — the calibrated leaf model is pessimistic on
flatting without initiative, as the project notes already said, but it is
not far off.

**Two things to know when reading lab output**

1. *Multiway equilibria are not unique.* The same 6-max game with a
   4-raise cap converged to a different equilibrium of the model in which
   HJ 3-bets only value and UTG folds 97.5% to it (a solver folds ~57%).
   Nothing was wrong with the solve (BR gap 0.0045 bb); the model has more
   than one equilibrium and CFR found that one. With a 3-raise cap it finds
   the polar-3-bet / defend one. Keep raise caps at 2–3 for cash-game
   studies and treat "everyone folds to the 3-bet" answers with suspicion.
2. *The postflop model decides blind-defence width.* Under the positional
   heuristic the BB defends 84% vs a BTN open, under raw pot × equity 97%,
   under calibrated 37% (solver: 35–40%). Calibrated is the only usable
   default; the others exist for sensitivity checks.

## 5. Ideas, ranked

1. **Solver-anchored calibration of the leaf model.** The calibrated fit
   already reproduces a full solver's opening, blind-defence and 3-bet-pot
   numbers to within a few points (section 4). What it still gets wrong is
   systematic: in-position cold-calls are under-used, early seats open a
   little wide, the SB raises too much. A second fitting objective — make
   the lab's HU equilibria reproduce a full solver's preflop frequencies on
   the configurations both can solve (6-max / 9-max, 100bb, no limps; GTO
   Wizard's charts as the reference) — would close those with the machinery
   M5 already has (class base × role × pot-type multipliers). Moderate
   effort, and it improves every multiway line, not just HU ones.
2. **Exact heads-up subgames for the lines that matter** ("Tier 2" in
   TODO.md): a 3-bet pot BB vs BTN is heads-up; solve the preflop street +
   flop subset as ONE game with the postflop engine (no leaf model). Exact,
   but a bigger build; item 1 should come first because it fixes every
   multiway line too.
3. **Data-grounded archetypes + per-situation stats** (this work): stats
   split by situation (unopened vs vs-limps, cold vs after-limping,
   size-banded), with the dataset's numbers as defaults. Add `vpip/pfr vs
   limps` (limp-behind and iso rates differ from unopened rates) and
   `fold-vs-raise after limping` as first-class stats — the two live-game
   numbers the generator currently derives from VPIP.
4. **Table templates**: save a scenario + every seat's profile + hero as one
   named "table" (`saves/tables/`), so "$2/2 Tuesday lineup" is one click.
5. **Robustness dial (RNR)**: hero solves against "profile with probability
   p, free adversary with 1−p" (TODO item 5). Max-exploit lines like
   "raise 98% over three limpers" are correct only if the read is exactly
   right; p ≈ 0.8 keeps most of the EV and stays hard to punish.
6. **Profile-conditioned realization**: a station's postflop tendencies
   should feed the *preflop* leaf value (a seat that folds 55% to flop bets
   realizes less), so preflop exploits reflect postflop weakness without
   sending every line to the postflop solver. Cheap version: a per-seat
   realization multiplier derived from the postflop tendencies.
7. **Straddles and per-seat stacks**: live $2/2 games straddle; the config
   has per-seat posts but action order for a straddle (acts last preflop)
   needs a builder change. Per-seat stacks (TODO) matter for the same games.
8. **Import a HUD line**: paste a PokerTracker/Hand2Note stat string and
   map it onto the profile fields.
9. **Report cards for profiles**: after a solve, show each modeled seat's
   *implied* stats next to the entered ones AND next to the dataset's type
   averages, so an unrealistic profile is visible before it drives a study.
