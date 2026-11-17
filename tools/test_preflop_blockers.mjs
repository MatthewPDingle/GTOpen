import assert from 'node:assert/strict';
import { blockersConfig, blockersOf } from '../web/js/preflop_blockers.js';

// every new game is built with blockers, except with ICM payouts
assert.deepEqual(blockersConfig(false), { card_removal: true });
assert.deepEqual(blockersConfig(true), {}, 'ICM games are solved without blockers');

// a loaded game shows what it was solved with
assert.equal(blockersOf({ card_removal: true }), true);
assert.equal(blockersOf({ realization: 'leafnet' }), false, 'a save from before blockers has none');
assert.equal(blockersOf(null), false);
console.log('preflop blockers: ok');
