# Candidate: route repeated played-bank range-table checks

Prepared 1 October 2026 while the original matched-stack evaluation continues.
This separate candidate is not imported by the live trainer, evaluator, reader
or production. No registered input, gate, model selection or budget changed.

## Change

`PlayedBank.average` originally applies each generation's preflop overlays to
all observations, including postflop observations those overlays cannot change.
The earlier `CurrentPolicy.prepare` router does not remove that separate loop.

`stack_context_played_bank_routed_v1.py` keeps the original constructor and
complete first feature/history preparation. It computes preflop indices once,
applies each generation's overlays to those rows in their original order,
and maps results back to the original row indices. It accepts only the current
weighted preflop, exact BTN and board-root overlay types. A future overlay
contract requires separate qualification.

The network calculations, every played generation, actor-specific weights,
per-generation own-history reach, accumulation order and unsupported-row
uniform fallback are copied unchanged. This is routing work, not a smaller
model bank or altered poker policy.

## Completed software controls

The CPU-only check used existing two-model synthetic routing fixtures at all
seven depths and both 362/387 input widths. All 14 comparisons had bit-identical
probabilities and own-reach denominators against the original bank. They also
matched the earlier retained CPU reference within its unchanged 1e-10 tolerance.
Both versions rejected all 154 malformed query controls. All 166 consumed input
identities were authenticated again after the run. Control runtime was 15.141
seconds; that is test duration, not a speedup benchmark.

Below are overlay row visits during valid comparisons, including the original
complete first preparation. They count work routed away; they do not measure
elapsed-time savings or actual 64-generation throughput.

| Inputs | Stack (bb) | Query rows | Original overlay row visits | Candidate visits |
|---:|---:|---:|---:|---:|
| 362 | 20 | 296 | 2368 | 640 |
| 362 | 40 | 526 | 4208 | 1112 |
| 362 | 60 | 622 | 0 | 0 |
| 362 | 100 | 798 | 6384 | 1656 |
| 362 | 150 | 846 | 0 | 0 |
| 362 | 200 | 910 | 7280 | 1880 |
| 362 | 400 | 1030 | 8240 | 2120 |
| 387 | 20 | 296 | 2368 | 640 |
| 387 | 40 | 526 | 4208 | 1112 |
| 387 | 60 | 622 | 0 | 0 |
| 387 | 100 | 798 | 6384 | 1656 |
| 387 | 150 | 846 | 0 | 0 |
| 387 | 200 | 910 | 7280 | 1880 |
| 387 | 400 | 1030 | 8240 | 2120 |

Held-out 60/150bb fixtures have no local tables, so both versions do zero overlay
work there. Subsequent-generation table calls at fitting depths contain no
postflop rows. The first full preparation remains intact.

## Still required

These are two-model synthetic routing fixtures, not qualification on the actual
four 64-generation trained banks. This check does not cover a zero-denominator
fixture: every retained comparison row had positive arriving support. Actual
complete-bank CPU/CUDA equivalence, zero-support behavior, representative
resource bounds and end-to-end timing remain required before installing it.
The current numerical tolerances, canonical features, legal menus, table
precedence, genuine histories and unsupported fallback must remain intact.

No CUDA initialization, native executable, fitting, new deals or fresh-test
payoff/range inspection occurred. No scientific accuracy, full runtime speedup
or production-readiness claim follows from these controls. The running study
keeps its original code; the final evaluation and independent readback remain
necessary. A future candidate admission must be separate and explicit.

Evidence: `stack-context-played-bank-routed-check-v1-{attempt,result}.json`.
Result SHA256: `72659e0ae16936f9535b1ba8a39f5a5416b829d9d9625fe0163756f72afc7ac2`.
