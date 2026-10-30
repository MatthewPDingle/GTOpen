# Native two-stage posterior64 timing and equivalence

Prepared before execution, 2026-09-28. The preceding v2 control passed all
eight retained TRAIN cases with exact posteriors, a correct 64-draw sample
mean and 38.989% fewer prepared queries. Its v1 preflight failed on a Windows
manifest separator before computation; both versions remain preserved.

Use the same eight cases, policies and target ordering. K=64, replacement
sampling and identity-bound seeds are unchanged. New hu_river_two_stage_v1
has separate explicit history and selected modes. History emits complete
990-pair actual paths with no future tree. Selected emits complete action
trees for an explicit sorted unique list of <=64 compatible opponent pairs.
No existing native exporter changes. No new opponent information enters the
model's visible inputs. Preserve the exact preflop/board-root policy overrides.

For each case, compare a fresh native exhaustive shared export, preparation,
CPU inference and exact evaluation to a fresh two-stage path. History export,
parsing, preparation, inference, posterior calculation, sample draws, selected
export, parsing, preparation, inference and mean-value evaluation all count
in the candidate elapsed time. Alternate full/new order by case index. The
second stage may repeat history preparation; count it rather than claiming
the projection as a speed result. Exclude only independent qualification and
artifact hashing. Preserve all timings, including unfavorable cases.

Require full reference policy to match previously retained probabilities at
1e-10 and identical support. Remap every new visible query/history to the full
native query table and require exact observation equality. Complete history
pair paths must equal reference paths. Each selected tree must exactly match
its reference pair's nodes, legal actions, children, geometry, payoffs and
showdown outcome after index remapping. Check posterior and sampled-pair
identities against the preceding control. Each selected action vector and
regret mean must agree within 1e-8 bb. Also retain source/query/policy binding
and distinct target identities. This is training-target engineering, not a
fresh range-quality test or a global speed estimate.

Reject malformed mode, history-with-selection, missing/empty/oversized selected
list, duplicate/unsorted pairs, blocked cards, repeated cards, out-of-domain
cards and duplicate targets, without creating output. The value reader must
reject mismatched draw-card sets and missing probabilities. Preserve draw
multiplicity, including deliberate uneven repeats.

CPU only, one BLAS thread, sequential paired cases, 300 seconds, 384 MB new
raw evidence, native maximum 64 MB/output and 250k queries/500k nodes. Require
24 GB free RAM and idle production; no deployment, push, cleanup, training or
evaluation-data reuse. Under the last global inventory and bounded additions
this remains below 721 GB of the 800 GB allocated research cap. Seal inputs
before running and retain output hashes. Any failed attempt remains immutable.

If correctness passes and aggregate complete generation time improves, retain
the implementation for a bounded actual weighted-ingestion/training pilot.
It may still be slower than the original one-opponent trainer; measure that
tradeoff in time-to-quality, not merely against exhaustive enumeration.
