# N15 GPU implementation and matched runtime check

Prepare this implementation while the frozen N15 model awaits its registered
400-reference evaluation. Do not execute GPU tests unless that accuracy gate
passes, and never overlap either research queue or live application work.
The live executable and port 56708 remain untouched.

Keep double precision and the existing anchored legal-pair interface. The
104-feature ridge base is unchanged. Stream the same 104 clipped features
through 16 scalar hidden accumulators (two eight-unit seeds), then add their
averaged, already-shrunk output to the base correction. Center the combined
correction once using the same compatible hand mass. This is algebraically
the sum of the separately centered base and neural corrections.

Fold standardization into weights and biases offline: clip each raw feature
to mean +/- six standard deviations, use weights divided by scale, and
subtract the corresponding mean contribution from hidden biases. Retain
binary64 constants. This removes per-feature division without quantization;
rounding equivalence still requires independent checks. No learned arrays,
gates, precision, feature set or evaluation labels are changed.

Export both serial summaries and N14's warp summaries with the same frozen
model. Run the existing independent physical-hand oracle on each (12 cases
per version, including sparse/off-path cases and 2/3/8-player interfaces).
Require action values within 2e-4 bb of the CPU oracle, its existing pot
accounting checks, and serial-versus-warp action changes below 2e-6 bb.
Larger-game checks validate the approximate heads-up reset, not exact
multiplayer dealing.

Then run three interleaved repeats of ordinary Balanced, N15 serial and N15
warp: 50 warm-up plus 100 timed iterations on the existing 410270-node save.
The ordinary path must reproduce N04's entire saved state exactly. Compare
every serial/warp regret and strategy accumulator with the N14 tolerances
(absolute 1e-6 plus relative 1e-5); inspected strategy probabilities must
agree within 1e-4 and EVs within 2e-5 bb. Each version's repeated saved
states must agree exactly. Record exact equality separately from tolerances.

The target is <=10% median iteration-time overhead versus ordinary Balanced.
Fixed-work runtime and value accuracy do not establish full-game convergence
or accuracy of changed-policy ranges. Those further checks remain required
before recommending adoption. The ten-hour deadline is unchanged.
