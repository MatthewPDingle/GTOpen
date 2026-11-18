import assert from 'node:assert/strict';
import { statusChips, engineChip } from '../web/js/preflop_status.js';

const labels = (st, opts) => statusChips(st, opts).map(c => c.label);
const gpuPlan = { engine: 'gpu', reason: '' };
const cpuPlan = { engine: 'cpu', reason: 'too big for this graphics card (needs 31.5 GB there, the card can give 31.4 GB)' };
const seats = { positions: ['BTN', 'SB', 'BB'] };

// a built game before any solve: the size line already says everything
assert.deepEqual(labels({ state: 'idle', iteration: 0, published_iteration: 0, plan: gpuPlan }, { formEngine: 'gpu' }), []);

// while a solve runs the progress bar has the iteration and the gap: only the engine is left
const running = { state: 'running', iteration: 647, published_iteration: 640, accuracy_iteration: 600,
  gaps: [0.01, 0.012, 0.0108], gap_total: 0.0328, gpu: true, plan: gpuPlan };
assert.deepEqual(labels(running, { ...seats, formEngine: 'gpu' }), ['⚡ GPU']);
// the first moments, before the card reports in
assert.deepEqual(labels({ state: 'running', iteration: 0, plan: gpuPlan }, { formEngine: 'gpu' }), ['GPU…']);
// a solve on the processor says so, with the reason in the tip
let chips = statusChips({ state: 'running', iteration: 12, plan: cpuPlan }, { formEngine: 'cpu' });
assert.deepEqual(chips.map(c => c.label), ['CPU']);
assert.match(chips[0].tip, /^Solving on the processor \(CPU\): too big for this graphics card/);

// a finished solve: that it is done, and the final gap, once each
const done = { state: 'done', stop_reason: 'target_reached', iteration: 1600, published_iteration: 1600,
  accuracy_iteration: 1600, gaps: [0.001, 0.002, 0.0019], gap_total: 0.0049, gpu: true, plan: gpuPlan };
chips = statusChips(done, { ...seats, formEngine: 'gpu' });
assert.deepEqual(chips.map(c => c.label), ['done · iter 1600', 'gap 0.0049 → 0.0050']);
assert.match(chips[0].tip, /^Target gap reached\./);
assert.match(chips[1].tip, /BTN: 0\.0010 · SB: 0\.0020 · BB: 0\.0019$/);

// stopped between measurements: the gap says which iteration it belongs to
const stopped = { ...done, state: 'stopped', stop_reason: '', iteration: 647, published_iteration: 647,
  accuracy_iteration: 600, gap_total: 0.0328 };
assert.deepEqual(labels(stopped, { ...seats, formEngine: 'gpu' }), ['stopped · iter 647', 'gap 0.0328 → 0.0050 at iter 600']);
// the screen is behind the solver only when a final copy failed: then it says so
assert.deepEqual(labels({ ...stopped, published_iteration: 600 }, { ...seats, formEngine: 'gpu' }).slice(2), ['showing iter 600']);
// a loaded game has no measured gap yet
assert.deepEqual(labels({ state: 'stopped', iteration: 74, published_iteration: 74, accuracy_iteration: null, gaps: [], plan: gpuPlan },
  { formEngine: 'gpu' }), ['stopped · iter 74']);

// the engine chip stays after a solve only when it is not what the size line names
assert.equal(engineChip(done, 'gpu'), null);
assert.equal(engineChip(done, 'cpu').label, '⚡ GPU');
const fellBack = { state: 'done', iteration: 300, gpu: false, plan: gpuPlan,
  gpu_note: 'Solving on the processor (CPU): the graphics card could not take this game (out of memory).' };
assert.deepEqual(engineChip(fellBack, 'gpu'), { label: 'CPU', tip: fellBack.gpu_note });
assert.equal(engineChip(fellBack, 'cpu'), null);
// a built game whose table (profiles, locks) no longer fits the card, though the form's game would
assert.equal(engineChip({ state: 'idle', iteration: 0, plan: cpuPlan }, 'gpu').label, 'CPU');
// an older server sends no plan
assert.equal(engineChip({ state: 'idle', iteration: 0 }, null), null);
assert.equal(engineChip({ state: 'running', iteration: 3 }, null).label, 'CPU');
console.log('preflop status chips: ok');
