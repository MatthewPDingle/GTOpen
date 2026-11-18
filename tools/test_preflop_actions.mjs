// Preflop Lab action labels: every size in bb, a re-raise's multiple as a note.
import assert from 'node:assert/strict';
import { actionText, formatPreflopView } from '../web/js/preflop_actions.js';

const positions = ['CO', 'BTN', 'SB', 'BB'];
const posts = [0, 0, 0.5, 1];
const fold = { kind: 'fold', to: 0, label: 'Fold' };
const call = (to, label = `Call ${to}`) => ({ kind: 'call', to, label });
const raise = (to, label = `Raise ${to}`) => ({ kind: 'raise', to, label });
const step = (actor_pos, actions, chosen = null) => ({ actor_pos, actions, chosen });
const last = (history, config = {}) => formatPreflopView({ positions, history }, { posts, ...config }).actions;
const texts = actions => actions.map(actionText);

// Pan's spot: BTN opens to 4, SB folds, BB may call or 3-bet 2.75 times.
let actions = last([
  step('CO', [fold, raise(4)], 0),
  step('BTN', [fold, raise(4)], 1),
  step('SB', [fold, call(4), raise(11, '3-bet 11')], 0),
  step('BB', [fold, call(4), raise(11, '3-bet 11')]),
]);
assert.deepEqual(texts(actions), ['Fold', 'Call 3 bb', '3-bet 11 bb (2.75x)']);
assert.equal(actions[2].label, '3-bet 11 bb');
assert.equal(actions[2].note, '2.75x');
assert.equal(actions[2].sizingHint, "To 11 bb in total: 2.75 times BTN's raise to 4 bb.");
assert.equal(actions[2].phrase, '3-bet to 11 bb');
// an open is the bb amount alone: its multiple of the big blind is the same number
assert.deepEqual(texts(last([step('CO', [fold, raise(4)])])), ['Fold', 'Raise 4 bb']);

// Callers' money: 3 times an open of 3 over two callers is 9 + 3 + 3 = 15.
const squeeze = [
  step('CO', [fold, raise(3)], 1),
  step('BTN', [fold, call(3), raise(9, '3-bet 9')], 1),
  step('SB', [fold, call(3), raise(12, '3-bet 12')], 1),
  step('BB', [fold, call(3), raise(15, '3-bet 15')]),
];
actions = last(squeeze, { caller_extra: 1 });
assert.deepEqual(texts(actions), ['Fold', 'Call 2 bb', '3-bet 15 bb (3x + callers)']);
assert.equal(actions[2].sizingHint, "To 15 bb in total: 3 times CO's raise to 3 bb, plus the 6 bb its callers put in.");
// the same tree without the setting (a chart, or a game that sizes it that way): the plain multiple
assert.deepEqual(texts(last(squeeze)), ['Fold', 'Call 2 bb', '3-bet 15 bb (5x)']);
// a new raise starts a new round of callers
actions = last([...squeeze.slice(0, 3), step('BB', squeeze[3].actions, 2),
  step('CO', [fold, call(15), raise(37.5, '4-bet 37.5')])], { caller_extra: 1 });
assert.deepEqual(texts(actions), ['Fold', 'Call 12 bb', '4-bet 37.5 bb (2.5x)']);
assert.equal(actions[2].sizingHint, "To 37.5 bb in total: 2.5 times BB's raise to 15 bb.");

// Over limpers: the open already holds the extra; the hint says so.
actions = last([
  step('CO', [fold, call(1, 'Limp 1'), raise(3)], 1),
  step('BTN', [fold, call(1, 'Limp 1'), raise(4)], 1),
  step('SB', [fold, call(1, 'Limp 1'), raise(5)]),
], { limper_extra: 1 });
assert.deepEqual(texts(actions), ['Fold', 'Complete 0.5 bb', 'Raise 5 bb']);
assert.equal(actions[2].sizingHint, 'To 5 bb in total, 2 bb of it for the 2 limpers.');
assert.equal(actions[2].phrase, 'raise to 5 bb');

// All-in: the stack in bb, no multiple in the label.
actions = last([
  step('CO', [fold, raise(2.5), { kind: 'jam', to: 20, label: 'All-in 20' }], 1),
  step('BTN', [fold, { kind: 'call', to: 2.5, label: 'Call 2.5' }, { kind: 'jam', to: 20, label: 'All-in 20' }]),
]);
assert.deepEqual(texts(actions), ['Fold', 'Call 2.5 bb', 'All-in 20 bb']);
assert.equal(actions[2].note, undefined);
assert.equal(actions[2].phrase, 'all-in for 20 bb');
console.log('Preflop action labels: bb everywhere, multiples as notes, callers and limpers explained.');
