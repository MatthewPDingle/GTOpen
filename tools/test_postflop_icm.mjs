import assert from 'node:assert/strict';
import { icmFingerprint, parseStacks } from '../web/js/postflop_icm.js';

// What the page sends for a tournament spot, and what the server echoes back
// for the same spot: empty lists dropped, fields in its own order.
const sent = { payouts: [50, 30, 20], ...parseStacks('35, 22') };
const echoed = { payouts: [50.0, 30.0, 20.0], others: [35.0, 22.0] };
assert.equal(icmFingerprint(sent), icmFingerprint(echoed), 'the same payouts must not read as a changed SETUP');

const bare = { payouts: [60, 40], ...parseStacks('') };
assert.deepEqual(bare.others, []);
assert.equal(icmFingerprint(bare), icmFingerprint({ payouts: [60, 40] }), 'empty lists equal missing lists');

const grouped = { payouts: [50, 30, 20], ...parseStacks('35, 144x25'), behind: [26, 40] };
const groupedEcho = { field_groups: [{ stack: 25, count: 144 }], others: [35], behind: [26.0, 40.0], payouts: [50, 30, 20] };
assert.equal(icmFingerprint(grouped), icmFingerprint(groupedEcho), 'field order does not matter');

// Real changes still read as changes.
assert.notEqual(icmFingerprint(sent), icmFingerprint({ ...sent, payouts: [50, 30, 21] }));
assert.notEqual(icmFingerprint(sent), icmFingerprint({ ...sent, others: [35, 23] }));
assert.notEqual(icmFingerprint(sent), icmFingerprint({ ...sent, behind: [26, 40] }));
assert.notEqual(icmFingerprint(grouped), icmFingerprint({ ...grouped, field_groups: [{ count: 143, stack: 25 }] }));
assert.equal(icmFingerprint(null), null);
assert.equal(icmFingerprint(undefined), null);
assert.notEqual(icmFingerprint(bare), null, 'payouts on is not the same as payouts off');

console.log('test_postflop_icm: ok');
