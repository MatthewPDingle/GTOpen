# Separating suit coverage from betting-menu changes

The previous literal two-board pilot used both 50% and 75% bets. The new
coverage runs use 50% bets to fit ten boards in memory. Those are two changes,
so comparing the previous AA mix directly with this run cannot identify the
cause of a difference.

Add two controls, fixed before execution and without changing the selected
boards: the old two literal boards with 50% bets; and the old two boards
closed under suit relabeling with both 50% and 75% bets. Solve each for 2,000
iterations. Together with the existing old two-board result and the new
old-two-orbits result this forms a two-by-two comparison. Preserve all
results, even if they do not favor the new construction. These controls do
not use the reserved board panel.
