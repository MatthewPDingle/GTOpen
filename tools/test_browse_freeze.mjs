import assert from 'node:assert/strict';
import { freezeableAncestors } from '../web/js/browse.js';

// A line with three earlier decisions and one card step: root, Check, Bet 33, deal turn.
const path = [
  { type: 'action', index: 0 },
  { type: 'action', index: 1 },
  { type: 'card', card: 12 },
  { type: 'action', index: 0 },
];
const labels = ['Check', 'Bet 3.3', '2s'];
const board = 'Ks7h2d';
const descs = [`${board} root`, `${board} Check`, `${board} Check > Bet 3.3 > 2s`];

const unlocked = freezeableAncestors(path, labels, board, () => false);
assert.equal(unlocked, 3, 'every earlier decision is freezeable when no ancestor is locked');

const seen = [];
freezeableAncestors(path, labels, board, d => { seen.push(d); return false; });
assert.deepEqual(seen, descs, 'ancestors are named the way the server names them');

// Locking an ancestor removes only that decision from the count.
assert.equal(freezeableAncestors(path, labels, board, d => d === descs[0]), 2);
assert.equal(freezeableAncestors(path, labels, board, d => d === descs[1]), 2);
assert.equal(freezeableAncestors(path, labels, board, d => d !== descs[2]), 1);

// The bug this guards: a lock at the node being viewed (a profile lock's
// badge) must not make the ancestors look locked. The callback answers per
// ancestor; the current node is never asked about.
const currentOnly = freezeableAncestors(path, labels, board, d => d.endsWith('root'));
assert.equal(currentOnly, 2, 'root is locked for real, the two later decisions are not');

// No earlier decision: nothing to freeze.
assert.equal(freezeableAncestors([], [], board, () => false), 0);
assert.equal(freezeableAncestors([{ type: 'card', card: 3 }], [], board, () => false), 0);

console.log('test_browse_freeze: ok');
