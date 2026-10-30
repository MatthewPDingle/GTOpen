# Strict checkpoint comparison for the deferred paging candidate

The candidate has compiled but has **not run on the GPU**. These new checks
prepare its qualification; they are not evidence of a speedup or parity.

The earlier general paging review reported exact checkpoint equality as a
diagnostic while its pass decision used numerical tolerances. The deferred
upload-only optimization has a stronger requirement: every saved scientific
field must match exactly. The new, separate `paging_candidate_review.py`
enforces that requirement without changing the frozen overnight experiment.

It requires exactly the registered iterations 1, 20, 100, 500 and 2000,
convergence below 0.01 bb, finite values, increasing elapsed times and the
predicted integer traffic relation: candidate bytes times six equals baseline
bytes times five. Only elapsed times and the traffic counter may differ.
All other fields, including board weights, entering normalization, every
checkpoint evaluation and every saved hand/action policy, must agree in
canonical JSON. Both files also pass the independent physical-card, frequency,
terminal-probability and chip/rake accounting audit.

This is exact equality of saved JSON values, not a comparison of unsaved
postflop arrays. The separate 160-switch GPU test remains mandatory for
bitwise array and returned-value parity. Source hashes, production-idle and
resource checks, and an uncontended timing comparison also remain required.

CPU-only controls passed on the completed original two-board result, with
a **fabricated** candidate changing only its recorded times and traffic.
Thirteen corruptions were rejected: missing, duplicate, reordered or incomplete
checkpoints; changed intermediate EV or final hand policy; altered weights;
an unexpected field; wrong or unchanged traffic; nonfinite data; backwards
time; and failed convergence. The fabricated times provide no performance
evidence. See `paging-candidate-review-controls.json`.

After real GPU qualification, run from the primary research checkout:

```text
python tools/research/paging_candidate_review.py BASELINE_JSON CANDIDATE_JSON NEW_REVIEW_JSON
```

Use the frozen `paged-two-result.json` baseline (SHA-256
`cf56de577e1c3092e32b04f60637bf8f7f5ecb82d8dfba63bec385f0fdfd2a09`)
and the same subtree/old-two-orbits inputs recorded in `paged-two-freeze.json`.
The checker refuses to overwrite an existing review. It never starts a solve,
modifies a source result or touches the production app.
