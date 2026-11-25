// Tournament (ICM) payoffs for postflop spots: a collapsible panel that turns
// the spot request's `icm` on and off, on the Postflop Setup & Solve page for
// two or three players; the Preflop Lab's flop exports fill it in.

import { holdRakeBoxes, releaseRakeBoxes } from './icm_rake.js';

const parseNums = text => String(text || '').split(/[\s,]+/).filter(Boolean);

/** The tournament payouts of a spot request as one canonical string, or null
 *  when it has none. The page sends empty lists and its own field order; the
 *  server's echo drops empty lists and orders fields its own way. Comparing
 *  the raw JSON made every tournament spot look as if SETUP had changed, so
 *  the solve button rebuilt the tree and threw the node locks away. */
export function icmFingerprint(icm) {
  if (!icm) return null;
  const num = x => Math.round(+x * 1e3) / 1e3; // the form holds three decimals
  return JSON.stringify([
    (icm.payouts || []).map(num),
    icm.behind ? icm.behind.map(num) : null,
    (icm.others || []).map(num),
    (icm.field_groups || []).map(g => [+g.count, num(g.stack)]),
  ]);
}

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
 * from the player rows. `setSeats` switches between the two. `onChange` runs
 * after every edit.
 */
export function createPostflopIcm(anchor, { seats = 2, onChange = () => {} } = {}) {
  // The on/off box always shows, so whether a spot uses tournament payouts
  // reads without opening anything; its fields appear when it is on.
  const details = document.createElement('div');
  details.className = 'postflop-icm';
  const onRow = document.createElement('div');
  onRow.className = 'postflop-icm-on';
  const on = document.createElement('label');
  on.className = 'check';
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
    + 'doubling up wins. Results still read in big blinds, stacks use the pot’s units, and there is no rake. '
    + 'A flop sent from a Preflop Lab tournament game fills this in.';
  onRow.append(on, about);
  details.append(onRow);
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
  const behindLabels = [];
  {
    for (const who of ['OOP', 'IP']) {
      const input = document.createElement('input');
      input.type = 'number'; input.min = '0'; input.step = 'any';
      input.placeholder = 'effective stack';
      const label = document.createElement('label');
      label.dataset.tip = `${who} chips behind at the start of the solve. Chips past the effective stack `
        + 'are never at risk but count for ICM.';
      label.append(`${who} chips behind `, input);
      behind.push(input);
      behindLabels.push(label);
      label.hidden = seats !== 2;
      grid.append(label);
    }
  }
  grid.append(payLabel, othersLabel);
  details.append(grid);
  anchor.after(details);
  // ICM solves need rake 0 (the server refuses otherwise), so the panel's
  // rake fields are driven to 0 and greyed out while ICM is on (icm_rake.js
  // says why in a tooltip). What they held is kept here and given back when
  // ICM goes off.
  const rakes = [...anchor.querySelectorAll('input[id*="rake"]')];
  let rakeStash = null;

  function holdRake() {
    if (rakeStash) return;
    rakeStash = rakes.map(el => ({ el, value: el.value }));
    for (const el of rakes) el.value = '0';
    holdRakeBoxes(rakes);
  }
  /** Give the fields back; `restore` puts the remembered numbers in, which is
   *  what turning ICM off means. A newly loaded spot (set) must keep the
   *  numbers it just wrote instead. */
  function releaseRake(restore) {
    if (!rakeStash) return;
    for (const { el, value } of rakeStash) {
      if (restore) el.value = value;
    }
    releaseRakeBoxes(rakes);
    rakeStash = null;
  }

  function render() {
    if (onBox.checked) holdRake();
    else releaseRake(false);
    grid.hidden = !onBox.checked;
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
      if (seats === 2 && behind.some(b => b.value.trim() !== '')) {
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
    /** 2 shows the chips-behind boxes, 3 hides them (and leaves them out). */
    setSeats(n) {
      seats = n === 3 ? 3 : 2;
      for (const l of behindLabels) l.hidden = seats !== 2;
    },
  };
}
