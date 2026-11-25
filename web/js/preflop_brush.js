// The brush of the player-model range editor (Preflop Lab, "The ranges this
// player plays"). A brush is a mix: how often a painted hand calls, raises and
// goes all-in, in whole percent. Whatever is left folds, or checks where
// checking is free. A click or drag gives each hand exactly this mix.
//
// The profile already stores a hand that way (`call`, `raise` and `jam` per
// hand class, fold is the remainder), so the brush changes nothing in the file
// format or the engine.

export const BRUSH_ACTIONS = ['call', 'raise', 'jam'];
/** The order a grid cell draws its bars in, left to right. */
export const DRAW_ORDER = ['raise', 'jam', 'call', 'fold'];

const pct = value => {
  const v = Math.round(Number(value));
  return Number.isFinite(v) ? Math.max(0, Math.min(100, v)) : 0;
};

/** A brush that does one thing every time: "fold", "call", "raise" or "jam". */
export function pureBrush(action) {
  const brush = { call: 0, raise: 0, jam: 0, recent: [] };
  if (BRUSH_ACTIONS.includes(action)) { brush[action] = 100; brush.recent = [action]; }
  return brush;
}

/** Sets one action's share. The number just typed stays: when the three add
 *  up to more than 100, the other two give way, the one changed longest ago
 *  first. Room that is left over is the fold share. */
export function setShare(brush, action, value) {
  if (!BRUSH_ACTIONS.includes(action)) return brush;
  const next = { call: pct(brush.call), raise: pct(brush.raise), jam: pct(brush.jam) };
  next[action] = pct(value);
  const recent = (brush.recent || []).filter(a => a !== action && BRUSH_ACTIONS.includes(a));
  let excess = next.call + next.raise + next.jam - 100;
  const others = BRUSH_ACTIONS.filter(a => a !== action)
    .sort((a, b) => recent.indexOf(a) - recent.indexOf(b));
  for (const other of others) {
    if (excess <= 0) break;
    const cut = Math.min(next[other], excess);
    next[other] -= cut;
    excess -= cut;
  }
  return { ...next, recent: [...recent, action] };
}

/** What the brush paints, as shares of 1. Where checking is free nothing
 *  folds: the remainder checks (it is stored as the call share). */
export function brushParts(brush, freeCheck = false) {
  const raise = pct(brush.raise) / 100, jam = pct(brush.jam) / 100;
  let call = pct(brush.call) / 100;
  const over = raise + jam + call;
  if (over > 1) call = Math.max(0, 1 - raise - jam);
  const rest = Math.max(0, 1 - raise - jam - call);
  return freeCheck ? { raise, jam, call: call + rest, fold: 0 } : { raise, jam, call, fold: rest };
}

/** The brush that repaints a hand as it is now (shares of 1 in, whole percent out). */
export function handBrush(call, raise, jam) {
  const raw = { call: Number(call) || 0, raise: Number(raise) || 0, jam: Number(jam) || 0 };
  const sum = raw.call + raw.raise + raw.jam;
  const scale = sum > 1 ? 1 / sum : 1; // the engine reads an over-full hand the same way
  const next = Object.fromEntries(BRUSH_ACTIONS.map(a => [a, pct(Math.max(0, raw[a]) * scale * 100)]));
  // rounding can leave 101: the biggest share gives the point back
  while (next.call + next.raise + next.jam > 100) {
    const top = BRUSH_ACTIONS.reduce((a, b) => (next[b] > next[a] ? b : a));
    next[top] -= 1;
  }
  // nothing was typed yet: the biggest share is the first to give way
  return { ...next, recent: BRUSH_ACTIONS.filter(a => next[a] > 0).sort((a, b) => next[b] - next[a]) };
}

/** "raise 40% · call 60%": the brush in words, nothing listed at 0. */
export function brushText(brush, freeCheck = false) {
  const parts = brushParts(brush, freeCheck);
  const name = action => (action === 'call' && freeCheck ? 'check' : action);
  return DRAW_ORDER.filter(a => parts[a] > 0.0005)
    .map(a => `${name(a)} ${Math.round(parts[a] * 100)}%`).join(' · ');
}

/** How many of the 1,326 starting hands a class holds. Index = hi*13+lo for
 *  suited, lo*13+hi for offsuit, rank*14 for pairs. */
export function classCombos(index) {
  const a = Math.floor(index / 13), b = index % 13;
  return a === b ? 6 : a > b ? 4 : 12;
}

/** What a whole grid adds up to: the share of all hands dealt that raises,
 *  goes all-in, calls and folds, in percent. */
export function rangeTotals(policy, freeCheck = false) {
  const totals = { raise: 0, jam: 0, call: 0, fold: 0 };
  if (!policy) return totals;
  for (let index = 0; index < 169; index++) {
    let raise = Math.max(0, policy.raise?.[index] || 0);
    let jam = Math.max(0, policy.jam?.[index] || 0);
    let call = Math.max(0, policy.call?.[index] || 0);
    const sum = raise + jam + call;
    if (sum > 1) { raise /= sum; jam /= sum; call /= sum; }
    const rest = Math.max(0, 1 - raise - jam - call);
    const weight = classCombos(index) / 1326 * 100;
    totals.raise += raise * weight;
    totals.jam += jam * weight;
    totals.call += (freeCheck ? call + rest : call) * weight;
    totals.fold += (freeCheck ? 0 : rest) * weight;
  }
  return totals;
}
