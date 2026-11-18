import assert from 'node:assert/strict';
import { statusChips, engineChip, isStopping, runningLabel, endedLabel } from '../web/js/preflop_status.js';

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

// STOP ends with one last accuracy check: the gap belongs to the strategy on screen
const stoppedNow = { ...done, state: 'stopped', stop_reason: 'stopped', iteration: 647, published_iteration: 647,
  accuracy_iteration: 647, gap_total: 0.0328 };
chips = statusChips(stoppedNow, { ...seats, formEngine: 'gpu' });
assert.deepEqual(chips.map(c => c.label), ['stopped · iter 647', 'gap 0.0328 → 0.0050']);
assert.match(chips[0].tip, /^Stopped before the target gap/);
assert.match(chips[0].tip, /RE-SOLVE carries on/);
assert.match(chips[1].tip, /^Measured when the solve stopped, on the strategy shown\. The target is 0\.0050\. /);
assert.match(chips[1].tip, /BTN: 0\.0010 · SB: 0\.0020 · BB: 0\.0019$/);
// a gap from an earlier check says which iteration it belongs to (a server from before the last check)
const stopped = { ...stoppedNow, stop_reason: '', accuracy_iteration: 600 };
chips = statusChips(stopped, { ...seats, formEngine: 'gpu' });
assert.deepEqual(chips.map(c => c.label), ['stopped · iter 647', 'gap 0.0328 → 0.0050 at iter 600']);
assert.match(chips[1].tip, /^Measured at iteration 600; the strategy shown is from iteration 647\. /);
// a finished solve's gap needs no such note
assert.match(statusChips(done, seats)[1].tip, /^Best-response gap/);
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

// --- the progress bar: solving, stopping, ended ---
const run = { state: 'running', phase: 'iterating', iteration: 110, gap_total: 0.6143 };
const at = { clock: '0:42', shown: 110, earlyPreviews: true };
assert.equal(runningLabel(run, at), 'solving · iter 110 · 0:42 · gap 0.6143 \u2192 0.0050');
assert.equal(runningLabel({ ...run, phase: 'measuring' }, at), 'solving · iter 110 · 0:42 · measuring accuracy…');
assert.equal(runningLabel({ ...run, phase: 'publishing' }, at), 'solving · iter 110 · 0:42 · publishing preview…');
assert.equal(runningLabel({ ...run, gap_total: 0, iteration: 12 }, { ...at, shown: 12 }), 'solving · iter 12 · 0:42 · preview at 12; accuracy every 50 iter');
assert.equal(runningLabel({ ...run, gap_total: 0, iteration: 1 }, { ...at, shown: 1 }), 'solving · iter 1 · 0:42 · preparing first learned preview');
assert.equal(runningLabel({ ...run, gap_total: 0, iteration: 1 }, { ...at, shown: 1, earlyPreviews: false }),
  'solving · iter 1 · 0:42 · first strategy at accuracy checkpoint');
// STOP clicked: the line says so at once and keeps saying so, whatever the solver is finishing
const stopping = { ...at, stopping: true };
assert.equal(runningLabel(run, stopping), 'stopping · iter 110 · 0:42');
assert.equal(runningLabel({ ...run, phase: 'publishing' }, stopping), 'stopping · iter 110 · 0:42');
assert.equal(runningLabel({ ...run, phase: 'final_check' }, stopping), 'stopping · iter 110 · 0:42 · checking final accuracy…');
// a check that was already running when STOP came is that last check
assert.equal(runningLabel({ ...run, phase: 'measuring' }, stopping), 'stopping · iter 110 · 0:42 · checking final accuracy…');

// stopping: from this page's click, or because the server says so (another tab, a reload)
assert.equal(isStopping(run), false);
assert.equal(isStopping(run, true), true);
assert.equal(isStopping({ ...run, stopping: true }), true);
assert.equal(isStopping({ ...run, phase: 'final_check' }), true);
// an older server reports neither: only the click counts
assert.equal(isStopping({ state: 'running', iteration: 3 }), false);
// once the solve has ended nothing is stopping, whatever was clicked
assert.equal(isStopping({ ...stoppedNow, stopping: true }, true), false);
assert.equal(isStopping(null, true), false);

// the bar's last word; the gap is in the chips
assert.equal(endedLabel(stoppedNow, '0:42'), 'stopped · iter 647 · 0:42');
assert.equal(endedLabel(done, '3:10'), 'done · Target gap reached · 3:10');
assert.equal(endedLabel({ state: 'done', stop_reason: 'iteration_limit', iteration: 3000 }, '9:00'),
  'done · Iteration limit reached · target not reached · 9:00');
console.log('preflop status chips: ok');
