# Cycle-two matching failure and parallel scheduling work

The matched training process exited with code 1 at about 12:30 Adelaide on
2026-09-30. Session 77177 returned the terminal traceback; PID 32368 is gone.
The failure and all scientific evidence are preserved. This is a terminal
outcome of the original invocation, not an observation timeout or an idle GPU.
No scientific training or evaluation has been restarted.

## Exact cause

The original controller compares `paired_sources` dictionaries, including the
SHA-256 of each entire `board-plan.json`. A plan contains the randomly drawn
board **and** `parent_state_sha256`, which identifies that arm's previous board
regret state. Different model arms legitimately have different parent states
after the first cycle. Their complete plan hashes therefore cannot be expected
to remain equal even when the sampled boards match.

The read-only diagnosis `stack-context-paired-chance-readback-v1-result.json`
passed once in 0.125 seconds. It restored the actual five baseline board-plan
files from their verified archives and compared them with the actual relative
arm's unpublished second-cycle files. It established:

- All 70 remaining source-generation/action-batch file hashes are identical.
- All five board draws and their generation/configuration identities match.
- The only differing field in every plan is `parent_state_sha256`.
- Both plans independently equal the exact plan reconstructed from their own
  authenticated generation-one model state and registered draw configuration.
- Thirty altered-board, wrong-parent, generation, configuration, unsealed-state
  and unexpected-field cases were rejected by the proposed corrected comparator.

`stack_context_paired_chance_v1.py` is the checked proposed comparator. It first
validates the complete plan against its own parent, then compares the fields
representing the random draw. It does not ignore parent-state identity. No old
registration, failure, matching record, checkpoint or progress marker was edited.

The baseline has two published cycles; the relative arm has one published cycle
and a complete, readable second-cycle checkpoint plus metrics. The failure
occurred before the relative cycle was archived or its progress marker advanced.
Both B arms have one published cycle. No completed cycle needs to be recollected
to diagnose or preserve this evidence. Any eventual continuation requires an
explicit, checked correction and provenance record, not deletion of the failure
or silent replacement of the original matching rule.

## Hardware scheduling

The user's requested concurrency is appropriate between the four independent
arms. Successive cycles inside an arm remain dependent. The original coordinator
runs only one arm at a time, with four CPU target workers and one board worker;
the five depth contexts also run sequentially. Short GPU inference/fitting
phases and serial preparation leave substantial machine capacity unused.

During inspection, available resources were about 100 GB RAM, 21 GB VRAM and
326 GB free on S:. The proposed four-arm continuation keeps each arm's existing
four target workers and one board worker. It preserves the original scientific
configuration and includes light desktop/video sharing, priority for active
solves and heavy work, and bounded combined resource use. Full-cycle throughput
must be measured; a fourfold gain has not been established.

The initial parallel prototype and plan assumed the existing runner would exit
normally at its 12-hour boundary. That assumption is now obsolete because the
runner failed the matching check. Its one-shot qualification
`stack-context-parallel-continuation-v1-check-failure.json` stopped when the
expected live owner was absent. It performed no CUDA work or scientific work.
Preserve that failed check. The v1 prototype must not be launched: it requires
a normal legacy exit, which did not occur. A revised adapter must handle the
documented comparator correction and complete-checkpoint provenance explicitly.

## Other completed preparation

`stack-context-independent-audit-check-v1-result.json` passed once in 18.547
seconds: five synthetic payoff scenarios, 56 contrasts per scenario, physical
range propagation on retained 20/60/400 BB trees, and 41 corruption rejections.
It uses separate vector arithmetic and all 1,326 physical holdings to check
reported statistics, arriving ranges, card removal and perfect-recall support.
This is implementation evidence, not a poker accuracy result.

The complete final readback controller is still an unexecuted draft in the
workspace staging directory. It must be updated to account for any accepted
operational amendment and the corrected matched-input semantics before use.
The existing final-bank selector/evaluation consumer also assumes raw matching
hash equality; those consumers need a versioned correction and fresh software
qualification before scientific evaluation.

## Next work

Prepare and qualify a versioned parallel continuation that preserves both the
failed original attempt and its completed work. Validate recovery of the already
completed relative cycle without new training; use per-arm parent validation
plus matched chance identities for subsequent checks. Carry that provenance
through final-bank selection, evaluation and independent readback. Verify actual
four-process compatibility and measure real throughput before estimating a new
completion time. Do not automatically repeat a failed scientific cycle, launch
a replacement experiment, or claim an accuracy improvement.

Production 56708 is unchanged. Nothing was pushed or deployed. The broad goal
remains active; the current status is **training stopped, correction in progress**.
