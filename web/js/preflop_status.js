// Preflop Lab: the chips under the SOLVE button. Each fact shows once.
// A running solve's iteration, time and gap are in the progress bar; a game's
// size, memory and planned engine are in the size line above BUILD GAME; the
// iteration on screen during a solve is in the preview banner. The chips add
// only what none of those say: how a finished solve ended and its gap, and
// the engine while a solve runs or when it is not the one the size line names.
// The progress bar's own wording for a running, stopping and ended solve is
// here too.
import { publishedIteration, solveCompletionLabel } from './preflop_preview.js';
import { planChip } from './preflop_memory.js';

const TARGET = '0.0050';

/** True from the STOP click until the solve has ended. `requested`: this page
 *  sent the STOP; the server says so too (`stopping`), for a page that did not. */
export function isStopping(st, requested = false) {
  return st?.state === 'running' && (requested || st.stopping === true || st.phase === 'final_check');
}

/** The progress bar's label while a solve runs. A stopping solve says so until
 *  it has ended: it finishes with one last accuracy check, which takes a moment. */
export function runningLabel(st, { clock, shown = 0, earlyPreviews = true, stopping = false } = {}) {
  const head = `iter ${st.iteration} · ${clock}`;
  if (stopping) {
    const checking = st.phase === 'final_check' || st.phase === 'measuring';
    return `stopping · ${head}${checking ? ' · checking final accuracy…' : ''}`;
  }
  if (st.phase === 'publishing') return `solving · ${head} · publishing preview…`;
  if (st.phase === 'measuring') return `solving · ${head} · measuring accuracy…`;
  if (st.gap_total > 0) return `solving · ${head} · gap ${st.gap_total.toFixed(4)} \u2192 ${TARGET}`;
  const waiting = shown >= 2 ? `preview at ${shown}; accuracy every 50 iter`
    : earlyPreviews ? 'preparing first learned preview' : 'first strategy at accuracy checkpoint';
  return `solving · ${head} · ${waiting}`;
}

/** The progress bar's last label when a run ends without an error. The gap is in the chips. */
export function endedLabel(st, clock) {
  if (st.stop_reason === 'stopped') return `stopped · iter ${st.iteration} · ${clock}`;
  return `done · ${solveCompletionLabel(st)} · ${clock}`;
}

/** The engine chip {label, tip}, or null when it would repeat the size line
 *  (`formEngine`: the engine that line names, 'gpu' | 'cpu' | null). */
export function engineChip(st, formEngine = null) {
  const running = st.state === 'running';
  if (st.gpu) {
    if (!running && formEngine === 'gpu') return null;
    return { label: '⚡ GPU', tip: running ? 'Solving on the GPU.' : 'Solved on the GPU.' };
  }
  if (!running && formEngine === 'cpu') return null;
  // a solve that fell back to the CPU says why
  if (st.gpu_note) return { label: 'CPU', tip: st.gpu_note };
  if (!st.plan) return running ? { label: 'CPU', tip: 'Solving on the CPU.' } : null;
  if (!running && st.plan.engine === formEngine) return null;
  return planChip(st.plan, running);
}

/** The chips for a status reply: [{label, tip}]. `positions` names the seats
 *  for the gap chip's tip. */
export function statusChips(st, { positions = [], formEngine = null } = {}) {
  const chips = [];
  if (st.state !== 'running') {
    const iteration = st.iteration || 0;
    // stopped by hand, before the target (a crash or a loaded game is not that)
    const stoppedEarly = st.state === 'stopped' && st.stop_reason === 'stopped';
    if (iteration > 0) {
      chips.push({
        label: `${st.state} · iter ${iteration}`,
        tip: `${solveCompletionLabel(st)}. The iteration count carries over resumes and loads.`,
      });
    }
    if (st.gaps && st.gaps.length) {
      const measured = st.accuracy_iteration;
      const stale = measured != null && measured !== iteration;
      chips.push({
        label: `gap ${st.gap_total.toFixed(4)} → ${TARGET}` + (stale ? ` at iter ${measured}` : ''),
        tip: (stale ? `Measured at iteration ${measured}; the strategy shown is from iteration ${iteration}. `
          : stoppedEarly ? `Measured when the solve stopped, on the strategy shown. The target is ${TARGET}. ` : '') +
          'Best-response gap: how much each seat could still gain by deviating (bb). Only seats still learning converge; ' +
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
