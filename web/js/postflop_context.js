// Contextual betting metadata travels with a player profile, including edits
// to its legacy HUD fields. Never reconstruct a measured profile from those
// visible fields alone.
export function editPostflopStats(original, fields) {
  return { ...structuredClone(original), ...fields };
}

export function hasContextualBetting(stats) {
  return stats?.contextual_betting?.version === 1;
}

export function rootBettingEvidence(evidence) {
  if (!evidence) return '';
  const pct = value => Number.isFinite(value) ? `${value.toFixed(1)}%` : 'unavailable';
  const kind = { donk: 'Flop donk', stab: 'Bet after a check', lead: 'Later-street lead', probe: 'Probe after check-through' }[evidence.kind] || 'Betting';
  const count = Number.isFinite(evidence.opportunities) ? evidence.opportunities.toLocaleString() : '0';
  const observed = Number.isFinite(evidence.observed) ? ` · observed ${pct(evidence.observed)}` : '';
  return `Root · ${kind} · ${count} observations${observed} · target ${pct(evidence.target)} · achieved ${pct(evidence.achieved)}`;
}
