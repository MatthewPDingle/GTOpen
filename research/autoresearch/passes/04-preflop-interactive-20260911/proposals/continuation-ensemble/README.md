# Coherent particle compression — research candidate

Status: source prepared; no quality or speed result claimed. The live model remains unchanged.

The candidate keeps a fixed equal-weight subset of the existing 1,024 coherent rank particles. Every seat uses the same subset. Each particle awards exactly one shared pot, including ties; averaging those awards retains conservation. This avoids the rejected independent heads-up equity product. It also inherits the source model's independent class prior and imperfect joint card removal: conserving a pot does not establish physical accuracy.

Two predeclared candidate families use 16, 32 or 64 particles:

- **Stratified:** midpoint of equally spaced strata in the original particle sequence.
- **Representative:** greedy selection without replacement, minimizing squared error of the uniform selected mean against the full particle mean. Training features are conditional equities for all 169 hero classes across 32 deterministic synthetic contexts (one through eight opponents, four contexts each), weighted by each hand class's combinatorial mass. Features use only source-model labels. Selection produces one nested 64-particle sequence, with 16/32 prefixes.

The synthetic generator varies strength thresholds, softness, pair/suit/gap preferences and seat distributions. Sixteen separate-seed contexts are development holdouts from the same generator, not an independent test of broad generalization. Historical seven-case physical-MC fixtures and the original BB failure are explicitly **previously seen regressions**. Registered independent cases owned by the quality agent were not read or used for fitting. Candidate sizes/families are frozen before their results.

## Files and execution

In `target/autoresearch/preflop-interactive-20260911`:

```powershell
cargo test -p solver --release --example preflop_ensemble_audit
cargo run -p solver --release --example preflop_ensemble_audit -- T:\Dev\GTOpen > <output.json>
```

Source files: `crates/solver/examples/preflop_ensemble_audit.rs` and `crates/solver/examples/support/continuation_ensemble.rs`. There are no runtime/model-selection changes. Root owns builds and measured runs. Feature storage is 44,302,336 bytes; greedy selection uses roughly 354 million feature products for 64 selections. The example writes JSON to stdout, status to stderr, and does not mutate input artifacts.

## Gates before integrating a preview mode

1. Full ordered 1,024-particle wrapper must match the current evaluator; reduced models must preserve finite values, 2–9-seat pot conservation, ties and zero-opponent behavior. Hero values must not require positive own reach.
2. Measure mean/p95/worst hand equity error against 1,024 particles, plus physical-MC error separately. Inspect premium overlap and the original BB KQo/76s failure even when aggregate errors look good.
3. Solve fixed trees under each candidate and evaluate resulting policies with the full reference. Compare per-hand decisions, continuation rates, full-reference EV/regret and time to a usable navigable spot. Fewer samples alone is not an end-to-end speedup or quality guarantee.
4. If integrated, use an explicit versioned approximation identifier and frozen indices in saved metadata. Keep normal 1,024 behavior available. GPU reduction/normalization must use actual particle count; validate CPU/GPU parity within each new model. Do not silently overwrite existing saves or market the source as a full physical/postflop solution.

Relevant prior evidence: [alternative-models.md](../../../../../multiway-equity-audit/alternative-models.md). The previous normalized-product model conserved pots yet reduced original-BB KQo equity from 20.80% physical MC to 10.59%, which is why conservation alone is insufficient.
