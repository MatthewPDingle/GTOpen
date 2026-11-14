// Tournament (ICM) payoffs for postflop spots: a collapsible panel that turns
// the spot request's `icm` on and off. Shared by SETUP (heads-up) and the
// 3-WAY tab; the Preflop Lab's flop exports fill it in.

const parseNums = text => String(text || '').split(/[\s,]+/).filter(Boolean);

/** "35, 22, 144x25" -> { others: [35, 22], field_groups: [{count: 144, stack: 25}] } */
export function parseStacks(text) {
  const others = [];
  const field_groups = [];
  for (const tok of parseNums(text)) {
    const m = tok.match(/^(\d+)\s*[x×]\s*([\d.]+)$/i);
    if (m) {
      const count = Number(m[1]), stack = Number(m[2]);
      if (!(count >= 1) || !(stack > 0)) throw new Error(`ICM: bad stack group "${tok}"`);
      field_groups.push({ count, stack });
    } else {
      const x = Number(tok);
      if (!(x > 0)) throw new Error(`ICM: other players' stacks must be positive numbers ("${tok}")`);
      others.push(x);
    }
  }
  return { others, field_groups };
}

export function formatStacks(icm) {
  const parts = (icm.others || []).map(x => String(+x.toFixed(3)));
  for (const g of icm.field_groups || []) parts.push(`${g.count}x${+g.stack.toFixed(3)}`);
  return parts.join(', ');
}

/**
 * Builds the panel after `anchor`. `seats` = 2 shows the chips-behind fields
 * (heads-up spots have one effective stack); 3-way spots take each stack
 * from the player rows. `onChange` runs after every edit.
 */
export function createPostflopIcm(anchor, { seats = 2, onChange = () => {} } = {}) {
  const details = document.createElement('details');
  details.className = 'pfl-position-sizes postflop-icm';
  const summary = document.createElement('summary');
  details.append(summary);
  const note = document.createElement('p');
  note.textContent = 'Every pot pays the change in each player’s prize-pool share (Malmuth–Harville ICM) '
    + 'instead of chips; EVs read in bb equivalents, stacks use the pot’s units. '
    + 'A Preflop Lab ICM export fills this in.';
  details.append(note);
  const on = document.createElement('label');
  on.className = 'check';
  const onBox = document.createElement('input');
  onBox.type = 'checkbox';
  on.append(onBox, ' use tournament payouts (ICM)');
  details.append(on);
  const grid = document.createElement('div');
  grid.className = 'pfl-grid2';
  const payouts = document.createElement('textarea');
  payouts.rows = 2;
  payouts.placeholder = 'e.g. 50, 30, 20';
  payouts.setAttribute('aria-label', 'Prize for each place, first place first');
  const payLabel = document.createElement('label');
  payLabel.style.gridColumn = '1 / -1';
  payLabel.append('Payouts, first place first ', payouts);
  const others = document.createElement('textarea');
  others.rows = 2;
  others.placeholder = 'e.g. 35, 22, 144x25';
  others.setAttribute('aria-label', 'Stacks of every other player still in');
  const othersLabel = document.createElement('label');
  othersLabel.style.gridColumn = '1 / -1';
  othersLabel.dataset.tip = 'Everyone still in the tournament but not in this hand: players who folded at '
    + 'this table, and players at other tables. "144x25": 144 players with 25 each.';
  othersLabel.append('Other players’ stacks ', others);
  const behind = [];
  if (seats === 2) {
    for (const who of ['OOP', 'IP']) {
      const input = document.createElement('input');
      input.type = 'number'; input.min = '0'; input.step = 'any';
      input.placeholder = 'effective stack';
      const label = document.createElement('label');
      label.dataset.tip = `${who} chips behind at the start of the solve. Chips past the effective stack `
        + 'are never at risk but count for ICM.';
      label.append(`${who} chips behind `, input);
      behind.push(input);
      grid.append(label);
    }
  }
  grid.append(payLabel, othersLabel);
  details.append(grid);
  anchor.after(details);
  // ICM solves need rake 0 (the server refuses otherwise), so the panel's
  // rake fields are driven to 0 and disabled while ICM is on. What they held
  // is kept here and given back when ICM goes off.
  const rakes = [...anchor.querySelectorAll('input[id*="rake"]')];
  let rakeStash = null;

  function holdRake() {
    if (rakeStash) return;
    rakeStash = rakes.map(el => ({ el, value: el.value }));
    for (const el of rakes) {
      el.value = '0';
      el.disabled = true;
      if (!el.closest('label')?.querySelector('.icm-rake')) {
        const tag = document.createElement('span');
        tag.className = 'dim icm-rake';
        tag.textContent = 'ICM · 0';
        el.closest('label')?.append(' ', tag);
      }
    }
  }
  /** Give the fields back; `restore` puts the remembered numbers in, which is
   *  what turning ICM off means. A newly loaded spot (set) must keep the
   *  numbers it just wrote instead. */
  function releaseRake(restore) {
    if (!rakeStash) return;
    for (const { el, value } of rakeStash) {
      if (restore) el.value = value;
      el.disabled = false;
      el.closest('label')?.querySelector('.icm-rake')?.remove();
    }
    rakeStash = null;
  }

  function render() {
    if (onBox.checked) holdRake();
    else releaseRake(false);
    grid.hidden = !onBox.checked;
    summary.textContent = onBox.checked ? 'Tournament payouts (ICM on)' : 'Tournament payouts (ICM)';
    if (onBox.checked) details.open = true;
  }
  const changed = () => { render(); onChange(); };
  onBox.addEventListener('change', () => {
    if (!onBox.checked) releaseRake(true); // the user turned ICM off
    changed();
  });
  for (const el of [payouts, others, ...behind]) el.addEventListener('input', changed);
  render();

  return {
    /** The request's `icm`, or undefined when off. Throws on bad input. */
    request() {
      if (!onBox.checked) return undefined;
      const pay = parseNums(payouts.value).map(Number);
      if (!pay.length || pay.some(p => !Number.isFinite(p) || p < 0)) {
        throw new Error('ICM payouts must be a list of non-negative prizes, first place first.');
      }
      const icm = { payouts: pay, ...parseStacks(others.value) };
      if (behind.length && behind.some(b => b.value.trim() !== '')) {
        if (behind.some(b => b.value.trim() === '')) throw new Error('ICM: give both players’ chips behind, or neither.');
        icm.behind = behind.map(b => Number(b.value));
      }
      return icm;
    },
    /** Fill from a request's or export's `icm` (falsy turns ICM off). */
    set(icm) {
      // The spot's rake (if the caller just wrote one) is the new baseline:
      // drop the previous spot's held numbers without putting them back.
      releaseRake(false);
      onBox.checked = !!icm;
      if (icm) {
        payouts.value = (icm.payouts || []).join(', ');
        others.value = formatStacks(icm);
        behind.forEach((b, i) => { b.value = icm.behind ? String(+icm.behind[i].toFixed(3)) : ''; });
      }
      render();
    },
    get on() { return onBox.checked; },
  };
}
