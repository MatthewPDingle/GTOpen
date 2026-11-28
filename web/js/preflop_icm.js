// Tournament (ICM) payouts for the Preflop Lab. With ICM on, every terminal
// pays the change in Malmuth–Harville prize equity, in bb equivalents.

import { holdRakeBoxes, releaseRakeBoxes } from './icm_rake.js';

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
  // Simple by default. The on/off box is part of the scenario form itself,
  // right under the rake boxes it switches off, so whether a game uses
  // tournament payouts shows without opening anything. Turning it on adds the
  // stage. Everything a stage fills in (other tables, stack-off rate, the
  // payout list) and the read-out of a built game sit under an "Advanced"
  // opener, closed until the user opens it or picks the Custom stage, which
  // needs them.
  const details = document.createElement('div');
  details.className = 'pfl-icm';
  const onRow = document.createElement('div');
  onRow.className = 'pfl-icm-on';
  const on = document.createElement('label');
  on.className = 'chk';
  const onBox = document.createElement('input');
  onBox.type = 'checkbox';
  on.append(onBox, ' tournament payouts (ICM)');
  const about = document.createElement('button');
  about.type = 'button';
  about.className = 'info-dot';
  about.textContent = '?';
  about.setAttribute('aria-label', 'About tournament payouts');
  about.setAttribute('data-tip-click', '');
  about.dataset.tip = 'Hands are valued in prize money instead of chips (ICM), so busting costs more than '
    + 'doubling up wins. Results still read in big blinds, and there is no rake. Pick how far along the '
    + 'tournament is under Stage.';
  onRow.append(on, about);
  details.append(onRow);
  const stage = document.createElement('select');
  stage.innerHTML = '<option value="">Custom</option>'
    + ICM_STAGES.map(s => `<option value="${s.id}">${s.label}</option>`).join('');
  const stageLabel = document.createElement('label');
  stageLabel.className = 'pfl-icm-stage';
  stageLabel.dataset.tip = 'How far along the tournament is. Each stage uses the payouts of a typical '
    + '1,000-player tournament. Custom lets you type your own under Advanced tournament settings.';
  stageLabel.append('Stage ', stage);
  details.append(stageLabel);
  const advanced = document.createElement('details');
  advanced.className = 'pfl-position-sizes pfl-icm-adv';
  const advSummary = document.createElement('summary');
  advSummary.dataset.tip = 'The numbers behind the stage: players at other tables, how often flops end all-in, '
    + 'and the payout list. Change them here if your tournament differs.';
  advanced.append(advSummary);
  const payouts = document.createElement('textarea');
  payouts.rows = 3;
  payouts.placeholder = 'e.g. 50, 30, 20';
  payouts.setAttribute('aria-label', 'Prize for each place, first place first');
  const payLabel = document.createElement('label');
  payLabel.className = 'pfl-icm-pay';
  payLabel.dataset.tip = 'The prize for each place still to be paid, first place first. Any unit works: '
    + 'only the proportions matter.';
  payLabel.append('Payouts, first place first ', payouts);
  const fieldCount = document.createElement('input');
  fieldCount.type = 'number'; fieldCount.min = '0'; fieldCount.step = '1';
  const countLabel = document.createElement('label');
  countLabel.dataset.tip = 'How many players are still in at the other tables.';
  countLabel.append('Players at other tables ', fieldCount);
  const fieldStack = document.createElement('input');
  fieldStack.type = 'number'; fieldStack.min = '0.5'; fieldStack.step = '0.5';
  const stackLabel = document.createElement('label');
  stackLabel.dataset.tip = 'The average stack at the other tables. Leave empty to use this table’s stack.';
  stackLabel.append('Their stack (bb) ', fieldStack);
  const stackOff = document.createElement('input');
  stackOff.type = 'number'; stackOff.min = '0'; stackOff.step = '0.25'; stackOff.placeholder = '0.4';
  const offLabel = document.createElement('label');
  offLabel.dataset.tip = 'How often a pot that sees the flop ends up all-in, which happens more when stacks are short '
    + 'next to the pot. Leave empty for the usual 0.4. At 0 only the pot is at risk.';
  offLabel.append('Stack-off rate ', stackOff);
  const status = document.createElement('p');
  status.className = 'mono';
  status.hidden = true;
  advanced.append(countLabel, stackLabel, offLabel, payLabel, status);
  details.append(advanced);
  els.stack.closest('.pfl-grid2')?.after(details);

  // a stage whose numbers were changed says so, even with the opener closed
  function renderEdited() {
    advSummary.textContent = state.stage && state.edited
      ? 'Advanced tournament settings · edited' : 'Advanced tournament settings';
  }
  function render() {
    onBox.checked = state.on;
    stage.value = state.stage || '';
    renderEdited();
    payouts.value = state.payouts;
    fieldCount.value = state.fieldCount;
    fieldStack.value = state.fieldStack;
    stackOff.value = state.stackOff ?? '';
    fieldStack.placeholder = els.stack.value || 'Stack';
    zeroRake(state.on);
    stageLabel.hidden = !state.on;
    advanced.hidden = !state.on;
  }
  // ICM solves need rake 0, so the fields are driven to 0 and greyed out
  // (icm_rake.js says why in a tooltip). The numbers the user entered are kept
  // in `state`, so turning ICM off (now, or after loading another scenario)
  // gives them back.
  let holdingRake = false;
  const rakeFields = () => [els.rakePct, els.rakeCap].filter(Boolean);
  // The rake type has no number to zero, so it is held and released with the
  // amounts but never overwritten.
  const heldRakeFields = () => [...rakeFields(), els.rakeType].filter(Boolean);
  function releaseRake() {
    holdingRake = false;
    releaseRakeBoxes(heldRakeFields());
  }
  function zeroRake(on) {
    if (on) {
      if (!holdingRake) {
        // whatever the fields hold now is the user's own rake
        state.rakePct = els.rakePct?.value ?? '';
        state.rakeCap = els.rakeCap?.value ?? '';
        holdingRake = true;
      }
      for (const el of rakeFields()) el.value = '0';
      holdRakeBoxes(heldRakeFields());
    } else if (holdingRake) {
      holdingRake = false;
      for (const [el, saved] of [[els.rakePct, state.rakePct], [els.rakeCap, state.rakeCap]]) {
        if (el) el.value = saved ?? '';
      }
      releaseRakeBoxes(heldRakeFields());
    }
  }
  // Custom has no preset behind it, so its numbers must be in view.
  const showCustom = () => { if (state.on && !state.stage) advanced.open = true; };
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
  const presetEdited = () => { state.edited = true; renderEdited(); };
  onBox.addEventListener('change', edit(() => {
    state.on = onBox.checked;
    if (state.on && !state.payouts) { state.stage = 'ft'; applyStage('ft'); }
    showCustom();
  }));
  stage.addEventListener('change', edit(() => {
    state.stage = stage.value;
    state.edited = false;
    applyStage(stage.value);
    showCustom();
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
      showCustom();
      render();
    },
    load: cfg => {
      state = icmFromConfig(cfg);
      // a saved game keeps the rake it was solved with (0 under ICM)
      if (els.rakePct) els.rakePct.value = String(cfg.rake_pct ?? 0);
      if (els.rakeCap) els.rakeCap.value = String(cfg.rake_cap ?? 0);
      releaseRake();
      showCustom();
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
      status.textContent = `In the built game 1 bb is worth about ${pct.toPrecision(3)}% of the prize pool. `
        + `Each seat’s share of the prize pool: ${eqs}`;
    },
  };
}
