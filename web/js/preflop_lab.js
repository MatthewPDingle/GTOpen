// PREFLOP LAB — UI for the multiway preflop solver (equity-model postflop).
// Build a game (any limps/sizes/players), solve it, walk the action tree with
// an action ribbon, and export any heads-up flop node straight into
// the postflop solver's SETUP.

import { api } from './api.js';
import { createPositionSizing } from './preflop_sizing.js';
import { createSeatStacks } from './preflop_stacks.js';
import { createIcmControls } from './preflop_icm.js';
import { RARE_STEP, frequencyText, frequencyDetail, lineStatus, lineNote, segmentLevels } from './preflop_reach.js';
import { publishedIteration, publicationKey, publicationLabel, solveCompletionLabel, supportsEarlyPreview, earlyPreviewRequest } from './preflop_preview.js';
import { cellInfo } from './cards.js';
import { formatPreflopView } from './preflop_actions.js';
import { blindSizes, blindPosts, unraisedWinner } from './preflop_blinds.js';
import { renderModelEvidence } from './model_evidence.js';
import { editPostflopStats, hasContextualBetting } from './postflop_context.js';
import { initRangeLabRef, matchContext, defaultGame } from './rangelab_ref.js';
import { initPreflopTrust } from './preflop_trust.js';
import { createLeafNetPicker } from './preflop_leafnet.js';

// Same key as the Browse matrix (browse.js): fold blue, check/call green,
// raises in the postflop bet reds — small / medium / large by size rank,
// jams in the overbet shade.
const COLORS = { fold: '#4a78c8', check: '#5ca75f', call: '#5ca75f' };
const RAISE_SHADES = ['#e8484c', '#c24345', '#a23a3c', '#7c3134'];
const DEFAULT_REALIZATION = 'balanced';
// Opt-in: balanced plus the learned flop correction (beta).
const LEARNED_REALIZATION = 'leafnet';
const currentModel = (m) => m === DEFAULT_REALIZATION || m === LEARNED_REALIZATION;

// One window-level pointer release for the paint grid. Registering it inside
// buildPaintGrid added a fresh handler every time the editor opened.
let onPaintRelease = null;
window.addEventListener('mouseup', () => { if (onPaintRelease) onPaintRelease(); });

const CHIP_STYLE = 'display:inline-block;padding:1px 6px;border:1px solid var(--line2);' +
  'border-radius:9px;font-size:10px;line-height:1.5;white-space:nowrap';

function positionsFor(nPlayers) {
  const NAMED = {
    2: ['SB', 'BB'], // HU: SB is the button, acts first pre
    3: ['BTN', 'SB', 'BB'],
    6: ['UTG', 'HJ', 'CO', 'BTN', 'SB', 'BB'],
    7: ['UTG', 'MP', 'HJ', 'CO', 'BTN', 'SB', 'BB'],
    8: ['UTG', 'UTG1', 'MP', 'HJ', 'CO', 'BTN', 'SB', 'BB'],
    9: ['UTG', 'UTG1', 'MP', 'LJ', 'HJ', 'CO', 'BTN', 'SB', 'BB'],
  };
  if (NAMED[nPlayers]) return NAMED[nPlayers];
  const all = ['UTG', 'UTG1', 'MP', 'LJ', 'HJ', 'CO', 'BTN'];
  return [...all.slice(7 - (nPlayers - 2)), 'SB', 'BB'];
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
    name: '6-max 100bb low-stakes: limps + 5% rake',
    players: 6, stack: 100, opens: '2.5,4', mult: '3', maxRaises: 3,
    limp: true, allin: false, ante: 0, rakePct: 5, rakeCap: 3,
  },
  {
    name: '8-max 150bb $2/2: limps + 10%, 8.5 cap rake', smallBlind: 2, bigBlind: 2,
    players: 8, stack: 150, opens: '7.5,10', mult: '2,4', maxRaises: 2,
    limp: true, allin: false, ante: 0, rakePct: 10, rakeCap: 8.5,
  },
  {
    name: '8-max 150bb $2/5: limps + 10%, 9 cap rake', smallBlind: 2, bigBlind: 5,
    players: 8, stack: 150, opens: '3,4', mult: '2.5,4', maxRaises: 2,
    limp: true, allin: true, ante: 0, rakePct: 10, rakeCap: 9,
  },
  {
    name: '8-max 200bb $2/5: limps + 5%, 2.2 cap rake', smallBlind: 2, bigBlind: 5,
    players: 8, stack: 200, opens: '3,4', mult: '2.5,4', maxRaises: 2,
    limp: true, allin: false, ante: 0, rakePct: 5, rakeCap: 2.2,
  },
];

export function initPreflopLab({ els, onExport, toast, gotoSetup }) {
  const positionSizing = createPositionSizing(els, positionsFor, () => estSoon());
  const seatStacks = createSeatStacks(els, positionsFor, () => estSoon());
  const icmControls = createIcmControls(els, positionsFor, () => estSoon());
  const leafNets = createLeafNetPicker(els, () => estSoon());
  const rangeLab = els.rangeLab ? initRangeLabRef(els.rangeLab) : null;
  // hero mode's trust dial, fed by every status poll
  const trustDial = els.trust ? initPreflopTrust(els.trust, { toast, positions: () => S.positions || [] }) : null;
  // Range source: this game's solve, or Range Lab's canonical charts walked
  // as a tree (no build or solve). Each source keeps its own line.
  const canon = { on: false, summary: null, tag: null, variant: null, depth: null, lines: {} };
  const previewBanner = document.createElement('div');
  previewBanner.id = 'pfl-publication';
  previewBanner.className = 'pfl-preview-note hidden';
  previewBanner.setAttribute('role', 'status');
  // Publication owns a full row; actor and evidence keep their existing row.
  els.nodeTitle.parentElement.before(previewBanner);
  const previewOption = document.createElement('label');
  previewOption.className = 'pfl-preview-option';
  previewOption.innerHTML = '<input type="checkbox" checked> Show early strategy previews';
  previewOption.dataset.tip = 'Publish a learned strategy after 2 iterations, then every 10. Early ranges are approximate; the accuracy target is unchanged.';
  const previewCheck = previewOption.querySelector('input');
  previewCheck.disabled = true;
  els.solve.parentElement.after(previewOption);
  const previewCapability = api.pfCapabilities().then(caps => {
    const supported = supportsEarlyPreview(caps);
    previewCheck.disabled = S.solveRunning || !supported;
    return supported;
  }).catch(() => false);
  const reachWarning = document.createElement('div');
  reachWarning.className = 'pfl-reach-warning hidden';
  reachWarning.setAttribute('role', 'status');
  previewBanner.after(reachWarning);
  const nodeEvidence = document.createElement('div');
  nodeEvidence.id = 'pfl-node-evidence';
  nodeEvidence.className = 'hidden';
  els.nodeTitle.after(nodeEvidence);
  const S = {
    built: false,
    formCfg: null,  // visible settings at build/load; independent of saved model metadata
    builtCfg: null, // actual engine config, including a loaded game's original model
    gameSaved: false, // current solve persisted via SAVE GAME / load (gates discard confirms)
    savedName: null,  // on-disk name behind gameSaved (the save chip)
    cursor: [],     // action indices to the node being VIEWED
    lineP: [],      // the full line (cursor is always a prefix of it)
    lineHist: null, // /api/preflop/node history for lineP (ribbon source)
    view: null,
    polling: null,
    positions: [],
    cells: [],      // persistent 13x13 cell divs (same markup as Browse)
    colors: [],
    rangeSeat: 0,   // whose arriving range the grid shows at terminals
    lastState: null, // last solver state seen by poll (drives the progress bar)
    gap0: null,      // first measured BR gap of the current run (progress scale)
    runPct: 0,       // monotonic progress within the current run
    model: null,     // per-seat {mode, profile, implied, label}; hero seat
    applied: null,   // last model actually sent to the solver (drives 🔒)
    appliedSeatSigs: [], // per-seat signatures of what the engine has
    appliedHero: null,   // hero seat the ENGINE actually has (null = off)
    heroPending: false,  // hero chosen but deferred until a solve exists
    lastApplyWasSolve: false, // the badge reads "applied with this solve"
    activeModel: null, // value model of the built/loaded game
    multiwayModel: null, // multiway equity version reported by the engine
    postflopDirty: false, // tendencies edited since the last table push —
                          // excluded from the seat signature (a postflop-only re-send
                          // must not read as "table changed"), but SOLVE and
                          // SAVE GAME re-send the table when set
    engineFrozen: null,  // engine-truth frozen mask from /status, if reported
    solveRunning: false, // mirrors status "running" (table changes refused)
    runBase: null,   // solver iteration count when the current run started
    runStart: null,  // wall-clock start of the current run (for the timer)
    lastGaps: null,  // per-seat BR gaps from the last checkpoint (bleeds)
    editSeat: null,  // seat open in the profile editor
    editBucket: 0,
    paintAction: 'call',
    paintWeight: 1.0,
    painting: false,
  };
  let ARCHETYPES = [];
  let SAVED_PROFILES = [];
  api.pfArchetypes().then(a => { ARCHETYPES = a; renderModel(); }).catch(() => {});
  api.pfProfiles().then(p => { SAVED_PROFILES = p; renderModel(); }).catch(() => {});

  // escape user-supplied text (profile/saved-game names) before
  // interpolating into innerHTML or attribute strings
  const esc = s => String(s).replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  // ----- step rail: numbered steps follow the range source -----
  // The page ships one rail for both sources. Range Lab charts skip the
  // build/solve/model steps, so the shared steps are renumbered rather than
  // explained in prose.
  const stepEls = {};
  {
    const wanted = [
      ['charts', /^1\s*·\s*CHOOSE THE CHARTS/i],
      ['scenario', /^1\s*·\s*SET UP/i],
      ['build', /^2\s*·\s*BUILD/i],
      ['solve', /^3\s*·\s*SOLVE/i],
      ['model', /^4\s*·\s*MODEL/i],
      ['walk', /^5\s*·\s*SET UP THE PREFLOP/i],
      ['send', /^6\s*·\s*SEND/i],
    ];
    for (const el of document.querySelectorAll('#view-preflop .pfl-step')) {
      const text = el.textContent.trim();
      const hit = wanted.find(([, re]) => re.test(text));
      if (hit && !stepEls[hit[0]]) stepEls[hit[0]] = el;
    }
  }
  const STEP_LABELS = { scenario: 'SCENARIO', build: 'BUILD', solve: 'SOLVE', model: 'MODEL', walk: 'WALK', send: 'SEND', charts: 'CHARTS' };
  const RAIL = {
    solve: ['scenario', 'build', 'solve', 'model', 'walk', 'send'],
    charts: ['charts', 'walk', 'send'],
  };
  const railOrder = () => RAIL[canon.on ? 'charts' : 'solve'];
  function renderStepRail() {
    const order = railOrder();
    for (const [key, el] of Object.entries(stepEls)) {
      const at = order.indexOf(key);
      el.classList.toggle('hidden', at < 0);
      if (at < 0) continue;
      el.textContent = `${at + 1} · ${STEP_LABELS[key]}`;
      // the rail names the step; the panel below carries the detail
      delete el.dataset.tip;
      el.removeAttribute('tabindex');
    }
  }

  // ----- save state chip (the button says when it can run, the chip why) -----
  const saveChip = document.createElement('div');
  saveChip.id = 'pfl-save-state';
  saveChip.className = 'dim mono';
  saveChip.style.cssText = 'font-size:10px;margin-top:4px;display:flex;gap:5px;align-items:center;flex-wrap:wrap';
  els.saveGame.closest('.btn-row').after(saveChip);
  function renderSaveState() {
    saveChip.classList.toggle('hidden', canon.on);
    els.saveGame.classList.toggle('hidden', canon.on);
    if (canon.on) return;
    const solved = S.built && lastIter >= 1;
    els.saveGame.disabled = !solved;
    if (!solved) {
      saveChip.textContent = S.built ? 'no solve yet · SAVE needs one' : 'nothing built yet';
      saveChip.dataset.tip = 'A save stores the solved strategies.';
      return;
    }
    const name = S.gameSaved && S.savedName ? S.savedName : `${S.positions.length}-max ${els.stack.value}bb`;
    saveChip.innerHTML = `<span>${esc(name)}</span><span>·</span><span>iter ${lastIter}</span><span>·</span>` +
      `<b style="color:${S.gameSaved ? '#8fbf8a' : '#e4c377'}">${S.gameSaved ? 'saved' : 'unsaved'}</b>`;
    saveChip.dataset.tip = S.gameSaved
      ? 'On disk. Solving or changing the table makes it unsaved.'
      : 'Not on disk. SAVE writes the current solution.';
  }

  // ----- export card: preconditions + what is sent, in one place -----
  const exportCard = document.createElement('div');
  exportCard.id = 'pfl-export-card';
  exportCard.style.cssText = 'margin-top:6px;padding:8px;border:1px solid var(--line2);border-radius:4px;font-size:11px;line-height:1.5';
  els.exportBtn.after(exportCard);
  const exportBody = document.createElement('div');
  exportCard.append(exportBody, els.exportBtn);
  els.exportBtn.textContent = 'SEND';
  function renderExportCard(continuation = null) {
    const v = S.view;
    if (!v) {
      exportBody.innerHTML = `<div class="pfl-step" style="margin:0 0 4px">POSTFLOP SETUP</div>` +
        `<div><span style="color:#c96a5f">\u2717</span> flop reached</div>` +
        `<div><span style="color:#c96a5f">\u2717</span> heads-up flop</div>` +
        `<div><span style="color:#c96a5f">\u2717</span> strategy at iter \u2265 2</div>`;
      els.exportBtn.disabled = true;
      return;
    }
    exportCard.classList.remove('hidden');
    const flop = v.kind === 'pot_share';
    const live = flop ? v.positions.filter((_, i) => v.live[i]) : [];
    // exportable is false both for a multiway flop and when the engine has no
    // published strategy at this point (a table change resets it), so the two
    // preconditions are named separately: an unsolved point is not "not
    // heads-up".
    const three = !canon.on && !!v.exportable3;
    const headsUp = flop && live.length === 2;
    const two = headsUp && !!v.exportable && !three;
    const hasStrategy = canon.on ? !!v.exportable : !v.strategy_note;
    const strategyReady = canon.on ? !!v.exportable : hasStrategy && lastIter >= 2;
    // what the postflop solver gets: chips still behind the shallowest live
    // seat (SPR × pot), not the game's starting stack or the chart's depth
    const stack = v.spr != null ? v.spr * v.pot : canon.on ? v.game?.depth : (!canon.on && S.builtCfg ? JSON.parse(S.builtCfg).stack : null);
    const chipsBehind = stack == null || Number(stack) > 1e-9;
    const ready = !!(flop && (two || three) && strategyReady && chipsBehind);
    els.exportBtn.disabled = !ready;
    els.exportBtn.dataset.dest = three ? '3-way' : '2-way';
    const tick = (ok, label) => `<div><span style="color:${ok ? '#8fbf8a' : '#c96a5f'}">${ok ? '\u2713' : '\u2717'}</span> ${label}</div>`;
    const cfg = !canon.on && S.builtCfg ? JSON.parse(S.builtCfg) : {};
    const dest = !flop ? 'POSTFLOP SETUP'
      : three ? 'POSTFLOP · 3-WAY'
      : live.length === 2 ? 'POSTFLOP · 2-WAY'
      : `POSTFLOP · ${live.length}-WAY`;
    const rows = [];
    if (flop) {
      rows.push(['ranges', live.join(' · ')]);
      rows.push(['pot', `${v.pot.toFixed(1)} bb`]);
      // what the postflop solver gets: chips still behind the shallowest live
      // seat (SPR × pot), not the game's starting stack or the chart's depth
      if (stack != null) rows.push(['stack', `${Number(Number(stack).toFixed(2))} bb`]);
      const rakePct = canon.on ? Number(els.canonRakePct.value) || 0 : Number(cfg.rake_pct) || 0;
      const rakeCap = canon.on ? Number(els.canonRakeCap.value) || 0 : Number(cfg.rake_cap) || 0;
      rows.push(['rake', rakePct ? `${rakePct}%${rakeCap ? ` · cap ${rakeCap} bb` : ' · uncapped'}` : 'none']);
      if (canon.on) rows.push(['source', 'Range Lab chart']);
      else rows.push(['models', live.map(p => {
        const i = S.positions.indexOf(p);
        const m = i >= 0 ? S.model?.seats[i] : null;
        return m && m.mode === 'ruled' ? `${p} ${m.label}` : `${p} solver`;
      }).join(' · ')]);
      let aggressor = null;
      takenSteps(S.cursor.length).forEach(st => { if (st.kind === 'raise' || st.kind === 'jam') aggressor = st.pos; });
      rows.push(['aggressor', aggressor || 'none']);
    }
    // the single reason the export is not ready, in the order the checks run
    const why = !ready && flop
      ? v.side_pots?.length
        ? 'This flop has side pots — the postflop solver starts from one pot with chips behind.'
        : live.length > 2
          ? `The postflop solver is heads-up only; this line reaches the flop <b>${live.length}-way</b>.`
          : !chipsBehind
            ? 'Nobody has chips behind — the postflop solver needs a stack to bet.'
            : ''
      : '';
    exportBody.innerHTML =
      `<div class="pfl-step" style="margin:0 0 4px">${dest}</div>` +
      (canon.on
        ? tick(flop, 'flop reached') + tick(!!v.exportable, 'Range Lab chart')
        : tick(flop, 'flop reached') + tick(headsUp || three, three ? `${live.length} players` : 'heads-up, stacks left') +
          tick(strategyReady, hasStrategy
            ? `strategy at iter \u2265 2 · iter ${Math.max(0, lastIter)}`
            : 'no solved strategy at this point') +
          tick(chipsBehind, 'chips behind')) +
      (rows.length ? `<dl style="display:grid;grid-template-columns:auto 1fr;gap:1px 10px;margin:6px 0 0">` +
        rows.map(([k, val]) => `<dt class="dim" style="margin:0">${k}</dt><dd style="margin:0;text-align:right">${esc(String(val))}</dd>`).join('') +
        `</dl>` : '') +
      (why ? `<div class="dim" style="margin-top:6px">${why}</div>` : '') +
      (!ready && flop && !strategyReady && hasStrategy && !canon.on ? `<div class="dim" style="margin-top:6px">Solve to iteration 2 first.</div>` : '');
    if (!ready && flop && live.length > 2) {
      const b = document.createElement('button');
      b.className = 'btn ghost xs';
      b.textContent = 'GO TO SETUP \u2192';
      b.addEventListener('click', gotoSetup);
      exportBody.append(b);
    }
    if (continuation) exportBody.appendChild(continuation);
  }

  // ----- status chips (state · iter · gap · measured · engine) -----
  const statusChips = document.createElement('div');
  statusChips.style.cssText = 'display:flex;flex-wrap:wrap;gap:3px 6px;align-items:center';
  const statusWarn = document.createElement('div');
  statusWarn.id = 'pfl-status-warn';
  statusWarn.className = 'hidden'; // poll() fills it, and unhides only when it has something to say
  statusWarn.setAttribute('role', 'status');
  statusWarn.style.cssText = 'margin-top:3px;line-height:1.4';
  els.status.replaceChildren(statusChips, statusWarn);
  delete els.status.dataset.tip; // the chips carry their own tips
  els.applyBtn.dataset.tip = 'Sends the staged table and hero. A changed table resets learning; SOLVE does this automatically.';
  function statusChip(label, tip) {
    const el = document.createElement('span');
    el.style.cssText = CHIP_STYLE;
    el.textContent = label;
    if (tip) el.dataset.tip = tip;
    return el;
  }

  // ----- model strip: value model + multiway equity in one place -----
  const modelStrip = document.createElement('div');
  modelStrip.id = 'pfl-model-strip';
  modelStrip.className = 'dim';
  modelStrip.style.cssText = 'display:flex;flex-wrap:wrap;gap:4px 6px;align-items:center;margin:4px 0 6px';
  if (stepEls.model) stepEls.model.after(modelStrip);
  else els.modelBox.before(modelStrip);
  const MULTIWAY_LABEL = {
    coupled_deck_v1: 'coupled-deck',
    three_way_table_v1: 'exact 3-way (beta)',
    legacy_product: 'legacy product',
  };
  const MULTIWAY_TIP = {
    coupled_deck_v1: 'Three or more players: coupled hand-strength samples and showdown value after rake. Approximate, not jointly dealt cards \u2014 overlapping tight ranges can still have large card-removal errors. Heads-up continuation is unchanged; the full postflop tree is not solved.',
    three_way_table_v1: 'Three-player pots: showdown equity by hand class, all three hands from one deck, so card removal is exact (Monte-Carlo boards). Four or more: coupled hand-strength samples. Heads-up continuation is unchanged; the full postflop tree is not solved.',
    legacy_product: 'This saved game keeps its original product-of-heads-up equity approximation. BUILD GAME starts with the current model.',
  };
  function renderModelStrip() {
    const visible = S.built && !canon.on;
    modelStrip.classList.toggle('hidden', !visible);
    if (!visible) return;
    const value = S.activeModel || 'unknown';
    const legacy = !currentModel(value);
    modelStrip.replaceChildren(
      statusChip(`value · ${value}${legacy ? ' · saved' : ''}`,
        legacy
          ? 'Saved game: keeps its original value model. RE-SOLVE continues it; BUILD GAME starts with the current model.'
          : 'Value model of the built game.'),
      ...(S.multiwayModel ? [statusChip(`multiway · ${MULTIWAY_LABEL[S.multiwayModel] || S.multiwayModel}`,
        MULTIWAY_TIP[S.multiwayModel] || '')] : []),
      ...(legacy ? [(() => { const el = statusChip('RE-SOLVE continues it'); el.style.borderStyle = 'dashed'; return el; })()] : []),
    );
  }

  // Model-library deletion is reversible and local to this browser. Keep the
  // source templates/files and profiles embedded in games intact.
  const deletedModelsKey = 'pfl-deleted-models-v1';
  let deletedModels = new Set();
  try {
    const saved = JSON.parse(localStorage.getItem(deletedModelsKey) || '[]');
    if (Array.isArray(saved)) deletedModels = new Set(saved.filter(x => typeof x === 'string'));
  } catch {}
  const managerButton = document.createElement('button');
  managerButton.type = 'button';
  managerButton.className = 'btn ghost xs pfl-model-manager-open';
  managerButton.textContent = 'Manage models';
  managerButton.setAttribute('aria-haspopup', 'dialog');
  const manager = document.createElement('dialog');
  manager.className = 'pfl-model-manager';
  manager.setAttribute('aria-labelledby', 'pfl-model-manager-title');
  manager.innerHTML = '<div class="pfl-model-manager-heading"><h2 id="pfl-model-manager-title">Manage models</h2><button type="button" class="btn ghost xs" data-close-manager aria-label="Close model manager">Close</button></div><p class="dim">Removes models from the seat menus in this browser. Existing games keep their profiles; Show removed restores a removed model.</p>' +
    '<input type="search" class="pfl-model-search" placeholder="Find a model…" aria-label="Find player models">' +
    '<div class="pfl-model-manager-actions"><button type="button" class="btn primary xs" data-new-model>New model</button><button type="button" class="btn ghost xs" data-clear-generated>Remove generated archetypes</button><label><input type="checkbox" data-show-deleted> Show removed</label></div><div class="pfl-model-library"></div><div class="pfl-model-manager-status dim" role="status" aria-live="polite"></div>';
  const libraryPane = document.createElement('div');
  libraryPane.className = 'pfl-model-library-pane';
  [...manager.children].slice(1, -1).forEach(el => libraryPane.appendChild(el));
  manager.querySelector('[role="status"]').before(libraryPane, els.editor);
  manager.querySelector('[data-new-model]').addEventListener('click', () => openLibraryEditor(null));
  els.modelBox.before(managerButton);
  document.body.appendChild(manager);
  managerButton.addEventListener('click', () => {
    renderModelManager();
    if (!manager.open) manager.showModal();
    (manager.classList.contains('editing') ? els.editor : manager.querySelector('.pfl-model-search')).focus();
  });
  manager.querySelector('[data-close-manager]').addEventListener('click', () => manager.close());
  manager.addEventListener('close', () => managerButton.focus());
  manager.addEventListener('click', e => {
    const r = manager.getBoundingClientRect();
    if (e.target === manager && (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom)) manager.close();
  });
  const managerList = manager.querySelector('.pfl-model-library');
  manager.querySelector('.pfl-model-search').addEventListener('input', renderModelManager);
  manager.querySelector('[data-show-deleted]').addEventListener('change', renderModelManager);
  manager.querySelector('[data-clear-generated]').addEventListener('click', () => {
    const keys = ARCHETYPES.filter(a => !a.name.startsWith('Data')).map(a => `arch:${a.name}`).filter(k => !deletedModels.has(k));
    if (!keys.length) return;
    updateDeletedModels(keys, true);
  });
  function updateDeletedModels(keys, remove) {
    const next = new Set(deletedModels);
    keys.forEach(key => remove ? next.add(key) : next.delete(key));
    try { localStorage.setItem(deletedModelsKey, JSON.stringify([...next])); }
    catch { manager.querySelector('[role="status"]').textContent = 'Could not save model-menu preferences in this browser.'; return; }
    deletedModels = next;
    renderModel();
    const message = remove ? `${keys.length === 1 ? 'Model' : `${keys.length} models`} removed.` : 'Model restored';
    if (manager.open) manager.querySelector('[role="status"]').textContent = message;
    else toast(message);
  }
  let managerSignature = '';
  function archetypeGroups(entries) {
    const groups = new Map();
    // Keep the generated group first: its removal action is intentionally
    // separate from every measured site/stake library.
    groups.set('Generated archetypes', []);
    for (const [a, k] of entries) {
      const coin = /^Data · CoinPoker · (NL\d+) · /.exec(a.name);
      const title = coin ? `CoinPoker · ${coin[1]} · measured` :
        a.name.startsWith('Data · Ignition · ') ? 'Ignition · NL10 regular · measured openings' :
        a.name.startsWith('Data') ? 'HandHQ · 25–50NL · measured (2009)' : 'Generated archetypes';
      if (!groups.has(title)) groups.set(title, []);
      groups.get(title).push([a, k]);
    }
    return [...groups];
  }
  const modelDisplayName = name => name.replace(/^Data · CoinPoker · /, 'CP ').replace(/^Data · Ignition · /, 'Ignition ');
  function renderModelManager() {
    const search = manager.querySelector('.pfl-model-search').value.trim().toLowerCase();
    const showDeleted = manager.querySelector('[data-show-deleted]').checked;
    const groups = [
      ...archetypeGroups(ARCHETYPES.map((a,k) => [a,k])).map(([title, entries]) =>
        [title, entries.map(([a]) => ({name:a.name, key:`arch:${a.name}`, note:a.note || ''}))]),
      ['Saved profiles', SAVED_PROFILES.map(name => ({name, key:`saved:${name}`}))],
    ];
    const seats = (S.model?.seats || []).map((m, i) => ({ m, i })).filter(({m}) => m.mode === 'ruled');
    const signature = JSON.stringify([groups, [...deletedModels], search, showDeleted, seats.map(({m,i}) => [i,m.label])]);
    if (signature === managerSignature) return;
    managerSignature = signature;
    manager.querySelector('[data-clear-generated]').disabled = !groups[0][1].some(m => !deletedModels.has(m.key));
    const currentRows = showDeleted ? [] : seats.filter(({m,i}) => `${S.positions[i]} ${m.label}`.toLowerCase().includes(search));
    managerList.innerHTML = (currentRows.length ? '<h4>Current game</h4>' + currentRows.map(({m,i}) =>
      `<div class="pfl-library-model"><span>${esc(S.positions[i])} · ${esc(m.label)}</span><button type="button" class="btn ghost xs" data-edit-seat="${i}">Edit seat</button></div>`).join('') : '') + groups.map(([title, models]) => {
      const rows = models.filter(m => deletedModels.has(m.key) === showDeleted && m.name.toLowerCase().includes(search));
      if (!rows.length) return '';
      return `<h4>${title} <span class="dim">${rows.length}</span></h4>` + rows.map(m =>
        `<div class="pfl-library-model"><span>${esc(modelDisplayName(m.name))}${m.note ? `<button type="button" class="info-dot"
          aria-label="About ${esc(m.name)}" data-tip="${esc(m.note)}">?</button>` : ''}</span>${showDeleted ? '' : `<button type="button" class="btn ghost xs" data-edit-model="${esc(m.key)}" aria-label="Edit ${esc(m.name)}">Edit</button>`}<button type="button" class="btn ghost xs" data-model-key="${esc(m.key)}" aria-label="${showDeleted ? 'Restore' : 'Remove'} ${esc(m.name)}">${showDeleted ? 'Restore' : 'Remove'}</button></div>`).join('');
    }).join('') || '<p class="dim">No matching models.</p>';
    managerList.querySelectorAll('[data-edit-seat]').forEach(button => button.addEventListener('click', () => openEditor(+button.dataset.editSeat)));
    managerList.querySelectorAll('[data-edit-model]').forEach(button => button.addEventListener('click', () => openLibraryEditor(button.dataset.editModel)));
    managerList.querySelectorAll('[data-model-key]').forEach(button => button.addEventListener('click', () => {
      const key = button.dataset.modelKey;
      updateDeletedModels([key], !showDeleted);
    }));
  }

  // The server refuses table/hero changes while a solve runs (HTTP 409); the
  // API layer formats that as "409 — …", so key off the status, not the text.
  const errText = e => e && e.status === 409
    ? 'a solve is running — STOP it or let it finish before changing the table'
    : (e && e.message) || String(e);

  // All hero calls go through here so poll() can tell when a /status
  // response predates an in-flight (or just-landed) hero change and must
  // not "resync" the dropdown back to the stale engine value.
  let heroBusy = 0, heroEpoch = 0;
  async function heroCall(seat) {
    heroBusy++; heroEpoch++;
    try { return await api.pfHero(seat); }
    finally { heroBusy--; heroEpoch++; }
  }

  // Browse-identical matrix: same .cell markup/classes; each cell carries a
  // data-tip with its exact numbers (the app tooltip system is delegated, so
  // updating the attribute on repaint is all it takes).
  (function buildGrid() {
    const m = els.grid;
    m.innerHTML = '';
    for (let i = 0; i < 13; i++) {
      for (let j = 0; j < 13; j++) {
        const cell = document.createElement('div');
        cell.className = 'cell';
        cell.innerHTML =
          `<div class="bars"></div><div class="fill"></div>` +
          `<div class="tag">${cellInfo(i, j).label}</div><div class="sub"></div>`;
        m.appendChild(cell);
        S.cells.push(cell);
      }
    }
  })();

  // ----- config -----
  // Scenarios: the built-in PRESETS plus the user's saved ones
  // (saves/scenarios/). A saved scenario with a built-in's name replaces it.
  let SCENARIOS = [];   // [{...preset, mine: bool}]
  const applyPreset = (p) => {
    els.smallBlind.value = blindSizes(p).smallBlind;
    els.bigBlind.value = blindSizes(p).bigBlind;
    els.players.value = p.players;
    els.straddleOn.checked = Number(p.straddle || 0) > 0;
    els.straddle.value = p.straddle || 2;
    syncStraddleControls();
    els.stack.value = p.stack;
    els.opens.value = p.opens;
    els.mult.value = p.mult;
    positionSizing.restore(p);
    seatStacks.restore(p);
    els.maxRaises.value = p.maxRaises;
    els.limp.checked = p.limp;
    els.allin.checked = p.allin;
    els.ante.value = p.ante;
    els.rakePct.value = p.rakePct;
    els.rakeCap.value = p.rakeCap;
    // after the rake fields: ICM re-reads them as the numbers to restore
    icmControls.restore(p);
    // Scenarios configure fresh games; old scenario model choices are retired.
    // Explicitly choosing a preset also starts fresh when an older solve is loaded.
    if (S.built && !currentModel(S.activeModel)) S.formCfg = null;
  };
  const currentScenario = () => ({
    players: +els.players.value, stack: +els.stack.value,
    smallBlind: +els.smallBlind.value, bigBlind: +els.bigBlind.value,
    straddle: els.straddleOn.checked ? +els.straddle.value : 0,
    opens: els.opens.value.trim(), mult: els.mult.value.trim(),
    ...positionSizing.scenario(),
    ...seatStacks.scenario(),
    maxRaises: +els.maxRaises.value, limp: els.limp.checked, allin: els.allin.checked,
    ante: +els.ante.value, rakePct: +els.rakePct.value, rakeCap: +els.rakeCap.value,
    // ICM owns the rake fields while it is on (they show 0): last, so its
    // remembered numbers replace the zero the form is displaying
    ...icmControls.scenario(),
  });
  function syncScenarioSelection() {
    const cur = currentScenario();
    const same = s => Object.entries(cur).every(([k, v]) =>
      k === 'smallBlind' || k === 'bigBlind' ? Math.abs(blindSizes(s).smallBlind / blindSizes(s).bigBlind - cur.smallBlind / cur.bigBlind) < 1e-9 :
      k === 'positionSizes' || k === 'seatStacks' ? JSON.stringify(s[k] || {}) === JSON.stringify(v) :
      k === 'laterMult' ? String(s[k] || '') === String(v) :
      k === 'straddle' ? Number(s.straddle || 0) === v :
      k === 'opens' || k === 'mult' ? String(s[k]).replace(/\s/g, '') === String(v).replace(/\s/g, '') : s[k] === v);
    const idx = SCENARIOS.findIndex(same);
    if (idx >= 0) {
      els.preset.value = String(idx);
      els.smallBlind.value = blindSizes(SCENARIOS[idx]).smallBlind;
      els.bigBlind.value = blindSizes(SCENARIOS[idx]).bigBlind;
    }
    else {
      if (!els.preset.querySelector('option[value="-1"]')) els.preset.add(new Option('Current game (custom settings)', '-1'));
      els.preset.value = '-1';
    }
    if (els.scnDel) els.scnDel.classList.toggle('hidden', !(SCENARIOS[idx]?.mine));
  }
  function renderScenarios(selectName) {
    const cur = selectName != null ? selectName
      : (SCENARIOS[+els.preset.value] || {}).name;
    els.preset.innerHTML = '';
    const mine = SCENARIOS.filter(s => s.mine);
    const builtin = SCENARIOS.filter(s => !s.mine);
    const group = (label, list) => {
      if (!list.length) return;
      const g = document.createElement('optgroup');
      g.label = label;
      for (const s of list) {
        const o = document.createElement('option');
        o.value = SCENARIOS.indexOf(s);
        o.textContent = s.name;
        g.appendChild(o);
      }
      els.preset.appendChild(g);
    };
    group('my scenarios', mine);
    group('built-in', builtin);
    const idx = SCENARIOS.findIndex(s => s.name === cur);
    els.preset.value = idx >= 0 ? idx : 0;
    const sel = SCENARIOS[+els.preset.value];
    if (els.scnDel) els.scnDel.classList.toggle('hidden', !(sel && sel.mine));
  }
  async function loadScenarios(selectName) {
    let saved = [];
    try { saved = await api.pfScenarios(); } catch { /* older server: built-ins only */ }
    const byName = new Map(saved.map(s => [s.name, { ...s, mine: true }]));
    SCENARIOS = [
      ...saved.map(s => byName.get(s.name)),
      ...PRESETS.filter(p => !byName.has(p.name)).map(p => ({ ...p, mine: false })),
    ];
    renderScenarios(selectName);
    if (S.built) syncScenarioSelection();
  }
  els.preset.addEventListener('change', () => {
    const s = SCENARIOS[+els.preset.value];
    if (s) applyPreset(s);
    if (els.scnDel) els.scnDel.classList.toggle('hidden', !(s && s.mine));
    updateEstimate();
  });
  if (els.scnSave) els.scnSave.addEventListener('click', async () => {
    const cur = SCENARIOS[+els.preset.value];
    const name = (prompt('Save scenario as', cur ? cur.name : '') || '').trim();
    if (!name) return;
    try {
      await api.pfScenarioSave(name, { ...currentScenario(), realization: DEFAULT_REALIZATION });
      await loadScenarios(name);
      toast(`scenario "${name}" saved`);
    } catch (e) { toast(errText(e), true); }
  });
  if (els.scnDel) els.scnDel.addEventListener('click', async () => {
    const cur = SCENARIOS[+els.preset.value];
    if (!cur || !cur.mine) return;
    if (!confirm(`Delete scenario "${cur.name}"?`)) return;
    try {
      await api.pfScenarioDelete(cur.name);
      await loadScenarios(null);
      const s = SCENARIOS[+els.preset.value];
      if (s) applyPreset(s);
      updateEstimate();
      toast(`scenario "${cur.name}" deleted`);
    } catch (e) { toast(errText(e), true); }
  });
  SCENARIOS = PRESETS.map(p => ({ ...p, mine: false }));
  renderScenarios(PRESETS[0].name);
  applyPreset(PRESETS[0]);
  loadScenarios(PRESETS[0].name);

  // ----- live tree-size estimate -----
  let estSeq = 0;
  async function updateEstimate() {
    const seq = ++estSeq;
    let e;
    try { e = await api.pfEstimate(config()); }
    catch (err) {
      if (seq !== estSeq) return; // superseded by a newer request
      els.estimate.textContent = `\u26a0 ${err.message}`;
      els.estimate.classList.add('bad');
      return;
    }
    if (seq !== estSeq) return; // stale response: a newer one is coming
    const nodes = (+e.nodes).toLocaleString();
    const mb = e.arena_mb < 1 ? e.arena_mb.toFixed(1) : e.arena_mb.toFixed(0);
    const fmtBig = x => x >= 1e6 ? (x / 1e6).toFixed(1) + 'M'
      : x >= 1e4 ? Math.round(x / 1e3) + 'k' : (+x).toLocaleString();
    const caps = `this machine allows ${fmtBig(e.limit_nodes)} nodes / ` +
      (e.limit_arena_mb >= 1000 ? (e.limit_arena_mb / 1000).toFixed(1) + ' GB' : e.limit_arena_mb.toFixed(0) + ' MB');
    const borderline = e.ok &&
      (e.nodes > 0.9 * e.limit_nodes || e.arena_mb > 0.9 * e.limit_arena_mb);
    els.estimate.classList.toggle('warn', borderline);
    const capsTip = `${caps}. The caps track FREE RAM, so they move as other apps use memory ` +
      `(PREFLOP_MAX_NODES / PREFLOP_MAX_ARENA_MB env vars override). ` +
      `CPU arena limits, not GPU memory; GPU fit is checked when solving.`;
    const dot = t => ` <button type="button" class="info-dot" aria-label="How this tree-size estimate is measured" data-tip="${t}">?</button>`;
    if (e.ok && borderline) {
      els.estimate.classList.remove('bad');
      els.estimate.innerHTML =
        `tree \u2248 <b>${nodes}</b> nodes \u00b7 ${mb} MB CPU arenas \u2014 fits, <b>barely</b> \u26a0` +
        dot(capsTip + ' Little headroom: the build may still refuse if memory tightens \u2014 close big apps or trim a size.');
    } else if (e.ok) {
      els.estimate.classList.remove('bad');
      els.estimate.innerHTML =
        `tree \u2248 <b>${nodes}</b> nodes \u00b7 ${mb} MB CPU arenas \u2014 fits \u2713` + dot(capsTip);
    } else {
      els.estimate.classList.add('bad');
      els.estimate.innerHTML = (e.truncated
        ? `tree &gt; <b>${nodes}</b> nodes \u00b7 &gt; ${mb} MB CPU arenas \u2014 too big \u2717`
        : `tree \u2248 <b>${nodes}</b> nodes \u00b7 ${mb} MB CPU arenas \u2014 too big \u2717`) +
        dot(capsTip + ' Trim open sizes, re-raise multipliers, the raise cap, or limps.');
    }
  }
  window.addEventListener('focus', () => estSoon());
  let estT = null;
  const estSoon = () => { clearTimeout(estT); estT = setTimeout(updateEstimate, 350); };
  function syncStraddleControls() {
    const n = +els.players.value;
    els.straddleOn.disabled = n < 3;
    if (n < 3) els.straddleOn.checked = false;
    els.straddle.disabled = !els.straddleOn.checked;
    els.straddleNote.hidden = !els.straddleOn.checked;
    const amount = +els.straddle.value, positions = positionsFor(n);
    els.straddleNote.textContent = `${positions[0]} posts ${amount} bb · ${positions[1]} acts first · minimum open ${2 * amount} bb.`;
  }
  [els.players, els.straddleOn, els.straddle].forEach(el => el.addEventListener('change', syncStraddleControls));
  els.straddle.addEventListener('input', syncStraddleControls);
  syncStraddleControls();
  [els.players, els.stack, els.smallBlind, els.bigBlind, els.straddleOn, els.straddle, els.opens, els.mult, els.maxRaises,
   els.ante, els.limp, els.allin].forEach(el => {
    el.addEventListener('input', estSoon);
    el.addEventListener('change', estSoon);
  });
  updateEstimate();

  function config() {
    const n = +els.players.value;
    const positions = positionsFor(n);
    const posts = blindPosts(positions, currentScenario());
    const nums = s => s.split(',').map(x => parseFloat(x)).filter(x => x > 0);
    return {
      positions,
      stack: +els.stack.value || 100,
      posts,
      ...(els.straddleOn.checked ? { utg_straddle: true } : {}),
      ante: +els.ante.value || 0,
      limp: els.limp.checked,
      open_raises: nums(els.opens.value),
      raise_mults: nums(els.mult.value),
      ...positionSizing.config(),
      ...seatStacks.config(),
      ...icmControls.config(),
      max_raises: +els.maxRaises.value || 1,
      add_allin: els.allin.checked,
      rake_pct: +els.rakePct.value || 0,
      rake_cap: +els.rakeCap.value || 0,
      no_flop_no_drop: true,
      realization: els.leaf?.checked ? LEARNED_REALIZATION : DEFAULT_REALIZATION,
      ...leafNets.config(),
    };
  }

  // ----- build / solve -----

  // One progress strip, always under the solve step. Solve progress is real
  // (iterations and gap); a build cannot know its own progress, so it shows
  // the phase, the planned size and elapsed time, never a percentage.
  const SOLVE_ITERS = 3000;
  els.stop.after(els.prog); // stable position: under 3 · SOLVE, for build, load and resumed runs
  els.prog.dataset.tip = 'Build: phase, nodes and elapsed time. Solve: iterations and gap toward 0.005 bb.';
  const progFill = els.prog.querySelector('i');
  const progLab = els.prog.querySelector('span');
  let progPulse = null;
  function progressSet(pct, label) {
    clearInterval(progPulse); progPulse = null;
    els.prog.classList.remove('hidden');
    progFill.style.width = `${Math.max(0, Math.min(100, pct)).toFixed(1)}%`;
    progLab.textContent = label;
  }
  // Indeterminate build: the bar sweeps while the label carries the facts.
  function progressPulse(labelFn) {
    clearInterval(progPulse);
    els.prog.classList.remove('hidden');
    const t0 = performance.now();
    const tick = () => {
      const el = performance.now() - t0;
      progFill.style.width = `${(10 + (el % 1400) / 1400 * 80).toFixed(1)}%`;
      progLab.textContent = labelFn(el);
    };
    tick();
    progPulse = setInterval(tick, 150);
  }
  function progressHide() {
    clearInterval(progPulse); progPulse = null;
    els.prog.classList.add('hidden');
  }

  async function buildGame() {
    // pf_build stops-and-joins a running solve and replaces the session —
    // mirror the LOAD guards (and the postflop BUILD) instead of destroying
    // a solve without a word
    if (S.solveRunning) {
      if (!confirm('A solve is RUNNING — building a new game stops and discards it. Continue?')) return false;
    } else if (S.built && lastIter > 0 && !S.gameSaved &&
        !confirm('The current game has not been saved — building a new game discards its solve. Continue?')) {
      return false;
    }
    let cfg;
    try { cfg = config(); } catch (e) { toast(e.message, true); return false; }
    els.build.disabled = true;
    els.solve.disabled = true;
    els.buildInfo.textContent = '';
    progressPulse(() => 'counting · tree size…');
    let expected = 0;
    try { expected = (await api.pfEstimate(cfg)).nodes || 0; } catch { /* build reports errors */ }
    const eqCold = !localStorage.getItem('pfl-eq-built');
    const t0 = performance.now();
    progressPulse(el => `building · ${eqCold ? 'equity cache' : 'allocating'} · ` +
      `${expected ? `${expected.toLocaleString()} nodes · ` : ''}${Math.round(el / 1000)} s`);
    try {
      const info = await api.pfBuild(cfg, els.eq3?.checked ? 'three_way_table_v1' : null);
      S.multiwayModel = info.multiway_equity_model || S.multiwayModel;
      renderModelStrip();
      icmControls.showSummary(info.icm);
      localStorage.setItem('pfl-eq-built', '1');
      S.built = true;
      S.activeModel = cfg.realization;
      S.gameSaved = false; // fresh tree: nothing of it is on disk
      S.savedName = null;
      S.builtCfg = JSON.stringify(cfg);
      S.formCfg = JSON.stringify(cfg);
      S.positions = cfg.positions;
      S.cursor = [];
      S.lineP = [];
      S.model = {
        seats: cfg.positions.map(() => ({ mode: 'live', profile: null, implied: null, label: 'Solver' })),
        hero: null,
      };
      S.applied = null;
      S.appliedSeatSigs = S.model.seats.map(seatSigOf);
      S.appliedHero = null;
      S.heroPending = false;
      S.lastApplyWasSolve = false;
      S.postflopDirty = false;
      S.engineFrozen = null;
      S.lastGaps = null;
      closeEditor();
      renderModel();
      els.buildInfo.textContent =
        `${info.nodes.toLocaleString()} nodes · ${info.action_nodes.toLocaleString()} decision points · ${info.arena_mb.toFixed(0)} MB CPU arenas`;
      progressSet(100, 'built \u2713');
      setTimeout(() => { if (S.lastState !== 'running') progressHide(); }, 1500);
      lastIter = 0;
      renderSaveState();
      renderModelStrip();
      clearRightPanel(); // uniform pre-solve strategies aren't worth showing
      startPolling();
      return true;
    } catch (e) {
      toast(e.message, true);
      els.buildInfo.textContent = '';
      progressHide();
      updateEstimate(); // re-sync the size line with the caps that refused us
      return false;
    } finally {
      clearInterval(progPulse); progPulse = null;
      els.build.disabled = false;
      els.solve.disabled = false;
    }
  }
  els.build.addEventListener('click', buildGame);

  // SOLVE builds first when there's nothing built yet or the settings
  // changed since the last build — one button does the right thing.
  els.solve.addEventListener('click', async () => {
    els.solve.disabled = true;
    try {
      if (!S.built || S.formCfg !== JSON.stringify(config())) {
        if (!(await buildGame())) return;
      }
      // staged table/hero edits apply here, so SOLVE is always one button:
      // the table part no-ops when nothing changed. A deferred hero is
      // re-applied when the run ends (the engine needs a solved table).
      // postflopDirty: tendencies edits don't reset learning on either side,
      // but the engine's profile copy is stale until re-sent — push it so
      // saves/exports carry the edited player.
      if (S.model && (pendingChanges().length || S.postflopDirty)) {
        if (!(await applyModel({ fromSolve: true, quiet: true }))) return;
      }
      // the table in the engine is the one being solved, whatever was staged
      S.lastApplyWasSolve = true;
      renderApplyState();
      // every seat modeled/frozen and no hero = the solver has nothing to
      // learn: the grids will just show the profiles.
      if (S.model && S.model.hero == null && S.model.seats.every(m => m.mode !== 'live')) {
        toast('Every seat is fixed and no HERO is set — nothing to solve; the grids show those profiles.', true);
      }
      progressSet(0, 'solving');
      const request = { iterations: SOLVE_ITERS, check_every: 50, target_gap: 0.005 };
      await api.pfSolve(earlyPreviewRequest(request, previewCheck.checked, await previewCapability));
      S.gameSaved = false; // strategies are moving away from any on-disk copy
      renderSaveState();
      startPolling();
    } catch (e) { toast(errText(e), true); progressHide(); }
    finally { els.solve.disabled = false; }
  });
  els.stop.addEventListener('click', () => {
    els.stop.disabled = true;
    progLab.textContent = 'stopping…';
    api.pfStop().catch(e => {
      // a swallowed failure would leave the button dead at "stopping…"
      els.stop.disabled = false;
      toast(`stop failed — ${errText(e)}`, true);
    });
  });

  // ----- saved games: full session snapshots on disk -----

  // The server strips filename-hostile characters before writing (main.rs
  // pf_game_path keeps letters/digits, space, - and _, then trims), so the
  // overwrite check must compare the REAL on-disk name: 'f/o/o' saves as
  // 'foo'. Replicated here; the server stays authoritative.
  const sanitizeGameName = s => String(s).replace(/[^\p{L}\p{N} _-]/gu, '').trim();

  let savedGameNames = []; // known on-disk names, for the overwrite confirm
  async function refreshSavedGames() {
    try {
      const list = await api.pfSavedGames();
      savedGameNames = list;
      els.savedSel.innerHTML = '<option value="">load a saved game…</option>' +
        list.map(n => `<option>${esc(n)}</option>`).join('');
    } catch { /* server not up yet */ }
  }
  refreshSavedGames();

  els.saveGame.addEventListener('click', async () => {
    if (!S.built || lastIter < 1) return toast('solve something first — a save stores the solved strategies', true);
    if (pendingChanges().length) return toast('APPLY the unapplied table changes first — SAVE stores the engine’s table', true);
    const def = `${S.positions.length}-max ${els.stack.value}bb iter${lastIter}`;
    const raw = window.prompt('save game as…', def);
    if (!raw || !raw.trim()) return;
    const name = sanitizeGameName(raw);
    if (!name) return toast('give the save a name (letters, digits, - _ space)', true);
    els.saveGame.disabled = true;
    try {
      // overwrite check against the on-disk list, refreshed first so a save
      // made elsewhere (other tab, earlier session) still gets a warning
      await refreshSavedGames();
      if (savedGameNames.includes(name) &&
          !confirm(`"${name}" already exists — overwrite it?`)) return;
      // tendencies edited since the last apply live only client-side; the
      // save stores the SERVER's profiles — push them first (a postflop-only
      // re-send is free: set_table strips postflop from its reset comparison)
      if (S.postflopDirty && !(await applyModel())) return;
      const out = await api.pfSaveGame(name);
      S.gameSaved = true; // it IS the on-disk copy now
      S.savedName = name;
      renderSaveState();
      toast(`game saved — "${name}" (iter ${out.iteration})`);
      refreshSavedGames();
    } catch (e) { toast(e.message, true); }
    finally { els.saveGame.disabled = false; renderSaveState(); }
  });

  els.savedSel.addEventListener('change', async () => {
    const name = els.savedSel.value;
    els.savedSel.value = '';
    if (!name) return;
    // pf_load_game silently stops-and-joins a running solve and replaces the
    // session — mirror the postflop load guards before letting it
    if (S.solveRunning) {
      if (!confirm('A solve is RUNNING — loading a game stops and discards it. Continue?')) return;
    } else if (S.built && lastIter > 0 && !S.gameSaved &&
        !confirm('The current game has not been saved — loading discards its solve. Continue?')) {
      return;
    }
    progressSet(40, `loading “${name}”…`);
    try {
      const out = await api.pfLoadGame(name);
      await applyLoadedGame(name, out);
      progressSet(100, 'loaded \u2713');
      setTimeout(() => { if (S.lastState !== 'running') progressHide(); }, 1500);
    } catch (e) { progressHide(); toast(e.message, true); }
  });

  /** Restore the whole lab session from a loaded game: config form, built
   *  state, seat models (profiles/frozen), and the solved tree view. */
  async function applyLoadedGame(name, out, opts = {}) {
    const cfg = out.config;
    els.players.value = cfg.positions.length;
    els.stack.value = cfg.stack;
    els.smallBlind.value = cfg.posts[cfg.positions.indexOf('SB')] ?? 0.5;
    els.bigBlind.value = cfg.posts[cfg.positions.indexOf('BB')] ?? 1;
    els.straddleOn.checked = !!cfg.utg_straddle;
    els.straddle.value = cfg.utg_straddle ? cfg.posts[0] : 2;
    syncStraddleControls();
    els.opens.value = (cfg.open_raises || []).join(',');
    els.mult.value = (cfg.raise_mults || []).join(',');
    positionSizing.load(cfg);
    seatStacks.load(cfg);
    els.maxRaises.value = cfg.max_raises;
    els.limp.checked = !!cfg.limp;
    els.allin.checked = !!cfg.add_allin;
    els.ante.value = cfg.ante || 0;
    els.rakePct.value = cfg.rake_pct || 0;
    els.rakeCap.value = cfg.rake_cap || 0;
    // after the rake fields: ICM shows 0 there while it is on, and reads the
    // loaded numbers as the ones to give back when it is turned off
    icmControls.load(cfg);
    S.activeModel = cfg.realization || 'static';
    if (els.leaf) els.leaf.checked = S.activeModel === LEARNED_REALIZATION;
    leafNets.load(cfg);
    S.built = true;
    syncScenarioSelection();
    S.gameSaved = opts.onDisk !== false; // a LOADED game IS the on-disk copy; an adopted live session may not be
    S.savedName = opts.onDisk !== false ? name : null;
    S.builtCfg = JSON.stringify(cfg);
    S.formCfg = JSON.stringify(config());
    S.positions = cfg.positions;
    S.cursor = [];
    S.lineP = [];
    S.lineHist = null;
    // A game saved in HERO mode stores the hero frozen mask (everyone but
    // the hero), not the user's table model — materializing that mask as
    // explicit Frozen seat models would diverge from the engine the moment
    // hero turns off (the engine restores its pre-hero flags; the client
    // would keep phantom Frozen rows). pf_load_game seeds /status with the
    // loaded hero, so read it first: with hero ON, frozen flags are
    // hero-induced, not seat models.
    let hero = null;
    try {
      const hst = await api.pfStatus();
      if (hst && hst.hero !== undefined) hero = hst.hero == null ? null : +hst.hero;
    } catch { /* older server: no hero on /status — flags stay explicit */ }
    S.model = {
      seats: (out.seats || []).map(st => st.profile
        // painted: any paint in a loaded profile happened in an earlier
        // session, so treat its buckets as painted — a stat edit must not
        // silently regenerate over them (GENERATE stays explicit)
        ? { mode: 'ruled', profile: st.profile, implied: null, label: st.profile.name,
            stats: st.profile.response?.source_stats || st.profile.stats || null,
            postflop: st.profile.postflop || null, selValue: `saved:${st.profile.name}`,
            painted: true }
        : (st.frozen && hero == null)
          ? { mode: 'frozen', profile: null, implied: null, label: 'Frozen', selValue: 'frozen' }
          : { mode: 'live', profile: null, implied: null, label: 'Solver', selValue: 'live' }),
      hero,
    };
    S.applied = S.model.seats.map(m => m.mode);
    S.appliedSeatSigs = S.model.seats.map(seatSigOf);
    S.appliedHero = hero; // adopted engine truth (frozen arrives via /status)
    S.heroPending = false;
    S.lastApplyWasSolve = false;
    S.postflopDirty = false;
    S.engineFrozen = null;
    S.lastGaps = null;
    S.multiwayModel = out.multiway_equity_model || null;
    closeEditor();
    renderModel();
    renderModelStrip();
    lastIter = out.iteration;
    renderSaveState();
    icmControls.showSummary(out.icm);
    els.buildInfo.textContent =
      `${out.nodes.toLocaleString()} nodes · ${out.arena_mb.toFixed(0)} MB CPU arenas · loaded “${name}” at iter ${out.iteration}`;
    updateEstimate();
    startPolling();
    refresh();
    if (!opts.quiet) toast(`loaded “${name}” — iter ${out.iteration}; RE-SOLVE continues converging`);
  }

  function startPolling() {
    if (S.polling) clearInterval(S.polling);
    S.polling = setInterval(poll, 1000);
    poll();
  }
  let lastIter = -1;
  let lastPublicationKey = '';
  async function poll() {
    const he = heroEpoch; // hero changes during this fetch make st.hero stale
    let st;
    try { st = await api.pfStatus(); } catch { return; }
    if (!st.state) return;
    if (st.multiway_equity_model !== undefined && st.multiway_equity_model !== S.multiwayModel) {
      S.multiwayModel = st.multiway_equity_model;
      renderModelStrip();
    }
    // Engine truth: newer servers report "hero" (number|null) and "frozen"
    // (bool array) on /status. Absent fields mean an older server — treat
    // them as unknown, never as hero-off.
    if (S.model && st.hero !== undefined && heroBusy === 0 && he === heroEpoch) {
      const srvHero = st.hero == null ? null : +st.hero;
      if (S.heroPending) {
        // waiting for a deferred hero: clear the flag once the engine has it
        if (srvHero === S.model.hero) { S.heroPending = false; S.appliedHero = srvHero; }
      } else if (S.model.hero === S.appliedHero) {
        // nothing staged: adopt the engine's hero
        if (srvHero !== S.model.hero) S.model.hero = srvHero;
        S.appliedHero = srvHero;
      } else {
        // a staged hero stays chosen; record the engine's actual state
        S.appliedHero = srvHero;
      }
    }
    if (S.model && Array.isArray(st.frozen) && st.frozen.length === S.positions.length) {
      S.engineFrozen = st.frozen; // engine-truth lock badges for the ribbon
    }
    trustDial?.update(st);
    const running = st.state === 'running';
    if (running !== S.solveRunning) {
      // the server refuses table/hero changes mid-solve (409) — mirror it
      S.solveRunning = running;
      els.applyBtn.disabled = running;
      previewCheck.disabled = running;
      if (!running) previewCapability.then(supported => { previewCheck.disabled = S.solveRunning || !supported; });
    }
    let gapChip = null;
    if (st.gaps && st.gaps.length) {
      gapChip = statusChip(`gap ${st.gap_total.toFixed(4)} \u2192 0.0050`,
        'Best-response gap: how much each seat could still gain by deviating (bb). Only seats still learning converge; ' +
        'a frozen or ruled seat’s gap is its BLEED against its pinned strategy. ' +
        st.gaps.map((g, i) => `${S.positions[i] || i}: ${g.toFixed(4)}`).join(' · '));
      S.lastGaps = st.gaps;
    } else if (st.accuracy_iteration === null) {
      S.lastGaps = null; // a changed model must not retain the old gap claim
    }
    renderModel(); // cheap: it skips unless its rendered state changed
    const engine = st.gpu ? statusChip('\u26a1 GPU', 'Solving on CUDA.')
      : statusChip('CPU', st.gpu_note || 'Solving on CPU.');
    const err = st.error || ''; // a crashed worker is not a STOP
    // the engine could not load the calibrated fit and priced with the static
    // model: say so every time, and toast it once per session
    // Keep fallback diagnostics without reintroducing retired model choices.
    const realizationNote = (st.realization_note || '').replace(
      'balanced uses raw equity; legacy calibrated uses positional values',
      currentModel(S.activeModel)
        ? 'using showdown-equity estimates until the fit is available'
        : 'using the saved game’s fallback values until the fit is available');
    if (st.realization_note && S.lastRealizationNote !== st.realization_note) {
      S.lastRealizationNote = st.realization_note;
      toast(realizationNote, true);
    }
    const shown = publishedIteration(st);
    const chips = [statusChip(st.state, 'Solver state.')];
    chips.push(statusChip(`iter ${st.iteration}`, 'Iterations completed; the counter survives resumes and loads.'));
    if (st.published_iteration !== undefined) {
      chips.push(statusChip(`displayed ${shown}`, 'Iteration of the strategy snapshot on screen.'));
    }
    if (gapChip) chips.push(gapChip);
    if (st.accuracy_iteration != null) {
      chips.push(statusChip(`measured @ ${st.accuracy_iteration}`, 'Iteration of the last accuracy measurement.'));
    }
    chips.push(engine);
    statusChips.replaceChildren(...chips);
    const warnings = [err, realizationNote, st.preview_note || ''].filter(Boolean);
    statusWarn.textContent = warnings.join(' \u00b7 ');
    statusWarn.classList.toggle('hidden', !warnings.length);
    statusWarn.style.color = err ? '#e8847a' : '';
    els.solve.textContent = st.state === 'done' || st.state === 'stopped' ? 'RE-SOLVE' : 'SOLVE';
    els.solve.classList.toggle('hidden', st.state === 'running');
    els.stop.classList.toggle('hidden', st.state !== 'running');
    // run timer: wall-clock since this run started (or since the page found
    // it already running)
    const secs = Math.max(0, Math.round((Date.now() - (S.runStart || Date.now())) / 1000));
    const clock = `${Math.floor(secs / 60)}:${String(secs % 60).padStart(2, '0')}`;
    if (st.state === 'running') {
      if (S.lastState !== 'running') {
        S.gap0 = null;
        S.runPct = 0;
        // st.iteration is the solver's CUMULATIVE counter (it survives
        // resumes and save/load) — baseline it so the bar measures THIS run
        S.runBase = st.iteration;
        S.runStart = Date.now();
      }
      if (S.gap0 == null && st.gap_total > 0) S.gap0 = st.gap_total;
      // Progress is convergence toward the 0.005 bb gap target (log scale),
      // with the iteration cap as a floor; monotonic within a run. The 3000
      // maximum is a safety net, not the destination — most solves stop at
      // the target long before it.
      const gapProg = S.gap0 > 0.005 && st.gap_total > 0
        ? Math.log(S.gap0 / st.gap_total) / Math.log(S.gap0 / 0.005) : 0;
      const runIter = Math.max(0, st.iteration - (S.runBase || 0));
      S.runPct = Math.max(S.runPct,
        100 * Math.max(runIter / SOLVE_ITERS, Math.min(1, Math.max(0, gapProg))));
      let label;
      if (st.phase === 'publishing') {
        label = `solving · iter ${st.iteration} · ${clock} · publishing preview…`;
      } else if (st.phase === 'measuring') {
        label = `solving · iter ${st.iteration} · ${clock} · measuring accuracy…`;
      } else if (st.gap_total > 0) {
        label = `solving · iter ${st.iteration} · ${clock} · gap ${st.gap_total.toFixed(4)} \u2192 0.0050`;
      } else {
        label = `solving · iter ${st.iteration} · ${clock} · ${shown >= 2 ? `preview at ${shown}; accuracy every 50 iter` : previewCheck.checked ? "preparing first learned preview" : "first strategy at accuracy checkpoint"}`;
      }
      progressSet(S.runPct, label);
    } else if (S.lastState === 'running') {
      // a run just ended (target hit, max iterations, STOP — or a crash,
      // which the engine reports in `error` and must not read as a STOP)
      els.stop.disabled = false;
      S.runBase = null;
      S.runStart = null;
      if (st.error) {
        progressSet(100, `stopped — ${st.error}`);
        toast(st.error, true);
      } else {
        progressSet(100, `done · ${solveCompletionLabel(st)} · ${clock}`);
      }
      setTimeout(() => { if (S.lastState !== 'running') progressHide(); }, 1200);
      if (S.heroPending && S.model && S.model.hero != null && st.iteration > 0) {
        reapplyHero(); // deferred hero: the table now has a solve to freeze
      }
    }
    S.lastState = st.state;
    const nextPublicationKey = publicationKey(st);
    if (nextPublicationKey !== lastPublicationKey && S.built) {
      lastPublicationKey = nextPublicationKey;
      lastIter = shown;
      renderSaveState();
      refresh(); // only a coherent published snapshot changed
    }
    if (st.state !== 'running' && S.polling && shown === lastIter) {
      clearInterval(S.polling);
      S.polling = null;
    }
  }

  // ----- node navigation / rendering -----
  let ribbonCursor = null;
  let revealRibbonCursor = false;
  function updateRibbonScroll() {
    const el = els.ribbon;
    const width = el.parentElement.clientWidth;
    if (!width) return; // the lab tab is hidden
    // Compare with the full wrapper, so showing the arrows cannot cause a
    // resize/show/hide loop at the overflow threshold.
    const overflow = el.scrollWidth > width + 2;
    els.ribbonLeft.classList.toggle('hidden', !overflow);
    els.ribbonRight.classList.toggle('hidden', !overflow);
    if (revealRibbonCursor) {
      const current = el.querySelector('.current');
      if (current) {
        const bounds = el.getBoundingClientRect(), selected = current.getBoundingClientRect();
        if (selected.left < bounds.left) el.scrollLeft -= bounds.left - selected.left;
        else if (selected.right > bounds.right) el.scrollLeft += selected.right - bounds.right;
      }
      revealRibbonCursor = false;
    }
    els.ribbonLeft.disabled = el.scrollLeft <= 1;
    els.ribbonRight.disabled = el.scrollLeft >= el.scrollWidth - el.clientWidth - 1;
  }
  for (const [button, direction] of [[els.ribbonLeft, -1], [els.ribbonRight, 1]]) {
    button.addEventListener('click', () => els.ribbon.scrollBy({
      left: direction * Math.max(140, els.ribbon.clientWidth * .7),
      behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
    }));
  }
  els.ribbon.addEventListener('scroll', updateRibbonScroll, { passive: true });
  // A click must not leave focus on the strip: the next key press of any kind would then draw its
  // focus outline around the whole ribbon, a second border outside the spot being viewed. Focus from
  // the keyboard stays (the arrow keys scroll a long line).
  els.ribbon.addEventListener('mousedown', () => setTimeout(() => {
    if (document.activeElement === els.ribbon) els.ribbon.blur();
  }, 0));
  // Trackpads and the native scrollbar work directly. A vertical mouse wheel
  // also moves a long ribbon, but still scrolls the page at either end.
  els.ribbon.addEventListener('wheel', event => {
    if (event.ctrlKey || Math.abs(event.deltaX) >= Math.abs(event.deltaY)) return;
    const delta = event.deltaY * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? els.ribbon.clientWidth : 1);
    const max = els.ribbon.scrollWidth - els.ribbon.clientWidth;
    if ((delta < 0 && els.ribbon.scrollLeft > 0) || (delta > 0 && els.ribbon.scrollLeft < max - 1)) {
      els.ribbon.scrollLeft += delta;
      event.preventDefault();
    }
  }, { passive: false });
  new ResizeObserver(updateRibbonScroll).observe(els.ribbon);

  function clearRightPanel() {
    previewBanner.classList.add('hidden');
    reachWarning.className = 'pfl-reach-warning hidden';
    els.ribbon.innerHTML = '';
    ribbonCursor = null;
    updateRibbonScroll();
    els.nodeTitle.textContent = '';
    renderModelEvidence(nodeEvidence, null);
    els.seats.innerHTML = '';
    S.view = null;
    renderExportCard();
    hideGrid();
    rangeLab?.update(null);
  }

  let refreshSeq = 0;
  async function refresh() {
    if (canon.on) return refreshCanonical();
    if (!S.built) return;
    if (lastIter < 2) { clearRightPanel(); return; } // nothing meaningful before solving
    // poll-driven and click-driven refreshes race each other: an older
    // response resolving last must not repaint over the newer one
    const seq = ++refreshSeq;
    try {
      const needLine = S.cursor.length !== S.lineP.length;
      const [view, lineView] = await Promise.all([
        api.pfNode(S.cursor),
        needLine ? api.pfNode(S.lineP) : Promise.resolve(null),
      ]);
      if (seq !== refreshSeq) return; // stale: superseded while in flight
      S.view = formatPreflopView(view, JSON.parse(S.builtCfg || '{}'));
      S.lineHist = lineView ? formatPreflopView(lineView, JSON.parse(S.builtCfg || '{}')).history : S.view.history;
    } catch (e) { if (seq === refreshSeq) toast(e.message, true); return; }
    renderRibbon();
    renderNode();
  }

  /** Chosen steps of the line up to the cursor: [{pos, label, kind}]. */
  function takenSteps(upTo) {
    const cfg = !canon.on && S.builtCfg ? JSON.parse(S.builtCfg) : {};
    const out = cfg.utg_straddle ? [{pos: cfg.positions[0], label: `Straddle ${cfg.posts[0]} bb`, kind: 'straddle'}] : [];
    (S.lineHist || []).slice(0, upTo).forEach(h => {
      if (h.chosen != null && h.actions[h.chosen]) {
        const a = h.actions[h.chosen];
        out.push({ pos: h.actor_pos, label: a.label, kind: a.kind });
      }
    });
    return out;
  }

  // Browse-style ribbon: one segment per decision along the FULL line, every
  // available action as a chip with its frequency. Clicking the taken chip
  // (or the segment) views that point without losing the line; clicking a
  // different chip branches the line there.
  function renderRibbon() {
    syncModelColors();
    const el = els.ribbon;
    const scrollLeft = el.scrollLeft;
    el.innerHTML = '';
    const cfg = !canon.on && S.builtCfg ? JSON.parse(S.builtCfg) : {};
    if (cfg.utg_straddle) {
      const post = document.createElement('div');
      post.className = 'hist-seg pfl-straddle-post';
      post.innerHTML = `<div class="hist-head"><span>${esc(cfg.positions[0])}</span></div><div class="hist-chip">Straddle ${cfg.posts[0]} bb</div>`;
      post.dataset.tip = 'Live forced post. Preflop action starts at the next seat; postflop position is unchanged.';
      el.appendChild(post);
    }
    const hist = S.lineHist || [];
    const cursor = S.cursor.length;
    // spots the solve never really worked on (Range Lab charts are not a solve: no marks)
    const levels = canon.on ? [] : segmentLevels(hist);
    hist.forEach((h, d) => {
      const seg = document.createElement('div');
      const unsolved = levels[d] === 'unsolved';
      seg.className = 'hist-seg' + (d === cursor ? ' current' : '') + (unsolved ? ' unsolved' : '');
      const head = document.createElement('div');
      head.className = 'hist-head';
      if (h.kind === 'action') {
        const si = canon.on ? -1 : S.positions.indexOf(h.actor_pos);
        // lock badge: what the client applied, plus engine-truth freezes
        // (e.g. hero mode pins the other seats) when the server reports them
        const locked = si >= 0 && ((S.applied && S.applied[si] !== 'live') ||
          (S.engineFrozen && S.engineFrozen[si]));
        const adaptive = S.model?.seats[si]?.profile?.response?.adaptive_from != null && !S.engineFrozen?.[si];
        head.title = adaptive ? 'Modeled ordinary actions; adaptive large-bet responses' : '';
        head.innerHTML = `<span>${adaptive ? '↔ ' : locked ? '🔒 ' : ''}${esc(h.actor_pos)}</span><b>${h.pot.toFixed(1)}</b>`;
        const position = head.querySelector('span');
        position.dataset.modelSeat = si;
        position.style.color = seatModelColor(si);
      } else {
        head.innerHTML = h.kind === 'pot_share'
          ? `<span>FLOP</span><b>${h.pot.toFixed(1)}</b>`
          : `<span>END</span><b>${h.pot.toFixed(1)}</b>`;
      }
      seg.appendChild(head);
      seg.dataset.tip = d === cursor
        ? ''
        : 'Click to view this point (the line is kept).';
      if (unsolved) seg.dataset.tip = (seg.dataset.tip ? seg.dataset.tip + ' ' : '') +
        'Not solved: the line that leads here is one the solution almost never plays.';
      if (h.forced) {
        seg.classList.add('forced');
        seg.dataset.tip = `Range Lab has no chart for ${h.actor_pos} here; its later charts assume ${h.actor_pos} folds.`;
      }
      seg.addEventListener('click', () => {
        if (d !== cursor) { S.cursor = S.lineP.slice(0, d); refresh(); }
      });
      if (h.kind === 'action') {
        h.actions.forEach((a, k) => {
          const chip = document.createElement('div');
          const rare = !canon.on && !h.strategy_note && !(a.freq >= RARE_STEP);
          chip.className = 'hist-chip' + (h.chosen === k ? ' taken' : '') + (rare ? ' rare-step' : '');
          chip.classList.add('has-frequency');
          const actionLabel = document.createElement('span');
          actionLabel.textContent = a.label;
          const frequency = document.createElement('span');
          frequency.className = 'hist-frequency';
          frequency.textContent = h.strategy_note ? "—" : frequencyText(a.freq);
          chip.append(actionLabel, frequency);
          chip.dataset.tip = h.chosen === k
            ? `${h.actor_pos} takes ${a.label} ${frequencyDetail(a.freq)} of the time here. Click to view the moment just after it.`
            : `${h.actor_pos}: ${a.label} ${frequencyDetail(a.freq)} of the time. Click to ${h.chosen == null ? 'take' : 'branch the line onto'} this action.`;
          if (h.strategy_note) chip.dataset.tip = h.strategy_note;
          else if (a.freq === 0) chip.dataset.tip += ' Zero modeled frequency: its continuation may have no solved strategy.';
          else if (rare) chip.dataset.tip += ` The solution has all but dropped this action, so the spots after it are not solved. To study them, give ${h.actor_pos} a player model or a lock that takes it, then solve again.`;
          if (a.sizingHint) chip.dataset.tip += ` ${a.sizingHint}`;
          chip.addEventListener('click', (e) => {
            e.stopPropagation();
            if (h.chosen === k) {
              S.cursor = S.lineP.slice(0, d + 1); // view after the taken action
            } else {
              S.lineP = [...S.lineP.slice(0, d), k]; // branch (or advance) here
              S.cursor = S.lineP.slice();
            }
            refresh();
          });
          seg.appendChild(chip);
        });
      } else {
        const chip = document.createElement('div');
        chip.className = 'hist-chip taken';
        chip.textContent = h.kind === 'pot_share' ? 'flop reached' : 'hand over';
        seg.appendChild(chip);
      }
      el.appendChild(seg);
    });
    el.scrollLeft = scrollLeft;
    const cursorKey = JSON.stringify(S.cursor);
    revealRibbonCursor ||= cursorKey !== ribbonCursor;
    ribbonCursor = cursorKey;
    updateRibbonScroll();
  }

  function actionColors(actions) {
    // raises darken with size rank (the tree lists them ascending); a jam
    // always takes the overbet shade so it reads the same at every node
    const raises = actions.filter(a => !COLORS[a.kind] && a.kind !== 'jam').length;
    let r = 0;
    return actions.map(a => {
      if (COLORS[a.kind]) return COLORS[a.kind];
      if (a.kind === 'jam') return RAISE_SHADES[3];
      // 1 size -> small; 2 -> small, medium; 3+ -> small … large
      const k = raises <= 1 ? 0 : Math.min(2, Math.round((r / (raises - 1)) * 2));
      r += 1;
      return RAISE_SHADES[k];
    });
  }

  function renderNode() {
    const v = S.view;
    previewBanner.textContent = publicationLabel(v.publication);
    // a line the solution (almost) never plays is not solved: say so above the grid, in words
    reachWarning.replaceChildren();
    const lineWarning = canon.on || v.strategy_note ? null : lineNote(lineStatus(v));
    reachWarning.className = `pfl-reach-warning ${lineWarning ? lineWarning.level : 'hidden'}`;
    if (lineWarning) {
      for (const [tag, text] of [['strong', lineWarning.title], ['span', lineWarning.text], ['em', lineWarning.fix]]) {
        if (!text) continue;
        const part = document.createElement(tag);
        part.textContent = text;
        reachWarning.append(part, ' '); // the space keeps the parts apart when read out or copied
      }
    }
    for (const el of [els.grid, els.legend]) el.classList.toggle('pfl-unsolved', lineWarning?.level === 'unsolved');
    previewBanner.classList.toggle('hidden', !v.publication);
    previewBanner.classList.toggle('converged', !!v.publication?.converged);
    renderModelEvidence(nodeEvidence, v.model_evidence);
    rangeLab?.update(canon.on ? null : matchContext(v, JSON.parse(S.builtCfg || 'null')));

    // seats strip: only while there's action (the ribbon carries the rest)
    els.seats.innerHTML = v.kind !== 'action' ? '' : v.positions.map((p, i) => {
      const dead = !v.live[i];
      const cur = v.actor === i;
      return `<span class="pfl-seat${dead ? ' dead' : ''}${cur ? ' cur' : ''}">${esc(p)} <small>${v.invested[i].toFixed(1)}</small></span>`;
    }).join('');

    if (v.strategy_note) {
      hideGrid();
      renderExportCard();
      els.nodeTitle.textContent = v.actor_pos ? `${v.actor_pos} · strategy unavailable` : 'Unreachable continuation';
      els.gridCap.innerHTML = `<div class="pfl-unavailable" role="status"><strong>${canon.on ? "No Range Lab chart here" : v.strategy_note.startsWith("Unreachable") ? "This line has zero modeled reach" : "No solved strategy at this point"}</strong><p>${esc(v.strategy_note)}</p></div>`;
      return;
    }
    let continuation = null;
    if (v.kind === 'action') {
      const colors = actionColors(v.actions);
      // headline: who acts, and what (if anything) they're facing
      const past = takenSteps(S.cursor.length);
      const lastAggr = [...past].reverse().find(s => s.kind === 'raise' || s.kind === 'jam');
      const facing = lastAggr && lastAggr.pos !== v.actor_pos
        ? ` — facing ${lastAggr.pos}'s ${lastAggr.label}`
        : lastAggr && lastAggr.pos === v.actor_pos
          ? '' // their own raise came back around (someone called/limped behind)
          : past.length ? ' — unraised pot' : ' — first to act';
      els.nodeTitle.textContent = `${v.actor_pos} to act${facing}`;
      S.colors = colors;
      els.rangeSeg.innerHTML = '';
      els.grid.classList.remove('hidden');
      els.fillSeg.classList.remove('hidden');
      paintGrid();
      renderLegend(v, colors);
      els.gridCap.innerHTML =
        `Grid = <b>${esc(v.actor_pos)}</b> · hover a cell for exact numbers.`;
      if (canon.on) {
        els.gridCap.innerHTML =
          `Grid = <b>${esc(v.actor_pos)}</b>'s Range Lab chart at this point (${esc(v.game.label)} · ${esc(v.game.variant_label)} · ${v.game.depth} bb)` +
          (v.chart ? `: <b>${esc(v.chart.family_label)}</b>, ${esc(v.chart.label)}` : '') +
          `.` +
          (v.note ? `<div class="pfl-context-note">${esc(v.note)}</div>` : '');
      }
      if (v.contextual_prediction && !v.model_evidence) {
        const model = v.contextual_prediction;
        const note = document.createElement('div');
        note.className = 'pfl-context-note';
        note.textContent = `Contextual v1 · ${model.active ? 'using this situation' : 'fallback / override'}${model.nominal_price != null ? ` · call price ${(model.nominal_price * 100).toFixed(1)}%` : ''}. ${model.note}`;
        els.gridCap.appendChild(note);
      }
    } else if (v.kind === 'fold_win') {
      const wi = v.live.findIndex(x => x);
      els.nodeTitle.textContent = `everyone folded — ${v.positions[wi]} takes ${v.pot.toFixed(1)} bb`;
      // still worth seeing: the range the winner got through with
      S.rangeSeat = wi;
      els.rangeSeg.innerHTML = '';
      els.grid.classList.remove('hidden');
      els.fillSeg.classList.remove('hidden');
      paintGrid();
      els.legend.innerHTML =
        `<span class="key"><i style="background:#f28c26"></i>${esc(v.positions[wi])}'s range when everyone folds — bar height = share of combos</span>`;
      els.gridCap.innerHTML = '';
    } else {
      const live = v.positions.filter((_, i) => v.live[i]);
      els.nodeTitle.textContent =
        `FLOP: ${live.join(' vs ')} · pot ${v.pot.toFixed(1)} bb` +
        (v.side_pots?.length
          ? ' · ' + v.side_pots.map((sp, k) => `${k ? `side pot ${k}` : 'main'} ${sp.amount.toFixed(1)} (${sp.seats.join(', ')})`).join(' · ')
          : '') +
        (v.spr != null ? ` · SPR ${v.spr.toFixed(1)}` : '');
      // keep the hand grid up: it shows each live player's arriving range
      const liveSeats = v.positions.map((_, i) => i).filter(i => v.live[i]);
      if (!liveSeats.includes(S.rangeSeat)) S.rangeSeat = liveSeats[0];
      els.rangeSeg.innerHTML = '';
      liveSeats.forEach(i => {
        const b = document.createElement('button');
        b.className = S.rangeSeat === i ? 'active' : '';
        b.textContent = v.positions[i];
        b.addEventListener('click', () => {
          S.rangeSeat = i;
          renderNode();
        });
        els.rangeSeg.appendChild(b);
      });
      els.grid.classList.remove('hidden');
      els.fillSeg.classList.remove('hidden');
      paintGrid();
      els.legend.innerHTML =
        `<span class="key"><i style="background:#f28c26"></i>${esc(v.positions[S.rangeSeat])}'s arriving range — bar height = share of that hand's combos reaching this flop</span>`;
      els.gridCap.innerHTML = '';
      if (v.continuation) {
        const estimate = v.continuation;
        const estimateNote = estimate.model === 'calibrated'
          ? estimate.note.replace('The calibrated model', 'This saved game’s value model')
          : estimate.note;
        const detail = document.createElement('details');
        detail.className = 'pfl-continuation';
        const rows = [
          ['Pot', estimate.pot_bb],
          ...estimate.players.map(p => [`${p.position} estimated value`, p.value_bb]),
          ['Combined value', estimate.total_value_bb],
          ['Unallocated amount', estimate.unallocated_bb],
        ];
        detail.innerHTML = `<summary>Preflop continuation estimate</summary>` +
          `<div class="pfl-continuation-body"><dl>${rows.map(([label,value]) =>
            `<dt>${esc(label)}</dt><dd>${Number(value).toFixed(2)} bb</dd>`).join('')}</dl>` +
          `<div><p>Values use the arriving ranges and include modeled future play, before subtracting preflop investment.</p>` +
          `<p>Requested rake: ${Number(estimate.requested_rake_pct).toFixed(1)}% · ${estimate.requested_rake_cap_bb > 0 ? `cap ${Number(estimate.requested_rake_cap_bb).toFixed(2)} bb` : 'uncapped'}.</p>` +
          `<p>${esc(estimateNote)}</p></div></div>`;
        continuation = detail;
      }
    }
    renderExportCard(continuation);
  }

  // ----- 4 · MODEL THE PLAYERS -----

  const PCOLORS = { fold: '#4a78c8', call: '#5ca75f', raise: '#e8484c', jam: '#7d3ca3' };
  const BUCKET_NAMES = ['UNOPENED', 'VS LIMPS', 'VS RAISE', 'SQUEEZE', 'VS 3-BET+'];
  const BUCKET_TIPS = [
    'Nobody has entered yet: open-limp, open-raise, or fold.',
    'Facing limper(s), no raise: limp behind, raise, or fold.',
    'Facing a single raise, no callers. One range covers every open size; solver-played seats stay size-aware.',
    'Facing a raise plus caller(s) \u2014 the squeeze spot.',
    'Facing a re-raise. Cold defense (no voluntary entry yet) and after-entry responses are separate; Situation picks which one you inspect. After-entry frequencies are conditional on reaching the decision, and re-raise depths are pooled.',
  ];

  // Reuse a color for every seat using the same named model. Keep existing
  // assignments when another seat changes, and recycle unused palette entries.
  const modelPalette = ['#7dd3fc', '#fbbf75', '#c4a1ff', '#5ee0bc', '#f59fc4',
    '#e3dc78', '#93b2ff', '#f28f83', '#c1dba0'];
  const modelColors = new Map();
  const modelKey = m => m?.mode === 'ruled' ? (m.label || m.profile?.name || 'Custom') : null;
  function syncModelColors() {
    const keys = new Set((S.model?.seats || []).map(modelKey).filter(Boolean));
    for (const key of modelColors.keys()) if (!keys.has(key)) modelColors.delete(key);
    for (const key of keys) {
      if (!modelColors.has(key)) {
        const used = new Set(modelColors.values());
        modelColors.set(key, modelPalette.find(color => !used.has(color)));
      }
    }
  }
  const seatModelColor = i => modelColors.get(modelKey(S.model?.seats[i])) || '';
  const modelStats = m => m.implied || m.profile?.response?.source_stats || m.stats || null;
  let modelSigRendered = null;
  function renderModel() {
    if (!els.modelBox) return;
    renderApplyState();
    renderModelManager();
    syncModelColors();
    els.ribbon.querySelectorAll('[data-model-seat]').forEach(el => {
      el.style.color = seatModelColor(Number(el.dataset.modelSeat));
    });
    // Rebuilding the <select>s closes any dropdown open under the cursor, so
    // skip whenever nothing rendered here actually changed — poll() calls
    // this every second during a solve.
    const sig = JSON.stringify(!S.model ? null : {
      pos: S.positions,
      seats: S.model.seats.map((m, i) => [m.mode, m.selValue || '', m.label,
        modelStats(m), seatModelColor(i), m.profile?.response?.adaptive_from]),
      gaps: S.lastGaps ? S.lastGaps.map(g => g.toFixed(2)) : null,
      applied: !!S.applied,
      edit: S.editSeat,
      arch: ARCHETYPES.map(a => a.name),
      saved: SAVED_PROFILES,
      deleted: [...deletedModels],
      hero: S.model.hero,
      running: !!S.solveRunning,
    });
    if (sig === modelSigRendered) return;
    modelSigRendered = sig;
    els.modelBox.innerHTML = '';
    if (!S.model) return;
    S.model.seats.forEach((m, i) => {
      const row = document.createElement('div');
      row.className = 'pfl-seatrow';
      const sel = document.createElement('select');
      let html = `<option value="live">Solver</option><option value="frozen">Frozen (as solved)</option>`;
      if (ARCHETYPES.length) {
        const available = ARCHETYPES.map((a, k) => [a, k]).filter(([a]) => !deletedModels.has(`arch:${a.name}`));
        for (const [title, entries] of archetypeGroups(available)) {
          if (!entries.length) continue;
          html += `<optgroup label="${esc(title)}">` +
            entries.map(([a, k]) => `<option value="arch:${k}" title="${esc(a.note || '')}">${esc(modelDisplayName(a.name))}</option>`).join('') + '</optgroup>';
        }
      }
      const availableSaved = SAVED_PROFILES.filter(n => !deletedModels.has(`saved:${n}`));
      if (availableSaved.length) {
        // "saved ·" prefix: a saved profile may share an archetype's name,
        // and the CLOSED select shows only the option label
        html += '<optgroup label="saved profiles">' +
          availableSaved.map(n => `<option value="saved:${esc(n)}">saved · ${esc(n)}</option>`).join('') +
          '</optgroup>';
      }
      sel.innerHTML = html;
      sel.dataset.tip = 'Who sits here. Solver = equilibrium play (adapts on RE-SOLVE) · ' +
        'Frozen = pinned to its current strategy (needs a solve) · a profile bends the solve ' +
        'to its stats · saved players load from disk.';
      const want = m.mode === 'live' ? 'live' : m.mode === 'frozen' ? 'frozen' : (m.selValue || 'live');
      if (!Array.from(sel.options).some(o => o.value === want)) {
        // the seat's profile matches no option (e.g. a loaded game's
        // archetype profile is not a disk file) — show its name, not blank
        const o = document.createElement('option');
        o.value = want;
        o.disabled = true;
        o.textContent = want.startsWith('custom:') ? m.label : `${m.label} (loaded)`;
        sel.appendChild(o);
      }
      sel.value = want;
      sel.title = sel.selectedOptions[0]?.textContent || m.label;
      sel.disabled = !!S.solveRunning; // table changes are refused mid-solve
      sel.addEventListener('change', () => seatSelect(i, sel));
      const info = document.createElement('span');
      info.className = 'pfl-seatinfo';
      // Implied VPIP/PFR here are first-in rates, which do not exist for BB.
      const useImplied = !!m.implied && i !== unraisedWinner(editorContextualConfig(), S.positions);
      const stats = useImplied ? m.implied : m.profile?.response?.source_stats || m.stats || null;
      info.dataset.tip = (m.note ? m.note + ' \u2014 ' : '') +
        (useImplied ? 'Implied' : 'Source') + ' VPIP / PFR / 3-bet percentages.';
      info.textContent = m.mode === 'ruled' && stats &&
        [stats.vpip, stats.pfr, stats.threebet].every(Number.isFinite)
        ? `${stats.vpip.toFixed(0)}/${stats.pfr.toFixed(0)}/${stats.threebet.toFixed(1)}%` : '';
      row.innerHTML = `<b>${esc(S.positions[i])}</b>`;
      row.querySelector('b').style.color = seatModelColor(i);
      row.appendChild(sel);
      row.appendChild(info);
      if (m.mode === 'ruled') {
        const ed = document.createElement('button');
        ed.className = 'btn ghost xs';
        ed.textContent = S.editSeat === i ? 'editing…' : 'edit';
        ed.addEventListener('click', () => openEditor(i));
        row.appendChild(ed);
      }
      els.modelBox.appendChild(row);
    });
    // hero options: staged like every other table edit (the badge carries
    // what is not on the engine yet)
    const hero = els.hero;
    const cur = S.model.hero == null ? '' : String(S.model.hero);
    hero.innerHTML = '<option value="">off</option>' +
      S.positions.map((p, i) => `<option value="${i}">${esc(p)}</option>`).join('');
    hero.value = cur;
    hero.disabled = !!S.solveRunning; // hero changes are refused mid-solve
  }

  async function seatSelect(i, sel) {
    const v = sel.value;
    const m = S.model.seats[i];
    // what the dropdown showed before this pick (renderModel's `want`
    // derivation) — a blocked pick must restore model AND visual state
    const prev = m.mode === 'live' ? 'live'
      : m.mode === 'frozen' ? 'frozen' : (m.selValue || 'live');
    m.selValue = v;
    // staleness guard: rapid re-picks of the same seat race their async
    // fetches — only the response for the NEWEST pick may land on the seat
    const seq = (m.selSeq = (m.selSeq || 0) + 1);
    const fresh = () => S.model && S.model.seats[i] === m && m.selSeq === seq;
    try {
      if (v === 'live') {
        Object.assign(m, { mode: 'live', profile: null, implied: null, label: 'Solver' });
      } else if (v === 'frozen') {
        Object.assign(m, { mode: 'frozen', profile: null, implied: null, label: 'Frozen' });
      } else if (v.startsWith('arch:')) {
        if (lastIter < 1) {
          toast('solve the unlocked game first — profiles distort that equilibrium', true);
          // revert to what the seat actually still is: m.mode/profile were
          // never touched, so showing 'live' here would claim Solver while
          // APPLY/SOLVE still send the previous (e.g. ruled) model
          m.selValue = prev;
          sel.value = prev;
          return;
        }
        const a = ARCHETYPES[+v.slice(5)];
        const out = await api.pfGenerate(i, a.stats, a.name);
        if (!fresh()) return;
        Object.assign(m, { mode: 'ruled', profile: out.profile, implied: out.implied, label: a.name, stats: { ...a.stats },
          postflop: a.postflop ? JSON.parse(JSON.stringify(a.postflop)) : null, painted: false, note: a.note || '' });
      } else if (v.startsWith('saved:')) {
        const prof = await api.pfProfileGet(v.slice(6));
        if (!fresh()) return;
        // painted: any paint in a saved profile happened in an earlier
        // session — protect it from silent auto-GENERATE on stat edits
        Object.assign(m, { mode: 'ruled', profile: prof, implied: null, label: prof.name,
          stats: prof.response?.source_stats || (prof.stats ? { ...prof.stats } : null),
          postflop: prof.postflop || null, painted: true });
      }
      // A pick replaces the seat's profile: its paint history belongs to the
      // old one, and restorePaint would write those bands into the new model.
      resetPaint(m);
    } catch (e) {
      if (!fresh()) return;
      toast(errText(e), true);
    }
    if (S.editSeat === i && m.mode !== 'ruled') closeEditor();
    S.lastApplyWasSolve = false;
    renderModel();
    if (S.editSeat === i) openEditor(i);
  }

  // The engine's copy of a seat: mode + profile. Postflop tendencies are a
  // separate dirty flag (they need a push but never reset learning).
  const seatSigOf = m => JSON.stringify({
    mode: m.mode,
    profile: m.mode === 'ruled' ? m.profile : null,
  });
  const pendingSeats = () => !S.model ? [] : S.model.seats.map((_, i) => i)
    .filter(i => seatSigOf(S.model.seats[i]) !== S.appliedSeatSigs[i]);
  // Staged table edits: a seat whose model differs from the engine's copy,
  // plus the hero choice. The postflop-only push rides along, uncounted.
  const pendingChanges = () => {
    const out = pendingSeats();
    if (S.model && (S.model.hero ?? null) !== (S.appliedHero ?? null)) out.push('hero');
    return out;
  };
  function renderApplyState() {
    const n = S.model ? pendingChanges().length : 0;
    els.applyBtn.disabled = !S.model || S.solveRunning || n === 0;
    els.applyBtn.textContent = !S.model ? 'APPLY'
      : n ? `${n} unapplied change${n === 1 ? '' : 's'} · APPLY`
      : S.lastApplyWasSolve ? 'applied with this solve' : 'applied';
  }

  async function applyModel({ fromSolve = false, quiet = false } = {}) {
    if (!S.model) { toast('build a game first', true); return false; }
    const changedSeats = pendingSeats().length > 0;
    const heroTarget = S.model.hero ?? null;
    const heroBefore = S.appliedHero ?? null;
    // pfTable can mutate hero: a CHANGED table leaves hero mode server-side
    // (an unchanged one keeps it), so the hero call below runs whenever the
    // engine's hero is not the staged one. Hold the hero epoch/busy guard
    // across the WHOLE transaction so poll() can't adopt a /status response
    // fetched mid-apply.
    heroBusy++; heroEpoch++;
    let heroOn = false;
    try {
      if (changedSeats || S.postflopDirty) {
        try {
          // postflop tendencies ride along on the profile, so SAVE GAME and
          // exports keep the villain's whole player model, not just preflop
          await api.pfTable(S.model.seats.map(m => ({
            frozen: m.mode === 'frozen',
            profile: m.mode === 'ruled' && m.profile
              ? { ...m.profile, postflop: m.postflop || m.profile.postflop || null }
              : null,
          })));
        } catch (e) { toast(errText(e), true); return false; }
        S.applied = S.model.seats.map(m => m.mode);
        S.appliedSeatSigs = S.model.seats.map(seatSigOf);
        S.postflopDirty = false; // the push above carried the current tendencies
        // A changed preflop table clears hero server-side, but a postflop-only
        // push (same table under the engine's comparison) keeps it. Adopt the
        // engine's truth instead of assuming either; if that read fails, mark
        // it unknown so the staged hero below is pushed regardless.
        try {
          const st = await api.pfStatus();
          S.appliedHero = st?.hero ?? null;
        } catch { S.appliedHero = undefined; }
      }
      if (heroTarget !== S.appliedHero) {
        try {
          await heroCall(heroTarget);
          heroOn = heroTarget != null;
          S.heroPending = false;
          S.appliedHero = heroTarget;
        } catch (e) {
          // The engine requires a solved table before hero can freeze the
          // other seats. Stay staged; the next solve runs the table first and
          // the run-end hook applies it.
          S.heroPending = heroTarget != null;
          if (heroTarget != null) S.appliedHero = null;
          if (!fromSolve) toast(heroTarget == null
            ? `hero off failed — ${errText(e)}`
            : `hero ${S.positions[heroTarget]} applies with the next SOLVE — ${errText(e)}`, true);
        }
      } else {
        S.heroPending = false;
      }
    } finally {
      heroBusy--; heroEpoch++;
    }
    if (changedSeats || heroOn) {
      S.gameSaved = false; // the engine no longer holds the on-disk strategies
      renderSaveState();
    }
    S.lastApplyWasSolve = fromSolve && !pendingChanges().length;
    if (!quiet && !S.heroPending) {
      toast(changedSeats
        ? 'table applied — the next solve converges fresh'
        : heroOn ? `hero ${S.positions[heroTarget]} — others frozen`
        : heroBefore != null && heroTarget == null ? 'hero off — the table plays as solved'
        : 'table applied');
    }
    renderModel();
    refresh(); // ribbon gets its lock badges
    // the engine's iteration, frozen mask and trust readout all moved: one
    // status poll (it stops itself again when the run is not running)
    startPolling();
    return true;
  }
  els.applyBtn.addEventListener('click', applyModel);

  /** Deferred-hero recovery: called when a run ends with hero still staged
   *  (the engine refused it pre-solve because the table had no strategies to
   *  freeze — now it does). */
  async function reapplyHero() {
    const h = S.model.hero;
    try {
      await heroCall(h);
      S.heroPending = false;
      S.appliedHero = h;
      S.gameSaved = false; // the hero's block was just reset: not what's on disk
      S.lastApplyWasSolve = true;
      toast(`hero ${S.positions[h]} — others frozen as solved`);
      renderSaveState();
      startPolling(); // adopt the engine's reset iteration and repaint the grid
    } catch (e) { toast(errText(e), true); }
    renderModel();
  }

  // Staging: the hero choice is part of the one unapplied-changes badge.
  els.hero.addEventListener('change', () => {
    if (!S.model) return;
    S.model.hero = els.hero.value === '' ? null : +els.hero.value;
    S.lastApplyWasSolve = false;
    renderModel();
  });

  // ----- profile editor (stats → generate → paint) -----

  let editDraft = null;
  let editorEpoch = 0;
  let contextualPreview = null;
  let contextualPreviewKey = '';
  let contextualPreviewRequest = 0;
  let evidencePreviewKey = '';
  let evidencePreview = null;
  let evidencePreviewRequest = 0;
  let editorCleanup = () => {};
  const editingModel = () => editDraft || S.model?.seats[S.editSeat];
  // Per-bucket paint bookkeeping: `paintedBuckets` drives the badge,
  // `paintBase`/`paintHistory` are the session's undo snapshots.
  const resetPaint = m => { m.paintedBuckets = new Set(); m.paintBase = {}; m.paintHistory = {}; };
  const defaultModelStats = () => ({ vpip: 25, pfr: 18, threebet: 6, fold_to_3bet: 50, squeeze: 5, fourbet: null, flatten: 0.2, raise_size: 'min' });
  async function openLibraryEditor(key) {
    const request = ++editorEpoch;
    manager.querySelector('[role="status"]').textContent = 'Opening model…';
    try {
      let draft;
      if (key?.startsWith('saved:')) {
        const profile = await api.pfProfileGet(key.slice(6));
        draft = { mode:'ruled', profile, label:profile.name, stats:profile.response?.source_stats || profile.stats || null, postflop:profile.postflop || null, painted:true };
      } else {
        const arch = key ? ARCHETYPES.find(a => `arch:${a.name}` === key) : null;
        const stats = arch ? structuredClone(arch.stats) : defaultModelStats();
        const label = arch ? `${arch.name} copy` : 'New player';
        draft = { mode:'ruled', label, stats, postflop:arch?.postflop ? structuredClone(arch.postflop) : null, note:arch?.note || '', painted:false, needsGeneration:true,
          profile:{ name:label, buckets:[], response:{adaptive_from:.25}, stats } };
      }
      if (request !== editorEpoch) return;
      openEditor(0, draft);
    } catch (e) { manager.querySelector('[role="status"]').textContent = e.message; }
  }
  function closeEditor() {
    ++editorEpoch;
    ++contextualPreviewRequest;
    editorCleanup();
    S.editSeat = null;
    editDraft = null;
    els.editor.classList.add('hidden');
    els.editor.innerHTML = '';
    manager.classList.remove('editing');
    libraryPane.classList.remove('hidden');
    manager.querySelector('[role="status"]').textContent = '';
    renderModel();
    if (manager.open) manager.querySelector('.pfl-model-search').focus();
  }

  function openEditor(i, draft = null) {
    editorCleanup();
    const epoch = ++editorEpoch;
    editDraft = draft;
    const m = draft || S.model?.seats[i];
    if (!m) return;
    if (m.mode !== 'ruled' || !m.profile) return;
    const editorMessage = message => { manager.querySelector('[role="status"]').textContent = message; };
    S.editSeat = draft ? null : i;
    S.editBucket = 0;
    S.editLimpContext = 0;
    S.editReraiseContext = 'cold';
    contextualPreview = null;
    contextualPreviewKey = '';
    evidencePreview = null;
    evidencePreviewKey = '';
    ++evidencePreviewRequest;
    ++contextualPreviewRequest;
    manager.classList.add('editing');
    libraryPane.classList.add('hidden');
    if (!manager.open) manager.showModal();
    manager.querySelector('[role="status"]').textContent = draft ? 'Library draft — Save player makes it available in the seat menus.' : 'Editing this seat. Apply model or Re-solve to use the changes in the game.';
    const st0 = m.stats || m.profile.response?.source_stats || { vpip: 25, pfr: 18, threebet: 6, fold_to_3bet: 50, squeeze: 5, fourbet: null, flatten: 0.2, raise_size: 'min' };
    const originalStats = structuredClone(st0);
    const measuredBands = st0.cont_vs_raise_bands?.length > 2 ? structuredClone(st0.cont_vs_raise_bands) : null;
    // measured archetypes carry f32 noise (57.299999...) — show one decimal
    const st = Object.fromEntries(Object.entries(st0).map(([k, v]) => [k, typeof v === 'number' && k !== 'flatten' ? Math.round(v * 10) / 10 : v]));
    els.editor.classList.remove('hidden');
    els.editor.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:baseline">
        <b style="font-size:12px">${draft ? 'Library model' : esc(S.positions[i])} — ${esc(m.label)}</b>
        <button class="btn ghost xs" id="pfe-close">Back to models</button>
      </div>
      ${draft ? `<label class="pfe-preview-seat">Generate ranges for <select id="pfe-preview-seat">${S.positions.length ? S.positions.map((pos,k) => `<option value="${k}">${esc(pos)}</option>`).join('') : '<option value="0">Build a Preflop game first</option>'}</select></label>` : ''}
      <div class="pfe-layout"><div class="pfe-settings">
      ${!m.stats && !m.profile.response?.source_stats ? '<div class="dim" style="font-size:10px">This older profile has no saved generation stats. The fields below are defaults; generating will replace its ranges.</div>' : ''}
      ${m.note ? `<div class="dim" style="font-size:10px;line-height:1.4;margin:2px 0 4px">${esc(m.note)}</div>` : ''}
      ${st0.dataset ? `<label style="display:block;margin:8px 0"><input type="checkbox" id="pfe-dataset" checked> Use ${esc(st0.dataset.site)} ${st0.dataset.response_policies?.length ? 'measured preflop ranges' : st0.dataset.empirical_opening ? 'measured opening ranges' : 'measured entry contexts'}</label><div class="dim" style="font-size:10px">Disabled fields show pooled source rates; the dataset supplies the matching hand policies. Uncheck to edit those rates and generate reference-ordered ranges.</div>` : ''}
      <div class="pfl-step" style="margin-top:6px" data-tip="How this player enters and defends pots before the flop. Each number is a frequency over the hands dealt in that situation; ranges are cut from a GTO reference ordering, re-ordered toward card appeal by naiveté.">PREFLOP TENDENCIES</div>
      <div class="field-grid" id="pfe-stats" style="margin:6px 0">
        <label data-tip="VPIP: of all hands dealt, how often he voluntarily puts chips in preflop — by limping, calling or raising (blind posts don't count). When open-raise / open-limp are blank it sets his first-in width; it always scales the defend targets below.">VPIP % <input id="pfe-vpip" type="number" value="${st.vpip}" min="1" max="100"></label>
        <label data-tip="PFR: of all hands dealt, how often he raises at least once preflop (opening, isolating, or re-raising). It is the raising slice of the VPIP; VPIP − PFR is his limping/calling share. When open-raise is blank it sets his first-in raise width.">PFR % <input id="pfe-pfr" type="number" value="${st.pfr}" min="0" max="100"></label>
        <label data-tip="Open-raise (first in): how often he raises when it is folded to him. Measured online: nit 9%, TAG 17%, loose-passive fish 12%, whale 14% (they limp instead).">open-raise % <input id="pfe-or" type="number" value="${st.open_raise != null ? st.open_raise : ''}" min="0" max="100" step="0.5"><span class="pfe-derived dim" style="font-size:9px;margin-left:3px" hidden>derived</span></label>
        <label data-tip="Open-limp (first in): how often he limps when it is folded to him. The derived number over-limps regs (a 17/12 TAG open-limps ~2%) and under-limps whales. Measured online: TAG 2%, tight-passive 11%, loose-passive fish 30%, whale 50%.">open-limp % <input id="pfe-ol" type="number" value="${st.open_limp != null ? st.open_limp : ''}" min="0" max="100" step="0.5"><span class="pfe-derived dim" style="font-size:9px;margin-left:3px" hidden>derived</span></label>
        <label data-tip="3-bet: when he faces a single raise with no callers yet, how often he re-raises (always strength-ranked — a 1% 3-bettor 3-bets AA/KK only). The rest of his continuing hands call; the calling width comes from VPIP.">3-bet % <input id="pfe-3b" type="number" value="${st.threebet}" min="0" max="100" step="0.5"></label>
        <label data-tip="Fold to 3-bet+: conditional on having already entered and facing a re-raise. Measured ranges supply the hand policies instead of one rate; cold defense is a separate policy.">fold to 3-bet+ % <input id="pfe-f3b" type="number" value="${st.fold_to_3bet}" min="0" max="100"></label>
        <label data-tip="Squeeze: when he faces a raise that has ALREADY been called by someone, how often he re-raises. Its own situation, because even aggressive players squeeze tighter than they 3-bet.">squeeze % <input id="pfe-sq" type="number" value="${st.squeeze}" min="0" max="100" step="0.5"></label>
        <label data-tip="Fold vs raise (COLD): nothing invested yet, facing a single raise. Online pools fold 80–90% here: mostly fold, 3-bet the top, flat a little.">fold vs raise % <input id="pfe-fvr" type="number" value="${st.cont_vs_raise != null ? (100 - st.cont_vs_raise).toFixed(0) : ''}" min="0" max="100"><span class="pfe-derived dim" style="font-size:9px;margin-left:3px" hidden>derived</span></label>
        <label data-tip="Fold vs raise AFTER LIMPING: he limped and a raise comes. Measured limpers fold only 30–55% (they limped to see a flop) vs 80–90% cold, and this drives the whole exploit in a limpy game.">fold vs raise after limping % <input id="pfe-fvrl" type="number" value="${st.cont_vs_raise_limped != null ? (100 - st.cont_vs_raise_limped).toFixed(0) : ''}" min="0" max="100"><span class="pfe-derived dim" style="font-size:9px;margin-left:3px" hidden>derived</span></label>
        <label data-tip="Iso-raise: facing one or more limpers with nothing invested yet, how often he raises.">iso-raise vs limpers % <input id="pfe-ir" type="number" value="${st.iso_raise != null ? st.iso_raise : ''}" min="0" max="100" step="0.5"><span class="pfe-derived dim" style="font-size:9px;margin-left:3px" hidden>derived</span></label>
        <label data-tip="Limp behind: facing limpers with nothing invested yet, how often he limps along. Limpy live games hinge on this number: it is what builds the multiway pots.">limp behind % <input id="pfe-lb" type="number" value="${st.limp_behind != null ? st.limp_behind : ''}" min="0" max="100" step="0.5"><span class="pfe-derived dim" style="font-size:9px;margin-left:3px" hidden>derived</span></label>
        <label data-tip="Fold vs a raise TO at least the bb amount beside it. Real players fold more to big raises; without a size band every size gets the same fold rate and the exploit picks the cheapest raise.">fold vs big raise % <span style="display:inline-flex;align-items:center;gap:3px"><input id="pfe-fvrb" type="number" value="${(st.cont_vs_raise_bands && st.cont_vs_raise_bands.length > 1) ? (100 - st.cont_vs_raise_bands[st.cont_vs_raise_bands.length - 1][1]).toFixed(0) : ''}" min="0" max="100"><span class="dim">\u2265</span><input id="pfe-fvrthr" type="number" value="${(st.cont_vs_raise_bands && st.cont_vs_raise_bands.length > 1) ? st.cont_vs_raise_bands[0][0] : ''}" min="1" step="0.5" placeholder="bb" style="width:56px"><span class="dim">bb</span></span><span class="pfe-derived dim" style="font-size:9px;margin-left:3px" hidden>derived</span></label>
        <label data-tip="Fold vs squeeze spot: facing a raise and one or more callers with nothing voluntarily invested.">fold vs squeeze % <input id="pfe-fsq" type="number" value="${st.cont_squeeze != null ? (100 - st.cont_squeeze).toFixed(0) : ''}" min="0" max="100"><span class="pfe-derived dim" style="font-size:9px;margin-left:3px" hidden>derived</span></label>
        <label data-tip="Naiveté, 0–1: how the ranges are ORDERED, not how wide they are. 0 = solver-shaped: positional, and ranked by playability (the equilibrium folds dominated hands like Q9o to a raise but defends 53s). 1 = plays his cards: the same ranges from every seat, ranked by raw card appeal — high cards and any suited hand in, low suited junk out. A whale is ~0.7+, a reg ~0.2.">naiveté <input id="pfe-flat" type="number" value="${st.flatten}" min="0" max="1" step="0.05"></label>
        <label data-tip="Fallback sizing for raises with no measured size mix: min, max, or jam (all-in).">fallback raise size <select id="pfe-size"><option value="min">min</option><option value="max">max</option><option value="jam">jam</option></select></label>
        ${measuredBands ? `<details style="grid-column:1/-1"><summary>Measured raise-size responses · ${measuredBands.length} bands</summary><div class="field-grid" style="margin-top:6px">${measuredBands.map(([bound,continuing],b) => `<label>Fold vs raise ${b===measuredBands.length-1 ? `above ${measuredBands[b-1][0]}` : b===0 ? `up to ${bound}` : `over ${measuredBands[b-1][0]}, up to ${bound}`} bb %<input id="pfe-band-${b}" type="number" min="0" max="100" step="0.1" value="${Math.round((100-continuing)*100)/100}"></label>`).join('')}</div></details>` : ''}
      </div>
      <label class="dim" style="display:block;margin:8px 0">Adaptive responses from % of stack
        <input id="pfe-adaptive" type="number" min="1" max="100" step="1" placeholder="blank = fixed" value="${m.profile.response?.adaptive_from != null ? m.profile.response.adaptive_from * 100 : ''}">
      </label>
      <div class="dim" style="font-size:10px;line-height:1.4">At or above this raise-to amount, opponents learn their responses \u2014 a modeling assumption for large bets, not measured behavior. Blank keeps fixed responses.</div>
      <div class="pfl-step" style="margin-top:10px" data-tip="The same player after the flop. Only used when a spot is sent to postflop SETUP, where the numbers become node locks on his postflop tree. 'Initiative' means he was the last to bet or raise so far in the hand.">POSTFLOP TENDENCIES</div>
      <div class="field-grid" id="pfe-pf" style="margin:6px 0">
        <label data-tip="C-bet: on the flop, when he has the initiative (he was the preflop raiser), how often he bets when it is his turn to act and nobody has bet yet.">c-bet flop % <input id="pfe-cb0" type="number" min="0" max="100"></label>
        <label data-tip="Turn barrel: on the turn, when he STILL has the initiative, how often he bets into an unbet pot. That means: he bet the flop and got called (the classic double barrel) — or he was the preflop raiser and the flop checked through, since a check doesn't hand the initiative over (a delayed c-bet). It is NOT independent of the flop: if the opponent bet or raised the flop, the initiative is theirs and this number no longer applies to him.">turn barrel % <input id="pfe-cb1" type="number" min="0" max="100"></label>
        <label data-tip="River barrel: on the river, when he still has the initiative (he made the last bet or raise in the hand so far), how often he bets into an unbet pot — the triple barrel, or a delayed barrel after streets that checked through.">river barrel % <input id="pfe-cb2" type="number" min="0" max="100"></label>
        <label data-tip="Fold vs bet, flop: when he faces a bet or raise on the flop, how often he folds — at every raise depth and regardless of the size faced. The rest of his hands continue (call, or raise per 'raise vs bet').">fold vs bet flop % <input id="pfe-fb0" type="number" min="0" max="100"></label>
        <label data-tip="Fold vs bet, turn: when he faces a bet or raise on the turn, how often he folds — any depth, any size.">fold vs bet turn % <input id="pfe-fb1" type="number" min="0" max="100"></label>
        <label data-tip="Fold vs bet, river: when he faces a bet or raise on the river, how often he folds — any depth, any size.">fold vs bet river % <input id="pfe-fb2" type="number" min="0" max="100"></label>
        <label data-tip="Raise vs bet: when he faces a bet or raise (any street, any depth), how often he raises — a share of ALL the hands facing it, alongside the fold number (fold + raise + call = 100). His strongest continuing hands raise first.">raise vs bet % <input id="pfe-rvb" type="number" min="0" max="100" step="0.5"></label>
        <label data-tip="Donk / stab: how often he bets into an unbet pot when he does NOT have the initiative — leading into the aggressor (a donk bet), or stabbing after the aggressor checked. One number for all streets.">donk / stab % <input id="pfe-donk" type="number" min="0" max="100"></label>
        <label data-tip="Which size his postflop bets and raises use: the smallest or the largest of whatever the postflop tree offers at each node.">bet size <select id="pfe-bsz"><option value="min">min</option><option value="max">max</option></select></label>
      </div>
      <div class="btn-row" style="margin-top:8px">
        <button class="btn" id="pfe-gen" data-tip="Rebuild this seat's ranges from the tendencies above. Numbers rebuild automatically; after hand-painting, this replaces the painted edits. It lights up when the stats and paint disagree.">GENERATE FROM STATS</button>
        <button class="btn ghost" id="pfe-copyall" data-tip="Copies the preflop and postflop tendencies above to every other seat and generates each seat's own positional ranges (a 30/20 player opens tighter from UTG than from the BTN). Hand-painted edits are not copied.">COPY TO ALL SEATS</button>
      </div>
      <div id="pfe-implied" class="mono dim" style="font-size:10px;margin:4px 0 6px" data-tip="Frequencies measured from the generated ranges — compare with the stats above."></div>
      </div><div class="pfe-ranges"><div class="pfl-step" style="margin-top:6px" data-tip="What this seat does with every hand in each preflop situation. Built from the tendencies above; pick a brush and click hands to overrule any cell. Painted edits stay until GENERATE FROM STATS runs again.">THE RANGES THIS PLAYER PLAYS</div>
      <div id="pfe-rangenote"></div>
      <div class="seg" id="pfe-buckets" style="margin-top:8px">${
        BUCKET_NAMES.map((n, k) => `<button data-b="${k}" class="${k === 0 ? 'active' : ''}" data-tip="${BUCKET_TIPS[k]}">${n}</button>`).join('')
      }</div>
      <label id="pfe-limp-context-row" class="dim hidden" style="font-size:11px;margin-top:6px">Facing <select id="pfe-limp-context"></select></label>
      <div id="pfe-reraise-context-row" class="pfe-response-context hidden">
        <label>Situation <select id="pfe-reraise-context">
          <option value="cold">Facing a re-raise cold</option>
          <option value="entered">After already entering</option>
        </select></label>
        <p id="pfe-reraise-explanation"></p>
        <div id="pfe-contextual-fields" class="hidden">
          <div class="pfe-contextual-inputs">
            <label>Facing <select id="pfe-context-depth"><option value="2">3-bet</option><option value="3">4-bet+</option></select></label>
            <label>Already in (bb) <input id="pfe-context-invested" type="number" min="0" step="0.5"></label>
            <label>Facing total (bb) <input id="pfe-context-to" type="number" min="0" step="0.5"></label>
            <label>Pot before call (bb) <input id="pfe-context-pot" type="number" min="0" step="0.5"></label>
          </div>
          <p id="pfe-contextual-status" role="status" aria-live="polite"></p>
        </div>
      </div>
      <div id="pfe-paint-state" class="dim" style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;font-size:10px;margin-top:6px">
        <span id="pfe-paint-caption"></span>
        <span id="pfe-paint-badge" class="hidden" style="background:#4b3a1a;color:#f3dfb2;padding:1px 6px;border-radius:8px;font-size:9px;letter-spacing:.08em">painted</span>
        <button type="button" class="btn ghost xs hidden" id="pfe-paint-undo" data-tip="Undo the last stroke in this bucket.">undo</button>
        <button type="button" class="btn ghost xs hidden" id="pfe-paint-clear" data-tip="Discard every stroke in this bucket from this session.">clear</button>
      </div>
      <div id="pfe-paint-controls" class="pfl-gridbar" style="margin-top:6px">
        <div class="seg pfl-palette" id="pfe-palette">
          <button data-a="fold" data-tip="Paint hands out of the range (fold / check back).">FOLD</button><button data-a="call" data-tip="Paint calls (or limps, in unopened spots).">CALL</button><button data-a="raise" data-tip="Paint raises \u2014 they use this profile\u2019s raise size.">RAISE</button><button data-a="jam" data-tip="Paint all-in jams.">JAM</button>
        </div>
        <label class="dim" style="font-size:10px">weight <input id="pfe-w" type="range" min="5" max="100" value="100" style="width:70px;vertical-align:middle"> <span id="pfe-wv">100%</span></label>
      </div>
      <div id="pfe-not-applicable" class="pfe-not-applicable hidden" role="status">
        <strong>Not applicable — everyone folded; the last live blind wins</strong>
        <p>There is no opening or calling range here.</p>
        <p>Choose <b>Vs Limps</b> for checks and raises, or a defensive tab for responses to bets.</p>
      </div>
      <div id="pfl-paint" class="matrix browse"></div>
      </div></div><div class="btn-row pfe-save-row" style="margin-top:6px">
        <input type="text" id="pfe-name" placeholder="save as…" value="${esc(m.label)}" data-tip="Name for the saved player (saving under an existing name replaces it).">
        <button class="btn" id="pfe-save" data-tip="Stores the stats, postflop tendencies and generated or painted ranges in saves/profiles/. It then appears under 'saved profiles' in every seat dropdown, on any game.">SAVE PLAYER</button>
      </div>`;
    document.getElementById('pfe-size').value = st.raise_size || 'min';
    // Derived values live in the field that uses them: a blank first-in or
    // fold field shows the number the engine would use, marked derived.
    const numOf = id => { const v = document.getElementById(id)?.value; return v === '' || v == null ? null : +v; };
    const derivedPlaceholders = {
      'pfe-or': () => [numOf('pfe-pfr'), false],
      'pfe-ol': () => [Math.max(0, (numOf('pfe-vpip') ?? 0) - (numOf('pfe-pfr') ?? 0)), false],
      'pfe-ir': () => [numOf('pfe-pfr'), false],
      'pfe-lb': () => [Math.max(0, (numOf('pfe-vpip') ?? 0) - (numOf('pfe-pfr') ?? 0)), false],
      // the engine blends toward 65% of VPIP continuing vs a raise and 50%
      // in the squeeze spot; shown as approximations
      'pfe-fvr': () => [100 - 0.65 * (numOf('pfe-vpip') ?? 0), true],
      'pfe-fsq': () => [100 - 0.5 * (numOf('pfe-vpip') ?? 0), true],
      // blank = the cold number, after limping and for big raises
      'pfe-fvrl': () => [numOf('pfe-fvr') ?? (100 - 0.65 * (numOf('pfe-vpip') ?? 0)), true],
      'pfe-fvrb': () => [numOf('pfe-fvr') ?? (100 - 0.65 * (numOf('pfe-vpip') ?? 0)), true],
    };
    function syncDerived() {
      for (const [id, value] of Object.entries(derivedPlaceholders)) {
        const input = document.getElementById(id);
        if (!input) continue;
        const [v, approx] = value();
        const usable = input.value.trim() === '' && !input.disabled && Number.isFinite(v);
        input.placeholder = usable ? `${approx ? '\u2248' : ''}${Math.max(0, Math.min(100, v)).toFixed(1)}` : '';
        const tag = input.closest('label')?.querySelector('.pfe-derived');
        if (tag) tag.hidden = !usable;
      }
    }
    for (const id of ['pfe-vpip', 'pfe-pfr', 'pfe-fvr', 'pfe-or', 'pfe-ol']) {
      document.getElementById(id)?.addEventListener('input', syncDerived);
    }
    syncDerived();
    for (const id of ['pfe-context-invested','pfe-context-to','pfe-context-pot']) {
      document.getElementById(id).addEventListener('input', () => {
        refreshContextualPreview();
      });
    }
    document.getElementById('pfe-context-depth').addEventListener('change', () => {
      resetContextualAmounts();
      refreshContextualPreview();
    });
    if (measuredBands) {
      document.getElementById('pfe-fvrb').closest('label').classList.add('hidden');
      document.getElementById('pfe-fvrthr').closest('label').classList.add('hidden');
    }
    const originalInputs = new Map([...document.querySelectorAll('#pfe-stats input, #pfe-stats select')].map(e => [e.id,e.value]));
    const inputUnchanged = id => document.getElementById(id).value === originalInputs.get(id);
    const pfDef = { cbet: [65, 55, 45], fold_to_bet: [45, 48, 52], raise_bet: 9, donk: 8, bet_size: 'min' };
    const pf = m.postflop || pfDef;
    if (hasContextualBetting(pf)) {
      const legacy = document.getElementById('pfe-donk');
      legacy.disabled = true;
      legacy.closest('label').firstChild.textContent = 'legacy donk / stab % ';
      legacy.closest('label').dataset.tip = 'Reference only: contextual profiles estimate betting by street and pot type, so this pooled number sets no targets.';
      document.getElementById('pfe-bsz').closest('label').dataset.tip = 'Preferred size for other bets and raises. Betting without initiative keeps the solved bet-size mix.';
      const note = document.createElement('div');
      note.className = 'dim';
      note.style.cssText = 'font-size:10px;line-height:1.4;margin:4px 0';
      note.textContent = 'Betting without initiative (donks, bets after checks, later-street leads and probes) is estimated by street and pot type. Sparse evidence stays closer to the solved strategy; hand selection and size mix come from the solve. These safeguards are modeling assumptions.';
      note.dataset.tip = pf.contextual_betting.source || '';
      document.getElementById('pfe-pf').before(note);
    }
    [['pfe-cb0', pf.cbet[0]], ['pfe-cb1', pf.cbet[1]], ['pfe-cb2', pf.cbet[2]],
     ['pfe-fb0', pf.fold_to_bet[0]], ['pfe-fb1', pf.fold_to_bet[1]], ['pfe-fb2', pf.fold_to_bet[2]],
     ['pfe-rvb', pf.raise_bet], ['pfe-donk', pf.donk], ['pfe-bsz', pf.bet_size || 'min']]
      .forEach(([id, v]) => { document.getElementById(id).value = typeof v === 'number' ? Math.round(v * 10) / 10 : v; });
    const originalPfInputs = new Map([...document.querySelectorAll('#pfe-pf input')].map(e => [e.id,e.value]));
    const pfValue = (id, original) => document.getElementById(id).value === originalPfInputs.get(id) ? original : +document.getElementById(id).value;
    const collectPf = () => editPostflopStats(pf, {
      cbet: pf.cbet.map((v,j) => pfValue(`pfe-cb${j}`,v)),
      fold_to_bet: pf.fold_to_bet.map((v,j) => pfValue(`pfe-fb${j}`,v)),
      raise_bet: pfValue('pfe-rvb',pf.raise_bet),
      donk: pfValue('pfe-donk',pf.donk),
      bet_size: document.getElementById('pfe-bsz').value,
    });
    document.getElementById('pfe-pf').addEventListener('input', () => {
      m.postflop = collectPf();
      // tendencies are outside the seat signature (deliberately: no learning-reset
      // messaging) — flag them so SOLVE/SAVE re-send the table anyway
      if (!draft) S.postflopDirty = true;
    });
    document.getElementById('pfe-close').addEventListener('click', closeEditor);
    // Every HUD number the editor holds, on top of the seat's current stats
    // (measured overrides the editor has no field for survive a nudge).
    // Fold-vs-raise / big-raise / squeeze are entered as FOLD %, stored as
    // the engine's continue % (blank = leave to the VPIP blend).
    const collectStats = () => {
      const prev = m.stats || {};
      const num = id => { const v = document.getElementById(id).value; return v === '' ? null : +v; };
      const threebet = +document.getElementById('pfe-3b').value;
      const fvr = num('pfe-fvr');
      const fvrb = num('pfe-fvrb');
      const thr = num('pfe-fvrthr');
      const fsq = num('pfe-fsq');
      const fvrl = num('pfe-fvrl');
      const firstIn = { open_raise: num('pfe-or'), open_limp: num('pfe-ol'), iso_raise: num('pfe-ir'), limp_behind: num('pfe-lb') };
      const cont = f => Math.max(threebet, Math.min(100, 100 - f)); // engine requires continue >= 3-bet
      const stats = {
        ...prev,
        vpip: +document.getElementById('pfe-vpip').value,
        pfr: +document.getElementById('pfe-pfr').value,
        threebet,
        fold_to_3bet: +document.getElementById('pfe-f3b').value,
        squeeze: +document.getElementById('pfe-sq').value,
        fourbet: prev.fourbet != null ? prev.fourbet : null,
        flatten: +document.getElementById('pfe-flat').value,
        raise_size: document.getElementById('pfe-size').value,
        cont_vs_raise: fvr != null ? cont(fvr) : null,
        cont_vs_raise_bands: (fvr != null && fvrb != null && thr != null && thr > 0)
          ? [[thr - 0.01, cont(fvr)], [999, cont(fvrb)]] : null,
        cont_squeeze: fsq != null ? Math.max(+document.getElementById('pfe-sq').value, Math.min(100, 100 - fsq)) : null,
        cont_vs_raise_limped: fvrl != null ? Math.max(0, Math.min(100, 100 - fvrl)) : null,
        ...firstIn,
      };
      // Display rounding must not rewrite measured percentages just because a
      // user previews or saves the model, or edits an unrelated field.
      const fields = {vpip:'pfe-vpip',pfr:'pfe-pfr',threebet:'pfe-3b',fold_to_3bet:'pfe-f3b',squeeze:'pfe-sq',
        flatten:'pfe-flat',raise_size:'pfe-size',cont_vs_raise:'pfe-fvr',cont_squeeze:'pfe-fsq',
        cont_vs_raise_limped:'pfe-fvrl',open_raise:'pfe-or',open_limp:'pfe-ol',iso_raise:'pfe-ir',limp_behind:'pfe-lb'};
      for (const [key,id] of Object.entries(fields)) {
        if (inputUnchanged(id) && Object.hasOwn(originalStats,key)) stats[key] = originalStats[key];
      }
      if (measuredBands) {
        stats.cont_vs_raise_bands = measuredBands.map(([bound,value],b) => [bound,
          Math.max(stats.threebet, inputUnchanged(`pfe-band-${b}`) ? value : 100-num(`pfe-band-${b}`))]);
      } else if (['pfe-fvr','pfe-fvrb','pfe-fvrthr'].every(inputUnchanged)) {
        stats.cont_vs_raise_bands = originalStats.cont_vs_raise_bands?.map(([bound,value]) => [bound,Math.max(stats.threebet,value)]) ?? null;
      }
      if (stats.cont_vs_raise != null) stats.cont_vs_raise = Math.max(stats.threebet,stats.cont_vs_raise);
      if (stats.cont_squeeze != null) stats.cont_squeeze = Math.max(stats.squeeze,stats.cont_squeeze);
      stats.dataset = document.getElementById('pfe-dataset')?.checked ? originalStats.dataset : null;
      return stats;
    };
    async function doGenerate(auto) {
      if (epoch !== editorEpoch) return false;
      if (!S.model || lastIter < 1) {
        manager.querySelector('[role="status"]').textContent = 'Build and solve a Preflop game first to generate this model’s positional ranges.';
        return false;
      }
      // Start from the seat's current stats so the measured overrides the
      // editor has no fields for (cont_vs_raise, cont_squeeze,
      // cont_vs_raise_bands, fourbet — the CoinPoker archetypes carry them)
      // survive a stat nudge instead of silently reverting to the VPIP blend.
      const stats = collectStats();
      // staleness guard: a slow generate must not overwrite a newer one for
      // THIS seat (or a seat that was reassigned while it was in flight).
      // Per-seat (like m.selSeq): seat B generating in its own editor must
      // NOT cancel seat A's in-flight generate — a global counter silently
      // dropped A's stat edit.
      const seq = (m.genSeq = (m.genSeq || 0) + 1);
      try {
        const adaptive = document.getElementById('pfe-adaptive').value;
        const out = await api.pfGenerate(i, stats, m.label, adaptive === '' ? null : Number(adaptive) / 100);
        if (epoch !== editorEpoch || seq !== m.genSeq || (!draft && S.model?.seats[i] !== m)) return false;
        Object.assign(m, { profile: out.profile, implied: out.implied, stats, painted: false, needsGeneration:false });
        resetPaint(m);
        evidencePreviewKey = '';
        evidencePreview = null;
        ++evidencePreviewRequest;
        updateRangeNote();
        const impEl = document.getElementById('pfe-implied');
        if (editingModel() === m && impEl) {
          renderEditorImplied();
          document.getElementById('pfe-gen').classList.remove('attn');
          paintBucket();
        }
        renderModel();
        return true;
      } catch (e) {
        if (epoch !== editorEpoch || seq !== m.genSeq) return false;
        // auto-runs report quietly (e.g. "solve first" right after an apply)
        const impEl = document.getElementById('pfe-implied');
        if (impEl) impEl.textContent = e.message;
        manager.querySelector('[role="status"]').textContent = e.message;
        return false;
      }
    }
    document.getElementById('pfe-gen').addEventListener('click', () => doGenerate(false));
    document.getElementById('pfe-preview-seat')?.addEventListener('change', e => {
      i = +e.target.value;
      contextualPreviewKey = '';
      resetContextualAmounts();
      S.painting = false;
      paintBucket();
      updateRangeNote();
      if (!m.painted) doGenerate(true);
      else manager.querySelector('[role="status"]').textContent = 'Click Generate from stats to replace painted ranges for the selected position.';
    });
    document.getElementById('pfe-adaptive').addEventListener('change', () => {
      const v = document.getElementById('pfe-adaptive').value;
      const f = v === '' ? null : Number(v) / 100;
      if (f !== null && (!Number.isFinite(f) || f <= 0 || f > 1)) return editorMessage('Use 1 to 100, or blank for fixed responses');
      m.profile.response = { ...m.profile.response, adaptive_from: f };
      paintBucket();
      updateRangeNote();
      renderModel();
    });
    // one set of numbers for the whole table: copy this seat's stats +
    // postflop tendencies to every other seat and generate each seat's
    // (positional) profile from them
    document.getElementById('pfe-copyall').addEventListener('click', async () => {
      if (lastIter < 1) return editorMessage('Build and solve a Preflop game first');
      const stats = collectStats();
      const pf = collectPf();
      const label = m.label;
      const adaptive = document.getElementById('pfe-adaptive').value;
      const btn = document.getElementById('pfe-copyall');
      btn.classList.add('busy');
      let n = 0;
      try {
        for (let j = 0; j < S.model.seats.length; j++) {
          if (!draft && j === i) continue;
          const mj = S.model.seats[j];
          try {
            const out = await api.pfGenerate(j, stats, label, adaptive === '' ? null : Number(adaptive) / 100);
            if (!S.model || S.model.seats[j] !== mj) continue;
            Object.assign(mj, {
              mode: 'ruled', profile: out.profile, implied: out.implied, label,
              stats: { ...stats }, postflop: JSON.parse(JSON.stringify(pf)),
              painted: false, selValue: `custom:${label}`,
            });
            resetPaint(mj);
            n++;
          } catch (e) { editorMessage(`${S.positions[j]}: ${errText(e)}`); }
        }
        m.stats = stats;
        m.postflop = pf;
        S.postflopDirty = true;
        renderModel();
        editorMessage(`"${label}" tendencies copied to ${n} seat${n === 1 ? '' : 's'}`);
      } finally {
        btn.classList.remove('busy');
      }
    });
    // Stat edits regenerate automatically — EXCEPT when the profile has
    // hand-painted edits, which a rebuild would replace: then the button
    // lights up and the user chooses.
    let genTimer = null;
    editorCleanup = () => { clearTimeout(genTimer); S.painting = false; };
    const datasetToggle = document.getElementById('pfe-dataset');
    const datasetFields = () => {
      for (const id of ['pfe-or','pfe-ol','pfe-ir','pfe-lb']) document.getElementById(id).disabled = !!datasetToggle?.checked;
      const responses = st0.dataset?.rows?.some(r => r.responses?.raise != null);
      for (const id of ['pfe-3b','pfe-fvr','pfe-sq','pfe-fsq','pfe-f3b','pfe-fvrb','pfe-fvrthr',...(measuredBands || []).map((_,i)=>`pfe-band-${i}`)]) {
        document.getElementById(id).disabled = !!datasetToggle?.checked && !!responses;
      }
      syncDerived();
    };
    datasetFields();
    datasetToggle?.addEventListener('change', () => {
      datasetFields();
      document.getElementById('pfe-stats').dispatchEvent(new Event('change'));
    });
    document.getElementById('pfe-stats').addEventListener('change', () => {
      if (m.painted) {
        document.getElementById('pfe-gen').classList.add('attn');
        document.getElementById('pfe-implied').textContent =
          'stats edited — GENERATE rebuilds the ranges (replaces your painted edits)';
        return;
      }
      clearTimeout(genTimer);
      genTimer = setTimeout(() => doGenerate(true), 400);
    });
    document.querySelectorAll('#pfe-buckets button').forEach(b =>
      b.addEventListener('click', () => {
        S.editBucket = +b.dataset.b;
        document.querySelectorAll('#pfe-buckets button').forEach(x =>
          x.classList.toggle('active', x === b));
        paintBucket();
        updateRangeNote();
      }));
    // the brush (S.paintAction / S.paintWeight) survives across editor
    // sessions — sync the controls to it so they show what a click paints
    document.querySelectorAll('#pfe-palette button').forEach(b => {
      b.classList.toggle('active', b.dataset.a === S.paintAction);
      b.addEventListener('click', () => {
        S.paintAction = b.dataset.a;
        document.querySelectorAll('#pfe-palette button').forEach(x =>
          x.classList.toggle('active', x === b));
        renderPaintState();
      });
    });
    const w = document.getElementById('pfe-w');
    w.value = Math.round(S.paintWeight * 100);
    document.getElementById('pfe-wv').textContent = `${Math.round(S.paintWeight * 100)}%`;
    w.addEventListener('input', () => {
      S.paintWeight = +w.value / 100;
      document.getElementById('pfe-wv').textContent = `${w.value}%`;
      renderPaintState();
    });
    document.getElementById('pfe-paint-undo').addEventListener('click', () => {
      undoPaint(); paintBucket(); updateRangeNote();
    });
    document.getElementById('pfe-paint-clear').addEventListener('click', () => {
      clearPaint(); paintBucket(); updateRangeNote();
    });
    document.getElementById('pfe-save').addEventListener('click', async () => {
      const name = document.getElementById('pfe-name').value.trim();
      if (!name) return editorMessage('Give the model a name before saving');
      const button = document.getElementById('pfe-save');
      button.disabled = true;
      try {
        clearTimeout(genTimer);
        if ((m.needsGeneration || !m.painted) && !await doGenerate(false)) return;
        if (epoch !== editorEpoch) return;
        m.profile.name = name;
        m.label = name;
        m.profile.postflop = m.postflop || collectPf();
        // the numbers the ranges came from travel with the file, so the
        // editor shows them again on reload (the engine ignores the key)
        m.profile.stats = collectStats();
        m.stats = { ...m.profile.stats };
        await api.pfProfileSave(name, m.profile);
        SAVED_PROFILES = await api.pfProfiles();
        if (deletedModels.has(`saved:${name}`)) updateDeletedModels([`saved:${name}`], false);
        editorMessage(`Model "${name}" saved`);
        renderModel();
      } catch (e) { manager.querySelector('[role="status"]').textContent = e.message; }
      finally { button.disabled = false; }
    });
    buildPaintGrid();
    updateRangeNote();
    renderEditorImplied();
    paintBucket();
    els.editor.tabIndex = -1;
    els.editor.scrollTop = 0;
    els.editor.focus();
    if (m.needsGeneration) doGenerate(true);
  }

  let paintCells = [];
  function buildPaintGrid() {
    const g = document.getElementById('pfl-paint');
    g.innerHTML = '';
    paintCells = [];
    for (let i = 0; i < 13; i++) {
      for (let j = 0; j < 13; j++) {
        const cell = document.createElement('div');
        cell.className = 'cell';
        cell.innerHTML = `<div class="bars"></div><div class="fill"></div><div class="tag">${cellInfo(i, j).label}</div><div class="sub"></div>`;
        const idx = (12 - i) * 13 + (12 - j);
        cell.dataset.idx = String(idx);
        // roving tabindex: the grid is one tab stop, arrows move inside it
        cell.tabIndex = paintCells.length ? -1 : 0;
        cell.setAttribute('role', 'button');
        cell.addEventListener('mousedown', e => { e.preventDefault(); S.painting = true; paintClass(idx); });
        cell.addEventListener('mouseenter', () => { if (S.painting) paintClass(idx); });
        g.appendChild(cell);
        paintCells.push(cell);
      }
    }
    g.addEventListener('keydown', e => {
      const cell = e.target.closest('.cell');
      if (!cell || !g.contains(cell)) return;
      const step = { ArrowLeft: -1, ArrowRight: 1, ArrowUp: -13, ArrowDown: 13 }[e.key];
      if (step) {
        e.preventDefault();
        const next = paintCells[paintCells.indexOf(cell) + step];
        if (!next) return;
        cell.tabIndex = -1;
        next.tabIndex = 0;
        next.focus();
      } else if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        paintClass(+cell.dataset.idx);
      }
    });
  }
  // The window-level mouseup lives at module scope (one handler, not one per
  // editor open).
  onPaintRelease = () => { S.painting = false; };

  function bucketPol(forPainting = false) {
    const m = editingModel();
    if (!m || !m.profile) return null;
    if (S.editBucket === 4 && editorContextualVersion()) {
      // A contextual grid is an inspection of one state, never a replacement
      // for the model or a hand-paintable global re-raise policy.
      if (!contextualPreview || contextualPreview.error) return null;
      if (contextualPreview.policy) return contextualPreview.policy;
    }
    if (S.editBucket === 4 && editorColdReraise()) return m.profile.response.cold_reraise;
    const contexts = m.profile.response?.limp_contexts;
    if (S.editBucket === 1 && contexts?.length) {
      const context = contexts[S.editLimpContext || 0] || contexts[0];
      if (forPainting && !(S.editLimpContext || 0)) m.profile.buckets[1] = context.policy;
      return context.policy;
    }
    let pol = m.profile.buckets[S.editBucket];
    if (!pol && forPainting) {
      // take over a solver-played bucket: start from all-fold
      pol = {
        call: new Array(169).fill(0),
        raise: new Array(169).fill(0),
        jam: new Array(169).fill(0),
        raise_size: (m.stats && m.stats.raise_size) || 'min',
      };
      m.profile.buckets[S.editBucket] = pol;
    }
    return pol;
  }

  function editorWinsUnopened() {
    const seat = S.editSeat ?? Number(document.getElementById('pfe-preview-seat')?.value || 0);
    return seat === unraisedWinner(editorContextualConfig(), S.positions);
  }

  function editorColdReraise() {
    return S.editReraiseContext === 'cold' && !!editingModel()?.profile?.response?.cold_reraise;
  }

  function editorContextualVersion() {
    return editingModel()?.profile?.response?.contextual_reraise || null;
  }

  function editorContextualConfig() {
    // Preview the built game, even if the scenario form has unbuilt edits.
    return S.builtCfg ? JSON.parse(S.builtCfg) : config();
  }

  function resetContextualAmounts() {
    const cfg = editorContextualConfig();
    const seat = S.editSeat ?? Number(document.getElementById('pfe-preview-seat')?.value || 0);
    const depth = Number(document.getElementById('pfe-context-depth')?.value || 2);
    const post = cfg.posts[seat] || 0;
    const available = cfg.stack - post;
    const open = Math.min(2.5, Math.max(2, cfg.stack * .08));
    const previous = depth === 2 ? open : open * 3;
    const invested = S.editReraiseContext === 'cold' ? post
      : Math.min(Math.max(previous, post + Math.min(.25, available / 4)), post + available * .6);
    // Short stacks may necessarily cross the adaptive threshold. Keep a valid
    // paid entry/call; the explanatory note makes that override visible.
    const faced = Math.max(Math.min(depth === 2 ? open * 3.6 : open * 9.6, cfg.stack * .24),
      invested + Math.min(1, (cfg.stack - invested) / 2));
    document.getElementById('pfe-context-invested').value = Number(invested.toFixed(3));
    document.getElementById('pfe-context-to').value = Number(faced.toFixed(3));
    document.getElementById('pfe-context-pot').value = Number((faced + previous + invested + 1.5).toFixed(3));
  }

  async function refreshContextualPreview() {
    const version = editorContextualVersion();
    if (S.editBucket !== 4 || !version) return;
    const epoch = editorEpoch;
    const cfg = editorContextualConfig();
    const seat = S.editSeat ?? Number(document.getElementById('pfe-preview-seat')?.value || 0);
    const context = {
      entry: S.editReraiseContext,
      raises: Number(document.getElementById('pfe-context-depth').value),
      invested: Number(document.getElementById('pfe-context-invested').value),
      to_call: Number(document.getElementById('pfe-context-to').value),
      pot: Number(document.getElementById('pfe-context-pot').value),
    };
    const key = JSON.stringify({version,cfg,seat,context});
    if (key === contextualPreviewKey) return;
    contextualPreviewKey = key;
    contextualPreview = null;
    const request = ++contextualPreviewRequest;
    // Invalidate evidence immediately, before the frequency request finishes.
    // It has its own key and stale-response guard for these same inputs.
    updateRangeNote();
    const status = document.getElementById('pfe-contextual-status');
    status.textContent = 'Calculating contextual frequencies…';
    document.getElementById('pfl-paint').classList.add('hidden');
    try {
      const out = await api.pfContextualPreview(version, cfg, seat, context);
      if (epoch !== editorEpoch || request !== contextualPreviewRequest) return;
      contextualPreview = out;
    } catch (e) {
      if (epoch !== editorEpoch || request !== contextualPreviewRequest) return;
      contextualPreview = {error: e.message};
    }
    paintBucket();
    updateRangeNote();
  }

  function renderReraiseContext() {
    const row = document.getElementById('pfe-reraise-context-row');
    row?.classList.toggle('hidden', S.editBucket !== 4);
    if (S.editBucket !== 4) return;
    const contextual = !!editorContextualVersion();
    const hasCold = !!editingModel()?.profile?.response?.cold_reraise;
    const select = document.getElementById('pfe-reraise-context');
    if (select.dataset.contextual !== String(contextual)) {
      select.dataset.contextual = String(contextual);
      select.innerHTML = contextual
        ? '<option value="cold">No voluntary entry yet</option><option value="called">Previously limped / called</option><option value="raised">Previously raised</option>'
        : '<option value="cold">Facing a re-raise cold</option><option value="entered">After already entering</option>';
      S.editReraiseContext = 'cold';
      contextualPreviewKey = '';
      resetContextualAmounts();
    }
    select.querySelector('[value="cold"]').disabled = !hasCold;
    select.value = contextual ? S.editReraiseContext : editorColdReraise() ? 'cold' : 'entered';
    select.onchange = () => {
      S.painting = false;
      S.editReraiseContext = select.value;
      if (contextual) resetContextualAmounts();
      paintBucket(); updateRangeNote();
    };
    document.getElementById('pfe-contextual-fields').classList.toggle('hidden', !contextual);
    document.getElementById('pfe-reraise-explanation').textContent = contextual
      ? `Contextual v1 · ${editorContextualConfig().stack}bb starting stack. Frequencies are conditional on arriving here, not a share of all dealt hands. This preview is read-only.`
      : editorColdReraise()
      ? 'No chips invested voluntarily yet \u2014 e.g. an open and a 3-bet before the BB acts.'
      : 'Conditional on having already limped, called or raised \u2014 a 50% call here is not 50% of all dealt hands. Sparse hands borrow pooled estimates; raise depths and prices are mixed.';
    if (contextual) {
      refreshContextualPreview();
      if (contextualPreview) {
        const out = contextualPreview;
        const adaptive = editingModel()?.profile?.response?.adaptive_from;
        const faced = Number(document.getElementById('pfe-context-to').value);
        const learns = adaptive != null && faced >= editorContextualConfig().stack * adaptive;
        document.getElementById('pfe-contextual-status').textContent = out.error ||
          `${!out.policy && out.nominal_price != null ? `Call price ${(out.nominal_price * 100).toFixed(1)}% · ` : ''}${out.note}${learns ? ' In the game, this amount reaches the adaptive threshold: the solver learns the response instead of fixing these frequencies.' : ''}`;
      }
    }
  }

  function editorUnopenedNotApplicable() {
    return S.editBucket === 0 && editorWinsUnopened();
  }

  function renderEditorImplied() {
    const el = document.getElementById('pfe-implied');
    if (!el) return;
    el.classList.toggle('hidden', editorUnopenedNotApplicable());
    const m = editingModel(), imp = m?.implied;
    if (!imp) { el.textContent = ''; return; }
    const prefix = editorWinsUnopened() ? '' : `first-in ${imp.vpip.toFixed(1)}% (raises ${imp.pfr.toFixed(1)}%) · `;
    el.textContent = prefix + `3-bets ${imp.threebet.toFixed(1)}% · folds to a raise ${(100 - imp.cont_vs_raise).toFixed(0)}% cold` +
      (m.stats?.cont_vs_raise_limped != null ? ` / ${(100 - m.stats.cont_vs_raise_limped).toFixed(0)}% after limping` : '') +
      (editorContextualVersion() ? ' · re-raise responses vary with the situation' : editorWinsUnopened() ? '' : ` · folds to a 3-bet ${(100 - imp.cont_vs_3bet).toFixed(0)}% of its opens`);
  }

  /** Read-only provenance for this exact grid, with stale responses discarded. */
  async function updateRangeNote() {
    const el = document.getElementById('pfe-rangenote');
    const pm = editingModel();
    if (!el || !pm) return;
    if (editorUnopenedNotApplicable()) {
      ++evidencePreviewRequest;
      evidencePreviewKey = '';
      evidencePreview = null;
      renderModelEvidence(el, null);
      return;
    }
    if (pm.needsGeneration) {
      ++evidencePreviewRequest;
      evidencePreviewKey = '';
      evidencePreview = null;
      renderModelEvidence(el, {kind:'pending',label:'Ranges not generated',summary:'Generate from stats to create this model.',details:[]});
      return;
    }
    const contextual = S.editBucket === 4 && !!editorContextualVersion();
    const body = {
      cfg: editorContextualConfig(),
      seat: S.editSeat ?? Number(document.getElementById('pfe-preview-seat')?.value || 0),
      profile: pm.profile,
      bucket: S.editBucket,
      cold: S.editBucket === 4 && editorColdReraise(),
    };
    const limp = pm.profile.response?.limp_contexts?.[S.editLimpContext || 0];
    if (S.editBucket === 1 && limp) body.limp_context = {limpers:limp.limpers,free_check:limp.free_check};
    if (contextual) body.context = {
      entry: S.editReraiseContext,
      raises: Number(document.getElementById('pfe-context-depth').value),
      invested: Number(document.getElementById('pfe-context-invested').value),
      to_call: Number(document.getElementById('pfe-context-to').value),
      pot: Number(document.getElementById('pfe-context-pot').value),
    };
    const key = JSON.stringify(body);
    if (key === evidencePreviewKey && evidencePreview) {
      renderModelEvidence(el, evidencePreview);
      return;
    }
    if (key === evidencePreviewKey) return;
    evidencePreviewKey = key;
    evidencePreview = null;
    const request = ++evidencePreviewRequest;
    const epoch = editorEpoch;
    renderModelEvidence(el, {kind:'pending',label:'Checking source',summary:'Reading evidence for this situation…',details:[]});
    // Drag-painting and rapid context changes need only the final source query.
    await new Promise(resolve => setTimeout(resolve, 80));
    if (epoch !== editorEpoch || request !== evidencePreviewRequest) return;
    try {
      const out = await api.pfModelEvidence(body);
      if (epoch !== editorEpoch || request !== evidencePreviewRequest) return;
      const generatedKey = body.cold ? 'cold_reraise' : ['unopened','limps','raise','squeeze','reraise'][body.bucket];
      const generated = !pm.painted && pm.implied?.model_evidence?.[generatedKey];
      evidencePreview = !contextual && out.kind === 'saved_policy' && generated?.kind === 'stat_derived' ? {...generated, sizing: out.sizing} : out;
    } catch (e) {
      if (epoch !== editorEpoch || request !== evidencePreviewRequest) return;
      evidencePreview = {kind:'unavailable',label:'Evidence unavailable',summary:'The source could not be checked.',details:[e.message]};
    }
    renderModelEvidence(el, evidencePreview);
  }

  // ----- paint state: the bucket badge, its caption, undo/clear -----
  // A bucket key names the exact policy being painted (limp contexts and the
  // two re-raise situations are separate policies).
  const bucketKey = () => S.editBucket === 1 ? `limps:${S.editLimpContext || 0}`
    : S.editBucket === 4 ? (editorColdReraise() ? 'reraise:cold' : 'reraise:entered')
    : ['unopened', 'limps', 'raise', 'squeeze', 'reraise'][S.editBucket];
  function paintSituation() {
    const m = editingModel();
    if (S.editBucket === 0) return editorWinsUnopened() ? 'UNOPENED · last blind' : 'UNOPENED · first in';
    if (S.editBucket === 1) {
      const c = m?.profile?.response?.limp_contexts?.[S.editLimpContext || 0];
      return c ? `VS LIMPS · ${c.limpers === 3 ? '3+' : c.limpers} limper${c.limpers === 1 ? '' : 's'} · ${c.free_check ? 'check free' : 'call / complete'}` : 'VS LIMPS';
    }
    if (S.editBucket === 2) return 'VS RAISE · one raise';
    if (S.editBucket === 3) return 'SQUEEZE · raise + callers';
    if (editorContextualVersion()) {
      const depth = document.getElementById('pfe-context-depth')?.value;
      const entry = { cold: 'no voluntary entry', called: 'after limp / call', raised: 'after raising' }[S.editReraiseContext] || S.editReraiseContext;
      return `VS 3-BET+ · ${entry} · ${depth === '3' ? '4-bet+' : '3-bet'}`;
    }
    return editorColdReraise() ? 'VS 3-BET+ · no voluntary entry' : 'VS 3-BET+ · after entering';
  }
  function bucketPolExists() {
    const m = editingModel();
    if (!m?.profile) return false;
    if (S.editBucket === 4 && editorColdReraise()) return true;
    if (S.editBucket === 1 && m.profile.response?.limp_contexts?.length) {
      return !!(S.editLimpContext || 0) || !!m.profile.buckets[1];
    }
    return !!m.profile.buckets[S.editBucket];
  }
  function paintSnapshot() {
    const m = editingModel();
    const pol = bucketPol();
    const bands = S.editBucket === 2 && m?.profile?.vs_raise_bands
      ? m.profile.vs_raise_bands.map(([, b]) => [[...b.call], [...b.raise], [...b.jam]]) : null;
    // A solver-managed bucket has no policy yet: the snapshot only records
    // that undoing the first stroke must give it back to the solver.
    if (!pol && !bands) return { bucket: S.editBucket, existed: bucketPolExists(), pol: null, bands: null };
    return {
      bucket: S.editBucket,
      existed: bucketPolExists(),
      pol,
      call: pol ? [...pol.call] : null,
      raise: pol ? [...pol.raise] : null,
      jam: pol ? [...pol.jam] : null,
      bands,
    };
  }
  function restorePaint(snap) {
    if (!snap) return;
    const m = editingModel();
    if (snap.pol && snap.call) {
      snap.pol.call = [...snap.call];
      snap.pol.raise = [...snap.raise];
      snap.pol.jam = [...snap.jam];
    }
    if (!snap.existed && m?.profile?.buckets) {
      delete m.profile.buckets[snap.bucket]; // back to solver-managed
    }
    if (snap.bands && m?.profile?.vs_raise_bands) {
      m.profile.vs_raise_bands.forEach(([, b], k) => {
        const s = snap.bands[k];
        if (!s) return;
        b.call = [...s[0]]; b.raise = [...s[1]]; b.jam = [...s[2]];
      });
    }
  }
  function undoPaint() {
    const m = editingModel();
    const key = bucketKey();
    const history = m?.paintHistory?.[key];
    if (!history?.length) return;
    restorePaint(history.pop());
    if (!history.length) {
      delete m.paintHistory[key];
      delete m.paintBase[key];
      m.paintedBuckets?.delete(key);
    }
  }
  function clearPaint() {
    const m = editingModel();
    const key = bucketKey();
    const base = m?.paintBase?.[key];
    if (!base) return;
    restorePaint(base);
    delete m.paintHistory[key];
    delete m.paintBase[key];
    m.paintedBuckets?.delete(key);
  }
  function renderPaintState() {
    const caption = document.getElementById('pfe-paint-caption');
    const badge = document.getElementById('pfe-paint-badge');
    const undo = document.getElementById('pfe-paint-undo');
    const clear = document.getElementById('pfe-paint-clear');
    const m = editingModel();
    if (!caption || !badge || !m) return;
    const brush = S.paintAction === 'fold' ? 'fold' : `${S.paintAction} ${Math.round(S.paintWeight * 100)}%`;
    caption.textContent = `Painting ${paintSituation()} · ${brush}`;
    const key = bucketKey();
    const painted = !!m.paintedBuckets?.has(key);
    badge.classList.toggle('hidden', !painted);
    undo.classList.toggle('hidden', !painted);
    clear.classList.toggle('hidden', !painted);
    const canClear = !!m.paintBase?.[key];
    clear.disabled = !canClear;
    clear.dataset.tip = canClear ? 'Discard every stroke in this bucket from this session.' : 'No pre-paint copy in this session.';
  }

  function paintClass(idx) {
    if (editorUnopenedNotApplicable() || editingModel()?.needsGeneration || (S.editBucket === 4 && editorContextualVersion())) return;
    const pm = editingModel();
    const key = bucketKey();
    const before = paintSnapshot();
    const pol = bucketPol(true);
    if (!pol) return;
    if (pm) {
      pm.painted = true; // stat edits now need explicit GENERATE
      if (before) {
        const history = (pm.paintHistory ??= {})[key] ??= [];
        history.push(before);
        if (history.length > 40) history.shift();
        (pm.paintBase ??= {})[key] ??= before;
        (pm.paintedBuckets ??= new Set()).add(key);
      }
    }
    pol.call[idx] = 0;
    pol.raise[idx] = 0;
    pol.jam[idx] = 0;
    if (S.paintAction !== 'fold') pol[S.paintAction][idx] = S.paintWeight;
    const freeLimp = S.editBucket === 1 && pm?.profile.response?.limp_contexts?.[S.editLimpContext || 0]?.free_check;
    if (freeLimp) {
      // There is no fold when checking is free. A partial check brush leaves
      // the remainder raising, rather than drawing an impossible fold share.
      if (S.paintAction === 'call') pol.raise[idx] = 1 - S.paintWeight;
      pol.call[idx] = Math.max(0, 1 - pol.raise[idx] - pol.jam[idx]);
    }
    // A hand-painted cold response must reach the live size-band policies too.
    if (S.editBucket === 2 && pm?.profile.vs_raise_bands) {
      for (const [, band] of pm.profile.vs_raise_bands) {
        for (const action of ['call','raise','jam']) band[action][idx] = pol[action][idx];
      }
    }
    paintBucket();
    updateRangeNote();
  }

  function paintBucket() {
    renderReraiseContext();
    const unavailable = editorUnopenedNotApplicable();
    const contextual = S.editBucket === 4 && !!editorContextualVersion();
    document.getElementById('pfe-not-applicable')?.classList.toggle('hidden', !unavailable);
    document.getElementById('pfe-paint-controls')?.classList.toggle('hidden', unavailable || contextual);
    document.getElementById('pfl-paint')?.classList.toggle('hidden', unavailable || (contextual && (!contextualPreview || !!contextualPreview.error)));
    renderEditorImplied();
    renderPaintState();
    if (unavailable) {
      S.painting = false;
      document.getElementById('pfe-limp-context-row')?.classList.add('hidden');
      return;
    }
    const contexts = editingModel()?.profile?.response?.limp_contexts || [];
    const select = document.getElementById('pfe-limp-context');
    const row = document.getElementById('pfe-limp-context-row');
    if (row) row.classList.toggle('hidden', S.editBucket !== 1 || !contexts.length);
    if (select && contexts.length) {
      select.innerHTML = contexts.map((c, i) => c.free_check === contexts[0].free_check
        ? `<option value="${i}">${c.limpers === 3 ? '3+' : c.limpers} limper${c.limpers === 1 ? '' : 's'} · ${c.free_check ? 'check free' : 'call / complete'}</option>` : '').join('');
      select.value = String(S.editLimpContext || 0);
      select.onchange = () => { S.editLimpContext = +select.value; paintBucket(); updateRangeNote(); };
    }
    const pol = bucketPol();
    const freeLimp = S.editBucket === 1 && contexts[S.editLimpContext || 0]?.free_check;
    const foldBrush = document.querySelector('#pfe-palette [data-a="fold"]');
    const callBrush = document.querySelector('#pfe-palette [data-a="call"]');
    if (foldBrush) foldBrush.disabled = !!freeLimp;
    if (callBrush) callBrush.textContent = freeLimp ? 'CHECK' : 'CALL';
    if (!pol) {
      // Inspecting a solver-managed bucket must not create an all-fold lock.
      // Only an explicit brush action takes ownership of this bucket.
      for (const cell of paintCells) {
        cell.querySelector('.bars').replaceChildren();
        cell.classList.add('empty');
        cell.dataset.tip = 'Solver-managed range · paint a hand to create a fixed policy';
        cell.setAttribute('aria-label', cell.dataset.tip);
      }
      return;
    }
    for (let i = 0; i < 13; i++) {
      for (let j = 0; j < 13; j++) {
        const cell = paintCells[i * 13 + j];
        const idx = (12 - i) * 13 + (12 - j);
        const c = pol.call[idx] || 0, r = pol.raise[idx] || 0, jm = pol.jam[idx] || 0;
        const f = Math.max(0, 1 - c - r - jm);
        const bars = cell.querySelector('.bars');
        bars.style.height = '100%';
        bars.style.opacity = 1;
        bars.innerHTML =
          (r > 0.001 ? `<div style="width:${r * 100}%;background:${PCOLORS.raise}"></div>` : '') +
          (jm > 0.001 ? `<div style="width:${jm * 100}%;background:${PCOLORS.jam}"></div>` : '') +
          (c > 0.001 ? `<div style="width:${c * 100}%;background:${PCOLORS.call}"></div>` : '') +
          (f > 0.001 ? `<div style="width:${f * 100}%;background:#20242a"></div>` : '');
        cell.classList.toggle('empty', c + r + jm < 0.002);
        cell.dataset.tip = `${cellInfo(i, j).label}: raise ${(r * 100).toFixed(0)}% · jam ${(jm * 100).toFixed(0)}% · ${freeLimp ? 'check' : 'call'} ${(c * 100).toFixed(0)}%${freeLimp ? '' : ` · fold ${(f * 100).toFixed(0)}%`}`;
        if (S.editBucket === 4) cell.dataset.tip += editorColdReraise() ? ' · facing a re-raise cold' : ' · conditional on prior entry';
        cell.setAttribute('aria-label', cell.dataset.tip);
      }
    }
  }

  els.exportBtn.addEventListener('click', async () => {
    if (S.view && S.view.exportable3 && !canon.on) {
      try {
        const ex = await api.pfExport3(S.cursor);
        if (window.gtopenApplyThreeWay) window.gtopenApplyThreeWay(ex);
      } catch (e) { toast(e.message, true); }
      return;
    }
    try {
      const ex = canon.on
        ? await api.rangeLabExport({ ...canonRequest(S.cursor), rake_pct: Number(els.canonRakePct.value) || 0, rake_cap: Number(els.canonRakeCap.value) || 0 })
        : await api.pfExport(S.cursor);
      const steps = takenSteps(S.cursor.length);
      const lineText = canon.on
        ? 'Range Lab · ' + (steps.filter(s => s.kind !== 'fold').map(s => `${s.pos} ${s.label}`).join(' · ') || 'root')
        : steps.map(s => `${s.pos} ${s.label}`).join(' · ') || 'root';
      // ribbon segments for Browse: continuing actions only (folds are just
      // dead money in the pot, same convention as the study module)
      ex.segments = steps
        .filter(st => st.kind !== 'fold')
        .map(st => ({ pos: st.pos, label: st.label }));
      // carry each flop player's postflop profile (if the seat is modeled)
      // and who arrives with the initiative, for villain locks in Browse
      const profFor = pos => {
        if (canon.on) return null;
        const k = S.positions.indexOf(pos);
        const sm = k >= 0 && S.model ? S.model.seats[k] : null;
        return sm && sm.mode === 'ruled' && sm.postflop
          ? { name: sm.label, stats: sm.postflop } : null;
      };
      ex.villains = { oop: profFor(ex.oop_pos), ip: profFor(ex.ip_pos) };
      let lastAggr = null;
      steps.forEach(st => { if (st.kind === 'raise' || st.kind === 'jam') lastAggr = st.pos; });
      ex.aggressor = lastAggr === ex.oop_pos ? 0 : lastAggr === ex.ip_pos ? 1 : null;
      onExport(ex, lineText);
    } catch (e) { toast(e.message, true); }
  });

  function hideGrid() {
    els.grid.classList.add('hidden');
    els.fillSeg.classList.add('hidden');
    els.rangeSeg.innerHTML = '';
    els.legend.innerHTML = '';
    els.gridCap.innerHTML = '';
  }

  /** Repaint the persistent cells from the current view (Browse STRAT style:
   *  discrete action colors at full opacity, reach shown as bottom-anchored
   *  bar height, empty cells dark with a dim label). */
  function paintGrid() {
    const v = S.view;
    if (!v) return;
    // action nodes paint the actor's strategy; flop terminals paint the
    // selected live player's ARRIVING RANGE (single-color, reach heights)
    let reachVec = null, na = 0;
    if (v.kind === 'action') {
      reachVec = v.reach;
      na = v.actions.length;
    } else if (v.kind === 'pot_share' || v.kind === 'fold_win') {
      reachVec = (v.reaches_all || [])[S.rangeSeat] || null;
    }
    if (!reachVec) return;
    const colors = S.colors;
    // bar height = the actual fraction of the hand's combos still held here
    const fillH = r => (r <= 1e-9 ? 0 : Math.min(1, r));
    for (let i = 0; i < 13; i++) {
      for (let j = 0; j < 13; j++) {
        const cell = S.cells[i * 13 + j];
        const idx = (12 - i) * 13 + (12 - j);
        const reach = reachVec[idx] || 0;
        const bars = cell.querySelector('.bars');
        const segs = [];
        let cont = 0; // how often the hand continues (everything but fold)
        if (v.kind === 'action') {
          // biggest action on the LEFT (jam / largest raise), fold on the
          // right — the engine lists actions fold-first, so walk backwards
          for (let a = na - 1; a >= 0; a--) {
            const f = v.strategy[a * 169 + idx];
            if (v.actions[a].kind !== 'fold') cont += f;
            if (f > 0.001) {
              segs.push(`<div style="width:${(f * 100).toFixed(1)}%;background:${colors[a]}"></div>`);
            }
          }
        } else {
          segs.push('<div style="width:100%;background:#f28c26"></div>');
        }
        bars.innerHTML = segs.join('');
        bars.style.height = `${(fillH(reach) * 100).toFixed(1)}%`;
        bars.style.opacity = reach > 1e-9 ? 1 : 0;
        cell.classList.toggle('empty', reach < 0.002);
        const lab = cellInfo(i, j).label;
        if (v.kind === 'action') {
          // plain text (one action per line) in data-tip; the aligned
          // two-column table in data-tip-html for tooltip.js to prefer
          const pct = k => `${(v.strategy[k * 169 + idx] * 100).toFixed(1)}%`;
          const inRange = reach < 0.995 ? `${(reach * 100).toFixed(0)}% of combos still in range` : '';
          if (reach < 0.002) {
            cell.dataset.tip = `${lab} — ${v.actor_pos} almost never holds this here`;
            cell.dataset.tipHtml = '';
          } else {
            cell.dataset.tip = lab + (inRange ? ` — ${inRange}` : '') + '\n' +
              v.actions.map((a, k) => `${a.label}  ${pct(k)}`).join('\n');
            cell.dataset.tipHtml = `<b>${lab}</b>` +
              (inRange ? ` <span class="dim">${inRange}</span>` : '') +
              `<div class="tip-rows">` + v.actions.map((a, k) =>
                `<span>${esc(a.label)}</span><span>${pct(k)}</span>`).join('') +
              `</div>`;
          }
        } else {
          const pos = v.positions[S.rangeSeat];
          cell.dataset.tip = reach < 0.002
            ? `${lab} — not in ${pos}'s range here`
            : `${lab} — ${(reach * 100).toFixed(0)}% of ${pos}'s combos still held here`;
          cell.dataset.tipHtml = '';
        }
        // corner number, as in Browse: the continue frequency of a MIXED
        // hand (pure folds / pure continues stay clean)
        const mixed = v.kind === 'action' && reach >= 0.002 && cont >= 0.03 && cont <= 0.97;
        cell.querySelector('.sub').textContent = mixed ? `${Math.round(cont * 100)}%` : '';
      }
    }
  }


  function renderLegend(v, colors) {
    els.legend.innerHTML =
      `<span class="key dim">cell colors = ${esc(v.actor_pos)}'s action mix:</span>` +
      [...v.actions.keys()].reverse().map(k =>
        `<span class="key"><i style="background:${colors[k]}"></i>${esc(v.actions[k].label)}</span>`).join('') +
      `<span class="key dim">\u00b7 bar height = share of the hand's combos still in range \u00b7 number = continue frequency of a mixed hand \u00b7 dark cell = hand no longer here</span>`;
  }

  // ----- RANGE LAB CHARTS as the range source -----

  const CANON_KEY = 'pfl-canon';
  const pill = els.canonBox.closest('.pfl-side').querySelector('h2 .pill');
  const PILL_SOLVE = pill?.textContent;
  const canonPrefs = (() => { try { return JSON.parse(localStorage.getItem(CANON_KEY)) || {}; } catch { return {}; } })();
  Object.assign(canon, { tag: canonPrefs.tag ?? null, variant: canonPrefs.variant ?? null, depth: canonPrefs.depth ?? null });
  els.canonRakePct.value = canonPrefs.rakePct ?? els.rakePct.value;
  els.canonRakeCap.value = canonPrefs.rakeCap ?? els.rakeCap.value;
  function saveCanonPrefs() {
    try {
      localStorage.setItem(CANON_KEY, JSON.stringify({ on: canon.on, tag: canon.tag, variant: canon.variant, depth: canon.depth,
        rakePct: els.canonRakePct.value, rakeCap: els.canonRakeCap.value }));
    } catch { /* private window: preferences just aren't kept */ }
  }
  function canonRequest(path) {
    return { tag: canon.tag, variant: canon.variant, depth: canon.depth, path };
  }
  const nearestBy = (list, key, x) => list.reduce((a, b) => Math.abs(key(b) - x) < Math.abs(key(a) - x) ? b : a);

  /** Open size / stage and stack lists for the chosen game, keeping the
   *  current choice when it exists, else the closest to the scenario. */
  function fillCanonAxes() {
    const g = canon.summary?.games.find(x => x.tag === canon.tag);
    const variants = g?.variants || [];
    if (!variants.some(v => v.key === canon.variant)) {
      const open = Math.min(...els.opens.value.split(',').map(parseFloat).filter(x => x > 0));
      const sized = variants.filter(v => v.open_bb != null);
      canon.variant = (Number.isFinite(open) && sized.length ? nearestBy(sized, v => v.open_bb, open) : variants[0])?.key ?? null;
    }
    els.canonVariant.innerHTML = variants.map(v => `<option value="${esc(v.key)}">${esc(v.label)}</option>`).join('');
    if (canon.variant != null) els.canonVariant.value = canon.variant;
    const depths = variants.find(v => v.key === canon.variant)?.depths || [];
    if (!depths.includes(canon.depth)) {
      canon.depth = depths.length ? nearestBy(depths, d => d, Number(canon.depth ?? els.stack.value) || 100) : null;
    }
    els.canonDepth.innerHTML = depths.map(d => `<option value="${d}">${d} bb</option>`).join('');
    if (canon.depth != null) els.canonDepth.value = String(canon.depth);
  }

  async function loadCanon() {
    try { canon.summary = await api.rangeLab(); } catch (e) { els.canonNote.textContent = `Range Lab charts unavailable: ${e.message}`; return; }
    const sm = canon.summary;
    if (!sm.total) {
      els.canonGame.innerHTML = '';
      els.canonNote.innerHTML = 'No Range Lab data found. Put <code>data.js</code> and <code>cash-data.js</code> in ' +
        sm.dirs.map(d => `<code>${esc(d)}</code>`).join(' or ') + ', then pick “Range Lab charts” again.';
      return;
    }
    els.canonGame.innerHTML = sm.games.map(g => `<option value="${esc(g.tag)}">${esc(g.label)}</option>`).join('');
    if (!sm.games.some(g => g.tag === canon.tag)) {
      const table = { players: Number(els.players.value), straddle: els.straddleOn.checked, ante: Number(els.ante.value) };
      canon.tag = (defaultGame(table, sm.games) || sm.games[0]).tag;
    }
    els.canonGame.value = canon.tag;
    fillCanonAxes();
    saveCanonPrefs();
    els.canonNote.textContent = `${sm.total.toLocaleString()} canonical charts. Nothing to build or solve: the charts are the strategy.`;
    if (canon.on) refresh();
  }

  async function refreshCanonical() {
    if (!canon.tag || canon.variant == null || canon.depth == null) { clearRightPanel(); return; }
    const seq = ++refreshSeq;
    try {
      // the line follows seats without a chart (forced folds) to the next decision
      const atEnd = S.cursor.length === S.lineP.length;
      const lineView = await api.rangeLabNode({ ...canonRequest(S.lineP), extend: true });
      if (seq !== refreshSeq) return;
      S.lineP = lineView.path;
      if (atEnd) S.cursor = S.lineP.slice();
      const view = atEnd ? lineView : await api.rangeLabNode(canonRequest(S.cursor));
      if (seq !== refreshSeq) return;
      const cfg = { posts: lineView.posts };
      S.view = formatPreflopView(view, cfg);
      S.lineHist = formatPreflopView(lineView, cfg).history;
    } catch (e) { if (seq === refreshSeq) toast(e.message, true); return; }
    renderRibbon();
    renderNode();
  }

  function setSource(on) {
    els.source.value = on ? 'canonical' : 'solve';
    if (canon.on !== on) {
      canon.lines[canon.on ? 'canonical' : 'solve'] = { cursor: S.cursor, lineP: S.lineP };
      const next = canon.lines[on ? 'canonical' : 'solve'] || { cursor: [], lineP: [] };
      S.cursor = next.cursor;
      S.lineP = next.lineP;
      S.lineHist = null;
      S.view = null;
      canon.on = on;
    }
    els.canonBox.classList.toggle('hidden', !on);
    els.solveSetup.classList.toggle('hidden', on);
    els.solveSaved.classList.toggle('hidden', on);
    els.rangeLab?.classList.toggle('hidden', on);
    // charts have no solve to explain: the rail renumbers instead
    els.step5.classList.toggle('hidden', on);
    renderStepRail();
    renderSaveState();
    renderModelStrip();
    renderApplyState();
    renderExportCard();
    if (pill) pill.textContent = on ? 'Range Lab charts · no solve' : PILL_SOLVE;
    saveCanonPrefs();
    if (on && !canon.summary) loadCanon();
    clearRightPanel();
    refresh();
  }

  const restartCanonLine = () => { S.cursor = []; S.lineP = []; saveCanonPrefs(); refresh(); };
  els.source.addEventListener('change', () => {
    if (els.source.value === 'canonical' && canon.summary && !canon.summary.total) canon.summary = null; // rescan the folders
    setSource(els.source.value === 'canonical');
  });
  els.canonGame.addEventListener('change', () => { canon.tag = els.canonGame.value; fillCanonAxes(); restartCanonLine(); });
  els.canonVariant.addEventListener('change', () => { canon.variant = els.canonVariant.value; fillCanonAxes(); restartCanonLine(); });
  els.canonDepth.addEventListener('change', () => { canon.depth = Number(els.canonDepth.value); restartCanonLine(); });
  els.canonRakePct.addEventListener('change', saveCanonPrefs);
  els.canonRakeCap.addEventListener('change', saveCanonPrefs);
  if (canonPrefs.on) setSource(true);

  // A reload must not hide a live or solved session: adopt the engine's
  // current game (config, seat models, iteration) the way LOAD does, so
  // SOLVE continues it instead of rebuilding over it — pf_build silently
  // stops-and-joins a running solve — and a running solve shows its
  // progress with STOP available instead of an empty lab.
  (async () => {
    let sess;
    try { sess = await api.pfSession(); } catch { return; } // no session (or an older server)
    if (!sess || !sess.config) return;
    try {
      await applyLoadedGame('current session', sess, { quiet: true, onDisk: false });
      els.buildInfo.textContent =
        `${sess.nodes.toLocaleString()} nodes · ${sess.arena_mb.toFixed(0)} MB CPU arenas · session resumed at iter ${sess.iteration}`;
      if (sess.state === 'running') { progressSet(0, 'solving'); }
    } catch (e) { console.warn('could not adopt the preflop session', e); }
  })();

  renderStepRail();
  renderSaveState();
  renderModelStrip();
  renderApplyState();
  renderExportCard();

  return { refresh };
}
