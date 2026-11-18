// Preflop Lab: how much memory a game needs and where it will be solved,
// in plain words. The server works the numbers out (`plan` on the estimate,
// build, load, session and status replies); this file only words them.
//
// Sizes are shown in the GB that Windows and a card's box use (1 GB =
// 1024 MB), so "32 GB card" and "128 GB of RAM" compare directly.

import { RESTART_TIP } from './version.js';

const MB_PER_GB = 1024 * 1024 * 1024 / 1e6; // the server counts 1 MB = 1,000,000 bytes
// the tree outside the solver's tables, as the server counts it
const TREE_BYTES_PER_NODE = 400;
/** The third line when the running server cannot say where the game solves. */
export const UNKNOWN_ENGINE = 'Solves on: not known \u2014 restart GTOpen to finish updating it';

/** A size for people: "18.8 GB", "132 GB", or "350 MB" under a gigabyte. */
export function sizeText(mb) {
  const gb = mb / MB_PER_GB;
  if (gb >= 99.95) return `${gb.toFixed(0)} GB`;
  if (gb >= 0.95) return `${gb.toFixed(1)} GB`;
  return `${Math.max(1, Math.round(mb / (MB_PER_GB / 1024)))} MB`;
}

// what the card keeps free for itself and the desktop, as the server counts it
const CARD_MARGIN_MB = 512;

/** The card's side of a plan: 'fits' | 'too_big' (even for an empty card) |
 *  'busy' (too little free right now) | 'none' | 'off' | 'unsupported'.
 *  A server from before `card` is read from the rest of its plan. */
export function cardState(plan) {
  if (plan.card) return plan.card;
  if (plan.engine === 'gpu') return 'fits';
  if (!(plan.gpu_total_mb > 0)) {
    return /switched off/.test(plan.reason) ? 'off' : /no graphics card support/.test(plan.reason) ? 'unsupported' : 'none';
  }
  return /right now/.test(plan.reason) ? 'busy' : 'too_big';
}

/** The graphics card's own line: what the game needs there against what the
 *  card has, kept apart from the RAM line so the two are never read as one. */
export function cardText(plan) {
  const need = sizeText(plan.gpu_need_mb);
  const limit = plan.gpu_limit_mb ?? Math.max(0, plan.gpu_total_mb - CARD_MARGIN_MB);
  switch (cardState(plan)) {
    case 'fits': return `Graphics card: needs ${need}, ${sizeText(plan.gpu_free_mb)} free \u2014 fits\u00a0\u2713`;
    case 'too_big': return Number.isFinite(plan.gpu_need_mb)
      ? `Graphics card: needs ${need}, has ${sizeText(limit)} \u2014 too big\u00a0\u2717`
      : 'Graphics card: far too big for the card\u00a0\u2717';
    case 'busy': return `Graphics card: needs ${need}, only ${sizeText(plan.gpu_free_mb)} free now \u2014 no room\u00a0\u2717`;
    case 'off': return 'Graphics card: switched off for GTOpen (SOLVER_GPU=0)';
    case 'unsupported': return 'Graphics card: this copy of GTOpen cannot use one';
    default: return 'Graphics card: no NVIDIA card found';
  }
}

/** A game too big for the card's normal solve that the card still takes a
 *  part at a time (a server from before the mode never says so). */
export function largeGame(plan) {
  return plan.engine === 'gpu' && plan.gpu_mode === 'large';
}

/** Where the next solve will run. The card's line above says why. */
export function engineText(plan) {
  if (plan.engine !== 'gpu') return 'Solves on: CPU (processor), slower';
  return largeGame(plan) ? 'Solves on: GPU (graphics card), large-game mode' : 'Solves on: GPU (graphics card)';
}

/** The engine chip until a solve reports its own engine: the plan before
 *  one, and the first moments of one while the card is being set up. */
export function planChip(plan, running = false) {
  if (plan.engine !== 'gpu') {
    return { label: 'CPU', tip: `${running ? 'Solving' : 'The next solve will run'} on the processor (CPU): ${plan.reason}.` };
  }
  if (running) return { label: 'GPU\u2026', tip: 'Getting the graphics card (GPU) ready.' };
  return largeGame(plan)
    ? { label: 'GPU', tip: 'The next solve will run on the graphics card (GPU), in large-game mode.' }
    : { label: 'GPU', tip: 'The next solve will run on the graphics card (GPU).' };
}

/**
 * The size lines of the game on the form, from an estimate reply: the game
 * tree, RAM, the graphics card and where it solves, one fact a line.
 * Returns the lines, the "?" popup text and the state of the RAM line
 * ('ok' | 'warn' | 'bad').
 */
export function estimateView(e) {
  // A server from before the plan (pulled but not restarted) sends only the
  // tree and its tables: show those, and say what is missing and why.
  const plan = e.plan || { engine: null, ram_mb: e.arena_mb + e.nodes * TREE_BYTES_PER_NODE / 1e6 };
  const nodes = `${e.truncated ? 'more than ' : ''}${(+e.nodes).toLocaleString()}`;
  const borderline = e.ok && (e.nodes > 0.9 * e.limit_nodes || e.arena_mb > 0.9 * e.limit_arena_mb);
  const state = !e.ok ? 'bad' : borderline ? 'warn' : 'ok';
  // the mark stays on the line with its word
  const verdict = { ok: 'fits\u00a0\u2713', warn: 'only just fits\u00a0\u26a0', bad: 'too big for this computer right now\u00a0\u2717' }[state];
  // the RAM limit in the same terms as the figure shown
  const limit = e.arena_mb > 0 ? e.limit_arena_mb * (plan.ram_mb / e.arena_mb) : e.limit_arena_mb;
  const lines = [
    `Game tree: ${nodes} nodes`,
    `RAM: needs ${e.truncated ? 'more than' : 'about'} ${sizeText(plan.ram_mb)} \u2014 ${verdict}`,
  ];
  if (e.ok && plan.engine) lines.push(cardText(plan), engineText(plan));
  else if (e.ok) lines.push(UNKNOWN_ENGINE);
  const smaller = 'fewer sizes, fewer raises, no limps or no all-in option';
  const card = plan.engine ? cardState(plan) : null;
  const tip = !plan.engine ? RESTART_TIP : [
    `RAM is this computer's normal memory; every game has to fit there. Right now it can take ` +
      `a game like this up to about ${sizeText(limit)}.`,
    `A graphics card (GPU) solves much faster, but the game has to fit in the card's free memory too. ` +
      `It needs more there than in RAM: the card works on the whole game at once, so besides the ` +
      `solver's tables it holds a range for every spot and a value for every ending. ` +
      `A game too big for that can still solve on the card in large-game mode, a part of the game ` +
      `at a time: same answer, with more steps for the card to run. ` +
      `When even that does not fit, the game solves on the processor (CPU): same answer, slower.`,
    plan.engine && largeGame(plan)
      ? 'This game is in large-game mode: it is too big for the card all at once, so the card takes it a part at a time.' : '',
    state === 'warn' ? 'Only just fits: the build may still be refused if memory gets tighter.' : '',
    state === 'bad' ? `To make the game smaller: ${smaller}.` : '',
    e.ok && card === 'too_big' ? `To fit the card, make the game smaller: ${smaller}.` : '',
    e.ok && card === 'busy' ? 'To fit the card, close whatever else is using it, or make the game smaller.' : '',
  ].filter(Boolean).join(' ');
  return { lines, tip, state };
}
