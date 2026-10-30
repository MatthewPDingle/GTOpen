# Prospective bounded native exporter qualification

This is a software qualification plan. It reuses the exact retained 20bb context, board requests, physical batches, action seeds, frozen policy transports and river requests from the completed one-cycle profile. It proposes no new deals, policy inference, target fitting, checkpoint publication or scientific accuracy claim. No native control or compilation has been run by this review.

`plan.json` pins the original sources, source snapshots, four registered binaries, the complete 809-file profile, its prior independent readback, and the current retained Cargo compilation metadata. `all-117-invocations.json` maps every original native receipt to its inputs, output channels, caller and child identity. `representative-controls.json` supplies exact reference paths, hashes, byte lengths and original argv for the seven primary cases. New source and binary paths remain pending independent review.

| Primary case | Retained request | Reference payload bytes |
|---|---|---:|
| Board draw 0 | board-000, complete ordered 1081 private hands per actor | 35,575,642 |
| Board draw 1 | board-001, complete ordered 1081 private hands per actor | 35,716,185 |
| Bridge queries | batch-007, original 13 deals and action seed | 557,912 |
| Bridge verify | batch-006, original batch and frozen policies | 25,597 |
| Action trace | batch-005, original batch and frozen policies | 682,115 |
| River history | batch-011 / chunk-000, original stdin request | 16,934,530 |
| River selected | batch-002 / chunk-000, original stdin selected-pair request | 4,870,176 |

The primary payload total is 94,362,157 bytes. The optional coherent transport group replays queries, verify and trace from batch-007 using its unchanged retained policies. It checks consistency across stages without computing a fresh policy. The full inventory contains 2 board, 13 queries, 13 verify, 13 trace, 38 river-history and 38 river-selected invocations.

## Source and compilation review before execution

Review each separate new example against its pinned original, including all referenced research modules. Changes should be confined to argument validation, input byte limits, bounded serialization and safe output publication. Private-hand domains, card evaluation, node visitation, query deduplication/order, action menus, leaf payoffs, RNG, frozen-policy checks, own histories and derived target records must remain unchanged. Shared serialization code must operate on the original result values without rewriting floating values, key order, strings, arrays or poker calculations. Check the unchanged originals and registered binaries again after compilation.

The retained example fingerprints show **no solver features and no Rust flags for board, bridge and trace**. Their referenced `serde_json` fingerprint has `default,std` and lacks `float_roundtrip`. River was compiled with `continuation-transfer-research,gpu,preflop-research`, no Rust flags, and `serde_json default,float_roundtrip,std`. `crates/solver/Cargo.toml` makes `continuation-transfer-research` enable `serde_json/float_roundtrip`. Preserve these role-specific feature graphs in separate build invocations; globally enabling that feature for all examples can change parsing and downstream floating results. No new example names or feature commands are assumed until the sources are supplied.

Current Cargo fingerprints are retained compilation evidence, not a cryptographic binary-to-build receipt. Pin the new sources, helper, dependency lock, target configuration, exact build argv/log, Cargo JSON artifact messages and resulting binary hashes before qualification. An isolated new target/output directory avoids replacing original binaries. The compiled `gpu` dependency for river does not authorize GPU work; these exporter controls must retain the original CPU math and make no GPU calls.

## Byte-exact success controls

For each primary control, use the supplied new binary with the **same input paths and exact stdin bytes**. Replace only argv[0] and, for bridge/trace, the final output destination. The destination must be a new never-existing file in a new owned control folder; never pass a historical output path. Keep the original 13 deals, seeds and policies, the board's complete 1081-hand lists, and the complete river history/selected-pair request unchanged.

Require successful process-bound receipts with exact executable/input/helper pins, argv, PID, creation time, owning parent, return code, start/terminal interval, output sizes and hashes. Native stdout, stderr and direct CLI output files are different artifacts; authenticate and compare every applicable channel. Verify hashes before interpreting JSON, then verify exact byte length and raw bytes against retained reference artifacts. A canonical JSON digest, numerical tolerance or selected field comparison does not replace byte equality.

Preserve each original output convention:

- Board: compact JSON on stdout followed by exactly one LF.
- Bridge: compact JSON in its direct output file **without** LF, plus separate compact summary JSON and one LF on stdout.
- Trace: compact JSON in its direct output file **without** LF; empty stdout.
- River: compact JSON and one LF on stdout; deterministic compact summary JSON and one LF on stderr.

The old Python process monitor counted stdout/stderr, while bridge and trace also wrote direct output files. The new qualification must measure and cap those direct files explicitly. Record both logical bytes and independently queried named allocation in the new control store; NTFS compression changes allocation, not byte-limit semantics. Keep resource guards and the volume reserve separate from candidate-specific compression savings.

## Pre-write rejection controls

These controls are prospective. Use only new software-control files and a separately pinned downward cap override or helper test entrypoint. An override may lower the normal role limit and must never raise it. If the new interface has no downward override, qualify helper boundaries with pure serialization unit controls and explicitly mark the native over-budget path untested rather than claim it passed.

1. Let B be a retained exact serialized payload length, including the role's LF when present. At cap B, require byte-exact success into a new target; at B-1, require a nonzero exit, a retained failure receipt, no direct output artifact, and no JSON payload on stdout. A separate B+1 success checks inclusive-limit behavior. Capture each invocation under unique labels and never reopen a prior result path for writing.
2. Test small nested JSON values through the shared serialization helper at exact and one-byte-short limits, both with and without LF. Include escaped control/non-ASCII strings, integer keys represented as strings, booleans, nulls, arrays, and finite floats. Compare accepted bytes to the pinned original serializer. An instrumented sink must observe **zero writes** when serialization or budget validation fails. A bounded buffer may contain a rejected partial encoding in memory; it must not reach a filesystem or stdout sink.
3. Create a new owned sentinel file containing recorded nonempty bytes. Passing that path as a bridge/trace destination must fail and preserve its bytes, length and file identity. Also test a directory at the requested output path. Opening output with `create_new` after successful validation protects against a destination appearing between checks; an existence assertion followed by `std::fs::write` is insufficient.
4. For role input limits, copy an existing request/context/batch/policy into a new control file and append whitespace to the exact boundary and one byte above it. This changes no poker deals or policy values. Above-limit inputs must reject before any payload write. Preserve the original river context limit of 16 MiB and stdin limit of 64 KiB, its 64,000,000-byte pre-write output cap, 500,000 nodes, 250,000 queries, 32 targets, 990 complete history pairs, and at most 64 explicit selected pairs. Do not enlarge those existing gates.
5. Check invalid/zero cap and malformed serialized inputs reject without creating/truncating output. Keep all generated sentinels, accepted artifacts and rejection receipts. Repeating a failed software case requires a new labelled control version, with the original failure retained; it does not retry the original poker profile.
6. Source-review every output sink. Validate/count serialized output before creating a direct destination or writing the first stdout payload byte. Include newline bytes and all intended direct channels in their declared budgets. A post-write polling rejection, an output truncated to a limit, or a partial JSON prefix fails pre-write qualification.

The serializer's disk-byte bound does not bound construction of the in-memory result, serializer buffers, directory metadata, stderr or other concurrent outputs. Native memory/process/runtime controls, safe stdout/stderr capture, filesystem reserves and complete multi-worker accounting remain separate obligations. The existing river native cap is a source-level pre-write payload cap; the Python polling monitor alone is not a strict on-disk bound for uncapped exporters.

## Admission and retained evidence

After new sources and binaries arrive, independently pin and compare the source changes before enabling any native control. Register all cases, budgets, destinations, source/executable/input hashes and expected byte lengths before starting. Use one fresh bounded software-control store, never write into the original profile or either retention control. Stop on the first unexplained mismatch and retain its receipt and artifacts. No silent normalization, payoff replacement, dropped private hands, source-patch retry or gate loosening is admissible.

Passing these controls would support parity and pre-write serialization qualification for the retained 20bb requests under the pinned build. It would not establish poker accuracy, convergence, deeper-stack output bounds, a filesystem quota, or safe concurrency for a larger scientific run. Those need separately registered prospective evidence.
