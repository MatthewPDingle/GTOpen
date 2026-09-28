# Follow-up: public pot scaling with the original chip-error objective

## Evidence motivating this test

The CPU readback reproduced all saved baseline validation losses within
2.23e-8. Four parallel workers took 5.6-8.1 seconds each; total elapsed time,
including allocated-storage admission, was 134 seconds. It used no GPU.

Pots of 100 bb or more contribute 58.11% of squared prediction error from
19.95% of source weight. The largest-error 1% of postflop rows contribute
23.83% of error. These are equal-dataset means, not population estimates.
Large chip mistakes deserve weight; their concentration is not itself a bug.

More directly useful is how much each model improves on predicting zero
advantage for every legal action. This is a regression reference, not a
recommended poker policy:

| Dataset | Error reduction, pot <10 bb | Error reduction, pot 10-50 bb | Error reduction, pot 200+ bb |
|---|---:|---:|---:|
| Seed 1 BB | 0.016% | 6.939% | 44.002% |
| Seed 1 BTN | 0.087% | 3.204% | 39.770% |
| Seed 2 BB | 1.076% | 6.902% | 48.935% |
| Seed 2 BTN | -0.909% | 3.412% | 37.831% |
| Equal-dataset mean | 0.068% | 5.114% | 42.635% |

The model learns almost no predictive signal in the smallest pots by this
metric. This motivates testing numerical representation of output scale. It
does not establish that loss imbalance caused inaccurate preflop ranges.

The duplicate-input audit cannot settle target noise: only 1,096 of 536,609
postflop training rows repeat an identical visible input/legal menu (0.204%).
Only 18 rows repeat within the same iteration. There are no repeated river
inputs and almost no repeated turn inputs. Do not estimate a global noise
floor from this sparse, selected coverage. A later noise study would need
new repeated-situation samples under explicitly fixed policies.

## Fixed, bounded comparison

Use the same four generation-77 reservoirs, original salted input-disjoint
split, training-only target normalization, original fit seeds, 302/64/64/4
architecture, Adam 0.003, 512 steps and 4,096-row gradient chunks. Preserve all
examples, weights, legal masks and the chip-scale squared-error objective.
No new input features, target clipping, Huber loss, added deals, width search,
fit-budget search or validation-driven changes to the scale formula.

Run three arms on every dataset:

1. Original initialization and original fitting. Require all four saved
   baseline weights and validation losses to reproduce within 1e-7.
2. Zero-output initialization: retain the original seeded hidden layers, but
   set the last layer's weights and biases to zero. Otherwise fit identically.
3. The same zero-output initialization, with output factor
   `g = current_public_pot_bb / 10` postflop and `g = 1` preflop. Use exact
   public pot values from the qualified native-state catalog. All factors
   must be finite and strictly positive.

Zero-output initialization gives arms 2 and 3 the same initial function,
without adding a frozen second network to preserve a random initial output.
Arm 1 remains the practical reference. If initialization itself helps, report
that separately; do not attribute that effect to pot scaling.

For original normalized target `y` and network output `f`, arm 3 predicts
`g*f`. Fit targets `y/g` with weights multiplied by `g^2`, keeping the original
denominator. Then `w*g^2*(f-y/g)^2 = w*(g*f-y)^2`. This changes the parameterized
prediction function and its numerical conditioning, not which chip errors
receive weight. Restore `g*f` before every reported raw-scale metric. The
existing within-input variance constant stays in original units because `g`
is identical within each input/menu group.

At a given information set, multiplying every legal action score by the same
positive factor preserves regret matching, including the all-nonpositive
argmax fallback. Qualify this explicitly with legal masks and ties. This may
avoid extra inference work when obtaining policies, but checkpoint metadata
and policy-evaluation integration still require validation before adoption.

## Controls before looking at the new comparison

- Verify the transformed objective and gradients against direct restored-output
  error on a hand-calculated fixture and real training inputs.
- A factor of one must reproduce the zero-output baseline fit.
- Compare captured and ordinary training on a real, multichunk fixture spanning
  all streets. Use the existing numerical tolerances unless a separately
  documented reason requires a new control version.
- Verify initial predictions are zero for both comparison arms and that the
  output layer receives gradients. Validate finite targets/weights and factor
  bounds before capture.
- Bind sources, controls, catalog, inputs and formula in a new registration
  before any full-dataset candidate fit. Keep original frozen sources intact.

## Metrics and decision

Primary: equal-dataset mean postflop validation MSE in the original normalized
chip units. Report each dataset, street and the five predeclared pot buckets,
including error relative to zero, training loss, runtime and memory. Report
arms 2 and 3 against each other and against the original baseline.

For pot scaling to justify a full-policy training comparison, require at least
1% lower primary loss than **both** baselines, improvement over both in every
dataset, and no increase in the under-50-bb validation loss in any dataset.
The under-50-bb value must combine raw error/mass from the first two buckets,
not average their means. Preserve mixed and negative outcomes. This practical
gate is not a significance test or proof of poker strength.

Use validation only. It is reused tuning data, not fresh confirmation. Keep
the final test closed. Bounds: 30 minutes, 100 MB retained outputs, 8 GB own
CUDA allocation, at most four CPU preparation workers after resource checks.
Respect shared locks, the 800 GB allocated-storage cap and light-desktop GPU
sharing; yield to active solves or heavier workloads.

Before adoption, a promising change still needs separate complete-policy
training and fresh-deal evaluation. Accurate flexible preflop ranges across
positions, stack sizes, bet menus and multiway situations remain unproven.
Production is unchanged, and no process was left running after this audit.

Evidence: `board-later-error-audit-v1-result.json`,
`board-later-error-audit-v1-analysis.json`, and
`BOARD-LATER-ERROR-AUDIT-FINDINGS.md`.
