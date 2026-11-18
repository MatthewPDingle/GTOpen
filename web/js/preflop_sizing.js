const parse = text => {
  if (!String(text ?? '').trim()) return [];
  const values = String(text).split(',').map(x => Number(x.trim()));
  if (values.some(x => !Number.isFinite(x) || x <= 0)) throw new Error('Sizes must be positive numbers separated by commas.');
  return [...new Set(values)].sort((a,b) => a-b);
};

export function sizingConfig(positions, rows, later, defaultMult) {
  const menu = key => {
    const values = positions.map(p => parse(rows[p]?.[key]));
    return values.some(v => v.length) ? values : null;
  };
  return {
    open_raises_by_seat: menu('open'),
    raise_mults_by_seat: menu('three'),
    fourbet_mults: parse(later.trim() || defaultMult),
    fourbet_mults_by_seat: menu('later'),
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
  return {rows, later: (cfg.fourbet_mults || cfg.raise_mults || []).join(',')};
}

export function createPositionSizing(els, positionsFor, changed) {
  let rows = {};
  const label = document.createElement('label');
  label.textContent = '4-bet+ ×prev ';
  // the box is narrow: a short placeholder, the full story in the tooltip
  label.dataset.tip = 'A 4-bet or later raise is this many times the raise it faces. Separate several sizes with commas. Leave empty to use the 3-bet number.';
  const later = document.createElement('input');
  later.type = 'text'; later.placeholder = 'as 3-bet'; later.setAttribute('aria-label','4-bet and later multipliers; empty uses the 3-bet multiplier');
  label.append(later); els.mult.closest('label').after(label);
  els.mult.setAttribute('aria-label','Default 3-bet multipliers');
  const details = document.createElement('details'); details.className = 'pfl-position-sizes';
  const summary = document.createElement('summary'); summary.textContent = 'Sizes by position'; details.append(summary);
  const note = document.createElement('p');
  note.textContent = 'Type in a box to give that seat its own sizes, for example 4 or 4,6. They replace the main setting for that seat. An empty box uses the main setting, shown in grey.';
  details.append(note);
  const table = document.createElement('table');
  table.innerHTML = '<thead><tr><th>Seat</th>'
    + '<th tabindex="0" data-tip="What this seat raises to when it is the first to raise, in big blinds. Also used when it raises over limpers.">Open · bb</th>'
    + '<th tabindex="0" data-tip="This seat\u2019s 3-bet, as a multiple of the raise it faces: 4 against a raise to 6 bb makes it 24 bb. Its squeezes use this too.">3-bet · ×prev</th>'
    + '<th tabindex="0" data-tip="This seat\u2019s 4-bets and later raises, as a multiple of the raise it faces.">4-bet+ · ×prev</th></tr></thead><tbody></tbody>';
  details.append(table);
  const rebuild = document.createElement('p'); rebuild.textContent = 'Build and solve again for new sizes to count.'; details.append(rebuild);
  els.mult.closest('.pfl-grid2').after(details);
  // An empty box shows, in grey, the main setting that seat will use.
  const mainSizes = () => ({
    open: els.opens.value.trim() || 'none',
    three: els.mult.value.trim() || 'none',
    later: later.value.trim() || els.mult.value.trim() || 'none',
  });
  function placeholders() {
    const main = mainSizes();
    table.querySelectorAll('input').forEach(input => { input.placeholder = main[input.dataset.size]; });
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
  later.addEventListener('input',changed); els.players.addEventListener('change',render); render();
  for (const el of [els.opens, els.mult, later]) el.addEventListener('input', placeholders);
  details.addEventListener('toggle', placeholders);
  return {
    // the form is read after every change, so the grey defaults follow a loaded scenario too
    config: () => { placeholders(); return sizingConfig(positionsFor(+els.players.value), rows, later.value, els.mult.value); },
    scenario: () => ({positionSizes: JSON.parse(JSON.stringify(rows)), laterMult: later.value.trim()}),
    restore: value => { rows=JSON.parse(JSON.stringify(value?.positionSizes || value?.rows || {})); later.value=value?.laterMult ?? value?.later ?? ''; render(); },
    load: cfg => {const value=sizingFromConfig(cfg); rows=value.rows; later.value=value.later; render();},
  };
}
