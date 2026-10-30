// 3-WAY tab: build, solve and browse three-player postflop spots
// (/api/mw/*). Self-contained so the heads-up screens are untouched.

import { toast } from './api.js';
import { cardChip } from './browse.js';
import { cellInfo } from './cards.js';

const $ = id => document.getElementById(id);

async function req(method, url, body) {
  const opts = { method, headers: {} };
  if (body !== undefined) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(url, opts);
  if (!res.ok) throw new Error((await res.text()) || `${res.status}`);
  return res.json();
}

const DEFAULT_PLAYERS = [
  { name: 'BB', stack: 975, range: '22-QQ,A2s-AJs,K5s-KJs,Q8s-QJs,J8s+,T7s+,96s+,86s+,75s+,64s+,54s,A8o-AJo,KTo+,QTo+,JTo' },
  { name: 'CO', stack: 975, range: '22-JJ,A2s-AJs,K9s+,Q9s+,J9s+,T8s+,97s+,87s,76s,65s,ATo-AJo,KJo+,QJo' },
  { name: 'BTN', stack: 975, range: '22-QQ,A2s-AQs,K7s+,Q8s+,J8s+,T8s+,97s+,86s+,75s+,65s,54s,A9o-AQo,KTo+,QTo+,JTo' },
];

const ACTION_COLORS = { fold: '#4a78c8', check: '#5ca75f', call: '#5ca75f' };
function actionColor(a, pot) {
  if (a.kind === 'bet' || a.kind === 'raise') {
    const pct = pot > 0 ? (a.amount / pot) * 100 : 100;
    if (pct <= 40) return '#e8484c';
    if (pct <= 80) return '#c24345';
    if (pct <= 135) return '#a23a3c';
    return '#7c3134';
  }
  return ACTION_COLORS[a.kind] || '#888';
}

const S = {
  names: DEFAULT_PLAYERS.map(p => p.name),
  path: [],      // steps sent to the server (action index or card string)
  line: [],      // display labels for each step
  view: null,
  polling: null,
  built: false,
};

function fmt(x, d = 1) {
  if (x == null || !isFinite(x)) return '—';
  return Math.abs(x - Math.round(x)) < 1e-6 ? String(Math.round(x)) : x.toFixed(d);
}
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);

// ---------------------------------------------------------------- setup ---

function renderPlayers() {
  const box = $('mw-players');
  box.innerHTML = '';
  DEFAULT_PLAYERS.forEach((p, i) => {
    const d = document.createElement('div');
    d.className = 'mw-player';
    d.innerHTML = `
      <div class="mw-player-head">
        <span class="setup-step">P${i + 1}</span>
        <input type="text" class="mw-name" id="mw-name-${i}" value="${esc(p.name)}" aria-label="P${i + 1} position">
        <span class="dim">${i === 0 ? 'acts first' : i === 2 ? 'acts last' : 'acts second'}</span>
        <label class="mw-stack">stack <input type="number" id="mw-stack-${i}" value="${p.stack}" min="1"></label>
      </div>
      <textarea id="mw-range-${i}" spellcheck="false" aria-label="P${i + 1} range">${esc(p.range)}</textarea>`;
    box.appendChild(d);
  });
}

function spotRequest() {
  const sizes = [0, 1, 2].map(k => ({ bet: $(`mw-bet-${k}`).value.trim(), raise: $(`mw-raise-${k}`).value.trim() }));
  return {
    board: $('mw-board').value.replace(/[\s,]/g, ''),
    ranges: [0, 1, 2].map(i => $(`mw-range-${i}`).value.trim()),
    starting_pot: Number($('mw-pot').value),
    stacks: [0, 1, 2].map(i => Number($(`mw-stack-${i}`).value)),
    sizes,
    rake_pct: Number($('mw-rake').value) || 0,
    rake_cap: Number($('mw-rakecap').value) || 0,
    max_raises: Number($('mw-maxraises').value),
    allin_threshold: Number($('mw-allinthr').value) || 85,
    add_allin: $('mw-addallin').checked,
  };
}

function treeText(t) {
  if (!t) return '';
  let gpu = '';
  if (t.gpu_mb > 0) {
    gpu = ` · GPU est. ${fmt(t.gpu_mb / 1000, 2)} GB`;
    if (t.gpu_min_mb > 0 && t.gpu_min_mb < t.gpu_mb * 0.95) gpu += ` (fits in ${fmt(t.gpu_min_mb / 1000, 2)} GB)`;
  }
  return `${t.nodes.toLocaleString()} nodes · ${t.action_nodes.toLocaleString()} decisions · ` +
    `RAM ${fmt(t.arena_mb_compressed / 1000, 2)} GB${gpu} · hands ${t.hands.join('/')}`;
}

async function build() {
  const btn = $('mw-build');
  btn.classList.add('busy');
  $('mw-build-info').textContent = 'building…';
  try {
    S.names = [0, 1, 2].map(i => $(`mw-name-${i}`).value.trim() || `P${i + 1}`);
    const info = await req('POST', '/api/mw/spot', spotRequest());
    $('mw-build-info').textContent = treeText(info);
    S.built = true;
    resetBrowse();
    await refreshNode();
  } catch (e) {
    $('mw-build-info').textContent = '';
    toast(e.message, true);
  } finally {
    btn.classList.remove('busy');
  }
}

// ---------------------------------------------------------------- solve ---

async function solve() {
  try {
    await req('POST', '/api/mw/solve', {
      max_iterations: Number($('mw-iters').value) || 1000,
      target_exploit_pct: Number($('mw-target').value) || 0.3,
      check_every: Number($('mw-check').value) || 10,
      engine: $('mw-engine').value,
      algorithm: $('mw-algo').value,
    });
    startPolling();
  } catch (e) {
    toast(e.message, true);
  }
}

function startPolling() {
  if (S.polling) return;
  S.polling = setInterval(poll, 700);
  poll();
}

let lastRefreshIter = -1;
async function poll() {
  let st;
  try {
    st = await req('GET', '/api/mw/status');
  } catch {
    return;
  }
  const g = st.gaps.map(x => fmt(x, 2)).join(' / ');
  $('mw-progress').textContent = st.iteration > 0
    ? `${st.state} · iter ${st.iteration} · ${fmt(st.exploit_pct, 3)}% pot · ${fmt(st.iters_per_sec, 1)} it/s · gaps ${g}`
    : st.state;
  $('mw-engine-note').textContent = st.error ? `error: ${st.error}` : st.note;
  if (st.tree && !$('mw-build-info').textContent) $('mw-build-info').textContent = treeText(st.tree);
  if (st.state !== 'running') {
    clearInterval(S.polling);
    S.polling = null;
    if (S.built) refreshNode();
  } else if (S.built && st.iteration - lastRefreshIter >= 50) {
    lastRefreshIter = st.iteration;
    refreshNode();
  }
}

async function refreshSaves() {
  try {
    const list = await req('GET', '/api/mw/saves');
    const sel = $('mw-load-select');
    sel.innerHTML = '<option value="">saved 3-way solves…</option>';
    for (const s of list) {
      const o = document.createElement('option');
      o.value = s.name;
      o.textContent = `${s.name} · ${s.board} · ${s.iteration} it` + (s.exploit_pct != null ? ` · ${fmt(s.exploit_pct, 2)}%` : '');
      sel.appendChild(o);
    }
  } catch { /* server without saves dir */ }
}

// --------------------------------------------------------------- browse ---

function resetBrowse() {
  S.path = [];
  S.line = [];
  S.view = null;
}

async function refreshNode() {
  try {
    S.view = await req('POST', '/api/mw/node', { path: S.path, ev: true });
    renderNode();
  } catch (e) {
    toast(e.message, true);
  }
}

function go(step, label) {
  S.path.push(step);
  S.line.push(label);
  refreshNode();
}

function renderLine() {
  const box = $('mw-line');
  box.innerHTML = '';
  const root = document.createElement('button');
  root.className = 'btn xs';
  root.textContent = 'root';
  root.addEventListener('click', () => { S.path = []; S.line = []; refreshNode(); });
  box.appendChild(root);
  S.line.forEach((l, i) => {
    const b = document.createElement('button');
    b.className = 'btn xs';
    b.textContent = l;
    b.addEventListener('click', () => {
      S.path = S.path.slice(0, i + 1);
      S.line = S.line.slice(0, i + 1);
      refreshNode();
    });
    box.appendChild(b);
  });
}

function renderNode() {
  const v = S.view;
  renderLine();
  const head = $('mw-head');
  head.innerHTML = '';
  const board = document.createElement('div');
  board.className = 'board-cards';
  v.board.forEach(c => board.appendChild(cardChip(c)));
  head.appendChild(board);
  const info = document.createElement('div');
  const players = [0, 1, 2].map(k => {
    const live = v.live[k] ? '' : ' (folded)';
    const act = v.actor === k ? ' ◀' : '';
    return `${esc(S.names[k])} in ${fmt(v.put[k])}${live}${act} · ${fmt(v.range_combos[k], 1)} combos`;
  });
  info.innerHTML = `<div>pot ${fmt(v.pot)}</div>` + players.map(p => `<div>${p}</div>`).join('');
  head.appendChild(info);

  const acts = $('mw-actions');
  acts.innerHTML = '';
  const cards = $('mw-cards');
  cards.innerHTML = '';
  const matrix = $('mw-matrix');
  matrix.innerHTML = '';
  $('mw-detail').innerHTML = '';
  if (v.kind === 'action') {
    const who = document.createElement('span');
    who.className = 'mono';
    who.textContent = `${S.names[v.actor]} to act:`;
    acts.appendChild(who);
    v.actions.forEach((a, i) => {
      const b = document.createElement('button');
      b.className = 'btn sm mw-act';
      b.style.borderLeft = `4px solid ${actionColor(a, v.pot)}`;
      b.textContent = `${a.label} · ${(a.freq * 100).toFixed(1)}%`;
      b.addEventListener('click', () => go(i, `${S.names[v.actor]} ${a.label}`));
      acts.appendChild(b);
    });
    renderMatrix(v);
  } else if (v.kind === 'chance') {
    acts.textContent = `Deal the ${v.board.length === 3 ? 'turn' : 'river'}:`;
    v.cards.forEach(c => {
      const chip = cardChip(c);
      chip.classList.add('mw-card');
      chip.addEventListener('click', () => go(c, c));
      cards.appendChild(chip);
    });
  } else {
    const live = [0, 1, 2].filter(k => v.live[k]).map(k => S.names[k]);
    acts.textContent = v.kind === 'fold'
      ? `Hand over: ${live.join(', ')} wins the pot of ${fmt(v.pot)}.`
      : `Showdown between ${live.join(', ')} for a pot of ${fmt(v.pot)}.`;
  }
}

function renderMatrix(v) {
  const matrix = $('mw-matrix');
  const colors = v.actions.map(a => actionColor(a, v.pot));
  // reach share per class: weight / combos (combos at full weight = 1)
  for (let i = 0; i < 13; i++) {
    for (let j = 0; j < 13; j++) {
      const k = i * 13 + j;
      const c = v.classes[k];
      const cell = document.createElement('div');
      cell.className = 'cell';
      const share = c.combos > 0 ? Math.min(1, c.weight / c.combos) : 0;
      if (share <= 1e-4) {
        cell.classList.add('empty');
      } else {
        const bars = document.createElement('div');
        bars.className = 'bars';
        bars.style.height = `${Math.max(8, share * 100)}%`;
        bars.style.top = 'auto';
        c.strategy.forEach((f, a) => {
          const d = document.createElement('div');
          d.style.width = `${f * 100}%`;
          d.style.background = colors[a];
          bars.appendChild(d);
        });
        cell.appendChild(bars);
      }
      const tag = document.createElement('span');
      tag.className = 'tag';
      tag.textContent = cellInfo(i, j).label;
      cell.appendChild(tag);
      if (c.ev != null && share > 1e-4) {
        const sub = document.createElement('span');
        sub.className = 'sub';
        sub.textContent = fmt(c.ev, 1);
        cell.appendChild(sub);
      }
      cell.addEventListener('mouseenter', () => showDetail(v, k, colors));
      matrix.appendChild(cell);
    }
  }
}

function showDetail(v, k, colors) {
  const c = v.classes[k];
  const rows = v.hands.filter(h => h.class === k && h.weight > 0);
  const head = `<div class="mw-detail-head">${esc(c.label)} · ${fmt(c.weight, 2)} of ${c.combos} combos` +
    (c.ev != null ? ` · EV ${fmt(c.ev, 2)}` : '') +
    (v.ev_skipped ? ' · EVs shown from the next street on (tree too big to evaluate here)' : '') + '</div>';
  const legend = v.actions.map((a, i) =>
    `<span class="mw-key"><i style="background:${colors[i]}"></i>${esc(a.label)} ${(c.strategy[i] * 100).toFixed(0)}%</span>`).join('');
  const table = rows.map(h => {
    const bar = h.strategy.map((f, i) => `<i style="width:${f * 100}%;background:${colors[i]}"></i>`).join('');
    return `<div class="mw-combo"><span>${esc(h.combo)}</span><span class="mw-bar">${bar}</span>` +
      `<span>${h.ev != null ? fmt(h.ev, 2) : ''}</span></div>`;
  }).join('');
  $('mw-detail').innerHTML = head + `<div class="mw-legend">${legend}</div>` + table;
}

// ------------------------------------------------- preflop lab handoff ---

/** Fill the setup from a 3-way Preflop Lab export and switch to this tab. */
export function applyThreeWayExport(ex) {
  ex.positions.forEach((p, i) => {
    $(`mw-name-${i}`).value = p;
    $(`mw-range-${i}`).value = ex.ranges[i];
    $(`mw-stack-${i}`).value = fmt(ex.stacks_bb[i], 2);
  });
  $('mw-pot').value = fmt(ex.pot_bb, 2);
  $('mw-rake').value = ex.rake_pct;
  $('mw-rakecap').value = ex.rake_cap;
  document.querySelector('.tab[data-tab="threeway"]').click();
  toast('3-way spot loaded from the Preflop Lab: pick a board and BUILD TREE.');
}
window.gtopenApplyThreeWay = applyThreeWayExport;

// ------------------------------------------------------------------ init ---

renderPlayers();
$('mw-build').addEventListener('click', build);
$('mw-solve').addEventListener('click', solve);
$('mw-stop').addEventListener('click', () => req('POST', '/api/mw/stop').catch(e => toast(e.message, true)));
$('mw-save').addEventListener('click', async () => {
  const name = $('mw-save-name').value.trim();
  if (!name) return toast('Enter a save name first.', true);
  try {
    await req('POST', '/api/mw/save', { name });
    toast(`Saved ${name}`);
    refreshSaves();
  } catch (e) { toast(e.message, true); }
});
$('mw-load').addEventListener('click', async () => {
  const name = $('mw-load-select').value;
  if (!name) return;
  try {
    const st = await req('POST', '/api/mw/load', { name });
    S.built = true;
    $('mw-build-info').textContent = treeText(st.tree);
    $('mw-board').value = st.tree.board;
    resetBrowse();
    await poll();
    await refreshNode();
  } catch (e) { toast(e.message, true); }
});
document.querySelector('.tab[data-tab="threeway"]').addEventListener('click', () => {
  refreshSaves();
  poll();
});
// Re-attach to a session that survived a page reload.
req('GET', '/api/mw/status').then(st => {
  if (st.tree) {
    S.built = true;
    $('mw-build-info').textContent = treeText(st.tree);
    if (st.state === 'running') startPolling();
  }
}).catch(() => {});
