// BEST SIZE — size-sweep reports ("dynamic sizing").
//
// A sweep report (kind "sweep", see crates/server/src/sweep.rs) solved one
// single-size tree per candidate size of ONE player's first bet on every
// flop, then refined between the best size's neighbours. Per flop it holds
// every solved point (size, EV for the chooser in % pot, exploitability,
// bet frequency) and a verdict: best size, best grid size, and the tie band
// (sizes whose EV gap to the best is inside the two solves' combined
// exploitability — the solves cannot tell them apart).
//
// This module renders the REPORTS "Best size" view of a sweep and the
// Browse "find best size" panel. Everything recomputes client-side for the
// texture filter, mirroring solver::size_sweep::summarize.

import { api } from './api.js';
import { SUIT_GLYPH } from './cards.js';
import { RANKS, cardsOf, texOf, TEX } from './textures.js';

const esc = s => String(s).replace(/[&<>"']/g, c =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const posName = p => (p === 0 ? 'OOP' : 'IP');
const STREETS = ['flop', 'turn', 'river'];
const fmtBoard = b => (b.match(/.{2}/g) || []).map(c => c[0] + (SUIT_GLYPH[c[1]] || c[1])).join('');
const fmtSize = s => `${+(+s).toFixed(1)}%`;
const fmtPct = (x, d = 2) => `${(+x).toFixed(d)}%`;
const near = (a, b) => Math.abs(a - b) < 1e-6;
/** The size token the server writes into the spot ("33", "12.5"). */
export const sizeToken = s => String(+(+s).toFixed(3));

// ---------------------------------------------------------------- color ----

/** Ordinal one-hue ramp for n bet sizes (small → large), in the app's
 *  bet reds: lightness falls monotonically with size, so order reads in the
 *  color; identity never relies on it alone (labels, legend, table). */
const rampL = t => 0.88 - 0.42 * t;
export function sizeRamp(n) {
  const out = [];
  for (let i = 0; i < n; i++) {
    const t = n > 1 ? i / (n - 1) : 0;
    out.push(oklchHex(rampL(t), 0.10 + 0.08 * t, 55 - 50 * t));
  }
  return out;
}
/** Readable label ink on ramp step i of n (dark ink on the light steps). */
const rampInk = (i, n) => rampL(n > 1 ? i / (n - 1) : 0) >= 0.62 ? '#141414' : 'var(--ink)';
function oklchHex(L, C, h) {
  const a = C * Math.cos(h * Math.PI / 180), b = C * Math.sin(h * Math.PI / 180);
  const l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3;
  const m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3;
  const s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3;
  const rgb = [
    4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
    -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
    -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
  ];
  return '#' + rgb.map(x => {
    x = Math.max(0, Math.min(1, x));
    x = x <= 0.0031308 ? 12.92 * x : 1.055 * x ** (1 / 2.4) - 0.055;
    return Math.round(x * 255).toString(16).padStart(2, '0');
  }).join('');
}

// ------------------------------------------------------------- summary ----

/** solver::size_sweep::summarize over a filtered set of sweep rows. */
export function summarize(grid, rows) {
  const fixed = grid.map(size => ({ size, lost: 0, lostGrid: 0, best: 0, tie: 0 }));
  let w = 0, gain = 0, allTie = 0;
  for (const r of rows) {
    const wt = r.weight || 1;
    const gridPts = r.points.filter(p => !p.refined);
    if (!gridPts.length) continue;
    const gridBest = Math.max(...gridPts.map(p => p.ev_pct));
    w += wt;
    gain += wt * Math.max(0, r.verdict.best_ev_pct - gridBest);
    let every = true;
    for (const f of fixed) {
      const p = gridPts.find(q => near(q.size, f.size));
      if (!p) { every = false; continue; }
      f.lost += wt * Math.max(0, r.verdict.best_ev_pct - p.ev_pct);
      f.lostGrid += wt * Math.max(0, gridBest - p.ev_pct);
      if (near(r.verdict.best_grid, f.size)) f.best += wt;
      if (r.verdict.ties.some(t => near(t, f.size))) f.tie += wt; else every = false;
    }
    if (every) allTie += wt;
  }
  const d = w > 0 ? w : 1;
  return {
    n: rows.length,
    fixed: fixed.map(f => ({ size: f.size, lost: f.lost / d, lostGrid: f.lostGrid / d, best: f.best / d, tie: f.tie / d })),
    gain: gain / d,
    allTie: allTie / d,
  };
}

/** Where the swept bet is made, in words. */
export function sweepDecision(rep) {
  const sw = rep.sweep || {};
  const street = STREETS[Math.max(0, ((rep.flops?.[0]?.board || rep.spot?.board || '').length / 2) - 3)] || 'flop';
  return sw.player === 1
    ? `IP's ${street} bet after a check`
    : `OOP's first ${street} bet`;
}

/** The sweep's spot with the swept bet set to one size (what each variant
 *  and Open in Browse use). */
export function spotWithSize(rep, board, size) {
  const spot = JSON.parse(JSON.stringify(rep.spot));
  const street = Math.max(0, Math.min(2, board.length / 2 - 3));
  const side = rep.sweep.player === 0 ? spot.oop : spot.ip;
  side[street] = { ...side[street], bet: sizeToken(size) };
  return spot;
}

// ---------------------------------------------------------- EV sparkline ----

/** A plain text button that inherits its cell's type (sort headers, cells). */
const PLAIN_BTN = 'background:none;border:0;padding:0;margin:0;font:inherit;color:inherit;text-align:left;cursor:pointer';

/** Small SVG of EV (% pot) against size (log scale) for one flop: grid
 *  points as dots, refined points as rings, the tie band shaded. The x axis
 *  carries its size ticks and the y axis its top EV. */
function evCurve(row, { width = 168, height = 44, colors, grid } = {}) {
  const pts = row.points.slice().sort((a, b) => a.size - b.size);
  if (!pts.length) return '';
  const lx = s => Math.log(s);
  const x0 = lx(pts[0].size), x1 = lx(pts[pts.length - 1].size);
  const evs = pts.map(p => p.ev_pct);
  const y0 = Math.min(...evs), y1 = Math.max(...evs);
  const pad = 5, base = height - 12;
  const X = s => pad + (x1 > x0 ? (lx(s) - x0) / (x1 - x0) : 0.5) * (width - 2 * pad);
  const Y = e => 8 + (1 - (y1 > y0 ? (e - y0) / (y1 - y0) : 0.5)) * (base - 12);
  const [b0, b1] = row.verdict.band;
  const band = `<rect x="${X(b0) - 3}" y="1" width="${Math.max(6, X(b1) - X(b0) + 6)}" height="${base}" rx="3" fill="var(--accent-soft)"/>`;
  const axis = `<line x1="${pad}" x2="${width - pad}" y1="${base}" y2="${base}" stroke="var(--line2)"/>` +
    `<line x1="${pad}" x2="${width - pad}" y1="${Y(y1)}" y2="${Y(y1)}" stroke="var(--line)" stroke-dasharray="2 3"/>`;
  const ticks = [pts[0].size, pts[Math.floor(pts.length / 2)].size, pts[pts.length - 1].size]
    .filter((s, i, a) => a.indexOf(s) === i)
    .map(s => `<text x="${X(s)}" y="${height - 2}" text-anchor="middle" font-size="7" ` +
      `font-family="var(--font-data)" fill="var(--ink-faint)">${fmtSize(s)}</text>`).join('') +
    `<text x="${pad}" y="${Y(y1) - 2}" font-size="7" font-family="var(--font-data)" fill="var(--ink-faint)">${fmtPct(y1, 0)}</text>`;
  const line = `<polyline fill="none" stroke="var(--ink-dim)" stroke-width="1.5" points="${pts.map(p => `${X(p.size).toFixed(1)},${Y(p.ev_pct).toFixed(1)}`).join(' ')}"/>`;
  const dots = pts.map(p => {
    const gi = grid.findIndex(g => near(g, p.size));
    const best = near(p.size, row.verdict.best);
    const fill = p.refined ? 'var(--panel)' : (colors[gi] || 'var(--ink)');
    return `<circle cx="${X(p.size).toFixed(1)}" cy="${Y(p.ev_pct).toFixed(1)}" r="${best ? 4 : 3}" fill="${fill}" stroke="${best ? 'var(--accent)' : (p.refined ? 'var(--ink-dim)' : 'var(--panel)')}" stroke-width="${best ? 2 : 1.5}"/>`;
  }).join('');
  return `<svg class="bs-curve" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" aria-hidden="true">${band}${axis}${line}${dots}${ticks}</svg>`;
}

/** The sparkline's swatch legend. */
const curveLegend = `<div class="legend bs-legend">` +
  `<span><span class="bs-swatch" style="background:var(--accent-soft)"></span>tie band</span>` +
  `<span><span class="bs-swatch bs-refined"></span>refinement</span>` +
  `<span><span class="bs-swatch" style="background:var(--panel);border:2px solid var(--accent);box-sizing:border-box"></span>best</span></div>`;

const bestPoint = row => row.points.find(p => near(p.size, row.verdict.best)) || row.points[0];
const bandText = v => near(v.band[0], v.band[1]) ? fmtSize(v.best) : `${fmtSize(v.band[0])}–${fmtSize(v.band[1])}`;
const edgeNote = (v, grid) => v.edge
  ? (near(v.best_grid, grid[0]) ? ' · at the smallest size, smaller may be better' : ' · at the largest size, larger may be better')
  : '';

// ------------------------------------------------------------ the view ----

/** The REPORTS Best size view. `ctx`: { toast, openInBrowse(spot, board),
 *  openVariant(name, board) }. Returns { render(rep), name }. */
export function initBestSizeView(el, ctx) {
  const S = { rep: null, tex: 'all', sort: { key: 'rank', dir: -1 }, selected: null, fixed: null };

  function rowsOf() {
    const rows = (S.rep?.flops || []).filter(r => r.board.length !== 6 || texOf(r.board)[S.tex]);
    const { key, dir } = S.sort;
    const val = r => {
      switch (key) {
        case 'best': return r.verdict.best;
        case 'width': return Math.log(r.verdict.band[1] / r.verdict.band[0]);
        case 'ev': return r.verdict.best_ev_pct;
        case 'lost': {
          const p = r.points.find(q => !q.refined && near(q.size, S.fixed));
          return p ? r.verdict.best_ev_pct - p.ev_pct : 0;
        }
        default: {
          const rs = cardsOf(r.board).map(c => RANKS.indexOf(c[0])).sort((a, b) => b - a);
          return rs[0] * 169 + rs[1] * 13 + rs[2];
        }
      }
    };
    return rows.sort((a, b) => dir * (val(b) - val(a)));
  }

  function render(rep) {
    if (rep !== undefined) {
      if (rep?.name !== S.rep?.name) { S.selected = null; S.fixed = null; }
      S.rep = rep;
    }
    el.classList.toggle('hidden', !S.rep);
    if (!S.rep) { el.innerHTML = ''; return; }
    const r = S.rep;
    const grid = r.grid || r.sweep.sizes;
    const colors = sizeRamp(grid.length);
    const all = rowsOf();
    const sum = summarize(grid, all);
    const bestFixed = sum.fixed.slice().sort((a, b) => a.lost - b.lost)[0];
    if (S.fixed == null || !grid.some(g => near(g, S.fixed))) S.fixed = bestFixed?.size ?? grid[0];
    const cpu = r.flops.filter(f => f.points.some(p => p.engine === 'cpu')).length;
    const engine = r.flops.length ? (cpu ? ` · ⚠ ${cpu} of ${r.flops.length} flops solved on CPU` : ' · ⚡ GPU') : '';
    const solves = r.flops.reduce((n, f) => n + f.points.length, 0);
    const secs = r.flops.reduce((n, f) => n + f.points.reduce((m, p) => m + (p.seconds || 0), 0), 0);
    const variants = new Map((r.variants || []).map(v => [v.size, v.name]));

    const head =
      // the sweep viewer is its own mutually exclusive Reports view, so its
      // title is that view's h1 (CSS: #rep-sweep-viewer h1)
      `<div class="pfl-nodehead"><h1 class="bs-title" title="${esc(r.name)}">${esc(r.name)}</h1></div>` +
      `<div class="bs-context">Best size of <b>${esc(sweepDecision(r))}</b> · sizes ${grid.map(fmtSize).join(' / ')} pot · ` +
      `${r.flops.length} flops${r.complete ? '' : ' · PARTIAL RUN'}${r.villain ? ` · vs ${esc(r.villain.name)}` : ''}</div>` +
      `<details class="rep-settings"><summary>Sweep settings</summary><div class="mono dim bs-settings">` +
      `pot ${r.spot.starting_pot} · stack ${r.spot.effective_stack} · rake ${r.spot.rake_pct}% · ` +
      `target ${r.target_pct}% pot per solve · up to ${r.sweep.refine} refinement solves per flop · ` +
      `${solves} solves in ${(secs / 60).toFixed(1)} min${engine}. The rest of the tree uses the report's menu: ` +
      (r.spot.oop || []).map((s, i) => `${['F', 'T', 'R'][i]} OOP ${esc(s.bet || '—')} / IP ${esc((r.spot.ip[i] || {}).bet || '—')}`).join(' · ') +
      `.</div></details>`;

    const filters = `<div class="rep-filter-controls"><span class="dim">Filter flops</span><div class="seg" id="bs-tex" aria-label="Filter flops">` +
      TEX.map(([k, l]) => `<button type="button" data-t="${k}" aria-pressed="${S.tex === k}" class="${S.tex === k ? 'active' : ''}">${l}</button>`).join('') +
      `</div></div>`;

    const tiles = `<div class="bs-tiles">` +
      tile('Best single size', bestFixed ? fmtSize(bestFixed.size) : '—',
        bestFixed ? `loses ${fmtPct(bestFixed.lost)} pot vs each flop's best` : '',
        'EV lost on average against using each flop’s own best size.') +
      tile('Per-flop sizing gain', bestFixed ? `+${fmtPct(bestFixed.lostGrid)}` : '—', 'pot, best grid size per flop',
        'Gained by choosing the best grid size flop by flop instead of always using the best single size. Compare it with the solves’ target accuracy before reading much into it.') +
      tile('Refinement gain', `+${fmtPct(sum.gain)}`, 'pot over the best grid size',
        'Extra EV found by refining between the best grid size’s neighbours. Usually inside solver noise.') +
      tile('Every size ties', fmtPct(100 * sum.allTie, 0), 'of flops',
        'Flops where every candidate size is within the solves’ combined exploitability of the best: the solves cannot separate the sizes.') +
      `</div>`;

    const fixedTable = `<div class="rep-section"><h3>ALWAYS ONE SIZE <span class="rep-section-note">EV lost against the best size on each flop, % pot (weighted by flop frequency).</span></h3>` +
      `<table class="bs-table"><thead><tr><th>Size</th><th data-tip="Share of flops where this is the best grid size.">Best on</th>` +
      `<th data-tip="Share of flops where this size is inside the tie band: statistically as good as the best.">Tied best on</th>` +
      sortHead('lost', 'EV lost', 'Mean EV lost against each flop’s best evaluated size (grid and refined). Sorts the flops.') +
      `<th data-tip="Mean EV lost against each flop's best grid size only.">vs best grid</th><th></th></tr></thead><tbody>` +
      sum.fixed.map((f, i) => {
        const isFixed = near(f.size, S.fixed);
        return `<tr class="bs-fixed${isFixed ? ' active' : ''}" data-size="${f.size}" style="cursor:default">` +
          `<td><button type="button" class="bs-pick" data-size="${f.size}" aria-pressed="${isFixed}" ` +
          `data-tip="Always use this size in the flop table." style="${PLAIN_BTN}">` +
          `<span class="bs-swatch" style="background:${colors[i]}"></span>${fmtSize(f.size)}</button></td>` +
          `<td>${fmtPct(100 * f.best, 0)}</td><td>${fmtPct(100 * f.tie, 0)}</td>` +
          `<td class="mono">${fmtPct(f.lost)}</td><td class="mono">${fmtPct(f.lostGrid)}</td>` +
          `<td>${variants.has(f.size) ? `<button type="button" class="btn ghost xs" data-variant="${esc(variants.get(f.size))}" data-tip="Open this size as an ordinary report: browse every node across the flops.">OPEN REPORT</button>` : ''}</td></tr>`;
      }).join('') +
      `</tbody></table></div>`;

    // best size mix by texture: stacked shares of the best grid size, each
    // row a pressed filter button
    const legend = `<div class="legend bs-legend">` + grid.map((g, i) =>
      `<span><span class="bs-swatch" style="background:${colors[i]}"></span>${fmtSize(g)}</span>`).join('') + `</div>`;
    const texRows = TEX.map(([k, label]) => {
      const rs = (S.rep.flops || []).filter(r => r.board.length === 6 && texOf(r.board)[k]);
      if (!rs.length) return '';
      let w = 0;
      const share = grid.map(() => 0);
      for (const r of rs) {
        const gi = grid.findIndex(g => near(g, r.verdict.best_grid));
        const wt = r.weight || 1;
        w += wt;
        if (gi >= 0) share[gi] += wt;
      }
      const segs = share.map((s, i) => {
        const f = w > 0 ? s / w : 0;
        if (f <= 0) return '';
        const tip = `${label}: best grid size ${fmtSize(grid[i])} on ${(100 * f).toFixed(0)}% of ${rs.length} flops`;
        return `<span class="bs-seg" style="flex:${f};background:${colors[i]};color:${rampInk(i, grid.length)}" data-tip="${esc(tip)}">${f >= 0.1 ? `${(100 * f).toFixed(0)}%` : ''}</span>`;
      }).join('');
      return `<button type="button" class="bs-texrow${S.tex === k ? ' active' : ''}" data-t="${k}" ` +
        `aria-pressed="${S.tex === k}" style="${PLAIN_BTN};display:grid;width:100%">` +
        `<span class="bs-texname">${label}</span><span class="bs-bar">${segs}</span><span class="dim mono">${rs.length}</span></button>`;
    }).join('');
    const texChart = `<div class="rep-section" role="group" aria-label="Filter flops by texture"><h3>BEST SIZE BY TEXTURE <span class="rep-section-note">Share of flops where each size is the best grid size.</span></h3>${legend}<div class="bs-texchart">${texRows}</div></div>`;

    // per-flop table: every action lives on its column (sort buttons, the
    // board button opens the detail), never on a whole row
    const flopHead = `<div class="rep-section"><h3>FLOPS <span class="rep-section-note">${all.length} shown</span></h3>${curveLegend}`;
    const flopRows = all.map(r => {
      const v = r.verdict;
      const bp = bestPoint(r);
      const fp = r.points.find(q => !q.refined && near(q.size, S.fixed));
      const lost = fp ? v.best_ev_pct - fp.ev_pct : null;
      const sel = S.selected === r.board;
      return `<tr class="bs-flop${sel ? ' active' : ''}" data-board="${esc(r.board)}" style="cursor:default">` +
        `<td class="mono"><button type="button" class="bs-open" data-board="${esc(r.board)}" aria-expanded="${sel}" ` +
        `data-tip="Show this flop's sizes, EVs and engines." style="${PLAIN_BTN}">${fmtBoard(r.board)}</button></td>` +
        `<td><b>${fmtSize(v.best)}</b>${v.edge ? ' <span class="dim" data-tip="Best at the edge of the grid: the true best may lie outside it.">edge</span>' : ''}</td>` +
        `<td>${bandText(v)}</td>` +
        `<td class="mono">${fmtPct(v.best_ev_pct)}</td>` +
        `<td class="mono">${bp?.bet_freq != null ? fmtPct(100 * bp.bet_freq, 0) : '—'}</td>` +
        `<td class="mono">${lost == null ? '—' : fmtPct(lost)}</td>` +
        `<td>${evCurve(r, { colors, grid })}</td></tr>` +
        (sel ? `<tr class="bs-detail"><td colspan="7">${detail(r, grid, colors, variants)}</td></tr>` : '');
    }).join('');
    const flopTable = flopHead +
      `<table class="bs-table bs-flops"><thead><tr>` +
      sortHead('rank', 'Board') +
      sortHead('best', 'Best') +
      sortHead('width', 'Tie band', 'Sizes the solves cannot tell apart from the best.') +
      sortHead('ev', 'EV', `${posName(r.sweep.player)}'s EV at the best size, % of the starting pot.`) +
      `<th data-tip="How often ${esc(posName(r.sweep.player))} bets at the best size.">Bets</th>` +
      sortHead('lost', `Lost by ${fmtSize(S.fixed)}`, `EV lost on this flop by always using ${fmtSize(S.fixed)} (pick the size in ALWAYS ONE SIZE).`) +
      `<th>EV by size</th></tr></thead><tbody>${flopRows || '<tr><td colspan="7" class="dim">No flops match this filter.</td></tr>'}</tbody></table></div>`;

    el.innerHTML = head + filters + tiles + fixedTable + texChart + flopTable;

    el.querySelectorAll('#bs-tex button, .bs-texrow').forEach(b => b.addEventListener('click', () => {
      S.tex = S.tex === b.dataset.t && b.classList.contains('bs-texrow') ? 'all' : b.dataset.t;
      render();
    }));
    el.querySelectorAll('[data-sort]').forEach(b => b.addEventListener('click', () => {
      const key = b.dataset.sort;
      S.sort = { key, dir: S.sort.key === key ? -S.sort.dir : (['rank', 'best'].includes(key) ? -1 : 1) };
      render();
    }));
    el.querySelectorAll('.bs-pick').forEach(b => b.addEventListener('click', () => {
      S.fixed = +b.dataset.size;
      render();
    }));
    el.querySelectorAll('[data-variant]').forEach(b => b.addEventListener('click', () =>
      ctx.openVariant(b.dataset.variant, b.dataset.board || S.selected)));
    el.querySelectorAll('.bs-open').forEach(b => b.addEventListener('click', () => {
      S.selected = S.selected === b.dataset.board ? null : b.dataset.board;
      render();
    }));
    el.querySelectorAll('[data-browse]').forEach(b => b.addEventListener('click', e => {
      e.stopPropagation();
      ctx.openInBrowse(spotWithSize(S.rep, b.dataset.board, +b.dataset.browse), b.dataset.board);
    }));
  }

  /** A sortable column header: the button reverses on a second click. */
  function sortHead(key, label, tip) {
    const active = S.sort.key === key;
    const aria = active ? (S.sort.dir === 1 ? 'descending' : 'ascending') : 'none';
    const arrow = active ? (S.sort.dir === 1 ? ' ↓' : ' ↑') : '';
    return `<th aria-sort="${aria}"${tip ? ` data-tip="${esc(tip)}"` : ''}>` +
      `<button type="button" class="bs-sort" data-sort="${key}" style="${PLAIN_BTN}">${label}` +
      `<span aria-hidden="true">${arrow}</span></button></th>`;
  }

  function tile(label, value, sub, tip) {
    return `<div class="bs-tile" tabindex="0" data-tip="${esc(tip)}"><label>${label}</label><div class="mono bs-big">${value}</div><span class="dim">${sub}</span></div>`;
  }

  function detail(r, grid, colors, variants) {
    const v = r.verdict;
    const pts = r.points.slice().sort((a, b) => a.size - b.size);
    return `<div class="bs-detail-body"><div class="dim">${esc(posName(S.rep.sweep.player))} bets ${fmtSize(v.best)} best; ` +
      `tied: ${v.ties.map(fmtSize).join(', ')}${edgeNote(v, grid)}.</div>` +
      `<table class="bs-table bs-points"><thead><tr><th>Size</th><th>EV % pot</th><th>vs best</th><th>Exploitability</th><th>Bets</th><th>Iterations</th><th>Engine</th><th></th></tr></thead><tbody>` +
      pts.map(p => {
        const gi = grid.findIndex(g => near(g, p.size));
        const tied = v.ties.some(t => near(t, p.size));
        const vname = variants.get(gi >= 0 ? grid[gi] : -1);
        return `<tr class="${near(p.size, v.best) ? 'bs-best' : ''}"><td>${gi >= 0 ? `<span class="bs-swatch" style="background:${colors[gi]}"></span>` : '<span class="bs-swatch bs-refined"></span>'}${fmtSize(p.size)}${p.refined ? ' <span class="dim">refined</span>' : ''}</td>` +
          `<td class="mono">${fmtPct(p.ev_pct, 3)}</td><td class="mono">${near(p.size, v.best) ? 'best' : `−${fmtPct(v.best_ev_pct - p.ev_pct, 3)}${tied ? ' · tie' : ''}`}</td>` +
          `<td class="mono">${fmtPct(p.exploit_pct, 3)}</td><td class="mono">${p.bet_freq != null ? fmtPct(100 * p.bet_freq, 1) : '—'}</td>` +
          `<td class="mono">${p.iterations}</td><td>${esc(p.engine || '')}</td>` +
          `<td><button type="button" class="btn ghost xs" data-browse="${p.size}" data-board="${esc(r.board)}" data-tip="Load this size into SETUP, build and solve, then open it in Browse.">BROWSE</button>` +
          (vname ? ` <button type="button" class="btn ghost xs" data-variant="${esc(vname)}" data-board="${esc(r.board)}">REPORT</button>` : '') +
          `</td></tr>`;
      }).join('') + `</tbody></table></div>`;
  }

  return { render, get name() { return S.rep?.name || null; } };
}

// ------------------------------------------------------ Browse panel ----

/** Switch to REPORTS and open a saved sweep by name. The library is
 *  reports.js's; refresh it first (a sweep started here does not touch the
 *  Reports poll), then click the entry once it renders. */
async function openSavedReport(name, ctx) {
  document.querySelector('.tab[data-tab="reports"]')?.click();
  await ctx?.refreshReports?.();
  const find = () => [...document.querySelectorAll('#rep-library .report-item')].find(b => b.dataset.name === name);
  const hit = find();
  if (hit) return hit.click();
  let tries = 0;
  const timer = setInterval(() => {
    const entry = find();
    if (entry || ++tries > 20) { clearInterval(timer); entry?.click(); }
  }, 100);
}

/** Browse "find best size": at the first bet decision of the root street
 *  (OOP's root, or IP after a check), run a one-board sweep of that bet on
 *  the spot being browsed and show EV by size inline. `ctx`: { toast,
 *  currentSpot, openInBrowse(spot, board), refreshReports }. Returns
 *  { update(view, path) }. */
export function initBrowseBestSize(el, ctx) {
  const S = { key: null, player: null, board: null, running: false, rep: null, poll: null, error: '' };

  function decisionAt(view, path) {
    if (!view || view.node_type !== 'action') return null;
    const kinds = (view.actions || []).map(a => a.kind);
    if (!kinds.includes('check') || !kinds.includes('bet')) return null;
    if (!path.every(s => s.type === 'action')) return null;
    // the root street's first bet: OOP at the root, IP right after a check
    if (path.length === 0 && view.player === 0) return 0;
    if (path.length === 1 && view.player === 1) return 1;
    return null;
  }

  function update(view, path) {
    const player = decisionAt(view, path);
    const board = view ? (view.board || []).join('') : '';
    const key = player == null ? null : `${board}|${player}`;
    if (key !== S.key && !S.running) { S.rep = null; S.error = ''; }
    S.key = key; S.player = player; S.board = board;
    render();
  }

  const reportName = () => `Find best size ${S.board} ${posName(S.player)}`;

  function render() {
    if (S.key == null && !S.running) { el.innerHTML = ''; el.classList.add('hidden'); return; }
    el.classList.remove('hidden');
    const sizes = el.querySelector('#bsb-sizes')?.value || '25 33 50 75 125';
    let body = '';
    if (S.running) body = `<div class="mono dim" id="bsb-status">${esc(S.status || 'starting…')}</div>`;
    else if (S.error) body = `<div class="bs-error">${esc(S.error)}</div>`;
    if (S.rep && !S.running) {
      const row = S.rep.flops[0];
      if (row) {
        const grid = S.rep.grid || S.rep.sweep.sizes;
        const colors = sizeRamp(grid.length);
        const v = row.verdict;
        body += `<div class="bs-browse-result"><div><b>Best ${fmtSize(v.best)}</b> · tie band ${bandText(v)}${edgeNote(v, grid)}</div>` +
          `${evCurve(row, { width: 240, height: 44, colors, grid })}` +
          `<div class="bs-browse-points mono">` + row.points.slice().sort((a, b) => a.size - b.size).map(p =>
            `<span class="${near(p.size, v.best) ? 'bs-best' : ''}">${fmtSize(p.size)} <b>${fmtPct(p.ev_pct)}</b>` +
            `${p.refined ? ' <span class="bs-swatch bs-refined"></span>' : ''}</span>`).join('') +
          `</div><div class="legend bs-legend">` +
          `<span><span class="bs-swatch bs-refined"></span>refinement</span>` +
          `<span><span class="bs-swatch" style="background:var(--panel);border:2px solid var(--accent);box-sizing:border-box"></span>best</span>` +
          `<span class="dim">EV of ${esc(posName(S.rep.sweep.player))} in % pot</span></div>` +
          `<div class="bs-browse-report"><span class="dim">saved</span> ` +
          `<button type="button" class="btn ghost xs" id="bsb-report" data-tip="Open this sweep in REPORTS">${esc(S.rep.name)}</button></div>` +
          `<button type="button" class="btn ghost xs" id="bsb-use">SOLVE WITH ${fmtSize(v.best)}</button></div>`;
      }
    }
    const who = S.player != null ? posName(S.player) : '';
    el.innerHTML = `<div class="bs-browse-head"><b>Find best size</b>` +
      (S.key != null ? ` <span class="dim">${who}'s bet here</span>` : '') +
      ` <button type="button" class="info-dot" aria-label="How the size sweep solves" data-tip="Solves this board once per candidate size of this bet (the rest of the tree keeps the menu of the tree you are browsing), to 0.15% pot, plus up to 3 refinement solves between the best size's neighbours. Sizes whose EV gap is within the solves' combined exploitability count as tied. Runs in the background.">?</button></div>` +
      `<div class="bs-browse-row"><label>sizes % pot <input type="text" id="bsb-sizes" value="${esc(sizes)}"></label>` +
      (S.running ? `<button type="button" class="btn danger xs" id="bsb-stop">STOP</button>`
        : `<button type="button" class="btn xs" id="bsb-run" ${S.key == null ? 'disabled' : ''}>FIND</button>`) + `</div>` + body;
    el.querySelector('#bsb-run')?.addEventListener('click', run);
    el.querySelector('#bsb-stop')?.addEventListener('click', () => api.reportsStop().catch(() => {}));
    el.querySelector('#bsb-report')?.addEventListener('click', () => openSavedReport(S.rep.name, ctx));
    el.querySelector('#bsb-use')?.addEventListener('click', () => {
      const row = S.rep.flops[0];
      ctx.openInBrowse(spotWithSize(S.rep, row.board, row.verdict.best), row.board);
    });
  }

  async function run() {
    const spot = ctx.currentSpot();
    if (!spot) return ctx.toast('build a tree first', true);
    const sizes = (el.querySelector('#bsb-sizes').value.match(/[\d.]+/g) || []).map(Number).filter(x => x > 0);
    if (!sizes.length) return ctx.toast('give at least one size, % pot', true);
    const uniq = [...new Set(sizes.map(s => +s.toFixed(3)))].sort((a, b) => a - b);
    spot.board = S.board;
    const name = reportName();
    try {
      await api.reportsRun({
        name, spot, boards: [S.board],
        sweep: { player: S.player, sizes: uniq, keep_variants: false },
      });
    } catch (e) { S.error = e.message; render(); return; }
    S.running = true; S.rep = null; S.error = ''; S.status = 'starting…';
    render();
    clearInterval(S.poll);
    S.poll = setInterval(async () => {
      let st;
      try { st = await api.reportsStatus(); } catch { return; }
      if (st.running) {
        S.status = `${st.step || 'starting'} · ${(st.seconds / 60).toFixed(1)} min`;
        const s = el.querySelector('#bsb-status');
        if (s) s.textContent = S.status;
        return;
      }
      clearInterval(S.poll); S.poll = null; S.running = false;
      if (st.error) S.error = st.error;
      try {
        const rep = await api.reportsGet(name);
        if (rep.flops?.length) S.rep = rep;
        else if (!S.error) S.error = 'stopped before the sweep finished';
      } catch (e) { S.error = S.error || e.message; }
      render();
    }, 2000);
  }

  return { update };
}
