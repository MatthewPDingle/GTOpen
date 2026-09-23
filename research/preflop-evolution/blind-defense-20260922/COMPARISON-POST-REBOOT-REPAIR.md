# Comparison activity-check repair

All seven stages of `sampled-visible-hybrid-completion-study-v1` completed
successfully, including BB and BTN independent audits. The subsequent
`accuracy-followthrough-v1` queue stopped at its first comparison stage, before
writing a comparison registration/result or launching any equity work.

Its imported historical comparison reader used `loopback_research_validation`
and rejected the empty post-reboot preflop session. The current independent
`reboot_research_idle_v1` check passed: blank preflop state with zero iterations,
the session endpoint returning the exact no-game error, postflop idle and no
running reports. No active solve was bypassed or stopped.

`post_reboot_comparison_reader_v1.py` keeps the historical reader's complete
read/aggregation function unchanged and imports the already verified activity
guard instead. `hu_visible_hybrid_completion_comparison_v2_20260923.py` uses that
reader, records its source and guard hashes, and writes separate v2 outputs.
There are no policy, payoff, configuration, sample-count or statistical changes.
The original queue status and failure log remain preserved; it is not restarted.
Remaining prepared jobs will be launched separately after the v2 comparison.
