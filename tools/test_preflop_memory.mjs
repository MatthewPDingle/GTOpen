import assert from 'node:assert/strict';
import { sizeText, cardState, cardText, engineText, largeGame, planChip, estimateView, UNKNOWN_ENGINE } from '../web/js/preflop_memory.js';

// sizes in the GB Windows and a card's box use (the server sends 1 MB = 1,000,000 bytes)
assert.equal(sizeText(34359.738368), '32.0 GB');
assert.equal(sizeText(137438.953472), '128 GB');
assert.equal(sizeText(524.288), '500 MB');
assert.equal(sizeText(0.2), '1 MB');

const gpu = { engine: 'gpu', reason: '', ram_mb: 2147.483648, gpu_need_mb: 1073.741824, gpu_free_mb: 30000, gpu_total_mb: 34190 };
const cpu = {
  engine: 'cpu', ram_mb: 21474.83648, gpu_need_mb: 33784, gpu_free_mb: 32000, gpu_total_mb: 34190,
  reason: 'too big for this GPU (needs 31.5 GB of GPU memory, it has 31.4 GB)',
};

// GPU memory has its own line, apart from RAM: what the game needs there against what the GPU has
const GB = 2 ** 30 / 1e6;
const busy = { engine: 'cpu', card: 'busy', ram_mb: 9000, gpu_need_mb: 20 * GB, gpu_free_mb: 8 * GB, gpu_total_mb: 34190, gpu_limit_mb: 33678,
  reason: 'the GPU has too little memory free right now (needs 20.0 GB, 8.0 GB free)' };
const noCard = card => ({ engine: 'cpu', card, ram_mb: 500, gpu_need_mb: 300, gpu_free_mb: 0, gpu_total_mb: 0, gpu_limit_mb: 0, reason: 'x' });
assert.equal(cardText({ ...gpu, card: 'fits', gpu_limit_mb: 33678 }), 'GPU memory: needs 1.0 GB, 27.9 GB free — fits\u00a0✓');
assert.equal(cardText({ ...cpu, card: 'too_big', gpu_limit_mb: 33678 }),
  'GPU memory: needs 31.5 GB, has 31.4 GB — too big\u00a0✗');
assert.equal(cardText({ ...cpu, card: 'too_big', gpu_need_mb: null }), 'GPU memory: far too big for this GPU\u00a0✗');
assert.equal(cardText(busy), 'GPU memory: needs 20.0 GB, only 8.0 GB free now — no room\u00a0✗');
assert.equal(cardText(noCard('none')), 'GPU: no NVIDIA GPU found');
assert.equal(cardText(noCard('off')), 'GPU: switched off for GTOpen (SOLVER_GPU=0)');
assert.equal(cardText(noCard('unsupported')), 'GPU: this copy of GTOpen cannot use one');
// a server from before `card` and `gpu_limit_mb`: the same lines, read from the rest of its plan
assert.equal(cardState(gpu), 'fits');
assert.equal(cardState(cpu), 'too_big');
assert.equal(cardText(cpu), 'GPU memory: needs 31.5 GB, has 31.4 GB — too big\u00a0✗');
assert.equal(cardState({ ...busy, card: undefined }), 'busy');
assert.equal(cardState({ ...noCard(undefined), reason: 'no NVIDIA graphics card found' }), 'none');
assert.equal(cardState({ ...noCard(undefined), reason: 'the graphics card is switched off for GTOpen (SOLVER_GPU=0)' }), 'off');
assert.equal(cardState({ ...noCard(undefined), reason: 'this copy of GTOpen has no graphics card support' }), 'unsupported');
assert.equal(cardState({ ...noCard(undefined), reason: 'this copy of GTOpen has no GPU support' }), 'unsupported');
assert.equal(engineText(gpu), 'Solves on: GPU — uses both the RAM and the GPU memory');
assert.equal(engineText(cpu), 'Solves on: CPU, slower — uses the RAM only');

// the chip before a solve is the plan; in a solve's first moments it says what is happening
assert.deepEqual(planChip(gpu), { label: 'GPU', tip: 'The next solve will run on the GPU.' });
assert.equal(planChip(gpu, true).label, 'GPU…');
assert.equal(planChip(cpu).label, 'CPU');
assert.match(planChip(cpu).tip, /^The next solve will run on the CPU: too big for this GPU/);
assert.match(planChip(cpu, true).tip, /^Solving on the CPU: too big for this GPU/);

const estimate = (over = {}) => ({
  nodes: 1_000_000, action_nodes: 480_000, arena_mb: 1600, truncated: false, ok: true,
  limit_nodes: 30_000_000, limit_arena_mb: 38_000, plan: gpu, ...over,
});

// a game that fits: its size, the memory it needs, and where it solves
let view = estimateView(estimate());
assert.equal(view.state, 'ok');
assert.deepEqual(view.lines, [
  'Game tree: 1,000,000 nodes',
  'RAM: needs about 2.0 GB — fits\u00a0✓',
  'GPU memory: needs 1.0 GB, 27.9 GB free — fits\u00a0✓',
  'Solves on: GPU — uses both the RAM and the GPU memory',
]);
assert.match(view.tip, /A GPU solve is much faster and uses both: this RAM, and the GPU's own memory/);
assert.match(view.tip, /because the GPU works on the whole game at once/);

// too big for the card: it still fits the computer, and the line says why the CPU
view = estimateView(estimate({ plan: cpu, nodes: 11_546_836, arena_mb: 15_611 }));
assert.equal(view.state, 'ok');
assert.equal(view.lines[0], 'Game tree: 11,546,836 nodes');
// RAM and the card are separate lines, so "fits" is never read as fitting the card
assert.deepEqual(view.lines.slice(1), [
  'RAM: needs about 20.0 GB — fits\u00a0✓',
  'GPU memory: needs 31.5 GB, has 31.4 GB — too big\u00a0✗',
  'Solves on: CPU, slower — uses the RAM only',
]);
assert.match(view.tip, /To fit the GPU, make the game smaller/);
assert.match(estimateView(estimate({ plan: busy })).tip, /close whatever else is using it/);
assert.doesNotMatch(estimateView(estimate({ plan: noCard('none') })).tip, /To fit the GPU/);

// too big for the GPU all at once, but not a part at a time: still the GPU, and the line says which way
const large = { engine: 'gpu', card: 'fits', gpu_mode: 'large', reason: '', ram_mb: 35_840.6, gpu_need_mb: 19_095,
  gpu_free_mb: 33_678, gpu_total_mb: 34_190, gpu_limit_mb: 33_678 };
view = estimateView(estimate({ plan: large, nodes: 11_546_836, arena_mb: 15_611 }));
assert.deepEqual(view.lines.slice(1), [
  'RAM: needs about 33.4 GB — fits\u00a0✓',
  'GPU memory: needs 17.8 GB, 31.4 GB free — fits\u00a0✓',
  'Solves on: GPU, large-game mode — uses RAM and GPU memory',
]);
assert.ok(view.lines.every(line => line.length <= 58), 'the lines fit a narrow panel');
assert.match(view.tip, /This game is in large-game mode: it is too big for the GPU all at once/);
assert.doesNotMatch(view.tip, /To fit the card/);
assert.equal(planChip(large).tip, 'The next solve will run on the GPU, in large-game mode.');
// a game that fits whole, and a server from before the mode, read as before
assert.equal(largeGame(gpu), false);
assert.equal(largeGame({ ...cpu, gpu_mode: 'large' }), false);
assert.doesNotMatch(estimateView(estimate()).tip, /This game is in large-game mode/);
assert.match(estimateView(estimate()).tip, /can still solve on the GPU in large-game mode/);

// near the RAM limit, and over it
view = estimateView(estimate({ arena_mb: 36_000 }));
assert.equal(view.state, 'warn');
assert.match(view.lines[1], /only just fits/);
view = estimateView(estimate({ ok: false, truncated: true, nodes: 40_000_000, arena_mb: 50_000 }));
assert.equal(view.state, 'bad');
assert.equal(view.lines[0], 'Game tree: more than 40,000,000 nodes');
assert.match(view.lines[1], /^RAM: needs more than \d+\.\d GB — too big for this computer right now/);
assert.equal(view.lines.length, 2, 'no card or engine line for a game that cannot be built');
assert.match(view.tip, /To make the game smaller/);

// nothing a player reads uses the engine's own words
for (const v of [estimateView(estimate()), estimateView(estimate({ plan: cpu })), estimateView(estimate({ ok: false }))]) {
  assert.doesNotMatch(v.lines.join(' ') + v.tip, /arena|VRAM|CUDA|env var/i);
}
console.log('preflop memory: ok');

// A server that was pulled but not restarted sends no plan: the size still shows, and says why the rest is missing.
{
  const old = estimate({ nodes: 5_779_786, arena_mb: 7800 });
  delete old.plan;
  const view = estimateView(old);
  assert.equal(view.state, 'ok');
  assert.equal(view.lines[0], 'Game tree: 5,779,786 nodes');
  assert.match(view.lines[1], /^RAM: needs about 9\.\d GB — fits/);
  assert.equal(view.lines[2], UNKNOWN_ENGINE);
  assert.match(view.lines[2], /restart GTOpen/);
  assert.match(view.tip, /newer than the GTOpen program that is running/);
  const tooBig = estimateView({ ...old, ok: false });
  assert.equal(tooBig.lines.length, 2);
  assert.equal(tooBig.state, 'bad');
}
console.log('preflop memory without a plan: ok');
