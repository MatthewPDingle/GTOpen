# Large-game preflop refinement research

Research branch only. The app on port 56708 is unchanged.

- [Status](STATUS.md): current qualification and outstanding work.
- [Protocol](PROTOCOL.md): registered tests, limits and changes after failures.
- [Initial large-game results](STAGE1.md): exact preservation and six-path checks.
- [GPU variance-reduction results](CV_RESULTS.md): numerically sound prototype,
  rejected for current speed and memory costs.

`raw/` retains successful and failed runs, input and executable hashes,
per-hand conditional audits, canonical full-model checks, and test logs.
Scripts use read-only live status checks and stop their own research work if
the user starts a solve or report. They never restart the app or load research
saves into it. Run hardware workloads serially.

Locally refined saves use different local DCFR ages. They are offline outputs
and must not be resumed as ordinary global solver sessions. Conditional gates
measure one-step deviations within the existing coupled-deck continuation
model; they do not establish physical-deal equity accuracy.
