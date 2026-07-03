// PREFLOP LAB — UI for the multiway preflop solver (equity-model postflop).
// Build a game (any limps/sizes/players), solve it, walk the action tree with
// a GTO Wizard-style ribbon, and export any heads-up flop node straight into
// the postflop solver's SETUP.

import { api } from './api.js';

const COLORS = { fold: '#4a78c8', check: '#5ca75f', call: '#5ca75f' };
const RAISE_SHADES = ['#e8484c', '#c73e55', '#a4335f', '#7d3ca3'];
const RANKS_DESC = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2'];

function positionsFor(nPlayers) {
  const all = ['UTG', 'UTG1', 'MP', 'LJ', 'HJ', 'CO', 'BTN', 'SB', 'BB'];
  if (nPlayers === 2) return ['SB', 'BB']; // HU: SB is the button, acts first pre
  const nonBlinds = all.slice(0, 7).slice(7 - (nPlayers - 2));
  return [...nonBlinds, 'SB', 'BB'];
}

const PRESETS = [
  {
    name: 'HU 10bb push/fold',
    players: 2, stack: 10, opens: '', mult: '', maxRaises: 1,
    limp: false, allin: true, ante: 0, rakePct: 0, rakeCap: 0,
  },
  {
    name: 'HU 25bb: limp, raise, jam',
    players: 2, stack: 25, opens: '2,2.5', mult: '3', maxRaises: 3,
    limp: true, allin: true, ante: 0, rakePct: 0, rakeCap: 0,
  },
  {
    name: '6-max 100bb, 2.5x open (no limps)',
    players: 6, stack: 100, opens: '2.5', mult: '3', maxRaises: 4,
    limp: false, allin: false, ante: 0, rakePct: 0, rakeCap: 0,
  },
  {
    name: '6-max 100bb low-stakes: limps + 5% rake',
    players: 6, stack: 100, opens: '2.5,4', mult: '3', maxRaises: 3,
    limp: true, allin: false, ante: 0, rakePct: 5, rakeCap: 3,
  },
];

export function initPreflopLab({ els, onExport, toast }) {
  const S = {
    built: false,
    path: [],       // action indices from the root
    line: [],       // [{pos, label, kind}] for the ribbon
    view: null,
    polling: null,
    positions: [],
  };

  // ----- config -----
  PRESETS.forEach((p, i) => {
    const o = document.createElement('option');
    o.value = i;
    o.textContent = p.name;
    els.preset.appendChild(o);
  });
  const applyPreset = (p) => {
    els.players.value = p.players;
    els.stack.value = p.stack;
    els.opens.value = p.opens;
    els.mult.value = p.mult;
    els.maxRaises.value = p.maxRaises;
    els.limp.checked = p.limp;
    els.allin.checked = p.allin;
    els.ante.value = p.ante;
    els.rakePct.value = p.rakePct;
    els.rakeCap.value = p.rakeCap;
  };
  els.preset.addEventListener('change', () => applyPreset(PRESETS[+els.preset.value]));
  applyPreset(PRESETS[0]);

  function config() {
    const n = +els.players.value;
    const positions = positionsFor(n);
    const posts = positions.map(p => (p === 'SB' ? 0.5 : p === 'BB' ? 1.0 : 0.0));
    const nums = s => s.split(',').map(x => parseFloat(x)).filter(x => x > 0);
    return {
      positions,
      stack: +els.stack.value || 100,
      posts,
      ante: +els.ante.value || 0,
      limp: els.limp.checked,
      open_raises: nums(els.opens.value),
      raise_mults: nums(els.mult.value),
      max_raises: +els.maxRaises.value || 1,
      add_allin: els.allin.checked,
      rake_pct: +els.rakePct.value || 0,
      rake_cap: +els.rakeCap.value || 0,
      no_flop_no_drop: true,
      realization: 'static',
    };
  }

  // ----- build / solve -----
  els.build.addEventListener('click', async () => {
    els.build.disabled = true;
    els.buildInfo.textContent = 'building… (first build computes the equity table, ~1 min)';
    try {
      const cfg = config();
      const info = await api.pfBuild(cfg);
      S.built = true;
      S.positions = cfg.positions;
      S.path = [];
      S.line = [];
      els.buildInfo.textContent =
        `${info.nodes.toLocaleString()} nodes · ${info.action_nodes.toLocaleString()} decision points · ${info.arena_mb.toFixed(0)} MB`;
      toast('preflop game built — SOLVE it');
      refresh();
      startPolling();
    } catch (e) { toast(e.message, true); els.buildInfo.textContent = ''; }
    els.build.disabled = false;
  });

  els.solve.addEventListener('click', async () => {
    if (!S.built) return toast('build a game first', true);
    try {
      await api.pfSolve({ iterations: 3000, check_every: 50, target_gap: 0.005 });
      startPolling();
    } catch (e) { toast(e.message, true); }
  });
  els.stop.addEventListener('click', () => api.pfStop().catch(() => {}));

  function startPolling() {
    if (S.polling) clearInterval(S.polling);
    S.polling = setInterval(poll, 1000);
    poll();
  }
  let lastIter = -1;
  async function poll() {
    let st;
    try { st = await api.pfStatus(); } catch { return; }
    if (!st.state) return;
    const gaps = st.gaps && st.gaps.length
      ? ` · BR gap ${st.gap_total.toFixed(4)} bb (${st.gaps.map(g => g.toFixed(3)).join(' / ')})`
      : '';
    els.status.textContent = `${st.state} · iter ${st.iteration}${gaps}`;
    els.solve.classList.toggle('hidden', st.state === 'running');
    els.stop.classList.toggle('hidden', st.state !== 'running');
    if (st.iteration !== lastIter && S.built) {
      lastIter = st.iteration;
      refresh(); // strategies moved: repaint current node
    }
    if (st.state !== 'running' && S.polling && st.iteration === lastIter) {
      clearInterval(S.polling);
      S.polling = null;
    }
  }

  // ----- node navigation / rendering -----
  async function refresh() {
    if (!S.built) return;
    try {
      S.view = await api.pfNode(S.path);
    } catch (e) { toast(e.message, true); return; }
    renderRibbon();
    renderNode();
  }

  function jumpTo(depth) {
    S.path = S.path.slice(0, depth);
    S.line = S.line.slice(0, depth);
    refresh();
  }

  function renderRibbon() {
    const el = els.ribbon;
    el.innerHTML = '';
    const root = document.createElement('button');
    root.className = 'pfl-crumb' + (S.path.length === 0 ? ' cur' : '');
    root.textContent = '⟲ START';
    root.dataset.tip = 'Start of the hand, before any action. The green outline marks the point you are viewing — click any step to jump back to it.';
    root.addEventListener('click', () => jumpTo(0));
    el.appendChild(root);
    S.line.forEach((step, k) => {
      const b = document.createElement('button');
      b.className = 'pfl-crumb' + (k === S.line.length - 1 ? ' cur' : '');
      b.innerHTML = `<b>${step.pos}</b> ${step.label}`;
      b.style.borderBottomColor = step.color || 'transparent';
      b.dataset.tip = `${step.pos} ${step.label} — click to view the moment just after this action.`;
      b.addEventListener('click', () => jumpTo(k + 1));
      el.appendChild(b);
    });
  }

  function actionColors(actions) {
    let r = 0;
    return actions.map(a => {
      if (COLORS[a.kind]) return COLORS[a.kind];
      const c = RAISE_SHADES[Math.min(r, RAISE_SHADES.length - 1)];
      r += 1;
      return a.kind === 'jam' ? RAISE_SHADES[3] : c;
    });
  }

  function renderNode() {
    const v = S.view;
    const el = els.actions;
    el.innerHTML = '';
    els.exportBtn.classList.add('hidden');

    // seats strip: who's live, what they've put in
    els.seats.innerHTML = v.positions.map((p, i) => {
      const dead = !v.live[i];
      const cur = v.kind === 'action' && v.actor === i;
      return `<span class="pfl-seat${dead ? ' dead' : ''}${cur ? ' cur' : ''}">${p} <small>${v.invested[i].toFixed(1)}</small></span>`;
    }).join('');
    els.pot.textContent = `pot ${v.pot.toFixed(1)} bb${v.spr != null ? ` · SPR ${v.spr.toFixed(1)}` : ''}`;

    if (v.kind === 'action') {
      const colors = actionColors(v.actions);
      // headline: who acts, and what (if anything) they're facing
      const lastAggr = [...S.line].reverse().find(s => s.kind === 'raise' || s.kind === 'jam');
      const facing = lastAggr && lastAggr.pos !== v.actor_pos
        ? ` — facing ${lastAggr.pos}'s ${lastAggr.label}`
        : lastAggr && lastAggr.pos === v.actor_pos
          ? '' // their own raise came back around (someone called/limped behind)
          : S.line.length ? ' — unraised pot' : ' — first to act';
      els.nodeTitle.textContent = `${v.actor_pos} to act${facing}`;
      v.actions.forEach((a, k) => {
        const b = document.createElement('button');
        b.className = 'pfl-act';
        b.style.background = colors[k];
        b.innerHTML = `${a.label} <b>${(a.freq * 100).toFixed(1)}%</b>`;
        b.addEventListener('click', () => {
          S.path.push(k);
          S.line.push({ pos: v.actor_pos, label: a.label, kind: a.kind, color: colors[k] });
          refresh();
        });
        el.appendChild(b);
      });
      renderGrid(v, colors);
      renderLegend(v, colors);
      els.gridCap.innerHTML =
        `Grid = <b>${v.actor_pos}</b>'s play with every starting hand AT THIS POINT. ` +
        `Bar colors = how often the hand takes each action; <b>dim cells</b> = hands ` +
        `${v.actor_pos} rarely still holds here, filtered out by its own earlier actions ` +
        `(hover a cell for exact numbers).`;
    } else if (v.kind === 'fold_win') {
      const w = v.positions[v.live.findIndex(x => x)];
      els.nodeTitle.textContent = `everyone folded — ${w} takes ${v.pot.toFixed(1)} bb`;
      els.grid.innerHTML = '';
      els.legend.innerHTML = '';
      els.gridCap.innerHTML = '';
    } else {
      const live = v.positions.filter((_, i) => v.live[i]);
      els.nodeTitle.textContent =
        `FLOP: ${live.join(' vs ')} · pot ${v.pot.toFixed(1)} bb` +
        (v.exportable ? '' : ` (${live.length}-way — postflop solver is heads-up only)`);
      els.grid.innerHTML = '';
      els.legend.innerHTML = '';
      els.gridCap.innerHTML = '';
      if (v.exportable) {
        els.exportBtn.classList.remove('hidden');
      }
    }
  }

  els.exportBtn.addEventListener('click', async () => {
    try {
      const ex = await api.pfExport(S.path);
      const lineText = S.line.map(s => `${s.pos} ${s.label}`).join(' · ') || 'root';
      onExport(ex, lineText);
    } catch (e) { toast(e.message, true); }
  });

  function renderGrid(v, colors) {
    const na = v.actions.length;
    const cells = [];
    for (let i = 0; i < 13; i++) {
      for (let j = 0; j < 13; j++) {
        const idx = (12 - i) * 13 + (12 - j);
        const lab = i <= j
          ? RANKS_DESC[i] + RANKS_DESC[j] + (i === j ? '' : 's')
          : RANKS_DESC[j] + RANKS_DESC[i] + 'o';
        const reach = v.reach ? v.reach[idx] : 1;
        const segs = [];
        for (let a = 0; a < na; a++) {
          const f = v.strategy[a * 169 + idx];
          if (f > 0.001) {
            segs.push(`<i style="width:${(f * 100).toFixed(1)}%;background:${colors[a]}"></i>`);
          }
        }
        const dim = reach < 0.005;
        cells.push(
          `<div class="pfl-cell${dim ? ' dim' : ''}" data-tip="${lab}: ` +
          v.actions.map((a, k) => `${a.label} ${(v.strategy[k * 169 + idx] * 100).toFixed(0)}%`).join(' · ') +
          `${reach < 1 ? ` · ${(reach * 100).toFixed(0)}% of combos reach` : ''}">` +
          `<span class="pfl-bars" style="opacity:${(0.25 + 0.75 * reach).toFixed(2)}">${segs.join('')}</span>` +
          `<span class="pfl-lab">${lab}</span></div>`
        );
      }
    }
    els.grid.innerHTML = cells.join('');
  }

  function renderLegend(v, colors) {
    els.legend.innerHTML = v.actions.map((a, k) =>
      `<span class="key"><i style="background:${colors[k]}"></i>${a.label}</span>`).join('');
  }

  return { refresh };
}
