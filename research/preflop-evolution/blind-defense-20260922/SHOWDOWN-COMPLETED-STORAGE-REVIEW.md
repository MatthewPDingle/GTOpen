# Completed-baseline storage and continuation risk

The first 78-update baseline is complete and independently audited. This review
uses its actual files plus the corrected arm's first eight completed updates.
It does not change live training, remove files, or increase any resource limit.
The reproducible size inputs and per-update transients are recorded in
`showdown-completed-baseline-storage-review-v1.json`.

## Measured completed baseline

| Category | Files | Logical bytes |
| --- | ---: | ---: |
| Training batch archives | 624 | 633,442,504 |
| Reservoir archives | 10 | 52,923,808 |
| Immutable JSON model/checkpoint objects | 360 | 373,275,713 |
| Restored final reservoir objects | 2 | 50,765,798 |
| Metadata and saved played policies | 879 | 3,176,338 |
| Total | 1,875 | 1,113,584,161 |

The immutable object bundle is 424,041,511 bytes, below the existing codec's
536,870,912-byte raw limit. The separate in-memory probe completed successfully:
the existing preset-6 container produces **126,422,648 compressed bytes**, below
its 134,217,728-byte packed limit. All 362 original byte streams were recovered
exactly and all source files remained unchanged. Compression took 388.98 seconds;
the full check took 399.11 seconds. No archive was published and no files retired.

The measured potential saving is **297,618,863 bytes** before small manifest and
receipt overhead. Packed size is close enough to the codec limit that other
completed arms still need their own size check. This probe does not qualify
durable archive publication, deletion, a resumed training run, or evaluation
storage admission. Results and source bindings are in
`completed-baseline-archive-probe-v1-result.json` and its registration.

## Why the original cap is at risk

The baseline writes all eight raw subbatches before archiving them. At update
78 those raw files totalled 274,852,572 bytes, while their final archives totalled
7,368,664 bytes: an extra 267,483,908 bytes during that update, before allowing
for other checkpoint/compression overlap. The largest observed difference in
the baseline was 290,901,435 bytes.

The corrected arm has three model envelopes per generation, versus four in the
baseline. Its first eight batch archives occupy 97.99% of the matched baseline
prefix. Applying that ratio to the baseline's batch storage, removing the one
absent model family, and leaving other categories unchanged gives an illustrative
four-arm final size of 4.241 GB. Adding the observed final-update transient gives
about **4.508 GB**, exceeding the registered **4.250 GB** training cap.

This is a forecast, not a hard bound: later corrected policies, model JSON,
reservoir contents, metadata, and the second seed can change the sizes. It
nevertheless identifies a likely late-run resource stop. Free drive space does
not override the registered experiment cap or the 800 GB global allocation
ceiling. Logical and allocated sizes are different accounting measures.

## Continuation requirements if the resource guard stops training

1. Verify the controller and worker are terminal. Preserve their failure record
   and all partial outputs. A polling timeout is not evidence of termination.
2. Identify the last complete recovery checkpoint in the interrupted arm and
   independently audit that prefix. Preserve the exact configuration, played
   models, accumulated regrets, reservoirs, and random-number states.
3. Only with all writers quiescent, use the qualified owned-object retention
   path on completed audited arms. Verify durable archives and every original
   byte before retiring exact duplicates. Do not touch legacy research data.
4. Separately register a deterministic continuation before running it. Recover
   the same state and finish the original fixed 78-update budget for every arm;
   do not reset seeds, select a prefix, or treat a partial arm as completed.
   Replay of any already completed updates beyond the recovery checkpoint must
   agree with their retained scientific artifacts; timing metadata may differ.
5. Report the interrupted original attempt and continuation explicitly. Bind
   both in the final training provenance. Do not overwrite the original failed
   run as though it completed uninterrupted. Recheck actual global allocation,
   transient output needs, and the remaining evaluation budget before launch.
6. Require complete independent training readback and the complete-bank
   CPU/GPU controls before the unchanged fresh payoff comparison.

These are prerequisites, not a qualified continuation implementation. Current
training remains unmodified. The existing retention entry point correctly
refuses to retire any arm while the original training worker is active, since
its whole-store size scan could race concurrent deletion.

## Mid-run update at corrected generation 38

`showdown-midrun-resource-review-v1.json` binds all 78 completed baseline
markers and the first 38 corrected markers, with the live status snapshot.
The corrected/baseline compressed batch ratio over the same 38 updates is now
99.78%, versus 97.99% over the first eight. Substituting this measured ratio in
the earlier illustrative calculation gives **4.264 GB final**, or **4.531 GB**
with the previously measured last-update transient. The final-size estimate
alone is slightly above the original 4.250 GB cap. This remains a forecast,
not an admission measurement or permission to alter the running study.

Time also has little margin. Baseline updates averaged 155.69 seconds;
corrected updates most recently averaged 158.29 seconds over eight updates.
Using those rates for the remaining fixed work projects 48,844 seconds total
(13 h 34 m). Applying the slower observed late-baseline rate of 166.76 seconds
to all remaining updates projects 50,707 seconds (14 h 5 m), against the
registered 50,400-second limit. These are two illustrative scenarios, not a
confidence interval; they exclude further final-restore/controller overhead.
The second seed can change both timing and compression.

Continue the existing fixed-budget experiment unchanged. If it stops, verify
the actual terminal cause and remaining charged runtime before any continuation.
A continuation cannot reset the original clock or relabel an exhausted budget
as an uninterrupted pass. If the time budget is exhausted, record the original
attempt as incomplete; any later resource-budget amendment needs its own
prospective registration and explicit reporting. No such amendment or new
training launch has occurred here. The complete four-arm scientific comparison
is still required; a resource-stopped prefix cannot replace it.
