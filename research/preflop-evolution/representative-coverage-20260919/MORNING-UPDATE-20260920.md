# Morning research update — 20 September 2026

Useful progress, but no new production-ready accuracy upgrade yet. The overnight work is complete and the live app on port 56708 was left unchanged.

## Broader board coverage helped

The completed study evaluated strategies trained on 10 versus 47 flops. On the broader 164-board evaluation, the combined profitable deviation fell from 2.70446 bb to 0.63792 bb. Lower is better: it measures how much improvement opponents could find by changing their play within this restricted two-player branch. It is not a full-game accuracy percentage or a head-to-head win rate.

Both strategies had looked well solved on their own training boards. The result reinforces that solving a narrow selection more thoroughly does not remove errors caused by missing board coverage. The 164-board evaluation includes training boards; independently reserved cases are reported separately in the [study review](POPULATION-TRANSFER-REVIEW.md).

![Board coverage comparison](population-transfer-comparison.png)

## A promising exact memory-saving route

Storing only exact suit-related duplicates between games preserved results through 24 small fixtures, 24 larger fixtures and 720 repeated game/player passes. The calculation itself still uses the explicit GPU solver. This avoids relying on the separate compact traversal path whose changing-range behavior remains unqualified.

This is a test-only prototype. Production integration, error handling and full memory accounting remain. In particular, unused per-game pinned staging allocations still need to be shared or released.

The 164-board plan estimates 123.18 GB of full strategy arrays, or 89.48 GB parked compactly. At the morning snapshot, 100.88 GB of RAM was available. Preserving a 20 GB system reserve leaves an 8.60 GB shortfall even for the compact arrays alone, before metadata and temporary buffers. The full run was therefore not started.

See [larger storage checks](../symmetric-bridge-20260919/HOST-ORBIT-LARGE-REVIEW.md) and [720-pass workspace checks](../symmetric-bridge-20260919/HOST-PAGING-REVIEW.md).

## Other results

- A research-only transfer optimization preserved checkpoints exactly, transferred 16.67% fewer bytes and reduced runtime by 5.56% in one fresh sequential benchmark pair. This is not a live-app speed claim. See [qualification](PAGING-FINAL-QUALIFICATION.md).
- A CPU/GPU difference when the opponent range is zero was isolated. Identical-state GPU replay checks passed; trajectories with fixed ranges settled closely, but changing-range probe discrepancies remain. The evidence does not justify promoting the compact traversal solver.

## Recommended next steps

Integrate the exact storage approach into the research solver, remove redundant staging allocations and measure the entire memory footprint. Then choose a broader training panel that fits safely, or add bounded cold storage, and test on fresh reserved cases. Keep deployment separate until accuracy and integration checks pass.

All research jobs had finished at the 08:33 Adelaide check. Production 56708 remained listening. Raw evidence and resumable research state are retained; no saved games were replaced.
