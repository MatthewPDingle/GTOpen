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

/** Toast suffix for a lock reply that also kept earlier decisions as solved. */
function frozenNote(out) {
  const n = out?.frozen || 0;
  return n ? `, and ${n} earlier decision${n > 1 ? 's' : ''} kept as solved` : '';
}

/** An action label without its "(50%)" pot share: "Bet 4.25 (50%)" -> "Bet 4.25". */
export function shortAction(label) {
  return String(label || '').replace(/\s*\(\d+(\.\d+)?%\)\s*$/, '');
}

/** Where a lock sits, from the actions that lead to it: "first decision",
 *  "after Check", "after … › Call › 7h › Check". */
export function lockWhere(line) {
  if (!line?.length) return 'first decision';
  const parts = line.map(shortAction);
  const tail = parts.length > 3 ? ['…', ...parts.slice(-3)] : parts;
  return `after ${tail.join(' › ')}`;
}

/** What a lock makes the range do: "100% Check", "48% Check, 52% All-in 26". */
export function lockMix(actions, freqs) {
  const parts = [];
  (actions || []).forEach((a, k) => {
    const pct = Math.round((freqs?.[k] || 0) * 100);
    if (pct >= 1) parts.push(`${pct}% ${shortAction(a)}`);
  });
  return parts.join(', ');
}

/** Hand names for a sentence: "AA, AKs, AKo" or "AA, AKs, AKo, KK, QQ + 4 more". */
export function handList(names, max = 6) {
  if (names.length <= max) return names.join(', ');
  return `${names.slice(0, max - 1).join(', ')} + ${names.length - (max - 1)} more`;
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
export function freezeableAncestors(path, pathLabels, board, isLocked, isOwn = () => true) {
  let n = 0;
  for (let i = 0; i < path.length; i++) {
    if (path[i].type !== 'action') continue;
    // only the locked player's own decisions, when the server keeps just those
    if (!isOwn(i)) continue;
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
    // Hands picked in the grid for the lock box (cells "i,j" at the viewed
    // node), the numbers typed there, and the list of every lock.
    this.lockSel = new Set();
    this.lockSelAt = '';
    this.lockDraft = null;      // { at, vals }: typed numbers survive re-renders
    this.lockScope = 'range';   // with filters on and nothing picked: 'range' | 'filtered'
    this.locksView = null;      // GET /api/locks/list; null against an older server
    this.serverLevel = null;    // what the running server can do (see version.js)
    api.version().then(v => { this.serverLevel = v?.server_level ?? 0; })
      .catch(() => { this.serverLevel = 0; });
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
      } else if (e.key === 'Escape' && (this.selectedCell || this.lockSel.size)) {
        this.selectedCell = null;
        this.lockSel.clear();
        this.renderMatrix();
        this.renderHandsPanel();
        this.drawEquityChart();
        if (this.view.node_type === 'action') this.renderActions();
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
        // press = pick (or pin); keep the button down and move to pick several
        cell.addEventListener('mousedown', e => {
          if (e.button !== 0) return;
          const was = this.lockSel.has(`${i},${j}`);
          this.selectCell(i, j);
          this.dragPick = this.canPickHands() ? { add: !was } : null;
        });
        cell.addEventListener('mouseenter', e => {
          if (this.dragPick && (e.buttons & 1)) this.pickCell(i, j, this.dragPick.add);
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
    m.style.userSelect = 'none'; // dragging over hands picks them, not their text
    window.addEventListener('mouseup', () => { this.dragPick = null; });
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
      // the list of locks: who, where, what — and what to do next
      this.locksBar = document.createElement('div');
      this.locksBar.className = 'locks-bar';
      this.locksBar.style.display = 'none';
      host.insertBefore(this.locksBar, top);
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

  /** The tab's no-spot state before a build: a node fetch in flight is
   *  "loading", not "no spot". */
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

  /** Record a lock/fit edit: the displayed strategy is stale until the next
   *  solve, and the list of locks says so until one has run. */
  noteLockEdit() {
    this.pendingLockEdits += 1;
    if (this._pendingBase == null) {
      const gen = ++this._pendingGen;
      api.status().then(st => {
        if (gen === this._pendingGen && this._pendingBase == null) this._pendingBase = st.iteration;
      }).catch(() => { /* no baseline: the note is still true */ });
    }
    this.onLockEdit?.(); // app.js resyncs the server's trust readout
    this.renderLocksBar();
  }

  /** Remove every lock. One Undo brings them all back. */
  async clearAllLocks() {
    try {
      const out = await api.locksClear();
      this.setLockHistory(out.history);
      this.lockCells.clear();
      this.saveLockCells();
      this.syncVillainLocked(out.history);
      this.noteLockEdit();
      toast('all locks cleared (Undo brings them back)');
      this.renderVillainLocks();
      await this.refresh();
    } catch (e) { this.fail(e); }
  }

  /** Remove one lock from the list, wherever the grid is. */
  async removeLock(l) {
    try {
      const out = await api.unlock(l.path);
      this.setLockHistory(out.history);
      this.forgetLockCells(l.label);
      this.noteLockEdit();
      toast('lock removed');
      await this.refresh();
    } catch (e) { this.fail(e); }
  }

  /** The list of locks above the grid: one chip per locked decision (who,
   *  where, what), click to go there, x to remove. After a lock change it
   *  also says the solve is older than the locks and offers to solve again
   *  (the instant answer is the EXPLOIT view, which has its own button). */
  renderLocksBar() {
    const bar = this.locksBar;
    if (!bar) return;
    const lv = this.locksView;
    const labels = this.lockLabels || [];
    const profile = lv?.profile || [0, 0];
    const count = lv ? lv.locks.length + (profile[0] ? 1 : 0) + (profile[1] ? 1 : 0) : labels.length;
    const pending = this.pendingLockEdits > 0;
    const solve = this.solveInfo?.() || { label: 'RE-SOLVE', drift: false, running: false };
    if (!this.view || (!count && !pending)) {
      bar.style.display = 'none';
      bar.innerHTML = '';
      this._locksBarKey = null;
      return;
    }
    // repaint only on a real change: this runs on every status poll, and a
    // rebuilt bar would drop the tooltip or the focus the user has on it
    const key = JSON.stringify([lv, lv ? null : labels, pending, solve, this.path, this.player,
      this.villainLocked, [...this.lockCells].map(([at, cells]) => [at, cells.size])]);
    if (key === this._locksBarKey) return;
    this._locksBarKey = key;
    bar.style.display = 'flex';
    bar.innerHTML = '';
    const head = document.createElement('span');
    head.className = 'lb-head';
    head.textContent = 'LOCKS';
    bar.appendChild(head);

    const here = JSON.stringify(this.path);
    const chip = (text, tip, { current = false, go = null, remove = null, removeTip = '' } = {}) => {
      const c = document.createElement('span');
      c.className = 'lb-chip' + (current ? ' current' : '');
      const main = document.createElement(go ? 'button' : 'span');
      main.className = 'lb-go';
      if (go) { main.type = 'button'; main.addEventListener('click', go); }
      main.textContent = text;
      main.dataset.tip = tip;
      c.appendChild(main);
      if (remove) {
        const x = document.createElement('button');
        x.type = 'button';
        x.className = 'lb-x';
        x.textContent = '×';
        x.setAttribute('aria-label', `remove: ${text}`);
        x.dataset.tip = removeTip;
        x.addEventListener('click', remove);
        c.appendChild(x);
      }
      bar.appendChild(c);
    };
    if (lv) {
      for (const l of lv.locks) {
        const who = this.posLabel(l.player);
        const what = l.kind === 'kept' ? 'kept as solved' : lockMix(l.actions, l.freqs);
        const cells = [...(this.lockCells.get(l.label) || [])]
          .map(k => cellInfo(...k.split(',').map(Number)).label);
        let tip = `${who}, ${lockWhere(l.line)}: ${what}.`;
        if (cells.length) tip += ` You set ${handList(cells, 12)}; ${who}'s other hands play as they did then.`;
        if (l.kind === 'kept') tip += ` Held the way the solve had it, because it leads to another of ${who}'s locks.`;
        if (l.kind === 'fit') tip += ' The result of a "Least exploitable" lock.';
        const isHere = l.path && JSON.stringify(l.path) === here;
        tip += isHere ? ' You are looking at it.' : l.path ? ' Click to go to this decision.' : '';
        const some = cells.length && l.kind === 'manual' ? `${cells.length} hand${cells.length === 1 ? '' : 's'} set · ` : '';
        chip(`${who} · ${lockWhere(l.line)} · ${some}${what}`, tip, {
          current: isHere,
          go: l.path && !isHere ? () => this.navigate(l.path) : null,
          remove: l.path ? () => this.removeLock(l) : null,
          removeTip: 'Remove this lock. The other locks stay.',
        });
      }
      profile.forEach((n, p) => {
        if (!n) return;
        const who = this.posLabel(p);
        const v = this.preflop?.villains?.[p === 0 ? 'oop' : 'ip'];
        const name = this.villainLocked === p && v?.name ? v.name : 'a player model';
        chip(`${who} · every decision · plays like ${name}`,
          `${n} of ${who}'s decisions are locked to the model's bet, fold and raise rates.`, {
            remove: () => (v && this.villainLocked === p ? this.toggleVillainLock(p, v) : this.clearProfileLocks()),
            removeTip: `Remove the player model from ${who}. Your own locks stay.`,
          });
      });
    } else {
      // an older server only names the locks: restart GTOpen for the full list
      for (const l of labels) chip(l, 'Restart GTOpen to jump to a lock or remove it from here.');
    }
    if (!count) {
      const none = document.createElement('span');
      none.className = 'lb-note';
      none.textContent = 'none';
      bar.appendChild(none);
    } else if (lv && count > 1) {
      const all = document.createElement('button');
      all.type = 'button';
      all.className = 'btn ghost xs';
      all.textContent = 'clear all';
      all.dataset.tip = 'Remove every lock. One Undo brings them all back.';
      all.addEventListener('click', () => this.clearAllLocks());
      bar.appendChild(all);
    }
    if (!pending) return;
    // the next step after a lock change, said once and close to the locks
    const next = document.createElement('span');
    next.className = 'lb-next';
    const note = document.createElement('span');
    note.className = 'lb-note';
    note.textContent = count ? 'not in the solve yet' : 'locks changed since the solve';
    const why = document.createElement('button');
    why.type = 'button';
    why.className = 'info-dot';
    why.textContent = '?';
    why.setAttribute('aria-label', 'What to do after changing a lock');
    why.dataset.tip = 'The grid still shows the solve from before your last lock change. ' +
      'EXPLOIT shows at once how the player whose hands are showing should play against the locks. ' +
      'RE-SOLVE solves again with the locks in place, so both players adjust.';
    next.append(note, why);
    if (!solve.running) {
      const again = document.createElement('button');
      again.type = 'button';
      again.className = 'btn sm' + (solve.drift ? ' ghost' : '');
      again.textContent = solve.label;
      again.dataset.tip = solve.drift
        ? 'Setup no longer matches the tree you locked, so solving builds a new tree and drops these locks. To keep them, put Setup back the way it was.'
        : 'Solve again with the locks in place, so both players adjust around them.';
      again.addEventListener('click', () => document.getElementById('btn-solve-top')?.click());
      next.appendChild(again);
    }
    bar.appendChild(next);
  }

  /** Drop a player model's locks when this page does not know which model made them. */
  async clearProfileLocks() {
    try {
      const out = await api.profileLocksClear();
      this.setLockHistory(out.history);
      this.syncVillainLocked(out.history);
      this.noteLockEdit();
      toast('player model removed');
      this.renderVillainLocks();
      await this.refresh();
    } catch (e) { this.fail(e); }
  }

  /** Clear the note once a solve has finished past the edits' baseline. */
  clearPendingAfterSolve() {
    if (!this.pendingLockEdits || this._pendingBase == null) return;
    const base = this._pendingBase;
    api.status().then(st => {
      if (st.state === 'running' || st.iteration <= base) return;
      this.pendingLockEdits = 0;
      this._pendingBase = null;
      this.renderLocksBar();
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
  lockSummaryText(at, viewed = true) {
    const s = this.lockSummary(at);
    if (!s) {
      // `view.locked` describes the node on screen, not an earlier one
      if (!viewed || !this.view?.locked) return '';
      return this.lockHistory?.profile_players?.length ? 'player model' : 'locked';
    }
    const words = { range: 'whole range', solved: 'as solved', fit: 'whole range', profile: 'player model' };
    const base = words[s.kind] || 'locked';
    // hand classes this page set, when it remembers them; else the combo count
    const cells = this.lockedCellsAt(at).size;
    const some = cells ? `${cells} hand${cells === 1 ? '' : 's'}`
      : `${s.combos} combo${s.combos === 1 ? '' : 's'}`;
    if (s.kind === 'hands') return some;
    return s.combos ? `${base} + ${some}` : base;
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
    const listP = api.locksList().catch(() => null); // an older server has no list
    let view;
    try {
      view = await api.node(this.path);
    } catch (e) {
      if (gen !== this._refreshGen) return; // superseded: a newer refresh owns the UI
      this.loadingNode = false;
      this.fail(e, () => this.refresh());
      if (this.path.length) { this.path = []; this.line = []; this.lineHistory = null; return this.refresh(); }
      this.view = null;
      this.renderLocksBar();
      if (this.els.matrix) this.els.matrix.style.opacity = '';
      if (this.els.pot) this.els.pot.textContent = '—';
      this.renderEmptyState();
      return;
    }
    if (gen !== this._refreshGen) return; // stale response: user navigated again mid-flight
    this.loadingNode = false;
    this.view = view;
    this.lockLabels = await locksP; // which nodes hold a lock
    this.locksView = await listP;
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
    // hands picked for the lock box belong to one decision
    const lockAt = this.lockNodeLabel();
    if (lockAt !== this.lockSelAt) {
      this.lockSel.clear();
      this.lockSelAt = lockAt;
      this.lockDraft = null;
      this.lockScope = 'range';
    }
    this.renderLocksBar();
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
    this.locksView = null;
    this.lockSel.clear();
    this.lockDraft = null;
    this.renderLocksBar();
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
    // every box that holds a lock shows a padlock: labels of the line so far
    // name each box the way the server names its lock
    const board = this.rootBoard();
    const stepLabels = hist.map(h =>
      h.kind === 'card' ? (h.card || '?') : h.kind === 'action' ? (h.actions[h.chosen]?.label || '?') : '?');
    const lockAtStep = i => {
      const before = stepLabels.slice(0, i);
      return this.lockSummaryText(before.length ? `${board} ${before.join(' > ')}` : `${board} root`, false);
    };
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
        const hd = head(s, this.posLabel(h.player), fmt(h.stack), 'stack');
        const locked = lockAtStep(i);
        if (locked) {
          const mark = document.createElement('i');
          mark.className = 'hist-lock';
          mark.textContent = '\u{1F512}';
          mark.dataset.tip = `${this.posLabel(h.player)} is locked here (${locked}).`;
          hd.firstChild.after(mark);
        }
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
        tile.dataset.tip = `${a.label}: average EV ${ev != null ? fmt(ev) : '—'}. Click to show only the hands that take it. The arrow goes to what happens after it.`;
        tile.innerHTML = `
          <div class="at-label">${a.label}</div>
          <div class="at-foot">
            <span class="at-pct">${(freq * 100).toFixed(1)}%</span>
            <span class="at-combos">${freqs[k].toFixed(1)}<small>combos</small></span>
          </div>` +
          (sel ? `<span class="at-badge" aria-hidden="true" style="position:absolute;top:4px;right:27px;` +
            `font:9px/1 var(--font-disp);letter-spacing:.08em;background:#fff;color:#111;` +
            `border-radius:2px;padding:2px 4px">filter</span>` : '');
        tile.addEventListener('click', () => {
          this.actionFilter = this.actionFilter === k ? null : k;
          this.renderActions();
          this.renderMatrix();
          this.renderLegend();
        });
        // the tile filters; this arrow follows the action, like its name in the line above
        const go = document.createElement('span');
        go.className = 'at-go';
        go.setAttribute('role', 'button');
        go.tabIndex = 0;
        go.textContent = '›';
        go.setAttribute('aria-label', `go to what happens after ${a.label}`);
        go.dataset.tip = `Go to what happens after ${shortAction(a.label)}.`;
        const follow = e => {
          e.stopPropagation();
          e.preventDefault();
          this.navigate([...this.path, { type: 'action', index: k }]);
        };
        go.addEventListener('click', follow);
        go.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') follow(e); });
        tile.appendChild(go);
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
            // one pick per fetch: a second card step on the same path is
            // rejected by the server, and refresh()'s recovery would drop the
            // whole navigated line
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

  /** True when a click in the grid picks hands for the lock box: the grid
   *  shows the hands of the player whose decision this is. */
  canPickHands() {
    return !!this.view && this.view.node_type === 'action' && this.player === this.view.player;
  }

  /** The acting player's combos in a grid cell, as [{ name, hi }]. */
  actorCombos(i, j) {
    if (!this.view || this.view.node_type !== 'action') return [];
    const idx = this.handIdx[this.view.player];
    const out = [];
    for (const [a, b] of cellCombos(cellInfo(i, j))) {
      const hi = idx.get(comboIndex(a, b));
      if (hi !== undefined) out.push({ name: cardToString(a) + cardToString(b), hi });
    }
    return out;
  }

  /** What the lock box would set. Null means the whole range. Otherwise the
   *  hands picked in the grid, or the hands the filters show: { kind, cells,
   *  names, combos, filtered }. With filters on, a lock only sets the combos
   *  that match them, which is how one suit or one hand group gets locked. */
  lockTarget() {
    if (!this.canPickHands()) return null;
    const p = this.view.player;
    const filtered = this.filtersActive();
    const keep = c => !filtered || this.handMatches(p, c.hi);
    const gather = (kind, cellList) => {
      const out = { kind, cells: [], names: [], combos: [], filtered };
      for (const [i, j] of cellList) {
        const cs = this.actorCombos(i, j).filter(keep);
        if (!cs.length) continue;
        out.cells.push([i, j]);
        out.names.push(cellInfo(i, j).label);
        out.combos.push(...cs);
      }
      return out;
    };
    if (this.lockSel.size) {
      const picked = [...this.lockSel].map(k => k.split(',').map(Number))
        .sort((a, b) => a[0] - b[0] || a[1] - b[1]);
      return gather('picked', picked);
    }
    if (filtered && this.lockScope === 'filtered') {
      const all = [];
      for (let i = 0; i < 13; i++) for (let j = 0; j < 13; j++) all.push([i, j]);
      return gather('filtered', all);
    }
    return null;
  }

  /** The lock box. One editor for every kind of lock: with no hand picked the
   *  numbers are for the whole range, with hands picked (or filters applied)
   *  they are exact for those hands. */
  renderLockControls(el, colors) {
    const p = this.view.player;
    const who = this.posLabel(p);
    const acts = this.view.actions;
    const hands = this.view.players[p].hands;
    const locked = this.view.locked;
    const label = this.lockNodeLabel();
    const summary = this.lockSummaryText(label);
    const target = this.lockTarget();
    const filtersOn = this.canPickHands() && this.filtersActive();

    // how a set of hands plays now: weighted by how often each gets here, or
    // evenly when none does (a hand that never arrives still has a play)
    const mixOf = idxs => {
      let tot = 0, n = 0;
      const agg = acts.map(() => 0), flat = acts.map(() => 0);
      for (const hi of idxs) {
        const h = hands[hi];
        if (!h?.strategy) continue;
        n++;
        tot += h.reach;
        h.strategy.forEach((x, k) => { agg[k] += x * h.reach; flat[k] += x; });
      }
      if (tot > 1e-9) return { mix: agg.map(x => x / tot), reach: tot };
      return { mix: n ? flat.map(x => x / n) : null, reach: 0 };
    };
    const whole = mixOf(hands.map((_, i) => i));
    const cur = target ? mixOf(target.combos.map(c => c.hi)) : whole;

    const wrap = document.createElement('div');
    wrap.className = 'lock-panel';
    wrap.innerHTML = `
      <div class="lock-head">NODE LOCKING <button type="button" class="info-dot" aria-label="How node locking works" data-tip="A lock fixes how ${who} plays at this decision until you remove it. Then EXPLOIT shows the other player's best reply at once, and RE-SOLVE lets both players adjust. On a turn or river, a lock also covers the runouts that differ only by suit.">?</button>${summary ? ` <span class="lock-badge" data-lock-summary data-tip="What is locked at this decision now.">${summary}</span>` : ''}${this.view.fit ? ' <span class="lock-badge">FITTING</span>' : ''}<span class="lock-history"></span>${locked ? '<button type="button" class="btn ghost xs lock-unlock" data-tip="Remove the lock at this decision. Locks elsewhere stay.">unlock this decision</button>' : ''}</div>
      <div class="lk-for"></div>
      <div class="lock-body"></div>`;
    const body = wrap.querySelector('.lock-body');
    const forEl = wrap.querySelector('.lk-for');
    this.paintLockHistory(wrap.querySelector('.lock-history'));
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

    // --- who and which hands the numbers below are for
    const say = html => { const sp = document.createElement('span'); sp.innerHTML = html; forEl.appendChild(sp); return sp; };
    const link = (text, tip, fn) => {
      const b = document.createElement('button');
      b.type = 'button'; b.className = 'btn ghost xs'; b.textContent = text; b.dataset.tip = tip;
      b.addEventListener('click', fn);
      forEl.appendChild(b);
      return b;
    };
    if (target?.kind === 'picked') {
      say(`How <b>${who}</b> plays <b>${handList(target.names) || 'the picked hands'}</b> here` +
        (target.filtered ? ' <span class="dim">(only the combos your filters show)</span>' : ''));
      link('whole range instead', 'Drop the picked hands. The numbers then apply to the whole range.', () => {
        this.lockSel.clear();
        this.lockDraft = null;
        this.renderMatrix();
        this.renderActions();
      });
    } else if (filtersOn) {
      say(`How <b>${who}</b> plays here, for`);
      const seg = document.createElement('div');
      seg.className = 'seg lk-method';
      for (const [key, name, tip] of [
        ['range', 'the whole range', 'The numbers are for the whole range, whatever the filters show.'],
        ['filtered', 'the hands your filters show', 'The numbers are exact for the hands the FILTERS tab leaves in the grid, such as every top pair or one suit. The other hands stay as they play now.'],
      ]) {
        const b = document.createElement('button');
        b.type = 'button'; b.textContent = name; b.dataset.tip = tip;
        b.className = this.lockScope === key ? 'active' : '';
        b.addEventListener('click', () => { this.lockScope = key; this.lockDraft = null; this.renderActions(); });
        seg.appendChild(b);
      }
      forEl.appendChild(seg);
    } else if (this.canPickHands()) {
      say(`How <b>${who}</b> plays here, as a <b>whole range</b>. <span class="dim">Click hands in the grid to lock only those.</span>`);
    } else {
      say(`How <b>${who}</b> plays here, as a <b>whole range</b>. <span class="dim">The grid is showing ${this.posLabel(1 - p)}'s hands.</span>`);
      link(`show ${who}'s hands`, `Show ${who}'s hands in the grid, so you can pick the ones to lock.`, () => {
        this.player = p;
        this.syncSegs(); this.renderActions(); this.renderMatrix(); this.renderLegend();
        this.renderHandsPanel(); this.drawEquityChart();
      });
    }

    // --- one [ %] box per action; what is typed stays until it is locked
    const draft = this.lockDraft && this.lockDraft.at === label && this.lockDraft.vals.length === acts.length
      ? this.lockDraft.vals : null;
    const freqEditor = init => {
      const cont = document.createElement('div');
      cont.className = 'lk-actions';
      const inputs = [];
      const pcts = init ? pctShares(init) : acts.map(() => 0); // integers summing to exactly 100
      const sumRow = document.createElement('div');
      sumRow.className = 'lk-sumrow';
      const sumEl = document.createElement('span'); sumEl.className = 'lk-sum';
      const update = () => {
        const t = inputs.reduce((a, i) => a + (+i.value || 0), 0);
        sumEl.textContent = `total ${Math.round(t)}%`;
        sumEl.classList.toggle('bad', Math.abs(t - 100) > 0.5);
      };
      const typed = () => { this.lockDraft = { at: label, vals: inputs.map(i => i.value) }; update(); };
      acts.forEach((a, k) => {
        const row = document.createElement('label');
        row.className = 'lk-act';
        row.innerHTML = `<i class="lk-sw" style="background:${colors[k]}"></i><span class="lk-lab">${a.label}</span>`;
        const always = document.createElement('button');
        always.type = 'button'; always.className = 'btn ghost xs lk-always'; always.textContent = 'always';
        always.dataset.tip = `Set ${shortAction(a.label)} to 100% and the rest to 0.`;
        always.addEventListener('click', e => {
          e.preventDefault();
          inputs.forEach((inp, m) => { inp.value = m === k ? '100' : '0'; });
          typed();
        });
        const inp = document.createElement('input');
        inp.type = 'number'; inp.min = '0'; inp.max = '100'; inp.step = '1';
        inp.value = draft ? draft[k] : `${pcts[k]}`;
        inp.className = 'lk-pct';
        inp.setAttribute('aria-label', `${a.label} %`);
        const unit = document.createElement('span'); unit.className = 'lk-unit'; unit.textContent = '%';
        row.append(always, inp, unit);
        cont.appendChild(row);
        inputs.push(inp);
      });
      const norm = document.createElement('button'); norm.type = 'button'; norm.className = 'btn ghost xs'; norm.textContent = 'make it 100%';
      norm.dataset.tip = 'Scale the numbers so they add up to 100%.';
      norm.addEventListener('click', () => {
        const t = inputs.reduce((a, i) => a + (+i.value || 0), 0);
        if (t > 0) {
          const np = pctShares(inputs.map(i => +i.value || 0));
          inputs.forEach((inp, k) => { inp.value = `${np[k]}`; });
          typed();
        }
      });
      inputs.forEach(i => i.addEventListener('input', typed));
      update();
      sumRow.append(sumEl, norm);
      if (draft && init) {
        const back = document.createElement('button'); back.type = 'button'; back.className = 'btn ghost xs'; back.textContent = 'as played now';
        back.dataset.tip = 'Put back how these hands play now.';
        back.addEventListener('click', () => { this.lockDraft = null; this.renderActions(); });
        sumRow.appendChild(back);
      }
      return { cont, inputs, sumRow };
    };
    const readFreqs = ed => {
      const freqs = ed.inputs.map(i => Math.max(0, +i.value || 0));
      if (freqs.reduce((a, b) => a + b, 0) <= 0) { toast('set at least one action above 0%', true); return null; }
      return freqs;
    };
    const done = () => { this.lockSel.clear(); this.lockDraft = null; this.refresh(); };
    const foot = document.createElement('div'); foot.className = 'btn-row';

    if (target) {
      // exact numbers for the picked (or filtered) hands
      if (!target.combos.length) {
        const help = document.createElement('div'); help.className = 'lk-help';
        help.textContent = target.kind === 'picked'
          ? 'Your filters hide every combo of the picked hands. Clear the filters or pick other hands.'
          : `Your filters leave none of ${who}'s hands.`;
        body.appendChild(help);
      } else {
        const ed = freqEditor(cur.mix);
        const n = target.cells.length;
        const what = target.kind === 'filtered' ? 'FILTERED HANDS'
          : n === 1 ? target.names[0] : `${n} HANDS`;
        const note = document.createElement('div'); note.className = 'lk-help';
        note.textContent = `${target.combos.length} combo${target.combos.length === 1 ? '' : 's'}. ${who}'s other hands stay as they play now.`;
        body.append(ed.cont, ed.sumRow, note);
        const lock = document.createElement('button'); lock.type = 'button'; lock.className = 'btn lk-go';
        lock.textContent = `LOCK ${what}`;
        lock.dataset.tip = 'Make these hands play exactly these numbers at this decision.';
        lock.addEventListener('click', async () => {
          const freqs = readFreqs(ed);
          if (!freqs) return;
          const edits = target.combos.map(c => ({ combo: c.name, freqs }));
          try {
            const out = await this.lockHere({ kind: 'hands', edits }, label);
            for (const c of target.cells) this.rememberLockedCell(c, label);
            toast(`${target.kind === 'filtered' ? 'filtered hands' : handList(target.names, 4)} locked${frozenNote(out)}`);
            done();
          } catch (e) { this.fail(plainLockError(e)); }
        });
        foot.appendChild(lock);
      }
    } else if (whole.reach <= 1e-9) {
      // nothing arrives: there is no range to shift, only single hands to set
      const help = document.createElement('div'); help.className = 'lk-help';
      help.textContent = `None of ${who}'s hands gets here in the solve, so there is no range to shift. Pick hands in the grid to set them one by one.`;
      body.appendChild(help);
    } else {
      const ed = freqEditor(whole.mix);
      body.append(ed.cont, ed.sumRow);
      const fit = this.view.fit;
      if (fit) {
        // a "Least exploitable" lock is steering this decision in the solve
        const st = document.createElement('div');
        st.className = 'lk-help lk-fit';
        const pct = v => Number.isFinite(v) ? `${(v * 100).toFixed(1)}%` : '—';
        st.innerHTML = '<b>Working towards your numbers.</b> ' + acts.map((a, k) =>
          `${a.label} ${pct(fit.achieved[k])} → ${pct(fit.target[k])}`).join(' · ') +
          '. Locked when the solve ends; one Undo removes it.';
        body.appendChild(st);
      }
      // which hands move when the range is pushed onto the numbers
      const methods = [
        ['rake', 'Scale', 'Every hand shifts its mix by the same factor until the range hits your numbers. A hand that never takes an action still never takes it.'],
        ['quick', 'Least EV loss', 'The hands that lose the least by switching do the switching. Instant, but a perfect counter can still punish it.'],
        ['full', 'Least exploitable', 'Finds the way to hit your numbers that gives the other player the least. It starts a re-solve and locks the result when the solve ends.'],
      ];
      if (!methods.some(m => m[0] === this.fitMethod)) {
        let saved = null;
        try { saved = localStorage.getItem('gtopen.fitMethod'); } catch { /* storage off */ }
        // "Least exploitable" starts a solve, so it is never the remembered default
        this.fitMethod = saved === 'quick' ? 'quick' : 'rake';
      }
      const how = document.createElement('div');
      how.className = 'lk-how';
      const cap = document.createElement('span');
      cap.className = 'dim';
      cap.textContent = 'Which hands change:';
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
          this.renderActions(); // the typed numbers are kept (lockDraft)
        });
        seg.appendChild(b);
      }
      how.append(cap, seg);
      body.appendChild(how);
      const lock = document.createElement('button'); lock.type = 'button'; lock.className = 'btn lk-go';
      lock.textContent = this.fitMethod === 'full' ? 'LOCK + RE-SOLVE' : 'LOCK WHOLE RANGE';
      lock.dataset.tip = this.fitMethod === 'full'
        ? 'Start a re-solve that steers the range onto your numbers and locks the result when it ends.'
        : `Make ${who}'s range take each action this often at this decision.`;
      lock.addEventListener('click', async () => {
        const freqs = readFreqs(ed);
        if (!freqs) return;
        try {
          if (this.fitMethod === 'full') {
            const out = await api.fit(this.path, freqs, label, this.keepArg());
            this.forgetLockCells(label); // a tree fit replaces per-hand marks
            this.setLockHistory(out.history); this.noteLockEdit();
            toast(`solving towards your numbers${frozenNote(out)}; locked when the solve ends`);
            document.getElementById('btn-solve-top')?.click();
          } else {
            const out = await this.lockHere({ kind: this.fitMethod === 'quick' ? 'fit' : 'range', freqs }, label);
            toast(`whole range locked${frozenNote(out)}`);
          }
          done();
        } catch (e) { this.fail(e); }
      });
      foot.appendChild(lock);
      if (fit) {
        const cancel = document.createElement('button'); cancel.type = 'button'; cancel.className = 'btn ghost'; cancel.textContent = 'CANCEL';
        cancel.dataset.tip = 'Stop steering this decision. Nothing is locked.';
        cancel.addEventListener('click', async () => {
          try { await api.fitCancel(this.path); toast('cancelled'); this.refresh(); }
          catch (e) { this.fail(e); }
        });
        foot.appendChild(cancel);
      }
    }
    this.appendLockFooter(foot, label);
    body.appendChild(foot);
    el.appendChild(wrap);
  }

  /** What "also keep the earlier play on this line" sends: nothing when the
   *  box is off or has nothing to keep, else the locked player's own earlier
   *  decisions ('own'; every decision on the line against an older server). */
  keepArg() {
    if (!this.freezeLine || this.freezeCount() <= 0) return false;
    return this.keepsOwnOnly() ? 'own' : 'all';
  }

  /** The server can keep only the locked player's earlier decisions. */
  keepsOwnOnly() {
    return (this.serverLevel ?? 0) >= 4;
  }

  /** Lock the current node with `mode`, keeping the earlier decisions on
   *  the line too when that option is on. Returns the server's reply. */
  async lockHere(mode, label) {
    const out = await api.lock(this.path, mode, label, this.keepArg());
    // a whole-range/solved lock recomputes every hand: drop per-cell marks
    if (mode.kind !== 'hands') this.forgetLockCells(label);
    this.setLockHistory(out.history); this.noteLockEdit();
    return out;
  }

  /** True when the current node has a decision before it on the line. */
  hasEarlierDecision() {
    return this.path.some(step => step.type === 'action');
  }

  /** Earlier decisions the "keep earlier play" box would still hold: action
   *  steps on the line that carry no lock yet. Only the acting player's own
   *  ones when the server can tell them apart (see keepsOwnOnly). */
  freezeCount() {
    if (!this.view || !this.pathLabels || !this.hasEarlierDecision()) return 0;
    const own = this.keepsOwnOnly() && this.view.node_type === 'action';
    const hist = this.view.history || [];
    return freezeableAncestors(this.path, this.pathLabels, this.rootBoard(), d => !!this.lockSummary(d),
      i => !own || hist[i]?.player === this.view.player);
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
    for (const [dir, glyph, word, list] of [['undo', '↶', 'Undo', h.undo], ['redo', '↷', 'Redo', h.redo]]) {
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

  /** Shared "lock as solved" + "keep earlier play" controls for the lock box. */
  appendLockFooter(foot, label) {
    const keepN = this.freezeCount();
    if (keepN > 0) {
      const who = this.posLabel(this.view.player);
      const own = this.keepsOwnOnly();
      const line = document.createElement('label');
      line.className = 'chk lk-line';
      line.dataset.tip = own
        ? `Ticked: how ${who} got here stays the way the solve has it, so a re-solve cannot change ${who}'s earlier play to suit this lock. ${this.posLabel(1 - this.view.player)}'s earlier play stays free. Unticked: both may change.`
        : 'Ticked: every earlier decision on this line stays the way the solve has it when you re-solve.';
      const box = document.createElement('input');
      box.type = 'checkbox';
      box.checked = !!this.freezeLine;
      box.addEventListener('change', () => {
        this.freezeLine = box.checked;
        try { localStorage.setItem('gtopen.freezeLine', box.checked ? '1' : '0'); } catch { /* storage off */ }
      });
      line.append(box, document.createTextNode(own
        ? ` also keep ${who}'s ${keepN === 1 ? 'earlier decision' : `${keepN} earlier decisions`} on this line as solved`
        : ` also keep the ${keepN === 1 ? 'earlier decision' : `${keepN} earlier decisions`} on this line as solved`));
      foot.prepend(line);
    }
    const freeze = document.createElement('button');
    freeze.type = 'button';
    freeze.className = 'btn ghost'; freeze.textContent = 'LOCK AS SOLVED';
    freeze.dataset.tip = 'Lock this decision the way the solve plays it now, so it stays put while you change things elsewhere and re-solve.';
    freeze.addEventListener('click', async () => {
      try {
        const out = await this.lockHere({ kind: 'freeze' }, label);
        toast(`locked as solved${frozenNote(out)}`);
        this.lockSel.clear(); this.lockDraft = null;
        this.refresh();
      } catch (e) { this.fail(e); }
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
   *  exploiter acts here, else each hand's gain from the best reply (grey
   *  for none, green for some: never the red-to-green EV scale, where the
   *  lowest value on the grid is red and "nothing to gain" read as a jam). */
  effMode() {
    if (this.mode !== 'exploit') return this.mode;
    return this.exploitReady() && this.exploit.player === this.exploit.exploiter
      ? 'strategy' : 'gain';
  }

  /** In EXPLOIT the grid shows every hand of the player's range, not only
   *  the ones the solve brings here: the best reply with a hand does not
   *  depend on how often that hand arrives, and the hand under review is
   *  often one the solve plays another way earlier on. */
  showsWholeRange(p) {
    return this.mode === 'exploit' && this.exploitReady() && p === this.player;
  }

  /** How much of a hand counts at this node: how often it gets here, or in
   *  EXPLOIT its weight in the starting range (see showsWholeRange). */
  presence(h, p) {
    return this.showsWholeRange(p) ? (h.weight ?? h.reach) : h.reach;
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
        this.renderHandsPanel(); // the combo tiles show the best reply too
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
      b.innerHTML = `<b>EXPLOIT</b> working out ${this.posLabel(this.player)}'s best reply…`;
    } else {
      const e = this.exploit;
      const nm = this.posLabel(e.exploiter);
      const other = this.posLabel(1 - e.exploiter);
      const mine = e.locked && e.player === e.exploiter;
      b.innerHTML = e.avg_gain != null
        ? `<b>EXPLOIT</b> ${nm}'s best reply to ${other} as ${other} plays now: ` +
          `<b>${fmt(e.avg_br_ev)}</b> a hand from here instead of ${fmt(e.avg_cur_ev)} ` +
          `(<b>+${fmt(Math.max(0, e.avg_gain))}</b>).` +
          (mine ? ` ${nm} is locked at this decision, so the lock is what shows.` : '')
        : `<b>EXPLOIT</b> ${nm} never gets here in the solve, so there is no average to show.`;
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
      const reach = this.presence(h, p);
      if (reach <= 1e-9) continue;
      out.push({ reach, ev: h.ev, eq: h.eq, strat: h.strategy,
                 combo: cardToString(a) + cardToString(b) });
    }
    return out;
  }

  cellAgg(i, j, p) {
    // Aggregate hands of player p within a cell class.
    const combos = cellCombos(cellInfo(i, j));
    const hands = this.handsFor(p);
    const idx = this.handIdx[p];
    let reach = 0, weight = 0, ev = 0, evW = 0, eq = 0, eqW = 0, arrives = 0;
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
      const pr = this.presence(h, p);
      present++;
      reach += pr;
      arrives += h.reach;
      weight += h.weight;
      // EV/EQ averages weight by reach x valid (card-removal-adjusted opponent
      // mass, when the server provides it) so aggregates respect blockers
      const w = pr * (h.valid != null ? h.valid : 1);
      if (h.ev != null) { ev += h.ev * w; evW += w; }
      if (h.eq != null) { eq += h.eq * w; eqW += w; }
      if (strat && h.strategy) h.strategy.forEach((s, k) => strat[k] += s * pr);
    }
    if (strat && reach > 1e-12) strat = strat.map(s => s / reach);
    return { present, total: possible, reach, weight, arrives,
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
    const picking = this.canPickHands(); // the hands the lock box is for
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
        // (real arrival, also in EXPLOIT: it tells the rare hands apart)
      }
    }
    // Fill mode: how much of a cell/column to fill for a given per-combo reach.
    //  normalized -> relative to the busiest hand class (best use of space)
    //  range      -> the hand's actual weight/reach out of a full combo
    //  full       -> fill completely (ignore reach), just show the colors
    const wholeRange = this.showsWholeRange(p);
    const fillMode = wholeRange ? 'full' : (this.fillMode || 'normalized');
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
    // EXPLOIT with the other player to act: grey = nothing to gain, greener =
    // more to gain with the best reply from here on
    let gainMax = 0;
    if (effMode === 'gain') {
      hands.forEach((h, hi) => {
        // (not the faded hands: their gain is against a play the solve never settled)
        if (this.presence(h, p) > 1e-9 && h.ev != null && h.reach >= 0.02 * maxReach
            && this.handMatches(p, hi)) gainMax = Math.max(gainMax, h.ev);
      });
    }
    const gainColor = g => {
      if (!(g > 0.005) || gainMax <= 0.005) return '#3d3d3d';
      const t = Math.min(1, g / gainMax);
      return `hsl(130 ${(25 + 40 * t).toFixed(0)}% ${(30 + 16 * t).toFixed(0)}%)`;
    };
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
        // EXPLOIT shows every hand; the ones the solve rarely brings here are faded
        cell.classList.toggle('rare', wholeRange && agg.reach > 1e-9
          && agg.arrives / Math.max(agg.total, 1) < 0.02 * maxReach);
        const isSelected = !!(this.selectedCell && this.selectedCell[0] === i && this.selectedCell[1] === j);
        const isPicked = picking && this.lockSel.has(`${i},${j}`);
        cell.classList.toggle('selected', isSelected && !isPicked);
        cell.classList.toggle('picked', isPicked);
        cell.setAttribute('aria-pressed', isSelected || isPicked ? 'true' : 'false');
        // lock dot: bright on cells a per-hand lock names, dim on every cell a
        // whole-range/solved/fit lock constrains
        const mark = cell.querySelector('.lk-mark');
        if (mark) {
          // the lock is the acting player's: no marks on the other player's hands
          const hand = picking && lockedCells.has(`${i},${j}`);
          const whole = picking && wholeLocked && agg.present > 0 && agg.reach > 1e-9;
          mark.style.display = (hand || whole) ? 'block' : 'none';
          mark.style.background = hand ? '#f5c542' : 'rgba(245,197,66,.55)';
        }
        const intensity = fillH(agg.reach / Math.max(agg.total, 1));
        // a faded hand has no solved play here to compare the best reply with
        const faded = cell.classList.contains('rare');
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
            agg.ev != null && agg.reach > 1e-9 && !faded ? fmt(agg.ev) : '';
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
        } else if (effMode === 'gain') {
          const gainText = agg.ev != null && agg.reach > 1e-9 && !faded ? fmt(agg.ev) : '';
          if (this.comboRows) {
            const list = this.cellCombosData(i, j, p).filter(c => c.ev != null);
            renderCols(bars, fill, sub, list, c => gainColor(faded ? 0 : c.ev), gainText);
          } else {
            renderAgg(bars, fill, sub, agg.ev != null ? gainColor(faded ? 0 : agg.ev) : null,
              intensity, gainText, agg.reach);
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
      const me = this.posLabel(this.player), them = this.posLabel(1 - this.player);
      if (this.effMode() === 'strategy') {
        key.textContent = `EXPLOIT: ${me}'s best play with each hand against ${them} as ${them} plays now, locks included. ` +
          'The number is what it gains over the solve\'s play.';
      } else if (this.view.node_type === 'action') {
        key.innerHTML = `EXPLOIT: <b style="color:var(--ink)">${them} acts here</b>, so there is no ${me} play to show. ` +
          `Click one of ${me}'s boxes in the line above. The number is what ${me}'s best reply gains with that hand from here on ` +
          '(grey = nothing).';
      } else {
        key.textContent = `EXPLOIT: what ${me}'s best reply gains with each hand from here on (grey = nothing).`;
      }
      el.appendChild(key);
      const rare = document.createElement('span');
      rare.className = 'key dim';
      rare.textContent = `Every hand in ${me}'s range is shown. Faded = the solve rarely gets here with it, so it has no gain to show.`;
      el.appendChild(rare);
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
    // the grid can show one player's hands at the other player's decision
    if (this.view.node_type === 'action' && this.view.player !== this.player) {
      const note = document.createElement('span');
      note.className = 'key dim';
      note.textContent = `These are ${this.posLabel(this.player)}'s hands. ${this.posLabel(this.view.player)} acts here.`;
      el.appendChild(note);
    }
  }

  // ----- hands panel (hover-driven) -----

  /** A press on a hand. When the grid shows the hands of the player whose
   *  decision this is, it adds the hand to (or takes it out of) the hands
   *  the lock box is for; the last hand pressed stays pinned in HANDS.
   *  Otherwise it only pins or unpins the hand. */
  selectCell(i, j) {
    const key = `${i},${j}`;
    const same = !!this.selectedCell && this.selectedCell[0] === i && this.selectedCell[1] === j;
    if (this.canPickHands() && this.actorCombos(i, j).length) {
      if (this.lockSel.has(key)) {
        this.lockSel.delete(key);
        if (same) this.selectedCell = null;
      } else {
        this.lockSel.add(key);
        this.selectedCell = [i, j];
      }
    } else {
      this.selectedCell = same ? null : [i, j];
    }
    this.afterPick();
  }

  /** Dragging over the grid: add (or remove) the hand under the pointer. */
  pickCell(i, j, add) {
    const key = `${i},${j}`;
    if (!this.canPickHands() || !this.actorCombos(i, j).length || this.lockSel.has(key) === add) return;
    if (add) { this.lockSel.add(key); this.selectedCell = [i, j]; }
    else this.lockSel.delete(key);
    this.afterPick();
  }

  afterPick() {
    this.renderMatrix();
    this.renderHandsPanel();
    // the lock box follows the picked hands
    if (this.view && this.view.node_type === 'action') this.renderActions();
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

    const d = this.cellHandData(i, j, { reply: eff === 'hands' });
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
  cellHandData(i, j, { reply = false } = {}) {
    const info = cellInfo(i, j);
    const p = this.player;
    // `reply`: in EXPLOIT the combo tiles show the best reply the grid shows
    // (they used to keep the old solve's mix under the best reply's numbers)
    const best = reply && this.showsWholeRange(p);
    const hands = best ? this.handsFor(p) : this.view.players[p].hands;
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
      best,
      // a best reply holds for a combo however rarely it gets here: no dimming
      minReach: best ? 0 : Math.max(1e-9, cellMaxReach * 0.01),
      isActor: this.view.node_type === 'action' && this.view.player === p,
      colors: this.actionColors(),
      acts: this.view.actions || [],
    };
  }

  handTilesHtml({ cand, best, minReach, isActor, colors, acts }, mini = false) {
    // Layout: 2 columns up to 4 combos, 3 columns beyond.
    const cols3 = cand.length > 4;
    const tiles = cand.map(([h, a, b, m]) =>
      this.handTile(h, a, b, isActor, colors, acts, cols3,
        !m || h.reach < minReach, mini, best));
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
    const d = this.cellHandData(i, j, { reply: true });
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
    // anything else with a bracket (a raise) keeps its amount: "RAISE 12"
    return shortAction(act.label).toUpperCase();
  }

  handTile(h, a, b, isActor, colors, acts, compact, dimmed, mini = false, best = false) {
    const name =
      `<span class="suit-${SUITS[suit(a)]}">${RANKS[rank(a)]}${SUIT_GLYPH[SUITS[suit(a)]]}</span>` +
      `<span class="suit-${SUITS[suit(b)]}">${RANKS[rank(b)]}${SUIT_GLYPH[SUITS[suit(b)]]}</span>`;
    const meta = best ? 'best reply' : (h.eq != null ? `${(h.eq * 100).toFixed(0)}% eq` : '');
    let body;
    let heads = '';
    if (isActor && h.strategy) {
      // Horizontal split, aggressive actions on the left; over it a small
      // table, one row per action: name, how often, EV. The two column
      // heads sit right above the numbers (in the popup: in the tile's top
      // line, which is just as close there).
      heads = `<span class="hl-f" data-tip="How often this hand takes each action.">how often</span>` +
        `<span class="hl-ev" data-tip="What each action is worth to this hand, in the same units as the pot.">EV</span>`;
      const segs = [];
      const lines = [];
      const ev = k => (h.evs && h.evs[k] != null ? fmt(h.evs[k]) : '—');
      const line = (k, f, off) =>
        `<div class="hand-line${off ? ' off' : ''}"><span class="hl-lab">${mini ? this.miniLabel(acts[k]) : acts[k].label}</span>` +
        `<span class="hl-f">${freqPct(f)}</span>` +
        `<span class="hl-ev">${ev(k)}</span></div>`;
      for (let k = acts.length - 1; k >= 0; k--) {
        const f = h.strategy[k];
        if (f < 0.001) {
          // a best reply is one action: still list what the others are worth
          if (best) lines.push(line(k, 0, true));
          continue;
        }
        segs.push(
          `<div style="flex:${f.toFixed(4)};background:${colors[k]}" ` +
          `data-tip="${acts[k].label}: ${freqPct(f)} of the time · EV ${ev(k)}"></div>`);
        lines.push(line(k, f, false));
      }
      const headRow = mini ? '' : `<div class="hand-line hl-head"><span class="hl-lab"></span>${heads}</div>`;
      body = `<div class="htb-h${compact ? ' short' : ''}">` +
        `<div class="hseg-row">${segs.join('')}</div>` +
        `<div class="hand-lines">${headRow}${lines.join('')}</div></div>`;
    } else if (best) {
      body = `<div class="htb flat"><span>EV <b>${h.br_ev != null ? fmt(h.br_ev) : '—'}</b></span>` +
        `<span>gain <b>${h.gain != null ? fmt(h.gain) : '—'}</b></span></div>`;
    } else {
      body = `<div class="htb flat"><span>EV <b>${h.ev != null ? fmt(h.ev) : '—'}</b></span>` +
        `<span>EQ <b>${h.eq != null ? (h.eq * 100).toFixed(1) + '%' : '—'}</b></span></div>`;
    }
    const meta_html = mini
      ? (heads ? `<span class="hl-head">${heads}</span>` : '')
      : `<span class="meta">${meta}</span>`;
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
    // the lock box can be for "the hands your filters show"
    if (this.view?.node_type === 'action') this.renderActions();
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

/** A refused per-hand lock, in plain words. The solver treats suits a board
 *  cannot tell apart as one, so two such combos must be locked alike. */
export function plainLockError(e) {
  const m = /([2-9TJQKA][cdhs][2-9TJQKA][cdhs]) is mirrored by ([2-9TJQKA][cdhs][2-9TJQKA][cdhs])/.exec(e?.message || '');
  if (!m) return e;
  return new Error(`On this board ${m[1]} and ${m[2]} are the same hand apart from the suits, so they have to be locked alike. ` +
    'Include both, or drop the suit filter.');
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

/** How often an action is taken, for the combo tiles: "27.5%", and plain
 *  "100%" / "0%" at the ends (no "100.0%"). */
export function freqPct(f) {
  const p = (f || 0) * 100;
  if (p >= 99.95) return '100%';
  if (p < 0.05) return '0%';
  return `${p.toFixed(1)}%`;
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
