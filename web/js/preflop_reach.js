// Explain when global convergence does not validate a rare branch.
export function branchWarning(view) {
  if (!view?.low_reach) return '';
  const p = view.branch_probability;
  const frequency = p > 0 ? `${(p * 100).toPrecision(3)}%` : '0%';
  return `Rare branch · ${frequency} modeled reach. The whole-game accuracy target does not establish accuracy here. Treat these responses as unverified.`;
}
