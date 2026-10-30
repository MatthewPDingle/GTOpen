# Shared native query export qualification

Prepared before execution, 2026-09-28. The actual-policy pilot matched all 67
visited river targets to the current native action trace, but measured stages
cost about 20x the baseline. Of 28.71 added stage seconds, Python union merging
used 7.70 seconds, preparation 8.38 seconds, export 5.77 seconds, values 6.08
seconds and neural inference 0.78 seconds. Full validation was timed separately.
These are stage sums, not end-to-end training or convergence measurements.

Candidate: a NEW native exporter accepts up to 32 identified river targets and
builds a single canonical visible-query table. Public trees, every legal action,
all 990 opponent pairs, native payoffs and actual paths remain unchanged.
The batch keeps separate per-target trees, sharing only query data and policy
preparation. No opponent/future card is added to a policy input. Preserve the
already-executed single-target exporter and all previous evidence.

A separate new multi-target value reader validates the shared policy/entry
binding once, then uses the same per-target bottom-up conditional expectation.
It avoids re-hashing a whole union policy for every target. Native structural
and independent scalar path checks remain part of qualification; compare every
posterior, pair-conditional vector and full regret vector against the frozen
single-target reader. Shared validation is valid only within one bound batch.

Use exactly the eight completed deal/model cases from the actual-policy cost
pilot. The target list is reconstructed from original positive river records,
in their existing order; no case or target is selected by label or timing.
Expand and remap each batch target to its original single-target document and
require exact equality of geometry, pairs, paths, action menus, node identities
and native terminal values. Every reference visible observation, feature and
own-history link must match after remapping. The union may not omit or invent
observations. Bind each returned target to its request identity.

Infer the same registered generation-77 CPU policy once per native union.
Require every target slice to agree with the saved pilot probabilities within
1e-10 and retain identical zero/nonzero support. Derive full conditional values
and require each new regret vector to match the previous overlay within 1e-8 bb.
The qualified scalar validator checks each returned tree independently too.

Measure complete stages, including file read/parsing, native export, preparation,
inference and evaluation, separately from equivalence checks and evidence
archival. Repeat the old per-target native export plus Python merge path once
in this same run for each case, alternating old/new order by case index. Include
fresh export work for both paths, no cross-policy cached-export advantage. Compare
the same downstream policy/value path. Retain all eight comparisons. This is
an engineering timing control on reused inputs, not evidence of better poker.

Malformed batch requests: empty, duplicate targets, too many targets, wrong
format and a target key that is not a river decision must reject without an
output file. At most 250,000 unique queries, 500,000 total tree nodes and 64 MB
per native output. Sequential case comparisons, at most four independent old
export processes, reduced when necessary to reserve each output's full bound
within the remaining storage allowance. No GPU, learning, production changes,
pushes or deletions.
Maximum 900 seconds and 512 MB additional evidence under the existing global
800 GB cap; the prior inventory plus all recent bounded allocations is below
720 GB. Preserve failures and version corrections rather than editing an
executed source or quietly removing an unfavorable case.
