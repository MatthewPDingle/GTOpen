// RANGE LAB REFERENCE — the canonical charts from the Range Lab trainer, shown
// beside the Preflop Lab's own solve. The charts are private data:
// the server reads them from local folders (cache/rangelab/ or ../Range Lab/)
// and nothing here bundles them. "Follow the line" picks the chart whose
// action history matches the Preflop Lab line (fold / check / call / raise,
// sizes ignored), then the nearest open size and stack depth.

import { api } from './api.js';
import { cellInfo } from './cards.js';

const COLORS = { fold: '#4a78c8', check: '#5ca75f', call: '#5ca75f' };
const RAISE_SHADES = ['#e8484c', '#c24345', '#a23a3c', '#7c3134'];
const TOKEN = { fold: 'F', check: 'X', call: 'C', raise: 'R', jam: 'R' };

/** Kind-only tokens of the actions taken before the current decision. */
export function lineTokens(history) {
  return (history || []).slice(0, -1)
    .filter(h => h.kind === 'action' && h.chosen != null && h.actions?.[h.chosen])
    .map(h => TOKEN[h.actions[h.chosen].kind] || '?');
}

/** What the matcher needs from a Preflop Lab action node and its config. */
export function matchContext(view, cfg) {
  if (!view || view.kind !== 'action' || !cfg) return null;
  const taken = (view.history || []).slice(0, -1)
    .filter(h => h.kind === 'action' && h.chosen != null)
    .map(h => h.actions[h.chosen]);
  const firstRaise = taken.find(a => a.kind === 'raise' || a.kind === 'jam');
  const opens = (cfg.open_raises || []).filter(Number.isFinite);
  return {
    players: view.positions.length,
    stack: cfg.stack,
    straddle: !!cfg.utg_straddle,
    ante: cfg.ante || 0,
    line: lineTokens(view.history),
    open_to: firstRaise ? firstRaise.to : (opens.length ? Math.min(...opens) : null),
    actor_pos: view.actor_pos,
  };
}

/** The Range Lab game that best fits the Preflop Lab table. */
export function defaultGame(ctx, games) {
  const fits = (games || []).filter(g => !ctx || g.players === ctx.players);
  if (!fits.length) return null;
  const pick = tags => tags.map(t => fits.find(g => g.tag === t)).find(Boolean);
  if (ctx?.straddle) return pick(['str']) || null;
  if (ctx?.ante > 0) return pick(['cev9', 'icm8']) || fits[0];
  return pick(['reg']) || fits.find(g => g.tag !== 'str') || fits[0];
}

export function actionColors(actions) {
  const raises = actions.filter(a => a.kind === 'raise').length;
  let r = 0;
  return actions.map(a => {
    if (COLORS[a.kind]) return COLORS[a.kind];
    if (a.kind === 'jam') return RAISE_SHADES[3];
    const k = raises <= 1 ? 0 : Math.min(2, Math.round((r / (raises - 1)) * 2));
    r += 1;
    return RAISE_SHADES[k];
  });
}

const esc = s => String(s).replace(/[&<>"']/g, c =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const num = x => String(Number(Number(x).toFixed(2)));

export function initRangeLabRef(host) {
  host.innerHTML = `
    <details class="rl-ref" open>
      <summary>RANGE LAB REFERENCE <span class="dim">· canonical charts from Range Lab</span></summary>
      <div class="rl-controls">
        <label class="chk" data-tip="Show the chart for the decision you are viewing in the ribbon: same action sequence (fold, check, call, raise), then the nearest open size and stack depth. Untick to browse every chart.">
          <input type="checkbox" class="rl-follow" checked> Follow the line</label>
        <label>Game <select class="rl-game"></select></label>
        <label>Open / stage <select class="rl-variant"></select></label>
        <label>Stack <select class="rl-depth"></select></label>
        <label class="rl-spot-wrap">Spot <select class="rl-spot"></select></label>
      </div>
      <div class="rl-title"></div>
      <div class="rl-note dim"></div>
      <div class="matrix browse rl-grid hidden"></div>
      <div class="legend rl-legend"></div>
    </details>`;
  const q = sel => host.querySelector(sel);
  const el = {
    follow: q('.rl-follow'), game: q('.rl-game'), variant: q('.rl-variant'), depth: q('.rl-depth'),
    spot: q('.rl-spot'), spotWrap: q('.rl-spot-wrap'), title: q('.rl-title'), note: q('.rl-note'),
    grid: q('.rl-grid'), legend: q('.rl-legend'),
  };
  const cells = [];
  for (let i = 0; i < 13; i++) {
    for (let j = 0; j < 13; j++) {
      const cell = document.createElement('div');
      cell.className = 'cell';
      cell.innerHTML = `<div class="bars"></div><div class="fill"></div><div class="tag">${cellInfo(i, j).label}</div><div class="sub"></div>`;
      el.grid.appendChild(cell);
      cells.push(cell);
    }
  }

  const S = { summary: null, ctx: null, gameChosen: false, seq: 0, spot: null };
  const game = () => S.summary?.games.find(g => g.tag === el.game.value) || null;
  const options = (sel, list, value) => {
    sel.innerHTML = list.map(o => `<option value="${esc(o.value)}">${esc(o.label)}</option>`).join('');
    if (value != null && list.some(o => String(o.value) === String(value))) sel.value = String(value);
  };

  function clear(message) {
    S.spot = null;
    el.title.textContent = '';
    el.note.innerHTML = message || '';
    el.grid.classList.add('hidden');
    el.legend.innerHTML = '';
  }

  function fillDepths(keepDepth) {
    const v = game()?.variants.find(x => x.key === el.variant.value);
    const depths = v?.depths || [];
    // keep the stack when this open size has it, else the nearest one
    const near = keepDepth == null || !depths.length ? keepDepth
      : depths.reduce((a, b) => Math.abs(b - keepDepth) < Math.abs(a - keepDepth) ? b : a);
    options(el.depth, depths.map(d => ({ value: d, label: `${num(d)} bb` })), near);
  }

  function fillGameAxes(keepVariant, keepDepth) {
    const g = game();
    options(el.variant, (g?.variants || []).map(v => ({ value: v.key, label: v.label })), keepVariant);
    fillDepths(keepDepth);
  }

  function syncMode() {
    const follow = el.follow.checked;
    el.variant.disabled = follow;
    el.depth.disabled = follow;
    el.spotWrap.classList.toggle('hidden', follow);
  }

  async function load() {
    try { S.summary = await api.rangeLab(); } catch (e) { clear(`Range Lab charts unavailable: ${esc(e.message)}`); return; }
    const sm = S.summary;
    if (!sm.total) {
      const bad = sm.files.filter(f => f.error).map(f => `${esc(f.path)} (${esc(f.error)})`);
      clear(`No Range Lab data found. Put <code>data.js</code> and <code>cash-data.js</code> (or crawl JSON) in ` +
        sm.dirs.map(d => `<code>${esc(d)}</code>`).join(' or ') +
        ` (or set <code>GTOPEN_RANGELAB_DIR</code>) and reopen this panel. The charts stay on this machine; they are never committed.` +
        (bad.length ? `<br>Skipped: ${bad.join('; ')}` : ''));
      return;
    }
    options(el.game, sm.games.map(g => ({ value: g.tag, label: `${g.label} (${g.spots.toLocaleString()} charts)` })));
    const g = defaultGame(S.ctx, sm.games);
    if (g) el.game.value = g.tag;
    fillGameAxes();
    syncMode();
    update(S.ctx);
  }

  async function show(promise, context) {
    const seq = ++S.seq;
    let spot;
    try { spot = await promise; } catch (e) { if (seq === S.seq) clear(esc(e.message)); return; }
    if (seq !== S.seq) return; // superseded by a newer request
    if (!spot) { clear(context); return; }
    render(spot);
  }

  async function follow() {
    const g = game();
    if (!S.ctx) { clear('Pick a decision point in the ribbon above to see the matching chart, or untick “Follow the line” to browse.'); return; }
    if (!g || g.players !== S.ctx.players) {
      clear(`Range Lab has no ${S.ctx.players}-handed charts in this game. Its charts are ` +
        S.summary.games.map(x => `${esc(x.label)} (${x.players}-handed)`).join(', ') + '.');
      return;
    }
    const req = { tag: g.tag, players: S.ctx.players, line: S.ctx.line, stack: S.ctx.stack };
    if (S.ctx.open_to != null) req.open_to = S.ctx.open_to;
    await show(api.rangeLabMatch(req).then(r => r.spot),
      `No ${esc(g.label)} chart for this line. Range Lab covers unopened pots, single raises (with one caller for squeezes), 3-bets and 4-bets, and the big blind against a small-blind limp; limped and multi-caller pots have no chart.`);
  }

  async function browse(keepSpot) {
    const g = game();
    if (!g) return;
    let list;
    try { list = await api.rangeLabSituations(g.tag, el.variant.value, Number(el.depth.value)); } catch (e) { clear(esc(e.message)); return; }
    const groups = new Map();
    list.forEach(s => { if (!groups.has(s.family_label)) groups.set(s.family_label, []); groups.get(s.family_label).push(s); });
    el.spot.innerHTML = [...groups].map(([fam, items]) => `<optgroup label="${esc(fam)}">` +
      items.map(s => `<option value="${s.id}">${esc(s.label)}${s.hist ? ` · ${esc(s.hist)}` : ''}</option>`).join('') +
      '</optgroup>').join('');
    const same = keepSpot && list.find(s => s.family_label === keepSpot.family_label && s.label === keepSpot.label);
    if (same) el.spot.value = String(same.id);
    if (!list.length) { clear('No charts at this open size and stack.'); return; }
    await show(api.rangeLabSpot(Number(el.spot.value)), 'Chart not found.');
  }

  function update(ctx) {
    S.ctx = ctx;
    if (!S.summary?.total) return;
    if (!S.gameChosen) {
      const g = defaultGame(ctx, S.summary.games);
      if (g && g.tag !== el.game.value) { el.game.value = g.tag; fillGameAxes(); }
    }
    if (el.follow.checked) follow();
    else if (!S.spot) browse();
  }

  function render(spot) {
    S.spot = spot;
    if (el.follow.checked) {
      fillGameAxes(spot.variant, spot.depth);
    }
    const colors = actionColors(spot.actions);
    const na = spot.actions.length;
    el.title.textContent = `${spot.label} · ${spot.family_label} · ${spot.variant_label} · ${num(spot.depth)} bb`;
    const notes = [`${esc(spot.game)}${spot.hist ? ` · line <span class="mono">${esc(spot.hist)}</span>` : ' · first to act'}`];
    if (el.follow.checked && S.ctx) {
      const off = [];
      if (Math.abs(spot.depth - S.ctx.stack) > 1e-6) off.push(`stack ${num(spot.depth)} bb vs your ${num(S.ctx.stack)} bb`);
      const ob = Number.parseFloat(spot.variant);
      if (S.ctx.open_to != null && Number.isFinite(ob) && Math.abs(ob - S.ctx.open_to) > 1e-6) off.push(`open ${num(ob)} bb vs your ${num(S.ctx.open_to)} bb`);
      if (off.length) notes.push(`Closest chart: ${off.join(', ')}.`);
      notes.push("Range Lab's game (open sizes, rake, stacks) differs from your solve; compare shapes, not exact frequencies.");
    }
    el.note.innerHTML = notes.join('<br>');
    el.grid.classList.remove('hidden');
    for (let i = 0; i < 13; i++) {
      for (let j = 0; j < 13; j++) {
        const cell = cells[i * 13 + j];
        const idx = (12 - i) * 13 + (12 - j);
        const reach = spot.reach ? spot.reach[idx] : 1;
        const segs = [];
        let cont = 0;
        for (let a = na - 1; a >= 0; a--) {
          const f = spot.strategy[a * 169 + idx];
          if (spot.actions[a].kind !== 'fold') cont += f;
          if (f > 0.001) segs.push(`<div style="width:${(f * 100).toFixed(1)}%;background:${colors[a]}"></div>`);
        }
        const bars = cell.querySelector('.bars');
        bars.innerHTML = segs.join('');
        bars.style.height = `${(Math.min(1, reach) * 100).toFixed(1)}%`;
        bars.style.opacity = reach > 1e-9 ? 1 : 0;
        cell.classList.toggle('empty', reach < 0.002);
        const lab = cellInfo(i, j).label;
        const pct = a => `${(spot.strategy[a * 169 + idx] * 100).toFixed(1)}%`;
        const loss = a => spot.ev_loss[a * 169 + idx];
        const lossText = a => loss(a) >= 0.005 ? ` (−${loss(a).toFixed(2)} bb)` : '';
        const inRange = spot.reach && reach < 0.995 ? `${(reach * 100).toFixed(0)}% of combos still in range` : '';
        if (reach < 0.002) {
          cell.dataset.tip = `${lab} — ${spot.hero_pos} almost never holds this here`;
          cell.dataset.tipHtml = '';
        } else {
          cell.dataset.tip = lab + (inRange ? ` — ${inRange}` : '') + '\n' +
            spot.actions.map((a, k) => `${a.label}  ${pct(k)}${lossText(k)}`).join('\n');
          cell.dataset.tipHtml = `<b>${lab}</b>` + (inRange ? ` <span class="dim">${inRange}</span>` : '') +
            `<div class="tip-rows">` + spot.actions.map((a, k) =>
              `<span>${esc(a.label)}</span><span>${pct(k)}${esc(lossText(k))}</span>`).join('') +
            `</div><div class="dim">EV loss vs the best action in brackets</div>`;
        }
        const mixed = reach >= 0.002 && cont >= 0.03 && cont <= 0.97;
        cell.querySelector('.sub').textContent = mixed ? `${Math.round(cont * 100)}%` : '';
      }
    }
    el.legend.innerHTML =
      `<span class="key dim">${esc(spot.hero_pos)}'s chart:</span>` +
      [...spot.actions.keys()].reverse().map(k =>
        `<span class="key"><i style="background:${colors[k]}"></i>${esc(spot.actions[k].label)} ${(spot.actions[k].freq * 100).toFixed(1)}%</span>`).join('') +
      `<span class="key dim">· bar height = share of combos still in range · number = continue frequency of a mixed hand</span>`;
  }

  el.follow.addEventListener('change', () => {
    syncMode();
    if (el.follow.checked) follow(); else browse(S.spot);
  });
  el.game.addEventListener('change', () => {
    S.gameChosen = true;
    fillGameAxes(S.spot?.variant, S.spot?.depth);
    if (el.follow.checked) follow(); else browse(S.spot);
  });
  el.variant.addEventListener('change', () => { fillDepths(Number(el.depth.value)); browse(S.spot); });
  el.depth.addEventListener('change', () => browse(S.spot));
  el.spot.addEventListener('change', () => show(api.rangeLabSpot(Number(el.spot.value)), 'Chart not found.'));
  // Reopening the panel rescans the folders (new or changed data files).
  q('details').addEventListener('toggle', e => { if (e.target.open && !S.summary?.total) load(); });

  load();
  return { update };
}
