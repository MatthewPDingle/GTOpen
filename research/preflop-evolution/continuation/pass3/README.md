# Saved-game continuation validation — pass 3

This is an independent test of the **unchanged joint-v1 research candidate**
against raw equity, static realization and the current calibrated model.
**Completed: all 150 references met the target.** The frozen joint candidate
has 3.018%-pot mean error versus 4.810% static and 4.951% calibrated, with
positive paired aggregate improvement intervals in this sample. However,
calibrated is better in both $2/5 3-bet/call fixtures. See [the complete results
and limitations](RESULTS.md); the improvement is not universal.

Production continuation pricing is unchanged. Every reference in this pass is
validation data; none is used to tune or refit the candidate.

## What is being tested

The experiment reads the user's current saved $2/2 and $2/5 configuration files
once during preparation and freezes their fields and SHA256 hashes. It derives
these four heads-up flop situations from the smallest saved opening and
re-raising sizes, with no antes:

| Saved game | Preflop line | Pot, bb | Stack behind, bb | SPR | Rake | Cap, bb |
|---|---|---:|---:|---:|---:|---:|
| $2/2, 150 bb | MP limp-calls BTN raise to 6 bb; blinds fold | 14 | 144 | 10.29 | 10% | 8.5 |
| $2/2, 150 bb | BTN opens 6 bb, BB raises to 18 bb, BTN calls; SB folds | 37 | 132 | 3.57 | 10% | 8.5 |
| $2/5, 200 bb | MP limp-calls BTN raise to 3 bb; blinds fold | 7.4 | 197 | 26.62 | 5% | 2.2 |
| $2/5, 200 bb | BTN opens 3 bb, BB raises to 9 bb, BTN calls; SB folds | 18.4 | 191 | 10.38 | 5% | 2.2 |

The flop ranges come from two existing saved $2/2 reports: MP limp/call versus
BTN isolation and BB 3-bet versus BTN call. These fractional reaching ranges
were not in the joint-v1 fitting corpus. Their exact text and source-file
hashes are frozen in `manifest.json`.

**They are transported ranges**, held fixed to test the valuation models on
new range shapes. They were not re-solved for today's opening sizes or for
$2/5. Their originating reports used older preflop modeling assumptions. This
experiment therefore tests realistic application inputs, not a claim that these
are the correctly solved current ranges. No private hand histories or live
session state are needed to reproduce the reference solves.

Each situation is evaluated with either 50%-pot or 75%-pot bets, on every
street, plus one 100%-pot raise per street. Both players use the same menu.
All-in is not added as a separate option; the engine's normal near-stack
threshold still applies. Full turn and river runouts are enumerated. These
are two restricted action abstractions, not exhaustive full-game solutions.

Two additional controls repeat each game's 50%-bet isolation case at zero
rake, holding everything else fixed. They help distinguish expected rake from
the calibrated model's embedded value reduction. They are reported separately
from the eight primary raked configurations.

## Sampling, precision and frozen decisions

The reference set contains **150 solves**: 15 canonical flops × 10 configurations.
All 35 previously examined pass-one/pass-two boards are excluded. The target
population is the remaining **1,720 canonical flops**, not the previous holdout.

The new draw chooses three boards uniformly without replacement in each of
five pairedness/suit strata: paired rainbow, paired two-tone, unpaired rainbow,
unpaired two-tone and unpaired monotone. The fixed SHA256 ordering and seed
are recorded before collection. Paired includes trips. Suit multiplicity,
compatible hand-pair mass and inverse inclusion probability supply each board's
weight. Both ranges must use suit-symmetric hand classes; suit-specific combos
are rejected because canonical-board multiplicities would then be invalid.
The expectation is the ratio of weighted sums within a configuration.

Postflop values are aggregated by each hand's reach multiplied by compatible
opponent mass. Hand counts alone would give incorrect weights. Preflop model
predictions only use the ranges and the starting pot, stack and rake settings;
they never receive the sampled board or board-conditioned equity.

The primary metric is mean absolute error of each configuration's **weighted
preflop value expectation**, in percent of its starting pot, averaged equally
across the eight raked configurations and both players. Per-configuration bb
errors are also retained. This avoids giving the largest pot all the weight.
It is not mean per-flop prediction error: the preflop estimates intentionally
cannot know the next flop.

Paired 95% intervals resample boards within strata 2,000 times, keeping the
same board's results together across all configurations and all models. Three
boards per stratum is a small sample; intervals are conditional on this
candidate, these fixed ranges and these action abstractions. They do not
include model fitting uncertainty, uncertainty about range construction, or the
remaining numerical error at the reference stopping threshold.

References stop at a 0.3%-pot best-response gap, checked every 25 iterations,
with a fixed 750-iteration maximum. Unconverged, nonfinite or provenance-mixed
checkpoints fail validation; they are never silently dropped. No extra boards,
parameter tuning or outcome-based stopping is allowed after seeing outcomes.
Two independent workers use four CPU threads each. Their summed job times are
not an elapsed-time benchmark because work overlaps.

## Reproduce

```powershell
# Preparation requires the private scenario/report source files once.
python tools/research/continuation_saved.py prepare
cargo build --release -p solver --example continuation_saved
python tools/research/continuation_saved.py run
python -m unittest discover -s tools/research -p test_continuation_saved.py -v

# A complete public corpus can be re-evaluated without the native executable.
python tools/research/continuation_saved.py report
```

`prepare` retains and verifies an existing frozen manifest. Resume requires
the same executable and equity/calibration caches. The accepted executable's
source example is retained as `recorded-example.rs`; binary/cache hashes are
embedded in every checkpoint. The model artifact remains the existing
`../pass2/joint-v1.json` with SHA256
`19afc4bc76c1aac837654e233639a1bfac6e1450b3a9ae526ac6e2871b8562a7`.

See `progress.json` / `progress.png` for collection progress. Final numerical
results and limitations are in `evaluation.json` and the accompanying charts.
The study does not promote or install the candidate.

`independent-review.json` records an independent reproduction of the weighted
metrics, bootstrap intervals and all 150 compatible hand-pair masses.
