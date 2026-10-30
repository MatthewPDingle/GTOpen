# Prepared final comparison report

Prepared during the two fixed 78-update board-root training runs. This is
reporting preparation, not a result or evidence of stronger poker play.

`tools/research/board_final_findings_v1.py` defaults to a read-only prerequisite
check. `--run` requires complete candidate training, its independent full
readback, the complete-bank numerical control and its independent review, the
fixed 65,536-deal evaluation (seed 9281101), and all 2,048 evaluation batches
independently checked. It verifies the matching result hashes before reading
the final outcomes. It never trains, draws fresh deals, chooses checkpoints,
or changes production.

The final outputs will include all eight registered payoff contrasts, all 169
hand classes, a plot of all simultaneous intervals, and compute/storage costs.
The descriptive range-consistency measure is explicitly separate from playing
strength. Inconclusive intervals are not presented as equivalence. Unplayed
generation 78 is excluded by the audited evaluation bank.

Costs use each arm's 78 committed update records exactly once. Stage times
overlap; neither their sum nor GPU-fit wall time is GPU utilization. Residual
board wait is separate from board computation. Storage peak means the largest
recorded quiescent boundary measurement, not a continuously measured peak.
Historical control timing is not a controlled speed benchmark; invocation
timers may exclude earlier interruptions and idle gaps. No automatic deployment
or promotion follows a report.

`board_final_findings_control_v1.py` passed synthetic checks covering positive,
negative and inconclusive outcomes, all 169 native class labels, and rejection
of eight malformed/partial reports. It also verified the timing schema of both
finished historical controls and rejected reporting without prerequisites.
No candidate payoff data were opened. Evidence:
`board-final-findings-control-v1-result.json`.

After the final report is rendered, visually review the plot and interpret the
complete results before selecting further research. Training, numerical-control,
evaluation and independent-readback drivers remain unchanged.
