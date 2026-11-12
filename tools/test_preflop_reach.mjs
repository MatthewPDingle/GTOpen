import assert from 'node:assert/strict';
import { RARE_STEP, SELDOM_LINE, UNSOLVED_LINE, frequencyText, frequencyDetail, oneIn, lineSteps, lineStatus, segmentLevels, lineNote } from '../web/js/preflop_reach.js';

// One ribbon entry: the acting seat, its actions as [label, frequency], and the action taken (null = the spot viewed).
const node = (actor_pos, actions, chosen = null) => ({ kind: 'action', actor_pos, chosen,
  actions: actions.map(([label, freq]) => ({ label, kind: label.split(' ')[0].toLowerCase(), freq })) });
const view = (history, branch_probability) => ({ history, branch_probability });

// a rounded 0% no longer hides the difference between rare and never
assert.equal(frequencyText(0), '0%');
assert.equal(frequencyText(0.00004), '<0.1%');
assert.equal(frequencyText(0.003), '0.3%');
assert.equal(frequencyText(0.0099), '1.0%');
assert.equal(frequencyText(0.19), '19%');
assert.equal(frequencyText(NaN), '0%');
assert.equal(frequencyDetail(0), '0%');
assert.equal(frequencyDetail(0.00004), '0.004%');
assert.equal(frequencyDetail(3e-9), 'under 0.0001%');
assert.equal(frequencyDetail(0.003), '0.30%');
assert.equal(frequencyDetail(0.19), '19.0%');
assert.equal(oneIn(1), null);
assert.equal(oneIn(0), null);
assert.equal(oneIn(0.013), '77');
assert.equal(oneIn(4e-5), '25,000');
assert.equal(oneIn(3.5e-6), '290,000');
assert.equal(oneIn(1e-7), '10 million');
assert.equal(oneIn(2.9e-8), '34 million');
assert.equal(oneIn(8e-10), '1.3 billion');
assert.equal(oneIn(1e-15), 'more than a trillion');

// the line in the report: UTG limps (0.004%), HJ raises, CO 3-bets, BTN calls, SB to act
const utg = chosen => node('UTG', [['Fold', 0.81], ['Limp 1 bb', 0.00004], ['Raise 2.5x', 0.19], ['Raise 4x', 0.0002]], chosen);
const limped = [
  utg(1),
  node('HJ', [['Fold', 0.911], ['Limp 1 bb', 0.003], ['Raise 2.5x', 0.087]], 2),
  node('CO', [['Fold', 0.818], ['Call 2.5 bb', 0.106], ['3-bet 3x', 0.076]], 2),
  node('BTN', [['Fold', 0.291], ['Call 7.5 bb', 0.137], ['4-bet 3x', 0.572]], 1),
  node('SB', [['Fold', 0.259], ['Call 7.5 bb', 0.028], ['4-bet 3x', 0.713]]),
];
const steps = lineSteps(limped);
assert.deepEqual(steps.map(s => s.pos), ['UTG', 'HJ', 'CO', 'BTN']);
assert.deepEqual(steps.map(s => s.index), [0, 1, 2, 3]);
assert.ok(Math.abs(steps[3].chance - 0.00004 * 0.087 * 0.076 * 0.137) < 1e-15);

// the first spot behind the dropped limp is already not solved, whatever the line's chance
const afterLimp = lineStatus(view(limped.slice(0, 1).concat(node('HJ', [['Fold', 0.9], ['Raise 2.5x', 0.1]])), 0.00004));
assert.equal(afterLimp.level, 'unsolved');
assert.equal(afterLimp.dropped.pos, 'UTG');
assert.ok(afterLimp.chance > UNSOLVED_LINE && afterLimp.chance < SELDOM_LINE);
const deep = lineStatus(view(limped));
assert.equal(deep.level, 'unsolved');
assert.equal(deep.dropped.label, 'Limp 1 bb');
assert.equal(deep.rarest.label, 'Limp 1 bb');
const note = lineNote(deep);
assert.equal(note.level, 'unsolved');
assert.equal(note.title, 'Not solved from here on');
assert.match(note.text, /^UTG almost never takes Limp 1 bb here \(0\.004% of the time\), so this line is not part of the solution\./);
assert.match(note.text, /in proportion to how often hands reach it/);
assert.match(note.text, /not a strategy: two solves of this game can disagree completely here\.$/);
assert.equal(note.fix, 'To study this line, give UTG a player model or a lock that takes Limp 1 bb, then solve again.');

// a common line carries no note, and neither does the root
const common = [
  utg(2),
  node('HJ', [['Fold', 0.92], ['Call 2.5 bb', 0.02], ['3-bet 3x', 0.07]], 2),
  node('CO', [['Fold', 0.96], ['Call 7.5 bb', 0.002], ['4-bet 3x', 0.04]]),
];
assert.equal(lineStatus(view(common, 0.19 * 0.07)).level, 'ok');
assert.equal(lineNote(lineStatus(view(common, 0.19 * 0.07))), null);
assert.equal(lineStatus(view([utg(null)], 1)).level, 'ok');
assert.equal(lineStatus(view([utg(null)], 0)).level, 'ok'); // nothing taken yet
assert.equal(lineStatus(undefined).level, 'ok');
assert.equal(lineNote(null), null);

// no single dropped step: the line's chance decides, with the server's number when it sends one
const rare = (branch_probability) => view([
  node('UTG', [['Fold', 0.8], ['Raise 2.5x', 0.2]], 1),
  node('HJ', [['Fold', 0.9], ['3-bet 3x', 0.1]], 1),
  node('CO', [['Fold', 0.95], ['4-bet 3x', 0.05]], 1),
  node('BTN', [['Fold', 0.9], ['Call', 0.05], ['Jam', 0.05]], 1),
  node('SB', [['Fold', 0.6], ['Call', 0.4]]),
], branch_probability);
assert.equal(lineStatus(rare()).level, 'seldom'); // 0.2 * 0.1 * 0.05 * 0.05 = 5e-5
assert.ok(Math.abs(lineStatus(rare()).chance - 5e-5) < 1e-12);
const seldom = lineNote(lineStatus(rare()));
assert.equal(seldom.level, 'seldom');
assert.equal(seldom.title, 'Seldom played.'); // inline with its sentence: reads as two sentences when copied or spoken
assert.match(seldom.text, /^This line comes up about once in 20,000 hands \(rarest step: CO 4-bet 3x, 5\.0%\)\./);
assert.match(seldom.text, /read these ranges as rough\.$/);
assert.equal(seldom.fix, '');
assert.equal(lineStatus(rare(2e-4)).level, 'ok');
assert.equal(lineStatus(rare(SELDOM_LINE)).level, 'ok');
assert.equal(lineStatus(rare(UNSOLVED_LINE)).level, 'seldom');
const lost = lineStatus(rare(3e-7));
assert.equal(lost.level, 'unsolved');
assert.equal(lost.dropped, null);
const lostNote = lineNote(lost);
assert.equal(lostNote.title, 'Not solved here');
assert.match(lostNote.text, /^This exact line comes up about once in 3\.3 million hands \(rarest step: CO 4-bet 3x, 5\.0%\)\./);
assert.match(lostNote.fix, /player models or locks/);
// a step at exactly the limit is still part of the solution
assert.equal(lineStatus(view([node('UTG', [['Fold', 1 - RARE_STEP], ['Limp 1 bb', RARE_STEP]], 1), node('HJ', [['Fold', 1]])], RARE_STEP)).level, 'ok');
// an action with exactly zero frequency is a dropped step too
assert.equal(lineStatus(view([node('UTG', [['Fold', 1], ['Limp 1 bb', 0]], 1), node('HJ', [['Fold', 1]])], 0)).dropped.freq, 0);
assert.match(lineNote(lineStatus(view([node('UTG', [['Fold', 1], ['Limp 1 bb', 0]], 1), node('HJ', [['Fold', 1]])], 0))).text, /\(0% of the time\)/);

// the ribbon: every spot after the limp is marked, the limp's own spot is not
assert.deepEqual(segmentLevels(limped), ['ok', 'unsolved', 'unsolved', 'unsolved', 'unsolved']);
assert.deepEqual(segmentLevels(common), ['ok', 'ok', 'ok']);
assert.deepEqual(segmentLevels(rare().history), ['ok', 'ok', 'ok', 'ok', 'seldom']);
// a flop or hand-over entry is a spot like any other
assert.deepEqual(segmentLevels([utg(1), { kind: 'pot_share', actor_pos: '', actions: [], chosen: null }]), ['ok', 'unsolved']);
assert.deepEqual(segmentLevels(null), []);
console.log('preflop line reach, wording and ribbon mark tests passed');
