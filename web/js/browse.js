// Strategy browser: navigate the tree, render the 13x13 strategy matrix,
// action frequencies, per-combo detail, EV and equity displays.

import { cellInfo, cellCombos, comboIndex, cardToString, cardFromString,
         rank, suit, RANKS, SUIT_GLYPH, SUITS } from './cards.js';
import { api, toast } from './api.js';
import { hasContextualBetting, rootBettingEvidence } from './postflop_context.js';
import { classify, suitTags, MADE_LABELS, MADE_ORDER, DRAW_LABELS, DRAW_ORDER,
         EQS_LABELS, EQA_LABELS } from './classify.js';

// Strategy color palette.
const ACTION_COLORS = {
  fold: '#4a78c8',
  check: '#5ca75f',
  call: '#5ca75f',
};
// Bet/raise reds by size category (Small / Medium / Large / Overbet),
// classified by the wager as a fraction of the pot.
const BET_SHADES = {
  small: '#e8484c',
  medium: '#c24345',
  large: '#a23a3c',
  overbet: '#7c3134',
};
// Player colors: OOP light cyan, IP green.
const EQ_COLORS = ['#8edced', '#46b556'];
// Equity chart margins (CSS px); the roomier left/bottom hold axis titles.
const EQ_M = { L: 50, R: 12, T: 14, B: 38 };

/** Toast suffix for a lock reply that also froze earlier decisions. */
function frozenNote(out) {
  const n = out?.frozen || 0;
  return n ? ` (+${n} earlier decision${n > 1 ? 's' : ''} frozen too)` : '';
}

function betShade(amount, pot) {
  const pct = pot > 0 ? (amount / pot) * 100 : 100;
  if (pct <= 40) return BET_SHADES.small;
  if (pct <= 80) return BET_SHADES.medium;
  if (pct <= 135) return BET_SHADES.large;
  return BET_SHADES.overbet;
}

function stepEq(a, b) {
  if (!a || !b || a.type !== b.type) return false;
  return a.type === 'action' ? a.index === b.index : a.card === b.card;
}
function isPrefix(a, b) {
  return a.length <= b.length && a.every((s, i) => stepEq(s, b[i]));
}

/** Earlier decisions a freeze-earlier lock would still freeze: action steps
 *  on the line whose node (the prefix BEFORE the step, as freeze_line walks
 *  it) carries no lock. Pure so the per-ancestor rule is testable: a lock at
 *  the node being viewed must never make its ancestors look locked. */
export function freezeableAncestors(path, pathLabels, board, isLocked) {
  let n = 0;
  for (let i = 0; i < path.length; i++) {
    if (path[i].type !== 'action') continue;
    const prefix = pathLabels.slice(0, i);
    const desc = prefix.length ? `${board} ${prefix.join(' > ')}` : `${board} root`;
    if (!isLocked(desc)) n++;
  }
  return n;
}

export class Browser {
  constructor(els, hooks = {}) {
    this.els = els;
    /** The app's persistent failure surface (app.js reportError); falls back to
     *  a toast when the browser is constructed on its own. */
    this.onError = hooks.onError || null;
    this.path = [];        // the node currently VIEWED (a prefix of `line`)
    this.line = [];        // the full navigated line (cursor can sit anywhere on it)
    this.lineHistory = null; // cached node history for the whole line (ribbon source)
    this.preflop = null;   // {oop, ip, potBb, effStackBb, segments} from preflop study setup, else null
    this.view = null;
    this._refreshGen = 0;  // serializes overlapping /api/node refreshes (stale-response guard)
    this.lockHistory = null; // server's lock undo/redo stacks (labels), see setLockHistory
    this.lockStepBusy = false;
    // Lock option: also freeze the earlier decisions on the line. On by
    // default — a lock below the root otherwise shifts earlier play silently.
    this.freezeLine = true;
    try {
      const saved = localStorage.getItem('gtopen.freezeLine');
      if (saved != null) this.freezeLine = saved === '1';
    } catch { /* storage off */ }
    this.lockLabels = [];       // GET /api/locks labels (one per locked node)
    this.lockCells = new Map(); // node label -> cells its per-hand lock covers
    try {
      // the server's lock label names only the combo COUNT, so remember which
      // cells this tab locked (validated against /api/locks on every refresh)
      for (const [at, cells] of JSON.parse(sessionStorage.getItem('gtopen.lockCells') || '[]')) {
        this.lockCells.set(at, new Set(cells));
      }
    } catch { /* storage off */ }
    this.pendingLockEdits = 0;  // lock/fit edits since the last finished solve
    this._pendingBase = null;   // solve iteration those edits were made against
    this._pendingGen = 0;
    this.panelBusy = false;     // pointer/focus inside the filters/blockers panel
    this.loadingNode = false;   // a /api/node fetch is in flight (not "no spot")
    this.player = 0;     // matrix viewpoint
    this.mode = 'strategy';
    this.exploit = null;          // /api/exploit payload for EXPLOIT mode
    this._exploitHands = null;    // view-shaped cache of exploit.hands
    this._exploitLoading = false;
    this._exploitGen = 0;         // bumped whenever a cached BR becomes stale (see loadExploit)
    this.comboRows = false; // orientation: false = Horizontal (combined bar), true = Vertical (per-combo columns)
    this.fillMode = 'normalized'; // 'normalized' | 'range' | 'full'
    this.selectedCell = null; // pinned by click
    this.hoverCell = null;    // transient mouse-over
    this.handsTab = 'hands';
    // Filters tab state (persists across navigation)
    this.filterMode = 'include';
    this.filterCats = new Set();  // made/draw/eq bucket keys
    this.filterSuits = new Set(); // s0..s3 (suited), o0..o3 (offsuit containing)
    this.filterPreview = null;    // hovered filter: {type:'cat'|'suit', key}
    this.actionFilter = null;     // selected action tile -> grid shows its range
    this.buildMatrix();
    this.buildBrowseChrome();
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
    // action-history ribbon scrolling: arrows, mouse wheel, and arrow refresh
    if (this.els.histLeft) {
      const step = () => Math.max(140, this.els.history.clientWidth * 0.7);
      this.els.histLeft.addEventListener('click', () =>
        this.els.history.scrollBy({ left: -step(), behavior: 'smooth' }));
      this.els.histRight.addEventListener('click', () =>
        this.els.history.scrollBy({ left: step(), behavior: 'smooth' }));
      this.els.history.addEventListener('scroll', () => this.updateHistNav());
      this.els.history.addEventListener('wheel', e => {
        // let a vertical wheel scroll the ribbon horizontally
        if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
          this.els.history.scrollLeft += e.deltaY;
          e.preventDefault();
        }
      }, { passive: false });
      window.addEventListener('resize', () => this.updateHistNav());
    }
    window.addEventListener('resize', () => this.drawEquityChart());
    // keyboard: Backspace = step back one node, Escape = unpin
    document.addEventListener('keydown', e => {
      const browseActive = document.getElementById('view-browse')?.classList.contains('active');
      const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName || '');
      if (!browseActive || typing || !this.view) return;
      // Ctrl/Cmd+Z undoes the last lock edit; +Shift (or Ctrl+Y) redoes it
      const mod = e.ctrlKey || e.metaKey;
      if (mod && !e.altKey && (e.key.toLowerCase() === 'z' || e.key.toLowerCase() === 'y')) {
        e.preventDefault();
        this.stepLockHistory(e.key.toLowerCase() === 'y' || e.shiftKey ? 'redo' : 'undo');
        return;
      }
      if (e.key === 'Backspace' && this.path.length) {
        e.preventDefault();
        this.viewDepth(this.path.length - 1); // step cursor back, keep the line
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
        cell.tabIndex = (i === 0 && j === 0) ? 0 : -1; // roving tab stop
        cell.setAttribute('role', 'button');
        cell.setAttribute('aria-label', info.label);
        cell.setAttribute('aria-pressed', 'false');
        cell.innerHTML = `<div class="bars"></div><div class="fill"></div>` +
          `<div class="tag">${info.label}</div><div class="sub"></div>` +
          `<i class="lk-mark" aria-hidden="true" style="position:absolute;top:3px;right:4px;` +
          `width:6px;height:6px;border-radius:50%;display:none;z-index:4;pointer-events:none"></i>`;
        cell.addEventListener('click', () => this.selectCell(i, j));
        cell.addEventListener('mouseenter', () => {
          this.hoverCell = [i, j];
          this.renderHandsPanel(); // flips FILTERS/BLOCKERS to HANDS while hovering
          this.drawEquityChart();
          this.showHandPop(i, j, cell);
        });
        // keyboard: focus shows the same hand the pointer would, and a visible
        // ring replaces the transparent outline the grid uses for the mouse
        cell.addEventListener('focus', () => {
          cell.style.outline = '2px solid var(--accent)';
          this.hoverCell = [i, j];
          this.renderHandsPanel();
          this.drawEquityChart();
        });
        cell.addEventListener('blur', () => {
          cell.style.outline = '';
          if (document.activeElement?.closest?.('.matrix')) return;
          this.hoverCell = null;
          this.renderHandsPanel();
          this.drawEquityChart();
        });
        m.appendChild(cell);
        this.cells.push(cell);
      }
    }
    // arrow keys move the roving tab stop, Enter/Space pins the cell (the
    // mouse-free route into the per-hand lock editor)
    m.addEventListener('keydown', e => {
      const cell = e.target.closest?.('.cell');
      if (!cell || cell.parentElement !== m) return;
      const i = +cell.dataset.i, j = +cell.dataset.j;
      const delta = { ArrowUp: [-1, 0], ArrowDown: [1, 0], ArrowLeft: [0, -1], ArrowRight: [0, 1] }[e.key];
      if (delta) {
        e.preventDefault();
        this.focusCell(Math.max(0, Math.min(12, i + delta[0])), Math.max(0, Math.min(12, j + delta[1])));
      } else if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        this.selectCell(i, j);
        this.focusCell(i, j);
      }
    });
    m.addEventListener('mouseleave', () => {
      this.hoverCell = null;
      this.renderHandsPanel(); // reverts to FILTERS/BLOCKERS when leaving the grid
      this.drawEquityChart();
      this.hideHandPop();
    });
  }

  /** Move the matrix's single tab stop and focus that cell. */
  focusCell(i, j) {
    const cell = this.cells?.[i * 13 + j];
    if (!cell) return;
    this.cells.forEach(c => { c.tabIndex = -1; });
    cell.tabIndex = 0;
    cell.focus();
  }

  /** Browse-owned chrome: pending-lock bar, no-spot panel and the filtered-share
   *  line. Built here so every element the view reads has one owner. */
  buildBrowseChrome() {
    if (this.els.matrix?.after) {
      this.emptyEl = document.createElement('div');
      this.emptyEl.style.cssText =
        'display:flex;align-items:center;gap:10px;padding:26px 8px;font-size:12px;color:var(--ink-dim)';
      const txt = document.createElement('span');
      txt.textContent = 'no spot loaded';
      const setup = document.createElement('button');
      setup.className = 'btn sm';
      setup.textContent = 'OPEN SETUP';
      setup.addEventListener('click', () =>
        document.querySelector('.tab[data-tab="setup"]')?.click());
      this.emptyEl.append(txt, setup);
      this.els.matrix.after(this.emptyEl);
    }
    if (this.els.legend?.after) {
      this.filterStateEl = document.createElement('div');
      this.filterStateEl.style.cssText =
        'display:none;align-items:center;gap:8px;font-size:11px;color:var(--ink-dim);margin-top:6px';
      this.els.legend.after(this.filterStateEl);
    }
    const host = document.getElementById('view-browse');
    const top = host?.querySelector('.browse-top');
    if (host && top) {
      this.pendingBar = document.createElement('div');
      this.pendingBar.className = 'pending-locks';
      this.pendingBar.setAttribute('role', 'status');
      this.pendingBar.style.cssText =
        'display:none;align-items:center;gap:10px;position:sticky;top:80px;z-index:40;' +
        'margin:6px 0 2px;padding:5px 9px;font-size:11px;color:var(--ink);' +
        'background:var(--accent-soft);border:1px solid var(--line2);' +
        'border-left:3px solid var(--accent);border-radius:4px';
      host.insertBefore(this.pendingBar, top);
    }
    // A filter/blocker edit must survive the pointer passing over the grid:
    // keep the hover-flip off while the panel holds the pointer or the keyboard.
    const content = this.els.handsContent;
    if (content) {
      const enter = () => { this.panelBusy = true; };
      const leave = () => {
        if (content.contains(document.activeElement) || content.matches(':hover')) return;
        this.panelBusy = false;
        this.renderHandsPanel();
      };
      content.addEventListener('pointerenter', enter);
      content.addEventListener('pointerleave', leave);
      content.addEventListener('focusin', enter);
      // defer: during focusout the browser has not moved focus to the next
      // control yet, and rebuilding the panel here would drop it
      content.addEventListener('focusout', () => setTimeout(leave, 0));
    }
  }

  /** No-spot state: the tab used to render as an empty grid before a build.
   *  A node fetch in flight is "loading", not "no spot". */
  renderEmptyState() {
    if (!this.emptyEl) return;
    const empty = !this.view && !this.loadingNode;
    this.emptyEl.style.display = empty ? 'flex' : 'none';
    if (this.filterStateEl && !this.view) this.filterStateEl.style.display = 'none';
  }

  /** Matched share of the reach in the range under the active filters, and
   *  whether anything matched at all. Null when no filter is on. */
  filterShare() {
    if (!this.view || !this.filtersActive()) return null;
    const p = this.player;
    const hands = this.handsFor(p);
    let matched = 0, total = 0, any = false;
    hands.forEach((h, hi) => {
      if (!(h.reach > 1e-9)) return;
      total += h.reach;
      if (this.handMatches(p, hi)) { matched += h.reach; any = true; }
    });
    return { share: total > 0 ? matched / total : 0, any };
  }

  renderFilterState() {
    const el = this.filterStateEl;
    if (!el) return;
    const fs = this.filterShare();
    el.innerHTML = '';
    if (!fs) { el.style.display = 'none'; return; }
    el.style.display = 'flex';
    const txt = document.createElement('span');
    if (!fs.any) {
      txt.textContent = 'showing 0% of range — no hands match';
      const clear = document.createElement('button');
      clear.className = 'btn ghost xs';
      clear.textContent = 'clear filters';
      clear.addEventListener('click', () => {
        this.filterCats.clear();
        this.filterSuits.clear();
        this.applyFilters();
      });
      el.append(txt, clear);
      return;
    }
    const pct = fs.share * 100;
    txt.textContent = `showing ${pct < 10 ? pct.toFixed(1) : Math.round(pct)}% of range`;
    el.appendChild(txt);
  }

  /** Record a lock/fit edit: the displayed strategy is now stale until the
   *  next solve. The bar replaces the reminder each toast used to repeat. */
  noteLockEdit() {
    this.pendingLockEdits += 1;
    if (this._pendingBase == null) {
      const gen = ++this._pendingGen;
      api.status().then(st => {
        if (gen === this._pendingGen && this._pendingBase == null) this._pendingBase = st.iteration;
      }).catch(() => { /* no baseline: the bar is still true */ });
    }
    this.onLockEdit?.(); // existing hook (app.js resyncs the trust readout)
    this.renderPendingBar();
  }

  renderPendingBar() {
    if (!this.pendingBar) return;
    const n = this.pendingLockEdits;
    this.pendingBar.style.display = n ? 'flex' : 'none';
    this.pendingBar.innerHTML = '';
    if (!n) return;
    const txt = document.createElement('span');
    txt.textContent = `${n} lock edit${n === 1 ? '' : 's'} pending — RE-SOLVE / EXPLOIT`;
    const off = document.createElement('button');
    off.className = 'btn ghost xs';
    off.textContent = '×';
    off.setAttribute('aria-label', 'dismiss the pending-lock reminder');
    off.style.marginLeft = 'auto';
    off.addEventListener('click', () => {
      this.pendingLockEdits = 0;
      this._pendingBase = null;
      this.renderPendingBar();
    });
    this.pendingBar.append(txt, off);
  }

  /** Clear the bar once a solve has finished past the edits' baseline. */
  clearPendingAfterSolve() {
    if (!this.pendingLockEdits || this._pendingBase == null) return;
    const base = this._pendingBase;
    api.status().then(st => {
      if (st.state === 'running' || st.iteration <= base) return;
      this.pendingLockEdits = 0;
      this._pendingBase = null;
      this.renderPendingBar();
    }).catch(() => {});
  }

  // ----- lock composition -----

  /** The spot's root board: view.board includes cards dealt on the way here,
   *  but lock descriptions (like the server's path_description) start from the
   *  board the tree was built on. */
  rootBoard() {
    const dealt = (this.view?.history || []).filter(h => h.kind === 'card' && h.card).length;
    const cards = this.view?.board || [];
    return cards.slice(0, Math.max(0, cards.length - dealt)).join('');
  }

  /** The node's description in the server's own shape (see path_description in
   *  crates/solver): "<flop> root" or "<flop> Check > Bet 3.3". This is the
   *  "at" part the lock labels carry. */
  lockNodeLabel() {
    if (!this.view) return '';
    const board = this.rootBoard();
    return this.pathLabels?.length
      ? `${board} ${this.pathLabels.join(' > ')}`
      : `${board} root`;
  }

  /** Lock labels at the viewed node. GET /api/locks names the node itself (a
   *  manual lock stores its description); the *kind* of lock is only in the
   *  edit history (/api/locks/history), whose labels carry a "Lock …" prefix.
   *  Composed state: per-hand edits stack on an earlier range/solved/fit lock
   *  at the same node, so the history is walked back to that base. */
  lockSummary(at) {
    if (!at) return null;
    const raw = (this.lockLabels || []).filter(l => lockLabelAtNode(l, at));
    if (!raw.length) {
      if (at === this.lockNodeLabel() && this.view?.locked && this.lockHistory?.profile_players?.length) return { kind: 'profile', combos: 0 };
      return null;
    }
    const hist = (this.lockHistory?.undo || []).filter(h => editLabelAtNode(h, at));
    const cur = hist.length ? editKind(hist[0]) : null;
    if (cur && cur.kind !== 'none') {
      if (cur.kind !== 'hands') return cur;
      let combos = cur.combos;
      for (let i = 1; i < hist.length; i++) {
        const k = editKind(hist[i]);
        if (k.kind === 'hands') { combos += k.combos; continue; }
        if (k.kind === 'none') break;
        return { ...k, combos };
      }
      return { kind: 'hands', combos };
    }
    // locks whose kind is written into the label itself
    if (raw.some(l => l.startsWith(`${at} (least exploitable`))) return { kind: 'fit', combos: 0 };
    if (raw.some(l => l.startsWith(`${at} (frozen on the line to `))) return { kind: 'solved', combos: 0 };
    return { kind: 'other', combos: 0 };
  }

  /** Compact lock state for the panel head: "range + 6 combos", "solved", … */
  lockSummaryText(at) {
    const s = this.lockSummary(at);
    if (!s) {
      if (!this.view?.locked) return '';
      return this.lockHistory?.profile_players?.length ? 'profile' : 'locked';
    }
    const words = { range: 'range', solved: 'solved', fit: 'fit', profile: 'profile' };
    const base = words[s.kind] || 'locked';
    if (s.kind === 'hands') return `${s.combos} combo${s.combos === 1 ? '' : 's'}`;
    return s.combos ? `${base} + ${s.combos} combo${s.combos === 1 ? '' : 's'}` : base;
  }

  /** Cells a per-hand lock covers: remembered from this page's edits, plus
   *  edit labels that name their combo ("Lock AsAh · …"). A class lock's
   *  combos are not in the label, so they are only marked while this page
   *  remembers the edit. */
  lockedCellsAt(at) {
    const out = new Set(at ? this.lockCells.get(at) || [] : []);
    if (!at) return out;
    for (const h of this.lockHistory?.undo || []) {
      if (!editLabelAtNode(h, at)) continue;
      if (editKind(h).kind !== 'hands') break; // an earlier base lock reset the node
      const m = h.match(/^Lock ([2-9TJQKA][cdhs][2-9TJQKA][cdhs]) · /);
      if (!m) continue;
      try {
        out.add(comboCell(cardFromString(m[1].slice(0, 2)), cardFromString(m[1].slice(2))));
      } catch { /* not a combo label */ }
    }
    return out;
  }

  rememberLockedCell([i, j], at = this.lockNodeLabel()) {
    if (!at) return;
    if (!this.lockCells.has(at)) this.lockCells.set(at, new Set());
    this.lockCells.get(at).add(`${i},${j}`);
    this.saveLockCells();
  }

  /** Drop a node's per-hand cell marks (whole-range lock, unlock, re-fit). */
  forgetLockCells(at) {
    if (this.lockCells.delete(at)) this.saveLockCells();
  }

  /** Keep only marks whose node still carries a lock. */
  pruneLockCells() {
    const labels = this.lockLabels || [];
    let changed = false;
    for (const at of [...this.lockCells.keys()]) {
      if (!labels.some(l => lockLabelAtNode(l, at))) { this.lockCells.delete(at); changed = true; }
    }
    if (changed) this.saveLockCells();
  }

  saveLockCells() {
    try {
      sessionStorage.setItem('gtopen.lockCells',
        JSON.stringify([...this.lockCells].map(([at, cells]) => [at, [...cells]])));
    } catch { /* storage off */ }
  }

  /** Repaint the head badge when the lock history (the composition source)
   *  arrives after the panel was first drawn. */
  paintLockBadge() {
    const el = this.els.actionList?.querySelector('[data-lock-summary]');
    if (!el) return;
    const text = this.lockSummaryText(this.lockNodeLabel());
    el.textContent = text;
    el.style.display = text ? '' : 'none';
  }

  /** Route an operation failure to the app's persistent error surface. Short
   *  validation prompts stay toasts (nothing failed yet); a failed request or
   *  lock edit must stay on screen with its retry. */
  fail(e, retry = null) {
    if (this.onError) this.onError(e, retry);
    else toast(e.message, true);
  }

  async refresh() {
    // loading feedback: node EV queries can take a couple of seconds on big trees
    this.hideHandPop(); // stale combo popup would show the previous node
    if (this.els.pot) this.els.pot.textContent = 'computing…';
    if (this.els.matrix) this.els.matrix.style.opacity = '.55';
    // Serialize overlapping navigations: the ribbon stays clickable during the
    // multi-second fetch, so only the LATEST refresh may apply its response
    // (same staleness idea as loadRunouts/loadExploit, generation-counted).
    const gen = ++this._refreshGen;
    this.loadingNode = true;
    this.renderEmptyState();
    const locksP = api.locks().catch(() => this.lockLabels || []);
    let view;
    try {
      view = await api.node(this.path);
    } catch (e) {
      if (gen !== this._refreshGen) return; // superseded: a newer refresh owns the UI
      this.loadingNode = false;
      this.fail(e, () => this.refresh());
      if (this.path.length) { this.path = []; this.line = []; this.lineHistory = null; return this.refresh(); }
      this.view = null;
      if (this.els.matrix) this.els.matrix.style.opacity = '';
      if (this.els.pot) this.els.pot.textContent = '—';
      this.renderEmptyState();
      return;
    }
    if (gen !== this._refreshGen) return; // stale response: user navigated again mid-flight
    this.loadingNode = false;
    this.view = view;
    this.lockLabels = await locksP; // which nodes hold a lock
    this.pruneLockCells();
    if (gen !== this._refreshGen) return;
    // lock undo/redo labels: cheap, and kept off the critical path
    api.lockHistory().then(h => { if (gen === this._refreshGen) this.setLockHistory(h); }).catch(() => {});
    this.exploit = null;        // stale for the new node/strategy state
    this._exploitGen++;         // ...and so is any BR request still in flight
    this._exploitHands = null;
    // Maintain the full line: viewing a node ON the line keeps the line intact;
    // a path that isn't a prefix of the line (a new/diverging action) replaces it.
    if (!this.lineHistory || !isPrefix(this.path, this.line)) {
      this.line = this.path.slice();
      this.lineHistory = this.view.history;
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
    this.boardSet = new Set(boardCards); // for board-aware combo-count normalization
    this.cats = [0, 1].map(p =>
      this.view.players[p].hands.map(h => ({
        ...classify(boardCards, h.c1, h.c2, h.eq),
        suits: suitTags(h.c1, h.c2),
      })));
    // auto-follow actor: matrix shows the player to act when at action node
    if (this.view.node_type === 'action') this.player = this.view.player;
    this.blockerSort = null; // action list may differ per node
    this.filterPreview = null;
    this.actionFilter = null; // action set differs per node
    // path labels (for lock descriptions) reconstructed from server history
    this.pathLabels = (this.view.history || [])
      .slice(0, this.path.length)
      .map(h => h.kind === 'card' ? (h.card || '?') : (h.actions[h.chosen]?.label || '?'));
    this.renderHistory();
    this.renderVillainLocks();
    this.renderActions();
    this.onNodeChange?.(this.view, this.path); // e.g. Browse "find best size"
    this.renderMatrix();
    this.renderLegend();
    this.renderHandsPanel();
    this.buildEqCurves();
    this.renderEqStats();
    this.drawEquityChart();
    this.applyFilterPreview(); // clears any stale preview dim
    this.syncSegs();
    // matrix opacity is owned by renderMatrix(): it clears the loading dim on a
    // normal paint and keeps the .45 dim while EXPLOIT data for this node loads
    this.els.pot.textContent =
      `pot ${fmt(this.view.pot)} · ${this.posLabel(0)} in ${fmt(this.view.put[0])} / ${this.posLabel(1)} in ${fmt(this.view.put[1])}`;
    this.renderEmptyState();
    this.clearPendingAfterSolve();
  }

  actionColors() {
    if (!this.view || this.view.node_type !== 'action') return [];
    return computeActionColors(this.view.actions, this.view.pot);
  }

  // ----- action history bar -----

  /** Reset the line + cursor (call when a new spot is built/loaded). */
  reset() {
    this.path = [];
    this.line = [];
    this.lineHistory = null;
    // a session swap (BUILD/LOAD) keeps the root path, so an old session's
    // best response still in flight would pass the path check — retire it
    this.exploit = null;
    this._exploitHands = null;
    this._exploitGen++;
    this.preflop = null; // build handler re-sets this after reset when applicable
    this.villainLocked = null; // player index whose postflop profile is locked in
    this.villainLockEvidence = null;
    this.lockHistory = null;   // server's lock undo/redo stacks (labels)
    this.lockLabels = [];      // a new session starts with no locks
    this.lockCells.clear();
    this.saveLockCells();
    this.pendingLockEdits = 0; // pending edits described the old session
    this._pendingBase = null;
    this.renderPendingBar();
  }

  /** Position label for player p: BB/BTN/… from the preflop study setup, else
   *  the generic OOP/IP. Used everywhere the two players are named. */
  posLabel(p) {
    if (this.preflop) return p === 0 ? this.preflop.oop : this.preflop.ip;
    return p === 0 ? 'OOP' : 'IP';
  }

  /** Take a step from node depth `d`: follow the line if it matches, else branch. */
  navigate(path) {
    this.path = path;
    this.refresh();
  }

  /** Move the view cursor to node `depth` along the line WITHOUT changing the line. */
  viewDepth(depth) {
    this.navigate(this.line.slice(0, depth));
  }

  renderHistory() {
    const el = this.els.history;
    if (!el) return;
    el.innerHTML = '';
    // Leading PREFLOP segments from the study setup (read-only — they describe
    // the line that produced this spot, not nodes in the solved postflop tree).
    if (this.preflop && this.preflop.segments) {
      for (const sg of this.preflop.segments) {
        const s = document.createElement('div');
        s.className = 'hist-seg hist-preflop';
        s.dataset.tip = 'Preflop action that produced this spot — not part of the solved postflop tree.';
        const h = document.createElement('div');
        h.className = 'hist-head';
        h.innerHTML = `<span>${sg.pos}</span>`;
        s.appendChild(h);
        const chip = document.createElement('div');
        chip.className = 'hist-chip taken';
        chip.textContent = sg.label;
        s.appendChild(chip);
        el.appendChild(s);
      }
    }
    // Render the FULL line (so past/future nodes stay visible); the cursor is
    // at depth = this.path.length. Viewing a node never truncates the line.
    const hist = this.lineHistory || this.view.history || [];
    const cursor = this.path.length;
    // what the freeze option would still hold: only dim when it would lock
    // something (freezeCount skips decisions that already carry a lock)
    const freezing = this.freezeLine && this.freezeCount() > 0;
    const STREETS = ['FLOP', 'TURN', 'RIVER'];

    const seg = (depth, cls = '') => {
      const d = document.createElement('div');
      d.className = `hist-seg ${cls}`;
      // clicking the segment body views that node (keeps the line intact)
      if (depth != null) {
        d.addEventListener('click', () => { if (depth !== cursor) this.viewDepth(depth); });
      }
      el.appendChild(d);
      return d;
    };
    const head = (parent, left, right, unit) => {
      const h = document.createElement('div');
      h.className = 'hist-head';
      h.innerHTML = `<span>${left}</span>${right != null ? `<b>${unit ? unit + ' ' : ''}${right}</b>` : ''}`;
      parent.appendChild(h);
      return h;
    };

    // Leading board segment: the initial street's cards + starting pot.
    const cardStepsViewed = (this.view.history || []).filter(h => h.kind === 'card' && h.card).length;
    const initLen = this.view.board.length - cardStepsViewed;
    const rootPot = hist.length ? hist[0].pot : this.view.pot;
    {
      const s = seg(null);
      s.classList.add('hist-board');
      head(s, STREETS[Math.max(0, initLen - 3)], fmt(rootPot), 'pot');
      const row = document.createElement('div');
      row.className = 'hist-cards';
      for (let k = 0; k < initLen; k++) {
        row.appendChild(cardChip(this.view.board[k], 'bcard mini'));
      }
      s.appendChild(row);
      s.addEventListener('click', () => { if (cursor !== 0) this.viewDepth(0); });
    }

    hist.forEach((h, i) => {
      const prefix = this.line.slice(0, i);
      const isCursor = i === cursor;
      if (h.kind === 'action') {
        const s = seg(i, isCursor ? 'current' : '');
        // what the freeze option would hold: dim the earlier decisions it locks
        if (freezing && i < cursor && this.view.node_type === 'action') {
          s.style.opacity = '.45';
        }
        head(s, this.posLabel(h.player), fmt(h.stack), 'stack');
        h.actions.forEach((a, k) => {
          const chip = document.createElement('button');
          chip.className = 'hist-chip' + (h.chosen === k ? ' taken' : '');
          chip.textContent = a.label;
          chip.dataset.tip = h.chosen === k
            ? ''
            : `Branch the line: take ${a.label.toLowerCase()} from here instead.`;
          chip.addEventListener('click', (e) => {
            e.stopPropagation();
            // taken action on a past node -> just view it (keep the line);
            // a different action (or any action at the frontier) -> branch/advance
            if (h.chosen === k) this.viewDepth(i);
            else this.navigate([...prefix, { type: 'action', index: k }]);
          });
          s.appendChild(chip);
        });
      } else if (h.kind === 'card') {
        const s = seg(i, isCursor ? 'current' : '');
        s.dataset.tip = 'Click to view this point; pick another card in the panel to change the runout.';
        head(s, STREETS[h.street], fmt(h.pot), 'pot');
        const row = document.createElement('div');
        row.className = 'hist-cards';
        row.appendChild(h.card ? cardChip(h.card, 'bcard mini') : facedownChip('bcard mini'));
        s.appendChild(row);
      } else {
        const s = seg(i, isCursor ? 'current dim' : 'dim');
        head(s, 'END', null);
        const lbl = document.createElement('div');
        lbl.className = 'hist-chip taken';
        // fold vs showdown: HistoryStep doesn't carry it, so look at the
        // action that led here
        const prev = hist[i - 1];
        const folded = prev && prev.kind === 'action'
          && prev.actions[prev.chosen]?.kind === 'fold';
        lbl.textContent = folded ? 'Fold — hand over' : 'Showdown';
        s.appendChild(lbl);
      }
    });

    // Trailing hint: next street still to come on the LINE's deepest node.
    const deep = hist[hist.length - 1];
    if (deep && deep.kind === 'action' && deep.street < 2) {
      const s = seg(null, 'dim');
      head(s, STREETS[deep.street + 1], null);
      const row = document.createElement('div');
      row.className = 'hist-cards';
      row.appendChild(facedownChip('bcard mini'));
      s.appendChild(row);
    }

    // keep the viewed node's segment in view, then refresh the scroll arrows
    const cur = el.querySelector('.hist-seg.current');
    if (cur) {
      const cr = cur.getBoundingClientRect(), er = el.getBoundingClientRect();
      if (cr.left < er.left) el.scrollLeft -= er.left - cr.left + 8;
      else if (cr.right > er.right) el.scrollLeft += cr.right - er.right + 8;
    }
    this.updateHistNav();
  }

  /** Show the ribbon scroll arrows only when (and on the side) it overflows. */
  updateHistNav() {
    const el = this.els.history;
    if (!el || !this.els.histLeft) return;
    const max = el.scrollWidth - el.clientWidth;
    const overflow = max > 2;
    this.els.histLeft.classList.toggle('hidden', !overflow || el.scrollLeft <= 1);
    this.els.histRight.classList.toggle('hidden', !overflow || el.scrollLeft >= max - 1);
  }

  // ----- actions panel -----

  renderActions() {
    const el = this.els.actionList;
    const picker = this.els.cardPicker;
    el.innerHTML = '';
    picker.classList.add('hidden');
    this.els.runouts && (this.els.runouts.innerHTML = '');
    this.runoutRep = null; // drop any prior runouts report when the node changes
    // BROWSE is reachable before any solve (and after a failed root fetch)
    if (!this.view) { this.els.actionsTitle.textContent = ''; return; }
    if (this.mode === 'exploit') this.renderExploitBanner(el);

    if (this.view.node_type === 'action') {
      const colors = this.actionColors();
      const actor = this.view.player;
      const hands = this.handsFor(actor);
      this.els.actionsTitle.textContent =
        `${this.posLabel(actor)} to act — street ${['flop','turn','river'][this.view.street]}`;
      // global frequencies: reach-weighted average strategy
      let totalReach = 0;
      const freqs = this.view.actions.map(() => 0);
      const evs = this.view.actions.map(() => ({ n: 0, d: 0 }));
      hands.forEach(h => {
        if (!h.strategy) return;
        totalReach += h.reach;
        // EVs weight by reach x valid (card-removal-adjusted opponent mass,
        // when the server provides it); frequencies stay pure reach
        const w = h.reach * (h.valid != null ? h.valid : 1);
        h.strategy.forEach((s, a) => {
          freqs[a] += s * h.reach;
          if (h.evs && h.evs[a] != null) { evs[a].n += h.evs[a] * w * s; evs[a].d += w * s; }
        });
      });
      // Action tiles. Navigation lives in the history ribbon;
      // clicking a tile filters the grid to that action's range instead.
      const tiles = document.createElement('div');
      tiles.className = 'act-tiles';
      this.view.actions.forEach((a, k) => {
        const freq = totalReach > 0 ? freqs[k] / totalReach : 0;
        const ev = evs[k].d > 1e-9 ? evs[k].n / evs[k].d : null;
        const sel = this.actionFilter === k;
        // a toggle button: the badge + aria-pressed say the grid is filtered
        const tile = document.createElement('button');
        tile.type = 'button';
        tile.className = 'act-tile' + (sel ? ' sel' : '');
        tile.setAttribute('aria-pressed', sel ? 'true' : 'false');
        tile.style.background = colors[k];
        tile.style.font = 'inherit';
        tile.style.textAlign = 'left';
        tile.dataset.tip = `${a.label}: avg EV ${ev != null ? fmt(ev) : '—'}. Click to filter the grid to this action.`;
        tile.innerHTML = `
          <div class="at-label">${a.label}</div>
          <div class="at-foot">
            <span class="at-pct">${(freq * 100).toFixed(1)}%</span>
            <span class="at-combos">${freqs[k].toFixed(1)}<small>combos</small></span>
          </div>` +
          (sel ? `<span class="at-badge" aria-hidden="true" style="position:absolute;top:4px;right:5px;` +
            `font:9px/1 var(--font-disp);letter-spacing:.08em;background:#fff;color:#111;` +
            `border-radius:2px;padding:2px 4px">filter</span>` : '');
        tile.addEventListener('click', () => {
          this.actionFilter = this.actionFilter === k ? null : k;
          this.renderActions();
          this.renderMatrix();
          this.renderLegend();
        });
        tiles.appendChild(tile);
      });
      el.appendChild(tiles);
      // overall split bar
      const sumbar = document.createElement('div');
      sumbar.className = 'act-sumbar';
      sumbar.innerHTML = this.view.actions.map((_, k) => {
        const freq = totalReach > 0 ? freqs[k] / totalReach : 0;
        return `<i style="width:${(freq * 100).toFixed(2)}%;background:${colors[k]}"></i>`;
      }).join('');
      el.appendChild(sumbar);
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
            // one pick per fetch: a second click mid-flight used to push a
            // second card step onto the SAME path array, the server rejected
            // the two-card path, and refresh()'s recovery dumped the user at
            // the root with the whole navigated line gone
            if (this._pickerBusy) return;
            this._pickerBusy = true;
            picker.querySelectorAll('button').forEach(x => { x.disabled = true; });
            this.path = this.path.concat([{ type: 'card', card: cs }]); // copy-on-write
            this.pathLabels = this.pathLabels.concat([cs]);
            Promise.resolve(this.refresh()).finally(() => { this._pickerBusy = false; });
          });
          picker.appendChild(b);
        }
      }
      // runouts report
      const btn = document.createElement('button');
      btn.className = 'btn';
      btn.style.marginTop = '12px';
      btn.textContent = 'RUNOUTS REPORT';
      btn.dataset.tip = 'Strategy and equity for every possible next card.';
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
    const p = this.view.player;
    const acts = this.view.actions;
    const hands = this.view.players[p].hands;
    const locked = this.view.locked;
    const label = this.lockNodeLabel();
    const summary = this.lockSummaryText(label);
    if (this.lockMode !== 'hands') this.lockMode = 'range';

    // current reach-weighted aggregate frequency per action
    let tot = 0;
    const agg = acts.map(() => 0);
    hands.forEach(h => {
      if (!h.strategy) return;
      tot += h.reach;
      h.strategy.forEach((s, k) => agg[k] += s * h.reach);
    });
    const curFreq = agg.map(x => tot > 1e-9 ? x / tot : 0);

    const wrap = document.createElement('div');
    wrap.className = 'lock-panel';
    wrap.innerHTML = `
      <div class="lock-head">NODE LOCKING <button type="button" class="info-dot" aria-label="How node locking works" data-tip="Pins this node's strategy until you unlock it. Covers all suit-equivalent runouts; re-locking replaces the previous lock.">?</button>${summary ? ` <span class="lock-badge" data-lock-summary>${summary}</span>` : ''}${this.view.fit ? ' <span class="lock-badge">FITTING</span>' : ''}<span class="lock-history"></span>${locked ? '<button type="button" class="btn ghost xs lock-unlock" data-tip="clears this node\'s lock">unlock all</button>' : ''}</div>
      <div class="lock-modes seg">
        <button data-lm="range" class="${this.lockMode === 'range' ? 'active' : ''}"
          data-tip="Model a whole-range read: 'folds 70% to this bet'. Each hand's mix is scaled proportionally, so the right hands do the extra folding or calling.">Overall %</button>
        <button data-lm="hands" class="${this.lockMode === 'hands' ? 'active' : ''}"
          data-tip="Set exact action frequencies for one hand class (click a cell to pin it); other hands keep their current strategy.">Per hand</button>
      </div>
      <div class="lock-body"></div>`;
    const body = wrap.querySelector('.lock-body');
    this.paintLockHistory(wrap.querySelector('.lock-history'));
    wrap.querySelectorAll('.lock-modes button').forEach(b =>
      b.addEventListener('click', () => { this.lockMode = b.dataset.lm; this.renderActions(); }));
    wrap.querySelector('.lock-unlock')?.addEventListener('click', async () => {
      try {
        const out = await api.unlock(this.path);
        this.setLockHistory(out.history);
        this.forgetLockCells(label);
        this.noteLockEdit();
        toast('unlocked');
        this.refresh();
      } catch (e) { this.fail(e); }
    });

    // a per-action [ %] editor with a live total + normalize button
    const freqEditor = (init) => {
      const cont = document.createElement('div');
      cont.className = 'lk-actions';
      const inputs = [];
      const pcts = pctShares(init); // integers summing to exactly 100
      acts.forEach((a, k) => {
        const row = document.createElement('label');
        row.className = 'lk-act';
        row.innerHTML = `<i class="lk-sw" style="background:${colors[k]}"></i><span class="lk-lab">${a.label}</span>`;
        const inp = document.createElement('input');
        inp.type = 'number'; inp.min = '0'; inp.max = '100'; inp.step = '1';
        inp.value = `${pcts[k]}`;
        inp.className = 'lk-pct';
        const unit = document.createElement('span'); unit.className = 'lk-unit'; unit.textContent = '%';
        row.appendChild(inp); row.appendChild(unit);
        cont.appendChild(row);
        inputs.push(inp);
      });
      const sumRow = document.createElement('div');
      sumRow.className = 'lk-sumrow';
      const sumEl = document.createElement('span'); sumEl.className = 'lk-sum';
      const norm = document.createElement('button'); norm.className = 'btn ghost xs'; norm.textContent = 'normalize';
      const update = () => {
        const s = inputs.reduce((a, i) => a + (+i.value || 0), 0);
        sumEl.textContent = `total ${Math.round(s)}%`;
        sumEl.classList.toggle('bad', Math.abs(s - 100) > 0.5);
      };
      norm.addEventListener('click', () => {
        const s = inputs.reduce((a, i) => a + (+i.value || 0), 0);
        if (s > 0) {
          const np = pctShares(inputs.map(i => +i.value || 0));
          inputs.forEach((inp, k) => { inp.value = `${np[k]}`; });
        }
        update();
      });
      inputs.forEach(i => i.addEventListener('input', update));
      update();
      sumRow.appendChild(sumEl); sumRow.appendChild(norm);
      return { cont, inputs, sumRow };
    };

    if (this.lockMode === 'range') {
      if (tot <= 1e-9) {
        // no reach: any prefill would be a uniform guess, not "the solution"
        const help = document.createElement('div'); help.className = 'lk-help';
        help.textContent = 'no hands reach this node';
        const foot = document.createElement('div'); foot.className = 'btn-row';
        this.appendLockFooter(foot, label);
        body.append(help, foot);
        el.appendChild(wrap);
        return;
      }
      const help = document.createElement('div');
      help.className = 'lk-help';
      help.innerHTML = 'Set how often the <b>whole range</b> takes each action. ' +
        'The pre-filled values are the current solution.';
      const ed = freqEditor(curFreq);
      body.append(help, ed.cont, ed.sumRow);
      const fit = this.view.fit;
      if (fit) {
        // a least-exploitable fit is steering this node in the solve
        const st = document.createElement('div');
        st.className = 'lk-help lk-fit';
        const pct = v => Number.isFinite(v) ? `${(v * 100).toFixed(1)}%` : '\u2014';
        st.innerHTML = '<b>Least-exploitable fit running.</b> ' + acts.map((a, k) =>
          `${a.label} ${pct(fit.achieved[k])} \u2192 ${pct(fit.target[k])}`).join(' \u00b7 ') +
          '. Locked when the solve ends; one undo removes it.';
        body.appendChild(st);
      }
      const methods = [
        ['rake', 'Scale', 'Scale every hand\u2019s mix by the same factor until the range hits your numbers. Hands that never take an action can\u2019t be scaled in.'],
        ['quick', 'Least EV loss', 'Move the hands that lose the least EV by switching, given how both players play now. Instant, only this node changes, and a best response can still punish it.'],
        ['full', 'Least exploitable', 'Find the play for the whole tree that hits your numbers while giving away the least to a best response. Starts a RE-SOLVE; the result is locked when it ends.'],
      ];
      if (!methods.some(m => m[0] === this.fitMethod)) {
        let saved = null;
        try { saved = localStorage.getItem('gtopen.fitMethod'); } catch { /* storage off */ }
        this.fitMethod = methods.some(m => m[0] === saved) ? saved : 'rake';
      }
      const seg = document.createElement('div');
      seg.className = 'seg lk-method';
      for (const [key, name, tip] of methods) {
        const b = document.createElement('button');
        b.type = 'button';
        b.textContent = name;
        b.dataset.tip = tip;
        b.className = this.fitMethod === key ? 'active' : '';
        b.addEventListener('click', () => {
          this.fitMethod = key;
          try { localStorage.setItem('gtopen.fitMethod', key); } catch { /* storage off */ }
          this.renderActions();
        });
        seg.appendChild(b);
      }
      body.appendChild(seg);
      const foot = document.createElement('div'); foot.className = 'btn-row';
      const lock = document.createElement('button'); lock.className = 'btn';
      lock.textContent = this.fitMethod === 'full' ? 'FIT + RE-SOLVE' : 'LOCK FREQUENCIES';
      lock.dataset.tip = methods.find(m => m[0] === this.fitMethod)[2];
      lock.addEventListener('click', async () => {
        const freqs = ed.inputs.map(i => Math.max(0, +i.value || 0));
        if (freqs.reduce((a, b) => a + b, 0) <= 0) return toast('set at least one action above 0%', true);
        try {
          if (this.fitMethod === 'full') {
            const out = await api.fit(this.path, freqs, label, this.freezeLine && this.freezeCount() > 0);
            this.forgetLockCells(label); // a tree fit replaces per-hand marks
            this.setLockHistory(out.history); this.noteLockEdit();
            toast(`least-exploitable fit set${frozenNote(out)} — solving; locks when the solve ends`);
            document.getElementById('btn-solve-top')?.click();
          } else {
            const out = await this.lockHere({ kind: this.fitMethod === 'quick' ? 'fit' : 'range', freqs }, label);
            toast(`locked${frozenNote(out)}`);
          }
          this.refresh();
        } catch (e) { this.fail(e); }
      });
      foot.appendChild(lock);
      if (fit) {
        const cancel = document.createElement('button'); cancel.className = 'btn ghost'; cancel.textContent = 'CANCEL FIT';
        cancel.dataset.tip = 'Stop steering this node; nothing is locked.';
        cancel.addEventListener('click', async () => {
          try { await api.fitCancel(this.path); toast('fit cancelled'); this.refresh(); }
          catch (e) { this.fail(e); }
        });
        foot.appendChild(cancel);
      }
      this.appendLockFooter(foot, label);
      body.appendChild(foot);
    } else {
      const sel = this.selectedCell;
      const foot = document.createElement('div'); foot.className = 'btn-row';
      if (!sel) {
        const help = document.createElement('div'); help.className = 'lk-help';
        help.textContent = 'Click a hand in the matrix to pin it, then set its exact frequencies here.';
        body.appendChild(help);
      } else {
        const info = cellInfo(sel[0], sel[1]);
        let ct = 0; const cagg = acts.map(() => 0); const combos = [];
        for (const [a, b] of cellCombos(info)) {
          const hi = this.handIdx[p].get(comboIndex(a, b));
          if (hi === undefined) continue;
          combos.push(cardToString(a) + cardToString(b));
          const h = hands[hi];
          if (h.strategy) { ct += h.reach; h.strategy.forEach((s, k) => cagg[k] += s * h.reach); }
        }
        if (!combos.length) {
          body.innerHTML = `<div class="lk-help">${info.label} is not in ${this.posLabel(p)}'s range here.</div>`;
        } else if (ct <= 1e-9) {
          // combos exist but nothing reaches: a uniform 1/na prefill would be
          // a fabricated "current solution", so refuse the edit instead
          body.innerHTML = `<div class="lk-help">${info.label} — this hand no longer reaches this node.</div>`;
        } else {
          const cur = cagg.map(x => x / ct);
          const help = document.createElement('div'); help.className = 'lk-help';
          help.innerHTML = `Set exact frequencies for <b style="color:var(--ink)">${info.label}</b> (${combos.length} combo${combos.length > 1 ? 's' : ''}).`;
          const ed = freqEditor(cur);
          body.append(help, ed.cont, ed.sumRow);
          const lock = document.createElement('button'); lock.className = 'btn'; lock.textContent = `LOCK ${info.label}`;
          lock.addEventListener('click', async () => {
            const freqs = ed.inputs.map(i => Math.max(0, +i.value || 0));
            if (freqs.reduce((a, b) => a + b, 0) <= 0) return toast('set at least one action above 0%', true);
            const edits = combos.map(c => ({ combo: c, freqs }));
            try {
              const out = await this.lockHere({ kind: 'hands', edits }, label);
              this.rememberLockedCell(sel, label);
              toast(`${info.label} locked${frozenNote(out)}`); this.refresh();
            } catch (e) { this.fail(e); }
          });
          foot.appendChild(lock);
        }
      }
      this.appendLockFooter(foot, label);
      body.appendChild(foot);
    }
    el.appendChild(wrap);
  }

  /** Lock the current node with `mode`, freezing the earlier decisions on
   *  the line too when that option is on. Returns the server's reply. */
  async lockHere(mode, label) {
    const out = await api.lock(this.path, mode, label, this.freezeLine && this.freezeCount() > 0);
    // a whole-range/solved lock recomputes every hand: drop per-cell marks
    if (mode.kind !== 'hands') this.forgetLockCells(label);
    this.setLockHistory(out.history); this.noteLockEdit();
    return out;
  }

  /** True when the current node has a decision before it on the line. */
  hasEarlierDecision() {
    return this.path.some(step => step.type === 'action');
  }

  /** Earlier decisions a freeze-earlier lock would still freeze: action steps
   *  on the line whose node (the prefix BEFORE the step, as freeze_line walks
   *  it) carries no lock yet. */
  freezeCount() {
    if (!this.view || !this.pathLabels || !this.hasEarlierDecision()) return 0;
    return freezeableAncestors(this.path, this.pathLabels, this.rootBoard(), d => !!this.lockSummary(d));
  }

  setLockHistory(h) {
    if (!h) return;
    this.lockHistory = h;
    this.paintLockHistory(this.els.actionList?.querySelector('.lock-history'));
    this.paintLockBadge(); // composition may include a range base from the history
  }

  /** Undo / redo buttons in the lock panel head, labelled with the edit
   *  each one would step over. */
  paintLockHistory(el) {
    if (!el) return;
    const h = this.lockHistory || { undo: [], redo: [] };
    el.innerHTML = '';
    for (const [dir, glyph, word, list] of [['undo', '\u21b6', 'Undo', h.undo], ['redo', '\u21b7', 'Redo', h.redo]]) {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'btn ghost xs lock-step';
      b.textContent = `${glyph} ${word}`;
      b.disabled = !list.length || !!this.lockStepBusy;
      const key = dir === 'undo' ? 'Ctrl+Z' : 'Ctrl+Shift+Z';
      b.setAttribute('aria-label', list.length ? `${word}: ${list[0]}` : `Nothing to ${word.toLowerCase()}`);
      b.dataset.tip = list.length
        ? `${word}: ${list[0]} (${key}).` + (list.length > 1 ? ` ${list.length - 1} more step${list.length > 2 ? 's' : ''} after this.` : '')
        : `Nothing to ${word.toLowerCase()}.`;
      b.addEventListener('click', e => { e.stopPropagation(); this.stepLockHistory(dir); });
      el.appendChild(b);
    }
  }

  async stepLockHistory(dir) {
    const list = this.lockHistory?.[dir];
    if (this.lockStepBusy || !list?.length) return;
    this.lockStepBusy = true;
    this.setLockHistory(this.lockHistory);
    try {
      const out = await (dir === 'undo' ? api.lockUndo() : api.lockRedo());
      this.lockStepBusy = false;
      this.setLockHistory(out.history); this.noteLockEdit();
      this.lockCells.clear(); // an undo/redo changes the per-hand composition
      this.saveLockCells();
      this.syncVillainLocked(out.history);
      if (out.label) toast(`${dir === 'undo' ? 'undid' : 'redid'}: ${out.label}`);
      await this.refresh();
    } catch (e) {
      this.fail(e);
      // a refused step clears the server's history: show what is left
      api.lockHistory().then(h => this.setLockHistory(h)).catch(() => {});
    } finally {
      this.lockStepBusy = false;
      this.renderVillainLocks();
    }
  }

  /** Undo/redo can add or remove a villain's profile locks: keep the
   *  villain-lock toggle in step with what the server holds. */
  syncVillainLocked(h) {
    const players = h?.profile_players || [];
    if (this.villainLocked !== null && !players.includes(this.villainLocked)) {
      this.villainLocked = null;
      this.villainLockEvidence = null;
    } else if (this.villainLocked === null && players.length) {
      this.villainLocked = players[0];
      this.villainLockEvidence = null;
    }
  }

  /** Shared "lock as solved" + "freeze earlier" controls for the lock panel. */
  appendLockFooter(foot, label) {
    const freezeN = this.freezeCount();
    if (freezeN > 0) {
      const line = document.createElement('label');
      line.className = 'chk lk-line';
      line.dataset.tip = 'also freeze every earlier decision on this line';
      const box = document.createElement('input');
      box.type = 'checkbox';
      box.checked = !!this.freezeLine;
      box.addEventListener('change', () => {
        this.freezeLine = box.checked;
        try { localStorage.setItem('gtopen.freezeLine', box.checked ? '1' : '0'); } catch { /* storage off */ }
        this.renderHistory(); // dim the ribbon segments a lock would freeze
      });
      line.append(box, document.createTextNode(
        ` freeze ${freezeN} earlier decision${freezeN === 1 ? '' : 's'}`));
      foot.prepend(line);
    }
    const freeze = document.createElement('button');
    freeze.className = 'btn ghost'; freeze.textContent = 'LOCK AS SOLVED';
    freeze.dataset.tip = 'Freeze this node exactly as currently solved \u2014 it stops adapting while you experiment elsewhere. (LOCK FREQUENCIES pins your numbers; LOCK AS SOLVED pins the solver\u2019s.)';
    freeze.addEventListener('click', async () => {
      try { const out = await this.lockHere({ kind: 'freeze' }, label); toast(`locked as solved${frozenNote(out)}`); this.refresh(); }
      catch (e) { this.fail(e); }
    });
    foot.appendChild(freeze);
  }

  async loadRunouts(btn) {
    btn.disabled = true; btn.textContent = 'computing…';
    const forPath = JSON.stringify(this.path); // guard against navigating away mid-compute
    let rep;
    try { rep = await api.runouts(this.path); }
    catch (e) { this.fail(e); btn.disabled = false; btn.textContent = 'RUNOUTS REPORT'; return; }
    btn.disabled = false; btn.textContent = 'RUNOUTS REPORT';
    if (JSON.stringify(this.path) !== forPath) return; // stale: user moved on
    this.runoutRep = rep;
    this.runoutSort = { col: 'card', dir: -1 }; // default: high card -> low
    this.renderRunouts();
  }

  renderRunouts() {
    const rep = this.runoutRep;
    const el = this.els.runouts;
    if (!el) return;
    // keep keyboard focus on the sort column across the rebuild
    const focusSort = document.activeElement?.classList?.contains('ro-sort')
      ? document.activeElement.dataset.sort : null;
    el.innerHTML = '';
    if (!rep) return;
    if (!this.runoutMetric) this.runoutMetric = 'eq';
    if (!this.runoutTex) this.runoutTex = 'all';
    const colors = computeActionColors(rep.actions, this.view ? this.view.pot : 0);
    // aggression = combined bet/raise frequency; the natural "strategy" sort key
    const aggrIdx = rep.actions
      .map((a, k) => (a.kind === 'bet' || a.kind === 'raise') ? k : -1).filter(k => k >= 0);
    const stratVal = row => {
      if (!row.freqs || !row.freqs.length) return null;          // all-in runout, no action
      if (aggrIdx.length) return aggrIdx.reduce((s, k) => s + (row.freqs[k] || 0), 0);
      return 1 - (row.freqs[0] || 0);                            // fallback: non-first action share
    };
    const metric = this.runoutMetric;
    const eqr = (row, p) =>
      row.ev && row.ev[p] != null && row.eq[p] != null && row.eq[p] > 0.02 && rep.pot > 0
        ? row.ev[p] / (rep.pot * row.eq[p]) : null;
    const mval = (row, p) =>
      metric === 'eq' ? (row.eq[p] != null ? row.eq[p] : null) :
      metric === 'ev' ? (row.ev && row.ev[p] != null ? row.ev[p] : null) :
      eqr(row, p);
    const mfmt = v =>
      v == null ? '—' :
      metric === 'eq' ? (v * 100).toFixed(1) :
      metric === 'ev' ? fmt(v) : v.toFixed(2);

    // card textures vs the current board
    const board = (this.view && this.view.board) || [];
    const bRanks = board.map(c => RANKS.indexOf(c[0]));
    const bSuits = board.map(c => c[1]);
    const bMax = Math.max(...bRanks);
    const texOf = card => {
      const r = RANKS.indexOf(card[0]);
      const flushy = bSuits.filter(x => x === card[1]).length >= 2;
      const paired = bRanks.includes(r);
      const over = r > bMax;
      const straighty = bRanks.filter(x => x !== r && Math.abs(x - r) <= 3).length >= 2;
      return { all: true, flushy, paired, over, straighty,
        brick: !flushy && !paired && !over && !straighty };
    };
    const TEX = [
      ['all', 'ALL', ''],
      ['flushy', 'FLUSH', 'Cards bringing a third (or fourth) card of a suit.'],
      ['paired', 'PAIRS', ''],
      ['straighty', 'STRAIGHTY', 'Cards within 3 ranks of two or more board cards.'],
      ['over', 'OVER', 'Overcards to the board.'],
      ['brick', 'BRICK', 'None of the above.'],
    ];

    const valOf = (row, col) =>
      col === 'card' ? RANKS.indexOf(row.card[0]) * 4 + SUITS.indexOf(row.card[1]) :
      col === 'strat' ? stratVal(row) :
      col === 'oop' ? mval(row, 0) : mval(row, 1);

    const { col: sortCol, dir: sortDir } = this.runoutSort;
    const rows = rep.rows.filter(r => texOf(r.card)[this.runoutTex]).sort((a, b) => {
      const av = valOf(a, sortCol), bv = valOf(b, sortCol);
      if (av == null && bv == null) return 0;
      if (av == null) return 1;                                  // nulls always last
      if (bv == null) return -1;
      return sortDir === -1 ? bv - av : av - bv;
    });

    // metric + texture controls
    const bar = document.createElement('div');
    bar.className = 'ro-controls';
    const MET = [
      ['eq', 'EQ', ''],
      ['ev', 'EV', 'Average EV on each runout (pot-share: EV OOP + EV IP = pot).'],
      ['eqr', 'EQR', 'Equity realization = EV / (pot \u00d7 equity). 1.00 = exactly your equity share; above 1 over-realizes, below under-realizes.'],
    ];
    bar.innerHTML =
      `<div class="seg">${MET.map(([k, l, t]) =>
        `<button data-m="${k}" class="${k === metric ? 'active' : ''}" data-tip="${t}">${l}</button>`).join('')}</div>` +
      `<div class="seg">${TEX.map(([k, l, t]) =>
        `<button data-t="${k}" class="${k === this.runoutTex ? 'active' : ''}" data-tip="${t}">${l}</button>`).join('')}</div>`;
    el.appendChild(bar);
    bar.querySelectorAll('button[data-m]').forEach(b =>
      b.addEventListener('click', () => { this.runoutMetric = b.dataset.m; this.renderRunouts(); }));
    bar.querySelectorAll('button[data-t]').forEach(b =>
      b.addEventListener('click', () => { this.runoutTex = b.dataset.t; this.renderRunouts(); }));

    const arrow = key => key === sortCol ? (sortDir === -1 ? ' ▼' : ' ▲') : '';
    const cls = key => `ro-sort${key === sortCol ? ' sorted' : ''}`;
    const ariaSort = key => key === sortCol ? (sortDir === -1 ? 'descending' : 'ascending') : 'none';
    // real buttons (role=columnheader carries aria-sort); one shared hint below
    const sortBtn = (clsName, key, label, style = '') =>
      `<button type="button" role="columnheader" aria-sort="${ariaSort(key)}" ` +
      `class="${clsName} ${cls(key)}" data-sort="${key}" ` +
      `style="background:none;border:0;font:inherit;color:inherit;padding:0;text-align:inherit;cursor:pointer;${style}">` +
      `${label}${arrow(key)}</button>`;
    const stratLabel = rep.player != null ? this.posLabel(rep.player) + ' strategy' : 'strategy';
    const mname = metric.toUpperCase();
    const hint = document.createElement('div');
    hint.className = 'dim';
    hint.style.cssText = 'font-size:10px;margin:2px 0 5px';
    hint.textContent = 'click a column to sort';
    el.appendChild(hint);
    const head = document.createElement('div');
    head.className = 'combo-row head';
    head.innerHTML =
      sortBtn('cname', 'card', 'card') +
      sortBtn('cbar', 'strat', stratLabel, 'height:auto;display:block') +
      sortBtn('cnum', 'oop', `OOP ${mname}`, 'text-align:right') +
      sortBtn('cnum', 'ip', `IP ${mname}`, 'text-align:right');
    el.appendChild(head);

    // aggregate over the visible (filtered) cards, equal weight per card
    if (rows.length) {
      const mean = xs => {
        const v = xs.filter(x => x != null);
        return v.length ? v.reduce((a, b) => a + b, 0) / v.length : null;
      };
      const withAct = rows.filter(r => r.freqs && r.freqs.length);
      const aggBar = rep.actions.map((a, k) => {
        const f = mean(withAct.map(r => r.freqs[k] || 0)) || 0;
        return `<div style="width:${(f * 100).toFixed(1)}%;background:${colors[k]}" data-tip="${a.label}: ${(f * 100).toFixed(1)}% averaged over ${withAct.length} cards"></div>`;
      }).join('');
      const agg = document.createElement('div');
      agg.className = 'combo-row ro-agg';
      agg.innerHTML =
        `<span class="cname" data-tip="Equal-weight average over the ${rows.length} cards shown.">avg·${rows.length}</span>` +
        `<span class="cbar">${aggBar}</span>` +
        `<span class="cnum">${mfmt(mean(rows.map(r => mval(r, 0))))}</span>` +
        `<span class="cnum">${mfmt(mean(rows.map(r => mval(r, 1))))}</span>`;
      el.appendChild(agg);
    }

    for (const row of rows) {
      const r = document.createElement('div');
      r.className = 'combo-row';
      const name = `<span class="suit-${row.card[1]}">${row.card[0]}${SUIT_GLYPH[row.card[1]]}</span>`;
      const rbar = row.freqs.map((f, k) =>
        `<div style="width:${(f * 100).toFixed(1)}%;background:${colors[k]}" data-tip="${rep.actions[k].label}: ${(f * 100).toFixed(1)}% of range"></div>`).join('');
      r.innerHTML = `<span class="cname">${name}</span><span class="cbar">${rbar}</span>
        <span class="cnum">${mfmt(mval(row, 0))}</span>
        <span class="cnum">${mfmt(mval(row, 1))}</span>`;
      el.appendChild(r);
    }
    // legend
    const leg = document.createElement('div');
    leg.className = 'legend';
    rep.actions.forEach((a, k) => {
      leg.innerHTML += `<span class="key"><i style="background:${colors[k]}"></i>${a.label}</span>`;
    });
    el.appendChild(leg);

    head.querySelectorAll('.ro-sort').forEach(h =>
      h.addEventListener('click', () => {
        const col = h.dataset.sort;
        if (this.runoutSort.col === col) this.runoutSort.dir *= -1; // same column: flip
        else this.runoutSort = { col, dir: -1 };                    // new column: desc first
        this.renderRunouts();
      }));
    if (focusSort != null) {
      el.querySelector(`.ro-sort[data-sort="${focusSort}"]`)?.focus();
    }
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

  // ----- Exploit (max-exploit / best-response) mode -----

  exploitReady() {
    return !!(this.exploit && this.exploit.exploiter === this.player
      && this.exploit._path === JSON.stringify(this.path));
  }

  /** Effective render mode: in EXPLOIT, strategy-style cells when the
   *  exploiter acts here, else an EV-style heatmap of the per-hand gain. */
  effMode() {
    if (this.mode !== 'exploit') return this.mode;
    return this.exploitReady() && this.exploit.player === this.exploit.exploiter
      ? 'strategy' : 'ev';
  }

  /** Hand array driving the matrix: the exploit overlay (strategy = BR
   *  actions, ev = gain vs current) when active, else the solver view. */
  handsFor(p) {
    if (this.mode === 'exploit' && this.exploitReady() && p === this.player) {
      if (!this._exploitHands) {
        this._exploitHands = this.exploit.hands.map(h => ({
          ...h,
          strategy: h.br_strategy || null,
          ev: h.gain != null ? h.gain : null,
          eq: null,
          evs: h.evs || null,
        }));
      }
      return this._exploitHands;
    }
    return this.view.players[p].hands;
  }

  async loadExploit() {
    if (this._exploitLoading) return;
    this._exploitLoading = true;
    const forPath = JSON.stringify(this.path), forPlayer = this.player;
    // Generation guard: path/player alone can't tell a stale response apart
    // when the STRATEGY changed under the same path (a lock, a re-solve, or a
    // session swap that lands on the same root) — refresh()/reset() bump the
    // generation and the old best response is discarded instead of installed
    // over the new state (where its hands wouldn't even index the new tree).
    const gen = this._exploitGen;
    let stale = false;
    try {
      const ex = await api.exploit(this.path, this.player);
      if (gen === this._exploitGen && JSON.stringify(this.path) === forPath
          && this.player === forPlayer && this.mode === 'exploit') {
        ex._path = forPath;
        this.exploit = ex;
        this._exploitHands = null;
        this.renderActions();
        this.renderMatrix();
        this.renderLegend();
      } else {
        stale = true; // user navigated / toggled player / left exploit mid-flight
      }
    } catch (e) {
      this.fail(e);
      this.els.matrix.style.opacity = ''; // un-dim; grid keeps its last paint
    }
    finally { this._exploitLoading = false; }
    // A discarded stale response leaves no request outstanding (the concurrent
    // renderMatrix call early-returned on _exploitLoading), so re-issue for the
    // CURRENT path/player — otherwise the view wedges on the 'computing…'
    // banner with the previous node's dimmed grid until some other interaction.
    if (stale && this.mode === 'exploit' && !this.exploitReady()) this.loadExploit();
  }

  renderExploitBanner(el) {
    const b = document.createElement('div');
    b.className = 'exploit-banner';
    if (!this.exploitReady()) {
      b.innerHTML = `<b>EXPLOIT</b> computing best response for ${this.posLabel(this.player)}…`;
    } else {
      const e = this.exploit;
      const nm = this.posLabel(e.exploiter);
      b.innerHTML = e.avg_gain != null
        ? `<b>EXPLOIT</b> ${nm} best response vs current strategy: EV ` +
          `<b>${fmt(e.avg_br_ev)}</b> vs ${fmt(e.avg_cur_ev)} → gains ` +
          `<b>${fmt(e.avg_gain)}</b> chips/hand (reach-weighted)` +
          (e.locked ? ' · this node is locked: BR cannot deviate here' : '')
        : `<b>EXPLOIT</b> ${nm} has no reachable hands at this node.`;
    }
    el.appendChild(b);
  }

  /** Per-combo data for a cell (present + filter-matching, with reach): for the
   *  per-combo EV/EQ columns. */
  cellCombosData(i, j, p) {
    const idx = this.handIdx[p];
    const hands = this.handsFor(p);
    const out = [];
    for (const [a, b] of cellCombos(cellInfo(i, j))) {
      const hi = idx.get(comboIndex(a, b));
      if (hi === undefined || !this.handMatches(p, hi)) continue;
      const h = hands[hi];
      if (h.reach <= 1e-9) continue;
      out.push({ reach: h.reach, ev: h.ev, eq: h.eq, strat: h.strategy,
                 combo: cardToString(a) + cardToString(b) });
    }
    return out;
  }

  cellAgg(i, j, p) {
    // Aggregate hands of player p within a cell class.
    const combos = cellCombos(cellInfo(i, j));
    const hands = this.handsFor(p);
    const idx = this.handIdx[p];
    let reach = 0, weight = 0, ev = 0, evW = 0, eq = 0, eqW = 0;
    let strat = null, na = 0;
    if (this.view.node_type === 'action' && this.view.player === p) {
      na = this.view.actions.length;
      strat = new Array(na).fill(0);
    }
    let present = 0, possible = 0;
    for (const [a, b] of combos) {
      // height is normalized over combos the board actually allows, not the
      // theoretical 4/6/12 (a board card removes that suit's combo)
      if (this.boardSet && (this.boardSet.has(a) || this.boardSet.has(b))) continue;
      possible++;
      const hi = idx.get(comboIndex(a, b));
      if (hi === undefined) continue;
      if (!this.handMatches(p, hi)) continue;
      const h = hands[hi];
      present++;
      reach += h.reach;
      weight += h.weight;
      // EV/EQ averages weight by reach x valid (card-removal-adjusted opponent
      // mass, when the server provides it) so aggregates respect blockers
      const w = h.reach * (h.valid != null ? h.valid : 1);
      if (h.ev != null) { ev += h.ev * w; evW += w; }
      if (h.eq != null) { eq += h.eq * w; eqW += w; }
      if (strat && h.strategy) h.strategy.forEach((s, k) => strat[k] += s * h.reach);
    }
    if (strat && reach > 1e-12) strat = strat.map(s => s / reach);
    return { present, total: possible, reach, weight,
             ev: evW > 1e-12 ? ev / evW : null,
             eq: eqW > 1e-12 ? eq / eqW : null, strat };
  }

  renderMatrix() {
    if (!this.view) { this.renderEmptyState(); return; } // no spot yet: the tab says so
    const p = this.player;
    const colors = this.actionColors();
    if (this.mode === 'exploit' && !this.exploitReady()) {
      // Don't paint a misleading frame of non-exploit colors while the BR
      // data loads — keep the previous grid, dimmed; loadExploit re-renders.
      this.loadExploit();
      this.els.matrix.style.opacity = '.45';
      return;
    }
    this.els.matrix.style.opacity = '';
    const effMode = this.effMode();
    const hands = this.handsFor(p);
    const aggs = [];
    for (let i = 0; i < 13; i++)
      for (let j = 0; j < 13; j++) aggs.push(this.cellAgg(i, j, p));
    // lock coverage for this node, painted as a corner dot per cell
    const lockAt = this.lockNodeLabel();
    const lockState = this.lockSummary(lockAt);
    const lockedCells = this.lockedCellsAt(lockAt);
    const wholeLocked = !!lockState && lockState.kind !== 'hands';
    // Normalize fill height to the busiest hand class in the FULL (unfiltered)
    // range, so applying a filter just blanks non-matching cells instead of
    // rescaling the height of the ones that remain.
    let maxReach = 1e-12;
    for (let i = 0; i < 13; i++) {
      for (let j = 0; j < 13; j++) {
        const combos = cellCombos(cellInfo(i, j));
        let r = 0, poss = 0;
        for (const [a, b] of combos) {
          if (this.boardSet && (this.boardSet.has(a) || this.boardSet.has(b))) continue;
          poss++;
          const hi = this.handIdx[p].get(comboIndex(a, b));
          if (hi !== undefined) r += hands[hi].reach;
        }
        maxReach = Math.max(maxReach, r / Math.max(poss, 1));
      }
    }
    // Fill mode: how much of a cell/column to fill for a given per-combo reach.
    //  normalized -> relative to the busiest hand class (best use of space)
    //  range      -> the hand's actual weight/reach out of a full combo
    //  full       -> fill completely (ignore reach), just show the colors
    const fillMode = this.fillMode || 'normalized';
    const fillH = (perCombo) => {
      if (perCombo <= 1e-9) return 0;
      if (fillMode === 'full') return 1;
      if (fillMode === 'range') return Math.min(1, perCombo);
      return Math.min(1, perCombo / maxReach);
    };
    // EV colour ramp range across the displayed (filtered) combos
    let evMin = Infinity, evMax = -Infinity;
    if (effMode === 'ev') {
      this.handsFor(p).forEach((h, hi) => {
        if (h.reach > 1e-9 && h.ev != null && this.handMatches(p, hi)) {
          if (h.ev < evMin) evMin = h.ev;
          if (h.ev > evMax) evMax = h.ev;
        }
      });
    }
    const evSpan = evMax - evMin;
    const evColor = (ev) => {
      const t = evSpan > 1e-6 ? Math.max(0, Math.min(1, (ev - evMin) / evSpan)) : 0.5;
      return `hsl(${(t * 130).toFixed(0)} 70% 50%)`;
    };
    const eqColor = (eq) => `hsl(${(eq * 130).toFixed(0)} 75% 52%)`;
    // render each combo as its own bottom-anchored vertical column
    const renderCols = (bars, fill, sub, list, colorFn, aggText) => {
      fill.style.opacity = 0;
      if (!list.length) { bars.style.opacity = 0; sub.textContent = ''; return; }
      bars.style.opacity = 1;
      bars.style.height = '100%';
      bars.style.alignItems = 'flex-end';
      const w = (100 / list.length).toFixed(3);
      bars.innerHTML = list.map(c =>
        `<div data-combo="${c.combo}" style="width:${w}%;height:${(fillH(c.reach) * 100).toFixed(1)}%;background:${colorFn(c)}"></div>`
      ).join('');
      sub.textContent = aggText;
    };
    // combined (Horizontal) value cell: one bottom-anchored bar coloured by the
    // cell's aggregate EV/EQ, height = how much of the cell reaches the node
    // (mirrors the STRAT combined bar via the same `intensity`).
    const renderAgg = (bars, fill, sub, color, intensity, aggText, reach) => {
      bars.style.opacity = 0;
      const show = color != null && reach > 1e-9;
      fill.style.height = `${(intensity * 100).toFixed(1)}%`;
      fill.style.background = color || 'transparent';
      fill.style.opacity = show ? 1 : 0;
      sub.textContent = aggText;
    };
    for (let i = 0; i < 13; i++) {
      for (let j = 0; j < 13; j++) {
        const cell = this.cells[i * 13 + j];
        const agg = aggs[i * 13 + j];
        const bars = cell.querySelector('.bars');
        const fill = cell.querySelector('.fill');
        const sub = cell.querySelector('.sub');
        bars.innerHTML = '';
        bars.style.height = '';
        bars.style.alignItems = '';
        bars.style.flexDirection = '';
        bars.style.gap = '';
        fill.style.height = '0';
        cell.classList.toggle('empty', agg.present === 0 || agg.reach <= 1e-9);
        cell.classList.toggle('absent', agg.present === 0);
        const isSelected = !!(this.selectedCell && this.selectedCell[0] === i && this.selectedCell[1] === j);
        cell.classList.toggle('selected', isSelected);
        cell.setAttribute('aria-pressed', isSelected ? 'true' : 'false');
        // lock dot: bright on cells a per-hand lock names, dim on every cell a
        // whole-range/solved/fit lock constrains
        const mark = cell.querySelector('.lk-mark');
        if (mark) {
          const hand = lockedCells.has(`${i},${j}`);
          const whole = wholeLocked && agg.present > 0 && agg.reach > 1e-9;
          mark.style.display = (hand || whole) ? 'block' : 'none';
          mark.style.background = hand ? '#f5c542' : 'rgba(245,197,66,.55)';
        }
        const intensity = fillH(agg.reach / Math.max(agg.total, 1));
        if (effMode === 'strategy' && agg.strat
            && this.actionFilter != null && this.actionFilter < agg.strat.length) {
          // Action filter: show ONLY the selected action, in its colour. The
          // fill mode AND orientation apply exactly like the unfiltered STRAT
          // view -- the bar is just that action's slice of the hand's reach-fill
          // (Full -> pure frequency, Range/Normalized -> reach-weighted).
          const af = this.actionFilter;
          if (this.comboRows) {
            // Vertical: one column per combo, height = reach-fill x this combo's
            // frequency for the selected action.
            const list = this.cellCombosData(i, j, p).filter(c => c.strat);
            if (!list.length) { bars.style.opacity = 0; sub.textContent = ''; }
            else {
              bars.style.opacity = 1;
              bars.style.height = '100%';
              bars.style.alignItems = 'flex-end';
              const w = (100 / list.length).toFixed(3);
              bars.innerHTML = list.map(c => {
                const colH = fillH(c.reach) * (c.strat[af] || 0) * 100;
                return `<div data-combo="${c.combo}" style="width:${w}%;height:${colH.toFixed(1)}%;background:${colors[af]}"></div>`;
              }).join('');
              sub.textContent = '';
            }
          } else {
            // Horizontal: single bar, height = reach-fill x action frequency.
            const f = agg.strat[af];
            const d = document.createElement('div');
            d.style.width = '100%';
            d.style.background = colors[af];
            bars.appendChild(d);
            const show = agg.reach > 1e-9 && f > 0.002;
            bars.style.opacity = show ? 1 : 0;
            bars.style.height = `${(intensity * f * 100).toFixed(1)}%`;
            sub.textContent = show ? `${Math.round(f * 100)}%` : '';
          }
        } else if (effMode === 'strategy' && agg.strat && this.comboRows) {
          // one vertical column per combo (cell chopped vertically): column
          // height = its reach, split by that combo's action frequencies with
          // the most aggressive actions (reds) at the bottom
          const list = this.cellCombosData(i, j, p).filter(c => c.strat);
          if (!list.length) { bars.style.opacity = 0; sub.textContent = ''; }
          else {
            bars.style.opacity = 1;
            bars.style.height = '100%';
            bars.style.alignItems = 'flex-end'; // bottom-anchor the columns
            const w = (100 / list.length).toFixed(3);
            bars.innerHTML = list.map(c => {
              const colH = fillH(c.reach) * 100;
              const segs = c.strat.map((s, k) =>
                `<div style="height:${(s * 100).toFixed(2)}%;background:${colors[k]}"></div>`).join('');
              return `<div data-combo="${c.combo}" style="width:${w}%;height:${colH.toFixed(1)}%;display:flex;flex-direction:column">${segs}</div>`;
            }).join('');
            sub.textContent = '';
          }
        } else if (effMode === 'strategy' && agg.strat) {
          // biggest actions on the LEFT (jam / largest raise), fold on the
          // right — the tree lists actions passive-first, so walk it backwards
          for (let k = agg.strat.length - 1; k >= 0; k--) {
            const d = document.createElement('div');
            d.style.width = `${agg.strat[k] * 100}%`;
            d.style.background = colors[k];
            bars.appendChild(d);
          }
          // Discrete action colors at full opacity. How much of this hand
          // reaches the node is shown as vertical fill height ("Range
          // style), bottom-anchored — not by dimming the colors.
          bars.style.opacity = agg.reach > 1e-9 ? 1 : 0;
          bars.style.height = `${(intensity * 100).toFixed(1)}%`;
          // "Strategy + EV" display: the hand's EV in the cell corner
          sub.textContent =
            agg.ev != null && agg.reach > 1e-9 ? fmt(agg.ev) : '';
        } else if (effMode === 'strategy') {
          // not the actor: range-weight presence as a vertical orange bar
          bars.style.opacity = 0;
          fill.style.height = `${(intensity * 100).toFixed(1)}%`;
          fill.style.background = '#f28c26';
          fill.style.opacity = agg.reach > 1e-9 ? 0.9 : 0;
          sub.textContent = '';
        } else if (effMode === 'ev') {
          // Vertical (comboRows): one column per combo, height = its reach,
          // colour = its EV, natural combo order (same column = same combo as
          // STRAT/EQ). Horizontal: one combined bar coloured by aggregate EV.
          const evText = agg.ev != null && agg.reach > 1e-9 ? fmt(agg.ev) : '';
          if (this.comboRows) {
            const list = this.cellCombosData(i, j, p).filter(c => c.ev != null);
            renderCols(bars, fill, sub, list, c => evColor(c.ev), evText);
          } else {
            renderAgg(bars, fill, sub, agg.ev != null ? evColor(agg.ev) : null,
              intensity, evText, agg.reach);
          }
        } else if (effMode === 'eq') {
          const eqText = agg.eq != null && agg.reach > 1e-9 ? `${Math.round(agg.eq * 100)}%` : '';
          if (this.comboRows) {
            const list = this.cellCombosData(i, j, p).filter(c => c.eq != null);
            renderCols(bars, fill, sub, list, c => eqColor(c.eq), eqText);
          } else {
            renderAgg(bars, fill, sub, agg.eq != null ? eqColor(agg.eq) : null,
              intensity, eqText, agg.reach);
          }
        }
      }
    }
    this.renderFilterState();
  }

  renderLegend() {
    const el = this.els.legend;
    el.innerHTML = '';
    if (!this.view) return; // BROWSE controls are usable before any solve
    if (this.mode === 'exploit') {
      const key = document.createElement('span');
      key.className = 'key';
      key.textContent = this.effMode() === 'strategy'
        ? `EXPLOIT: cells = ${this.posLabel(this.player)}'s best-response actions (mostly pure); cell number = EV gain vs current strategy`
        : `EXPLOIT: heatmap = ${this.posLabel(this.player)}'s per-hand EV gain from best-responding vs the current strategy`;
      el.appendChild(key);
      return;
    }
    if (this.view.node_type === 'action' && this.mode === 'strategy'
        && this.view.player === this.player) {
      const colors = this.actionColors();
      if (this.actionFilter != null && this.actionFilter < this.view.actions.length) {
        const k = this.actionFilter;
        const key = document.createElement('span');
        key.className = 'key';
        key.innerHTML = `<i style="background:${colors[k]}"></i>${this.view.actions[k].label} frequency (bar height = how often each hand takes it)`;
        el.appendChild(key);
      } else {
        // legend reads left-to-right like the cell bars: biggest action first
        [...this.view.actions.keys()].reverse().forEach(k => {
          const a = this.view.actions[k];
          const key = document.createElement('span');
          key.className = 'key';
          key.innerHTML = `<i style="background:${colors[k]}"></i>${a.label}`;
          el.appendChild(key);
        });
      }
    } else if (this.mode === 'ev') {
      // per-combo columns exist only in the Vertical orientation; Horizontal
      // paints one combined bar per cell, so the caption would mislead there
      el.innerHTML = `<span class="key"><i style="background:hsl(0 70% 50%)"></i>lowest EV</span>
                      <span class="key"><i style="background:hsl(65 70% 50%)"></i>mid</span>
                      <span class="key"><i style="background:hsl(130 70% 50%)"></i>highest EV</span>` +
        (this.comboRows ? `<span class="key dim">· each column = one combo</span>` : '');
    } else if (this.mode === 'eq') {
      el.innerHTML = `<span class="key"><i style="background:hsl(0 75% 52%)"></i>0%</span>
                      <span class="key"><i style="background:hsl(65 75% 52%)"></i>50%</span>
                      <span class="key"><i style="background:hsl(130 75% 52%)"></i>100%</span>`;
    } else {
      el.innerHTML = `<span class="key"><i style="background:#f28c26"></i>range weight</span>`;
    }
  }

  // ----- hands panel (hover-driven) -----

  selectCell(i, j) {
    // click pins/unpins a cell so it stays after the mouse leaves the matrix
    if (this.selectedCell && this.selectedCell[0] === i && this.selectedCell[1] === j) {
      this.selectedCell = null;
    } else {
      this.selectedCell = [i, j];
    }
    this.renderMatrix();
    this.renderHandsPanel();
    // per-hand lock editor targets the pinned cell — refresh it on pin change
    if (this.lockMode === 'hands' && this.view && this.view.node_type === 'action') {
      this.renderActions();
    }
  }

  /** Villain-profile locks: when the spot came from the Preflop Lab with a
   *  modeled seat, one click compiles that player's postflop stats into node
   *  locks across his whole tree (equilibrium distortion via Range rakes). */
  renderVillainLocks() {
    this.onVillainLocksChange?.(); // the trust dial follows the villain lock
    const box = document.getElementById('villain-locks');
    if (!box) return;
    box.innerHTML = '';
    const task = this.villainLockTask;
    box.setAttribute('aria-busy', task ? 'true' : 'false');
    const pf = this.preflop;
    if (!pf || !pf.villains) return;
    for (const [side, p] of [['oop', 0], ['ip', 1]]) {
      const v = pf.villains[side];
      if (!v) continue;
      const on = this.villainLocked === p;
      const b = document.createElement('button');
      b.className = 'btn ghost sm vlock' + (on ? ' on' : '');
      b.textContent = on
        ? `\u{1F512} ${this.posLabel(p)} = ${v.name} \u00b7 unlock`
        : `LOCK ${this.posLabel(p)} TO ${v.name}`;
      b.disabled = !!task;
      if (task?.player === p) b.textContent = `${task.clearing ? 'UNLOCKING' : 'LOCKING'} ${this.posLabel(p)}…`;
      b.dataset.tip = on
        ? `${v.name}'s postflop stats are locked into every ${this.posLabel(p)} decision.`
        : hasContextualBetting(v.stats)
          ? `Apply ${v.name}'s contextual betting estimates and other postflop tendencies. Sparse evidence stays closer to the solved strategy; missing context keeps its betting baseline. Hand selection is inferred from the solve.`
          : `Compile ${v.name}'s postflop stats (c-bet ${v.stats.cbet.join('/')} \u00b7 fold-to-bet ${v.stats.fold_to_bet.join('/')} \u00b7 raise ${v.stats.raise_bet}%) into locks on every ${this.posLabel(p)} decision. Betting hands are inferred from the solve and adjusted to the stat targets.`;
      b.addEventListener('click', () => this.toggleVillainLock(p, v));
      box.appendChild(b);
    }
    if (this.villainLockEvidence && this.villainLocked !== null) {
      const evidence = document.createElement('div');
      evidence.className = 'dim';
      evidence.style.cssText = 'font-size:11px;flex-basis:100%;line-height:1.4';
      evidence.textContent = rootBettingEvidence(this.villainLockEvidence);
      evidence.dataset.tip = [this.villainLockEvidence.note, this.villainLockEvidence.source].filter(Boolean).join(' · ');
      box.appendChild(evidence);
    }
    if (task) {
      const feedback = document.createElement('div');
      feedback.className = 'vlock-progress';
      const stage = document.createElement('span');
      stage.className = 'vlock-stage';
      stage.setAttribute('role', 'status');
      stage.textContent = task.phase;
      const elapsed = document.createElement('span');
      elapsed.className = 'vlock-elapsed mono';
      const bar = document.createElement('progress');
      // No value: the current API provides completion, not intermediate counts.
      bar.setAttribute('aria-label', task.phase);
      feedback.append(stage, elapsed, bar);
      box.appendChild(feedback);
      this.updateVillainLockElapsed();
    }
  }

  updateVillainLockElapsed() {
    if (!this.villainLockTask) return;
    const elapsed = document.querySelector('#villain-locks .vlock-elapsed');
    const seconds = Math.floor((performance.now() - this.villainLockTask.startedAt) / 1000);
    if (elapsed) elapsed.textContent = `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')} elapsed`;
  }

  async toggleVillainLock(p, v) {
    if (this.villainLockTask) return; // one tree-wide change at a time
    const clearing = this.villainLocked === p;
    this.villainLockTask = {
      player: p, clearing, startedAt: performance.now(),
      phase: clearing ? 'Clearing profile locks…' : `Applying ${v.name} across the tree…`,
    };
    this.renderVillainLocks();
    const timer = setInterval(() => this.updateVillainLockElapsed(), 250);
    try {
      if (clearing) {
        const out = await api.profileLocksClear();
        this.setLockHistory(out.history); this.noteLockEdit();
        this.villainLocked = null;
        this.villainLockEvidence = null;
        toast('villain profile locks cleared');
      } else {
        const out = await api.profileLocks(p, v.stats,
          this.preflop ? this.preflop.aggressor : null, this.preflop?.pot_type ?? null, v.name);
        this.setLockHistory(out.history); this.noteLockEdit();
        this.villainLocked = p;
        this.villainLockEvidence = out.root_evidence || null;
        const worst = (out.rows || []).reduce((w, r) =>
          !w || Math.abs(r.achieved - r.target) > Math.abs(w.achieved - w.target) ? r : w, null);
        toast(`${out.locked} nodes locked to ${v.name}` +
          (worst ? ` (worst fit: ${worst.label} ${worst.achieved.toFixed(0)}% vs target ${worst.target.toFixed(0)}%)` : ''));
      }
      this.villainLockTask.phase = 'Refreshing…';
      this.renderVillainLocks();
      await this.refresh(); // keep feedback visible through the EV query too
    } catch (e) { this.fail(e); }
    finally {
      clearInterval(timer);
      this.villainLockTask = null;
      this.renderVillainLocks();
    }
  }

  renderHandsPanel() {
    const content = this.els.handsContent;
    const label = this.els.handsLabel;
    if (!content) return;
    if (!this.view) { content.innerHTML = ''; label.textContent = ''; return; }
    // Hovering a hand temporarily flips FILTERS/BLOCKERS to the HANDS view, so
    // you can inspect a combo without leaving your filter; it reverts on exit.
    // It stays put while the panel holds the pointer/keyboard (mid-edit).
    const flip = !this.panelBusy && this.hoverCell
      && (this.handsTab === 'filters' || this.handsTab === 'blockers');
    const eff = flip ? 'hands' : this.handsTab;
    if (this.els.handsTabs) {
      this.els.handsTabs.querySelectorAll('.htab').forEach(x =>
        x.classList.toggle('active', x.dataset.v === eff));
    }
    if (eff === 'filters') {
      const n = this.filterCats.size + this.filterSuits.size;
      label.textContent = n ? `${n} active · ${this.filterMode}` : '';
      this.renderFiltersPanel(content);
      return;
    }
    if (eff === 'blockers') {
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

    const d = this.cellHandData(i, j);
    if (!d.cand.length) {
      content.innerHTML = '<div class="dim" style="padding:10px 4px;font-size:11px">not in range</div>';
      return;
    }
    if (eff === 'hands') {
      content.innerHTML = this.handTilesHtml(d);
    } else {
      content.innerHTML = this.summaryHtml(
        d.cand.filter(x => x[3]), d.isActor, d.colors, d.acts);
    }
  }

  // Shared by the HANDS tab and the grid-hover popup: gather a cell's
  // in-deck combos. ALL of them are shown (dropping combos would skew the
  // SUMMARY stats); combos that barely reach this
  // node — e.g. a suit that folded out on an earlier street keeps a tiny
  // non-zero reach — are dimmed rather than hidden, judged relative to the
  // busiest combo of the SAME hand.
  cellHandData(i, j) {
    const info = cellInfo(i, j);
    const p = this.player;
    const hands = this.view.players[p].hands;
    const idx = this.handIdx[p];
    const cand = [];
    let cellMaxReach = 0;
    for (const [a, b] of cellCombos(info)) {
      const hi = idx.get(comboIndex(a, b));
      if (hi === undefined) continue;
      const h = hands[hi];
      if (h.reach > cellMaxReach) cellMaxReach = h.reach;
      cand.push([h, a, b, this.handMatches(p, hi)]);
    }
    return {
      cand,
      minReach: Math.max(1e-9, cellMaxReach * 0.01),
      isActor: this.view.node_type === 'action' && this.view.player === p,
      colors: this.actionColors(),
      acts: this.view.actions || [],
    };
  }

  handTilesHtml({ cand, minReach, isActor, colors, acts }, mini = false) {
    // Layout: 2 columns up to 4 combos, 3 columns beyond.
    const cols3 = cand.length > 4;
    const tiles = cand.map(([h, a, b, m]) =>
      this.handTile(h, a, b, isActor, colors, acts, cols3,
        !m || h.reach < minReach, mini));
    return `<div class="hand-tiles${cols3 ? ' cols3' : ''}">${tiles.join('')}</div>`;
  }

  // ----- grid-hover popup: the HANDS view in miniature -----

  showHandPop(i, j, cellEl) {
    if (!this.view) return;
    if (!this.handPop) {
      this.handPop = document.createElement('div');
      this.handPop.id = 'hand-pop';
      document.body.appendChild(this.handPop);
    }
    const d = this.cellHandData(i, j);
    if (!d.cand.length) return this.hideHandPop();
    const pop = this.handPop;
    pop.innerHTML = this.handTilesHtml(d, true);
    pop.classList.remove('hidden');
    // beside the hovered cell, flipped/clamped to stay on screen
    const r = cellEl.getBoundingClientRect();
    let x = r.right + 10;
    if (x + pop.offsetWidth > window.innerWidth - 8) x = r.left - pop.offsetWidth - 10;
    const y = Math.max(8, Math.min(r.top - 8, window.innerHeight - pop.offsetHeight - 8));
    pop.style.left = `${Math.max(8, x)}px`;
    pop.style.top = `${y}px`;
  }

  hideHandPop() {
    if (this.handPop) this.handPop.classList.add('hidden');
  }

  // Popup-compact action label: the kind plus %-of-pot only ("BET 75%",
  // "CHECK", "ALL-IN") — chip amounts stay in the side panel and tooltips.
  miniLabel(act) {
    if (act.label.startsWith('All-in')) return 'ALL-IN';
    const m = act.label.match(/\((\d+)%\)/);
    if (act.kind === 'bet' && m) return `BET ${m[1]}%`;
    return act.label.toUpperCase();
  }

  handTile(h, a, b, isActor, colors, acts, compact, dimmed, mini = false) {
    const name =
      `<span class="suit-${SUITS[suit(a)]}">${RANKS[rank(a)]}${SUIT_GLYPH[SUITS[suit(a)]]}</span>` +
      `<span class="suit-${SUITS[suit(b)]}">${RANKS[rank(b)]}${SUIT_GLYPH[SUITS[suit(b)]]}</span>`;
    const meta = `${h.eq != null ? (h.eq * 100).toFixed(0) + '% eq · ' : ''}EV`;
    let body;
    if (isActor && h.strategy) {
      // Horizontal split, aggressive actions on the left;
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
          `<div class="hand-line"><span class="hl-lab">${mini ? this.miniLabel(acts[k]) : acts[k].label}</span>` +
          `<span class="hl-ev">${ev}</span></div>`);
      }
      body = `<div class="htb-h${compact ? ' short' : ''}">` +
        `<div class="hseg-row">${segs.join('')}</div>` +
        `<div class="hand-lines">${lines.join('')}</div></div>`;
    } else {
      body = `<div class="htb flat"><span>EV <b>${h.ev != null ? fmt(h.ev) : '—'}</b></span>` +
        `<span>EQ <b>${h.eq != null ? (h.eq * 100).toFixed(1) + '%' : '—'}</b></span></div>`;
    }
    const meta_html = mini ? '' : `<span class="meta">${meta}</span>`;
    return `<div class="hand-tile${dimmed ? ' fdim' : ''}"><div class="hth"><span>${name}</span>${meta_html}</div>${body}</div>`;
  }

  // ----- Filters tab -----

  renderFiltersPanel(content) {
    const p = this.player;
    const hands = this.view.players[p].hands;
    const cats = this.cats[p];
    const isActor = this.view.node_type === 'action' && this.view.player === p;
    const colors = this.actionColors();
    const na = (this.view.actions || []).length;
    // the panel is rebuilt on every filter change: keep keyboard focus on the
    // control that was just used
    const ae = content.contains(document.activeElement) ? document.activeElement : null;
    const focusSel = ae?.dataset?.key ? `.filter-row[data-key="${ae.dataset.key}"]`
      : ae?.dataset?.suit ? `.suit-btn[data-suit="${ae.dataset.suit}"]`
      : ae?.dataset?.fmode ? `[data-fmode="${ae.dataset.fmode}"]`
      : ae?.id === 'filter-clear' ? '#filter-clear' : null;

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
        data-tip="The bar shows how these hands play here.">
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

    // Draw stats are meaningless on the river (every hand is 'no_draw'), so
    // the section is hidden there — EXCEPT filters still selected from an
    // earlier street, which must stay visible/deselectable: a persisting draw
    // INCLUDE filter matches nothing on the river and would otherwise blank
    // the whole matrix with no way to clear just that filter.
    const drawKeys = this.view.board.length < 5
      ? DRAW_ORDER
      : DRAW_ORDER.filter(k => this.filterCats.has(k));

    content.innerHTML = `
      <div class="filter-top">
        <div class="seg">
          <button data-fmode="include" class="${this.filterMode === 'include' ? 'active' : ''}">INCLUDE</button>
          <button data-fmode="exclude" class="${this.filterMode === 'exclude' ? 'active' : ''}">EXCLUDE</button>
        </div>
        <button class="btn ghost" id="filter-clear">clear</button>
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
          ${section('Draws', drawKeys.map(k => [k, DRAW_LABELS[k]]))}
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
    if (focusSel) content.querySelector(focusSel)?.focus();
  }

  applyFilters() {
    this.renderMatrix();
    this.renderHandsPanel();
  }


  // ----- equity distribution chart -----

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
        // weight by reach x valid (card-removal-adjusted opponent mass, when
        // the server provides it) so EV_OOP + EV_IP = pot holds in the sidebar
        const w = h.reach * (h.valid != null ? h.valid : 1);
        if (h.ev != null) { ev += h.ev * w; evW += w; }
        if (h.eq != null) { eq += h.eq * w; eqW += w; }
      });
      const avgEv = evW > 1e-12 ? ev / evW : null;
      const avgEq = eqW > 1e-12 ? eq / eqW : null;
      const eqr = avgEv != null && avgEq > 1e-9 ? avgEv / (avgEq * pot) : null;
      return `<div class="eqstat" data-tip="EQR = equity realization: EV as a fraction of (equity × pot). Under 100% this range under-realizes its equity.">
        <div class="eqstat-head"><i style="background:${EQ_COLORS[p]}"></i>${this.posLabel(p)}</div>
        <div class="eqstat-grid">
          <span><label>EV</label><div>${avgEv != null ? fmt(avgEv) : '—'}</div></span>
          <span><label>Equity</label><div>${avgEq != null ? (avgEq * 100).toFixed(1) + '%' : '—'}</div></span>
          <span><label>EQR</label><div>${eqr != null ? `${Math.round(eqr * 100)}%` : '—'}</div></span>
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

    // grid + tick labels, with the two axis titles so the panel tooltip is not
    // the only place that defines the axes
    ctx.strokeStyle = '#262626';
    ctx.fillStyle = '#8a8a8a';
    ctx.font = '12px IBM Plex Mono';
    ctx.textAlign = 'right';
    for (const v of [0.25, 0.5, 0.75]) {
      ctx.beginPath(); ctx.moveTo(px(0), py(v)); ctx.lineTo(px(1), py(v)); ctx.stroke();
      ctx.fillText(`${v * 100}`, L - 7, py(v) + 4);
      ctx.beginPath(); ctx.moveTo(px(v), py(0)); ctx.lineTo(px(v), py(1)); ctx.stroke();
      ctx.textAlign = 'center';
      ctx.fillText(`${v * 100}`, px(v), H - B + 14);
      ctx.textAlign = 'right';
    }
    ctx.font = '11px IBM Plex Sans';
    ctx.textAlign = 'center';
    ctx.fillText('% of range', L + (W - L - R) / 2, H - 6);
    ctx.save();
    ctx.translate(13, T + (H - T - B) / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('equity', 0, 0);
    ctx.restore();
    ctx.textAlign = 'start';
    ctx.font = '12px IBM Plex Mono';

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
      ctx.fillText(this.posLabel(p), L + 24, T + 14 + p * 17);
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
      ctx.textAlign = 'center';
      ctx.fillText(`${Math.round(xv * 100)}`, px(xv), H - B + 14);
      ctx.textAlign = 'start';
      const lines = [];
      for (const p of [0, 1]) {
        const { pts } = this.eqCurves[p];
        if (!pts.length) continue;
        let pt = pts[0];
        for (const q of pts) { if (q.x <= xv) pt = q; else break; }
        const h = this.view.players[p].hands[pt.i];
        lines.push({ p, text: `${this.posLabel(p)} ${h.combo} ${(pt.y * 100).toFixed(1)}%`, y: pt.y });
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

  // ----- Blockers tab -----

  renderBlockersPanel(content) {
    const p = this.player;
    const isActor = this.view.node_type === 'action' && this.view.player === p;
    // keep keyboard focus on the sort column across the rebuild
    const focusSort = content.contains(document.activeElement)
      ? document.activeElement.dataset?.sort : null;
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
    const ariaSort = k =>
      k === sortCol ? (sortDir === -1 ? 'descending' : 'ascending') : 'none';
    // header cells are buttons: focusable, Enter/Space sorts, aria-sort labels
    // the active column (one shared hint above instead of per-column tips)
    const header =
      `<div class="blocker-row head" style="grid-template-columns:52px repeat(${na},1fr)">` +
      `<button type="button" role="columnheader" aria-sort="${ariaSort('card')}" ` +
      `class="bk-head${sortCol === 'card' ? ' sorted' : ''}" data-sort="card" ` +
      `style="background:none;border:0;font:inherit;color:inherit">cards${arrow('card')}</button>` +
      acts.map((a, k) =>
        `<button type="button" role="columnheader" aria-sort="${ariaSort(k)}" ` +
        `class="bk-head${k === sortCol ? ' sorted' : ''}" data-sort="${k}" ` +
        `style="background:none;border:0;font:inherit;color:inherit">` +
        `<i style="background:${colors[k]}"></i>${a.label}${arrow(k)}</button>`
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

    // delta key: colours run red (holding it folds more) -> green (plays more)
    const key = `<div class="dim" style="display:flex;gap:10px;align-items:center;font-size:10px;margin-bottom:6px">` +
      [['−', 'hsl(8 65% 41%)'], ['0', 'hsl(70 50% 40%)'], ['+', 'hsl(120 50% 34%)']]
        .map(([s, c]) => `<span style="display:flex;align-items:center;gap:3px">` +
          `<i style="width:9px;height:9px;border-radius:2px;background:${c}"></i>${s}</span>`).join('') +
      `</div>`;

    content.innerHTML =
      `<div class="dim" style="font-size:11px;margin-bottom:8px">How holding each card shifts ` +
      `${this.posLabel(p)}'s strategy vs the range average.</div>` + key +
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
    if (focusSort != null) content.querySelector(`.bk-head[data-sort="${focusSort}"]`)?.focus();
  }

  summaryHtml(present, isActor, colors, acts) {
    let reach = 0, weight = 0, ev = 0, evW = 0, eq = 0, eqW = 0;
    const freqs = acts.map(() => 0);
    const aev = acts.map(() => ({ n: 0, d: 0 }));
    for (const [h] of present) {
      reach += h.reach; weight += h.weight;
      // EV/EQ averages weight by reach x valid (card-removal-adjusted opponent
      // mass, when the server provides it); frequencies stay pure reach
      const w = h.reach * (h.valid != null ? h.valid : 1);
      if (h.ev != null) { ev += h.ev * w; evW += w; }
      if (h.eq != null) { eq += h.eq * w; eqW += w; }
      if (isActor && h.strategy) {
        h.strategy.forEach((s, k) => {
          freqs[k] += s * h.reach;
          if (h.evs && h.evs[k] != null) { aev[k].n += h.evs[k] * w * s; aev[k].d += w * s; }
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
    this.els.segPlayer.querySelectorAll('button').forEach(b => {
      const p = +b.dataset.v;
      b.classList.toggle('active', p === this.player);
      b.textContent = this.posLabel(p); // BB/BTN… from preflop setup, else OOP/IP
    });
    this.els.segMode.querySelectorAll('button').forEach(b =>
      b.classList.toggle('active', b.dataset.v === this.mode));
  }
}

/** Round non-negative shares to integer percentages summing to EXACTLY 100
 *  (largest-remainder method) — independent rounding can produce 99/101%,
 *  making a pristine lock editor flag its own prefill as invalid. */
function pctShares(shares) {
  const clamped = shares.map(x => Math.max(0, x || 0));
  const total = clamped.reduce((a, b) => a + b, 0);
  const exact = clamped.map(x => total > 0 ? (x / total) * 100 : 100 / clamped.length);
  const out = exact.map(Math.floor);
  let left = 100 - out.reduce((a, b) => a + b, 0);
  const order = exact.map((x, k) => [x - out[k], k]).sort((a, b) => b[0] - a[0]);
  for (let i = 0; left > 0 && i < order.length; i++, left--) out[order[i][1]]++;
  return out;
}

/** Is this GET /api/locks label the lock at node `at`? A manual lock stores
 *  the node's own description; freeze-earlier and materialized fits append a
 *  parenthetical. Older sessions labelled the root just "root". */
function lockLabelAtNode(label, at) {
  if (!at) return false;
  if (label === at || label.startsWith(`${at} (`)) return true;
  return at.endsWith(' root') && label === 'root';
}

/** Edit-history labels append the node after " · " (lock_edit_label), then an
 *  optional "(+N earlier decisions frozen)" note. */
function editLabelAtNode(label, at) {
  if (!at) return false;
  return label.endsWith(` · ${at}`) || label.includes(` · ${at} (`);
}

/** What an edit-history label did, by its prefix (lock_edit_label in
 *  crates/server/src/main.rs). "Lock 6 combos" is a per-hand lock. */
function editKind(label) {
  if (label.startsWith('Lock frequencies (least EV loss)')) return { kind: 'fit', combos: 0 };
  if (label.startsWith('Lock frequencies')) return { kind: 'range', combos: 0 };
  if (label.startsWith('Lock as solved')) return { kind: 'solved', combos: 0 };
  if (label.startsWith('Start least-exploitable fit')) return { kind: 'fit', combos: 0 };
  if (label.startsWith('Unlock')) return { kind: 'none', combos: 0 };
  const many = label.match(/^Lock (\d+) combos · /);
  if (many) return { kind: 'hands', combos: +many[1] };
  if (label.startsWith('Lock ')) return { kind: 'hands', combos: 1 };
  return { kind: 'other', combos: 0 };
}

/** Matrix cell ("i,j") holding a two-card combo, matching cellInfo()'s order. */
function comboCell(a, b) {
  const hi = Math.max(rank(a), rank(b));
  const lo = Math.min(rank(a), rank(b));
  if (hi === lo) return `${12 - hi},${12 - hi}`;
  return suit(a) === suit(b) ? `${12 - hi},${12 - lo}` : `${12 - lo},${12 - hi}`;
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
