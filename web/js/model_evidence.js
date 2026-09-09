// Evidence describes provenance, not the probability that a strategy is correct.
// Keep the short label visible; supporting detail remains keyboard accessible.
const rendered = new WeakMap();
export function renderModelEvidence(host, evidence, extraDetails = []) {
  if (!host) return;
  const signature = JSON.stringify([evidence || null, extraDetails]);
  if (rendered.get(host) === signature) return;
  rendered.set(host, signature);
  const expanded = host.querySelector('details')?.open || false;
  host.replaceChildren();
  host.classList.toggle('hidden', !evidence);
  if (!evidence) return;

  const details = document.createElement('details');
  details.className = 'model-evidence';
  const kinds = ['measured', 'extrapolated', 'fallback', 'contextual_estimate', 'stat_derived', 'saved_policy', 'solver', 'adaptive', 'manual_lock', 'frozen_solver', 'unavailable', 'pending'];
  details.dataset.kind = kinds.includes(evidence.kind) ? evidence.kind : 'saved_policy';
  details.open = expanded;
  const summary = document.createElement('summary');
  const prefix = document.createElement('span');
  prefix.className = 'model-evidence-prefix';
  prefix.textContent = 'Evidence';
  const label = document.createElement('strong');
  label.textContent = evidence.label || 'Source not recorded';
  const short = document.createElement('span');
  short.className = 'model-evidence-summary';
  short.textContent = evidence.summary || '';
  summary.append(prefix, label, short);

  const body = document.createElement('div');
  body.className = 'model-evidence-body';
  const lines = [...(evidence.details || []), ...extraDetails].filter(Boolean);
  const count = key => Number.isInteger(evidence[key]) && evidence[key] >= 0 ? evidence[key] : null;
  if (count('sample_count') != null) {
    const coverage = [`${count('sample_count').toLocaleString()} decisions`];
    if (count('session_count') != null) coverage.push(`${count('session_count').toLocaleString()} sessions`);
    if (count('observed_classes') != null) coverage.push(`${count('observed_classes')} of 169 hand classes`);
    lines.unshift(`Pooled source coverage: ${coverage.join(' · ')}. Prices, stacks and earlier entry details are pooled.`);
  }
  if (evidence.source) lines.unshift(`Source: ${evidence.source}`);
  for (const line of [...new Set(lines)]) {
    const p = document.createElement('p');
    p.textContent = line;
    body.appendChild(p);
  }
  const caveat = document.createElement('p');
  caveat.className = 'model-evidence-caveat';
  caveat.textContent = 'Evidence describes where the frequencies came from; it is not a confidence score or proof of an optimal strategy.';
  body.appendChild(caveat);
  details.append(summary, body);
  host.appendChild(details);
}
