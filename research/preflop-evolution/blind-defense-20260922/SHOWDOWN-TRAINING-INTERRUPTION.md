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
as complete. Its failure record is retained. A separate v3 audit is running
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

1. Finish the independent 55-update readback before any object retirement.
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

No continuation has started, no original files have been retired, and no poker
strength improvement is established by this recovery work.
