import assert from 'node:assert/strict';
import { sizingConfig, sizingFromConfig, situationalConfig, usesSituationalSizes } from '../web/js/preflop_sizing.js';

const seats = ['UTG', 'HJ', 'CO', 'BTN', 'SB', 'BB'];

// Everything off: the config is exactly what the form sent before these
// settings existed, so an old scenario builds the old game.
const off = sizingConfig(seats, {}, '', '3');
assert.deepEqual(off, { open_raises_by_seat: null, raise_mults_by_seat: null, fourbet_mults: [3], fourbet_mults_by_seat: null });
assert.equal(usesSituationalSizes(off), false);
assert.deepEqual(situationalConfig(), {});
assert.deepEqual(situationalConfig({ limps: true, limperExtra: '', callerMoney: false, multOop: '', laterOop: '' }, '', '3'), {});
assert.deepEqual(situationalConfig({ limps: true, limperExtra: '0' }), {}, 'zero is off');

// the extra per limper: a bb amount, and only when limps are allowed
assert.deepEqual(situationalConfig({ limps: true, limperExtra: '1' }), { limper_extra: 1 });
assert.deepEqual(situationalConfig({ limps: true, limperExtra: ' 1.5 ' }), { limper_extra: 1.5 });
assert.deepEqual(situationalConfig({ limps: false, limperExtra: '1' }), {}, 'no limps, nothing to add');
assert.throws(() => situationalConfig({ limps: true, limperExtra: 'x' }), /per limper/);
assert.throws(() => situationalConfig({ limps: true, limperExtra: '-1' }), /per limper/);

// callers' money is all or nothing: one full call per caller
assert.deepEqual(situationalConfig({ callerMoney: true }), { caller_extra: 1 });

// out of position: 3-bets, and 4-bets follow the same "empty = as 3-bet" rule
assert.deepEqual(situationalConfig({ multOop: '4' }, '', '3'), { raise_mults_oop: [4], fourbet_mults_oop: [4] },
  'an empty 4-bet box uses the 3-bet number, in and out of position');
assert.deepEqual(situationalConfig({ multOop: '4' }, '2.3', '3'), { raise_mults_oop: [4] },
  'a 4-bet size with no out-of-position one is used in both');
assert.deepEqual(situationalConfig({ multOop: '4', laterOop: '2.7' }, '2.3', '3'), { raise_mults_oop: [4], fourbet_mults_oop: [2.7] });
assert.deepEqual(situationalConfig({ laterOop: '2.7,3' }, '', '3'), { fourbet_mults_oop: [2.7, 3] });
assert.throws(() => situationalConfig({ multOop: '4,x' }), /positive numbers/);

// the whole form, and back again from a built or loaded game
const by = { limps: true, limperExtra: '1', callerMoney: true, multOop: '4', laterOop: '2.7' };
const cfg = sizingConfig(seats, { BTN: { open: '2.5' } }, '2.3', '3', by);
assert.deepEqual(cfg, {
  open_raises_by_seat: [[], [], [], [2.5], [], []], raise_mults_by_seat: null,
  fourbet_mults: [2.3], fourbet_mults_by_seat: null,
  limper_extra: 1, caller_extra: 1, raise_mults_oop: [4], fourbet_mults_oop: [2.7],
});
assert.equal(usesSituationalSizes(cfg), true);
const back = sizingFromConfig({ positions: seats, raise_mults: [3], ...cfg });
assert.equal(back.later, '2.3');
assert.equal(back.limperExtra, '1');
assert.equal(back.callerMoney, true);
assert.equal(back.multOop, '4');
assert.equal(back.laterOop, '2.7');
assert.equal(back.rows.BTN.open, '2.5');
assert.deepEqual(sizingConfig(seats, back.rows, back.later, '3', { limps: true, ...back }), cfg, 'a loaded game builds the same game again');

// a game from before these settings loads with all of them off
const old = sizingFromConfig({ positions: seats, raise_mults: [3], fourbet_mults: [3] });
assert.deepEqual([old.limperExtra, old.callerMoney, old.multOop, old.laterOop], ['', false, '', '']);
console.log('preflop sizing: ok');
