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
  const later = document.createElement('input');
  later.type = 'text'; later.placeholder = 'Default re-raise sizes'; later.setAttribute('aria-label','Default 4-bet and later multipliers');
  label.append(later); els.mult.closest('label').after(label);
  els.mult.setAttribute('aria-label','Default 3-bet multipliers');
  const details = document.createElement('details'); details.className = 'pfl-position-sizes';
  const summary = document.createElement('summary'); summary.textContent = 'Sizes by position'; details.append(summary);
  const note = document.createElement('p');
  note.textContent = 'Blank overrides use the defaults above. Opens are raise-to amounts in bb; re-raises multiply the previous raise-to amount. For example, 4× facing 6bb raises to 24bb. 3-bet sizes also apply to squeezes; 4-bet+ sizes apply after two or more raises.';
  details.append(note);
  const table = document.createElement('table');
  table.innerHTML = '<thead><tr><th>Seat</th><th>Open · bb</th><th>3-bet · ×prev</th><th>4-bet+ · ×prev</th></tr></thead><tbody></tbody>';
  details.append(table);
  const rebuild = document.createElement('p'); rebuild.textContent = 'Size changes take effect after Build Game and a fresh solve.'; details.append(rebuild);
  els.mult.closest('.pfl-grid2').after(details);
  function render() {
    const body = table.querySelector('tbody'); body.replaceChildren();
    for (const p of positionsFor(+els.players.value)) {
      const tr = document.createElement('tr'); const title = document.createElement('th'); title.textContent = p; tr.append(title);
      for (const [key,name] of [['open','open sizes in bb'],['three','3-bet multipliers'],['later','4-bet and later multipliers']]) {
        const td=document.createElement('td'), input=document.createElement('input');
        input.type='text'; input.value=rows[p]?.[key] || ''; input.placeholder='Default'; input.setAttribute('aria-label',`${p} ${name}`);
        input.addEventListener('input',()=>{(rows[p]??={})[key]=input.value; changed();}); td.append(input); tr.append(td);
      }
      body.append(tr);
    }
  }
  later.addEventListener('input',changed); els.players.addEventListener('change',render); render();
  return {
    config: () => sizingConfig(positionsFor(+els.players.value), rows, later.value, els.mult.value),
    scenario: () => ({positionSizes: JSON.parse(JSON.stringify(rows)), laterMult: later.value.trim()}),
    restore: value => { rows=JSON.parse(JSON.stringify(value?.positionSizes || value?.rows || {})); later.value=value?.laterMult ?? value?.later ?? ''; render(); },
    load: cfg => {const value=sizingFromConfig(cfg); rows=value.rows; later.value=value.later; render();},
  };
}
