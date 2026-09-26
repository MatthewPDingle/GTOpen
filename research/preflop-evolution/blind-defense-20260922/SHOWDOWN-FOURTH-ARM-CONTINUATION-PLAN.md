# Fourth-arm continuation after the storage interruption

This is a prospective resource amendment for the existing two-seed, four-arm
BB-versus-BTN 200 bb study. It changes neither the hypothesis nor training
arithmetic, configurations, deal/action/reservoir/fit seeds, 78-update target,
played-model averaging rule, or subsequent fresh payoff evaluation design.
No improved poker strength has been established.

## Original evidence and required recovery

Original registration SHA:
`73305540181f7be96b5f5d68365408d89643c51d628966d2cb920aa423686eec`.
Three arms completed 78 updates. `9266301-corrected` has independently audited
durable updates 1–55, a complete checkpoint at 48, and partial output for 56.
The original controller failed its 4.25 GB output allowance after charging
48,771.453 seconds. Its failure and all fourth-arm files remain unchanged.

The exact GPU fit replay passed baseline 72→73 and corrected 16→17. Each next
model, scientific metric, and native batch artifact matched exactly. Parsed
initial policies matched, though their JSON object key ordering differed.
Only the already named timing fields were excluded. This qualifies those
replays, not the continuation controller or poker strength.

The continuation must:

1. Require the completed GPU replay, stopped-prefix audit, checkpoint overlay
   controls, and mixed archive/predecessor restore control.
2. Bind every original fourth-arm file, original frozen input, new source,
   control result, and this plan before starting a separate owned directory.
3. Restore the original checkpoint 48 with unchanged native reconstruction.
4. Reproduce updates 49–55, comparing exact model references, parsed scientific
   metrics/initial policies, and every original native batch artifact. Refuse
   update 56 unless all seven durable replay comparisons pass.
5. Compare the saved partial update 56 too, while continuing to identify it as
   originally incomplete. Do not count it as a previously completed update.
6. Finish at 78. At 56, 64, 72 and 78, restore the newly archived checkpoint
   using its authenticated read-only predecessor and compare complete model
   history, accumulated states, both chance/action states, reservoir arrays,
   and reservoir random states against live training state.
7. Preserve original references in the complete played bank. Reuse immutable
   predecessor objects without copying the entire old bank or modifying it.
   Only the two checkpoint reservoir objects may need temporary copies inside
   the new owned directory before the established archive/retire procedure.
8. Recheck every registered source after completion. Publish a distinct
   fourth-arm continuation result; never forge the original global success.

## Explicit resource amendment

The new worker may run for at most **3 additional hours**, including replayed
updates. The original 48,771.453-second charge remains visible; the maximum
cumulative charged training time is 59,571.453 seconds. This is an explicit
increase beyond the original runtime envelope after a resource interruption,
not a clock reset or an outcome-dependent training extension.

The new directory and associated output records have an **850 MB** allowance.
Fresh inventory must admit that allowance beneath the unchanged global
**800 GB** limit while retaining **2 GB** metadata reserve. Completed evidence
is losslessly archived to make room; no earlier failure or scientific sample
is deleted. The completed corrected arm's last 30 updates used about 230 MB
of compressed batches but peaked at 279 MB of raw temporary output per update;
both temporary output and new model/reservoir objects must fit the allowance.

Production on port 56708 must remain idle. Preserve the 20 GB available RAM,
40 GB free S-drive space, and 3 GB free GPU memory reserves. Use an exclusive
research lock, hidden workers, resource/user-activity stops, and durable
checkpoints. On any failure, preserve partial outputs and register a separate
recovery decision; never silently retry into the same directory or relax gates.

## What completion does and does not establish

A successful continuation establishes the intended 78-update fourth training
arm and its exact recovery checks. It still requires an independent composite
training audit and a provenance-aware complete-bank reader/evaluator. Only
after those pass may the fixed fresh payoff evaluation compare the four arms.
Training completion, checkpoint fidelity, lower target variance, and visually
plausible ranges are not evidence of improved poker strength by themselves.
