// A published snapshot is independent of the live solve counter.
export function publishedIteration(status) {
  return Number.isInteger(status?.published_iteration) ? status.published_iteration : (status?.iteration || 0);
}
export function publicationKey(status) {
  return `${publishedIteration(status)}:${status?.accuracy_iteration ?? ''}:${status?.stop_reason || ''}`;
}
export function publicationLabel(publication) {
  if (!publication) return '';
  const iteration = publication.published_iteration;
  if (iteration < 2) return 'Preparing a learned strategy preview';
  const fast = publication.multiway_model === 'coupled_preview64_v1';
  if (publication.converged) return fast
    ? `Fast estimate target reached at iteration ${iteration} · Reference error not measured`
    : `Target reached at iteration ${iteration} (preflop approximation)`;
  const measured = publication.accuracy_iteration;
  const gap = Number.isFinite(publication.gap_total) ? publication.gap_total.toFixed(4) : null;
  const accuracy = measured == null ? 'accuracy not measured'
    : `gap ${gap ?? '?'} bb measured at iteration ${measured}`;
  return `${fast ? 'Experimental fast preview' : 'Preview'} · iteration ${iteration} · ${accuracy}${fast ? ' · Reference error not measured' : ''}`;
}
export function solveCompletionLabel(status) {
  if (status.stop_reason === 'target_reached') return 'Target gap reached';
  if (status.stop_reason === 'iteration_limit') return 'Iteration limit reached · target not reached';
  if (status.state === 'stopped') return 'Stopped · current strategy retained';
  return 'Run complete · check the measured gap';
}

export function freshBuildUrl(model) {
  if (!model || model === 'coupled_deck_v1') return '/api/preflop/spot';
  if (model !== 'coupled_preview64_v1') throw new Error('Unsupported fresh-build multiway model');
  return `/api/preflop/spot?multiway_model=${encodeURIComponent(model)}`;
}
