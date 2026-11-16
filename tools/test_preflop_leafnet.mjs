import assert from 'node:assert/strict';
import { DEFAULT_NET, FIRST_NET, createLeafNet, modelFor, netConfig, netOf } from '../web/js/preflop_leafnet.js';

// a new game: learned flop values with the default net
assert.equal(modelFor(true, false), 'leafnet', 'ticked, no ICM: learned flop values');
assert.equal(modelFor(true, true), 'balanced', 'ICM payouts are priced by the balanced model');
assert.equal(modelFor(false, false), 'balanced', 'unticked: the balanced model alone');
assert.equal(netOf(null), DEFAULT_NET, 'no game: the default net');
assert.deepEqual(netConfig(true, DEFAULT_NET), { leaf_net: 'v2' }, 'the default net is named in the game');

// games from before a second net shipped name no net and mean v1
assert.equal(netOf({ realization: 'leafnet' }), FIRST_NET, 'an unnamed net is v1');
assert.deepEqual(netConfig(true, FIRST_NET), {}, 'v1 stays unnamed, as in older saves');
assert.equal(netOf({ realization: 'leafnet', leaf_net: 'snap/run' }), 'snap/run', 'a loaded game keeps its own net');
assert.equal(netOf({ realization: 'balanced', leaf_net: 'v1' }), DEFAULT_NET);

// no net is sent when the game does not use learned values
assert.deepEqual(netConfig(false, DEFAULT_NET), {});

// the form's net: default, a loaded game's own, back to the default for a fresh scenario
const net = createLeafNet();
assert.deepEqual(net.config(true), { leaf_net: 'v2' });
assert.deepEqual(net.config(false), {});
net.load({ realization: 'leafnet' });
assert.deepEqual(net.config(true), {}, 'a re-solve of an old save keeps v1');
net.load(null);
assert.deepEqual(net.config(true), { leaf_net: 'v2' });
console.log('preflop leaf net defaults: ok');
