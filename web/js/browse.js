// Strategy browser: navigate the tree, render the 13x13 strategy matrix,
// action frequencies, per-combo detail, EV and equity displays.

import { cellInfo, cellCombos, comboIndex, cardToString, cardFromString,
         rank, suit, RANKS, SUIT_GLYPH, SUITS } from './cards.js';
import { api, toast } from './api.js';
import { classify, suitTags, MADE_LABELS, MADE_ORDER, DRAW_LABELS, DRAW_ORDER,
         EQS_LABELS, EQA_LABELS } from './classify.js';

// GTO Wizard default palette.
const ACTION_COLORS = {
  fold: '#4a78c8',
  check: '#5ca75f',
  call: '#5ca75f',
};
// Bet/raise reds by size category (GTOW: Small / Medium / Large / Overbet),
// classified by the wager as a fraction of the pot.
const BET_SHADES = {
  small: '#e8484c',
  medium: '#c24345',
  large: '#a23a3c',
  overbet: '#7c3134',
};
// GTO Wizard player colors: OOP light cyan, IP green.
const EQ_COLORS = ['#8edced', '#46b556'];
// Equity chart margins (CSS px).
const EQ_M = { L: 38, R: 10, T: 12, B: 24 };

function betShade(amount, pot) {
  const pct = pot > 0 ? (amount / pot) * 100 : 100;
  if (pct <= 40) return BET_SHADES.small;
  if (pct <= 80) return BET_SHADES.medium;
  if (pct <= 135) return BET_SHADES.large;
  return BET_SHADES.overbet;
}

export class Browser {
  constructor(els) {
    this.els = els;
    this.path = [];
    this.view = null;
    this.player = 0;     // matrix viewpoint
    this.mode = 'strategy';
    this.selectedCell = null; // pinned by click
    this.hoverCell = null;    // transient mouse-over
    this.handsTab = 'hands';
    // Filters tab state (persists across navigation)
    this.filterMode = 'include';
    this.filterCats = new Set();  // made/draw/eq bucket keys
    this.filterSuits = new Set(); // s0..s3 (suited), o0..o3 (offsuit containing)
    this.filterPreview = null;    // hovered filter: {type:'cat'|'suit', key}
    this.buildMatrix();
    if (this.els.eqCanvas) {
      this.els.eqCanvas.addEventListener('mousemove', e => {
        const r = this.els.eqCanvas.getBoundingClientRect();
        const x = (e.clientX - r.left - EQ_M.L) / (r.width - EQ_M.L - EQ_M.R);
        this.eqHoverX = Math.max(0, Math.min(1, x));
        this.drawEquityChart();
      });
      this.els.eqCanvas.addEventListener('mouseleave', () => {
        this.eqHoverX = null;
        this.drawEquityChart();
      });
    }
    if (this.els.handsTabs) {
      this.els.handsTabs.querySelectorAll('.htab').forEach(b =>
        b.addEventListener('click', () => {
          this.handsTab = b.dataset.v;
          this.els.handsTabs.querySelectorAll('.htab').forEach(x =>
            x.classList.toggle('active', x.dataset.v === this.handsTab));
          this.renderHandsPanel();
        }));
    }
    window.addEventListener('resize', () => this.drawEquityChart());
    // keyboard: Backspace = step back one node, Escape = unpin
    document.addEventListener('keydown', e => {
      const browseActive = document.getElementById('view-browse')?.classList.contains('active');
      const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName || '');
      if (!browseActive || typing || !this.view) return;
      if (e.key === 'Backspace' && this.path.length) {
        e.preventDefault();
        this.navigate(this.path.slice(0, -1));
      } else if (e.key === 'Escape' && this.selectedCell) {
        this.selectedCell = null;
        this.renderMatrix();
        this.renderHandsPanel();
        this.drawEquityChart();
      }
    });
  }

  buildMatrix() {
    const m = this.els.matrix;
    m.innerHTML = '';
    this.cells = [];
    for (let i = 0; i < 13; i++) {
      for (let j = 0; j < 13; j++) {
        const info = cellInfo(i, j);
        const cell = document.createElement('div');
        cell.className = 'cell';
        cell.dataset.i = i; cell.dataset.j = j;
        cell.innerHTML = `<div class="bars"></div><div class="fill"></div><div class="tag">${info.label}</div><div class="sub"></div>`;
        cell.addEventListener('click', () => this.selectCell(i, j));
        cell.addEventListener('mouseenter', () => {
          this.hoverCell = [i, j];
          if (this.hoverDriven()) this.renderHandsPanel();
          this.drawEquityChart();
        });
        m.appendChild(cell);
        this.cells.push(cell);
      }
    }
    m.addEventListener('mouseleave', () => {
      this.hoverCell = null;
      if (this.hoverDriven()) this.renderHandsPanel();
      this.drawEquityChart();
    });
  }

  async refresh() {
    // loading feedback: node EV queries can take a couple of seconds on big trees
    if (this.els.pot) this.els.pot.textContent = 'computing…';
    if (this.els.matrix) this.els.matrix.style.opacity = '.55';
    try {
      this.view = await api.node(this.path);
    } catch (e) {
      toast(`node error: ${e.message}`, true);
      if (this.path.length) { this.path = []; return this.refresh(); }
      this.view = null;
      return;
    }
    // index hands by combo for matrix lookup
    this.handIdx = [new Map(), new Map()];
    for (const p of [0, 1]) {
      this.view.players[p].hands.forEach((h, i) => {
        this.handIdx[p].set(comboIndex(h.c1, h.c2), i);
      });
    }
    // classify every hand for the Filters tab (cheap, done per node)
    const boardCards = this.view.board.map(cardFromString);
    this.cats = [0, 1].map(p =>
      this.view.players[p].hands.map(h => ({
        ...classify(boardCards, h.c1, h.c2, h.eq),
        suits: suitTags(h.c1, h.c2),
      })));
    // auto-follow actor: matrix shows the player to act when at action node
    if (this.view.node_type === 'action') this.player = this.view.player;
    this.blockerSort = null; // action list may differ per node
    this.filterPreview = null;
    // path labels (for lock descriptions) reconstructed from server history
    this.pathLabels = (this.view.history || [])
      .slice(0, this.path.length)
      .map(h => h.kind === 'card' ? (h.card || '?') : (h.actions[h.chosen]?.label || '?'));
    this.renderHistory();
    this.renderActions();
    this.renderMatrix();
    this.renderLegend();
    this.renderHandsPanel();
    this.buildEqCurves();
    this.renderEqStats();
    this.drawEquityChart();
    this.applyFilterPreview(); // clears any stale preview dim
    this.syncSegs();
    this.els.matrix.style.opacity = '';
    this.els.pot.textContent =
      `pot ${fmt(this.view.pot)} · OOP in ${fmt(this.view.put[0])} / IP in ${fmt(this.view.put[1])}`;
  }

  actionColors() {
    if (!this.view || this.view.node_type !== 'action') return [];
    return computeActionColors(this.view.actions, this.view.pot);
  }

  // ----- GTO Wizard-style action history bar -----

  navigate(path) {
    this.path = path;
    this.refresh();
  }

  renderHistory() {
    const el = this.els.history;
    if (!el) return;
    el.innerHTML = '';
    const hist = this.view.history || [];
    const STREETS = ['FLOP', 'TURN', 'RIVER'];

    const seg = (cls = '') => {
      const d = document.createElement('div');
      d.className = `hist-seg ${cls}`;
      el.appendChild(d);
      return d;
    };
    const head = (parent, left, right) => {
      const h = document.createElement('div');
      h.className = 'hist-head';
      h.innerHTML = `<span>${left}</span>${right != null ? `<b>${right}</b>` : ''}`;
      parent.appendChild(h);
      return h;
    };

    // Leading board segment: the initial street's cards + starting pot.
    const cardSteps = hist.filter(h => h.kind === 'card' && h.card).length;
    const initLen = this.view.board.length - cardSteps;
    const rootPot = hist.length ? hist[0].pot : this.view.pot;
    {
      const s = seg(this.path.length === 0 && this.view.node_type !== 'action' ? 'current' : '');
      head(s, STREETS[Math.max(0, initLen - 3)], fmt(rootPot));
      const row = document.createElement('div');
      row.className = 'hist-cards';
      for (let k = 0; k < initLen; k++) {
        const chip = cardChip(this.view.board[k], 'bcard mini');
        chip.dataset.tip = 'Back to the start of the hand.';
        chip.addEventListener('click', () => this.navigate([]));
        row.appendChild(chip);
      }
      s.appendChild(row);
    }

    hist.forEach((h, i) => {
      const prefix = this.path.slice(0, i);
      const isCurrent = i === this.path.length;
      if (h.kind === 'action') {
        const s = seg(isCurrent ? 'current' : '');
        head(s, h.player === 0 ? 'OOP' : 'IP', fmt(h.stack));
        h.actions.forEach((a, k) => {
          const chip = document.createElement('button');
          chip.className = 'hist-chip' + (h.chosen === k ? ' taken' : '');
          chip.textContent = a.label;
          chip.dataset.tip = h.chosen === k ? 'The action taken in this line. Click to return here.' : `Jump to the line where ${a.label.toLowerCase()} happens instead.`;
          chip.addEventListener('click', () =>
            this.navigate([...prefix, { type: 'action', index: k }]));
          s.appendChild(chip);
        });
      } else if (h.kind === 'card') {
        const s = seg(isCurrent ? 'current' : '');
        head(s, STREETS[h.street], fmt(h.pot));
        const row = document.createElement('div');
        row.className = 'hist-cards';
        if (h.card) {
          const chip = cardChip(h.card, 'bcard mini');
          chip.dataset.tip = 'Go back to this card choice — pick a different runout.';
          chip.addEventListener('click', () => this.navigate(prefix));
          row.appendChild(chip);
        } else {
          row.appendChild(facedownChip('bcard mini'));
        }
        s.appendChild(row);
      } else {
        const s = seg(isCurrent ? 'current dim' : 'dim');
        head(s, 'END', null);
        const lbl = document.createElement('div');
        lbl.className = 'hist-chip taken';
        lbl.textContent = this.view.node_type === 'terminal_fold' ? 'Fold' : 'Showdown';
        s.appendChild(lbl);
      }
    });

    // Trailing hint: next street still to come.
    if (this.view.board.length < 5 && this.view.node_type === 'action') {
      const s = seg('dim');
      head(s, STREETS[this.view.street + 1], null);
      const row = document.createElement('div');
      row.className = 'hist-cards';
      row.appendChild(facedownChip('bcard mini'));
      s.appendChild(row);
    }
  }

  // ----- actions panel -----

  renderActions() {
    const el = this.els.actionList;
    const picker = this.els.cardPicker;
    el.innerHTML = '';
    picker.classList.add('hidden');
    this.els.runouts && (this.els.runouts.innerHTML = '');

    if (this.view.node_type === 'action') {
      const colors = this.actionColors();
      const actor = this.view.player;
      const hands = this.view.players[actor].hands;
      this.els.actionsTitle.textContent =
        `${actor === 0 ? 'OOP' : 'IP'} to act — street ${['flop','turn','river'][this.view.street]}`;
      // global frequencies: reach-weighted average strategy
      let totalReach = 0;
      const freqs = this.view.actions.map(() => 0);
      const evs = this.view.actions.map(() => ({ n: 0, d: 0 }));
      hands.forEach(h => {
        if (!h.strategy) return;
        totalReach += h.reach;
        h.strategy.forEach((s, a) => {
          freqs[a] += s * h.reach;
          if (h.evs && h.evs[a] != null) { evs[a].n += h.evs[a] * h.reach * s; evs[a].d += h.reach * s; }
        });
      });
      this.view.actions.forEach((a, k) => {
        const row = document.createElement('div');
        row.className = 'action-row';
        row.dataset.tip = `Click to follow this line. The % is how much of the whole range ${a.label.toLowerCase()}s here; EV is the average for the hands that choose it (so different actions' EVs reflect different hand groups, not a pure comparison).`;
        const freq = totalReach > 0 ? freqs[k] / totalReach : 0;
        const ev = evs[k].d > 1e-9 ? evs[k].n / evs[k].d : null;
        row.innerHTML = `
          <span class="swatch" style="background:${colors[k]}"></span>
          <span class="alabel">${a.label}</span>
          <span class="bar"><i style="width:${(freq * 100).toFixed(1)}%;background:${colors[k]}"></i></span>
          <span class="aev">${ev != null ? 'EV ' + fmt(ev) : ''}</span>
          <span class="afreq">${(freq * 100).toFixed(1)}%</span>`;
        row.addEventListener('click', () => {
          this.path.push({ type: 'action', index: k });
          this.pathLabels.push(a.label);
          this.refresh();
        });
        el.appendChild(row);
      });
      this.renderLockControls(el, colors);
    } else if (this.view.node_type === 'chance') {
      this.els.actionsTitle.textContent =
        `dealing ${this.view.street === 1 ? 'turn' : 'river'} — pick a card`;
      picker.classList.remove('hidden');
      picker.innerHTML = '';
      const avail = new Set(this.view.available_cards);
      // one row per suit (s/h/d/c), one column per rank (A..2)
      for (const s of [3, 2, 1, 0]) {
        for (let r = 12; r >= 0; r--) {
          const cs = RANKS[r] + SUITS[s];
          const b = document.createElement('button');
          b.className = 'pick';
          const glyph = SUIT_GLYPH[SUITS[s]];
          b.innerHTML = `${RANKS[r]}<span class="suit-${SUITS[s]}">${glyph}</span>`;
          if (!avail.has(cs)) b.classList.add('used');
          b.addEventListener('click', () => {
            this.path.push({ type: 'card', card: cs });
            this.pathLabels.push(cs);
            this.refresh();
          });
          picker.appendChild(b);
        }
      }
      // runouts report
      const btn = document.createElement('button');
      btn.className = 'btn';
      btn.style.marginTop = '12px';
      btn.textContent = 'RUNOUTS REPORT';
      btn.dataset.tip = 'Strategy and equity for every possible next card at once — spot which cards favor which player and which runouts get barreled.';
      btn.addEventListener('click', () => this.loadRunouts(btn));
      el.appendChild(btn);
    } else {
      this.els.actionsTitle.textContent = 'Terminal';
      const banner = document.createElement('div');
      banner.className = 'terminal-banner';
      banner.textContent = this.view.node_type === 'terminal_fold'
        ? 'fold — hand over' : 'showdown';
      el.appendChild(banner);
    }
  }

  renderLockControls(el, colors) {
    const wrap = document.createElement('div');
    wrap.style.cssText = 'margin-top:14px;padding-top:10px;border-top:1px solid var(--line)';
    const locked = this.view.locked;
    const lockLabel = this.pathLabels?.length
      ? this.view.board.join('') + ' ' + this.pathLabels.join(' > ') : 'root';
    wrap.innerHTML = `
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
        <span class="dim mono" style="font-size:11px;letter-spacing:.1em">NODE LOCKING${locked ? ' — <span style="color:#e3a73c">LOCKED</span>' : ''}</span>
      </div>
      <div class="dim" style="font-size:11px;margin-bottom:8px">
        Multipliers scale the current strategy per action and renormalize
        (0 = never, 1 = unchanged). Lock, then re-run SOLVE to optimize around it.
      </div>`;
    const inputs = [];
    const grid = document.createElement('div');
    grid.style.cssText = 'display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px';
    this.view.actions.forEach((a, k) => {
      const lab = document.createElement('label');
      lab.style.cssText = 'display:flex;align-items:center;gap:5px;font-size:11px;font-family:var(--font-data)';
      lab.innerHTML = `<i style="display:inline-block;width:10px;height:10px;border-radius:2px;background:${colors[k]}"></i>${a.label}`;
      const inp = document.createElement('input');
      inp.type = 'number'; inp.min = '0'; inp.step = '0.1'; inp.value = '1';
      inp.style.width = '58px';
      inputs.push(inp);
      lab.appendChild(inp);
      grid.appendChild(lab);
    });
    wrap.appendChild(grid);
    const btns = document.createElement('div');
    btns.className = 'btn-row';
    const lockBtn = document.createElement('button');
    lockBtn.className = 'btn';
    lockBtn.textContent = locked ? 'RE-LOCK' : 'LOCK NODE';
    lockBtn.dataset.tip = 'Freeze this node\'s strategy (scaled by the multipliers), then press SOLVE again — the rest of the tree re-optimizes around your assumption. Classic uses: set an action to 0 ("villain never raises here") or force a 100% c-bet.';
    lockBtn.addEventListener('click', async () => {
      try {
        const weights = inputs.map(i => +i.value);
        await api.lock(this.path, weights, lockLabel);
        toast('node locked — re-run SOLVE to apply');
        this.refresh();
      } catch (e) { toast(e.message, true); }
    });
    btns.appendChild(lockBtn);
    if (locked) {
      const un = document.createElement('button');
      un.className = 'btn ghost';
      un.textContent = 'UNLOCK';
      un.addEventListener('click', async () => {
        try { await api.unlock(this.path); toast('unlocked'); this.refresh(); }
        catch (e) { toast(e.message, true); }
      });
      btns.appendChild(un);
    }
    wrap.appendChild(btns);
    el.appendChild(wrap);
  }

  async loadRunouts(btn) {
    btn.disabled = true; btn.textContent = 'computing…';
    let rep;
    try { rep = await api.runouts(this.path); }
    catch (e) { toast(e.message, true); btn.disabled = false; btn.textContent = 'RUNOUTS REPORT'; return; }
    btn.disabled = false; btn.textContent = 'RUNOUTS REPORT';
    const el = this.els.runouts;
    el.innerHTML = '';
    const colors = computeActionColors(rep.actions, this.view ? this.view.pot : 0);
    const head = document.createElement('div');
    head.className = 'combo-row head';
    head.innerHTML = `<span class="cname">card</span><span class="cbar" style="background:none">${rep.player != null ? (rep.player === 0 ? 'OOP' : 'IP') + ' strategy' : ''}</span>
      <span class="cnum">OOP eq</span><span class="cnum">IP eq</span>`;
    el.appendChild(head);
    for (const row of rep.rows) {
      const r = document.createElement('div');
      r.className = 'combo-row';
      const name = `<span class="suit-${row.card[1]}">${row.card[0]}${SUIT_GLYPH[row.card[1]]}</span>`;
      const bar = row.freqs.map((f, k) =>
        `<div style="width:${(f * 100).toFixed(1)}%;background:${colors[k]}" data-tip="${rep.actions[k].label}: ${(f * 100).toFixed(1)}% of range"></div>`).join('');
      r.innerHTML = `<span class="cname">${name}</span><span class="cbar">${bar}</span>
        <span class="cnum">${row.eq[0] != null ? (row.eq[0] * 100).toFixed(1) : '—'}</span>
        <span class="cnum">${row.eq[1] != null ? (row.eq[1] * 100).toFixed(1) : '—'}</span>`;
      el.appendChild(r);
    }
    // legend
    const leg = document.createElement('div');
    leg.className = 'legend';
    rep.actions.forEach((a, k) => {
      leg.innerHTML += `<span class="key"><i style="background:${colors[k]}"></i>${a.label}</span>`;
    });
    el.appendChild(leg);
  }

  // ----- matrix -----

  // ----- filters -----

  filtersActive() {
    return this.filterCats.size > 0 || this.filterSuits.size > 0;
  }

  /** Hover-preview: dim matrix cells with no combos matching the hovered filter. */
  applyFilterPreview() {
    const pv = this.filterPreview;
    const p = this.player;
    for (let i = 0; i < 13; i++) {
      for (let j = 0; j < 13; j++) {
        const cell = this.cells[i * 13 + j];
        if (!pv) { cell.classList.remove('pdim'); continue; }
        let hasMatch = false;
        for (const [a, b] of cellCombos(cellInfo(i, j))) {
          const hi = this.handIdx[p].get(comboIndex(a, b));
          if (hi === undefined) continue;
          const h = this.view.players[p].hands[hi];
          if (h.reach <= 1e-9) continue;
          const c = this.cats[p][hi];
          const m = pv.type === 'suit'
            ? c.suits.has(pv.key)
            : (c.made === pv.key || c.draw === pv.key || c.eqs === pv.key || c.eqa === pv.key);
          if (m) { hasMatch = true; break; }
        }
        cell.classList.toggle('pdim', !hasMatch);
      }
    }
  }

  setFilterPreview(pv) {
    this.filterPreview = pv;
    this.applyFilterPreview();
  }

  /** Does hand index hi of player p pass the active filters? */
  handMatches(p, hi) {
    if (!this.filtersActive()) return true;
    const c = this.cats[p][hi];
    let match = true;
    if (this.filterCats.size) {
      match = this.filterCats.has(c.made) || this.filterCats.has(c.draw)
        || this.filterCats.has(c.eqs) || this.filterCats.has(c.eqa);
    }
    if (match && this.filterSuits.size) {
      match = [...c.suits].some(t => this.filterSuits.has(t));
    }
    return this.filterMode === 'include' ? match : !match;
  }

  cellAgg(i, j, p) {
    // Aggregate hands of player p within a cell class.
    const combos = cellCombos(cellInfo(i, j));
    const hands = this.view.players[p].hands;
    const idx = this.handIdx[p];
    let reach = 0, weight = 0, ev = 0, evW = 0, eq = 0, eqW = 0;
    let strat = null, na = 0;
    if (this.view.node_type === 'action' && this.view.player === p) {
      na = this.view.actions.length;
      strat = new Array(na).fill(0);
    }
    let present = 0;
    for (const [a, b] of combos) {
      const hi = idx.get(comboIndex(a, b));
      if (hi === undefined) continue;
      if (!this.handMatches(p, hi)) continue;
      const h = hands[hi];
      present++;
      reach += h.reach;
      weight += h.weight;
      if (h.ev != null) { ev += h.ev * h.reach; evW += h.reach; }
      if (h.eq != null) { eq += h.eq * h.reach; eqW += h.reach; }
      if (strat && h.strategy) h.strategy.forEach((s, k) => strat[k] += s * h.reach);
    }
    if (strat && reach > 1e-12) strat = strat.map(s => s / reach);
    return { present, total: combos.length, reach, weight,
             ev: evW > 1e-12 ? ev / evW : null,
             eq: eqW > 1e-12 ? eq / eqW : null, strat };
  }

  renderMatrix() {
    const p = this.player;
    const colors = this.actionColors();
    // max class reach for opacity normalization
    let maxReach = 1e-12;
    const aggs = [];
    for (let i = 0; i < 13; i++) {
      for (let j = 0; j < 13; j++) {
        const agg = this.cellAgg(i, j, p);
        aggs.push(agg);
        maxReach = Math.max(maxReach, agg.reach / Math.max(agg.total, 1));
      }
    }
    for (let i = 0; i < 13; i++) {
      for (let j = 0; j < 13; j++) {
        const cell = this.cells[i * 13 + j];
        const agg = aggs[i * 13 + j];
        const bars = cell.querySelector('.bars');
        const fill = cell.querySelector('.fill');
        const sub = cell.querySelector('.sub');
        bars.innerHTML = '';
        fill.style.height = '0';
        cell.classList.toggle('empty', agg.present === 0 || agg.reach <= 1e-9);
        cell.classList.toggle('absent', agg.present === 0);
        cell.classList.toggle('selected',
          this.selectedCell && this.selectedCell[0] === i && this.selectedCell[1] === j);
        const intensity = Math.min(1, (agg.reach / Math.max(agg.total, 1)) / maxReach);
        if (this.mode === 'strategy' && agg.strat) {
          let acc = 0;
          agg.strat.forEach((s, k) => {
            const d = document.createElement('div');
            d.style.width = `${s * 100}%`;
            d.style.background = colors[k];
            bars.appendChild(d);
            acc += s;
          });
          bars.style.opacity = agg.reach > 1e-9 ? (0.35 + 0.65 * intensity) : 0;
          // GTO Wizard "Strategy + EV": show the hand's EV in the cell corner
          sub.textContent =
            agg.ev != null && agg.reach > 1e-9 ? fmt(agg.ev) : '';
        } else if (this.mode === 'strategy') {
          // not the actor: range-weight heat (GTOW "Range" orange)
          bars.style.opacity = 0;
          fill.style.height = '100%';
          fill.style.background = '#f28c26';
          fill.style.opacity = (0.85 * intensity).toFixed(3);
          sub.textContent = '';
        } else if (this.mode === 'ev') {
          bars.style.opacity = 0;
          const v = agg.ev;
          fill.style.height = '100%';
          if (v == null || agg.reach <= 1e-9) { fill.style.opacity = 0; sub.textContent = ''; }
          else {
            fill.style.background = v >= 0 ? '#5ca75f' : '#c24345';
            // scale vs pot
            const rel = Math.min(1, Math.abs(v) / Math.max(this.view.pot, 1e-9));
            fill.style.opacity = (0.15 + 0.75 * rel).toFixed(3);
            sub.textContent = fmt(v);
          }
        } else if (this.mode === 'eq') {
          bars.style.opacity = 0;
          const v = agg.eq;
          fill.style.height = '100%';
          if (v == null || agg.reach <= 1e-9) { fill.style.opacity = 0; sub.textContent = ''; }
          else {
            fill.style.background = `hsl(${(v * 130).toFixed(0)} 55% 42%)`;
            fill.style.opacity = 0.8;
            sub.textContent = Math.round(v * 100) + '%';
          }
        }
      }
    }
  }

  renderLegend() {
    const el = this.els.legend;
    el.innerHTML = '';
    if (this.view.node_type === 'action' && this.mode === 'strategy'
        && this.view.player === this.player) {
      const colors = this.actionColors();
      this.view.actions.forEach((a, k) => {
        const key = document.createElement('span');
        key.className = 'key';
        key.innerHTML = `<i style="background:${colors[k]}"></i>${a.label}`;
        el.appendChild(key);
      });
    } else if (this.mode === 'ev') {
      el.innerHTML = `<span class="key"><i style="background:#5ca75f"></i>EV ≥ 0</span>
                      <span class="key"><i style="background:#c24345"></i>EV &lt; 0</span>`;
    } else if (this.mode === 'eq') {
      el.innerHTML = `<span class="key"><i style="background:hsl(0 55% 42%)"></i>0%</span>
                      <span class="key"><i style="background:hsl(65 55% 42%)"></i>50%</span>
                      <span class="key"><i style="background:hsl(130 55% 42%)"></i>100%</span>`;
    } else {
      el.innerHTML = `<span class="key"><i style="background:#f28c26"></i>range weight</span>`;
    }
  }

  // ----- GTO Wizard-style hands panel (hover-driven) -----

  selectCell(i, j) {
    // click pins/unpins a cell so it stays after the mouse leaves the matrix
    if (this.selectedCell && this.selectedCell[0] === i && this.selectedCell[1] === j) {
      this.selectedCell = null;
    } else {
      this.selectedCell = [i, j];
    }
    this.renderMatrix();
    this.renderHandsPanel();
  }

  renderHandsPanel() {
    const content = this.els.handsContent;
    const label = this.els.handsLabel;
    if (!content) return;
    if (!this.view) { content.innerHTML = ''; label.textContent = ''; return; }
    if (this.handsTab === 'filters') {
      const n = this.filterCats.size + this.filterSuits.size;
      label.textContent = n ? `${n} active · ${this.filterMode}` : '';
      this.renderFiltersPanel(content);
      return;
    }
    if (this.handsTab === 'blockers') {
      label.textContent = '';
      this.renderBlockersPanel(content);
      return;
    }
    const ref = this.hoverCell || this.selectedCell;
    if (!ref) {
      label.textContent = '';
      content.innerHTML = '<div class="dim" style="padding:10px 4px;font-size:11px">hover a hand in the matrix — click to pin</div>';
      return;
    }
    const [i, j] = ref;
    const info = cellInfo(i, j);
    const pinned = this.selectedCell && !this.hoverCell;
    label.textContent = info.label + (pinned ? ' · pinned' : '');

    const p = this.player;
    const hands = this.view.players[p].hands;
    const idx = this.handIdx[p];
    const isActor = this.view.node_type === 'action' && this.view.player === p;
    const colors = this.actionColors();
    const acts = this.view.actions || [];

    const present = [];
    for (const [a, b] of cellCombos(info)) {
      const hi = idx.get(comboIndex(a, b));
      if (hi !== undefined) present.push([hands[hi], a, b, this.handMatches(p, hi)]);
    }
    if (!present.length) {
      content.innerHTML = '<div class="dim" style="padding:10px 4px;font-size:11px">not in range</div>';
      return;
    }

    if (this.handsTab === 'hands') {
      // GTO Wizard layout: 2 columns up to 4 combos, 3 columns beyond.
      const cols3 = present.length > 4;
      const tiles = present.map(([h, a, b, m]) =>
        this.handTile(h, a, b, isActor, colors, acts, cols3, !m));
      content.innerHTML =
        `<div class="hand-tiles${cols3 ? ' cols3' : ''}">${tiles.join('')}</div>`;
    } else {
      content.innerHTML = this.summaryHtml(
        present.filter(x => x[3]), isActor, colors, acts);
    }
  }

  handTile(h, a, b, isActor, colors, acts, compact, dimmed) {
    const name =
      `<span class="suit-${SUITS[suit(a)]}">${RANKS[rank(a)]}${SUIT_GLYPH[SUITS[suit(a)]]}</span>` +
      `<span class="suit-${SUITS[suit(b)]}">${RANKS[rank(b)]}${SUIT_GLYPH[SUITS[suit(b)]]}</span>`;
    const meta = `${h.eq != null ? (h.eq * 100).toFixed(0) + '% eq · ' : ''}EV`;
    let body;
    if (isActor && h.strategy) {
      // Horizontal split, aggressive actions on the left (GTO Wizard style);
      // action labels with EVs overlaid bottom-left/right.
      const segs = [];
      const lines = [];
      for (let k = acts.length - 1; k >= 0; k--) {
        const f = h.strategy[k];
        if (f < 0.001) continue;
        const ev = h.evs && h.evs[k] != null ? fmt(h.evs[k]) : '—';
        segs.push(
          `<div style="flex:${f.toFixed(4)};background:${colors[k]}" ` +
          `data-tip="${acts[k].label}: ${(f * 100).toFixed(1)}% of the time · EV ${ev}"></div>`);
        lines.push(
          `<div class="hand-line"><span class="hl-lab">${acts[k].label}</span>` +
          `<span class="hl-ev">${ev}</span></div>`);
      }
      body = `<div class="htb-h${compact ? ' short' : ''}">` +
        `<div class="hseg-row">${segs.join('')}</div>` +
        `<div class="hand-lines">${lines.join('')}</div></div>`;
    } else {
      body = `<div class="htb flat"><span>EV <b>${h.ev != null ? fmt(h.ev) : '—'}</b></span>` +
        `<span>EQ <b>${h.eq != null ? (h.eq * 100).toFixed(1) + '%' : '—'}</b></span></div>`;
    }
    return `<div class="hand-tile${dimmed ? ' fdim' : ''}"><div class="hth"><span>${name}</span><span class="meta">${meta}</span></div>${body}</div>`;
  }

  // ----- Filters tab (GTO Wizard style) -----

  renderFiltersPanel(content) {
    const p = this.player;
    const hands = this.view.players[p].hands;
    const cats = this.cats[p];
    const isActor = this.view.node_type === 'action' && this.view.player === p;
    const colors = this.actionColors();
    const na = (this.view.actions || []).length;

    // reach + strategy mix per category
    const agg = new Map();
    let totalReach = 0;
    hands.forEach((h, i) => {
      totalReach += h.reach;
      for (const key of [cats[i].made, cats[i].draw, cats[i].eqs, cats[i].eqa]) {
        if (!key) continue;
        let a = agg.get(key);
        if (!a) { a = { reach: 0, strat: new Array(na).fill(0) }; agg.set(key, a); }
        a.reach += h.reach;
        if (isActor && h.strategy) h.strategy.forEach((s, k) => a.strat[k] += s * h.reach);
      }
    });

    const row = (key, label) => {
      const a = agg.get(key);
      const sel = this.filterCats.has(key);
      if ((!a || a.reach <= 1e-12) && !sel) return '';
      const pct = a && totalReach > 1e-12 ? (a.reach / totalReach) * 100 : 0;
      let bar = '';
      if (isActor && a && a.reach > 1e-12) {
        bar = a.strat.map((s, k) =>
          `<div style="width:${((s / a.reach) * 100).toFixed(1)}%;background:${colors[k]}"></div>`).join('');
      }
      return `<div class="filter-row${sel ? ' sel' : ''}" data-key="${key}"
        data-tip="Click to filter the matrix by this category. The bar shows how these hands play here.">
        <span class="fname">${label}</span>
        <span class="fpct">${pct.toFixed(1)}%</span>
        <span class="fbar">${bar}</span></div>`;
    };

    const section = (title, entries) => {
      const rows = entries.map(([k, l]) => row(k, l)).filter(Boolean).join('');
      return rows ? `<div class="filter-sec"><div class="fsec-title">${title}</div>${rows}</div>` : '';
    };

    const suitBtn = (tag, html, tip) =>
      `<button class="suit-btn${this.filterSuits.has(tag) ? ' sel' : ''}" data-suit="${tag}" data-tip="${tip}">${html}</button>`;
    const offsuitBtns = [3, 2, 1, 0].map(s =>
      suitBtn(`o${s}`, `<span class="suit-${SUITS[s]}">${SUIT_GLYPH[SUITS[s]]}</span>`,
        'Offsuit and pocket-pair combos containing this suit.')).join('');
    const suitedBtns = [3, 2, 1, 0].map(s =>
      suitBtn(`s${s}`, `<span class="suit-${SUITS[s]}">${SUIT_GLYPH[SUITS[s]]}${SUIT_GLYPH[SUITS[s]]}</span>`,
        'Suited combos of this suit.')).join('');

    content.innerHTML = `
      <div class="filter-top">
        <div class="seg">
          <button data-fmode="include" class="${this.filterMode === 'include' ? 'active' : ''}"
            data-tip="Matrix shows ONLY hands matching the selected filters.">INCLUDE</button>
          <button data-fmode="exclude" class="${this.filterMode === 'exclude' ? 'active' : ''}"
            data-tip="Matrix hides hands matching the selected filters.">EXCLUDE</button>
        </div>
        <button class="btn ghost" id="filter-clear" data-tip="Clear all active filters.">clear</button>
      </div>
      <div class="filter-suits">
        <span class="dim">Offsuit</span>${offsuitBtns}
        <span class="dim" style="margin-left:12px">Suited</span>${suitedBtns}
      </div>
      <div class="filter-cols">
        <div>
          ${section('Hands', MADE_ORDER.map(k => [k, MADE_LABELS[k]]))}
          ${section('EQ buckets — simple', Object.entries(EQS_LABELS))}
        </div>
        <div>
          ${this.view.board.length < 5 ? section('Draws', DRAW_ORDER.map(k => [k, DRAW_LABELS[k]])) : ''}
          ${section('EQ buckets — advanced', Object.entries(EQA_LABELS))}
        </div>
      </div>`;

    content.querySelectorAll('.filter-row').forEach(r => {
      r.addEventListener('click', () => {
        const k = r.dataset.key;
        if (this.filterCats.has(k)) this.filterCats.delete(k);
        else this.filterCats.add(k);
        this.applyFilters();
      });
      // hover preview: highlight matching hands in the matrix
      r.addEventListener('mouseenter', () =>
        this.setFilterPreview({ type: 'cat', key: r.dataset.key }));
      r.addEventListener('mouseleave', () => this.setFilterPreview(null));
    });
    content.querySelectorAll('.suit-btn').forEach(b => {
      b.addEventListener('click', () => {
        const t = b.dataset.suit;
        if (this.filterSuits.has(t)) this.filterSuits.delete(t);
        else this.filterSuits.add(t);
        this.applyFilters();
      });
      b.addEventListener('mouseenter', () =>
        this.setFilterPreview({ type: 'suit', key: b.dataset.suit }));
      b.addEventListener('mouseleave', () => this.setFilterPreview(null));
    });
    content.querySelectorAll('[data-fmode]').forEach(b =>
      b.addEventListener('click', () => {
        this.filterMode = b.dataset.fmode;
        this.applyFilters();
      }));
    content.querySelector('#filter-clear').addEventListener('click', () => {
      this.filterCats.clear();
      this.filterSuits.clear();
      this.applyFilters();
    });
    // panel was rebuilt: re-sync the preview dim (hovered row may be gone)
    this.applyFilterPreview();
  }

  applyFilters() {
    this.renderMatrix();
    this.renderHandsPanel();
  }

  hoverDriven() {
    return this.handsTab === 'hands' || this.handsTab === 'summary';
  }

  // ----- equity distribution chart (GTO Wizard style) -----

  buildEqCurves() {
    this.eqCurves = [0, 1].map(p => {
      const hands = this.view.players[p].hands;
      const items = hands
        .map((h, i) => ({ i, eq: h.eq, reach: h.reach }))
        .filter(x => x.eq != null && x.reach > 1e-9);
      items.sort((a, b) => a.eq - b.eq);
      const total = items.reduce((s, x) => s + x.reach, 0);
      let acc = 0;
      const pts = [];
      const posByHand = new Map();
      for (const x of items) {
        const xc = total > 0 ? (acc + x.reach / 2) / total : 0;
        acc += x.reach;
        pts.push({ x: xc, y: x.eq, i: x.i });
        posByHand.set(x.i, { x: xc, y: x.eq });
      }
      return { pts, posByHand };
    });
  }

  renderEqStats() {
    const el = this.els.eqStats;
    if (!el) return;
    const pot = this.view.pot;
    el.innerHTML = [0, 1].map(p => {
      const hands = this.view.players[p].hands;
      let r = 0, ev = 0, evW = 0, eq = 0, eqW = 0;
      hands.forEach(h => {
        r += h.reach;
        if (h.ev != null) { ev += h.ev * h.reach; evW += h.reach; }
        if (h.eq != null) { eq += h.eq * h.reach; eqW += h.reach; }
      });
      const avgEv = evW > 1e-12 ? ev / evW : null;
      const avgEq = eqW > 1e-12 ? eq / eqW : null;
      const eqr = avgEv != null && avgEq > 1e-9 ? avgEv / (avgEq * pot) : null;
      return `<div class="eqstat" data-tip="${p === 0 ? 'OOP' : 'IP'} at this node. EQR = equity realization: EV as a fraction of (equity × pot). Under 100% means this range under-realizes its equity — typical for out-of-position or capped ranges.">
        <div class="eqstat-head"><i style="background:${EQ_COLORS[p]}"></i>${p === 0 ? 'OOP' : 'IP'}</div>
        <div class="eqstat-grid">
          <span><label>EV</label><div>${avgEv != null ? fmt(avgEv) : '—'}</div></span>
          <span><label>Equity</label><div>${avgEq != null ? (avgEq * 100).toFixed(1) + '%' : '—'}</div></span>
          <span><label>EQR</label><div>${eqr != null ? (eqr * 100).toFixed(0) + '%' : '—'}</div></span>
          <span><label>Combos</label><div>${r.toFixed(1)}</div></span>
        </div></div>`;
    }).join('');
  }

  drawEquityChart() {
    const cv = this.els.eqCanvas;
    if (!cv || !this.view || !this.eqCurves) return;
    // render at the element's CSS size x devicePixelRatio so text stays crisp
    const rect = cv.getBoundingClientRect();
    if (rect.width < 10) return;
    const dpr = window.devicePixelRatio || 1;
    const wantW = Math.round(rect.width * dpr);
    const wantH = Math.round(rect.height * dpr);
    if (cv.width !== wantW || cv.height !== wantH) {
      cv.width = wantW;
      cv.height = wantH;
    }
    const ctx = cv.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const W = rect.width, H = rect.height;
    const { L, R, T, B } = EQ_M;
    const px = x => L + x * (W - L - R);
    const py = y => H - B - y * (H - T - B);
    ctx.clearRect(0, 0, W, H);

    // grid
    ctx.strokeStyle = '#262626';
    ctx.fillStyle = '#8a8a8a';
    ctx.font = '12px IBM Plex Mono';
    for (const v of [0.25, 0.5, 0.75]) {
      ctx.beginPath(); ctx.moveTo(px(0), py(v)); ctx.lineTo(px(1), py(v)); ctx.stroke();
      ctx.fillText(`${v * 100}`, 8, py(v) + 4);
      ctx.beginPath(); ctx.moveTo(px(v), py(0)); ctx.lineTo(px(v), py(1)); ctx.stroke();
      ctx.fillText(`${v * 100}`, px(v) - 9, H - 7);
    }

    // curves
    for (const p of [1, 0]) {
      const { pts } = this.eqCurves[p];
      if (!pts.length) continue;
      ctx.strokeStyle = EQ_COLORS[p];
      ctx.lineWidth = 1.8;
      ctx.beginPath();
      ctx.moveTo(px(0), py(pts[0].y));
      for (const pt of pts) ctx.lineTo(px(pt.x), py(pt.y));
      ctx.lineTo(px(1), py(pts[pts.length - 1].y));
      ctx.stroke();
    }
    ctx.lineWidth = 1;

    // legend
    [0, 1].forEach(p => {
      ctx.fillStyle = EQ_COLORS[p];
      ctx.beginPath(); ctx.arc(L + 14, T + 10 + p * 17, 4, 0, 7); ctx.fill();
      ctx.fillStyle = '#a8a8a8';
      ctx.fillText(p === 0 ? 'OOP' : 'IP', L + 24, T + 14 + p * 17);
    });

    // hovered/pinned hand combos as dots, on the viewed player's curve only
    const ref = this.hoverCell || this.selectedCell;
    if (ref) {
      const info = cellInfo(ref[0], ref[1]);
      const p = this.player;
      const { posByHand } = this.eqCurves[p];
      for (const [a, b] of cellCombos(info)) {
        const hi = this.handIdx[p].get(comboIndex(a, b));
        if (hi === undefined) continue;
        const pos = posByHand.get(hi);
        if (!pos) continue;
        ctx.fillStyle = '#f5c542';
        ctx.strokeStyle = '#1a1a1a';
        ctx.beginPath();
        ctx.arc(px(pos.x), py(pos.y), 4, 0, 7);
        ctx.fill(); ctx.stroke();
      }
    }

    // crosshair from chart hover: which hand sits at this percentile
    if (this.eqHoverX != null) {
      const xv = this.eqHoverX;
      ctx.strokeStyle = '#555';
      ctx.setLineDash([4, 3]);
      ctx.beginPath(); ctx.moveTo(px(xv), py(0)); ctx.lineTo(px(xv), py(1)); ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = '#c8c8c8';
      ctx.fillText(`${Math.round(xv * 100)}`, px(xv) - 9, H - 7);
      const lines = [];
      for (const p of [0, 1]) {
        const { pts } = this.eqCurves[p];
        if (!pts.length) continue;
        let pt = pts[0];
        for (const q of pts) { if (q.x <= xv) pt = q; else break; }
        const h = this.view.players[p].hands[pt.i];
        lines.push({ p, text: `${p === 0 ? 'OOP' : 'IP'} ${h.combo} ${(pt.y * 100).toFixed(1)}%`, y: pt.y });
        ctx.fillStyle = EQ_COLORS[p];
        ctx.beginPath(); ctx.arc(px(pt.x), py(pt.y), 3.5, 0, 7); ctx.fill();
      }
      // label box
      const bw = 168;
      const bx = Math.min(px(xv) + 10, W - bw - 6);
      const by = T + 8;
      ctx.fillStyle = 'rgba(18,18,18,.92)';
      ctx.fillRect(bx, by, bw, 18 * lines.length + 10);
      lines.forEach((l, k) => {
        ctx.fillStyle = EQ_COLORS[l.p];
        ctx.fillText(l.text, bx + 8, by + 16 + 18 * k);
      });
    }
  }

  // ----- Blockers tab (GTO Wizard style) -----

  renderBlockersPanel(content) {
    const p = this.player;
    const isActor = this.view.node_type === 'action' && this.view.player === p;
    if (!isActor) {
      content.innerHTML = '<div class="dim" style="padding:10px 4px;font-size:11px">' +
        'Blocker effects are shown for the player to act — navigate to one of their decision nodes.</div>';
      return;
    }
    const hands = this.view.players[p].hands;
    const acts = this.view.actions;
    const na = acts.length;
    const colors = this.actionColors();
    const boardSet = new Set(this.view.board.map(cardFromString));

    // overall action mix + per-card mix among hands containing the card
    const overall = new Array(na).fill(0);
    let totalReach = 0;
    const perCard = new Map(); // card -> {reach, strat[]}
    hands.forEach(h => {
      if (!h.strategy || h.reach <= 0) return;
      totalReach += h.reach;
      h.strategy.forEach((s, k) => overall[k] += s * h.reach);
      for (const c of [h.c1, h.c2]) {
        let e = perCard.get(c);
        if (!e) { e = { reach: 0, strat: new Array(na).fill(0) }; perCard.set(c, e); }
        e.reach += h.reach;
        if (h.strategy) h.strategy.forEach((s, k) => e.strat[k] += s * h.reach);
      }
    });
    if (totalReach <= 1e-12) {
      content.innerHTML = '<div class="dim" style="padding:10px 4px;font-size:11px">no hands reach this node</div>';
      return;
    }
    const overallFreq = overall.map(x => x / totalReach);

    const rows = [];
    for (const [c, e] of perCard) {
      if (boardSet.has(c) || e.reach <= 1e-9) continue;
      const deltas = e.strat.map((x, k) => x / e.reach - overallFreq[k]);
      rows.push({ c, deltas });
    }
    if (this.blockerSort == null || (this.blockerSort.col !== 'card' && this.blockerSort.col >= na)) {
      // default: the most-played aggressive action (its deltas are the
      // meaningful blocker signal), falling back to the most-played action
      let k = 0, best = -1;
      for (let a = 0; a < na; a++) {
        const aggr = acts[a].kind === 'bet' || acts[a].kind === 'raise';
        const score = overallFreq[a] + (aggr ? 1 : 0);
        if (score > best) { best = score; k = a; }
      }
      this.blockerSort = { col: k, dir: -1 }; // desc: strongest positive first
    }
    const { col: sortCol, dir: sortDir } = this.blockerSort;
    const cmp = sortCol === 'card'
      ? (a, b) => a.c - b.c
      : (a, b) => a.deltas[sortCol] - b.deltas[sortCol];
    rows.sort((a, b) => (sortDir === -1 ? cmp(b, a) : cmp(a, b)));
    const maxAbs = rows.reduce((m, r) => Math.max(m, ...r.deltas.map(Math.abs)), 1e-9);

    const arrow = k =>
      k === sortCol ? (sortDir === -1 ? ' ▼' : ' ▲') : '';
    const header =
      `<div class="blocker-row head" style="grid-template-columns:52px repeat(${na},1fr)">` +
      `<span class="bk-head${sortCol === 'card' ? ' sorted' : ''}" data-sort="card" ` +
      `data-tip="Sort by card (rank, then suit). Click again to flip direction.">cards${arrow('card')}</span>` +
      acts.map((a, k) =>
        `<span class="bk-head${k === sortCol ? ' sorted' : ''}" data-sort="${k}" ` +
        `data-tip="Sort by this action's blocker shift — descending puts the strongest positive effect on top; click again for ascending (strongest negative)."><i style="background:${colors[k]}"></i>${a.label}${arrow(k)}</span>`
      ).join('') + `</div>`;

    const body = rows.map(r => {
      const cardHtml =
        `<span class="bk-card"><b>${RANKS[rank(r.c)]}</b><span class="suit-${SUITS[suit(r.c)]}">${SUIT_GLYPH[SUITS[suit(r.c)]]}</span></span>`;
      const cells = r.deltas.map(d => {
        const t = Math.min(1, Math.abs(d) / maxAbs);
        const bg = d >= 0
          ? `hsl(${70 + 50 * t} 50% ${40 - 6 * t}%)`
          : `hsl(${35 - 27 * t} 65% ${46 - 5 * t}%)`;
        return `<span class="bk-cell" style="background:${bg}">${d >= 0 ? '+' : '−'} ${(Math.abs(d) * 100).toFixed(2)}%</span>`;
      }).join('');
      return `<div class="blocker-row" style="grid-template-columns:52px repeat(${na},1fr)">${cardHtml}${cells}</div>`;
    }).join('');

    content.innerHTML =
      `<div class="dim" style="font-size:11px;margin-bottom:8px">How holding each card shifts ` +
      `${p === 0 ? 'OOP' : 'IP'}'s strategy vs the range average — the essence of blocker selection.</div>` +
      header + `<div class="blocker-body">${body}</div>`;

    content.querySelectorAll('.bk-head').forEach(h =>
      h.addEventListener('click', () => {
        const col = h.dataset.sort === 'card' ? 'card' : +h.dataset.sort;
        if (this.blockerSort && this.blockerSort.col === col) {
          this.blockerSort.dir *= -1; // same column: flip direction
        } else {
          this.blockerSort = { col, dir: -1 };
        }
        this.renderBlockersPanel(content);
      }));
  }

  summaryHtml(present, isActor, colors, acts) {
    let reach = 0, weight = 0, ev = 0, evW = 0, eq = 0, eqW = 0;
    const freqs = acts.map(() => 0);
    const aev = acts.map(() => ({ n: 0, d: 0 }));
    for (const [h] of present) {
      reach += h.reach; weight += h.weight;
      if (h.ev != null) { ev += h.ev * h.reach; evW += h.reach; }
      if (h.eq != null) { eq += h.eq * h.reach; eqW += h.reach; }
      if (isActor && h.strategy) {
        h.strategy.forEach((s, k) => {
          freqs[k] += s * h.reach;
          if (h.evs && h.evs[k] != null) { aev[k].n += h.evs[k] * h.reach * s; aev[k].d += h.reach * s; }
        });
      }
    }
    const stats = `<div class="summary-stats">
      <div class="stat"><label>combos</label><div>${present.length}</div></div>
      <div class="stat"><label>weight</label><div>${weight.toFixed(1)}</div></div>
      <div class="stat"><label>avg EQ</label><div>${eqW > 1e-9 ? (eq / eqW * 100).toFixed(1) + '%' : '—'}</div></div>
      <div class="stat"><label>avg EV</label><div>${evW > 1e-9 ? fmt(ev / evW) : '—'}</div></div>
    </div>`;
    if (!isActor || reach <= 1e-9) return stats;
    const bar = `<div class="summary-bar">` + freqs.map((f, k) =>
      `<div style="width:${(f / reach * 100).toFixed(1)}%;background:${colors[k]}"></div>`).join('') + `</div>`;
    const rows = acts.map((a, k) => {
      const f = reach > 1e-9 ? freqs[k] / reach : 0;
      const e = aev[k].d > 1e-9 ? fmt(aev[k].n / aev[k].d) : '—';
      return `<div class="summary-row"><span class="swatch" style="background:${colors[k]}"></span>` +
        `<span class="lab">${a.label}</span><span class="num"><b>${(f * 100).toFixed(1)}%</b> · EV ${e}</span></div>`;
    }).join('');
    return stats + bar + rows;
  }

  syncSegs() {
    this.els.segPlayer.querySelectorAll('button').forEach(b =>
      b.classList.toggle('active', +b.dataset.v === this.player));
    this.els.segMode.querySelectorAll('button').forEach(b =>
      b.classList.toggle('active', b.dataset.v === this.mode));
  }
}

function fmt(x) {
  if (x == null || Number.isNaN(x)) return '—';
  if (Math.abs(x) < 0.005) x = 0; // avoid "-0.00"
  const a = Math.abs(x);
  if (a >= 100) return x.toFixed(0);
  if (a >= 10) return x.toFixed(1);
  return x.toFixed(2);
}

function computeActionColors(actions, pot) {
  return actions.map(a => {
    if (a.kind === 'bet' || a.kind === 'raise') {
      return betShade(a.amount, pot);
    }
    return ACTION_COLORS[a.kind] || '#888';
  });
}

export function cardChip(cs, cls = 'bcard') {
  const d = document.createElement('div');
  const r = cs[0], s = cs[1];
  d.className = `${cls} cbg-${s}`;
  d.innerHTML = `<span class="rank">${r}</span><span class="pip">${SUIT_GLYPH[s]}</span>`;
  return d;
}

export function facedownChip(cls = 'bcard') {
  const d = document.createElement('div');
  d.className = `${cls} facedown`;
  return d;
}
