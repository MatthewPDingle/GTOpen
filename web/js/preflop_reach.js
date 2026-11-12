// How far a clicked line can be trusted.
//
// The solver works on a spot in proportion to how often hands reach it, so a line the solution
// (almost) never plays is not solved: the ranges shown there are not a strategy. Thresholds are
// measured, not guessed: on two 2,000-iteration solves of one 6-max game (10,779 spots on 20,000
// sampled lines) action frequencies agree to about a point while a line comes up in 1 hand in
// 10,000 or more, drift apart below that, and below 1 in a million a quarter or more of the spots
// differ by over 10 points (more than half below 1 in 100 million).

/** A taken action below this share of the arriving range is one the solution has all but dropped. */
export const RARE_STEP = 1e-3;
/** A line that comes up less often than this is rough. */
export const SELDOM_LINE = 1e-4;
/** A line that comes up less often than this is not solved. */
export const UNSOLVED_LINE = 1e-6;

/** A frequency for a ribbon chip: tells "rare" from "never" where a rounded 0% cannot. */
export function frequencyText(freq) {
  if (!(freq > 0)) return '0%';
  if (freq < RARE_STEP) return '<0.1%';
  if (freq < 0.00995) return `${(freq * 100).toFixed(1)}%`;
  return `${(freq * 100).toFixed(0)}%`;
}

/** A frequency with enough digits to read a rare action (tooltips and notes). */
export function frequencyDetail(freq) {
  if (!(freq > 0)) return '0%';
  if (freq < 1e-6) return 'under 0.0001%';
  if (freq < RARE_STEP) return `${Number((freq * 100).toPrecision(1)).toLocaleString('en-US', { maximumFractionDigits: 6 })}%`;
  return `${(freq * 100).toFixed(freq < 0.01 ? 2 : 1)}%`;
}

/** "25,000", "3.5 million", "1.2 billion": the N of "about once in N hands". */
export function oneIn(chance) {
  if (!(chance > 0)) return null;
  const n = Number((1 / chance).toPrecision(2));
  if (n < 2) return null;
  const short = x => String(Number(x.toPrecision(2)));
  if (n >= 1e12) return 'more than a trillion';
  if (n >= 1e9) return `${short(n / 1e9)} billion`;
  if (n >= 1e6) return `${short(n / 1e6)} million`;
  return n.toLocaleString('en-US');
}

/** The actions taken along a node history: [{index, pos, label, freq, chance}], chance AFTER the step. */
export function lineSteps(history) {
  const steps = [];
  let chance = 1;
  (history || []).forEach((h, index) => {
    const a = h?.chosen != null ? h.actions?.[h.chosen] : null;
    if (!a) return;
    const freq = Number.isFinite(a.freq) ? Math.max(0, a.freq) : 0;
    chance *= freq;
    steps.push({ index, pos: h.actor_pos, label: a.label, freq, chance });
  });
  return steps;
}

function level(steps, chance) {
  if (!steps.length) return 'ok';
  if (steps.some(s => s.freq < RARE_STEP) || chance < UNSOLVED_LINE) return 'unsolved';
  return chance < SELDOM_LINE ? 'seldom' : 'ok';
}

/**
 * How solved the viewed spot is: {level: 'ok' | 'seldom' | 'unsolved', chance, dropped, rarest}.
 * `dropped` is the first step the solution has all but given up; `rarest` the least likely step.
 */
export function lineStatus(view) {
  const steps = lineSteps(view?.history);
  const product = steps.length ? steps[steps.length - 1].chance : 1;
  const chance = Number.isFinite(view?.branch_probability) ? view.branch_probability : product;
  return {
    level: level(steps, chance),
    chance,
    dropped: steps.find(s => s.freq < RARE_STEP) || null,
    rarest: steps.reduce((least, s) => (!least || s.freq < least.freq ? s : least), null),
  };
}

/** Per ribbon segment: the level of the spot it shows, from the steps taken before it. */
export function segmentLevels(history) {
  const steps = lineSteps(history);
  return (history || []).map((_, index) => {
    const before = steps.filter(s => s.index < index);
    return level(before, before.length ? before[before.length - 1].chance : 1);
  });
}

const WORK = 'The solver works on a spot in proportion to how often hands reach it';
const NOT_STRATEGY = 'The ranges below are not a strategy: two solves of this game can disagree completely here.';

/** The note above the grid, in plain words: {level, title, text, fix} or null when the spot is solved. */
export function lineNote(status) {
  if (!status || status.level === 'ok') return null;
  const n = oneIn(status.chance);
  const often = n ? `about once in ${n} hands` : 'almost never';
  const step = s => `${s.pos} ${s.label}`;
  if (status.level === 'seldom') {
    const rarest = status.rarest ? ` (rarest step: ${step(status.rarest)}, ${frequencyDetail(status.rarest.freq)})` : '';
    return {
      level: 'seldom',
      title: 'Seldom played',
      text: `This line comes up ${often}${rarest}. ${WORK}, so read these ranges as rough.`,
      fix: '',
    };
  }
  if (status.dropped) {
    const d = status.dropped;
    return {
      level: 'unsolved',
      title: 'Not solved from here on',
      text: `${d.pos} almost never takes ${d.label} here (${frequencyDetail(d.freq)} of the time), so this line is not part of the solution. ` +
        `${WORK}, and it has done almost no work behind that action. ${NOT_STRATEGY}`,
      fix: `To study this line, give ${d.pos} a player model or a lock that takes ${d.label}, then solve again.`,
    };
  }
  const rarest = status.rarest ? ` (rarest step: ${step(status.rarest)}, ${frequencyDetail(status.rarest.freq)})` : '';
  return {
    level: 'unsolved',
    title: 'Not solved here',
    text: `This exact line comes up ${often}${rarest}. ${WORK}, and it has done almost no work here. ${NOT_STRATEGY}`,
    fix: 'To study this line, give the seats on it player models or locks that take these actions, then solve again.',
  };
}
