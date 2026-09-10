# Automatic-budget modeled qualification (prepared only)

This separate runner leaves the frozen API50 helper unchanged. It has not started a server, built code or run GPU work. Eleven pure tests pass normally and with python -O.

Run only after the active API50 queue finishes:

```powershell
python research/autoresearch/passes/03-preflop-20260910/proposals/automatic-modeled-qualification/qualify_auto.py --id api-auto-modeled-b --execute
```

The exact frozen modeled native0 fixture comes from extended-convergence-protocol.json, including its original input SHA. Native input must be six seats, coupled model, nonempty modeled opponents, BTN Solver, and entirely zero arenas. Copies preserve all config/profile/lock/header data; outputs may change only native iteration0 to2. Runtime binaries, comparator and equity/fit caches are pinned to already reviewed hashes.

A new private output directory holds protocol.json, per-case copied executables/caches/input, server logs, status traces, result.json, qualification.json and resulting native files. All original user files and live56708 remain unchanged. Private POST load/solve/node/save calls revalidate child PID, executable SHA, creation time and file identity. Both child processes are hidden and only retained child handles can be terminated.

Order is candidate then original. Candidate explicitly removes SOLVER_GPU_MEM_MB, so the real server chooses current free VRAM minus its512MB margin. Both cases pin16threads, PREFLOP_EQ_SAMPLES=1024 and PREFLOP_GPU_LAYOUT_STATS=1. Candidate JSON telemetry supplies exact chosen budget, batch, cache flags, planned storage and reference source. Original receives that exact budget as a manual cap; original-resolved-budget.json records this predetermined adaptive input. Solve requests are exactly2iterations/check_every2/target_gap0.005. No retries or relaxed limits.

Comparability requires candidate deployed_prepass, actual batch/cache matching its literal reference, original printed batch matching, and original exact observed budget. The old runtime does not emit a HU-cache flag: its cache setting is inferred from the preserved same-budget literal planner, explicitly not claimed as observed telemetry. Missing evidence means noncomparability. Only two completed comparable cases proceed to complete native header/arena equality, root semantic JSON equality, and the existing full native comparator/assertion. Local explicit exceptions retain bitwise checks under -O.

Limits: at least660seconds must remain before21:29:18UTC at preflight and just before the pair. The whole pair including copying/comparison has600seconds, each child server at most240seconds from launch. A separate monitor checks the live56708 preflop/postflop/report status and deadlines every500ms; network failure fails closed and terminates only its child. Deadline observation has bounded polling/network delay. The existing comparator gets the remaining pair time minus10seconds to leave its guard cleanup room.

An original timeout after candidate completion is recorded as candidate_completed_original_timeout, never parity or performance success. Other errors, unavailable/mismatched layout and failed exactness receive separate explicit outcomes. Candidate result/native files remain retained even when original fails. This is one default-route/allocation qualification, not a performance study or universal budget guarantee.

## Harness correction before attempt b

Attempt a failed before solving at an API/native profile JSON comparison. Its files remain unchanged. The load handler routes profiles through serde_json::Value, whereas native saves directly serialize typed f32 vectors. Those serializers can emit different decimal representations of the same f32. This explains why the original gate is unsuitable, but the exact observed difference in a was not retained and is not claimed verified.

Attempt b retains the complete load response and the first differing API/native profile path, exact values/types and mismatch kind for diagnosis. It retains exact config, seat count, frozen and profile-presence checks. Before ANY solve, each own server saves loaded-input.gtop; complete native header and every arena SHA must equal the frozen input. This covers hero, all policy probabilities, locks and configuration without any numerical tolerance or JSON canonicalization. The load response does not include hero, so the old top-level check was removed in favor of this complete native-state gate. Disk reservation now includes both extra native saves.

## Final fixed23000 qualification

The optional --candidate-budget accepts only23000. Omission retains automatic behavior; neither mode changes the original's rule of pinning the exact observed candidate budget. Fixed mode records candidate_automatic_budget=false and candidate_requested_budget_mb=23000 in protocol and summary, and requires candidate layout telemetry to equal23000. This resolves the specific earlier23GB literal harness timeout using the actual server without rerunning automatic mode. Prior a/b files and protocols remain unchanged.

```powershell
python research/autoresearch/passes/03-preflop-20260910/proposals/automatic-modeled-qualification/qualify_auto.py --id api-modeled23000-a --candidate-budget 23000 --execute
```
