# User-requested reboot pause

The user requested a safe pause. Research workers and controllers are stopped; owned research locks are absent. Production on port 56708 was not changed or stopped by this pause.

48 of 78 complete training updates are saved. The full checkpoint was restored and verified after shutdown, including the played model bank, reservoirs, random states, and direct preflop tables. See the adjacent pause JSON for the exact checkpoint reference and registration hashes. The store is `S:\GTOpen-research\sampled-visible-hybrid-trial-pilot-v1`.

Original controller status files report worker exit 15 and training failure because the worker was deliberately terminated for reboot. Preserve those original files. This was not a numerical failure or deadline expiry. Partial work after the last complete checkpoint is not a completed update; retain it as evidence. No final evaluation has run.

## Resume after the user returns

Do not automatically restart while the user is rebooting. Do not rerun the original pilot from scratch: its controller expects a new store. First integrate and audit an explicitly versioned continuation using the existing `restore_checkpoint` API in `sampled_visible_hybrid_checkpoint_v1.py`. Preserve the original 48 updates, model bank, config, seeds, and registered statistical tests. Finish the remaining 30 updates, then perform the full training audit and both player evaluations. Make continuation provenance explicit and adapt admission/comparison artifact paths without editing frozen registered sources.

All research findings and next measurement preparations are in RESEARCH-DECISION-CHECKPOINT.md and STRATIFIED-RESPONSE-PREPARATION.md. Latest pre-pause code commit: cebb799d. No cloud resources were purchased.
