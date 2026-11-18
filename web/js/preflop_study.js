// How to study a line the solution never plays: the steps a user takes by hand.
//
// The solver cannot work out what follows an action a seat never takes. The way in is to make that
// seat a player model (a fixed player type) that does take it, and solve the rest of the table
// against that player. This module turns the step that led off the solution into those steps, in
// the app's own words: which tab of the model editor holds the spot, which brush paints the action
// and which number moves it. It only writes the words; the user does the steps.

import { lineStatus } from './preflop_reach.js';

/** The model editor's tabs, in the engine's order of situations. */
export const TABS = ['UNOPENED', 'VS LIMPS', 'VS RAISE', 'SQUEEZE', 'VS 3-BET+'];

/**
 * The spot a history step is taken in, counted the way the engine sorts spots into a player
 * model's tabs: {bucket, tab, entered, sizeRank, limpers, freeCheck}. `entered` says how the acting
 * seat already put chips in ('limped' | 'called' | 'raised' | null); `sizeRank` places a taken raise
 * among the node's raise sizes ('only' | 'smallest' | 'largest' | 'middle' | null); `limpers` and
 * `freeCheck` pick the VS LIMPS tab's "Facing" entry (1, 2 or 3 = three or more).
 */
export function stepSituation(history, index) {
  const node = history?.[index];
  if (!node) return null;
  let raises = 0, limpers = 0, callers = 0, entered = null;
  for (const h of history.slice(0, index)) {
    const a = h?.chosen != null ? h.actions?.[h.chosen] : null;
    if (!a) continue;
    const own = h.actor_pos === node.actor_pos;
    if (a.kind === 'call') {
      if (raises === 0) limpers += 1; else callers += 1;
      if (own) entered = raises === 0 ? 'limped' : 'called';
    } else if (a.kind === 'raise' || a.kind === 'jam') {
      raises += 1;
      callers = 0; // a raise starts a fresh calling round
      if (own) entered = 'raised';
    }
  }
  const bucket = raises === 0 ? (limpers === 0 ? 0 : 1) : raises === 1 ? (callers === 0 ? 2 : 3) : 4;
  const taken = node.chosen != null ? node.actions?.[node.chosen] : null;
  const sizes = (node.actions || []).filter(a => a.kind === 'raise'); // listed smallest first
  const at = taken ? sizes.indexOf(taken) : -1;
  const sizeRank = at < 0 ? null : sizes.length === 1 ? 'only'
    : at === 0 ? 'smallest' : at === sizes.length - 1 ? 'largest' : 'middle';
  return { bucket, tab: TABS[bucket], entered, sizeRank,
    limpers: Math.min(3, limpers), freeCheck: (node.actions || []).some(a => a.kind === 'check') };
}

/**
 * The step to change so the viewed line gets solved, or null when the line is solved (or only
 * seldom played): the action that led off the solution, else the line's rarest step.
 * {index, pos, label, kind, freq, single, bucket, tab, entered, sizeRank, limpers, freeCheck}
 */
export function studyTarget(view) {
  const status = lineStatus(view);
  if (status.level !== 'unsolved') return null;
  const step = status.dropped || status.rarest;
  const node = step ? view.history?.[step.index] : null;
  const action = node?.actions?.[node.chosen];
  if (!action) return null;
  return { index: step.index, pos: step.pos, label: step.label, kind: action.kind, freq: step.freq,
    single: !!status.dropped, ...stepSituation(view.history, step.index) };
}

const BRUSH = { fold: 'FOLD', call: 'CALL', check: 'CHECK', raise: 'RAISE', jam: 'JAM' };
const COLOUR = { fold: 'dark', call: 'green', check: 'green', raise: 'red', jam: 'purple' };
// generated player types that take each kind of action often
const EXAMPLES = {
  fold: ['Nit / OMC'],
  call: ['Whale (loose-passive)', 'Calling station'],
  check: ['Whale (loose-passive)', 'Calling station'],
  raise: ['LAG', 'Maniac'],
  jam: ['LAG', 'Maniac'],
};

/** What the hands painted with this action do, as a verb: "the green hands limp". */
function verb(target) {
  if (target.kind === 'call') return target.bucket >= 2 ? 'call' : /^complete/i.test(target.label) ? 'complete' : 'limp';
  return { fold: 'fold', check: 'check', raise: 'raise', jam: 'go all-in' }[target.kind] || 'take this action';
}

/** The one number in the editor that moves this action, and which way: ['raise' | 'lower', field name] or null. */
function statHint(target) {
  const { bucket, kind, entered } = target;
  const folds = bucket === 4 ? 'fold to 3-bet+ %' : bucket === 3 ? 'fold vs squeeze %'
    : bucket === 2 ? (entered === 'limped' ? 'fold vs raise after limping %' : 'fold vs raise %') : null;
  if (kind === 'fold') return folds ? ['raise', folds] : null;
  if (kind === 'jam' || kind === 'check') return null;
  if (bucket === 0) return ['raise', kind === 'call' ? 'open-limp %' : 'open-raise %'];
  if (bucket === 1) return ['raise', kind === 'call' ? 'limp behind %' : 'iso-raise vs limpers %'];
  if (kind === 'call') return ['lower', folds];
  if (entered) return ['lower', folds];
  return bucket === 2 ? ['raise', '3-bet %'] : bucket === 3 ? ['raise', 'squeeze %'] : ['lower', folds];
}

/** A raise is one of several sizes: which size a player model's raises use, in words. */
function sizeNote(target) {
  if (target.kind !== 'raise' || !target.sizeRank || target.sizeRank === 'only') return '';
  if (target.sizeRank === 'middle') {
    return ' A player type raises to the smallest or the largest size only, so a middle size like this one cannot be studied this way yet.';
  }
  return ` Its raises use one size: set "fallback raise size" to ${target.sizeRank === 'smallest' ? 'min' : 'max'} so they use this one.`;
}

/** The first time a seat acts its spot is one tab and can be painted hand by hand. Once it has
 *  chips in, and in re-raised pots, the engine blends several policies: only the numbers help. */
const paintable = target => !target.entered && target.bucket < 4;

/** The tab that holds the spot, with the VS LIMPS "Facing" entry when there is one to pick. */
function tabName(target) {
  if (target.bucket !== 1) return `${target.tab} tab`;
  const n = target.limpers >= 3 ? '3+ limpers' : `${target.limpers} limper${target.limpers === 1 ? '' : 's'}`;
  return `${target.tab} tab (Facing: ${n})`;
}

/** The line shown inside the model editor while it edits the seat this line needs: where to click. */
export function studyEditorHint(target) {
  if (!target) return '';
  const stat = statHint(target);
  const head = `To study ${target.pos}'s ${target.label}: `;
  if (!paintable(target)) {
    return head + 'this spot comes later in the hand, where single hands cannot be set.' +
      (stat ? ` ${stat[0] === 'raise' ? 'Raise' : 'Lower'} "${stat[1]}" to make ${target.pos} ${verb(target)} more.` : '');
  }
  return head + `${tabName(target)}, ${BRUSH[target.kind]} brush, then click the hands that should ${verb(target)}` +
    (stat ? `. Or ${stat[0]} "${stat[1]}".` : '.') + sizeNote(target);
}

/**
 * The steps, in plain words.
 * `seat` is the acting seat today: {state: 'solver' | 'frozen' | 'picked' | 'model', label}
 * ('picked' = a player type is chosen but the game has not been solved with it; 'model' = the game
 * already plays that type and it still never takes the action). `types` lists the player types on
 * offer, `ui` the labels the page shows for the model step and the solve button.
 * Returns {why, steps: [{key: 'model' | 'ranges' | 'solve', text, done}], after}.
 */
export function studyGuide(target, seat = { state: 'solver' }, types = [], ui = {}) {
  if (!target) return null;
  const { pos, label, kind } = target;
  const where = ui.modelStep || '4 · MODEL';
  const solve = ui.solveLabel || 'RE-SOLVE';
  const example = (EXAMPLES[kind] || []).find(name => types.includes(name));
  const does = { fold: 'folds here', call: target.bucket >= 2 ? 'calls here' : 'limps', check: 'checks here',
    raise: 'raises here', jam: 'goes all-in here' }[kind] || 'takes this action';

  const never = target.freq > 0 ? 'almost never' : 'never';
  const why = target.single
    ? `${pos} ${never} takes ${label}, so the solver did no real work on what comes after it. ` +
      `To study this line, ${seat.state === 'model' ? `${pos}'s player type has to take it` : `make ${pos} a player who does take it`}. ` +
      `The solver then works out how everyone else should play against that player.`
    : `No single step is to blame here: the whole line is too rare for the solver to have worked on it. ` +
      `Start with its rarest step, ${pos}'s ${label}: make ${pos} a player who takes it. The solver then works out how everyone else should play against that player.`;

  let model;
  if (seat.state === 'picked') {
    model = { text: `${pos} is set to "${seat.label}".`, done: true };
  } else if (seat.state === 'model') {
    model = { text: `${pos} plays as "${seat.label}", and that player ${never} takes ${label}. ` +
      `Change its hands in step 2, or pick a different player type in ${where} on the left.`, done: false };
  } else {
    model = { text: `In ${where} on the left, change ${pos} from "${seat.state === 'frozen' ? 'Frozen' : 'Solver'}" ` +
      `to a player type that ${does}${example ? `, for example "${example}"` : ''}.`, done: false };
  }

  const exact = paintable(target);
  const stat = statHint(target);
  let ranges;
  if (exact) {
    const change = kind === 'fold' ? 'To add more' : 'To change them';
    ranges = `Click "edit" beside ${pos}. On the ${tabName(target)}, the ${COLOUR[kind]} hands ${verb(target)}. ` +
      `${change}, pick the ${BRUSH[kind]} brush and click hands${stat ? `, or ${stat[0]} "${stat[1]}"` : ''}.` + sizeNote(target);
  } else {
    ranges = `Click "edit" beside ${pos} to see how that player type plays. This spot comes later in the hand, where single hands cannot be set` +
      (stat ? `: ${stat[0]} "${stat[1]}" to make ${pos} ${verb(target)} more.` : '.');
  }

  return {
    why,
    steps: [
      { key: 'model', ...model },
      { key: 'ranges', text: ranges, done: false },
      { key: 'solve', done: false, text: `Press ${solve}. It starts over, so it takes about as long as the first solve. ` +
        `When it is done, ${pos}'s ${label} shows a real share in the strip above and this line is solved.` },
    ],
    after: `The result is how to play against that ${pos}, not the game where everyone plays perfectly. ` +
      `To go back, set ${pos} to "Solver" and press ${solve}. SAVE the game first to keep the solve you have now.`,
  };
}
