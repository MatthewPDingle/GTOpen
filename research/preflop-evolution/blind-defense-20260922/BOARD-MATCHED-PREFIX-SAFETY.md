# Board study: storage and restart safeguards

Use `tools/research/board_matched_prefix_v2.py` for the next two-generation
prefix. Version 1 and its preparation evidence are retained unchanged. No
actual prefix registration or training directory exists yet; the version-1
output name remains the planned study identity so the prepared independent
reader remains compatible. Registrations made by version 2 identify the runner
version explicitly and bind its source bytes.

## What changed

The review found two orchestration defects in the unlaunched version 1:

- Allocation and logical-size checks happened before ordinary updates, but
  replay lacked the logical check and successful completion did not enforce
  the final measured sizes. Net drive-free-space change can understate study
  growth when unrelated files are removed or compressed.
- Replay and final completion JSON were written directly to their final names.
  An interruption during a write could leave an unreadable existing marker
  that prevented an otherwise valid checkpoint from resuming.

Version 2 checks actual study-directory allocation and logical size before and
after each generation/replay, after progress publication, and before final
success. It also repeats the global research allocation inventory before final
publication. The allowances remain 4 GB allocated / 8 GB logical for the whole
two-arm prefix, with a 1 GB pre-update reserve and a separate 2 GB global
metadata/headroom reserve under the 800 GB research ceiling.

Completion JSON is fully written and flushed to a unique file in the same
directory, then renamed atomically. Progress replacement is explicit; a new
completion marker refuses to overwrite an existing one. Failed temporary files
remain available for inspection and count toward storage measurements.
Explicit resume can preserve malformed completion JSON under a unique invalid
marker name before rebuilding it from published checkpoints. A registration
mismatch or a valid non-passing marker is rejected rather than silently repaired.
Progress checkpoints do not use this malformed-marker recovery path.

These checks enforce admission and successful-publication limits. They are not
an operating-system disk quota: transient writes can exceed an allowance before
the next guard or quiescent scan rejects the run. File flushing and atomic
rename also do not guarantee recovery from every hardware/power-loss failure.

## Verification

`board-matched-prefix-safety-control-v1-result.json` passed in 5.906 seconds.
It used real Windows files and allocation accounting, with tiny deterministic
mock training states; it did not run CUDA or the native poker engine.

- Eight injected storage failures covered both allocation and logical size
  after training, before replay, after replay, and before final success. None
  published a successful study result. A rejected first update left published
  progress at generation zero.
- Interrupted replay/result publication resumed successfully while retaining
  failed files. Replaying the interrupted replay was necessary, but no already
  published training generation was repeated. A failed final publication
  resumed with no additional updates.
- Partial serialization never exposed a final marker. Failed progress
  replacement retained the preceding file. New-marker overwrite and wrong
  registration were rejected; malformed-marker recovery retained the original
  bytes and hash.
- The normal two-arm fixture executed four updates and two deterministic
  replays, and refused to replace an already completed result.

`board-matched-prefix-preparation-control-v2-result.json` separately reproduced
all 2,048 historical physical deals and 32 action-batch seeds in 0.438 seconds.
The scientific configs, seeds, learning budget and planned independent audit
are unchanged. Missing genuine GPU/control-readback evidence still rejects
execution before resource or CUDA admission.

## What remains

The fixed 65,536-deal evaluation continues unchanged. Its existing queue owns
the report and subsequent GPU pipeline control. After that control and its
independent trained-state readback pass, qualify the general sequence reader,
then freshly admit the version-2 actual-budget prefix and independently audit
it. Only measured storage and that audit can admit a separately prepared full
78-generation continuation. This control provides no new range-quality or
playing-strength result, and nothing was deployed to port 56708.
