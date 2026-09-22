# Historical root targets are noisy as well as imperfectly fitted

The completed baseline pilot retained 4,992 BB root visits across 169 hand
classes: a median of 22 visits per class, with a range of 7-66. This readback
examines training data only. It does not access new test outcomes or change a
candidate.

Subtracting the fold advantage from each other action's advantage cancels the
shared state-value baseline. Across classes, median sample standard deviations
of those historical paired return differences were:

| Difference | Median sample standard deviation |
|---|---:|
| Call minus fold | 28.86 bb |
| Raise minus fold | 47.01 bb |
| Jam minus fold | 152.15 bb |

For context, median absolute historical means were 4.03, 7.71 and 32.70 bb,
respectively. The median standard-deviation divided by square-root-count ratios
were 5.02, 8.38 and 29.12 bb. These ratios are **not confidence intervals**:
strategies changed during collection, multiple visits share update policies,
and reservoir sampling does not make adaptive historical labels independent
measurements of the final policy's action EVs.

The evidence supports treating target variability separately from neural fitting
error. A direct preflop table removes regression error against its retained
means; it does not turn those means into precise equilibrium values. The dense
trial tests more fresh deals under the same fitting setup. Its completed
reservoir will receive the same descriptive readback, followed by the already
registered fresh-deal strength test.

Source: `sampled-physical-pilot-root-noise-v1-result.json`, with exact source
checkpoint, reservoir and analysis-source hashes. The old reservoir is unchanged.
No production or preview changes were made.
