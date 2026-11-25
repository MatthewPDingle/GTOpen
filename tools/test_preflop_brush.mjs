import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { BRUSH_ACTIONS, pureBrush, setShare, brushParts, handBrush, brushText, classCombos, rangeTotals } from '../web/js/preflop_brush.js';

const shares = brush => [brush.call, brush.raise, brush.jam];

// A name on its own is the old brush: one action, every time.
assert.deepEqual(shares(pureBrush('call')), [100, 0, 0]);
assert.deepEqual(shares(pureBrush('raise')), [0, 100, 0]);
assert.deepEqual(shares(pureBrush('jam')), [0, 0, 100]);
assert.deepEqual(shares(pureBrush('fold')), [0, 0, 0]);
assert.deepEqual(brushParts(pureBrush('fold')), { raise: 0, jam: 0, call: 0, fold: 1 });

// The mix the editor could not paint before: call 60%, raise 40%. One number
// is enough, the call share gives way.
let brush = setShare(pureBrush('call'), 'raise', 40);
assert.deepEqual(shares(brush), [60, 40, 0]);
assert.deepEqual(brushParts(brush), { raise: 0.4, jam: 0, call: 0.6, fold: 0 });
assert.equal(brushText(brush), 'raise 40% · call 60%');

// The number just typed stays. The share changed longest ago gives way first.
brush = setShare(brush, 'jam', 10);
assert.deepEqual(shares(brush), [50, 40, 10]);
brush = setShare(brush, 'call', 70);
assert.deepEqual(shares(brush), [70, 20, 10], 'raise was changed before jam, so raise gives way');
brush = setShare(brush, 'jam', 100);
assert.deepEqual(shares(brush), [0, 0, 100]);

// Lowering a share leaves the room to fold, never to another action.
brush = setShare(setShare(pureBrush('call'), 'raise', 40), 'call', 25);
assert.deepEqual(shares(brush), [25, 40, 0]);
assert.equal(brushParts(brush).fold, 0.35);
assert.equal(brushText(brush), 'raise 40% · call 25% · fold 35%');

// What is typed is read as a whole percent from 0 to 100.
assert.deepEqual(shares(setShare(pureBrush('fold'), 'raise', '12.6')), [0, 13, 0]);
assert.deepEqual(shares(setShare(pureBrush('fold'), 'raise', 400)), [0, 100, 0]);
assert.deepEqual(shares(setShare(pureBrush('call'), 'raise', -5)), [100, 0, 0]);
assert.deepEqual(shares(setShare(pureBrush('call'), 'raise', 'x')), [100, 0, 0]);
assert.deepEqual(shares(setShare(pureBrush('call'), 'fold', 50)), [100, 0, 0], 'fold is the remainder, not a share to set');

// Typing "100" into the raise box passes through 1 and 10. The editor applies
// each keystroke to the brush as it was before typing, so the steps on the
// way do not matter: the result is the same as setting 100 at once.
const before = setShare(pureBrush('call'), 'jam', 30);
for (const typed of ['1', '10', '100', '10', '40']) {
  const step = setShare(before, 'raise', typed);
  assert.equal(step.call + step.raise + step.jam <= 100, true);
}
assert.deepEqual(shares(setShare(before, 'raise', '40')), [30, 40, 30]);

// Where checking is free nothing folds: the remainder checks.
const free = brushParts(setShare(pureBrush('fold'), 'raise', 30), true);
assert.equal(free.fold, 0);
assert.equal(free.call, 0.7);
assert.equal(free.raise, 0.3);
assert.equal(brushText(setShare(pureBrush('fold'), 'raise', 30), true), 'raise 30% · check 70%');
assert.equal(brushText(pureBrush('fold'), true), 'check 100%');

// Every brush paints shares that add up to 1 with the fold share.
for (const call of [0, 15, 60, 100]) for (const raise of [0, 40, 85]) for (const jam of [0, 5, 100]) {
  const made = setShare(setShare(setShare(pureBrush('fold'), 'call', call), 'raise', raise), 'jam', jam);
  for (const freeCheck of [false, true]) {
    const parts = brushParts(made, freeCheck);
    assert.ok(Math.abs(parts.call + parts.raise + parts.jam + parts.fold - 1) < 1e-9);
    assert.ok(BRUSH_ACTIONS.every(a => parts[a] >= 0 && parts[a] <= 1));
  }
}

// Picking a hand up gives the brush that paints it back.
assert.deepEqual(shares(handBrush(0.6, 0.4, 0)), [60, 40, 0]);
assert.deepEqual(shares(handBrush(0, 0, 0)), [0, 0, 0]);
// rounding up twice would make 101: the biggest share gives the point back
assert.deepEqual(shares(handBrush(0.335, 0.335, 0.33)), [33, 34, 33]);
const thirds = handBrush(0.335, 0.335, 0.335);
assert.ok(thirds.call + thirds.raise + thirds.jam <= 100);
// a hand stored over-full is read the way the engine reads it, scaled to 1
assert.deepEqual(shares(handBrush(1, 1, 0)), [50, 50, 0]);
// and the picked-up brush can be mixed further
assert.deepEqual(shares(setShare(handBrush(0.6, 0.4, 0), 'jam', 20)), [40, 40, 20]);

// Totals under the grid: the share of all 1,326 hands, pairs 6, suited 4, offsuit 12.
assert.equal(classCombos(12 * 14), 6);        // AA
assert.equal(classCombos(12 * 13 + 11), 4);   // AKs: hi*13+lo
assert.equal(classCombos(11 * 13 + 12), 12);  // AKo: lo*13+hi
let combos = 0;
for (let index = 0; index < 169; index++) combos += classCombos(index);
assert.equal(combos, 1326);
const policy = { call: new Array(169).fill(0), raise: new Array(169).fill(0), jam: new Array(169).fill(0) };
assert.ok(Math.abs(rangeTotals(policy).fold - 100) < 1e-9);
assert.equal(rangeTotals(policy).raise, 0);
policy.raise[12 * 14] = 1;            // AA always raises
policy.call[12 * 13 + 11] = 0.6;      // AKs: call 60, raise 40
policy.raise[12 * 13 + 11] = 0.4;
let totals = rangeTotals(policy);
assert.ok(Math.abs(totals.raise - (6 + 1.6) / 1326 * 100) < 1e-9);
assert.ok(Math.abs(totals.call - 2.4 / 1326 * 100) < 1e-9);
assert.ok(Math.abs(totals.raise + totals.jam + totals.call + totals.fold - 100) < 1e-9);
// free check: what does not raise checks
totals = rangeTotals(policy, true);
assert.equal(totals.fold, 0);
assert.ok(Math.abs(totals.raise + totals.call - 100) < 1e-9);
assert.deepEqual(rangeTotals(null), { raise: 0, jam: 0, call: 0, fold: 0 });

// The editor is wired to the brush: a tile per action, a number box for each
// share, one undo step per stroke, and right-click to pick a hand up.
const lab = readFileSync(new URL('../web/js/preflop_lab.js', import.meta.url), 'utf8');
for (const action of BRUSH_ACTIONS) assert.match(lab, new RegExp(`id="pfe-mix-${action}"`));
for (const action of ['fold', ...BRUSH_ACTIONS]) assert.match(lab, new RegExp(`data-part="${action}"><button type="button" data-a="${action}"`));
assert.match(lab, /brushParts\(S\.brush, editorFreeCheck\(\)\)/);
assert.match(lab, /if \(before && strokeStart\)/);
assert.match(lab, /addEventListener\('contextmenu'/);
assert.doesNotMatch(lab, /paintWeight|paintAction/);

console.log('preflop brush tests passed');
