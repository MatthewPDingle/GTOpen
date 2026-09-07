// Presentation only: keep original report names as API/file identifiers.
export function reportLabel(name, villain) {
  let title = String(name || 'Untitled report').replace(/^overnight-\d{8}-\d{6}-[a-f\d]+\s+/i, '');
  let context = '';
  const scenario = title.match(/^(\d+-max)\s+(\d+bb)\s+\$?(\d+[/-]\d+)(?:\s*:\s*.*?\brake)?\s+(?=[A-Z]\s+(?:BTN|CO|BB|SB|UTG|HJ|MP))/i);
  if (scenario) {
    context = `$${scenario[3].replace('-', '/')} · ${scenario[2]} · ${scenario[1]}`;
    title = title.slice(scenario[0].length).replace(/^[A-Z]\s+/, '');
  }
  const variant = title.match(/\s+-\s+(GTO postflop|(?:fish|TAG) (?:station|folder))$/i);
  if (variant) title = title.slice(0, variant.index);
  if (villain) title = title.replace(/\s+vs (?:fish|TAG)$/i, '');
  return { title, context, model: villain ? `vs ${String(villain).replace(/^Data\s*·\s*/, '')}` : 'GTO' };
}

export function reportTimestamp(created) {
  if (!Number.isFinite(created) || created <= 0) return 'Date unavailable';
  return new Intl.DateTimeFormat('en-AU', {
    day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false,
  }).format(new Date(created * 1000));
}
