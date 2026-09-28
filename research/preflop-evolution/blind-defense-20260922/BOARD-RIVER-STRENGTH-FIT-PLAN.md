# Next experiment: explicit visible river strength with learned context

## Evidence and interpretation

The river audit checked 180,260 eligible training/validation records. Every
Call-minus-Fold target matched a native win, tie or loss endpoint to within
2.85e-14 bb. The native known-deal controls also passed. A simple payout-unit
or common-baseline error is therefore not supported by these records. The
audit does not independently validate the dealt opponent or its distribution.

On 31,995 validation records, the saved network had mean squared contrast error
3,866.710 bb squared. The visible-only uniform-opponent reference had 7,817.001,
102.16% worse. Replacing the learned prediction with uniform equity is rejected.

However, the predeclared pot-size breakdown identified a consistent weakness:

| Current pot | Network error | Uniform reference error | Reference change |
|---|---:|---:|---:|
| Under 10 bb | 23.181 | 10.673 | -53.96% |
| 10-50 bb | 273.150 | 237.203 | -13.16% |
| 50-100 bb | 1,512.238 | 2,045.585 | +35.27% |
| 100-200 bb | 3,188.160 | 4,296.835 | +34.77% |
| 200+ bb | 10,593.273 | 22,900.299 | +116.18% |

Each entry is an equal-dataset mean in original bb-squared units, not the
earlier full-action normalized loss. Both smaller-pot bands improved in all
four datasets. The under-10-bb validation counts are only 211-258 per dataset,
so this is exploratory evidence, not precise population accuracy. The model
is worse than a zero-difference prediction in three of those four small cells.

The uniform reference becomes too optimistic in larger pots: e.g. in Run A BB's
200+ bb bucket its average Call-minus-Fold prediction is +86.91 bb versus an
observed +2.30 bb and the network's +1.35 bb. Incoming ranges and betting
selection matter. This diagnostic does not prove the network models those
effects correctly, but it argues against discarding learned context.

The next hypothesis is that an explicit, physically valid river-strength input
can help the network learn the relationship while retaining its ability to
condition on the full public history. This is a targeted experiment, not a new
definition of the broader goal of accurate flexible preflop play.

## Fixed data and three comparison arms

Use the same four generation-77 reservoirs, original input-disjoint partitions,
train-only scales, original source weights, 512 steps, full-gradient objective,
Adam 0.003, hidden widths 64/64 and original saved seeds. No tuning those values
after seeing this outcome. No final-test inference or new simulation deals.

1. **Original:** reproduce the existing 302-input fit and its saved validation
   scores within the previous 1e-7 tolerance before interpreting either change.
2. **Public geometry control:** append the five features below with E fixed at
   0.5. This supplies the relevant pot/price arithmetic without hand strength.
3. **Visible strength:** append the same five features using exact equity E
   against all 990 legal, equally weighted opponent pairs.

Append features only to river decisions with legal Fold and Call actions;
every other decision receives five zeroes. Let P be current pot, C incremental
call, R rake on P+C, and T be starting postflop pot plus twice the initial
effective stack for the native branch. The five appended values are:

- 1 (eligible-state indicator).
- (P+C-R)/T (net matched pot fraction).
- C/T (incremental call fraction).
- 2E-1 (centered hand strength; zero in geometry control).
- [E*(P+C-R)-C]/T (uniform-reference value fraction).

Both added-input arms retain the original weights for all old inputs and all
later layers; initialize the five new input columns to zero. Their initial
function must match the original exactly. Both have the same input width (307)
and capacity, so the strength comparison is not confounded by parameter count.
No residual output correction or direct policy replacement is applied.

The reference equity is a deterministic redundant function of the acting
player's visible cards. It never uses actual sampled opponent cards, targets,
deal outcomes, future cards, learned opponent policies or Wizard data. The
uniform reference remains an input that the network may discount in context.

## Controls and implementation constraints

- Preserve the native helper and completed diagnostic sources unchanged.
- Use the qualified native 990-pair evaluator in bounded batches with up to
  16 CPU workers when available. Canonical reuse may ignore ordering within
  the two hole cards and within the five-card board; it must preserve those
  groups. Confirm result identity against the already qualified fixtures.
- Decode and enumerate only training and validation rows. Do not create test
  features or predictions. Existing split-proof reconstruction may inspect
  loaded arrays as before; do not describe this as never loading test targets.
- Cache only visible-card counts needed by the experiment, with source hashes
  and strict bounds. No bulky copied reservoirs or hidden-card cache.
- Verify exact original split, grouped target and weight reconstruction. The
  five additions must be identical for equal original visible inputs.
- Verify zero additions outside eligible river situations, legal menu joins,
  pot/stack accounting, feature bounds and initial-function identity.
- For each new arm, compare eager and CUDA-captured gradients/updates on a
  fixed training-only prefix. The original fit must reproduce before evaluating
  changed fits. No changed loss weighting or output normalization.
- Bind source, checkpoint, catalog, preparation and control hashes before the
  registered full run. Preserve unsuccessful results rather than overwriting.

## Reporting and advancement gate

Report all three arms for each dataset and equal-dataset means:

- Original weighted legal-action normalized MSE: all postflop and each street.
- River Call-minus-Fold MSE in original bb squared, with source-weight sum as
  denominator, overall and in the five existing pot buckets.
- Pooled under-50-bb river contrast MSE within each dataset; combine the two
  bands by their actual source-weight mass, not an unweighted bucket average.
- Training loss, final runtime, memory and retained bytes.

An input candidate advances to a separately specified policy-training test
only if all of the following hold on validation:

1. Its equal-dataset mean river contrast error is at least 1% below both the
   original and geometry-only control, with lower error than original in all
   four datasets.
2. Its mean pooled under-50-bb river contrast error is at least 5% below both
   controls, without a regression versus original in any dataset.
3. Mean full-postflop normalized error does not increase versus original, and
   no individual dataset increases by more than 1%.

These are prospective research advancement rules, not statistical confirmation
or a production adoption criterion. The validation data has already informed
this hypothesis. Any promising result still needs fresh simulated evaluation
of complete interacting policies, including whether preflop action values and
cross-run consistency improve. No new benchmark accuracy is established here.

## Resources and broader scope

The completed diagnostic used four CPU preparation workers and 16 native
enumeration workers, evaluated 25,758,810 opponent pairs, and finished in 2.19
minutes including the global storage scan. Enumerating visible river strength
is inexpensive in this bounded test; preserve equivalent visibility and runtime
checks before using it in a live training loop.

Keep shared research locks, production-activity checks, the 800 GB allocated
storage cap, and light-desktop GPU sharing. Bound the new study to 30 minutes,
8 GB own GPU memory and 100 MB retained outputs, including any feature cache.
Prepare independent inputs in parallel, train on one GPU, and yield to active
solves or heavier competing workloads. Production remains unchanged.

This tests a single 200bb heads-up subtree. Coverage of other stacks, positions,
sizes, incoming ranges, full preflop interactions and multiway play remains
necessary. A river-specific improvement would be one component of that work,
not completion of the preflop research goal.
