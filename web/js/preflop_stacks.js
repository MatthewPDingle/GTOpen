// Per-seat starting stacks for the Preflop Lab. Blank seats use the table
// stack; when every seat is blank (or equal) the config has no `stacks` and
// the game is the ordinary equal-stack tree.

const parseStack = text => {
  const t = String(text ?? '').trim();
  if (!t) return null;
  const v = Number(t);
  if (!Number.isFinite(v) || v <= 0) throw new Error('Seat stacks must be positive bb amounts.');
  return v;
};

/** {stack, stacks?} for the engine from the table stack and per-seat text. */
export function stacksConfig(positions, rows, tableStack) {
  const stacks = positions.map(p => parseStack(rows[p]) ?? tableStack);
  if (stacks.every(s => s === stacks[0])) return { stack: stacks[0] };
  return { stack: Math.max(...stacks), stacks };
}

/** Per-seat text rows from a saved config (empty when stacks are equal). */
export function stacksFromConfig(cfg) {
  const rows = {};
  if (cfg.stacks) cfg.positions.forEach((p, i) => { rows[p] = String(cfg.stacks[i]); });
  return rows;
}

export function createSeatStacks(els, positionsFor, changed) {
  let rows = {};
  const details = document.createElement('details');
  details.className = 'pfl-position-sizes pfl-seat-stacks';
  const summary = document.createElement('summary');
  summary.textContent = 'Stacks by seat';
  details.append(summary);
  const note = document.createElement('p');
  note.textContent = 'Starting stacks in bb, before antes. Blank seats use the Stack above. '
    + 'Short stacks call or shove all-in for less; extra chips are returned uncalled, and '
    + 'all-ins for different amounts make side pots, each won by the best hand among the seats in it.';
  details.append(note);
  const table = document.createElement('table');
  table.innerHTML = '<thead><tr><th>Seat</th><th>Stack · bb</th></tr></thead><tbody></tbody>';
  details.append(table);
  els.stack.closest('.pfl-grid2')?.after(details);
  function render() {
    const body = table.querySelector('tbody');
    body.replaceChildren();
    for (const p of positionsFor(+els.players.value)) {
      const tr = document.createElement('tr');
      const th = document.createElement('th');
      th.textContent = p;
      const td = document.createElement('td');
      const input = document.createElement('input');
      input.type = 'number'; input.min = '0.5'; input.step = '0.5';
      input.value = rows[p] || ''; input.placeholder = els.stack.value || 'Stack';
      input.setAttribute('aria-label', `${p} starting stack in bb`);
      input.addEventListener('input', () => { rows[p] = input.value; changed(); });
      td.append(input); tr.append(th, td); body.append(tr);
    }
    const custom = Object.values(rows).some(v => String(v ?? '').trim());
    summary.textContent = custom ? 'Stacks by seat (custom)' : 'Stacks by seat';
    if (custom) details.open = true;
  }
  els.players.addEventListener('change', render);
  els.stack.addEventListener('input', () => {
    table.querySelectorAll('input').forEach(i => { i.placeholder = els.stack.value || 'Stack'; });
  });
  render();
  return {
    config: () => stacksConfig(positionsFor(+els.players.value), rows, +els.stack.value || 100),
    scenario: () => ({ seatStacks: JSON.parse(JSON.stringify(rows)) }),
    restore: value => { rows = JSON.parse(JSON.stringify(value?.seatStacks || {})); render(); },
    load: cfg => { rows = stacksFromConfig(cfg); render(); },
  };
}
