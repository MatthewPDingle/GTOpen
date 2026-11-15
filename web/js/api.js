// Thin API layer.

/** Longest error detail the UI will show — the first line of an error body,
 *  clamped, never a whole HTML response. */
const MAX_DETAIL = 180;

/** Plain text out of a body that may be an HTML error page. */
function stripMarkup(text) {
  if (!text) return '';
  if (!/<[a-z!/]/i.test(text)) return text;
  try {
    const doc = new DOMParser().parseFromString(text, 'text/html');
    return doc.body ? (doc.body.textContent || '') : '';
  } catch {
    return text.replace(/<[^>]*>/g, ' ');
  }
}

/** First non-empty line of an error body, whitespace collapsed and clamped. */
function summarize(text) {
  const first = stripMarkup(text)
    .split(/\r?\n/)
    .map(line => line.trim())
    .find(Boolean) || '';
  const clean = first.replace(/\s+/g, ' ').trim();
  if (!clean) return '';
  return clean.length > MAX_DETAIL ? `${clean.slice(0, MAX_DETAIL - 1).trimEnd()}…` : clean;
}

/** A failed API call: HTTP status (0 = no response) plus a clamped detail. */
export class ApiError extends Error {
  constructor(status, detail, url) {
    super(status ? `${status} — ${detail || 'request failed'}` : (detail || 'server unreachable'));
    this.name = 'ApiError';
    this.status = status;
    this.url = url;
  }
}

/** Coerce anything thrown into an Error with a presentation-ready message. */
export function normalizeError(e) {
  if (e instanceof Error) return e;
  return new Error(summarize(String(e)) || 'unknown error');
}

async function req(method, url, body) {
  const opts = { method, headers: {} };
  if (body !== undefined) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }
  let res;
  try {
    res = await fetch(url, opts);
  } catch {
    throw new ApiError(0, 'server unreachable', url);
  }
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new ApiError(res.status, summarize(text), url);
  }
  try {
    return await res.json();
  } catch {
    throw new ApiError(res.status, 'invalid JSON response', url);
  }
}

export const api = {
  buildSpot: cfg => req('POST', '/api/spot', cfg),
  solve: opts => req('POST', '/api/solve', opts),
  stop: () => req('POST', '/api/stop'),
  status: () => req('GET', '/api/status'),
  node: path => req('POST', '/api/node', { path }),
  exploit: (path, exploiter) => req('POST', '/api/exploit', { path, exploiter }),
  pfBuild: (cfg, model) => req('POST', '/api/preflop/spot' + (model ? `?multiway_model=${encodeURIComponent(model)}` : ''), cfg),
  pfEstimate: cfg => req('POST', '/api/preflop/estimate', cfg),
  pfSolve: opts => req('POST', '/api/preflop/solve', opts || {}),
  pfStop: () => req('POST', '/api/preflop/stop'),
  pfCapabilities: () => req('GET', '/api/preflop/capabilities'),
  pfLeafNets: () => req('GET', '/api/preflop/leafnets'),
  pfStatus: () => req('GET', '/api/preflop/status'),
  pfSession: () => req('GET', '/api/preflop/session'),
  pfNode: path => req('POST', '/api/preflop/node', { path }),
  pfExport: path => req('POST', '/api/preflop/export', { path }),
  pfExport3: path => req('POST', '/api/preflop/export3', { path }),
  pfTable: seats => req('POST', '/api/preflop/table', { seats }),
  pfGenerate: (seat, stats, name, adaptive_from = 0.25) => req('POST', '/api/preflop/generate', { seat, stats, name, adaptive_from }),
  pfContextualPreview: (version, cfg, seat, context) => req('POST', '/api/preflop/contextual-preview', { version, cfg, seat, context }),
  pfModelEvidence: body => req('POST', '/api/preflop/model-evidence', body),
  pfArchetypes: () => req('GET', '/api/preflop/archetypes'),
  rangeLab: () => req('GET', '/api/preflop/rangelab'),
  rangeLabSituations: (tag, variant, depth) => req('POST', '/api/preflop/rangelab/situations', { tag, variant, depth }),
  rangeLabSpot: id => req('POST', '/api/preflop/rangelab/spot', { id }),
  rangeLabMatch: request => req('POST', '/api/preflop/rangelab/match', request),
  rangeLabNode: request => req('POST', '/api/preflop/rangelab/node', request),
  rangeLabExport: request => req('POST', '/api/preflop/rangelab/export', request),
  pfHero: seat => req('POST', '/api/preflop/hero', { seat }),
  pfTrust: trust => req('POST', '/api/preflop/trust', { trust }),
  pfProfiles: () => req('GET', '/api/preflop/profiles'),
  pfProfileSave: (name, profile) => req('POST', '/api/preflop/profiles/save', { name, profile }),
  pfProfileGet: name => req('POST', '/api/preflop/profiles/get', { name }),
  pfScenarios: () => req('GET', '/api/preflop/scenarios'),
  pfScenarioSave: (name, scenario) => req('POST', '/api/preflop/scenarios/save', { name, scenario }),
  pfScenarioDelete: name => req('POST', '/api/preflop/scenarios/delete', { name }),
  pfSaveGame: name => req('POST', '/api/preflop/save', { name }),
  pfLoadGame: name => req('POST', '/api/preflop/load', { name }),
  pfSavedGames: () => req('GET', '/api/preflop/saves'),
  lock: (path, mode, label, lock_path = false) => req('POST', '/api/lock', { path, mode, label, lock_path }),
  fit: (path, freqs, label, lock_path = false) => req('POST', '/api/fit', { path, freqs, label, lock_path }),
  fitCancel: (path = null) => req('POST', '/api/fit/cancel', { path }),
  fits: () => req('GET', '/api/fits'),
  lockHistory: () => req('GET', '/api/locks/history'),
  lockUndo: () => req('POST', '/api/locks/undo'),
  lockRedo: () => req('POST', '/api/locks/redo'),
  profileLocks: (player, stats, aggressor, pot_type = null, name = null) =>
    req('POST', '/api/profile_locks', { player, stats, aggressor, pot_type, name }),
  profileLocksClear: () => req('DELETE', '/api/profile_locks'),
  trust: trust => req('POST', '/api/trust', { trust }),
  reportsRun: body => req('POST', '/api/reports/run', body),
  reportsStatus: () => req('GET', '/api/reports/status'),
  reportsStop: () => req('POST', '/api/reports/stop'),
  reportsList: () => req('GET', '/api/reports'),
  reportsGet: name => req('POST', '/api/reports/get', { name }),
  reportsLines: (name, line) => req('POST', '/api/reports/lines', { name, line }),
  reportsDelete: name => req('POST', '/api/reports/delete', { name }),
  unlock: path => req('POST', '/api/unlock', { path }),
  locks: () => req('GET', '/api/locks'),
  runouts: path => req('POST', '/api/runouts', { path }),
  parseRange: text => req('POST', '/api/range/parse', { text }),
  presets: () => req('GET', '/api/presets'),
  save: name => req('POST', '/api/save', { name }),
  load: name => req('POST', '/api/load', { name }),
  saves: () => req('GET', '/api/saves'),
};

let toastTimer = null;
export function toast(msg, isError = false) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = isError ? 'show error' : 'show';
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.className = ''; }, isError ? 5000 : 2500);
}
