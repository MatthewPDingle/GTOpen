# Native visit-preserving river transport control

Prepared before execution, 2026-09-28. Scope: a separate research walker and
bounded CPU controls; no training, model fitting, deployment or full-policy
performance claim. Qualified sources and data stay unchanged.

The candidate retains the existing all-in estimator and every sampled branch,
decision record, and RNG draw. Only after visiting descendants may an updater
river decision replace its complete action vector. One policy-weighted mean
centers all regrets and is returned to ancestors. No source importance weight
is applied within the walker.

Use the 12 existing native pilot exports. Define positive deterministic
hand-dependent fixture probabilities on each export's visible keys and uniform
probabilities elsewhere. This fully specified test policy is not claimed to
be the played learned policy. A second variant zeros the first updater own-
history action leading to the target, redistributing over other legal actions;
the sampler must still visit that branch counterfactually. Cases without such
an ancestor retain the original policy and are labeled accordingly.

For each fixture, compute exact values with the qualified exporter reader and
actual registered entry ranges, retaining all 990 opponent pairs. Verify
importance weighting under both entry-proportional and a positive unequal
proposal: the weighted mean difference between the exact common vector and
pair-conditional vectors must vanish after opponent-path weighting. Test a
deliberately doubled source weight; it must fail whenever the nontrivial
control has a detectable difference. Here "doubled" means applying the
importance ratio twice to the update/return, and testing against the correct
weighted expectation (not multiplying an already-zero residual by a constant).
Entry-proportional proposals may have zero mass where the entry range is zero;
require proposal support everywhere the target distribution has support.
Do not insert the weight into payoffs.

The native harness receives the exact context, visible-key policy table and
full action vector. It validates canonical keys, legal arities, probabilities,
target identity and legal vector padding before walking. For pair indices
0, 495, 989 and seeds 9282801 through 9282804, compare the unchanged sampler,
candidate with replacement disabled, and enabled candidate from the preflop
root, for both updater seats. Also start at the target's reconstructed native
state for its updater to guarantee direct callback coverage even if earlier
sampled opponent actions do not reach that particular history.

Require disabled root values/records to equal the old sampler exactly.
Enabled/disabled visits, tags, policy query sequence, and final RNG must match.
Check every complete regret vector and root return independently from the
record-parent graph and the declared exact vector. Descendant records must
remain unchanged; ancestor differences must follow the action through which
the target was reached, including sampled opponent ancestors. Assert exact
replacement counts and unchanged opponent records. No claim that 12 seeds
establish an empirical convergence rate or a new data-quality result.

Retain control input/result hashes and registered source/binary hashes. Negative
requests must reject invalid arity, nonfinite/illegal vector contents, wrong
context identity, wrong policy identity, and duplicate visible keys. Preserve
failures; version corrections after execution. This gate qualifies a single
target substitution, not simultaneous nested replacements, every source of
chance, or an end-to-end trainer. Those remain later gates.

CPU only; <=600 seconds, <=100 MB retained new evidence, <=60 seconds per native
invocation, no changes to historical data. Use four independent CPU workers
only if other workloads permit; otherwise one. Existing 717.79 GB allocation
plus this allowance remains below the 800 GB cap. Heavy current GPU use is
untouched. The planned full training integration must separately measure cost.
