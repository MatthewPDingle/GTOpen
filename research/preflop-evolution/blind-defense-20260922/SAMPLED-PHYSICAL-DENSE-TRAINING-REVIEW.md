# Larger-data training completed; strength evaluation started

The fixed 78-update trial completed in 4,639 seconds, within its three-hour cap.
The independent readback replayed all 39,936 physical deals and 79,872 updater
traversals, checked every frozen subbatch generation, and reproduced the final
reservoir arrays and random-generator states exactly. All 78 played generations
remain the candidate; the unused generation 78 is excluded.

## Descriptive training comparison

Both rows below concern each run's unused next model and its own retained
historical training targets. These targets, policies and retained distributions
differ, so this is not a controlled strength comparison or an action-EV error.

| BB first-decision measurement | Original pilot | Larger-data trial |
|---|---:|---:|
| Fresh deals in completed training | 4,992 | 39,936 |
| Retained root visits | 4,992 | 10,719 |
| Root hand classes represented | 169 | 169 |
| Median retained visits per class | 22 | 51 |
| Network fit error against retained targets, RMS | 13.68 bb | 7.56 bb |
| Root share of the aggregate fitting error | 0.84% | 0.14% |

Eightfold fresh data produced about 2.15 times the retained root examples because
the BB reservoir reached its fixed 262,144-visit capacity. It saw 966,553 visits
in total. BTN retained all 97,329 of its visits. The capped retention algorithm
was unchanged, as registered.

The descriptive call-minus-fold sample-standard-deviation/square-root-count
ratio fell from a median 5.02 bb to 3.15 bb across root classes. The corresponding
raise ratio fell from 8.38 to 4.76 bb. These are adaptive historical samples,
not confidence intervals for final-policy EVs. A direct preflop table would
eliminate regression error against retained means, not their sampling uncertainty.

## Gates and next step

The separate hybrid-policy GPU numerical control also passed on its old fixture:
maximum action-probability difference versus CPU was 0.00003630, and maximum
fixed-deal payoff difference was 0.00000172 bb. This validates execution within
the registered tolerances; the hybrid model has not been trained or strength-tested.

The dense candidate's registered 8,192-deal response-training and 16,384-deal
held-out evaluation has started on its reserved fresh streams. CPU reference
checks precede held-out sampling. No range preview or production deployment
has been made, and no poker-accuracy improvement is yet established.

The first automatic handoff failed before any scientific stage because it tried
to create an existing status file. Its source, stale status and failure review
are preserved. A versioned continuation with atomic status updates launched the
unchanged audit/evaluation stages; neither training nor a failed evaluation was
repeated.

Evidence: `sampled-physical-dense-pilot-v1-independent-review.json`,
`sampled-physical-dense-fit-diagnosis-v1-result.json`,
`sampled-physical-dense-root-noise-v1-result.json`,
`sampled-physical-hybrid-gpu-control-v1-result.json`, and
`sampled-physical-dense-evaluation-v1-registration.json`.
