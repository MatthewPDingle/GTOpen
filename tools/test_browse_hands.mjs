// The "how often" figure on the Browse tab's combo tiles (web/js/browse.js).
import assert from 'node:assert/strict';
import { freqPct } from '../web/js/browse.js';

assert.equal(freqPct(0.275), '27.5%');
assert.equal(freqPct(0.012), '1.2%');
assert.equal(freqPct(0.001), '0.1%', 'the rarest action a tile lists');
assert.equal(freqPct(1), '100%', 'no "100.0%"');
assert.equal(freqPct(0.9996), '100%');
assert.equal(freqPct(0.998), '99.8%');
assert.equal(freqPct(0), '0%', 'an action a best reply never takes');
assert.equal(freqPct(undefined), '0%');

console.log('browse hands: ok');
