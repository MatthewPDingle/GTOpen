# Large-bet responses and limp-defense correction (September 2026)

The modeled 150bb game exposed two different issues: a conditioning bug and
extrapolation of ordinary-bet HUD rates to all-in bets.

First-in limps and over-limps now have separate defense policies, each calibrated
to its own arriving range. The former union-of-ranges policy made a profile with
a 68.7% after-limp continue target actually continue 91.4% after its narrower
first-in limp. Editing either defense now resets the old solve; cosmetic names
and postflop-only edits still preserve it.

New profiles generated through the app/API default to **adaptive responses from
25% of stack**. At a faced raise-to amount at or above that cutoff, opponents
learn their response instead of applying the ordinary-bet profile. For 150bb,
that means 37.5bb and larger, including shoves. Ordinary profile actions remain
fixed. This cutoff is an explicit modeling assumption, not a measured poker
statistic or a claim that real players respond optimally. Compare alternative
cutoffs before treating a marginal action as robust.

The profile editor exposes the percentage. Blank disables adaptation. The API
accepts `adaptive_from: 0.25` on `/api/preflop/generate`; explicit `null` retains
fixed responses. Rust `generate_profile` returns corrected limp ranges with
adaptation disabled until the caller chooses a threshold.

Leave **HERO off** and your target seat on **Solver** for joint adaptive solves.
HERO mode freezes other seats, so the engine refuses it while unfrozen adaptive
opponents are present. Explicit point locks still take priority; explicitly
frozen seats keep their saved averages. Adaptive seats show a convergence gap
within the fixed ordinary-action rules, while fully fixed/frozen seats retain
their unrestricted bleed measurement. CPU and CUDA use the same distinction.

Old saved games and hand-painted profiles retain their original policies and
load without a conversion. Regenerate old profiles from their intended stats
to obtain the separate limp defenses; preserve custom paint before doing so.
New fields, generation stats and both defense policies round-trip in saved games. Re-solving an
old fixed profile alone does not update its modeling assumptions.

The bundled **Data** archetypes come from online HandHQ cash-game histories
(July 2009), not observations of the user's live 2/2 or 2/5 players. They are
starting assumptions. Postflop station/folder stats affect exported postflop
node locks, but do not change Preflop Lab terminal values. The calibrated
postflop realization model and multiway equity approximation remain limitations;
a small convergence gap establishes a solution to this model, not exact live
poker strategy. See [player types](player_types.md).

## Reproduction and validation

The reproduced line is UTG limp, UTG1 limp, MP limp, HJ fold, CO fold, BTN to act:
8-max, 150bb, opens 7.5/10bb, raise multiples 3/5/7, max raises 2,
limps and all-ins enabled, 10% rake capped at 8.5bb, calibrated realization.
Opponent profiles match the reported table, with BTN on Solver and HERO off.
Frequencies below are combo-weighted within BTN's arriving range.

| Model | Iterations | Fold | Limp | Normal raises | Jam |
|---|---:|---:|---:|---:|---:|
| Original captured solution | 50 | 4.37% | 88.53% | 0.01% | 7.09% |
| limp-fix-only | 100 | 6.74% | 85.71% | 0.00% | 7.542% |
| adaptive25 | 100 | 6.65% | 89.19% | 4.14% | 0.022% |
| adaptive50 | 100 | 6.30% | 89.54% | 4.14% | 0.022% |
| adaptive100 | 100 | 6.30% | 89.54% | 4.14% | 0.022% |
| Adaptive 25%, tighter convergence | 500 | 3.03% | 92.99% | 3.99% | 0.00018% |

At 500 iterations the summed constrained gap was 0.0000833 bb; ATs limped
99.9994% and jammed 0.000386%. The remaining broad limp range is not evidence
that live players should limp this widely: continuation values still use the
approximate postflop model. Some low-reach/near-indifferent frequencies moved
between 100 and 500 iterations even though the overall gap was small.

Validation includes separate first-in/over-limp path regressions, changed-profile
reset behavior, adaptive threshold and point-lock priority, saved-profile
round trips, constrained-gap versus unrestricted-bleed semantics, full CPU tests,
CPU/CUDA strategy equivalence and exact cached-evaluation graph checks. The
night-runner tests also reject unconverged range exports.
