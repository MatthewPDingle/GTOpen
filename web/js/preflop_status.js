// Preflop Lab: the chips under the SOLVE button. Each fact shows once.
// A running solve's iteration, time and gap are in the progress bar; a game's
// size, memory and planned engine are in the size line above BUILD GAME; the
// iteration on screen during a solve is in the preview banner. The chips add
// only what none of those say: how a finished solve ended and its gap, and
// the engine while a solve runs or when it is not the one the size line names.
import { publishedIteration, solveCompletionLabel } from './preflop_preview.js';
import { planChip } from './preflop_memory.js';

const TARGET = '0.0050';

/** The engine chip {label, tip}, or null when it would repeat the size line
 *  (`formEngine`: the engine that line names, 'gpu' | 'cpu' | null). */
export function engineChip(st, formEngine = null) {
  const running = st.state === 'running';
  if (st.gpu) {
    if (!running && formEngine === 'gpu') return null;
    return { label: '⚡ GPU', tip: running ? 'Solving on the graphics card (GPU).' : 'Solved on the graphics card (GPU).' };
  }
  if (!running && formEngine === 'cpu') return null;
  // a solve that fell back to the processor says why
  if (st.gpu_note) return { label: 'CPU', tip: st.gpu_note };
  if (!st.plan) return running ? { label: 'CPU', tip: 'Solving on the processor (CPU).' } : null;
  if (!running && st.plan.engine === formEngine) return null;
  return planChip(st.plan, running);
}

/** The chips for a status reply: [{label, tip}]. `positions` names the seats
 *  for the gap chip's tip. */
export function statusChips(st, { positions = [], formEngine = null } = {}) {
  const chips = [];
  if (st.state !== 'running') {
    const iteration = st.iteration || 0;
    if (iteration > 0) {
      chips.push({
        label: `${st.state} · iter ${iteration}`,
        tip: `${solveCompletionLabel(st)}. The iteration count carries over resumes and loads.`,
      });
    }
    if (st.gaps && st.gaps.length) {
      const measured = st.accuracy_iteration;
      chips.push({
        label: `gap ${st.gap_total.toFixed(4)} → ${TARGET}` +
          (measured != null && measured !== iteration ? ` at iter ${measured}` : ''),
        tip: 'Best-response gap: how much each seat could still gain by deviating (bb). Only seats still learning converge; ' +
          'a frozen or ruled seat’s gap is its BLEED against its pinned strategy. ' +
          st.gaps.map((g, i) => `${positions[i] || i}: ${g.toFixed(4)}`).join(' · '),
      });
    }
    const shown = publishedIteration(st);
    if (iteration > 0 && shown !== iteration) {
      chips.push({ label: `showing iter ${shown}`, tip: 'The strategy on screen is the snapshot from this iteration.' });
    }
  }
  const engine = engineChip(st, formEngine);
  if (engine) chips.push(engine);
  return chips;
}
