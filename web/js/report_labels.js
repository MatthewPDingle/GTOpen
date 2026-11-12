// Presentation only: a report's identity arrives normalized in the library
// list (`summary`, built by /api/reports), so nothing here parses a name.

const STREET = ['F', 'T', 'R'];

export function fmtNum(x) {
  if (!Number.isFinite(x)) return '—';
  return Number.isInteger(x) ? String(x) : String(+x.toFixed(2));
}

/** Villain model label, or GTO when the run had no modeled villain. */
export function modelLabel(villain) {
  return villain ? `vs ${String(villain).replace(/^Data\s*·\s*/, '')}` : 'GTO';
}

/** The report card's two identity lines, from the list endpoint's summary:
 *  the spot on the card, the solved settings in the card's tooltip. */
export function reportCardFacts(summary = {}) {
  const context = [
    summary.stakes ? `$${summary.stakes}` : '',
    summary.bb ? `${fmtNum(summary.bb)}bb` : '',
    summary.players ? `${summary.players}-max` : '',
    summary.rake_pct != null ? `${fmtNum(summary.rake_pct)}% rake` : '',
  ].filter(Boolean).join(' · ');
  const menu = side => (summary[`${side}_sizes`] || [])
    .map((s, i) => `${STREET[i] || i + 1} ${s}`).join(' · ');
  const oop = menu('oop'), ip = menu('ip');
  const sizes = !oop && !ip ? '' : oop === ip ? `sizes ${oop}` : `sizes OOP ${oop} · IP ${ip}`;
  const detail = [
    summary.pot != null ? `pot ${fmtNum(summary.pot)}` : '',
    summary.stack != null ? `stack ${fmtNum(summary.stack)}` : '',
    sizes,
    summary.sweep_sizes?.length ? `swept ${summary.sweep_sizes.map(fmtNum).join('/')}` : '',
    summary.target != null ? `target ${fmtNum(summary.target)}%` : '',
  ].filter(Boolean).join(' · ');
  return { context, detail };
}

export function reportTimestamp(created) {
  if (!Number.isFinite(created) || created <= 0) return 'Date unavailable';
  return new Intl.DateTimeFormat('en-AU', {
    day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false,
  }).format(new Date(created * 1000));
}
