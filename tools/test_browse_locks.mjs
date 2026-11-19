// The words the Browse tab's list of locks is built from (web/js/browse.js).
import assert from 'node:assert/strict';
import { shortAction, lockWhere, lockMix, handList, plainLockError, freezeableAncestors } from '../web/js/browse.js';

assert.equal(shortAction('Bet 4.25 (50%)'), 'Bet 4.25');
assert.equal(shortAction('All-in 26'), 'All-in 26');
assert.equal(shortAction('Raise 12 (62.5%)'), 'Raise 12');

// where a lock sits
assert.equal(lockWhere([]), 'first decision');
assert.equal(lockWhere(['Check']), 'after Check');
assert.equal(lockWhere(['Check', 'Bet 4.25 (50%)']), 'after Check › Bet 4.25');
assert.equal(lockWhere(['Check', 'Bet 4.25 (50%)', 'Call', '7h', 'Check']), 'after … › Call › 7h › Check',
  'a long line keeps its last three steps');

// what a lock makes the range do: actions under 1% are left out
assert.equal(lockMix(['Check', 'Bet 4.25 (50%)', 'All-in 26'], [1, 0, 0]), '100% Check');
assert.equal(lockMix(['Check', 'All-in 26'], [0.594, 0.406]), '59% Check, 41% All-in 26');
assert.equal(lockMix(['Fold', 'Call'], [0.004, 0.996]), '100% Call');

assert.equal(handList(['AA', 'AKs', 'AKo']), 'AA, AKs, AKo');
assert.equal(handList(['AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', '77']), 'AA, KK, QQ, JJ, TT + 3 more');

// the solver's refusal of a one-suit lock on a board with twin suits, in plain words
// (the message is the one lock_node in crates/solver/src/query.rs sends)
const plain = plainLockError(new Error('per-hand lock breaks the suit symmetry the solver uses on this board: ' +
  'Ac7c is mirrored by Ad7d — lock the mirror to the same frequencies too (or solve with isomorphism off, SOLVER_ISO=0)'));
assert.match(plain.message, /Ac7c and Ad7d are the same hand apart from the suits/);
assert.match(plain.message, /locked alike/);
assert.doesNotMatch(plain.message, /SOLVER_ISO|isomorphism|symmetry/, 'no solver words reach the page');
const other = new Error('frequencies must sum to 1');
assert.equal(plainLockError(other), other, 'any other error passes through untouched');

// "keep earlier play" counts only the locked player's own earlier decisions
// when the server keeps just those: root (OOP), Check (IP), All-in (OOP to act).
const path = [{ type: 'action', index: 0 }, { type: 'action', index: 1 }];
const labels = ['Check', 'All-in 26'];
const ownOop = i => i % 2 === 0; // OOP acts at the root, IP after the check
assert.equal(freezeableAncestors(path, labels, 'As8h9d', () => false), 2, 'an older server keeps both players');
assert.equal(freezeableAncestors(path, labels, 'As8h9d', () => false, ownOop), 1, "only OOP's own decision");
assert.equal(freezeableAncestors(path, labels, 'As8h9d', d => d.endsWith('root'), ownOop), 0,
  'nothing to keep when that decision is already locked');

console.log('test_browse_locks: ok');
