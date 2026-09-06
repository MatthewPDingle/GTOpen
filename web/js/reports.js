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
// action colors, aggressive→passive fixed order), hover tooltips, click
// to inspect + open in Browse. Table + legend ship alongside (identity
// is never color-alone).

import { api } from './api.js';
import { MADE_LABELS, MADE_ORDER, DRAW_LABELS, DRAW_ORDER, EQA_LABELS } from './classify.js';

const RANKS = '23456789TJQKA';
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

export function initReports({ els, toast, currentSpot, villains, openInBrowse }) {
  const S = {
    report: null,      // loaded report json
    mode: 'legacy',    // 'lines' when the report carries per-node summaries
    line: '',          // lines mode: current node key ("" = flop root)
    lineData: null,    // lines mode: {history, rows} for S.line
    rows: [],          // lines mode: normalized per-flop rows at S.line
    sort: { key: 'rank', dir: -1 },
    tex: 'all',
    node: 'root',      // legacy: 'root' (OOP first decision) | 'vs_check' (IP reply)
    catDim: 'made',    // category panel: made | draw | eqa
    catPlayer: null,   // category panel: 0 | 1 | null (= the actor)
    selected: null,    // board string
    polling: null,
    lineSeq: 0,        // stale-response guard for line fetches
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
      _rs: rs, _span: span, _suits: suits.size,
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
  const stratOf = row => S.mode === 'lines'
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
        `${r.villain ? ' · vs ' + esc(r.villain) : ''}${r.complete ? '' : ' · PARTIAL'}` +
        `${r.lines ? '' : ' · legacy (2 nodes)'} · ${when}</span>`;
      row.addEventListener('click', () => loadReport(r.name));
      els.library.appendChild(row);
    }
  }

  async function loadReport(name) {
    try {
      const rep = await api.reportsGet(name);
      S.report = rep;
      S.selected = null;
      S.mode = rep.lines ? 'lines' : 'legacy';
      S.line = '';
      S.lineData = null;
      S.rows = [];
      if (S.mode === 'lines') await loadLine('');
      render();
    } catch (e) { toast(e.message, true); }
  }

  /** Fetch one node of the current report (lines mode) and normalize its
   *  per-flop rows into the shape the strip/table/aggregates render. */
  async function loadLine(key) {
    const seq = ++S.lineSeq;
    const data = await api.reportsLines(S.report.name, key);
    if (seq !== S.lineSeq) return; // superseded by a later click
    S.line = key;
    S.lineData = data;
    S.rows = data.rows.map(r => {
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
    if (S.selected && !S.rows.some(r => r.board === S.selected)) S.selected = null;
  }

  async function setLine(key) {
    try {
      await loadLine(key);
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
        const eta = st.done > 0 ? ` · ~${((st.seconds / st.done) * (st.total - st.done) / 60).toFixed(0)} min left` : '';
        els.progress.textContent =
          `${st.name}: ${st.done}/${st.total} · ${st.board} · ${(st.seconds / 60).toFixed(1)} min${eta}`;
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

  const posName = p => (p === 0 ? 'OOP' : 'IP');
  const STREET = ['FLOP', 'TURN', 'RIVER'];

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
    if (!rep) return;
    const v = rep.villain ? ` · villain: ${rep.villain.name}` : '';
    els.title.textContent = `${rep.name} — ${rep.flops.length} flops${v}`;
    const sz = (rep.spot.oop || []).map((s, i) => `${['F', 'T', 'R'][i]} ${s.bet}${s.raise ? ' / r' + s.raise : ''}`).join(' · ');
    els.subtitle.textContent =
      `pot ${rep.spot.starting_pot} · stack ${rep.spot.effective_stack} · rake ${rep.spot.rake_pct}%` +
      ` · sizes ${sz} · target ${rep.target_pct}% pot${rep.complete ? '' : ' · PARTIAL RUN'}`;

    renderRibbon();

    // controls (idempotent rebuild)
    const nodeSeg = S.mode === 'lines' ? '' :
      `<div class="seg" id="rep-node">` +
      `<button data-n="root" class="${S.node === 'root' ? 'active' : ''}" data-tip="The first decision on the flop (OOP acting into the pot).">OOP ROOT</button>` +
      `<button data-n="vs_check" class="${S.node === 'vs_check' ? 'active' : ''}" data-tip="IP's reply after OOP checks — the c-bet view.">IP VS CHECK</button></div>`;
    els.controls.innerHTML = nodeSeg +
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
    renderCategories(rows);
    renderTextures();
    renderFeatures();
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
    hist.forEach((h, d) => {
      const seg = document.createElement('div');
      seg.className = 'hist-seg' + (d === hist.length - 1 ? ' current' : '');
      const head = document.createElement('div');
      head.className = 'hist-head';
      if (h.kind === 'action') {
        head.innerHTML = `<span>${posName(h.actor)} · ${STREET[h.street]}</span><b>${(+h.pot).toFixed(1)}</b>`;
      } else if (h.kind === 'chance') {
        head.innerHTML = `<span>${STREET[h.street]} CARD</span><b>${(+h.pot).toFixed(1)}</b>`;
      } else {
        head.innerHTML = `<span>END</span><b>${(+h.pot).toFixed(1)}</b>`;
      }
      seg.appendChild(head);
      seg.dataset.tip = d === hist.length - 1
        ? `The point you are reading (${h.n_flops} flops carry it). EV OOP ${(+h.ev[0]).toFixed(2)} · IP ${(+h.ev[1]).toFixed(2)}.`
        : `Click to read the report at this earlier point. EV OOP ${(+h.ev[0]).toFixed(2)} · IP ${(+h.ev[1]).toFixed(2)}.`;
      seg.addEventListener('click', () => {
        if (d !== hist.length - 1) setLine(steps.slice(0, d).join(','));
      });
      const next = steps[d]; // the step taken from this point, if any
      if (h.kind === 'action') {
        h.actions.forEach((label, k) => {
          const chip = document.createElement('div');
          const taken = next === `a${k}`;
          chip.className = 'hist-chip' + (taken ? ' taken' : '');
          chip.textContent = `${label} · ${(h.freqs[k] * 100).toFixed(0)}%`;
          chip.dataset.tip = `${posName(h.actor)}: ${label} ${(h.freqs[k] * 100).toFixed(1)}% of the time (all flops, pooled). Click to read the report after this action.`;
          chip.addEventListener('click', e => {
            e.stopPropagation();
            setLine([...steps.slice(0, d), `a${k}`].join(','));
          });
          seg.appendChild(chip);
        });
      } else if (h.kind === 'chance') {
        const chip = document.createElement('div');
        chip.className = 'hist-chip' + (next === 'c' ? ' taken' : '');
        chip.textContent = `any ${STREET[h.street].toLowerCase()} ▸`;
        chip.dataset.tip = `Continue onto the ${STREET[h.street].toLowerCase()}: what follows is pooled over every card that can come, on every flop. For a specific runout open the flop in Browse and use its RUNOUTS REPORT.`;
        chip.addEventListener('click', e => {
          e.stopPropagation();
          setLine([...steps.slice(0, d), 'c'].join(','));
        });
        seg.appendChild(chip);
      } else {
        const chip = document.createElement('div');
        chip.className = 'hist-chip taken';
        chip.textContent = h.kind === 'terminal_fold' ? 'fold — hand over' : 'showdown';
        seg.appendChild(chip);
      }
      el.appendChild(seg);
    });
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
    st.actions.forEach((a, i) => {
      els.legend.innerHTML += `<span class="key"><i style="background:${colors[i]}"></i>${esc(a)}</span>`;
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
      bar = st0.freqs.map((f, a) =>
        `<div style="width:${(100 * f).toFixed(1)}%;background:${colors[a]}" data-tip="${esc(st0.actions[a])}: ${(100 * f).toFixed(1)}% pooled over ${rows.length} flops"></div>`).join('');
    }
    els.aggregate.innerHTML =
      `<span class="cname" data-tip="Iso-weighted average over the ${rows.length} flops shown${S.mode === 'lines' ? ', pooled by how much of each flop’s range reaches this point' : ''}.">avg·${rows.length}</span>` +
      `<span class="cbar">${bar}</span>` +
      `<span class="cnum">${agg.players[0].ev.toFixed(2)}</span><span class="cnum">${agg.players[1].ev.toFixed(2)}</span>` +
      `<span class="cnum">${(100 * agg.players[0].eq).toFixed(1)}</span><span class="cnum">${(100 * agg.players[0].eqr).toFixed(0)}%</span>`;
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
    ctx.fillText(`${rows.length} flops · sorted by ${S.sort.key} · bars = ${nodeCaption()}`, 4, H - 3);
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
      `<button class="btn ghost xs" id="rep-open" data-tip="Load this exact spot + board into SETUP, build and solve it, then study it in Browse${browseSteps().length ? ' at this line' : ''}.">OPEN IN BROWSE</button>`;
    els.detail.querySelector('#rep-open').addEventListener('click', () =>
      openInBrowse(S.report.spot, r.board, browseSteps()));
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
        `<div style="width:${(f * 100).toFixed(1)}%;background:${colors[a]}" data-tip="${esc(st.actions[a])}: ${(f * 100).toFixed(1)}%"></div>`).join('') : '';
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
      `<div class="seg">${[0, 1].map(p => `<button data-p="${p}" class="${player === p ? 'active' : ''}" data-tip="${p === actor ? 'The player acting here: share of range, strategy and EV per hand class.' : 'The other player: share of range and EV per hand class (no decision here).'}">${posName(p)}${p === actor ? ' · ACTING' : ''}</button>`).join('')}</div>` +
      `<span class="dim" style="font-size:10px">${esc(posName(player))}'s range at this point, by hand class — pooled over ${withCats.length} flops</span>` +
      `</div>`;
    const hrow = `<div class="combo-row head"><span class="cname" style="min-width:120px">class</span><span class="cnum" style="min-width:52px">share</span>` +
      `<span class="cbar" style="background:none">${isActor ? 'strategy' : ''}</span><span class="cnum">EV</span><span class="cnum">EQ</span></div>`;
    const body = order.map((key, k) => {
      const a = acc[k];
      if (a.w <= 0) return '';
      const share = a.w / total;
      if (share < 0.002) return '';
      const bar = isActor ? a.f.map((f, i) =>
        `<div style="width:${(100 * f / a.w).toFixed(1)}%;background:${colors[i]}" data-tip="${esc(st0.actions[i])}: ${(100 * f / a.w).toFixed(1)}% of ${esc(labels[key])}"></div>`).join('') : '';
      return `<div class="combo-row"><span class="cname" style="min-width:120px">${esc(labels[key])}</span>` +
        `<span class="cnum" style="min-width:52px"><i class="rep-share" style="width:${Math.min(100, share * 100).toFixed(1)}%"></i>${(100 * share).toFixed(1)}%</span>` +
        `<span class="cbar">${bar}</span>` +
        `<span class="cnum">${(a.ev / a.w).toFixed(2)}</span><span class="cnum">${(100 * a.eq / a.w).toFixed(1)}</span></div>`;
    }).join('');
    el.innerHTML = `<h3>HAND CLASSES <span class="info-dot" tabindex="0" data-tip="How each hand class plays at this point, pooled across the flops shown (each class weighted by how much of it reaches here on each flop). Share = fraction of the range; the strategy bar is the class’s action mix; EV in pot-share chips.">?</span></h3>` + head + hrow + body;
    el.querySelectorAll('.rep-cats-head [data-d]').forEach(b => b.addEventListener('click', () => { S.catDim = b.dataset.d; render(); }));
    el.querySelectorAll('.rep-cats-head [data-p]').forEach(b => b.addEventListener('click', () => { S.catPlayer = +b.dataset.p; render(); }));
  }

  // ----- texture groups + feature charts -----

  function stackedBar(agg) {
    if (!agg.strat) return '';
    const colors = stratColors(agg.strat);
    return agg.strat.freqs.map((f, a) =>
      `<div style="width:${(100 * f).toFixed(1)}%;background:${colors[a]}" data-tip="${esc(agg.strat.actions[a])}: ${(100 * f).toFixed(1)}%"></div>`).join('');
  }

  function renderTextures() {
    const el = els.textures;
    if (!el) return;
    el.innerHTML = '';
    const rows = allRows();
    if (!rows.length) { el.classList.add('hidden'); return; }
    el.classList.remove('hidden');
    const groups = TEX.filter(([k]) => k !== 'all').map(([k, l]) => {
      const rs = rows.filter(r => texOf(r.board)[k]);
      return { k, l, n: rs.length, agg: aggregate(rs) };
    }).filter(g => g.n > 0);
    const aggr = g => g.agg.strat ? g.agg.strat.freqs.reduce((s, f, i) =>
      s + ((g.agg.strat.kinds[i] === 'bet' || g.agg.strat.kinds[i] === 'raise') ? f : 0), 0) : 0;
    el.innerHTML = `<h3>BY TEXTURE <span class="info-dot" tabindex="0" data-tip="The same pooled strategy and EVs, one row per texture group (a flop can belong to several). Click a row to filter the strip and table to that group.">?</span></h3>` +
      `<div class="combo-row head"><span class="cname" style="min-width:90px">texture</span><span class="cnum" style="min-width:40px">flops</span><span class="cbar" style="background:none">strategy</span>` +
      `<span class="cnum">bet %</span><span class="cnum">OOP EV</span><span class="cnum">IP EV</span><span class="cnum">OOP EQ</span><span class="cnum">OOP EQR</span></div>` +
      groups.map(g =>
        `<div class="combo-row rep-texrow${S.tex === g.k ? ' sel' : ''}" data-t="${g.k}"><span class="cname" style="min-width:90px">${g.l}</span><span class="cnum" style="min-width:40px">${g.n}</span>` +
        `<span class="cbar">${stackedBar(g.agg)}</span><span class="cnum">${(100 * aggr(g)).toFixed(0)}%</span>` +
        `<span class="cnum">${g.agg.players[0].ev.toFixed(2)}</span><span class="cnum">${g.agg.players[1].ev.toFixed(2)}</span>` +
        `<span class="cnum">${(100 * g.agg.players[0].eq).toFixed(1)}</span><span class="cnum">${(100 * g.agg.players[0].eqr).toFixed(0)}%</span></div>`).join('');
    el.querySelectorAll('.rep-texrow').forEach(r => r.addEventListener('click', () => {
      S.tex = S.tex === r.dataset.t ? 'all' : r.dataset.t; render();
    }));
  }

  function renderFeatures() {
    const el = els.features;
    if (!el) return;
    el.innerHTML = '';
    const rows = allRows();
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
    el.innerHTML = `<h3>${esc(actorName)} AGGRESSION BY FLOP FEATURE <span class="info-dot" tabindex="0" data-tip="Bet + raise frequency of the acting player at this point, pooled within each flop feature group, with OOP’s EV beside it. Reads the report the way an aggregated-report summary does: where does aggression rise and fall.">?</span></h3>` +
      `<div class="rep-feat-grid">` + charts.map(ch => {
        const rowsHtml = ch.groups.map(([label, pred]) => {
          const rs = rows.filter(pred);
          if (!rs.length) return '';
          const agg = aggregate(rs);
          const a = aggr(agg);
          return `<div class="rep-feat-row" data-tip="${esc(label)}: ${rs.length} flops · ${esc(actorName)} bets/raises ${(100 * a).toFixed(1)}% · OOP EV ${agg.players[0].ev.toFixed(2)} · IP EV ${agg.players[1].ev.toFixed(2)}">` +
            `<span class="rep-feat-label">${esc(label)}</span><span class="rep-feat-bar"><i style="width:${(100 * a).toFixed(1)}%"></i></span>` +
            `<span class="rep-feat-num">${(100 * a).toFixed(0)}%</span><span class="rep-feat-ev dim">${agg.players[0].ev.toFixed(2)}</span></div>`;
        }).join('');
        return `<div class="rep-feat"><div class="rep-feat-title">${ch.title}<span class="dim"> · bet % · OOP EV</span></div>${rowsHtml}</div>`;
      }).join('') + `</div>`;
  }

  updateVillainGate();
  refreshLibrary();
  pollStatus();
  return { refreshLibrary };
}
