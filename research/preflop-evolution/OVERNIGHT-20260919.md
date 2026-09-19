# Overnight preflop accuracy research, 19–20 September 2026

The user authorized autonomous research until returning tomorrow morning.
Do not redeem reset credits or purchase usage. A one-time thread heartbeat
`resume-overnight-preflop-research` is scheduled for 00:15 Adelaide time,
after the reported 00:09 normal reset. Do not launch duplicate work if the
goal or a research process is already running. Codex and this computer must
remain available for the local follow-up to run.

## Current evidence

Read `integrated-coverage-20260919/RESULTS.md` and `SCALING.md` first.
All six prescribed connected-game development runs finished 2,000 iterations.
Numerical accounting passes; small board samples severely distort ranges.
AA call changes from 52.7% to 4.0% when the same two ranks and bet sizes gain
all suit relabelings. This is sample sensitivity, not a recommended AA range.
The ten-board panel gives 77 zero set flops and 99 about 43%, versus roughly
12% full-deck opportunities. More iterations cannot fix missing boards.

## Next priorities

1. Finish reviewing and pushing the completed coverage study.
2. Validate lossless future-card symmetry compression for changing external
   ranges. Check both ranges and lock symmetry; reject unsupported inputs.
   Compare CPU/GPU counterfactual values and accumulated strategies against
   uncompressed games before admitting larger experiments.
3. Investigate memory-bounded groups of board states without restarting their
   regrets or averaging independently solved preflop policies. Match the
   resident game's trajectory first. Measure RAM and transfer costs.
4. Preregister a more representative board set and stability tests before
   solving it. The existing 47-flop subset is a feasibility candidate, not an
   accuracy certificate. Preserve separately reserved validation cases.
5. Keep folded-card uncertainty integration separate and explicit. Never leak
   hidden folded cards to a postflop strategy or replace the joint posterior
   by unrelated marginal corrections.

## Operational constraints

- Repository: `T:\Dev\GTOpen`, branch master. Explicitly stage owned files;
  many unrelated research logs and artifacts are untracked.
- Preserve production `http://localhost:56708`, all sessions and saves.
  Check `/api/preflop/status`, `/api/status`, `/api/reports/status` before GPU
  research and while it runs. Stop only owned research children if needed.
- One GPU job at a time. Preserve the production app's resident memory.
- Save input/source/binary hashes before each substantive experiment. Do not
  overwrite historical freezes after rebuilding.
- No production deployment merely because a research comparison passes.
- Research remains CPU/GPU correctness focused; CPU optimization is not a goal.
- Use `C:\Program Files\Python312\python.exe`. CUDA NVRTC DLL path is
  `.cuda-nvrtc/nvidia/cuda_nvrtc/bin`. Limit research CPU threads appropriately.
- Push with Windows OpenSSH:
  `git -c core.sshCommand=C:/Windows/System32/OpenSSH/ssh.exe push origin master`.

Update this handoff after each validated step. Keep routine unchanged status
quiet; report meaningful findings, failures or a need for user input.
