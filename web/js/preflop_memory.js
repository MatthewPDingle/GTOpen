// Preflop Lab: how much memory a game needs and where it will be solved,
// in plain words. The server works the numbers out (`plan` on the estimate,
// build, load, session and status replies); this file only words them.
//
// Sizes are shown in the GB that Windows and a card's box use (1 GB =
// 1024 MB), so "32 GB card" and "128 GB of RAM" compare directly.

const MB_PER_GB = 1024 * 1024 * 1024 / 1e6; // the server counts 1 MB = 1,000,000 bytes

/** A size for people: "18.8 GB", "132 GB", or "350 MB" under a gigabyte. */
export function sizeText(mb) {
  const gb = mb / MB_PER_GB;
  if (gb >= 99.95) return `${gb.toFixed(0)} GB`;
  if (gb >= 0.95) return `${gb.toFixed(1)} GB`;
  return `${Math.max(1, Math.round(mb / (MB_PER_GB / 1024)))} MB`;
}

/** "about 18.8 GB of RAM", plus the graphics memory when it solves there. */
export function memoryText(plan) {
  const ram = `about ${sizeText(plan.ram_mb)} of RAM`;
  return plan.engine === 'gpu'
    ? `${ram} and ${sizeText(plan.gpu_need_mb)} of graphics memory`
    : ram;
}

/** Where the next solve will run, and why when that is the processor. */
export function engineText(plan) {
  return plan.engine === 'gpu'
    ? 'Solves on: GPU (graphics card)'
    : `Solves on: CPU (processor), slower — ${plan.reason}`;
}

/** The engine chip until a solve reports its own engine: the plan before
 *  one, and the first moments of one while the card is being set up. */
export function planChip(plan, running = false) {
  if (plan.engine !== 'gpu') {
    return { label: 'CPU', tip: `${running ? 'Solving' : 'The next solve will run'} on the processor (CPU): ${plan.reason}.` };
  }
  return running
    ? { label: 'GPU\u2026', tip: 'Getting the graphics card (GPU) ready.' }
    : { label: 'GPU', tip: 'The next solve will run on the graphics card (GPU).' };
}

/**
 * The size line of the game on the form, from an estimate reply.
 * Returns the two lines to show, the "?" popup text and the line's state
 * ('ok' | 'warn' | 'bad').
 */
export function estimateView(e) {
  const plan = e.plan;
  const nodes = `${e.truncated ? 'more than ' : ''}${(+e.nodes).toLocaleString()}`;
  const borderline = e.ok && (e.nodes > 0.9 * e.limit_nodes || e.arena_mb > 0.9 * e.limit_arena_mb);
  const state = !e.ok ? 'bad' : borderline ? 'warn' : 'ok';
  // the mark stays on the line with its word
  const verdict = { ok: 'fits ✓', warn: 'only just fits ⚠', bad: 'too big for this computer right now ✗' }[state];
  // the RAM limit in the same terms as the figure shown
  const limit = e.arena_mb > 0 ? e.limit_arena_mb * (plan.ram_mb / e.arena_mb) : e.limit_arena_mb;
  const lines = [
    `Game tree: ${nodes} nodes`,
    `Memory: ${e.truncated ? `more than ${sizeText(plan.ram_mb)} of RAM` : memoryText(plan)} — ${verdict}`,
  ];
  if (e.ok) lines.push(engineText(plan));
  const smaller = 'fewer sizes, fewer raises, no limps or no all-in option';
  const tip = [
    `RAM is this computer's normal memory; every game has to fit there. Right now it can take ` +
      `a game like this up to about ${sizeText(limit)}.`,
    `A graphics card (GPU) solves much faster, but only if the game fits in the card's free ` +
      `memory, and it takes more room there than in RAM. If not, it solves on the processor ` +
      `(CPU): same answer, slower.`,
    state === 'warn' ? 'Only just fits: the build may still be refused if memory gets tighter.' : '',
    state === 'bad' ? `To make the game smaller: ${smaller}.` : '',
    e.ok && plan.engine === 'cpu' && plan.gpu_need_mb > 0 && plan.gpu_free_mb > 0
      ? `To fit the card, make the game smaller: ${smaller}.`
      : '',
  ].filter(Boolean).join(' ');
  return { lines, tip, state };
}
