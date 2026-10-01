# Relative training finished; baseline continuation verified

Both relative-input runs completed all 64 registered cycles. Their successful arm outcomes match the exact published progress digests. Independently checked each final checkpoint and all 65 referenced model files per run: played generations 0 through 63, with generation 64 kept separate and unplayed. This observation verifies identities and bank metadata. It does not replay archive payloads, qualify complete-policy inference, or establish poker accuracy.

The same service-owned coordinator remains live. Its A-baseline worker is PID 92220, created 1790826750.308631, parent 90820, and resumes after completed cycle 60. The B-baseline worker is still queued at this observation. No cycle or scientific attempt was repeated. The evaluation-only helper remains live and waiting for all four banks.

The scheduler can admit at most two arms, but reserves scratch and remaining retained growth before each launch. At this baseline transition, 53.242 GB of logical evidence plus two 8 GB scratch reservations and two 1 GB growth reservations exceeds the unchanged 70 GB allowance. Thus only one baseline initially runs. These reservations are estimates rather than proven worst-case bounds. The availability of GPU memory does not remove this temporary evidence constraint. Do not raise the cap, change the admitted scheduler, or restart a scientific job to increase concurrency.

Evidence: `stack-context-pressure-baseline-transition-20261001-v1.json`, SHA256 `1618d5af66505e4feba88a9836618f5b7226535567d6939ec362740da70bee30`; observer source preserved alongside it. No fits, native jobs or GPU calls were launched by the observation. Production port 56708 is unchanged.

Remaining: actual completion of both baseline banks; the actual 64-bank CUDA/reference resource gate; the registered fresh 4096-deal comparison at each of seven depths; independent scientific readback; plain-English analysis. Separate prediction diagnostics remain unregistered and unadmitted. Broad preflop, GTO Wizard and multiway accuracy remain unproven.
