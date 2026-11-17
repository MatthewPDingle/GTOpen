import assert from 'node:assert/strict';
import { BLOCKERS_DEFAULT, blockersConfig, blockersOf, blockersWanted, rememberBlockers } from '../web/js/preflop_blockers.js';

const store = () => { const m = new Map(); return { getItem: k => (m.has(k) ? m.get(k) : null), setItem: (k, v) => m.set(k, v) }; };

// a new game follows the default until this browser chooses
const s = store();
assert.equal(blockersWanted(s), BLOCKERS_DEFAULT);
rememberBlockers(s, false);
assert.equal(blockersWanted(s), false);
rememberBlockers(s, true);
assert.equal(blockersWanted(s), true);
assert.equal(blockersWanted(null), BLOCKERS_DEFAULT, 'no storage: the default');

// the engine field is only sent when on, and never with ICM payouts
assert.deepEqual(blockersConfig(true, false), { card_removal: true });
assert.deepEqual(blockersConfig(false, false), {}, 'off: as in every older save');
assert.deepEqual(blockersConfig(true, true), {}, 'ICM games are solved without blockers');

// a loaded game shows what it was solved with
assert.equal(blockersOf({ card_removal: true }), true);
assert.equal(blockersOf({ realization: 'leafnet' }), false, 'an old save has no blockers');
assert.equal(blockersOf(null), false);
console.log('preflop blockers setting: ok');
