# Fourth-arm resource interruption

The original matched training attempt stopped while archiving update 56 of
`9266301-corrected`. The traceback identifies the logical output cap in the
original worker's guard. At quiescence the store contained 4,259,993,488 bytes,
above the registered 4,250,000,000-byte allowance. Controller elapsed time was
48,771.453 seconds; this was not the 50,400-second runtime guard.

Three arms have complete 78-update results. The fourth has contiguous durable
retention markers through 55, with the last complete recovery snapshot at 48.
Update 56 has metrics and partial output, but no retention marker or published
recovery snapshot. It must not be counted as a completed training update.
The original failure, partial output, registration, and source code are preserved.
`showdown-training-interruption-review-v1.json` binds the observed evidence.

## Independent prefix audit

The running v2 audit correctly refused to report the requested 78-update arm
as complete. Its failure record is retained. A separate v3 audit passed
against the entire 55-update durable prefix, with a new registration and result
identity. It cannot substitute that prefix for a complete scientific arm.

The v3 change is limited to terminal-prefix admission and source bindings.
The scalar policy, chance/action streams, targets, accumulated state, and
checkpoint reservoir reconstruction body is byte-for-byte unchanged from v2.
Admission verifies actual original process termination, released research locks,
the preserved failed status, and the entire contiguous retained prefix. Status,
markers, and metric hashes are bound before the audit and rechecked during it.
It rejects cherry-picked shorter prefixes and nonexistent later updates.

CPU preflight admitted 55 and rejected 54, 56, boolean true, 0, and 78; all
930 original frozen inputs remained unchanged. This is admission verification,
not the completed independent audit or qualification of a resumed fit.

The separately versioned retention entry point
`retain_completed_showdown_arm_v2_20260927.py` also recognizes the v3 auditor,
the fit-replay process, and competing retention commands as active readers or
writers. An actual invocation while the v3 audit was live refused before any
retention artifact was created. Archive arithmetic and eligibility checks are
unchanged; the original retention entry point is preserved. Use v2 for recovery.

## Remaining recovery sequence

1. Completed: independent readback of all 55 durable updates passed.
2. With relevant readers and writers quiescent, retain complete audited arms
   through verified lossless archives. Preserve partial update 56 untouched.
3. Admit and run the prepared exact GPU fit replay against already-used data.
4. Separately register a continuation only after replay qualifies. Restore
   update 48 and reproduce completed updates 49-55 exactly before proceeding.
   Finish the original 78-update target with unchanged seeds and arithmetic.
5. Preserve the original runtime charge and explicitly register any additional
   runtime needed. Recheck global storage admission; do not silently raise the
   original output allowance, reset its clock, or overwrite its failed result.
6. Qualify composite provenance, full training readback, and the complete policy
   banks before the unchanged fresh payoff evaluation.

## Completed stopped-prefix audit

The v3 audit passed all 55 retained updates in 2,717 seconds. It reconstructed
28,160 BB roots and 625,154 postflop targets. Maximum root-state error was
4.093e-12, target error 5.684e-14, and policy error 1.411e-12. All 1,044 registered
inputs were rechecked unchanged after completion. The result explicitly marks
the arm incomplete and does not qualify poker strength or a resumed fit.

Registration: `62572a750a85e35a0d680fa497f4b864e464e51d9a35d60679fd184e2d97dbbd`.
Result: `2de5cf777c3e32ae6b78d714c5b9ba22615f7e1a096b70600e606296d30c5209`.

No continuation has started and no poker strength improvement is established
by this recovery work.

## Completed corrected-arm retention

The first 140 MB archive admission was refused: measured allocation plus that
allowance and the unchanged 2 GB reserve exceeded the 800 GB ceiling by
8,912,402 bytes. The corrected completed arm was therefore retained first.
Its previously qualified 96,809,224-byte bundle fits a smaller 110 MB allowance.

The v3 entry point rechecked every source-probe input and the exact member set,
remeasured all three storage roots, and admitted 799,978,913,025 projected bytes.
It imposed a process-local 100 MB packed-byte cap, checked before publication,
with 10 MB inside the allowance for metadata. Frozen codec source was unchanged.
A focused control verified oversized output is rejected before publication and
leaves source bytes intact.

Actual corrected retention passed: 272 objects, 330,008,315 original bytes,
96,809,224 packed bytes, and 472.032 seconds after admission. Every retired file
was first recovered and compared byte-for-byte from the durable archive. The
complete 78-update model bank loaded before and after retention. The receipt
SHA is `6c6fe39484d010db8ce0d221f5ad86517fc23674b78437c8cf3195e0c3a9b17e`.
Savings are 233,199,091 bytes before manifests and receipts. Partial fourth-arm
update 56 is untouched, and all 930 original source inputs remain unchanged.

The same v3 entry point admitted the completed first baseline arm with its
own fresh inventory and 140 MB allowance. Its archive and retirement receipt
completed, but the command reached its 600-second time guard during the final
full-bank load. The original command must not be reported as successful.

A separately registered read-only check then loaded all 78 played models and
verified the same receipt, unchanged admission and implementation hashes,
archive bytes, and original scientific inputs. This passed in 14.719 seconds.
No compression or retirement was repeated. The unplayed generation 78 remains
excluded. Baseline retention preserves 362 objects: 424,041,511 original bytes
in 126,422,648 packed bytes, saving 297,618,863 bytes before metadata.
Receipt: `8bf2656b271084cfd9a7feb1b179e00d55086810a8d1e82c32d4e29484e4a237`.
Readback registration: `6713c9844a89e504162d40718468ca3c0cbe9cd4f3d5aa5f8fa37dd1a685778f`.

Together the two completed-arm archives save 530,817,954 bytes before metadata.
The exact GPU fit replay passed both original fixed cases within its 400 MB
budget. See `COMPACT-CHECKPOINT-RESTORE-FINDINGS.md` for exact comparisons and
source bindings. Fourth-arm continuation remains a separate required step.

For continuation budgeting, the completed corrected arm's updates 49-78 took
5,391.969 seconds, with 229,874,596 packed batch bytes and a maximum temporary
raw update of 278,536,817 bytes. These are resource estimates, not fourth-arm
results. Prospective continuation admission must include that temporary peak,
new model/checkpoint objects, and all prior retained evidence. If necessary,
retain the third completed audited arm as well; do not raise the global limit
or lower the reserve to force admission.


## Prepared additional headroom

`retain_completed_showdown_arm_v4_20260927.py` is prepared for the third
completed arm (`9266301-baseline`) only. It passed after successful GPU replay
and fresh admission of its 145 MB allowance under the unchanged cap.
It preserved 362 objects (424,538,510 original bytes) in a 127,370,124-byte
archive and passed the complete 78-model bank readback in 620.890 seconds.
Receipt: `b72d900eab3dc26d1f9068da290a27e917468c9b7b4f25f4da6b30fb55faf20c`.
This saves another 297,168,386 bytes before metadata. All three completed-arm
archives together save 827,986,340 bytes before manifests and receipts. Unlike the
corrected-first 110 MB admission, this command budgets the codec's full 128 MiB
packed maximum plus over 10 MB for metadata (145 MB total). The existing codec
refuses an oversized compressed buffer before writing it, so no separate
in-memory compression probe is needed. All original completion, ownership,
exact-byte comparison, and full-bank checks remain in place.

Its retention-only runtime allowance is prospectively 900 seconds, including
both bank checks. This does not change any training or evaluation runtime
budget. The original 600-second baseline timeout remains recorded above. The
new command was verified to refuse competing v3 retention before producing any
admission or archive artifacts; it also refuses the separate readback reader.
Run only after the GPU replay has terminated, and only if its fresh storage
admission passes. Existing archived originals must not be recompressed or
re-created just to pass an earlier entry point's raw-file requirements.


The new continuation controller has now been launched; completion is not
claimed. Its resource amendment and exact replay gates are prospectively
specified in `SHOWDOWN-FOURTH-ARM-CONTINUATION-PLAN.md`; it requires fresh global
storage admission and cannot run while retention owns the files. All three
completed archives have passed before the continuation command was launched.
Its worker must pass the exact old-update replays before advancing beyond 55.


## Prepared independent composite audit

`composite_showdown_evidence_v1.py` and
`compact_showdown_training_review_composite_v1.py` are prepared but have not
run against a finished continuation. Admission requires actual training
termination, released research locks, a successful separately registered
continuation, the original preserved failure, all original source bindings,
complete 1-78 model lineage, exact replay receipts 49-56, and the unmodified
configuration. Original iterations 1-48 and continuation iterations 49-78
are explicit separate file locations; no synthetic original success is made.

The independent scalar reconstruction loop is byte-for-byte identical to the
passed stopped-prefix v3 audit except for selecting the iteration's directory.
It will reconstruct every iteration from 1 through 78, including chance/action
streams, probabilities, postflop targets, root/exact regrets, and checkpointed
reservoirs. Its object reader routes authenticated references across the new
objects and read-only predecessor, checking any duplicate bytes agree.

CPU admission/routing preflight passed all 78 directory selections and rejected
invalid iteration types/ranges and conflicting source bindings. Stub-backed
reader checks covered old-only, new-only, matching duplicates, conflicting
duplicates, and unexpected directory requests. An actual auditor invocation
while continuation was live refused before creating registration/result files.
These are plumbing checks, not a completed scientific readback. Final audit
completion and complete-bank evaluation remain outstanding.
