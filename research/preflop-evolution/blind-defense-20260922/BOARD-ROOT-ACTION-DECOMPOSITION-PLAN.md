# Next diagnostic: separate root actions using the retained evaluation

Chosen after the completed board-root experiment and its saved-history review.
This is exploratory reuse of the existing 65,536-deal evaluation, not a fresh
confirmatory test, a sample extension, or a replacement for its inconclusive
registered payoff comparisons.

## Question

Do the disputed root actions differ materially in value under the actual
complete averaged policies, or are they close choices? Keep each player's later
behavior fixed while evaluating each legal BB root action. Compare all 169 hand
classes for every originally registered crossed profile, including unfavorable
and low-coverage cases.

## Reuse and correctness control

The existing native evaluator traverses all legal action paths but emits mixed
root values. The retained archives contain the physical deals, conditional
preflop all-in inputs, observation identities, and complete-bank probabilities.
First verify that all of these can be reconstructed from the authenticated
archive without another model call. Do not fall back to a single generation.

Construct four copies of each saved crossed profile. In each copy, replace only
the BB root probability row with one of fold/call/raise/jam. Preserve every later
probability, query identity, game setting, conditional-equity input and deal.
The eight original crossed profiles produce 32 forced profiles, within the
existing native evaluator's limit. Initial all-in equity remains conditioned on
the private cards; ordinary postflop outcomes still use the saved sampled board.

Before a full replay, qualify two fixed archived batches: test-000000 and
test-032768, covering the two retained evaluation attempts. Authenticate their
checkpoint routes, manifests and payloads. Reconstruct the original profiles
and reproduce their saved mixed values. For every deal/profile, require that
the original root probabilities times the four forced-action values reproduce
the saved mixed value for both players and expected rake. Keep the native
forward-cashflow and pot-conservation checks. Test that a changed non-root row,
wrong actor, illegal root identity or mismatched input is rejected by the adapter.

Do not change the frozen evaluator or its registered binary. If retained inputs
are insufficient, document that limit and design a new version explicitly.

## Interpretation limits

The diagnostic changes only the root decision. It is not a full best response;
continuation play can itself be poor or weakly supported. Report conditional hand
counts, all action-value estimates and paired differences. The archive retains
aggregate zero-reach counts and hashes of support vectors, not the numeric
per-observation support vectors themselves. Do not invent per-hand support from
those hashes or mistake the number of evaluation hands for training coverage.
Preserve exact preflop and sampled postflop distinctions.

Any action chosen by maximizing this reused sample has selection bias. Do not
report such a maximizer as a verified exploitability bound or present post-hoc
intervals as registered discoveries. Use the outcome to formulate a separate
fresh validation question. Do not overwrite or reinterpret the old eight tests.

## Resource use and retention

No GPU inference or training is planned. Start the two-batch control with bounded
CPU work, then qualify a faster worker count on the same inputs before any full
replay. Respect active user solves and heavier workloads; light desktop activity
can coexist. Use unique owned scratch directories and preserve all old evidence.
Retain compact action values and input hashes rather than duplicate the full
policy archives. Measure control output, budget the full replay under the global
800 GB allocation ceiling, and set a bounded deadline before launch. No full
replay is authorized by a readiness flag alone; the control must pass first.
