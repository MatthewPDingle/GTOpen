// FLOP REPORTS — solve the current SETUP spot across a canonical flop
// subset and study aggregate strategy/EV/EQ/EQR by texture, GTO-style.
// Chart = one thin stacked frequency bar per flop (the app's semantic
// action colors, aggressive→passive fixed order), hover tooltips, click
// to inspect + open in Browse. Table + legend ship alongside (identity
// is never color-alone).

import { api } from './api.js';

const RANKS = '23456789TJQKA';

export function initReports({ els, toast, currentSpot, villains, openInBrowse }) {
  const S = {
    report: null,      // loaded report json
    sort: { key: 'rank', dir: -1 },
    tex: 'all',
    node: 'root',      // 'root' (OOP first decision) | 'vs_check' (IP reply)
    selected: null,    // board string
    polling: null,
  };

  // ---------------------------------------------------------- helpers ----

  // escape user-supplied text before interpolating into innerHTML/attributes
  const esc = s => String(s).replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  const cardsOf = b => [b.slice(0, 2), b.slice(2, 4), b.slice(4, 6)];
  function texOf(board) {
    const cs = cardsOf(board);
    const rs = cs.map(c => RANKS.indexOf(c[0])).sort((a, b) => b - a);
    const suits = new Set(cs.map(c => c[1]));
    const paired = new Set(rs).size < 3;
    const span = rs[0] - rs[2];
    return {
      all: true,
      rainbow: suits.size === 3,
      twotone: suits.size === 2,
      mono: suits.size === 1,
      paired,
      connected: !paired && span <= 4,
      acehigh: rs[0] === 12,
      broadway: rs[0] === 11 || rs[0] === 10,
      mid: rs[0] >= 7 && rs[0] <= 9,
      low: rs[0] <= 6,
    };
  }
  const TEX = [
    ['all', 'ALL'], ['rainbow', 'RAINBOW'], ['twotone', 'TWO-TONE'],
    ['mono', 'MONO'], ['paired', 'PAIRED'], ['connected', 'CONNECTED'],
    ['acehigh', 'A-HIGH'], ['broadway', 'K/Q-HIGH'], ['mid', 'MID'], ['low', 'LOW'],
  ];

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
  const stratOf = row => (S.node === 'root' ? row.root : row.vs_check) || null;
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
        const rs = cardsOf(row.board).map(c => RANKS.indexOf(c[0]));
        return rs[0] * 169 + rs[1] * 13 + rs[2];
      }
    }
  };

  function visibleRows() {
    if (!S.report) return [];
    const rows = S.report.flops.filter(r => texOf(r.board)[S.tex]);
    const { key, dir } = S.sort;
    return rows.slice().sort((a, b) => dir * (metric(b, key) - metric(a, key)));
  }

  // ---------------------------------------------------------- library ----

  let libraryNames = [];
  async function refreshLibrary() {
    let list = [];
    try { list = await api.reportsList(); } catch { return; }
    libraryNames = list.map(r => r.name);
    els.library.innerHTML = '';
    if (!list.length) {
      els.library.innerHTML =
        '<div class="dim" style="font-size:11px;padding:6px 2px">no reports yet — configure a spot in SETUP and run one</div>';
      return;
    }
    for (const r of list) {
      const row = document.createElement('button');
      row.className = 'report-item';
      const when = r.created ? new Date(r.created * 1000).toISOString().slice(0, 10) : '';
      row.innerHTML = `<b>${esc(r.name)}</b><span class="dim">${r.n_flops} flops` +
        `${r.villain ? ' · vs ' + esc(r.villain) : ''}${r.complete ? '' : ' · PARTIAL'} · ${when}</span>`;
      row.addEventListener('click', () => loadReport(r.name));
      els.library.appendChild(row);
    }
  }

  async function loadReport(name) {
    try {
      S.report = await api.reportsGet(name);
      S.selected = null;
      render();
    } catch (e) { toast(e.message, true); }
  }

  // ------------------------------------------------------------- run ----

  // 'vs modeled villain' only works with a same-session Preflop Lab export
  // (context is lost on reload) — disable the box instead of silently
  // dropping the villain from the run.
  const villainRow = els.vsVillain.closest('label') || els.vsVillain.parentElement;
  const villainTip = villainRow ? villainRow.dataset.tip : '';
  function updateVillainGate() {
    const has = !!villains();
    els.vsVillain.disabled = !has;
    if (!has) els.vsVillain.checked = false;
    if (villainRow) {
      villainRow.classList.toggle('dim', !has);
      villainRow.dataset.tip = has ? villainTip :
        'No modeled villain in this session — build the spot from a PREFLOP LAB export first (villain context does not survive a reload).';
    }
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
    const body = {
      name, spot,
      flops: +els.flops.value,
      max_iterations: 600,
      target: 0.35,
    };
    if (els.vsVillain.checked) {
      const v = villains();
      if (!v) {
        updateVillainGate();
        return toast('vs modeled villain: no villain context in this session — rebuild the spot from a PREFLOP LAB export or untick the box', true);
      }
      body.villain = v;
    }
    try {
      await api.reportsRun(body);
      els.progress.textContent = `starting "${name}"…`;
      toast(`report "${name}" running — ${body.flops} flops${body.villain ? ' vs ' + body.villain.name : ''}`);
      pollStatus(true);
    } catch (e) {
      els.progress.textContent = '';
      toast(e.message, true);
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
        active = true;
        els.progress.textContent =
          `${st.name}: ${st.done}/${st.total} · ${st.board} · ${(st.seconds / 60).toFixed(1)} min`;
      } else {
        if (active || els.progress.textContent) {
          els.progress.textContent = st.error ? `failed: ${st.error}` : '';
          if (st.error) { toast(st.error, true); refreshLibrary(); }
          else if (st.name) { toast(`report "${st.name}" done`); refreshLibrary(); loadReport(st.name); }
        }
        clearInterval(S.polling);
        S.polling = null;
      }
    }, 2000);
  }

  // ----------------------------------------------------------- viewer ----

  function render() {
    const rep = S.report;
    els.viewer.classList.toggle('hidden', !rep);
    if (!rep) return;
    const v = rep.villain ? ` · villain: ${rep.villain.name}` : '';
    els.title.textContent = `${rep.name} — ${rep.flops.length} flops${v}`;
    els.subtitle.textContent =
      `pot ${rep.spot.starting_pot} · stack ${rep.spot.effective_stack} · rake ${rep.spot.rake_pct}%` +
      ` · target ${rep.target_pct}% pot${rep.complete ? '' : ' · PARTIAL RUN'}`;

    // controls (idempotent rebuild)
    els.controls.innerHTML =
      `<div class="seg" id="rep-node">` +
      `<button data-n="root" class="${S.node === 'root' ? 'active' : ''}" data-tip="The first decision on the flop (OOP acting into the pot).">OOP ROOT</button>` +
      `<button data-n="vs_check" class="${S.node === 'vs_check' ? 'active' : ''}" data-tip="IP's reply after OOP checks — the c-bet view.">IP VS CHECK</button></div>` +
      `<select id="rep-sort" data-tip="Order the flop strip and table (the table column headers sort too).">` +
      ['rank|board', 'bet|bet %', 'ev0|OOP EV', 'ev1|IP EV', 'eq0|OOP EQ', 'eq1|IP EQ', 'eqr0|OOP EQR', 'eqr1|IP EQR']
        .map(o => { const [k, l] = o.split('|'); return `<option value="${k}" ${S.sort.key === k ? 'selected' : ''}>${l}</option>`; }).join('') +
      `</select>` +
      `<div class="seg" id="rep-tex">` +
      TEX.map(([k, l]) => `<button data-t="${k}" class="${S.tex === k ? 'active' : ''}">${l}</button>`).join('') +
      `</div>`;
    els.controls.querySelectorAll('#rep-node button').forEach(b =>
      b.addEventListener('click', () => { S.node = b.dataset.n; render(); }));
    els.controls.querySelector('#rep-sort').addEventListener('change', e => {
      S.sort = { key: e.target.value, dir: -1 }; render();
    });
    els.controls.querySelectorAll('#rep-tex button').forEach(b =>
      b.addEventListener('click', () => { S.tex = b.dataset.t; render(); }));

    const rows = visibleRows();
    drawStrip(rows);
    renderAggregate(rows);
    renderTable(rows);
    renderDetail();
    renderLegend(rows);
  }

  function renderLegend(rows) {
    els.legend.innerHTML = '';
    const st = rows.map(stratOf).find(x => x);
    if (!st) return;
    const colors = stratColors(st);
    st.actions.forEach((a, i) => {
      els.legend.innerHTML += `<span class="key"><i style="background:${colors[i]}"></i>${a}</span>`;
    });
  }

  function renderAggregate(rows) {
    if (!rows.length) { els.aggregate.innerHTML = ''; return; }
    const st0 = rows.map(stratOf).find(x => x);
    if (!st0) { els.aggregate.innerHTML = ''; return; }
    const na = st0.freqs.length;
    const sums = new Array(na).fill(0);
    let wtot = 0;
    const m = { ev0: 0, ev1: 0, eq0: 0, eqr0: 0 };
    for (const r of rows) {
      const st = stratOf(r);
      const w = r.weight || 1;
      wtot += w;
      if (st) for (let a = 0; a < na; a++) sums[a] += (st.freqs[a] || 0) * w;
      m.ev0 += r.players[0].ev * w; m.ev1 += r.players[1].ev * w;
      m.eq0 += r.players[0].eq * w; m.eqr0 += r.players[0].eqr * w;
    }
    const colors = stratColors(st0);
    const bar = sums.map((s, a) =>
      `<div style="width:${(100 * s / wtot).toFixed(1)}%;background:${colors[a]}" data-tip="${st0.actions[a]}: ${(100 * s / wtot).toFixed(1)}% weighted over ${rows.length} flops"></div>`).join('');
    els.aggregate.innerHTML =
      `<span class="cname" data-tip="Iso-weighted average over the ${rows.length} flops shown.">avg·${rows.length}</span>` +
      `<span class="cbar">${bar}</span>` +
      `<span class="cnum">${(m.ev0 / wtot).toFixed(2)}</span><span class="cnum">${(m.ev1 / wtot).toFixed(2)}</span>` +
      `<span class="cnum">${(100 * m.eq0 / wtot).toFixed(1)}</span><span class="cnum">${(100 * m.eqr0 / wtot).toFixed(0)}%</span>`;
  }

  function drawStrip(rows) {
    const cv = els.canvas;
    const W = cv.clientWidth || 1100;
    const H = 190;
    const dpr = window.devicePixelRatio || 1;
    cv.width = W * dpr; cv.height = H * dpr;
    const ctx = cv.getContext('2d');
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, W, H);
    S.stripW = W;      // hitmap coordinate space — rowAt() rescales from CSS px
    S.hitmap = [];
    if (!rows.length) return;
    const bw = Math.max(2, Math.floor(W / rows.length) - 1);
    const step = W / rows.length;
    rows.forEach((r, i) => {
      const st = stratOf(r);
      const x = Math.floor(i * step);
      S.hitmap.push({ x0: x, x1: x + step, row: r });
      if (!st) return;
      const colors = stratColors(st);
      // draw passive at the bottom, aggressive stacked on top (fixed order)
      let y = H - 14;
      for (let a = st.freqs.length - 1; a >= 0; a--) {
        const hgt = st.freqs[a] * (H - 18);
        ctx.fillStyle = colors[a];
        ctx.fillRect(x, y - hgt, bw, hgt);
        y -= hgt;
      }
      if (r.board === S.selected) {
        ctx.strokeStyle = '#e6e6e6';
        ctx.strokeRect(x - 0.5, 1.5, bw + 1, H - 16);
      }
    });
    ctx.fillStyle = '#5a5a5a';
    ctx.font = '9px IBM Plex Mono, monospace';
    ctx.fillText(`${rows.length} flops · sorted by ${S.sort.key} · bars = ${S.node === 'root' ? 'OOP root strategy' : 'IP vs check'}`, 4, H - 3);
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
        drawStrip(visibleRows());
    }).observe(view);
  }
  els.canvas.addEventListener('mousemove', ev => {
    const r = rowAt(ev);
    // keep data-tip current per position; tooltip.js re-reads it while the
    // pointer moves. Set '' (not removeAttribute) so the canvas stays a
    // [data-tip] target between bars.
    if (!r) { els.canvas.dataset.tip = ''; return; }
    const st = stratOf(r);
    const parts = st ? st.actions.map((a, i) => `${a} ${(100 * st.freqs[i]).toFixed(0)}%`).join(' · ') : '';
    els.canvas.dataset.tip =
      `${fmtBoard(r.board)} — ${parts} · OOP EV ${r.players[0].ev.toFixed(2)} · EQ ${(100 * r.players[0].eq).toFixed(1)}% · EQR ${(100 * r.players[0].eqr).toFixed(0)}%`;
  });
  els.canvas.addEventListener('click', ev => {
    const r = rowAt(ev);
    if (r) { S.selected = r.board; render(); }
  });

  const SUIT_GLYPH = { c: '♣', d: '♦', h: '♥', s: '♠' };
  const fmtBoard = b => cardsOf(b).map(c => c[0] + SUIT_GLYPH[c[1]]).join('');

  function renderDetail() {
    const r = S.report && S.selected
      ? S.report.flops.find(x => x.board === S.selected) : null;
    els.detail.classList.toggle('hidden', !r);
    if (!r) return;
    const st = stratOf(r);
    els.detail.innerHTML =
      `<b class="mono">${fmtBoard(r.board)}</b> ` +
      `<span class="dim mono" style="font-size:11px">exploit ${r.exploit_pct.toFixed(2)}% · ` +
      (st ? st.actions.map((a, i) => `${a} ${(100 * st.freqs[i]).toFixed(1)}%`).join(' · ') : '') +
      ` · OOP ev ${r.players[0].ev.toFixed(2)} eq ${(100 * r.players[0].eq).toFixed(1)} eqr ${(100 * r.players[0].eqr).toFixed(0)}%` +
      ` · IP ev ${r.players[1].ev.toFixed(2)} eq ${(100 * r.players[1].eq).toFixed(1)} eqr ${(100 * r.players[1].eqr).toFixed(0)}%</span> ` +
      `<button class="btn ghost xs" id="rep-open" data-tip="Load this exact spot + board into SETUP, build and solve it, then study it in Browse.">OPEN IN BROWSE</button>`;
    els.detail.querySelector('#rep-open').addEventListener('click', () =>
      openInBrowse(S.report.spot, r.board));
  }

  function renderTable(rows) {
    const el = els.table;
    el.innerHTML = '';
    // headers drive the same sort state as the #rep-sort dropdown (render()
    // rebuilds the dropdown with the current key selected, so they stay in
    // sync); clicking the active column flips direction
    const arrow = k => k === S.sort.key ? (S.sort.dir === -1 ? ' ▲' : ' ▼') : '';
    const cls = k => `ro-sort${k === S.sort.key ? ' sorted' : ''}`;
    const head = document.createElement('div');
    head.className = 'combo-row head';
    head.innerHTML =
      `<span class="cname ${cls('rank')}" data-sort="rank" data-tip="Sort by board rank. Click again to flip direction.">flop${arrow('rank')}</span>` +
      `<span class="cbar ${cls('bet')}" data-sort="bet" style="background:none" data-tip="Sort by total bet/raise frequency. Click again to flip.">strategy${arrow('bet')}</span>` +
      `<span class="cnum ${cls('ev0')}" data-sort="ev0" data-tip="Sort by OOP EV. Click again to flip.">OOP EV${arrow('ev0')}</span>` +
      `<span class="cnum ${cls('ev1')}" data-sort="ev1" data-tip="Sort by IP EV. Click again to flip.">IP EV${arrow('ev1')}</span>` +
      `<span class="cnum ${cls('eq0')}" data-sort="eq0" data-tip="Sort by OOP equity. Click again to flip.">OOP EQ${arrow('eq0')}</span>` +
      `<span class="cnum ${cls('eqr0')}" data-sort="eqr0" data-tip="Equity realization = EV / (equity × pot), shown as a percent like Browse. Click to sort; click again to flip.">OOP EQR${arrow('eqr0')}</span>`;
    head.querySelectorAll('.ro-sort').forEach(h =>
      h.addEventListener('click', () => {
        const k = h.dataset.sort;
        if (S.sort.key === k) S.sort.dir *= -1;   // same column: flip
        else S.sort = { key: k, dir: -1 };        // new column: default order
        render();
      }));
    el.appendChild(head);
    const CAP = 200;
    for (const r of rows.slice(0, CAP)) {
      const st = stratOf(r);
      const colors = st ? stratColors(st) : [];
      const bar = st ? st.freqs.map((f, a) =>
        `<div style="width:${(f * 100).toFixed(1)}%;background:${colors[a]}" data-tip="${st.actions[a]}: ${(f * 100).toFixed(1)}%"></div>`).join('') : '';
      const row = document.createElement('div');
      row.className = 'combo-row' + (r.board === S.selected ? ' sel' : '');
      row.innerHTML = `<span class="cname mono">${fmtBoard(r.board)}</span><span class="cbar">${bar}</span>` +
        `<span class="cnum">${r.players[0].ev.toFixed(2)}</span><span class="cnum">${r.players[1].ev.toFixed(2)}</span>` +
        `<span class="cnum">${(100 * r.players[0].eq).toFixed(1)}</span><span class="cnum">${(100 * r.players[0].eqr).toFixed(0)}%</span>`;
      row.addEventListener('click', () => { S.selected = r.board; render(); });
      el.appendChild(row);
    }
    if (rows.length > CAP) {
      const more = document.createElement('div');
      more.className = 'dim mono';
      more.style.cssText = 'font-size:11px;padding:6px 2px;text-align:center';
      more.textContent = `showing ${CAP} of ${rows.length} flops — refine the texture filter or re-sort to bring targets to the top (strip + averages cover all ${rows.length})`;
      el.appendChild(more);
    }
  }

  updateVillainGate();
  refreshLibrary();
  pollStatus();
  return { refreshLibrary };
}
