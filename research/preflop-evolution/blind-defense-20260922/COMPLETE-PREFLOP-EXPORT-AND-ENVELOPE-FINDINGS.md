# Complete policy exports passed; the simple reach proposal is not worth a new run

The four frozen 110-model banks now have complete preflop policy exports. CPU
and CUDA agree on all 699 supported queries per bank, covering all five decision
points with the correct own-action histories. Generations 0..109 were included
with weights 1..110; unplayed generation 110 was excluded. No model was trained,
new poker deal drawn, historical accuracy result changed or app modified.

The next cheap calculation was negative: concentrating evaluation only by the
amount of preflop reach into postflop does not narrow the conservative uncertainty
enough. Do not launch a new large evaluation using this proposal.

## Export and native accounting checks

Maximum CPU/CUDA policy difference was 3.47e-18. Own-reach arrays matched exactly;
no exported row had zero own reach. The original model catalog, checkpoint
identities and inference implementation were retained. Reservoirs were not
restored merely to read frozen models.

The export took 325.39 seconds including a fresh global storage inventory. CPU
reference inference took 17.5-20.5 seconds per bank, overlapping GPU preparation
and inference. Own CUDA peak allocation/reservation was 83.89/96.47 MB. Retained
exports occupy 0.53 MB logical / 0.26 MB allocated. Admission measured 740.159 GB
globally allocated research storage, below the 800 GB cap. Light desktop sharing
and production-priority guards remained enabled.

A separate native accounting control reused one retained training deal and all
eight crossed frozen profiles. Forcing only preflop decisions exposed the three
existing postflop continuation values per profile. Independently propagated
preflop reach and actual-investment fold/all-in accounting recombined these into
the original native values, with maximum error 8.89e-16. No postflop policy was
changed. This is a decomposition check, not a broad accuracy test or a rigorous
floating-point error bound.

An independent closed-form readback checked 600 files, including all 440 played
model references, and recomputed the proposal quantities from the CPU exports.
Its maximum arithmetic disagreement was 2.85e-14.

## Why stop this precision approach here

Under the original class-pair distribution, about 42.0-42.3% of A profiles and
47.3-48.7% of B profiles reach postflop. A generic full-stack postflop bound still
has to allow large losses and gains on those branches. Taking the maximum width
needed for all eight contrasts gives a candidate half-width Z of **249.600 bb**.

That improves on the generic 400.5 bb gain half-width but is worse than the
already available shared-policy-mixture planning bound of 193.198 bb. At 16,384
observations, the candidate's empirical-Bernstein additive term alone would be
about **0.459 bb per entry**, before adding the variance-dependent term. The
observed historical gain estimates are much smaller. This is an opportunity-cost
decision, not a proof that all importance sampling or stratification is useless.

The center and width calculations are floating-point planning quantities. No
new proposal sampler, numerical-bound guarantee or confidence interval was
adopted, and the original study's inconclusive primary intervals remain intact.
Do not tune a sampler against its historical test outcomes or keep extending a
test until it appears positive.

## Next priority

Return to STACK-CONTEXT-PLAN.md. The existing 60-number public-economics encoder
and seven native stack-geometry fixtures are ready to reuse. The next missing
piece is an explicit context-aware observation/table/checkpoint contract for a
shared model, followed by matched small reference contexts and a limited training
pilot. Keep 60 and 150 bb outside fitting and tuning. Geometry checks at those
depths do not constitute trained or validated ranges.

Do not copy the 200 bb study's learned incoming ranges into every depth and call
that a full-game solution. A fixed-prior continuation diagnostic and a full
preflop model are separate milestones. Equal-stack heads-up is the initial
scope; other positions, varied menus, unequal stacks and multiway remain open.

The faster preparation pipelines and two-arm scheduling remain qualified for
future versioned work. The slower river treatment has promising point estimates
but has not earned an accuracy or production promotion. No new push/deployment.

## Evidence

- complete-preflop-bank-export-control-v1-registration.json
- complete-preflop-bank-export-control-v1-result.json
- preflop-proposal-envelope-screen-v1-registration.json
- preflop-proposal-envelope-screen-v1-result.json
- preflop-export-envelope-readback-v1.json
- COMPLETE-PREFLOP-BANK-EXPORT-PLAN.md
- PREFLOP-PROPOSAL-ENVELOPE-SCREEN-PLAN.md
