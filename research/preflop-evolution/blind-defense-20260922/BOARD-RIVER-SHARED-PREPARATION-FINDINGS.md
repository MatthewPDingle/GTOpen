# Duplicate river query preparation: CPU profile

The current two-bank collector rebuilds bank-independent card features,
betting-history arrays and public geometry separately for each opponent bank.
Sharing that preparation passed byte-for-byte controls on ten old TRAINING
cases spanning both actors and all five pot bands, with 2,438-3,966 queries per
case. Both banks' context/geometry validation remains; a mismatched second
bank is rejected. Original query objects remain unchanged.

| Ten-case pass | Separate preparation | Shared preparation |
|---|---:|---:|
| First paired order | 8.501 s | 4.274 s |
| Reverse paired order | 8.169 s | 4.383 s |

The counterbalanced separate/shared/shared/separate sequence gives **1.93x**
faster CPU preparation and about **0.401 seconds saved per case** for this
isolated stage. These are cached-input timings during concurrent collection;
they are not an end-to-end speed measurement. The broader earlier shared-array
control used a different evaluator, so its speed ratio is not substituted here.

The instrumented call profile identifies deep copying and visible-card summary
construction as substantial repeated work. Instrumentation itself adds overhead;
its cumulative seconds must not be treated as normal runtime or as independent
additive costs. No GPU inference, model-specific tables or policy accumulation
was tested in this CPU control. The live collection is unchanged.

## Next step after the current study releases the GPU

Qualify preparation reuse with both full frozen banks, keeping separate
model-dependent table construction and GPU uploads initially. Compare every
policy and own-reach output byte-for-byte against the existing path on the
same previously inspected cases, then reconstruct the saved conditional labels.
Measure complete two-bank preparation plus inference in counterbalanced order,
retaining guard overhead separately. Only an output-preserving end-to-end gain
would justify adopting it for a later collection. Do not rewrite sources of
the running registered experiment.

An eventual producer/consumer pipeline could overlap CPU preparation with GPU
inference, but that requires a separate resource and output-equivalence test.
This result does not establish its benefit or justify adding workers blindly.

Evidence: `board-river-shared-preparation-profile-v1-registration.json` and
`board-river-shared-preparation-profile-v1-result.json`. The control finished
in 63.2 seconds, used no GPU and retained less than 1 MB of evidence. No poker
model, training target, production state or historical archive was changed.
