// Tournament (ICM) payouts for the Preflop Lab. With ICM on, every terminal
// pays the change in Malmuth–Harville prize equity, in bb equivalents.

/**
 * An approximate standard payout structure: prizes for places 1..paid of an
 * MTT with `entrants` players, in % of the prize pool. Prizes fall as 1/place
 * with a min cash of 1.5 buy-ins. Real structures pay in bands; ICM only
 * needs the rough shape.
 */
export function standardPayouts(entrants = 1000, paidFrac = 0.15) {
  const paid = Math.max(1, Math.round(entrants * paidFrac));
  const minCash = 1.5 / entrants; // fraction of the pool
  let raw = Array.from({ length: paid }, (_, k) => 1 / (k + 1));
  const s = raw.reduce((a, b) => a + b, 0);
  raw = raw.map(x => Math.max(x / s, minCash));
  const t = raw.reduce((a, b) => a + b, 0);
  return raw.map(x => +(100 * x / t).toFixed(4));
}

/** Stage presets of a 1,000-player MTT, matching the Range Lab ICM stages. */
export const ICM_STAGES = [
  { id: 'ft', label: 'Final table (8 left)', left: 8 },
  { id: 't2', label: 'Two tables left (16 left)', left: 16 },
  { id: 'pct10', label: 'In the money, 10% left (100 left)', left: 100 },
  { id: 'bubble', label: 'Bubble (152 left, 150 paid)', left: 152 },
  { id: 'pct50', label: 'Half the field left (500 left)', left: 500 },
];

const parseList = text => String(text || '').split(/[\s,]+/).filter(Boolean).map(Number);

/** The engine's `icm` object from the panel's fields, or null when off. */
export function icmConfig(state, tableStack) {
  if (!state.on) return null;
  const payouts = parseList(state.payouts);
  if (!payouts.length || payouts.some(p => !Number.isFinite(p) || p < 0)) {
    throw new Error('ICM payouts must be a list of non-negative prizes, first place first.');
  }
  const count = Math.round(Number(state.fieldCount) || 0);
  if (count < 0) throw new Error('Players at other tables must be 0 or more.');
  const stack = String(state.fieldStack ?? '').trim() ? Number(state.fieldStack) : tableStack;
  if (count > 0 && !(stack > 0)) throw new Error('Other tables need a positive average stack.');
  const stackOff = String(state.stackOff ?? '').trim() ? Number(state.stackOff) : null;
  if (stackOff !== null && !(stackOff >= 0)) throw new Error('Stack-off rate must be 0 or more.');
  return {
    payouts, ...(count > 0 ? { field_groups: [{ stack, count }] } : {}),
    ...(stackOff !== null ? { stack_off: stackOff } : {}),
  };
}

/** The scenario block ICM contributes. `edited` must round-trip: a preset
 *  whose payouts were customized must not be refreshed by the preset when the
 *  table player count changes after a save/reload. The rake fields show ICM's
 *  0, so the entered values ride along separately to be restored on turn-off. */
export function icmScenario(state, rakePct, rakeCap) {
  return {
    icm: {
      on: state.on, payouts: state.payouts, fieldCount: state.fieldCount,
      fieldStack: state.fieldStack, stage: state.stage, stackOff: state.stackOff,
      edited: !!state.edited,
    },
    rakePct: +(rakePct || 0), rakeCap: +(rakeCap || 0),
  };
}

/** Panel fields from a saved config's `icm`. */
export function icmFromConfig(cfg) {
  const icm = cfg.icm;
  if (!icm) return { on: false, payouts: '', fieldCount: '', fieldStack: '', stage: '', stackOff: '', edited: false };
  const groups = [...(icm.field_groups || []), ...(icm.field || []).map(stack => ({ stack, count: 1 }))];
  const count = groups.reduce((a, g) => a + g.count, 0);
  const avg = count ? groups.reduce((a, g) => a + g.stack * g.count, 0) / count : '';
  return {
    on: true, payouts: icm.payouts.join(', '), stage: '', edited: false,
    fieldCount: count ? String(count) : '', fieldStack: count ? String(+avg.toFixed(3)) : '',
    stackOff: icm.stack_off === undefined ? '' : String(icm.stack_off),
  };
}

export function createIcmControls(els, positionsFor, changed) {
  let state = { on: false, payouts: '', fieldCount: '', fieldStack: '', stage: '', stackOff: '', edited: false,
    rakePct: '', rakeCap: '' };
  const details = document.createElement('details');
  details.className = 'pfl-position-sizes pfl-icm';
  const summary = document.createElement('summary');
  details.append(summary);
  const note = document.createElement('p');
  note.textContent = 'Every pot pays the change in each player’s prize-pool share (Malmuth–Harville ICM) '
    + 'instead of chips; EVs read in bb equivalents. Stage presets use an approximate 1,000-player payout '
    + 'structure and give other tables the table stack.';
  details.append(note);
  const on = document.createElement('label');
  on.className = 'chk';
  const onBox = document.createElement('input');
  onBox.type = 'checkbox';
  on.append(onBox, ' use tournament payouts (ICM)');
  details.append(on);
  const grid = document.createElement('div');
  grid.className = 'pfl-grid2';
  const stage = document.createElement('select');
  stage.innerHTML = '<option value="">Custom</option>'
    + ICM_STAGES.map(s => `<option value="${s.id}">${s.label}</option>`).join('');
  const stageNote = document.createElement('span');
  stageNote.className = 'dim';
  const stageLabel = document.createElement('label');
  stageLabel.append('Stage ', stage, ' ', stageNote);
  const payouts = document.createElement('textarea');
  payouts.rows = 2;
  payouts.placeholder = 'e.g. 50, 30, 20';
  payouts.setAttribute('aria-label', 'Prize for each place, first place first');
  const payLabel = document.createElement('label');
  payLabel.style.gridColumn = '1 / -1';
  payLabel.append('Payouts, first place first ', payouts);
  const fieldCount = document.createElement('input');
  fieldCount.type = 'number'; fieldCount.min = '0'; fieldCount.step = '1';
  const countLabel = document.createElement('label');
  countLabel.append('Players at other tables ', fieldCount);
  const fieldStack = document.createElement('input');
  fieldStack.type = 'number'; fieldStack.min = '0.5'; fieldStack.step = '0.5';
  const stackLabel = document.createElement('label');
  stackLabel.append('Their stack (bb) ', fieldStack);
  const stackOff = document.createElement('input');
  stackOff.type = 'number'; stackOff.min = '0'; stackOff.step = '0.25'; stackOff.placeholder = 'off';
  const offLabel = document.createElement('label');
  offLabel.dataset.tip = 'How often a pot that sees the flop is played for the stacks behind: all-in with '
    + 'chance k / (k + SPR). 0 prices a flop pot as the pot alone.';
  offLabel.append('Stack-off rate ', stackOff);
  grid.append(stageLabel, countLabel, stackLabel, offLabel, payLabel);
  details.append(grid);
  const status = document.createElement('p');
  status.className = 'mono';
  status.hidden = true;
  details.append(status);
  const anchor = document.querySelector('.pfl-seat-stacks') || els.stack.closest('.pfl-grid2');
  anchor?.after(details);

  function render() {
    onBox.checked = state.on;
    stage.value = state.stage || '';
    stageNote.textContent = state.stage ? (state.edited ? 'edited' : 'preset') : '';
    payouts.value = state.payouts;
    fieldCount.value = state.fieldCount;
    fieldStack.value = state.fieldStack;
    stackOff.value = state.stackOff ?? '';
    fieldStack.placeholder = els.stack.value || 'Stack';
    zeroRake(state.on);
    grid.hidden = !state.on;
    summary.textContent = state.on ? 'Tournament payouts (ICM on)' : 'Tournament payouts (ICM)';
    if (state.on) details.open = true;
  }
  // ICM solves need rake 0, so the fields are driven to 0 and disabled, marked
  // "ICM · 0". The numbers the user entered are kept in `state`, so turning ICM
  // off (now, or after loading another scenario) gives them back.
  let holdingRake = false;
  const rakeFields = () => [els.rakePct, els.rakeCap].filter(Boolean);
  function releaseRake() {
    holdingRake = false;
    for (const el of rakeFields()) {
      el.disabled = false;
      el.closest('label')?.querySelector('.icm-rake')?.remove();
    }
  }
  function zeroRake(on) {
    if (on) {
      if (!holdingRake) {
        // whatever the fields hold now is the user's own rake
        state.rakePct = els.rakePct?.value ?? '';
        state.rakeCap = els.rakeCap?.value ?? '';
        holdingRake = true;
      }
      for (const el of rakeFields()) {
        el.value = '0';
        el.disabled = true;
        if (!el.closest('label')?.querySelector('.icm-rake')) {
          const tag = document.createElement('span');
          tag.className = 'dim icm-rake';
          tag.textContent = 'ICM · 0';
          el.closest('label')?.append(' ', tag);
        }
      }
    } else if (holdingRake) {
      holdingRake = false;
      for (const [el, saved] of [[els.rakePct, state.rakePct], [els.rakeCap, state.rakeCap]]) {
        if (!el) continue;
        el.value = saved ?? '';
        el.disabled = false;
        el.closest('label')?.querySelector('.icm-rake')?.remove();
      }
    }
  }
  function applyStage(id) {
    const s = ICM_STAGES.find(x => x.id === id);
    if (!s) return;
    const table = positionsFor(+els.players.value).length;
    const all = standardPayouts(1000, 0.15);
    state.payouts = all.slice(0, Math.min(s.left, all.length)).join(', ');
    state.fieldCount = String(Math.max(0, s.left - table));
    state.fieldStack = '';
  }
  const edit = fn => () => { fn(); render(); changed(); };
  const presetEdited = () => { state.edited = true; };
  onBox.addEventListener('change', edit(() => {
    state.on = onBox.checked;
    if (state.on && !state.payouts) { state.stage = 'ft'; applyStage('ft'); }
  }));
  stage.addEventListener('change', edit(() => {
    state.stage = stage.value;
    state.edited = false;
    applyStage(stage.value);
  }));
  payouts.addEventListener('input', () => { state.payouts = payouts.value; presetEdited(); changed(); });
  fieldCount.addEventListener('input', () => { state.fieldCount = fieldCount.value; presetEdited(); changed(); });
  fieldStack.addEventListener('input', () => { state.fieldStack = fieldStack.value; changed(); });
  stackOff.addEventListener('input', () => { state.stackOff = stackOff.value; presetEdited(); changed(); });
  els.players.addEventListener('change', () => {
    if (state.stage && !state.edited) { applyStage(state.stage); render(); }
  });
  els.stack.addEventListener('input', () => { fieldStack.placeholder = els.stack.value || 'Stack'; });
  render();
  return {
    config: () => {
      const icm = icmConfig(state, +els.stack.value || 100);
      return icm ? { icm } : {};
    },
    scenario: () => (state.on ? icmScenario(state, state.rakePct, state.rakeCap) : {}),
    restore: value => {
      state = value?.icm ? { ...value.icm, edited: !!value.icm.edited, rakePct: '', rakeCap: '' } : { ...state, on: false };
      // a scenario stores the rake the user entered, never ICM's displayed 0
      if (value?.icm) {
        if (els.rakePct) els.rakePct.value = String(value.rakePct ?? els.rakePct.value ?? '');
        if (els.rakeCap) els.rakeCap.value = String(value.rakeCap ?? els.rakeCap.value ?? '');
      }
      releaseRake(); // the fields now hold this scenario's own numbers
      render();
    },
    load: cfg => {
      state = icmFromConfig(cfg);
      // a saved game keeps the rake it was solved with (0 under ICM)
      if (els.rakePct) els.rakePct.value = String(cfg.rake_pct ?? 0);
      if (els.rakeCap) els.rakeCap.value = String(cfg.rake_cap ?? 0);
      releaseRake();
      render();
    },
    /** Show what the built game's values mean (the build response's `icm`). */
    showSummary: info => {
      status.hidden = !info;
      if (!info) return;
      const pool = info.seat_equity.reduce((a, b) => a + b, 0)
        + (info.field || []).reduce((a, [, count, eq]) => a + count * eq, 0);
      const pct = pool > 0 ? 100 / (info.bb_per_prize * pool) : 0;
      const eqs = info.seat_equity.map(e => (100 * e / pool).toFixed(2) + '%').join(' · ');
      status.textContent = `1 bb ≈ ${pct.toPrecision(3)}% of the prize pool · seat equity ${eqs}`;
    },
  };
}
