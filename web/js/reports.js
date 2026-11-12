// FLOP REPORTS — solve the current SETUP spot across a canonical flop
// subset and study aggregate strategy/EV/EQ/EQR by texture, GTO-style.
//
// Reports made since the line summaries shipped carry, per board, a summary
// of EVERY recorded node (flop nodes all, turn nodes all, river nodes to the
// first response; turn/river nodes pooled over the cards dealt). The action
// ribbon walks that tree exactly like Browse's: pick an action, the whole
// report re-aggregates at that node — plus a hand-category breakdown and
// texture/feature charts at every stop. Older reports (two fixed nodes)
// still open in the legacy OOP ROOT / IP VS CHECK view.
//
// Chart = one thin stacked frequency bar per flop (the app's semantic
// action colors, aggressive→passive fixed order), hover tooltips, click or
// ← → to inspect + open in Browse. Table + legend ship alongside (identity
// is never color-alone).

import { api } from './api.js';
import { fmtNum, modelLabel, reportCardFacts, reportTimestamp } from './report_labels.js';
import { MADE_LABELS, MADE_ORDER, DRAW_LABELS, DRAW_ORDER, EQA_LABELS } from './classify.js';
import { RANKS, cardsOf, texOf, TEX } from './textures.js';
import { initBestSizeView } from './best_size.js';

const EQA_ORDER = Object.keys(EQA_LABELS);

// The standard report bet-size menu: aggregated reports are only comparable
// across spots when every report shares one menu. Overrides SETUP's sizes
// when the box is ticked. Sized to keep a 100bb wide-range single-raised
// pot inside a 24 GB GPU (~1.9M nodes): two flop sizes, one turn, one
// river (the all-in threshold turns big river bets into jams), 60% raises.
export const STANDARD_SIZES = {
  oop: [{ bet: '33 75', raise: '60', donk: '' }, { bet: '75', raise: '60', donk: '' }, { bet: '75', raise: '60', donk: '' }],
  ip: [{ bet: '33 75', raise: '60', donk: '' }, { bet: '75', raise: '60', donk: '' }, { bet: '75', raise: '60', donk: '' }],
  max_raises: 3,
};

export function initReports({ els, toast, onError, currentSpot, villains, openInBrowse }) {
  /** A failed request or report action: the app's persistent error surface,
   *  with a retry where one makes sense. Input prompts stay toasts. */
  const fail = (e, retry = null) =>
    onError ? onError(e, retry) : toast(e instanceof Error ? e.message : String(e), true);
  const S = {
    report: null,      // loaded report json
    mode: 'legacy',    // 'lines' when the report carries per-node summaries
    line: '',          // lines mode: current node key ("" = flop root)
    lineData: null,    // lines mode: {history, rows} for S.line
    rows: [],          // lines mode: normalized per-flop rows at S.line
    sort: { key: 'rank', dir: -1 },
    textureSort: { key: 'name', dir: -1 },
    handSort: { key: 'class', dir: -1 },
    tex: 'all',
    node: 'root',      // legacy: 'root' (OOP first decision) | 'vs_check' (IP reply)
    catDim: 'made',    // category panel: made | draw | eqa
    catPlayer: null,   // category panel: 0 | 1 | null (= the actor)
    selected: null,    // board string
    polling: null,
    running: null,     // the live /api/reports/status while a run writes a file
    lineSeq: 0,        // stale-response guard for line fetches
    loadSeq: 0,
    loadingName: null,
    ribbonKey: null,   // last line the ribbon scrolled to
    display: 'chart',
    grouping: 'flops',
    // side-by-side comparison with a second report (lines mode, both):
    // {name, report, cache: Map(line key -> lines payload), key, rows,
    //  matched (B's line found by sizing rather than label), error}
    cmp: null,
    cmpSeq: 0,
    cmpSort: { key: 'adbet', dir: 1 },
  };

  // size-sweep reports open in their own Best size view
  const bestSize = initBestSizeView(document.getElementById('rep-sweep-viewer'), {
    toast,
    openInBrowse: (spot, board) => openInBrowse(spot, board, []),
    openVariant: async (name, board) => {
      await loadReport(name);
      if (board && S.report?.name === name) { S.selected = board; render(); }
    },
  });
  const sweepToggle = document.getElementById('rep-sweep');
  sweepToggle?.addEventListener('change', () =>
    document.getElementById('rep-sweep-opts').classList.toggle('hidden', !sweepToggle.checked));

  // ---------------------------------------------------------- helpers ----

  // escape user-supplied text before interpolating into innerHTML/attributes
  const esc = s => String(s).replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  const activeSort = () => S.display === 'textures' ? S.textureSort : S.display === 'hands' ? S.handSort
    : S.display === 'compare' ? S.cmpSort : S.sort;
  const sortOptions = () => S.display === 'compare'
    ? ['adbet|Largest bet / raise change', 'dbet|Bet / raise change', 'dev0|OOP EV change', 'deqr0|OOP EQR change', 'rank|Board rank']
    : S.display === 'textures'
    ? ['name|Texture', 'count|Flops', 'bet|Bet / raise %', 'ev0|OOP EV', 'ev1|IP EV', 'eq0|OOP equity', 'eqr0|OOP EQR']
    : S.display === 'hands'
      ? ['class|Hand class', 'share|Range share', 'ev|EV', 'eq|Equity']
      : ['rank|Board rank', 'bet|Bet / raise %', 'ev0|OOP EV', 'ev1|IP EV', 'eq0|OOP equity', 'eq1|IP equity', 'eqr0|OOP EQR', 'eqr1|IP EQR'];
  function changeSort(key) {
    const sort = activeSort();
    sort.dir = sort.key === key ? -sort.dir : ['name', 'rank', 'class'].includes(key) ? -1 : 1;
    sort.key = key;
    render();
  }
  function sortHeading(key, label, cls, style = '') {
    const sort = activeSort(), selected = sort.key === key;
    const hint = key === 'bet' ? 'Sort by total bet and raise frequency' : `Sort by ${label}`;
    return `<button type="button" class="rep-column ${cls}${selected ? ' sorted' : ''}" data-sort="${key}" style="${style}" aria-label="${hint}${selected ? (sort.dir === -1 ? ', ascending' : ', descending') : ''}" data-tip="${hint}">${label}<span class="rep-sort-arrow" aria-hidden="true">${selected ? (sort.dir === -1 ? '↑' : '↓') : '↕'}</span></button>`;
  }
  function bindSortHeaders(el) {
    el.querySelectorAll('[data-sort]').forEach(b => b.addEventListener('click', () => changeSort(b.dataset.sort)));
  }

  // action colors: the app's semantic palette (fold blue, check/call green,
  // bets by size in reds, jam purple) — same mapping as every other view
  function actionColor(kind, label, idx, n) {
    if (kind === 'fold') return '#4a78c8';
    if (kind === 'check' || kind === 'call') return '#5ca75f';
    if (/All-in/i.test(label)) return '#7d3ca3';
    const reds = ['#e8484c', '#c73e55', '#a4335f'];
    return reds[Math.min(idx, reds.length - 1)];
  }
  function stratColors(strat) {
    // strat.kinds/labels; index bets by their order among aggressive acts
    let bi = 0;
    return strat.kinds.map((k, i) => {
      const c = actionColor(k, strat.actions[i], bi, strat.kinds.length);
      if (k === 'bet' || k === 'raise') bi++;
      return c;
    });
  }
  // horizontal bars read biggest-action-first (jam / largest raise on the
  // left, fold on the right); the engine lists actions passive-first
  const revIdx = n => Array.from({ length: n }, (_, i) => n - 1 - i);
  const stratOf = row => row.group || S.mode === 'lines'
    ? row.strat
    : (S.node === 'root' ? row.root : row.vs_check) || null;
  // pooling weights: flop iso-weight, times the pair mass at this node in
  // lines mode (a node reached by 2% of pairs must not count like the root)
  const wFreq = row => (row.weight || 1) * (S.mode === 'lines' && row.strat ? row.strat.w : 1);
  const wPlayer = (row, p) => (row.weight || 1) * (S.mode === 'lines' ? (row.players[p].w || 0) : 1);
  const aggrPct = row => {
    const st = stratOf(row);
    if (!st) return 0;
    return st.freqs.reduce((s, f, i) =>
      s + ((st.kinds[i] === 'bet' || st.kinds[i] === 'raise') ? f : 0), 0);
  };
  const metric = (row, key) => {
    const P = row.players;
    switch (key) {
      case 'bet': return aggrPct(row);
      case 'ev0': return P[0].ev; case 'ev1': return P[1].ev;
      case 'eq0': return P[0].eq; case 'eq1': return P[1].eq;
      case 'eqr0': return P[0].eqr; case 'eqr1': return P[1].eqr;
      default: {
        if (row.group) return row.rank;
        const rs = cardsOf(row.board).map(c => RANKS.indexOf(c[0]));
        return rs[0] * 169 + rs[1] * 13 + rs[2];
      }
    }
  };

  function allRows() {
    if (!S.report) return [];
    return S.mode === 'lines' ? S.rows : S.report.flops;
  }
  function visibleRows() {
    const rows = allRows().filter(r => texOf(r.board)[S.tex]);
    const { key, dir } = S.sort;
    return rows.slice().sort((a, b) => dir * (metric(b, key) - metric(a, key)));
  }

  function displayRows(rows) {
    if (S.grouping !== 'high') return rows;
    const groups = Array.from(RANKS, (rank, index) => {
      const members = rows.filter(r => texOf(r.board)._rs[0] === index);
      return members.length ? {
        ...aggregate(members), group: true, rank: index,
        board: `high:${rank}`, label: `${rank}-high`,
      } : null;
    }).filter(Boolean);
    const { key, dir } = S.sort;
    return groups.sort((a, b) => dir * (metric(b, key) - metric(a, key)));
  }

  // weighted aggregate of a row set: strategy freqs + per-player ev/eq/eqr
  function aggregate(rows) {
    const st0 = rows.map(stratOf).find(x => x);
    const na = st0 ? st0.freqs.length : 0;
    const sums = new Array(na).fill(0);
    let fw = 0;
    const P = [{ ev: 0, eq: 0, eqr: 0, w: 0 }, { ev: 0, eq: 0, eqr: 0, w: 0 }];
    for (const r of rows) {
      const st = stratOf(r);
      if (st) {
        const w = wFreq(r);
        fw += w;
        for (let a = 0; a < na; a++) sums[a] += (st.freqs[a] || 0) * w;
      }
      for (let p = 0; p < 2; p++) {
        const w = wPlayer(r, p);
        P[p].w += w;
        P[p].ev += r.players[p].ev * w;
        P[p].eq += r.players[p].eq * w;
        P[p].eqr += r.players[p].eqr * w;
      }
    }
    return {
      strat: st0 ? { ...st0, freqs: sums.map(s => fw > 0 ? s / fw : 0) } : null,
      players: P.map(p => ({ ev: p.w > 0 ? p.ev / p.w : 0, eq: p.w > 0 ? p.eq / p.w : 0, eqr: p.w > 0 ? p.eqr / p.w : 0 })),
      n: rows.length,
    };
  }

  // ---------------------------------------------------------- library ----

  let libraryNames = [];
  let libraryData = [];
  let libraryError = false;
  const deletingReports = new Set();
  document.getElementById('rep-search').addEventListener('input', renderLibrary);

  const metaOf = name => libraryData.find(r => r.name === name) || null;
  /** A report's display title, from the list endpoint's normalized summary. */
  const titleOf = name => metaOf(name)?.summary?.title || String(name ?? '');
  const summaryOf = report => report?.summary || {};
  /** A sweep's size variants share one title; the swept size tells them apart. */
  const cardLabel = report => {
    const summary = summaryOf(report);
    const size = summary.size;
    return `${summary.title || report.name || ''}${size != null ? ` · ${fmtNum(size)}%` : ''}`;
  };
  /** A card label for a run named only in the status payload. */
  const runLabel = name => metaOf(name) ? cardLabel(metaOf(name)) : String(name ?? '');

  /** No library, no selection and a failed refresh are different states; the
   *  error never borrows the empty-state copy. */
  let emptyStateKey = null;
  function paintEmptyState() {
    const el = document.getElementById('rep-empty-state');
    if (!el) return;
    const open = !!(S.report || bestSize.name);
    const key = [open, libraryError, S.loadingName, open ? '' : titleOf(S.loadingName), libraryData.length].join('|');
    if (key === emptyStateKey) return;
    emptyStateKey = key;
    el.classList.toggle('hidden', open);
    if (open) return;
    if (libraryError) {
      el.innerHTML = `<h1>Aggregate reports</h1><p>Couldn't refresh the library — <button type="button" class="btn ghost xs" id="rep-empty-retry">retry</button></p>`;
      el.querySelector('#rep-empty-retry').addEventListener('click', refreshLibrary);
    } else if (S.loadingName) {
      el.innerHTML = `<h1>Aggregate reports</h1><p>Loading ${esc(titleOf(S.loadingName))}…</p>`;
    } else if (!libraryData.length) {
      el.innerHTML = `<h1>Aggregate reports</h1><p>No reports yet. Create one under New report.</p>`;
    } else {
      el.innerHTML = `<h1>Aggregate reports</h1><p>Select a report from the library.</p>`;
    }
  }

  async function refreshLibrary() {
    try {
      const list = await api.reportsList();
      libraryData = list;
      libraryNames = list.map(r => r.name);
      libraryError = false;
    } catch {
      libraryError = true;   // keep the stale list; the retry line names the failure
    }
    renderLibrary();
    paintEmptyState();
  }

  /** A report that is being written is running, never merely partial. */
  function reportState(r) {
    const live = S.running?.name === r.name ? S.running : null;
    const size = summaryOf(r).size;
    const n = r.n_flops ?? 0;
    return [
      live ? `running · ${live.done}/${live.total}` : `${n} flop${n === 1 ? '' : 's'} · ${r.complete ? 'Complete' : 'Partial'}`,
      r.kind === 'sweep' ? 'sweep' : size != null ? `size ${fmtNum(size)}%` : r.lines ? '' : 'legacy',
    ].filter(Boolean).join(' · ');
  }
  /** Re-label cards only: a poll tick must not rebuild the list under the user. */
  function paintRunning() {
    els.library.querySelectorAll('[data-name]').forEach(row => {
      const report = libraryData.find(r => r.name === row.dataset.name);
      const state = row.querySelector('.report-state');
      if (report && state) state.textContent = reportState(report);
    });
  }

  function renderLibrary() {
    const query = document.getElementById('rep-search').value.trim().toLowerCase();
    const list = libraryData.filter(r => {
      const facts = reportCardFacts(summaryOf(r));
      return `${r.name} ${summaryOf(r).title || ''} ${r.villain || ''} ${reportTimestamp(r.created)} ${facts.context}`
        .toLowerCase().includes(query);
    });
    document.getElementById('rep-library-count').textContent = `${list.length}`;
    els.library.innerHTML = '';
    if (libraryError) {
      const warn = document.createElement('div');
      warn.className = 'dim rep-empty';
      warn.innerHTML = `Couldn't refresh the library · <button type="button" class="btn ghost xs">retry</button>`;
      warn.querySelector('button').addEventListener('click', refreshLibrary);
      els.library.append(warn);
    }
    if (!list.length) {
      if (!libraryError) {
        els.library.insertAdjacentHTML('beforeend',
          `<div class="dim rep-empty">${query ? 'No matching reports.' : 'No reports yet. Create one under New report.'}</div>`);
      }
      return;
    }
    // a sweep's per-size reports sit right under their sweep, indented
    const sizeOf = r => summaryOf(r).size ?? 0;
    const parents = new Set(list.filter(r => r.kind === 'sweep').map(r => r.name));
    const ordered = [];
    for (const r of list) {
      if (r.sweep_parent && parents.has(r.sweep_parent)) continue;
      ordered.push(r);
      if (r.kind === 'sweep')
        ordered.push(...list.filter(v => v.sweep_parent === r.name).sort((a, b) => sizeOf(a) - sizeOf(b)));
    }
    for (const r of ordered) {
      const entry = document.createElement('div');
      entry.className = 'report-entry' + (r.sweep_parent && parents.has(r.sweep_parent) ? ' report-variant' : '');
      const row = document.createElement('button');
      row.type = 'button';
      const isOpen = S.report?.name === r.name || bestSize.name === r.name;
      row.className = 'report-item' + (isOpen ? ' active' : '');
      row.setAttribute('aria-pressed', String(isOpen));
      const facts = reportCardFacts(summaryOf(r));
      if (facts.detail) row.dataset.tip = facts.detail;
      const title = summaryOf(r).title || r.name;
      row.dataset.name = r.name;
      row.innerHTML = `<b>${esc(title)}</b>` +
        `<span class="report-context">${esc([facts.context, modelLabel(r.villain)].filter(Boolean).join(' · '))}</span>` +
        `<span class="report-stamp">${esc(reportTimestamp(r.created))}</span>` +
        `<span class="report-state">${esc(reportState(r))}</span>`;
      row.addEventListener('click', () => loadReport(r.name));
      const remove = document.createElement('button');
      remove.type = 'button';
      remove.className = 'report-delete';
      remove.disabled = deletingReports.has(r.name);
      remove.setAttribute('aria-label', `Delete report: ${title} · ${reportTimestamp(r.created)}`);
      remove.dataset.tip = remove.disabled ? 'Deleting report…' : 'Delete report';
      remove.innerHTML = remove.disabled ? '…' : '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 7h16M9 7V4h6v3M6 7l1 14h10l1-14M10 10v8M14 10v8"/></svg>';
      remove.addEventListener('click', () => deleteReport(r));
      entry.append(row, remove);
      els.library.appendChild(entry);
    }
  }

  async function deleteReport(report) {
    const name = report.name;
    if (deletingReports.has(name)) return;
    const title = titleOf(name);
    const facts = reportCardFacts(summaryOf(report));
    const sizes = report.kind === 'sweep'
      ? libraryData.filter(r => r.sweep_parent === name).length : 0;
    const what = report.kind === 'sweep'
      ? `Permanently deletes the sweep${sizes ? ` and its ${sizes} size report${sizes === 1 ? '' : 's'}` : ''}.`
      : 'Permanently deletes the report and its board summaries.';
    if (!confirm(`Delete “${title}”?\n${[facts.context, modelLabel(report.villain), reportTimestamp(report.created)].filter(Boolean).join(' · ')}\n\n${what}`)) return;
    deletingReports.add(name);
    renderLibrary();
    try {
      const status = await api.reportsStatus();
      if (status.running && sanitizeReportName(status.name) === sanitizeReportName(name))
        throw new Error('This report is still running — stop it before deleting.');
      await api.reportsDelete(name);
      if (S.loadingName === name) { ++S.loadSeq; S.loadingName = null; }
      if (S.report?.name === name) {
        ++S.lineSeq;
        S.report = null; S.selected = null; S.rows = []; S.lineData = null;
        render();
      }
      if (S.cmp?.name === name) { ++S.cmpSeq; S.cmp = null; render(); }
      if (bestSize.name === name) {
        bestSize.render(null);
        paintEmptyState();
      }
      if (report.kind === 'sweep' && S.report && libraryData.some(r => r.name === S.report.name && r.sweep_parent === name)) {
        ++S.lineSeq;
        S.report = null; S.selected = null; S.rows = []; S.lineData = null;
        render();
      }
      libraryData = libraryData.filter(r => r.name !== name);
      libraryNames = libraryNames.filter(n => n !== name);
      renderLibrary();
      toast(`Deleted “${title}”${sizes ? ` and ${sizes} size reports` : ''}`);
      await refreshLibrary();
    } catch (e) { fail(e); }
    finally { deletingReports.delete(name); renderLibrary(); }
  }

  async function loadReport(name) {
    const seq = ++S.loadSeq;
    S.loadingName = name;
    paintEmptyState();
    try {
      const rep = await api.reportsGet(name);
      if (seq !== S.loadSeq) return;
      if (rep.kind === 'sweep') {
        ++S.lineSeq;
        if (S.cmp) { ++S.cmpSeq; S.cmp = null; }
        S.report = null; S.selected = null; S.rows = []; S.lineData = null;
        render();
        bestSize.render(rep);
        paintEmptyState();
        renderLibrary();
        return;
      }
      bestSize.render(null);
      S.report = rep;
      renderLibrary();
      S.selected = null;
      S.mode = rep.lines ? 'lines' : 'legacy';
      S.line = '';
      S.lineData = null;
      S.rows = [];
      if (S.cmp && (S.cmp.name === name || S.mode !== 'lines')) { ++S.cmpSeq; S.cmp = null; }
      if (S.mode === 'lines') await loadLine('');
      if (S.cmp) await loadCompareLine();
      if (seq !== S.loadSeq) return;
      render();
    } catch (e) { if (seq === S.loadSeq) fail(e, () => loadReport(name)); }
    finally {
      if (seq === S.loadSeq) { S.loadingName = null; paintEmptyState(); }
    }
  }

  /** Fetch one node of the current report (lines mode) and normalize its
   *  per-flop rows into the shape the strip/table/aggregates render. */
  async function loadLine(key) {
    const seq = ++S.lineSeq;
    const data = await api.reportsLines(S.report.name, key);
    if (seq !== S.lineSeq) return; // superseded by a later click
    S.line = key;
    S.lineData = data;
    S.rows = normalizeRows(data);
    if (S.selected && !S.rows.some(r => r.board === S.selected)) S.selected = null;
  }

  /** Per-flop rows of a lines payload in the shape every view renders. */
  function normalizeRows(data) {
    return data.rows.map(r => {
      const s = r.s;
      const players = [0, 1].map(p => {
        const ps = (s.players || [])[p] || { w: 0, ev: 0 };
        return { ev: ps.ev, eq: ps.eq ?? 0, eqr: ps.eqr ?? 0, w: ps.w, cats: ps.cats || null, hasEq: ps.eq != null };
      });
      const strat = s.kind === 'action' ? {
        actor: s.actor, actions: s.actions, kinds: s.kinds, freqs: s.freqs,
        w: players[s.actor].w,
      } : null;
      return { board: r.board, weight: r.weight, exploit_pct: r.exploit_pct, players, strat, kind: s.kind, pot: s.pot, street: s.street };
    });
  }

  async function setLine(key) {
    try {
      await loadLine(key);
      if (S.cmp) await loadCompareLine();
      render();
    } catch (e) { fail(e, () => setLine(key)); }
  }

  // ------------------------------------------------------- comparison ----

  /** Pick (or clear, name = '') the report compared with the open one. */
  async function setCompare(name) {
    const seq = ++S.cmpSeq;
    if (!name) { S.cmp = null; render(); return; }
    try {
      const report = await api.reportsGet(name);
      if (seq !== S.cmpSeq) return;
      if (!report.lines) throw new Error('That report predates line summaries — re-run it to compare');
      S.cmp = { name, report, cache: new Map(), key: null, rows: [], matched: false, error: null };
      await loadCompareLine();
      if (seq === S.cmpSeq) render();
    } catch (e) {
      if (seq === S.cmpSeq) { S.cmp = null; fail(e, () => setCompare(name)); render(); }
    }
  }

  /** A ⇄ B: read the compared report as A and the open one as B, keeping the
   *  current line when the new A also recorded it. */
  async function swapCompare() {
    const c = S.cmp;
    if (!c || !S.report) return;
    const aName = S.report.name, bName = c.name, line = S.line;
    await loadReport(bName);   // loadReport clears the comparison it replaces
    if (S.report?.name !== bName) return;
    if (line && S.mode === 'lines') {
      try { await loadLine(line); } catch { /* stay at the root when B lacks this line */ }
    }
    await setCompare(aName);
  }

  async function cmpFetch(key) {
    const c = S.cmp;
    if (!c.cache.has(key)) c.cache.set(key, await api.reportsLines(c.name, key));
    return c.cache.get(key);
  }

  // Bet / raise size as a fraction of the pot it goes into, read from the
  // engine's labels ("Bet 3.3 (33%)", "Raise 12", "All-in 40").
  function sizeOf(label, pot) {
    const amount = +(String(label).match(/[\d.]+/) || [NaN])[0];
    return pot > 0 ? amount / pot : NaN;
  }

  /** Index of B's action matching A's action k at the same decision: the
   *  same label, else the same kind at the nearest pot-relative size (within
   *  5% of the pot), all-in to all-in. -1 when B has no counterpart. */
  function matchAction(hA, k, hB) {
    const exact = hB.actions.indexOf(hA.actions[k]);
    if (exact >= 0) return exact;
    const kind = hA.kinds[k];
    const allIn = /^All-in/.test(hA.actions[k]);
    const candidates = hB.actions.map((label, j) => ({ label, j, kind: hB.kinds[j] }))
      .filter(c => c.kind === kind && /^All-in/.test(c.label) === allIn);
    if (kind === 'fold' || kind === 'check' || kind === 'call' || allIn) return candidates.length === 1 ? candidates[0].j : -1;
    const want = sizeOf(hA.actions[k], hA.pot);
    let best = -1, gap = 0.05;
    for (const c of candidates) {
      const d = Math.abs(sizeOf(c.label, hB.pot) - want);
      if (d <= gap) { best = c.j; gap = d; }
    }
    return best;
  }

  /** Follow the open report's line in the compared one, action by action,
   *  and load the compared report's rows there. */
  async function loadCompareLine() {
    const c = S.cmp;
    if (!c || !S.lineData) return;
    const seq = S.cmpSeq;
    const steps = S.line ? S.line.split(',') : [];
    const histA = S.lineData.history;
    const out = [];
    let matched = false, error = null;
    try {
      for (let d = 0; d < steps.length && !error; d++) {
        if (steps[d] === 'c') { out.push('c'); continue; }
        const k = +steps[d].slice(1);
        const hA = histA[d];
        const dataB = await cmpFetch(out.join(','));
        const hB = dataB.history[dataB.history.length - 1];
        if (hB.kind !== 'action' || hB.actor !== hA.actor) {
          error = `the compared report has no ${posName(hA.actor)} decision at this point`;
          break;
        }
        const j = matchAction(hA, k, hB);
        if (j < 0) { error = `the compared report has no “${hA.actions[k]}” here (${hB.actions.join(' / ')})`; break; }
        if (hB.actions[j] !== hA.actions[k]) matched = true;
        out.push(`a${j}`);
      }
      const key = out.join(',');
      const data = error ? null : await cmpFetch(key);
      if (seq !== S.cmpSeq || c !== S.cmp) return;
      Object.assign(c, { key: error ? null : key, matched, error, rows: data ? normalizeRows(data) : [], lineData: data });
    } catch (e) {
      if (seq !== S.cmpSeq || c !== S.cmp) return;
      Object.assign(c, { key: null, matched, error: e.message, rows: [], lineData: null });
    }
  }

  // ------------------------------------------------------------- run ----

  // 'vs modeled villain' only works with a same-session Preflop Lab export
  // (context is lost on reload) — disable the box instead of silently
  // dropping the villain from the run.
  const villainRow = els.vsVillain.closest('label') || els.vsVillain.parentElement;
  const villainTip = villainRow ? villainRow.dataset.tip : '';
  const trustRow = document.getElementById('rep-villain-trust-row');
  const trustInput = document.getElementById('rep-villain-trust');
  const trustTip = trustRow ? trustRow.dataset.tip : '';
  const NO_VILLAIN = 'No modeled villain in this session — build the spot from a PREFLOP LAB export first.';
  function updateVillainGate() {
    const has = !!villains();
    els.vsVillain.disabled = !has;
    if (!has) els.vsVillain.checked = false;
    if (villainRow) {
      villainRow.classList.toggle('dim', !has);
      villainRow.dataset.tip = has ? villainTip : NO_VILLAIN;
    }
    // the trust dial is only a decision while the run uses a villain
    if (trustRow) {
      trustRow.classList.toggle('hidden', !els.vsVillain.checked);
      trustRow.classList.toggle('dim', !has);
      trustRow.dataset.tip = has ? trustTip : NO_VILLAIN;
    }
    if (trustInput) trustInput.disabled = !has;
  }
  els.vsVillain.addEventListener('change', updateVillainGate);

  // STOP used to sit inside the collapsible "New report" panel while the
  // progress line stayed outside it: put the control beside the run it stops.
  {
    const runState = document.createElement('div');
    runState.id = 'rep-run-state';
    runState.style.cssText = 'display:flex;align-items:center;gap:8px;margin-top:6px';
    els.progress.parentNode.insertBefore(runState, els.progress);
    runState.append(els.stop, els.progress);
    els.progress.style.marginTop = '0';
  }

  // A toast that carries its own action; api.js's toast is text-only.
  let actionToastTimer = null;
  function toastAction(msg, label, action) {
    const el = document.getElementById('toast');
    if (!el) return;
    clearTimeout(actionToastTimer);
    const wrap = document.createElement('span');
    wrap.style.cssText = 'display:inline-flex;align-items:center;gap:10px';
    const text = document.createElement('span');
    text.textContent = msg;
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'btn ghost xs';
    button.textContent = label;
    button.addEventListener('click', () => {
      el.className = '';
      el.textContent = '';
      action();
    });
    wrap.append(text, button);
    el.textContent = '';
    el.append(wrap);
    el.className = 'show';
    actionToastTimer = setTimeout(() => {
      if (!wrap.isConnected) return;   // a later toast replaced this one
      el.className = '';
      el.textContent = '';
    }, 8000);
  }

  // The server strips filename-hostile characters before writing (main.rs
  // report_path keeps letters/digits, space, - and _, then trims), so the
  // overwrite check must compare the REAL on-disk name: 'f/o/o' writes
  // foo.json over an existing 'foo'. The stored report JSON keeps whatever
  // name was submitted (older reports may carry raw names), so sanitize BOTH
  // sides of the comparison. Replicated here; the server stays authoritative.
  const sanitizeReportName = s => String(s).replace(/[^\p{L}\p{N} _-]/gu, '').trim();

  els.run.addEventListener('click', async () => {
    const spot = currentSpot();
    if (!spot) return toast('configure a spot in SETUP first (ranges + sizes)', true);
    const name = sanitizeReportName(els.name.value.trim() ||
      `report ${new Date().toISOString().slice(0, 16).replace('T', ' ')}`);
    if (!name) return toast('give the report a name (letters, digits, - _ space)', true);
    if (libraryNames.some(n => sanitizeReportName(n) === name) &&
        !confirm(`"${name}" already exists — overwrite it?`)) return;
    if (els.stdSizes && els.stdSizes.checked) {
      spot.oop = STANDARD_SIZES.oop.map(s => ({ ...s }));
      spot.ip = STANDARD_SIZES.ip.map(s => ({ ...s }));
      spot.max_raises = STANDARD_SIZES.max_raises;
    }
    const body = {
      name, spot,
      flops: +els.flops.value,
      max_iterations: 600,
      target: 0.35,
    };
    if (sweepToggle?.checked) {
      const sizes = [...new Set((document.getElementById('rep-sweep-sizes').value.match(/[\d.]+/g) || [])
        .map(Number).filter(x => x > 0).map(x => +x.toFixed(3)))].sort((a, b) => a - b);
      if (!sizes.length) return toast('best size sweep: give at least one size, % pot', true);
      body.sweep = {
        player: +document.getElementById('rep-sweep-player').value,
        sizes,
        refine: +document.getElementById('rep-sweep-refine').value,
        keep_variants: document.getElementById('rep-sweep-keep').checked,
      };
    }
    if (els.vsVillain.checked) {
      const v = villains();
      if (!v) {
        updateVillainGate();
        return toast('vs modeled villain: no villain context in this session — rebuild the spot from a PREFLOP LAB export or untick the box', true);
      }
      body.villain = v;
      const trust = Number(document.getElementById('rep-villain-trust')?.value ?? 100);
      if (!Number.isFinite(trust) || trust < 0 || trust > 100) {
        return toast('trust the read: give a percent from 0 to 100', true);
      }
      if (trust < 100) {
        // the name labels the report's villain in the library and Compare
        body.villain = { ...v, name: `${v.name} · trust ${trust}%`, trust: trust / 100 };
      }
    }
    try {
      await api.reportsRun(body);
      els.progress.textContent = 'starting…';
      toast(`${body.sweep ? 'best size sweep' : 'report'} "${name}" running — ${body.flops} flops` +
        `${body.sweep ? ` × ${body.sweep.sizes.length + body.sweep.refine} solves` : ''}${body.villain ? ' vs ' + body.villain.name : ''}`);
      pollStatus(true);
    } catch (e) {
      els.progress.textContent = '';
      fail(e, () => els.run.click());
      refreshLibrary();
    }
  });
  els.stop.addEventListener('click', () => api.reportsStop().catch(() => {}));

  // fromRun: the poll follows a RUN click, so a not-running status must be
  // reported even if the run died before the first tick painted progress —
  // only the init-time call (page load, nothing started) stays quiet.
  function pollStatus(fromRun = false) {
    if (S.polling) clearInterval(S.polling);
    let active = fromRun;
    S.polling = setInterval(async () => {
      let st;
      try { st = await api.reportsStatus(); } catch { return; }
      els.stop.classList.toggle('hidden', !st.running);
      els.run.classList.toggle('hidden', st.running);
      if (st.running) {
        const started = S.running?.name !== st.name;
        active = true;
        S.running = st;
        const eta = st.done > 0 ? ` · ~${((st.seconds / st.done) * (st.total - st.done) / 60).toFixed(0)} min left` : '';
        els.progress.textContent =
          `${runLabel(st.name)}: ${st.done}/${st.total} · ${st.board}${st.step ? ` · ${st.step}` : ''} · ${(st.seconds / 60).toFixed(1)} min${eta}`;
        els.progress.title = st.name;
        if (started) refreshLibrary();   // the run's file has to list as running
        else paintRunning();
      } else {
        S.running = null;
        if (active || els.progress.textContent) {
          els.progress.textContent = st.error ? `failed: ${st.error}` : '';
          if (st.error) { fail(st.error); refreshLibrary(); }
          else if (st.name) {
            refreshLibrary();
            const open = S.report?.name || bestSize.name;
            if (open === st.name) loadReport(st.name);      // opened while it was writing
            else if (!open) { toast(`report "${st.name}" done`); loadReport(st.name); }
            else toastAction(`“${runLabel(st.name)}” done`, 'OPEN', () => loadReport(st.name));
          }
        }
        paintRunning();
        clearInterval(S.polling);
        S.polling = null;
      }
    }, 2000);
  }

  // ----------------------------------------------------------- viewer ----

  const posName = p => (p === 0 ? 'OOP' : 'IP');
  const STREET = ['FLOP', 'TURN', 'RIVER'];

  // The canvas caption is a real element: the strip's own fillText is not in
  // the accessibility tree and the table cannot carry it. The live region
  // announces the flop the arrow keys land on.
  const chartCaption = document.createElement('div');
  chartCaption.id = 'rep-chart-caption';
  chartCaption.className = 'dim mono';
  chartCaption.style.cssText = 'font-size:10px;margin:2px 0 4px';
  const chartLive = document.createElement('div');
  chartLive.id = 'rep-chart-live';
  chartLive.setAttribute('role', 'status');
  chartLive.setAttribute('aria-live', 'polite');
  chartLive.style.cssText = 'position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap';
  els.canvas.insertAdjacentElement('beforebegin', chartCaption);
  els.canvas.insertAdjacentElement('afterend', chartLive);
  els.canvas.tabIndex = 0;
  els.canvas.setAttribute('role', 'group');
  els.canvas.setAttribute('aria-label', 'Flop strategy chart');
  els.canvas.setAttribute('aria-describedby', 'rep-chart-caption');

  /** Where the report is being read, in words (strip caption, tooltips). */
  function nodeCaption() {
    if (S.mode !== 'lines') return S.node === 'root' ? 'OOP root strategy' : 'IP vs check';
    const h = S.lineData && S.lineData.history;
    const cur = h && h[h.length - 1];
    if (!cur) return '';
    if (cur.kind === 'action') return `${posName(cur.actor)} to act · ${STREET[cur.street]}` + (S.line ? '' : ' root');
    if (cur.kind === 'chance') return `going to the ${STREET[cur.street]}`;
    return 'hand over';
  }

  function render() {
    const rep = S.report;
    els.viewer.classList.toggle('hidden', !rep);
    paintEmptyState();
    if (!rep) return;
    const summary = summaryOf(metaOf(rep.name));
    const facts = reportCardFacts(summary);
    els.title.textContent = summary.title || rep.name;
    els.title.title = rep.name;
    document.getElementById('rep-context').textContent =
      [facts.context, modelLabel(rep.villain?.name), `${rep.flops.length} flops`, reportTimestamp(rep.created)]
        .filter(Boolean).join(' · ');
    const sz = (rep.spot.oop || []).map((s, i) => `${['F', 'T', 'R'][i]} ${s.bet}${s.raise ? ' / r' + s.raise : ''}`).join(' · ');
    // Recorded engine only: CPU can be selected explicitly or used after CUDA fallback.
    const cpuBoards = rep.flops.filter(f => f.engine === 'cpu').length;
    const engine = rep.flops.some(f => f.engine)
      ? (cpuBoards ? ` · ⚠ ${cpuBoards} of ${rep.flops.length} boards solved on CPU` : ' · ⚡ GPU')
      : '';
    els.subtitle.textContent =
      `pot ${rep.spot.starting_pot} · stack ${rep.spot.effective_stack} · rake ${rep.spot.rake_pct}%` +
      ` · sizes ${sz} · target ${rep.target_pct}% pot${rep.complete ? '' : ' · PARTIAL RUN'}${engine}`;

    renderRibbon();

    // controls (idempotent rebuild)
    const nodeSeg = S.mode === 'lines' ? '' :
      `<div class="seg" id="rep-node">` +
      `<button data-n="root" class="${S.node === 'root' ? 'active' : ''}">OOP ROOT</button>` +
      `<button data-n="vs_check" class="${S.node === 'vs_check' ? 'active' : ''}" data-tip="The c-bet view.">IP VS CHECK</button></div>`;
    document.getElementById('rep-display').innerHTML = ['chart|Chart', 'table|Table', 'hands|Hand classes', 'textures|Textures', 'compare|Compare']
      .map(item => { const [key, title] = item.split('|'); return `<button type="button" data-display="${key}" aria-pressed="${S.display === key}" class="${S.display === key ? 'active' : ''}">${title}</button>`; }).join('');
    document.querySelectorAll('#rep-display button').forEach(b => b.addEventListener('click', () => { S.display = b.dataset.display; render(); }));
    const groupedView = ['chart', 'table'].includes(S.display);
    const sort = activeSort();
    els.controls.innerHTML = nodeSeg + `<div class="rep-order-controls">` + (groupedView ?
      `<label class="rep-sort-label">Group by <select id="rep-group">` +
      `<option value="flops" ${S.grouping === 'flops' ? 'selected' : ''}>Individual flops</option>` +
      `<option value="high" ${S.grouping === 'high' ? 'selected' : ''}>High card</option></select></label>` : '') +
      `<label class="rep-sort-label">Sort <select id="rep-sort">` +
      sortOptions().map(o => { const [k, l] = o.split('|'); return `<option value="${k}" ${sort.key === k ? 'selected' : ''}>${l}</option>`; }).join('') +
      `</select></label><button type="button" class="btn ghost xs" id="rep-sort-direction" aria-label="${sort.dir === -1 ? 'Ascending' : 'Descending'} sort; reverse order" data-tip="Reverse sort order">${sort.dir === -1 ? '↑' : '↓'}</button></div>` +
      `<div class="rep-filter-controls"><span class="dim">Filter flops</span><div class="seg" id="rep-tex" aria-label="Filter flops">` +
      TEX.map(([k, l]) => `<button type="button" data-t="${k}" aria-pressed="${S.tex === k}" class="${S.tex === k ? 'active' : ''}">${l}</button>`).join('') +
      `</div></div>`;
    els.controls.querySelectorAll('#rep-node button').forEach(b =>
      b.addEventListener('click', () => { S.node = b.dataset.n; render(); }));
    els.controls.querySelector('#rep-group')?.addEventListener('change', e => {
      S.grouping = e.target.value;
      S.selected = null;
      S.sort = { key: 'rank', dir: S.grouping === 'high' ? 1 : -1 };
      render();
    });
    els.controls.querySelector('#rep-sort').addEventListener('change', e => {
      changeSort(e.target.value);
    });
    els.controls.querySelector('#rep-sort-direction').addEventListener('click', () => changeSort(activeSort().key));
    els.controls.querySelectorAll('#rep-tex button').forEach(b =>
      b.addEventListener('click', () => { S.tex = b.dataset.t; render(); }));

    const rows = visibleRows();
    renderAggregate(rows);
    if (S.display === 'table') renderTable(displayRows(rows));
    if (groupedView) renderDetail();
    else els.detail.classList.add('hidden');
    renderLegend(rows);
    if (S.display === 'hands') renderCategories(rows);
    if (S.display === 'textures') { renderTextures(rows); renderFeatures(rows); }
    if (S.display === 'compare') renderCompare(rows);
    els.compare.classList.toggle('hidden', S.display !== 'compare');
    els.aggregate.classList.toggle('hidden', S.display === 'compare');
    els.legend.classList.toggle('hidden', S.display === 'compare');
    els.canvas.classList.toggle('hidden', S.display !== 'chart');
    chartCaption.classList.toggle('hidden', S.display !== 'chart');
    els.table.classList.toggle('hidden', S.display !== 'table');
    els.cats.classList.toggle('hidden', S.display !== 'hands');
    els.textures.classList.toggle('hidden', S.display !== 'textures');
    els.features.classList.toggle('hidden', S.display !== 'textures');
    if (S.display === 'hands' && !els.cats.innerHTML) els.cats.innerHTML = '<p class="rep-empty dim">No hand-class data at this node.</p>';
    if (S.display === 'chart') {
      const shown = displayRows(rows);
      chartCaption.textContent = shown.length
        ? `${shown.length} ${S.grouping === 'high' ? 'high-card groups' : 'flops'} · ${nodeCaption()} · hover or ← → to inspect`
        : 'No flops match this filter.';
      drawStrip(shown);
    }
  }

  // ----- action ribbon (lines mode) -----

  function renderRibbon() {
    const el = els.ribbon;
    if (!el) return;
    el.innerHTML = '';
    if (S.mode !== 'lines' || !S.lineData) { el.classList.add('hidden'); return; }
    el.classList.remove('hidden');
    const hist = S.lineData.history;
    const steps = S.line ? S.line.split(',') : [];
    // the head is the step-back control; per-action chips are their own
    // buttons, so the segment itself stays a container (no nested buttons)
    const buttonStyle = 'background:none;border:0;padding:0;text-align:left;cursor:pointer';
    hist.forEach((h, d) => {
      const seg = document.createElement('div');
      seg.className = 'hist-seg' + (d === hist.length - 1 ? ' current' : '');
      const head = document.createElement('button');
      head.type = 'button';
      head.className = 'hist-head';
      head.style.cssText = buttonStyle + ';width:100%';
      if (d === hist.length - 1) head.style.cursor = 'default';
      const carried = Number.isFinite(h.n_flops) ? ` · ${h.n_flops} flops` : '';
      if (h.kind === 'action') {
        head.innerHTML = `<span>${posName(h.actor)} · ${STREET[h.street]}${carried}</span><b>${(+h.pot).toFixed(1)}</b>`;
      } else if (h.kind === 'chance') {
        head.innerHTML = `<span>${STREET[h.street]} CARD${carried}</span><b>${(+h.pot).toFixed(1)}</b>`;
      } else {
        head.innerHTML = `<span>END${carried}</span><b>${(+h.pot).toFixed(1)}</b>`;
      }
      if (d === hist.length - 1) head.setAttribute('aria-current', 'step');
      seg.appendChild(head);
      seg.dataset.tip = d === hist.length - 1
        ? `The point you are reading (${h.n_flops} flops carry it). EV OOP ${(+h.ev[0]).toFixed(2)} · IP ${(+h.ev[1]).toFixed(2)}.`
        : `Click to read the report at this earlier point. EV OOP ${(+h.ev[0]).toFixed(2)} · IP ${(+h.ev[1]).toFixed(2)}.`;
      head.addEventListener('click', () => {
        if (d !== hist.length - 1) setLine(steps.slice(0, d).join(','));
      });
      const next = steps[d]; // the step taken from this point, if any
      if (h.kind === 'action') {
        h.actions.forEach((label, k) => {
          const chip = document.createElement('button');
          chip.type = 'button';
          const taken = next === `a${k}`;
          chip.className = 'hist-chip' + (taken ? ' taken' : '') + ' has-frequency';
          const actionLabel = document.createElement('span');
          actionLabel.textContent = label;
          const frequency = document.createElement('span');
          frequency.className = 'hist-frequency';
          frequency.textContent = `${(h.freqs[k] * 100).toFixed(0)}%`;
          chip.append(actionLabel, frequency);
          chip.dataset.tip = `${(h.freqs[k] * 100).toFixed(1)}% of the time (all flops, pooled). Click to read the report after this action.`;
          chip.addEventListener('click', () => {
            setLine([...steps.slice(0, d), `a${k}`].join(','));
          });
          seg.appendChild(chip);
        });
      } else if (h.kind === 'chance') {
        const chip = document.createElement('button');
        chip.type = 'button';
        chip.className = 'hist-chip' + (next === 'c' ? ' taken' : '');
        chip.textContent = `any ${STREET[h.street].toLowerCase()} ▸`;
        chip.dataset.tip = `Continue onto the ${STREET[h.street].toLowerCase()}: pooled over every card, on every flop. For one runout, open the flop in Browse and use its RUNOUTS REPORT.`;
        chip.addEventListener('click', () => {
          setLine([...steps.slice(0, d), 'c'].join(','));
        });
        seg.appendChild(chip);
      } else {
        const chip = document.createElement('span');
        chip.className = 'hist-chip taken';
        chip.style.cursor = 'default';
        chip.textContent = h.kind === 'terminal_fold' ? 'fold — hand over' : 'showdown';
        seg.appendChild(chip);
      }
      el.appendChild(seg);
    });
    // navigating the ribbon can put the current point outside the strip
    const current = el.querySelector('.hist-seg.current');
    if (current && S.ribbonKey !== S.line) {
      S.ribbonKey = S.line;
      current.scrollIntoView?.({ block: 'nearest', inline: 'nearest' });
    }
  }

  function renderLegend(rows) {
    els.legend.innerHTML = '';
    const st = rows.map(stratOf).find(x => x);
    if (!st) {
      if (S.mode === 'lines' && S.lineData) {
        els.legend.innerHTML = `<span class="key dim">${esc(nodeCaption())} — no strategy at this point; the table shows each player's EV going forward.</span>`;
      }
      return;
    }
    const colors = stratColors(st);
    revIdx(st.actions.length).forEach(i => {
      els.legend.innerHTML += `<span class="key"><i style="background:${colors[i]}"></i>${esc(st.actions[i])}</span>`;
    });
    if (S.mode === 'lines') {
      els.legend.innerHTML += `<span class="key dim">· ${esc(posName(st.actor))} acting · frequencies pooled by pair mass · EV in pot-share chips (OOP + IP = pot)</span>`;
    }
  }

  function renderAggregate(rows) {
    if (!rows.length) { els.aggregate.innerHTML = ''; return; }
    const agg = aggregate(rows);
    const st0 = agg.strat;
    let bar = '';
    if (st0) {
      const colors = stratColors(st0);
      bar = revIdx(st0.freqs.length).map(a =>
        `<div style="width:${(100 * st0.freqs[a]).toFixed(1)}%;background:${colors[a]}" data-tip="${esc(st0.actions[a])}: ${(100 * st0.freqs[a]).toFixed(1)}% pooled over ${rows.length} flops"></div>`).join('');
    }
    const freq = st0 ? revIdx(st0.freqs.length).map(a =>
      `<span><i style="background:${stratColors(st0)[a]}"></i>${esc(st0.actions[a])} <b>${(100 * st0.freqs[a]).toFixed(1)}%</b></span>`).join('') : '';
    els.aggregate.innerHTML = `<div class="rep-overall"><label>${S.tex === 'all' ? 'Overall' : 'Filtered'} strategy · ${rows.length} / ${allRows().length} flops</label>` +
      `<div class="cbar">${bar}</div><div class="rep-frequencies">${freq || esc(nodeCaption())}</div></div>` +
      [['OOP EV', agg.players[0].ev.toFixed(2)], ['IP EV', agg.players[1].ev.toFixed(2)],
       ['OOP equity', (100 * agg.players[0].eq).toFixed(1) + '%'], ['OOP EQR', (100 * agg.players[0].eqr).toFixed(0) + '%']]
      .map(([label, value]) => `<div class="rep-stat"><label>${label}</label><b>${rows.length ? value : '—'}</b></div>`).join('');
  }

  function drawStrip(rows) {
    const cv = els.canvas;
    const W = cv.clientWidth || 1100;
    const H = 300;
    const grouped = S.grouping === 'high';
    const left = 38, top = 16, bottom = grouped ? 54 : 32;
    const plotW = W - left - 12, plotH = H - top - bottom;
    const dpr = window.devicePixelRatio || 1;
    cv.width = W * dpr; cv.height = H * dpr;
    const ctx = cv.getContext('2d');
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, W, H);
    S.stripW = W;      // hitmap coordinate space — rowAt() rescales from CSS px
    S.hitmap = [];
    ctx.font = '10px IBM Plex Mono, monospace';
    for (const pct of [0, 25, 50, 75, 100]) {
      const y = top + plotH * (1 - pct / 100);
      ctx.fillStyle = '#93999e'; ctx.fillText(`${pct}%`, 4, y + 3);
      ctx.strokeStyle = '#303333'; ctx.beginPath(); ctx.moveTo(left, y); ctx.lineTo(W - 12, y); ctx.stroke();
    }
    if (!rows.length) { ctx.fillStyle = '#a0a5aa'; ctx.fillText('No flops match this filter.', left + 20, H / 2); return; }
    const step = plotW / rows.length;
    const bw = grouped ? Math.max(2, step - 12) : Math.max(.5, step - (step >= 4 ? 1 : 0));
    rows.forEach((r, i) => {
      const st = stratOf(r);
      const slot = left + i * step;
      const x = slot + (grouped ? 6 : 0);
      S.hitmap.push({ x0: slot, x1: slot + step, row: r });
      if (grouped) {
        ctx.fillStyle = '#c5c9cd'; ctx.textAlign = 'center';
        ctx.fillText(r.label, slot + step / 2, top + plotH + 17);
        ctx.textAlign = 'left';
      }
      if (!st) return;
      const colors = stratColors(st);
      // draw passive at the bottom, aggressive stacked on top (fixed order)
      let y = top + plotH;
      for (let a = st.freqs.length - 1; a >= 0; a--) {
        const hgt = st.freqs[a] * plotH;
        ctx.fillStyle = colors[a];
        ctx.fillRect(x, y - hgt, bw, hgt);
        y -= hgt;
      }
      if (r.board === S.selected) {
        ctx.strokeStyle = '#e6e6e6';
        ctx.strokeRect(x - 0.5, top, bw + 1, plotH);
      }
    });
    // the caption line lives in #rep-chart-caption (render()), not fillText
  }

  function rowAt(ev) {
    // hitmap x-ranges live in draw-time pixels (S.stripW); the canvas is
    // CSS-stretched to width:100%, so rescale the cursor into that space —
    // stays correct after a resize or a hidden (clientWidth 0) render.
    const rect = els.canvas.getBoundingClientRect();
    if (!rect.width || !S.stripW) return null;
    const x = (ev.clientX - rect.left) * (S.stripW / rect.width);
    return (S.hitmap || []).find(h => x >= h.x0 && x < h.x1)?.row || null;
  }
  // redraw at the real width when the reports view becomes visible or the
  // window is resized (a report can finish + render while the tab is hidden)
  const view = els.canvas.closest('.view');
  if (view && typeof ResizeObserver !== 'undefined') {
    new ResizeObserver(() => {
      if (!view.clientWidth) return;   // still hidden
      updateVillainGate();
      if (S.report && els.canvas.clientWidth && els.canvas.clientWidth !== S.stripW)
        drawStrip(displayRows(visibleRows()));
    }).observe(view);
  }
  els.canvas.dataset.tipFollowPointer = '';
  els.canvas.addEventListener('mousemove', ev => {
    const r = rowAt(ev);
    // keep data-tip current per position; tooltip.js re-reads it while the
    // pointer moves. Set '' (not removeAttribute) so the canvas stays a
    // [data-tip] target between bars.
    if (!r) { els.canvas.dataset.tip = ''; els.canvas.dataset.tipHtml = ''; return; }
    const tip = flopTooltip(r);
    if (els.canvas.dataset.tip !== tip.text) {
      els.canvas.dataset.tip = tip.text;
      els.canvas.dataset.tipHtml = tip.html;
    }
  });
  els.canvas.addEventListener('click', ev => {
    const r = rowAt(ev);
    if (r) { S.selected = r.board; render(); announceRow(r); }
  });
  // The canvas is the default view, so it must be readable by keyboard too:
  // ← → walk the same hitmap the pointer uses and the live region announces
  // the selected flop.
  els.canvas.addEventListener('keydown', ev => {
    const step = ev.key === 'ArrowLeft' ? -1 : ev.key === 'ArrowRight' ? 1 : 0;
    if (!step && ev.key !== 'Home' && ev.key !== 'End') return;
    const rows = displayRows(visibleRows());
    if (!rows.length) return;
    ev.preventDefault();
    let i = rows.findIndex(r => r.board === S.selected);
    if (i < 0) i = step > 0 ? -1 : rows.length;
    const next = ev.key === 'Home' ? 0 : ev.key === 'End' ? rows.length - 1
      : Math.max(0, Math.min(rows.length - 1, i + step));
    const row = rows[next];
    S.selected = row.board;
    render();
    announceRow(row);
  });
  els.canvas.addEventListener('focus', () => {
    if (!S.selected) chartLive.textContent = 'Use the left and right arrow keys to inspect flops.';
  });

  const SUIT_GLYPH = { c: '♣', d: '♦', h: '♥', s: '♠' };
  const fmtBoard = b => cardsOf(b).map(c => c[0] + SUIT_GLYPH[c[1]]).join('');
  const boardTiles = b => cardsOf(b).map(c =>
    `<span class="rep-card suit-${esc(c[1])}">${esc(c[0])}${SUIT_GLYPH[c[1]] || ''}</span>`).join('');

  /** One short line for screen readers when the chart selection moves. */
  function announceRow(row) {
    if (!row) return;
    const st = stratOf(row);
    const top = st ? st.actions.map((a, i) => ({ a, f: st.freqs[i] })).sort((x, y) => y.f - x.f)[0] : null;
    chartLive.textContent = `${row.group ? `${row.label} · ${row.n} flops` : fmtBoard(row.board)} · ${nodeCaption()}` +
      (top ? ` · ${top.a} ${(100 * top.f).toFixed(0)}%` : '') +
      ` · EV OOP ${row.players[0].ev.toFixed(2)} · IP ${row.players[1].ev.toFixed(2)}`;
  }

  function strategyTooltipRows(st) {
    const colors = st ? stratColors(st) : [];
    return st ? st.actions.map((a, i) =>
      `<span><i class="rep-tip-swatch" style="background:${colors[i]}"></i>${esc(a)}</span><span>${(100 * st.freqs[i]).toFixed(1)}%</span>`).join('') : '';
  }

  function tooltipAttributes(tip) {
    return `data-tip="${esc(tip.text)}" data-tip-html="${esc(tip.html)}" data-tip-follow-pointer`;
  }

  function flopTooltip(row) {
    const st = stratOf(row);
    const actions = strategyTooltipRows(st);
    const metrics = [
      ['EV', p => p.ev.toFixed(2)],
      ['Equity', p => `${(100 * p.eq).toFixed(1)}%`],
      ['EQR', p => `${(100 * p.eqr).toFixed(0)}%`],
    ];
    return {
      text: `${row.group ? `${row.label} · ${row.n} flops` : fmtBoard(row.board)} · ${nodeCaption()}\n` +
        (st ? st.actions.map((a, i) => `${a} ${(100 * st.freqs[i]).toFixed(1)}%`).join('\n') + '\n' : '') +
        metrics.map(([label, fmt]) => `${label}: OOP ${fmt(row.players[0])} · IP ${fmt(row.players[1])}`).join('\n'),
      html: `<div class="rep-tip-heading"><b class="rep-board">${row.group ? `${esc(row.label)} · ${row.n} flops` : boardTiles(row.board)}</b><span class="dim">${esc(nodeCaption())}</span></div>` +
        (actions ? `<div class="tip-rows">${actions}</div>` : '') +
        `<div class="rep-tip-metrics"><span></span><b>OOP</b><b>IP</b>` +
        metrics.map(([label, fmt]) => `<span class="dim">${label}</span><span>${fmt(row.players[0])}</span><span>${fmt(row.players[1])}</span>`).join('') + `</div>`,
    };
  }

  /** Action indices of the current line up to the first card step: the part
   *  of it Browse can open on a specific flop. */
  function browseSteps() {
    if (S.mode !== 'lines' || !S.line) return [];
    const out = [];
    for (const s of S.line.split(',')) {
      if (s[0] !== 'a') break;
      out.push(+s.slice(1));
    }
    return out;
  }

  function renderDetail() {
    if (S.selected?.startsWith('high:')) {
      const group = displayRows(visibleRows()).find(r => r.board === S.selected);
      els.detail.classList.toggle('hidden', !group);
      if (group) {
        const st = group.strat;
        els.detail.innerHTML = `<b>${esc(group.label)} · ${group.n} flops</b><div class="rep-frequencies">` +
          (st ? st.actions.map((a, i) => `<span>${esc(a)} <b>${(100 * st.freqs[i]).toFixed(1)}%</b></span>`).join('') : esc(nodeCaption())) + '</div>';
      }
      return;
    }
    const r = S.report && S.selected
      ? allRows().find(x => x.board === S.selected) : null;
    els.detail.classList.toggle('hidden', !r);
    if (!r) return;
    const st = stratOf(r);
    els.detail.innerHTML =
      `<b class="mono">${fmtBoard(r.board)}</b> ` +
      `<span class="dim mono" style="font-size:11px">exploit ${(+r.exploit_pct).toFixed(2)}% · ` +
      (st ? st.actions.map((a, i) => `${esc(a)} ${(100 * st.freqs[i]).toFixed(1)}%`).join(' · ') : '') +
      ` · OOP ev ${r.players[0].ev.toFixed(2)} eq ${(100 * r.players[0].eq).toFixed(1)} eqr ${(100 * r.players[0].eqr).toFixed(0)}%` +
      ` · IP ev ${r.players[1].ev.toFixed(2)} eq ${(100 * r.players[1].eq).toFixed(1)} eqr ${(100 * r.players[1].eqr).toFixed(0)}%</span> ` +
      `<button class="btn ghost xs" id="rep-open" data-tip="Load this spot + board into SETUP, solve it, then open Browse${browseSteps().length ? ' at this line' : ''}.">OPEN IN BROWSE</button>`;
    els.detail.querySelector('#rep-open').addEventListener('click', () =>
      openInBrowse(S.report.spot, r.board, browseSteps()));
  }

  function renderTable(rows) {
    const el = els.table;
    el.innerHTML = '';
    // headers drive the same sort state as the #rep-sort dropdown (render()
    // rebuilds the dropdown with the current key selected, so they stay in
    // sync); clicking the active column flips direction
    const head = document.createElement('div');
    head.className = 'combo-row head';
    head.innerHTML =
      sortHeading('rank', S.grouping === 'high' ? 'High card' : 'Flop', 'cname') +
      sortHeading('bet', 'Strategy', 'cbar') +
      sortHeading('ev0', 'OOP EV', 'cnum') + sortHeading('ev1', 'IP EV', 'cnum') +
      sortHeading('eq0', 'OOP EQ', 'cnum') + sortHeading('eqr0', 'OOP EQR', 'cnum');
    bindSortHeaders(head);
    el.appendChild(head);
    if (!rows.length) el.insertAdjacentHTML('beforeend', '<p class="rep-empty dim">No flops match this filter. Select ALL to reset.</p>');
    const CAP = 200;
    for (const r of rows.slice(0, CAP)) {
      const st = stratOf(r);
      const colors = st ? stratColors(st) : [];
      const bar = st ? revIdx(st.freqs.length).map(a =>
        `<div style="width:${(st.freqs[a] * 100).toFixed(1)}%;background:${colors[a]}"></div>`).join('') : '';
      const row = document.createElement('div');
      row.className = 'combo-row' + (r.board === S.selected ? ' sel' : '');
      row.innerHTML = `<span class="cname mono rep-board${r.group ? ' rep-group-label' : ''}">${r.group ? `<b>${esc(r.label)}</b><small>${r.n} flops</small>` : boardTiles(r.board)}</span><span class="cbar">${bar}</span>` +
        `<span class="cnum">${r.players[0].ev.toFixed(2)}</span><span class="cnum">${r.players[1].ev.toFixed(2)}</span>` +
        `<span class="cnum">${(100 * r.players[0].eq).toFixed(1)}</span><span class="cnum">${(100 * r.players[0].eqr).toFixed(0)}%</span>`;
      const board = row.querySelector('.rep-board');
      const tip = flopTooltip(r);
      board.dataset.tip = tip.text;
      board.dataset.tipHtml = tip.html;
      const strategyBar = row.querySelector('.cbar');
      strategyBar.dataset.tip = tip.text;
      strategyBar.dataset.tipHtml = tip.html;
      strategyBar.dataset.tipFollowPointer = '';
      row.addEventListener('click', () => { S.selected = r.board; render(); });
      el.appendChild(row);
    }
    if (rows.length > CAP) {
      const more = document.createElement('div');
      more.className = 'dim mono';
      more.style.cssText = 'font-size:11px;padding:6px 2px;text-align:center';
      more.textContent = `showing ${CAP} of ${rows.length} flops — filter or sort to bring others up (strip + averages cover all ${rows.length})`;
      el.appendChild(more);
    }
  }

  // ----- comparison with a second report -----

  const SPOT_FIELDS = [
    ['starting_pot', 'pot', ''], ['effective_stack', 'stack', ''], ['rake_pct', 'rake', '%'],
    ['rake_cap', 'rake cap', ''], ['max_raises', 'raise cap', ''],
  ];
  const STREETS = ['F', 'T', 'R'];
  const stepText = x => x ? `${x.bet || ''}${x.raise ? '/r' + x.raise : ''}${x.donk ? '/d' + x.donk : ''}` : '';
  const valueText = (x, unit) => x == null ? '—' : `${fmtNum(x)}${unit}`;
  /** The stored villain name doubles as the trust label; split it so the
   *  trust percentage can be compared on its own. */
  const villainName = v => String(v?.name ?? 'none').replace(/\s*·\s*trust\s*\d+%\s*$/i, '');

  /** Settings that differ between the two reports, with both values. */
  function spotDifferences(a, b) {
    const sa = a.spot || {}, sb = b.spot || {};
    const out = [];
    for (const [key, label, unit] of SPOT_FIELDS) {
      if ((sa[key] ?? null) !== (sb[key] ?? null))
        out.push(`${label} ${valueText(sa[key], unit)} vs ${valueText(sb[key], unit)}`);
    }
    for (const side of ['oop', 'ip']) {
      const rowsA = sa[side] || [], rowsB = sb[side] || [];
      const streets = [];
      for (let i = 0; i < Math.max(rowsA.length, rowsB.length); i++) {
        const x = stepText(rowsA[i]), y = stepText(rowsB[i]);
        if (x !== y) streets.push(`${STREETS[i] || i + 1} ${x || '—'} vs ${y || '—'}`);
      }
      if (streets.length) out.push(`${side === 'ip' ? 'IP ' : ''}sizes ${streets.join(', ')}`);
    }
    if ((sa.range_oop ?? '') !== (sb.range_oop ?? '')) out.push('OOP range');
    if ((sa.range_ip ?? '') !== (sb.range_ip ?? '')) out.push('IP range');
    if ((a.target_pct ?? null) !== (b.target_pct ?? null))
      out.push(`target ${valueText(a.target_pct, '%')} vs ${valueText(b.target_pct, '%')}`);
    if (villainName(a.villain) !== villainName(b.villain))
      out.push(`villain ${villainName(a.villain)} vs ${villainName(b.villain)}`);
    const trustA = a.villain?.trust ?? 1, trustB = b.villain?.trust ?? 1;
    if (trustA !== trustB)
      out.push(`villain trust ${Math.round(100 * trustA)}% vs ${Math.round(100 * trustB)}%`);
    return out;
  }

  /** Reports without line summaries cannot be read at a shared node. */
  const compareBlocker = r => r.kind === 'sweep' ? 'best size sweep — pick a size report'
    : !r.lines ? 'no line summaries' : '';

  function renderCompare(rowsA) {
    const el = els.compare;
    const c = S.cmp;
    const others = libraryData.filter(r => r.name !== S.report.name);
    const usable = others.filter(r => !compareBlocker(r));
    const blocked = others.filter(compareBlocker);
    const option = r => `<option value="${esc(r.name)}" ${c?.name === r.name ? 'selected' : ''}>` +
      `${esc(cardLabel(r))} · ${esc(reportTimestamp(r.created))}</option>`;
    const picker = `<label class="rep-sort-label">Compare with <select id="rep-compare-select">` +
      `<option value="">Choose a report…</option>` +
      usable.map(option).join('') +
      (blocked.length ? `<optgroup label="Can't compare">` + blocked.map(r =>
        `<option disabled>${esc(cardLabel(r))} · ${esc(compareBlocker(r))}</option>`).join('') + `</optgroup>` : '') +
      `</select></label>` +
      `<button type="button" class="btn ghost xs" id="rep-cmp-swap" ${c ? '' : 'disabled'} aria-label="A ⇄ B — swap the two reports" data-tip="Read B as A and A as B">A ⇄ B</button>`;
    const note = text => `<p class="rep-empty dim">${text}</p>`;
    let body;
    if (S.mode !== 'lines') body = note('This report predates line summaries — re-run it to compare.');
    else if (!usable.length) body = note(others.length
      ? 'No report with line summaries to compare yet.'
      : 'No second report yet. Run one for another stack, size or villain.');
    else if (!c) body = note('Pick a second report. Both are read at the ribbon point, over shared flops.');
    else if (c.error) body = note(`Can’t compare at this point: ${esc(c.error)}. Step back along the ribbon.`);
    else body = compareBody(rowsA, c);
    el.innerHTML = `<div class="rep-compare-head">${picker}</div>${body}`;
    el.querySelector('#rep-compare-select').addEventListener('change', e => setCompare(e.target.value));
    el.querySelector('#rep-cmp-swap').addEventListener('click', swapCompare);
    bindSortHeaders(el);
    el.querySelectorAll('[data-board]').forEach(r => r.addEventListener('click', () => {
      S.selected = r.dataset.board;
      renderCompare(visibleRows());
    }));
  }

  function compareBody(rowsA, c) {
    const byBoard = new Map(c.rows.map(r => [r.board, r]));
    const specA = S.report.spot, specB = c.report.spot;
    // EV is pot-share chips; across different starting pots read it as % of
    // the pot at this point instead, or every delta is mostly the pot change
    const pctEv = specA.starting_pot !== specB.starting_pot;
    const scale = row => !pctEv ? row : {
      ...row, players: row.players.map(p => ({ ...p, ev: row.pot > 0 ? 100 * p.ev / row.pot : 0 })),
    };
    const pairs = rowsA.filter(r => byBoard.has(r.board)).map(a => ({ a: scale(a), b: scale(byBoard.get(a.board)) }));
    const labelA = titleOf(S.report.name);
    const labelB = titleOf(c.report.name);
    const diffs = spotDifferences(S.report, c.report);
    const evUnit = pctEv ? 'EV % pot' : 'EV';
    const fmtEv = x => pctEv ? `${x.toFixed(1)}%` : x.toFixed(2);
    // sign shown on the rounded value, so a tiny negative never reads "−0.0"
    const signed = (x, digits) => {
      const r = +x.toFixed(digits);
      return `${r > 0 ? '+' : r < 0 ? '−' : '±'}${Math.abs(r).toFixed(digits)}`;
    };

    const head = `<div class="rep-compare-sum">` +
      `<span class="rep-cmp-tag">A</span><b>${esc(labelA)}</b><span class="rep-cmp-vs">vs</span><span class="rep-cmp-tag b">B</span><b>${esc(labelB)}</b>` +
      `<span class="dim">· ${pairs.length} shared flops of ${rowsA.length} shown${c.rows.length !== pairs.length ? ` (B has ${c.rows.length} here)` : ''}` +
      `${c.matched ? ' · B’s line matched by bet size' : ''}</span></div>` +
      `<div class="rep-compare-diff dim">${diffs.length ? `Differs: ${esc(diffs.join(' · '))}` : 'Same spot settings'}` +
      `${pctEv ? ' · EV shown as % of the pot at this point, since the starting pots differ' : ''}</div>`;
    if (!pairs.length) return head + `<p class="rep-empty dim">The two reports share no flops under this filter.</p>`;

    const aggA = aggregate(pairs.map(p => p.a)), aggB = aggregate(pairs.map(p => p.b));
    const bar = agg => agg.strat ? `<div class="cbar">${stackedBar(agg)}</div>` : `<div class="cbar rep-cmp-none dim">${esc(nodeCaption())}</div>`;
    const aggrOf = agg => agg.strat ? agg.strat.freqs.reduce((t, f, i) =>
      t + ((agg.strat.kinds[i] === 'bet' || agg.strat.kinds[i] === 'raise') ? f : 0), 0) : null;
    // per-action change, A's actions matched to B's the same way as the line
    let actionDeltas = '';
    if (aggA.strat && aggB.strat) {
      const potA = S.lineData.history[S.lineData.history.length - 1].pot;
      const potB = c.lineData.history[c.lineData.history.length - 1].pot;
      const hA = { ...aggA.strat, pot: potA }, hB = { ...aggB.strat, pot: potB };
      const colors = stratColors(aggA.strat);
      const colorsB = stratColors(aggB.strat);
      const used = new Set();
      actionDeltas = `<div class="rep-frequencies">` + revIdx(hA.actions.length).map(k => {
        const j = matchAction(hA, k, hB);
        const fa = 100 * hA.freqs[k];
        if (j < 0) return `<span><i style="background:${colors[k]}"></i>${esc(hA.actions[k])} <b>${fa.toFixed(1)}%</b> <span class="dim">(not in B)</span></span>`;
        used.add(j);
        const fb = 100 * hB.freqs[j];
        const same = hB.actions[j] === hA.actions[k] ? '' : ` <span class="dim">(B: ${esc(hB.actions[j])})</span>`;
        return `<span><i style="background:${colors[k]}"></i>${esc(hA.actions[k])} <b>${fa.toFixed(1)}% → ${fb.toFixed(1)}%</b> <span class="rep-delta-text ${fb - fa > 0.05 ? 'up' : fb - fa < -0.05 ? 'down' : ''}">${signed(fb - fa, 1)}</span>${same}</span>`;
      }).join('') + revIdx(hB.actions.length).filter(j => !used.has(j)).map(j =>
        `<span><i style="background:${colorsB[j]}"></i>${esc(hB.actions[j])} <b>${(100 * hB.freqs[j]).toFixed(1)}%</b> <span class="dim">(B only)</span></span>`).join('') + `</div>`;
    }
    const metrics = [
      ['Bet / raise', aggrOf(aggA), aggrOf(aggB), x => `${(100 * x).toFixed(1)}%`, d => signed(100 * d, 1)],
      [`OOP ${evUnit}`, aggA.players[0].ev, aggB.players[0].ev, fmtEv, d => signed(d, pctEv ? 1 : 2)],
      ['OOP equity', aggA.players[0].eq, aggB.players[0].eq, x => `${(100 * x).toFixed(1)}%`, d => signed(100 * d, 1)],
      ['OOP EQR', aggA.players[0].eqr, aggB.players[0].eqr, x => `${(100 * x).toFixed(0)}%`, d => signed(100 * d, 0)],
      ['IP EQR', aggA.players[1].eqr, aggB.players[1].eqr, x => `${(100 * x).toFixed(0)}%`, d => signed(100 * d, 0)],
    ].filter(m => m[1] != null && m[2] != null);
    const overall = `<div class="rep-cmp-overall">` +
      `<div class="rep-cmp-bars"><span class="rep-cmp-tag">A</span>${bar(aggA)}<span class="rep-cmp-tag b">B</span>${bar(aggB)}</div>` +
      actionDeltas +
      `<div class="rep-cmp-stats"><span></span><b>A</b><b>B</b><b>B − A</b>` +
      metrics.map(([label, a, b, fmt, fd]) => `<span class="dim">${label}</span><span>${fmt(a)}</span><span>${fmt(b)}</span><span class="rep-delta-text ${b - a > 1e-9 ? 'up' : b - a < -1e-9 ? 'down' : ''}">${fd(b - a)}</span>`).join('') +
      `</div></div>`;

    // per-flop rows
    const rows = pairs.map(({ a, b }) => {
      const ba = aggrPct(a), bb = aggrPct(b), act = !!(stratOf(a) && stratOf(b));
      return {
        a, b, board: a.board, act,
        dbet: act ? bb - ba : 0, adbet: act ? Math.abs(bb - ba) : 0,
        dev0: b.players[0].ev - a.players[0].ev, deqr0: b.players[0].eqr - a.players[0].eqr,
        rank: metric(a, 'rank'),
      };
    });
    const { key, dir } = S.cmpSort;
    rows.sort((x, y) => dir * (y[key] - x[key]));
    const cellBar = row => {
      const st = stratOf(row);
      if (!st) return '';
      const colors = stratColors(st);
      return revIdx(st.freqs.length).map(i => `<div style="width:${(100 * st.freqs[i]).toFixed(1)}%;background:${colors[i]}"></div>`).join('');
    };
    // diverging bar: right/red = more betting in B, left/green = less; a
    // 50-point change fills the half-track
    const deltaCell = r => !r.act ? `<span class="cnum dim rep-delta">—</span>` :
      `<span class="cnum rep-delta" data-tip="Bet + raise frequency: A ${(100 * aggrPct(r.a)).toFixed(1)}% → B ${(100 * aggrPct(r.b)).toFixed(1)}%">` +
      `<span class="rep-delta-track"><i class="${r.dbet < 0 ? 'down' : 'up'}" style="width:${Math.min(50, 100 * Math.abs(r.dbet)).toFixed(1)}%"></i></span>` +
      `<span>${signed(100 * r.dbet, 1)}</span></span>`;
    const CAP = 200;
    const table = `<div class="rep-cmp-table"><div class="combo-row head">` +
      sortHeading('rank', 'Flop', 'cname') +
      `<span class="cbar rep-cmp-col">A strategy</span><span class="cbar rep-cmp-col">B strategy</span>` +
      sortHeading('dbet', 'Δ bet/raise', 'cnum rep-delta-head') +
      sortHeading('dev0', `Δ OOP ${pctEv ? 'EV%' : 'EV'}`, 'cnum') + sortHeading('deqr0', 'Δ OOP EQR', 'cnum') + `</div>` +
      rows.slice(0, CAP).map(r => {
        const ta = flopTooltip(r.a), tb = flopTooltip(r.b);
        return `<div class="combo-row${r.board === S.selected ? ' sel' : ''}" data-board="${esc(r.board)}">` +
          `<span class="cname mono rep-board">${boardTiles(r.board)}</span>` +
          `<span class="cbar" ${tooltipAttributes(ta)}>${cellBar(r.a)}</span><span class="cbar" ${tooltipAttributes(tb)}>${cellBar(r.b)}</span>` +
          deltaCell(r) +
          `<span class="cnum">${signed(r.dev0, pctEv ? 1 : 2)}</span><span class="cnum">${signed(100 * r.deqr0, 0)}</span></div>`;
      }).join('') +
      (rows.length > CAP ? `<div class="dim mono rep-cmp-more">showing ${CAP} of ${rows.length} flops — sort or filter to bring others up (the summary covers all ${rows.length})</div>` : '') +
      `</div>`;
    return head + overall +
      `<h3>BY FLOP <button type="button" class="info-dot" aria-label="What the deltas mean" data-tip="Δ = B − A. IP’s EV change mirrors OOP’s (the two share the pot), so only OOP’s is shown.">?</button></h3>` + table;
  }

  // ----- hand-category breakdown (lines mode, action nodes) -----

  function renderCategories(rows) {
    const el = els.cats;
    if (!el) return;
    el.innerHTML = '';
    const st0 = rows.map(stratOf).find(x => x);
    const withCats = rows.filter(r => r.players[0].cats || r.players[1].cats);
    if (S.mode !== 'lines' || !withCats.length) { el.classList.add('hidden'); return; }
    el.classList.remove('hidden');
    const actor = st0 ? st0.actor : 0;
    const player = S.catPlayer == null ? actor : S.catPlayer;
    const isActor = st0 && player === actor;
    const dims = [['made', 'MADE HANDS', MADE_ORDER, MADE_LABELS], ['draw', 'DRAWS', DRAW_ORDER, DRAW_LABELS], ['eqa', 'EQUITY', EQA_ORDER, EQA_LABELS]];
    const [, , order, labels] = dims.find(d => d[0] === S.catDim);
    // pooled per category: flop weight × the category's pair mass
    const acc = order.map(() => ({ w: 0, ev: 0, eq: 0, f: st0 ? new Array(st0.freqs.length).fill(0) : [] }));
    for (const r of withCats) {
      const cb = r.players[player].cats;
      if (!cb) continue;
      const list = cb[S.catDim] || [];
      list.forEach((c, k) => {
        if (!acc[k]) return;
        const w = (r.weight || 1) * c.w;
        acc[k].w += w; acc[k].ev += w * c.ev; acc[k].eq += w * c.eq;
        if (isActor && c.freqs) c.freqs.forEach((f, a) => { acc[k].f[a] += w * f; });
      });
    }
    const total = acc.reduce((s, a) => s + a.w, 0) || 1;
    const colors = st0 ? stratColors(st0) : [];
    const head =
      `<div class="rep-cats-head">` +
      `<div class="seg">${dims.map(d => `<button data-d="${d[0]}" class="${S.catDim === d[0] ? 'active' : ''}">${d[1]}</button>`).join('')}</div>` +
      `<div class="seg">${[0, 1].map(p => `<button data-p="${p}" class="${player === p ? 'active' : ''}" data-tip="${p === actor ? 'The acting player — strategy included.' : 'The other player — no decision here, so no strategy.'}">${posName(p)}${p === actor ? ' · ACTING' : ''}</button>`).join('')}</div>` +
      `<span class="dim" style="font-size:10px">${esc(posName(player))}'s range at this point · pooled over ${withCats.length} flops</span>` +
      `</div>`;
    const hrow = `<div class="combo-row head">` + sortHeading('class', 'Class', 'cname', 'min-width:120px') + sortHeading('share', 'Share', 'cnum', 'min-width:52px') +
      `<span class="cbar" style="background:none">${isActor ? 'strategy' : ''}</span>` + sortHeading('ev', 'EV', 'cnum') + sortHeading('eq', 'EQ', 'cnum') + '</div>';
    const { key: sortKey, dir } = S.handSort;
    const handMetric = k => sortKey === 'share' ? acc[k].w : sortKey === 'ev' ? acc[k].ev / (acc[k].w || 1) : sortKey === 'eq' ? acc[k].eq / (acc[k].w || 1) : k;
    const ordered = order.map((key, k) => ({ key, k })).sort((a, b) => dir * (handMetric(b.k) - handMetric(a.k)));
    const body = ordered.map(({key, k}) => {
      const a = acc[k];
      if (a.w <= 0) return '';
      const share = a.w / total;
      if (share < 0.002) return '';
      const st = isActor ? { ...st0, freqs: a.f.map(f => f / a.w) } : null;
      const caption = `${posName(player)} · pooled over ${withCats.length} flops`;
      const metrics = [['Range share', `${(100 * share).toFixed(1)}%`], ['EV', (a.ev / a.w).toFixed(2)], ['Equity', `${(100 * a.eq / a.w).toFixed(1)}%`]];
      const tip = {
        text: `${labels[key]} · ${caption}\n` + (st ? st.actions.map((action, i) => `${action} ${(100 * st.freqs[i]).toFixed(1)}%`).join('\n') + '\n' : 'No decision for this player here.\n') + metrics.map(([label, value]) => `${label}: ${value}`).join('\n'),
        html: `<div class="rep-tip-heading"><b>${esc(labels[key])}</b><span class="dim">${esc(caption)}</span></div>` +
          (st ? `<div class="tip-rows">${strategyTooltipRows(st)}</div>` : '<div class="dim">No decision for this player here.</div>') +
          `<div class="tip-rows">${metrics.map(([label, value]) => `<span class="dim">${label}</span><span>${value}</span>`).join('')}</div>`,
      };
      const bar = isActor ? revIdx(a.f.length).map(i =>
        `<div style="width:${(100 * a.f[i] / a.w).toFixed(1)}%;background:${colors[i]}"></div>`).join('') : '';
      return `<div class="combo-row" ${tooltipAttributes(tip)}><span class="cname" style="min-width:120px">${esc(labels[key])}</span>` +
        `<span class="cnum" style="min-width:52px"><i class="rep-share" style="width:${Math.min(100, share * 100).toFixed(1)}%"></i>${(100 * share).toFixed(1)}%</span>` +
        `<span class="cbar">${bar}</span>` +
        `<span class="cnum">${(a.ev / a.w).toFixed(2)}</span><span class="cnum">${(100 * a.eq / a.w).toFixed(1)}</span></div>`;
    }).join('');
    el.innerHTML = `<h3>HAND CLASSES <button type="button" class="info-dot" aria-label="How classes are weighted" data-tip="Each class is weighted by how much of it reaches this point on each flop.">?</button></h3>` + head + hrow + body;
    bindSortHeaders(el);
    el.querySelectorAll('.rep-cats-head [data-d]').forEach(b => b.addEventListener('click', () => { S.catDim = b.dataset.d; render(); }));
    el.querySelectorAll('.rep-cats-head [data-p]').forEach(b => b.addEventListener('click', () => { S.catPlayer = +b.dataset.p; render(); }));
  }

  // ----- texture groups + feature charts -----

  function stackedBar(agg) {
    if (!agg.strat) return '';
    const colors = stratColors(agg.strat);
    return revIdx(agg.strat.freqs.length).map(a =>
      `<div style="width:${(100 * agg.strat.freqs[a]).toFixed(1)}%;background:${colors[a]}"></div>`).join('');
  }

  function renderTextures(rows) {
    const el = els.textures;
    if (!el) return;
    el.innerHTML = '';
    if (!rows.length) { el.innerHTML = '<p class="rep-empty dim">No flops match this filter. Select ALL to reset.</p>'; return; }
    el.classList.remove('hidden');
    const groups = TEX.filter(([k]) => k !== 'all').map(([k, l]) => {
      const rs = rows.filter(r => texOf(r.board)[k]);
      return { k, l, n: rs.length, agg: aggregate(rs) };
    }).filter(g => g.n > 0);
    const aggr = g => g.agg.strat ? g.agg.strat.freqs.reduce((s, f, i) =>
      s + ((g.agg.strat.kinds[i] === 'bet' || g.agg.strat.kinds[i] === 'raise') ? f : 0), 0) : 0;
    const { key, dir } = S.textureSort;
    const value = g => key === 'count' ? g.n : key === 'bet' ? aggr(g) : metric({ ...g.agg, group: true }, key);
    groups.sort((a, b) => dir * (key === 'name' ? b.l.localeCompare(a.l) : value(b) - value(a)));
    el.innerHTML = `<h3>BY TEXTURE <button type="button" class="info-dot" aria-label="Texture grouping" data-tip="Groups overlap — a flop can belong to several. Strategy and EV are pooled within the current filter.">?</button><span class="rep-section-note">${rows.length} flops · click a texture name to view its flops</span></h3>` +
      // Strategy and Bet % are one quantity: one sortable heading, one arrow,
      // one sort state (the number keeps its column for alignment only).
      `<div class="combo-row head">` + sortHeading('name', 'Texture', 'cname', 'min-width:90px') + sortHeading('count', 'Flops', 'cnum', 'min-width:48px') + sortHeading('bet', 'Strategy', 'cbar') +
      `<span class="cnum" aria-hidden="true"></span>` + sortHeading('ev0', 'OOP EV', 'cnum') + sortHeading('ev1', 'IP EV', 'cnum') + sortHeading('eq0', 'OOP EQ', 'cnum') + sortHeading('eqr0', 'OOP EQR', 'cnum') + '</div>' +
      groups.map(g =>
        `<div class="combo-row" ${tooltipAttributes(flopTooltip({ ...g.agg, group: true, label: g.l, n: g.n }))}><button type="button" class="cname rep-texture-link" style="min-width:90px" data-t="${g.k}" data-tip="Filter Table to ${g.l.toLowerCase()} (replaces the current filter)">${g.l}</button><span class="cnum" style="min-width:48px">${g.n}</span>` +
        `<span class="cbar">${stackedBar(g.agg)}</span><span class="cnum">${(100 * aggr(g)).toFixed(0)}%</span>` +
        `<span class="cnum">${g.agg.players[0].ev.toFixed(2)}</span><span class="cnum">${g.agg.players[1].ev.toFixed(2)}</span>` +
        `<span class="cnum">${(100 * g.agg.players[0].eq).toFixed(1)}</span><span class="cnum">${(100 * g.agg.players[0].eqr).toFixed(0)}%</span></div>`).join('');
    bindSortHeaders(el);
    el.querySelectorAll('[data-t]').forEach(r => r.addEventListener('click', () => {
      S.tex = r.dataset.t; S.display = 'table'; S.grouping = 'flops'; S.selected = null; render();
    }));
  }

  function renderFeatures(rows) {
    const el = els.features;
    if (!el) return;
    el.innerHTML = '';
    const st0 = rows.map(stratOf).find(x => x);
    if (!rows.length || !st0) { el.classList.add('hidden'); return; }
    el.classList.remove('hidden');
    const aggr = agg => agg.strat ? agg.strat.freqs.reduce((s, f, i) =>
      s + ((agg.strat.kinds[i] === 'bet' || agg.strat.kinds[i] === 'raise') ? f : 0), 0) : 0;
    const charts = [
      { title: 'BY HIGH CARD', groups: ['A', 'K', 'Q', 'J', 'T', '9', '8', '7-'].map(l => [l, r => {
        const hi = texOf(r.board)._rs[0];
        return l === '7-' ? hi <= 5 : RANKS[hi] === l;
      }]) },
      { title: 'BY PAIRING', groups: [['unpaired', r => !texOf(r.board).paired], ['paired', r => texOf(r.board).paired]] },
      { title: 'BY SUITS', groups: [['rainbow', r => texOf(r.board).rainbow], ['two-tone', r => texOf(r.board).twotone], ['monotone', r => texOf(r.board).mono]] },
      { title: 'BY CONNECTEDNESS', groups: [['connected (span ≤4)', r => { const t = texOf(r.board); return !t.paired && t._span <= 4; }],
        ['medium (5–8)', r => { const t = texOf(r.board); return !t.paired && t._span >= 5 && t._span <= 8; }],
        ['wide (9+)', r => { const t = texOf(r.board); return !t.paired && t._span >= 9; }]] },
    ];
    const actorName = posName(st0.actor);
    el.innerHTML = `<h3>${esc(actorName)} AGGRESSION BY FLOP FEATURE <button type="button" class="info-dot" aria-label="What this chart pools" data-tip="Bet + raise frequency of the acting player, pooled within each feature group; OOP’s EV beside it.">?</button></h3>` +
      `<div class="rep-feat-grid">` + charts.map(ch => {
        const rowsHtml = ch.groups.map(([label, pred]) => {
          const rs = rows.filter(pred);
          if (!rs.length) return '';
          const agg = aggregate(rs);
          const a = aggr(agg);
          return `<div class="rep-feat-row" ${tooltipAttributes(flopTooltip({ ...agg, group: true, label, n: rs.length }))}>` +
            `<span class="rep-feat-label">${esc(label)}</span><span class="rep-feat-bar"><i style="width:${(100 * a).toFixed(1)}%"></i></span>` +
            `<span class="rep-feat-num">${(100 * a).toFixed(0)}%</span><span class="rep-feat-ev dim">${agg.players[0].ev.toFixed(2)}</span></div>`;
        }).join('');
        return rowsHtml ? `<div class="rep-feat"><div class="rep-feat-title">${ch.title}<span class="dim"> · bet % · OOP EV</span></div>${rowsHtml}</div>` : '';
      }).join('') + `</div>`;
  }

  updateVillainGate();
  refreshLibrary();
  pollStatus();
  return { refreshLibrary };
}
