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

/** The request fields for "also keep the earlier play on this line". */
function keepLine(keep) {
  if (keep === 'own') return { lock_path_own: true };
  return { lock_path: !!keep };
}

// One postflop spot is loaded at a time: a heads-up one (/api/*) or a
// three-player one (/api/mw/*). The Setup & Solve and Browse pages call the
// same functions for both; this is the number of players of the loaded spot.
let players = 2;
export const spotPlayers = () => players;
export function setSpotPlayers(n) { players = n === 3 ? 3 : 2; }
const mw = () => players === 3;
/** A spot request for three players carries `ranges`, a heads-up one
 *  `range_oop` / `range_ip`. */
export const isThreeWay = spot => Array.isArray(spot?.ranges);

/** A three-player status from a server older than the merged pages (it used
 *  other field names), read into the names the pages expect. */
function mwStatus(st) {
  if (!st || 'elapsed_secs' in st) return st;
  return {
    ...st,
    elapsed_secs: st.elapsed || 0,
    gpu: st.engine === 'gpu',
    gpu_note: '',
    history: (st.history || []).map(h => Array.isArray(h) ? { iteration: h[0], exploit_pct: h[1] } : h),
    tree: st.tree ? { arena_mb: st.tree.arena_mb_compressed, vram_mb: st.tree.gpu_mb, ...st.tree } : st.tree,
  };
}

export const api = {
  /** Which kind of spot the server holds right now (asked once, on page load). */
  async detectSpot() {
    try {
      const st = await req('GET', '/api/mw/status');
      setSpotPlayers(st?.tree ? 3 : 2);
    } catch { setSpotPlayers(2); }
    return players;
  },
  async buildSpot(cfg) {
    const three = isThreeWay(cfg);
    const info = await req('POST', three ? '/api/mw/spot' : '/api/spot', cfg);
    setSpotPlayers(three ? 3 : 2);
    return info;
  },
  // engine and algorithm are choices of the three-player solve only
  solve: ({ engine, algorithm, ...opts }) => mw()
    ? req('POST', '/api/mw/solve', { ...opts, ...(engine ? { engine } : {}), ...(algorithm ? { algorithm } : {}) })
    : req('POST', '/api/solve', opts),
  stop: () => req('POST', mw() ? '/api/mw/stop' : '/api/stop'),
  status: () => mw() ? req('GET', '/api/mw/status').then(mwStatus) : req('GET', '/api/status'),
  version: () => req('GET', '/api/version'),
  node: path => req('POST', mw() ? '/api/mw/node' : '/api/node', { path }),
  exploit: (path, exploiter) => req('POST', mw() ? '/api/mw/exploit' : '/api/exploit', { path, exploiter }),
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
  // keep: false = lock this decision only; 'own' = also keep the locked
  // player's earlier decisions on the line as solved; 'all' = both players'
  // (all an older server knows)
  lock: (path, mode, label, keep = false) => req('POST', '/api/lock', { path, mode, label, ...keepLine(keep) }),
  fit: (path, freqs, label, keep = false) => req('POST', '/api/fit', { path, freqs, label, ...keepLine(keep) }),
  fitCancel: (path = null) => req('POST', '/api/fit/cancel', { path }),
  fits: () => req('GET', '/api/fits'),
  lockHistory: () => mw() ? Promise.resolve({ undo: [], redo: [] }) : req('GET', '/api/locks/history'),
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
  // a three-player spot has no node locks yet
  locks: () => mw() ? Promise.resolve([]) : req('GET', '/api/locks'),
  locksList: () => mw() ? Promise.resolve({ locks: [], profile: [0, 0] }) : req('GET', '/api/locks/list'),
  locksClear: () => req('POST', '/api/locks/clear'),
  runouts: path => req('POST', '/api/runouts', { path }),
  parseRange: text => req('POST', '/api/range/parse', { text }),
  presets: () => req('GET', '/api/presets'),
  save: name => req('POST', mw() ? '/api/mw/save' : '/api/save', { name }),
  /** Load a saved solve; `n` is how many players it has (from `saves`). */
  async load(name, n = 2) {
    const out = await req('POST', n === 3 ? '/api/mw/load' : '/api/load', { name });
    setSpotPlayers(n);
    return out;
  },
  /** Every saved solve, both kinds: [{ name, players }]. */
  async saves() {
    const [two, three] = await Promise.all([
      req('GET', '/api/saves'),
      req('GET', '/api/mw/saves').catch(() => []),
    ]);
    return [
      ...two.map(name => ({ name, players: 2 })),
      ...three.map(s => ({ name: s.name, players: 3 })),
    ];
  },
};

let toastTimer = null;
export function toast(msg, isError = false) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = isError ? 'show error' : 'show';
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.className = ''; }, isError ? 5000 : 2500);
}
