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
  if (publication.converged) return `Target reached at iteration ${iteration} (preflop approximation)`;
  const measured = publication.accuracy_iteration;
  const gap = Number.isFinite(publication.gap_total) ? publication.gap_total.toFixed(4) : null;
  const accuracy = measured == null ? 'accuracy not measured'
    : `gap ${gap ?? '?'} bb measured at iteration ${measured}`;
  return `Preview · iteration ${iteration} · ${accuracy}`;
}
export function solveCompletionLabel(status) {
  if (status.stop_reason === 'target_reached') return 'Target gap reached';
  if (status.stop_reason === 'iteration_limit') return 'Iteration limit reached · target not reached';
  if (status.state === 'stopped') return 'Stopped · current strategy retained';
  return 'Run complete · check the measured gap';
}
