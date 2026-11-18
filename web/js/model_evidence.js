// Evidence describes provenance, not the probability that a strategy is correct.
// Keep the short label visible; supporting detail remains keyboard accessible.
// Every kind is named in the summary, so the colour is never the only signal.
// Where space is tight (the Preflop Lab node heading) the same text sits behind
// a small "Evidence" link instead: renderEvidenceLink.
const KINDS = {
  measured: 'measured',
  extrapolated: 'extrapolated',
  fallback: 'fallback',
  contextual_estimate: 'contextual',
  stat_derived: 'from stats',
  saved_policy: 'saved policy',
  stored_policy: 'saved policy',
  solver: 'solver',
  adaptive: 'adaptive',
  manual_lock: 'manual lock',
  frozen_solver: 'frozen solver',
  unavailable: 'unavailable',
  pending: 'pending',
};
const VOCABULARY = 'measured = real decisions · extrapolated = beyond the sample · fallback = a default fills in · '
  + 'contextual = this situation’s model · from stats = generated from HUD numbers · saved policy = a stored range set · '
  + 'solver = solved equilibrium · adaptive = responds to the solve · manual lock = hand-edited · '
  + 'frozen solver = pinned strategy · unavailable, pending = transient states.';
const CAVEAT = 'Provenance, not a confidence score.';
const kindOf = k => (k in KINDS ? k : 'saved_policy');
const unique = lines => [...new Set(lines.filter(Boolean))];

/** The supporting lines under the headline: source, pooled coverage, details. */
function bodyLines(evidence, extraDetails = []) {
  const lines = [evidence.sizing && evidence.summary, ...(evidence.details || []), ...extraDetails].filter(Boolean);
  const count = key => Number.isInteger(evidence[key]) && evidence[key] >= 0 ? evidence[key] : null;
  if (count('sample_count') != null) {
    const coverage = [`${count('sample_count').toLocaleString()} decisions`];
    if (count('session_count') != null) coverage.push(`${count('session_count').toLocaleString()} sessions`);
    if (count('observed_classes') != null) coverage.push(`${count('observed_classes')} of 169 hand classes`);
    lines.unshift(`Pooled source coverage: ${coverage.join(' · ')}. Prices, stacks and earlier entry details are pooled.`);
  }
  if (evidence.source) lines.unshift(`Source: ${evidence.source}`);
  return unique(lines);
}
const sizingLines = size => unique([size.summary, size.source && `Sizing source: ${size.source}`, ...(size.details || [])]);
const headline = (name, item) => `${name} · ${KINDS[kindOf(item.kind)]} · ${item.label || 'Source not recorded'}`;

/** Everything the evidence box says, as tooltip parts: {head: [...], lines: [...], caveat} or null. */
export function evidenceParts(evidence, extraDetails = []) {
  if (!evidence) return null;
  const head = [headline(evidence.sizing ? 'Hands' : 'Evidence', evidence)];
  if (evidence.sizing) head.push(headline('Sizing', evidence.sizing));
  const lines = [!evidence.sizing && evidence.summary, ...bodyLines(evidence, extraDetails)];
  const sizing = evidence.sizing ? sizingLines(evidence.sizing) : [];
  if (sizing.length) lines.push('Raise sizing:', ...sizing);
  return { head, lines: unique(lines), caveat: CAVEAT };
}
/** The same as plain text, one statement per line. */
export function evidenceText(evidence, extraDetails = []) {
  const parts = evidenceParts(evidence, extraDetails);
  return parts ? [...parts.head, ...parts.lines, '', parts.caveat].join('\n') : '';
}

const esc = s => String(s).replace(/[&<>"']/g, c =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
/** A small "Evidence" link whose tooltip holds the whole evidence text (hover, focus, click or tap). */
export function renderEvidenceLink(host, evidence) {
  if (!host) return;
  const parts = evidenceParts(evidence);
  host.classList.toggle('hidden', !parts);
  if (!parts) { host.replaceChildren(); return; }
  let link = host.querySelector('button.model-evidence-link');
  if (!link) {
    link = document.createElement('button');
    link.type = 'button';
    link.className = 'model-evidence-link';
    link.textContent = 'Evidence';
    link.dataset.tipClick = '';
    host.replaceChildren(link);
  }
  const text = evidenceText(evidence);
  if (link.dataset.tip === text) return;
  link.dataset.kind = kindOf(evidence.kind);
  link.dataset.tip = text;
  // server text is escaped; the tip keeps line breaks (white-space: pre-line)
  link.dataset.tipHtml = `<b class="tip-title">${parts.head.map(esc).join('\n')}</b>${parts.lines.map(esc).join('\n')}\n\n<span class="dim">${esc(parts.caveat)}</span>`;
}

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
  details.dataset.kind = kindOf(evidence.kind);
  details.open = expanded;
  const summary = document.createElement('summary');
  summary.dataset.tip = VOCABULARY;
  const addPart = (name, item) => {
    const part = document.createElement('span');
    part.className = 'model-evidence-part';
    part.dataset.kind = kindOf(item.kind);
    const prefix = document.createElement('span');
    prefix.className = 'model-evidence-prefix';
    prefix.textContent = `${name} · `;
    const kind = document.createElement('span');
    kind.className = 'model-evidence-kind';
    kind.textContent = `${KINDS[kindOf(item.kind)]} · `;
    const label = document.createElement('strong');
    label.textContent = item.label || 'Source not recorded';
    part.append(prefix, kind, label);
    summary.appendChild(part);
  };
  addPart(evidence.sizing ? 'Hands' : 'Evidence', evidence);
  if (evidence.sizing) addPart('Sizing', evidence.sizing);
  else {
    const short = document.createElement('span');
    short.className = 'model-evidence-summary';
    short.textContent = evidence.summary ? `\u00a0· ${evidence.summary}` : '';
    summary.appendChild(short);
  }

  const body = document.createElement('div');
  body.className = 'model-evidence-body';
  for (const line of bodyLines(evidence, extraDetails)) {
    const p = document.createElement('p');
    p.textContent = line;
    body.appendChild(p);
  }
  if (evidence.sizing) {
    const sizing = document.createElement('section');
    sizing.className = 'model-evidence-sizing';
    const heading = document.createElement('strong');
    heading.textContent = 'Raise sizing';
    sizing.appendChild(heading);
    for (const line of sizingLines(evidence.sizing)) {
      const p = document.createElement('p');
      p.textContent = line;
      sizing.appendChild(p);
    }
    body.appendChild(sizing);
  }
  details.append(summary, body);
  host.appendChild(details);
  // The caveat sits outside `details`: one line under the badge, visible
  // while the evidence is collapsed.
  const caveat = document.createElement('p');
  caveat.className = 'model-evidence-caveat';
  caveat.setAttribute('role', 'note');
  caveat.textContent = CAVEAT;
  host.appendChild(caveat);
}
