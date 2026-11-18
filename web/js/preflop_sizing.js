const parse = text => {
  if (!String(text ?? '').trim()) return [];
  const values = String(text).split(',').map(x => Number(x.trim()));
  if (values.some(x => !Number.isFinite(x) || x <= 0)) throw new Error('Sizes must be positive numbers separated by commas.');
  return [...new Set(values)].sort((a,b) => a-b);
};

// Sizes that follow the action so far. `by` holds the form's values:
// limps (limps allowed), limperExtra (bb added to an open per limper),
// callerMoney (re-raises add what the callers put in), multOop / laterOop
// (3-bet and 4-bet+ multipliers out of position; empty = as in position).
// A setting left off is left out of the config, which keeps the game, and
// its save, exactly what it was before these settings existed.
export function situationalConfig(by = {}, later = '', defaultMult = '') {
  const out = {};
  const extra = Number(String(by.limperExtra ?? '').trim() || 0);
  if (!Number.isFinite(extra) || extra < 0) throw new Error('The extra per limper must be a number of big blinds, 0 or more.');
  if (by.limps && extra > 0) out.limper_extra = extra;
  if (by.callerMoney) out.caller_extra = 1;
  const threeOop = parse(by.multOop);
  if (threeOop.length) out.raise_mults_oop = threeOop;
  // An empty 4-bet box uses the 3-bet number, so out of position an empty
  // one uses the out-of-position 3-bet number.
  const laterOop = parse(String(by.laterOop ?? '').trim() || (String(later).trim() ? '' : by.multOop));
  if (laterOop.length) out.fourbet_mults_oop = laterOop;
  return out;
}

/** True when a config uses any of the action-following sizes (they need a server that knows them). */
export const usesSituationalSizes = cfg =>
  !!(cfg && (cfg.limper_extra || cfg.caller_extra || cfg.raise_mults_oop || cfg.fourbet_mults_oop));

export function sizingConfig(positions, rows, later, defaultMult, by = {}) {
  const menu = key => {
    const values = positions.map(p => parse(rows[p]?.[key]));
    return values.some(v => v.length) ? values : null;
  };
  return {
    open_raises_by_seat: menu('open'),
    raise_mults_by_seat: menu('three'),
    fourbet_mults: parse(later.trim() || defaultMult),
    fourbet_mults_by_seat: menu('later'),
    ...situationalConfig(by, later, defaultMult),
  };
}

export function sizingFromConfig(cfg) {
  const rows = {};
  cfg.positions.forEach((p,i) => {
    rows[p] = {
      open: (cfg.open_raises_by_seat?.[i] || []).join(','),
      three: (cfg.raise_mults_by_seat?.[i] || []).join(','),
      // Older seat overrides applied to every re-raise. Preserve that tree.
      later: (cfg.fourbet_mults_by_seat?.[i]?.length ? cfg.fourbet_mults_by_seat[i]
        : cfg.fourbet_mults == null ? cfg.raise_mults_by_seat?.[i] || [] : []).join(','),
    };
  });
  return {
    rows, later: (cfg.fourbet_mults || cfg.raise_mults || []).join(','),
    limperExtra: cfg.limper_extra ? String(cfg.limper_extra) : '',
    callerMoney: !!cfg.caller_extra,
    multOop: (cfg.raise_mults_oop || []).join(','),
    laterOop: (cfg.fourbet_mults_oop || []).join(','),
  };
}

export function createPositionSizing(els, positionsFor, changed) {
  let rows = {};
  const label = document.createElement('label');
  label.textContent = '4-bet+ ×prev ';
  // the box is narrow: a short placeholder, the full story in the tooltip
  label.dataset.tip = 'A 4-bet or later raise is this many times the raise it faces. Separate several sizes with commas. Leave empty to use the 3-bet number.';
  const later = document.createElement('input');
  later.type = 'text'; later.placeholder = 'as 3-bet'; later.setAttribute('aria-label','4-bet and later multipliers; empty uses the 3-bet multiplier');
  label.append(later);
  els.mult.setAttribute('aria-label','Default 3-bet multipliers');
  // Sizes that follow the action. Each box sits beside the size it changes.
  const box = (text, tip, aria) => {
    const wrap = document.createElement('label'), input = document.createElement('input');
    wrap.textContent = text + ' '; wrap.dataset.tip = tip;
    input.type = 'text'; input.setAttribute('aria-label', aria); wrap.append(input);
    return [wrap, input];
  };
  const [limperLabel, limper] = box('+ per limper (bb)',
    'Added to the open size for each limper already in. With 1, an open of 3 becomes 5 over two limpers. Leave empty to raise the same size over limpers.',
    'Big blinds added to an open for each limper; empty adds nothing');
  const OOP_TIP = 'Out of position means acting before the raiser on the flop, like the blinds against the button. Players usually raise bigger there. Leave empty to use the same size in and out of position.';
  const [multOopLabel, multOop] = box('out of position', 'The 3-bet size out of position. ' + OOP_TIP,
    '3-bet multipliers out of position; empty uses the in-position ones');
  const [laterOopLabel, laterOop] = box('out of position', 'The size of 4-bets and later raises out of position. ' + OOP_TIP,
    '4-bet and later multipliers out of position; empty uses the in-position ones');
  const callersLabel = document.createElement('label'); callersLabel.className = 'chk pfl-callers-money';
  callersLabel.dataset.tip = 'A 3-bet over callers adds what they put in. 3 times an open of 3 is 9; with two callers it becomes 9 + 3 + 3 = 15. A 4-bet over callers of the 3-bet does the same. Limpers are not callers: they have their own box.';
  const callers = document.createElement('input'); callers.type = 'checkbox';
  callersLabel.append(callers, ' re-raises add the callers\u2019 money');
  els.opens.closest('label').after(limperLabel);
  els.mult.closest('label').after(multOopLabel, label, laterOopLabel, callersLabel);
  const by = () => ({limps: !!els.limp?.checked, limperExtra: limper.value, callerMoney: callers.checked, multOop: multOop.value, laterOop: laterOop.value});
  const details = document.createElement('details'); details.className = 'pfl-position-sizes';
  const summary = document.createElement('summary'); summary.textContent = 'Sizes by seat'; details.append(summary);
  const note = document.createElement('p');
  note.textContent = 'Type in a box to give that seat its own sizes, for example 4 or 4,6. They replace the main setting for that seat, in and out of position. An empty box uses the main setting, shown in grey.';
  details.append(note);
  const table = document.createElement('table');
  table.innerHTML = '<thead><tr><th>Seat</th>'
    + '<th tabindex="0" data-tip="What this seat raises to when it is the first to raise, in big blinds. Over limpers the extra per limper is added to it.">Open · bb</th>'
    + '<th tabindex="0" data-tip="This seat\u2019s 3-bet, as a multiple of the raise it faces: 4 against a raise to 6 bb makes it 24 bb. Used in and out of position; callers\u2019 money is still added when that is ticked.">3-bet · ×prev</th>'
    + '<th tabindex="0" data-tip="This seat\u2019s 4-bets and later raises, as a multiple of the raise it faces.">4-bet+ · ×prev</th></tr></thead><tbody></tbody>';
  details.append(table);
  const rebuild = document.createElement('p'); rebuild.textContent = 'Build and solve again for new sizes to count.'; details.append(rebuild);
  els.mult.closest('.pfl-grid2').after(details);
  // An empty box shows, in grey, the main setting that seat will use.
  // With an out-of-position size set, the grey text shows both: "3 / 4".
  const mainSizes = () => {
    const three = els.mult.value.trim(), threeOop = multOop.value.trim() || three;
    const four = later.value.trim() || three, fourOop = laterOop.value.trim() || (later.value.trim() ? four : threeOop);
    const pair = (inPos, out) => !inPos ? 'none' : out === inPos ? inPos : `${inPos} / ${out}`;
    return {open: els.opens.value.trim() || 'none', three: pair(three, threeOop), later: pair(four, fourOop), threeOop, fourOop};
  };
  function placeholders() {
    const main = mainSizes();
    table.querySelectorAll('input').forEach(input => { input.placeholder = main[input.dataset.size]; });
    // an empty out-of-position box shows, in grey, the size it will use
    multOop.placeholder = main.threeOop || 'same'; laterOop.placeholder = main.fourOop || 'same';
    limper.placeholder = '0';
    // no limps, no limpers: the box has nothing to change
    limper.disabled = !els.limp?.checked;
    limperLabel.classList.toggle('pfl-off', limper.disabled);
  }
  function render() {
    const body = table.querySelector('tbody'); body.replaceChildren();
    for (const p of positionsFor(+els.players.value)) {
      const tr = document.createElement('tr'); const title = document.createElement('th'); title.textContent = p; tr.append(title);
      for (const [key,name] of [['open','open sizes in bb'],['three','3-bet multipliers'],['later','4-bet and later multipliers']]) {
        const td=document.createElement('td'), input=document.createElement('input');
        input.type='text'; input.value=rows[p]?.[key] || ''; input.dataset.size=key; input.setAttribute('aria-label',`${p} ${name}; empty uses the main setting`);
        input.addEventListener('input',()=>{(rows[p]??={})[key]=input.value; changed();}); td.append(input); tr.append(td);
      }
      body.append(tr);
    }
    placeholders();
  }
  for (const el of [later, limper, multOop, laterOop]) el.addEventListener('input',changed);
  callers.addEventListener('change',changed);
  els.players.addEventListener('change',render); render();
  for (const el of [els.opens, els.mult, later, multOop, laterOop]) el.addEventListener('input', placeholders);
  els.limp?.addEventListener('change', placeholders);
  const setBy = value => {
    limper.value = value?.limperExtra ?? ''; callers.checked = !!value?.callerMoney;
    multOop.value = value?.multOop ?? ''; laterOop.value = value?.laterOop ?? '';
  };
  details.addEventListener('toggle', placeholders);
  return {
    // the form is read after every change, so the grey defaults follow a loaded scenario too
    config: () => { placeholders(); return sizingConfig(positionsFor(+els.players.value), rows, later.value, els.mult.value, by()); },
    scenario: () => ({positionSizes: JSON.parse(JSON.stringify(rows)), laterMult: later.value.trim(),
      limperExtra: limper.value.trim(), callerMoney: callers.checked, multOop: multOop.value.trim(), laterOop: laterOop.value.trim()}),
    // a scenario saved before these settings existed has none of them: all off
    restore: value => { rows=JSON.parse(JSON.stringify(value?.positionSizes || value?.rows || {})); later.value=value?.laterMult ?? value?.later ?? ''; setBy(value); render(); },
    load: cfg => {const value=sizingFromConfig(cfg); rows=value.rows; later.value=value.later; setBy(value); render();},
  };
}
