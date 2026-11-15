import assert from 'node:assert/strict';
import { DEFAULT_NET, FIRST_NET, modelFor, netConfig, netOf, label } from '../web/js/preflop_leafnet.js';

// a new game: learned flop values with the default net
assert.equal(modelFor(true, false), 'leafnet', 'ticked, no ICM: learned flop values');
assert.equal(modelFor(true, true), 'balanced', 'ICM payouts are priced by the balanced model');
assert.equal(modelFor(false, false), 'balanced', 'unticked: the balanced model alone');
assert.equal(netOf(null, null), DEFAULT_NET, 'nothing remembered: the default net');
assert.deepEqual(netConfig(true, DEFAULT_NET), { leaf_net: 'v2' }, 'the default net is named in the game');

// games from before a second net shipped name no net and mean v1
assert.equal(netOf({ realization: 'leafnet' }, 'snap/run'), FIRST_NET, 'an unnamed net is v1, whatever is remembered');
assert.deepEqual(netConfig(true, FIRST_NET), {}, 'v1 stays unnamed, as in older saves');
assert.equal(netOf({ realization: 'leafnet', leaf_net: 'snap/run' }, null), 'snap/run', 'a loaded game shows its own net');
assert.equal(netOf({ realization: 'balanced' }, 'snap/run'), 'snap/run', 'a balanced game leaves the remembered pick');
assert.equal(netOf({ realization: 'balanced', leaf_net: 'v1' }, null), DEFAULT_NET);

// no net is sent when the game does not use learned values
assert.deepEqual(netConfig(false, DEFAULT_NET), {});
assert.deepEqual(netConfig(modelFor(true, true) === 'leafnet', 'snap/run'), {}, 'ICM game: no net');
assert.deepEqual(netConfig(true, 'snap/run'), { leaf_net: 'snap/run' });

// the picker says which shipped net is the default, and when a file is missing
assert.equal(label({ id: 'v2', kind: 'shipped', default: true, members: 3 }), 'v2 · shipped · default · mean of 3 nets');
assert.equal(label({ id: 'v1', kind: 'shipped', train_examples: 52000 }), 'v1 · shipped · 52k examples');
assert.equal(label({ id: 'v2', kind: 'shipped', default: true, available: false }), 'v2 · shipped · default · missing');
console.log('preflop leaf net defaults: ok');
