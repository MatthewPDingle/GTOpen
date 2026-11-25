// Two or three players on the postflop pages: the page calls one set of
// functions and web/js/api.js sends them to the kind of spot that is loaded.
import assert from 'node:assert/strict';
import { api, isThreeWay, spotPlayers, setSpotPlayers } from '../web/js/api.js';

const calls = [];
let replies = {};
globalThis.fetch = async (url, opts = {}) => {
  calls.push(`${opts.method || 'GET'} ${url}`);
  const body = url in replies ? replies[url] : {};
  if (body instanceof Error) return { ok: false, status: 404, text: async () => 'Not Found' };
  return { ok: true, status: 200, json: async () => body, text: async () => JSON.stringify(body) };
};
const last = () => calls[calls.length - 1];

const HU = { board: 'Ks7h2d', range_oop: 'AA', range_ip: 'KK' };
const THREE = { board: 'Ks7h2d', ranges: ['AA', 'KK', 'QQ'], stacks: [100, 100, 100] };

// the request's shape says which kind it is
assert.equal(isThreeWay(THREE), true);
assert.equal(isThreeWay(HU), false);
assert.equal(isThreeWay(null), false);

// a heads-up spot uses the heads-up calls
await api.buildSpot(HU);
assert.equal(last(), 'POST /api/spot');
assert.equal(spotPlayers(), 2);
await api.node([]);
assert.equal(last(), 'POST /api/node');
await api.locks();
assert.equal(last(), 'GET /api/locks');
await api.solve({ max_iterations: 10, engine: 'gpu', algorithm: 'dcfr' });
assert.equal(last(), 'POST /api/solve');

// a three-player spot uses its own, and asks for no locks
await api.buildSpot(THREE);
assert.equal(last(), 'POST /api/mw/spot');
assert.equal(spotPlayers(), 3);
for (const [fn, url] of [
  [() => api.node([]), 'POST /api/mw/node'],
  [() => api.exploit([], 1), 'POST /api/mw/exploit'],
  [() => api.solve({ max_iterations: 10, engine: 'cpu' }), 'POST /api/mw/solve'],
  [() => api.stop(), 'POST /api/mw/stop'],
  [() => api.status(), 'GET /api/mw/status'],
  [() => api.save('x'), 'POST /api/mw/save'],
]) {
  await fn();
  assert.equal(last(), url);
}
const before = calls.length;
assert.deepEqual(await api.locks(), []);
assert.deepEqual(await api.lockHistory(), { undo: [], redo: [] });
assert.deepEqual(await api.locksList(), { locks: [], profile: [0, 0] });
assert.equal(calls.length, before, 'no lock requests for three players');

// one list of saved solves holds both kinds
replies = { '/api/saves': ['btn-vs-bb'], '/api/mw/saves': [{ name: 'three', board: 'Ks7h2d9h', iteration: 100 }] };
assert.deepEqual(await api.saves(), [{ name: 'btn-vs-bb', players: 2 }, { name: 'three', players: 3 }]);
// a server from before three-player saves still lists the others
replies['/api/mw/saves'] = new Error('gone');
assert.deepEqual(await api.saves(), [{ name: 'btn-vs-bb', players: 2 }]);

// loading says which kind it is, and later calls follow it
await api.load('btn-vs-bb', 2);
assert.equal(last(), 'POST /api/load');
assert.equal(spotPlayers(), 2);
await api.load('three', 3);
assert.equal(last(), 'POST /api/mw/load');
assert.equal(spotPlayers(), 3);

// on page load the page asks which kind the server holds
replies = { '/api/mw/status': { state: 'idle', tree: null } };
assert.equal(await api.detectSpot(), 2);
replies = { '/api/mw/status': { state: 'done', tree: { nodes: 10 } } };
assert.equal(await api.detectSpot(), 3);
replies = { '/api/mw/status': new Error('no such page') };
assert.equal(await api.detectSpot(), 2, 'a server without three-player spots');

// a status from a server older than the merged pages reads the same way
setSpotPlayers(3);
replies = { '/api/mw/status': { state: 'running', iteration: 20, exploit_pct: 1.5, elapsed: 12, engine: 'gpu',
  history: [[10, 4.2], [20, 1.5]], tree: { nodes: 5, arena_mb_compressed: 40, gpu_mb: 300 } } };
const st = await api.status();
assert.equal(st.elapsed_secs, 12);
assert.equal(st.gpu, true);
assert.deepEqual(st.history, [{ iteration: 10, exploit_pct: 4.2 }, { iteration: 20, exploit_pct: 1.5 }]);
assert.equal(st.tree.arena_mb, 40);
assert.equal(st.tree.vram_mb, 300);
// a current status passes through untouched
replies = { '/api/mw/status': { state: 'done', elapsed_secs: 3, gpu: false, history: [], tree: { arena_mb: 7 } } };
assert.deepEqual(await api.status(), replies['/api/mw/status']);

console.log('two or three players: ok');
