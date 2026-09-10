# Automatic-budget modeled qualification (prepared only)

This separate runner leaves the frozen API50 helper unchanged. It has not started a server, built code or run GPU work. Seven pure tests pass normally and with python -O.

Run only after the active API50 queue finishes:

```powershell
python research/autoresearch/passes/03-preflop-20260910/proposals/automatic-modeled-qualification/qualify_auto.py --id api-auto-modeled-a --execute
```

The exact frozen modeled native0 fixture comes from extended-convergence-protocol.json, including its original input SHA. Native input must be six seats, coupled model, nonempty modeled opponents, BTN Solver, and entirely zero arenas. Copies preserve all config/profile/lock/header data; outputs may change only native iteration0 to2. Runtime binaries, comparator and equity/fit caches are pinned to already reviewed hashes.

A new private output directory holds protocol.json, per-case copied executables/caches/input, server logs, status traces, result.json, qualification.json and resulting native files. All original user files and live56708 remain unchanged. Private POST load/solve/node/save calls revalidate child PID, executable SHA, creation time and file identity. Both child processes are hidden and only retained child handles can be terminated.

Order is candidate then original. Candidate explicitly removes SOLVER_GPU_MEM_MB, so the real server chooses current free VRAM minus its512MB margin. Both cases pin16threads, PREFLOP_EQ_SAMPLES=1024 and PREFLOP_GPU_LAYOUT_STATS=1. Candidate JSON telemetry supplies exact chosen budget, batch, cache flags, planned storage and reference source. Original receives that exact budget as a manual cap; original-resolved-budget.json records this predetermined adaptive input. Solve requests are exactly2iterations/check_every2/target_gap0.005. No retries or relaxed limits.

Comparability requires candidate deployed_prepass, actual batch/cache matching its literal reference, original printed batch matching, and original exact observed budget. The old runtime does not emit a HU-cache flag: its cache setting is inferred from the preserved same-budget literal planner, explicitly not claimed as observed telemetry. Missing evidence means noncomparability. Only two completed comparable cases proceed to complete native header/arena equality, root semantic JSON equality, and the existing full native comparator/assertion. Local explicit exceptions retain bitwise checks under -O.

Limits: at least660seconds must remain before21:29:18UTC at preflight and just before the pair. The whole pair including copying/comparison has600seconds, each child server at most240seconds from launch. A separate monitor checks the live56708 preflop/postflop/report status and deadlines every500ms; network failure fails closed and terminates only its child. Deadline observation has bounded polling/network delay. The existing comparator gets the remaining pair time minus10seconds to leave its guard cleanup room.

An original timeout after candidate completion is recorded as candidate_completed_original_timeout, never parity or performance success. Other errors, unavailable/mismatched layout and failed exactness receive separate explicit outcomes. Candidate result/native files remain retained even when original fails. This is one default-route/allocation qualification, not a performance study or universal budget guarantee.
