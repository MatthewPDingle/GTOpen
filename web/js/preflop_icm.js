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
  return { payouts, ...(count > 0 ? { field_groups: [{ stack, count }] } : {}) };
}

/** Panel fields from a saved config's `icm`. */
export function icmFromConfig(cfg) {
  const icm = cfg.icm;
  if (!icm) return { on: false, payouts: '', fieldCount: '', fieldStack: '', stage: '' };
  const groups = [...(icm.field_groups || []), ...(icm.field || []).map(stack => ({ stack, count: 1 }))];
  const count = groups.reduce((a, g) => a + g.count, 0);
  const avg = count ? groups.reduce((a, g) => a + g.stack * g.count, 0) / count : '';
  return {
    on: true, payouts: icm.payouts.join(', '), stage: '',
    fieldCount: count ? String(count) : '', fieldStack: count ? String(+avg.toFixed(3)) : '',
  };
}

export function createIcmControls(els, positionsFor, changed) {
  let state = { on: false, payouts: '', fieldCount: '', fieldStack: '', stage: '' };
  const details = document.createElement('details');
  details.className = 'pfl-position-sizes pfl-icm';
  const summary = document.createElement('summary');
  details.append(summary);
  const note = document.createElement('p');
  note.textContent = 'Tournament spots: every pot pays the change in each player’s share of the prize pool '
    + '(Malmuth–Harville ICM) instead of chips. EVs read in bb equivalents. Stage presets use an '
    + 'approximate standard 1,000-player payout structure and give everyone at other tables the table stack, '
    + 'like the Range Lab ICM charts. Needs rake 0.';
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
  const stageLabel = document.createElement('label');
  stageLabel.append('Stage ', stage);
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
  grid.append(stageLabel, countLabel, stackLabel, payLabel);
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
    payouts.value = state.payouts;
    fieldCount.value = state.fieldCount;
    fieldStack.value = state.fieldStack;
    fieldStack.placeholder = els.stack.value || 'Stack';
    grid.hidden = !state.on;
    summary.textContent = state.on ? 'Tournament payouts (ICM on)' : 'Tournament payouts (ICM)';
    if (state.on) details.open = true;
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
  onBox.addEventListener('change', edit(() => {
    state.on = onBox.checked;
    if (state.on && !state.payouts) { state.stage = 'ft'; applyStage('ft'); }
    if (state.on && els.rakePct && +els.rakePct.value) els.rakePct.value = 0;
  }));
  stage.addEventListener('change', edit(() => { state.stage = stage.value; applyStage(stage.value); }));
  payouts.addEventListener('input', () => { state.payouts = payouts.value; state.stage = ''; stage.value = ''; changed(); });
  fieldCount.addEventListener('input', () => { state.fieldCount = fieldCount.value; state.stage = ''; stage.value = ''; changed(); });
  fieldStack.addEventListener('input', () => { state.fieldStack = fieldStack.value; changed(); });
  els.players.addEventListener('change', () => { if (state.stage) { applyStage(state.stage); render(); } });
  els.stack.addEventListener('input', () => { fieldStack.placeholder = els.stack.value || 'Stack'; });
  render();
  return {
    config: () => {
      const icm = icmConfig(state, +els.stack.value || 100);
      return icm ? { icm } : {};
    },
    scenario: () => (state.on ? { icm: { ...state } } : {}),
    restore: value => { state = value?.icm ? { ...value.icm } : { ...state, on: false }; render(); },
    load: cfg => { state = icmFromConfig(cfg); render(); },
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
