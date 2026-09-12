# Next candidate: pair-outcome control variate with bounded GPU storage

The earlier reference-policy CV required 12.20 GB of extra storage on the
large fixture and slowed the small fixture. The normalized-regret optimizer
also failed its screen. Neither changes the need to qualify conditional play.

Proposed estimator, derived from the fixed canonical 1,024-particle table:

- For hero class h and each live opponent q, let x_q(s) be the particle's
  lower-ranked opponent mass plus half its tied mass, using a normalized
  opponent range. Let mu_q be its exact mean across the canonical table.
- Precompute a 169-by-169 pair-outcome matrix directly from that same table.
  Multiplying this matrix by the current normalized opponent range gives mu.
  **Do not substitute the physical heads-up equity cache:** its expectation
  differs and would bias the correction.
- Set b_q to the product of mu_j for other live opponents j != q (fixed
  coefficient 1; no fitted or adaptive coefficient in the first trial).
- Replace each sampled multiway share f(s) by
  `f(s) - sum_q b_q * (x_q(s) - mu_q)` during research learning only.
  For fixed ranges the correction has zero canonical mean, because each x_q
  has mean mu_q. Uniform cyclic sampling preserves that expectation. This
  does not guarantee lower variance or faster convergence; test both.
- Preserve the existing tie-share quadrature for f, folded-opponent reach,
  investments, rake, calibrated HU leaves, and standard regret updates.
  Never clip corrected samples to [0,1], which would invalidate the mean.

Storage design: one pair table plus one 169-float mean vector per existing
multiway union reach slot, rather than per terminal and per traverser. The
observed 760,578-slot fixture requires about 514.3 MB plus small kernel state,
well below the earlier 12.20 GB plan. This is a calculated storage estimate,
not yet an allocated or timed result. Explicitly cap added storage at 1 GiB
and refuse unsupported/minimal-metadata or combined research modes before
learning. Allocation failure must return an error without touching the server.

Implementation path: use `d_mw_blocks`, `d_mw_work`, `mw_spans`, and
`d_mw_slots` to project current reach vectors once per traverser. The new
terminal kernel can reuse the existing CDFs, lower/upper indices, compact
mapping, and prepared terminal probabilities. Refresh means on every learning
terminal call; active-gate transitions must never expose stale cached means.
Keep full accuracy checks on the existing canonical terminal kernel. Explicit
learning/evaluation state is needed so CUDA graph capture preserves that split.

Implementation details to preserve:

- Store pair means in opponent-class-major order so adjacent hero lanes read
  adjacent matrix entries. A block can share the normalized opponent vector
  while each hero lane computes one dot product. Write means by union slot;
  existing compact CDF mapping remains separate.
- The prepared terminal kernel already loads each opponent's lower and tied
  CDF mass for the tie quadrature. Reuse those loads for the additive control.
  Compute each b_q without division by mu_q, since means can be zero.
- Set an explicit CV learning flag from `research_tables_select`. Learning
  graphs capture the corrected path; full evaluation graphs capture the native
  path. Particle count alone cannot distinguish full-particle learning tests
  from full accuracy evaluation. Retain stable table/cache allocations.
- Use the existing normalized/raw reach data appropriately in the projection;
  the first prototype may require prepared normalized metadata and refuse
  unsupported modes explicitly. Zero/inactive slots and their later reactivation
  need direct tests. No per-terminal or per-traverser reference-value archive.

Validation before a large learning trial:

1. Pair-table symmetry/complement, self-tie values, and agreement with direct
   canonical per-particle means for nonuniform ranges.
2. GPU full-1,024 correction cancels within registered floating-point tolerance;
   zero reach, mixed fixed constraints, folded players, pot/investment units,
   and compact/union address mapping remain correct.
3. Numerical variance screen with fixed ranges: full cyclic average remains
   unbiased, report variance ratios by hand/fixture rather than only a pooled
   favorable number. Do not tune coefficients using the qualification seeds.
4. Eager/captured learning agreement and full CPU/GPU final-value agreement on
   a small fixture. CPU work is only independent correctness reference.
5. Same six-player gamma15/64 seeds 42 and 314159, controls off/on, limit 1,000,
   checks every 25, target 0.005 bb twice. Register a go/no-go runtime/variance
   gate before running. If passed, apply the unchanged large global and all-27
   conditional gates, with actual memory/time measurement and saved-file audit.

This plan is not implemented or validated yet. No claimed speedup or deployment.
