import assert from 'node:assert/strict';
import { TABS, stepSituation, studyTarget, studyGuide, studyEditorHint } from '../web/js/preflop_study.js';

// One ribbon entry: the acting seat, its actions as [label, kind, frequency], and the action taken (null = the spot viewed).
const node = (actor_pos, actions, chosen = null) => ({ kind: 'action', actor_pos, chosen,
  actions: actions.map(([label, kind, freq]) => ({ label, kind, freq })) });
const view = (history, branch_probability) => ({ history, branch_probability });
const TYPES = ['Whale (loose-passive)', 'Nit / OMC', 'Calling station', 'TAG', 'LAG', 'Maniac'];
const UI = { modelStep: '4 · MODEL', solveLabel: 'RE-SOLVE' };

// Pan's spot: 6-max, UTG limps under 0.1% of the time, HJ to act
const utg = chosen => node('UTG', [['Fold', 'fold', 0.82], ['Limp 1 bb', 'call', 0.00007], ['Raise 3x', 'raise', 0.18],
  ['Raise 5x', 'raise', 0.0004], ['All-in 150x', 'jam', 0.0002]], chosen);
const hj = chosen => node('HJ', [['Fold', 'fold', 0.89], ['Limp 1 bb', 'call', 0.02], ['Raise 3x', 'raise', 0.03], ['Raise 5x', 'raise', 0.06]], chosen);
const afterLimp = view([utg(1), hj()], 0.00007);

const limp = studyTarget(afterLimp);
assert.deepEqual([limp.pos, limp.label, limp.kind, limp.index, limp.single], ['UTG', 'Limp 1 bb', 'call', 0, true]);
assert.deepEqual([limp.bucket, limp.tab, limp.entered, limp.sizeRank], [0, 'UNOPENED', null, null]);

// a solved line and a seldom-played one have nothing to study
assert.equal(studyTarget(view([utg(2), hj()], 0.18)), null);
assert.equal(studyTarget(view([utg()], 1)), null);
assert.equal(studyTarget(undefined), null);

// the steps for the limp, seat still played by the solver
const guide = studyGuide(limp, { state: 'solver' }, TYPES, UI);
assert.match(guide.why, /^UTG almost never takes Limp 1 bb, so the solver did no real work on what comes after it\. To study this line, make UTG a player who does take it\./);
assert.deepEqual(guide.steps.map(s => s.key), ['model', 'ranges', 'solve']);
assert.equal(guide.steps[0].text, 'In 4 · MODEL on the left, change UTG from "Solver" to a player type that limps, for example "Whale (loose-passive)".');
assert.equal(guide.steps[1].text, 'Click "edit" beside UTG. On the UNOPENED tab, the green hands limp. To change them, pick the CALL brush and click hands, or raise "open-limp %".');
assert.equal(guide.steps[2].text, 'Press RE-SOLVE. It starts over, so it takes about as long as the first solve. When it is done, UTG\'s Limp 1 bb shows a real share in the strip above and this line is solved.');
assert.match(guide.after, /not the game where everyone plays perfectly\. To go back, set UTG to "Solver" and press RE-SOLVE\./);
assert.ok(guide.steps.every(s => !s.done));
// no lock anywhere: the Preflop Lab has no control for one
assert.doesNotMatch(JSON.stringify(guide), /\block\b/i);

// the first step follows the seat
assert.match(studyGuide(limp, { state: 'frozen' }, TYPES, UI).steps[0].text, /change UTG from "Frozen" to/);
const picked = studyGuide(limp, { state: 'picked', label: 'Whale (loose-passive)' }, TYPES, UI).steps[0];
assert.deepEqual(picked, { key: 'model', text: 'UTG is set to "Whale (loose-passive)".', done: true });
const stuck = studyGuide(limp, { state: 'model', label: 'Nit / OMC' }, TYPES, UI).steps[0];
assert.equal(stuck.done, false);
assert.match(stuck.text, /^UTG plays as "Nit \/ OMC", and that player almost never takes Limp 1 bb\. Change its hands in step 2/);
// an action the seat's player type never takes at all (the page shows no ranges there)
const zero = studyTarget(view([node('UTG', [['Fold', 'fold', 0.8], ['Limp 1 bb', 'call', 0], ['Raise 3x', 'raise', 0.2]], 1), hj()], 0));
const zeroGuide = studyGuide(zero, { state: 'model', label: 'TAG' }, TYPES, UI);
assert.match(zeroGuide.why, /^UTG never takes Limp 1 bb, so .* To study this line, UTG's player type has to take it\./);
assert.match(zeroGuide.steps[0].text, /^UTG plays as "TAG", and that player never takes Limp 1 bb\./);
// a removed player type is not offered; with none left there is no example
assert.match(studyGuide(limp, { state: 'solver' }, ['Calling station'], UI).steps[0].text, /for example "Calling station"\.$/);
assert.match(studyGuide(limp, { state: 'solver' }, [], UI).steps[0].text, /a player type that limps\.$/);
// the page's own labels are used
assert.match(studyGuide(limp, { state: 'solver' }, TYPES, { modelStep: '3 · MODEL', solveLabel: 'SOLVE' }).steps[2].text, /^Press SOLVE\./);

// the bigger of two open sizes: a player type raises one size, so the step says which setting picks it
const big = studyTarget(view([utg(3), hj()], 0.0004));
assert.deepEqual([big.kind, big.sizeRank, big.tab], ['raise', 'largest', 'UNOPENED']);
const bigSteps = studyGuide(big, { state: 'solver' }, TYPES, UI).steps;
assert.match(bigSteps[0].text, /a player type that raises here, for example "LAG"\.$/);
assert.match(bigSteps[1].text, /the red hands raise\. To change them, pick the RAISE brush and click hands, or raise "open-raise %"\. Its raises use one size: set "fallback raise size" to max so they use this one\.$/);
const three = node('UTG', [['Fold', 'fold', 0.8], ['Raise 2x', 'raise', 0.1], ['Raise 3x', 'raise', 0.00001], ['Raise 5x', 'raise', 0.1]], 2);
assert.equal(stepSituation([three, hj()], 0).sizeRank, 'middle');
assert.match(studyGuide(studyTarget(view([three, hj()], 0.00001)), { state: 'solver' }, TYPES, UI).steps[1].text, /a middle size like this one cannot be studied this way yet\.$/);
assert.equal(stepSituation([node('UTG', [['Fold', 'fold', 0.8], ['Raise 3x', 'raise', 0.2]], 1), hj()], 0).sizeRank, 'only');
assert.equal(stepSituation([node('UTG', [['Fold', 'fold', 0.8], ['Raise 2x', 'raise', 0.1], ['Raise 3x', 'raise', 0.1]], 1), hj()], 0).sizeRank, 'smallest');

// an all-in: painted with the JAM brush, no number moves it
const jam = studyTarget(view([utg(4), hj()], 0.0002));
assert.equal(studyGuide(jam, { state: 'solver' }, TYPES, UI).steps[1].text,
  'Click "edit" beside UTG. On the UNOPENED tab, the purple hands go all-in. To change them, pick the JAM brush and click hands.');

// the tabs follow the engine's sorting: limpers, one raise, raise and callers, re-raises
const co = (chosen, callFreq = 0.1) => node('CO', [['Fold', 'fold', 0.8], ['Call 3 bb', 'call', callFreq], ['3-bet 3x', 'raise', 0.1]], chosen);
const btn = chosen => node('BTN', [['Fold', 'fold', 0.8], ['Call 3 bb', 'call', 0.00002], ['3-bet 3x', 'raise', 0.2]], chosen);
assert.equal(stepSituation([utg(1), hj()], 1).tab, 'VS LIMPS');
assert.equal(stepSituation([utg(2), hj(0), co()], 2).tab, 'VS RAISE');
assert.equal(stepSituation([utg(2), hj(0), co(1), btn()], 3).tab, 'SQUEEZE');
assert.equal(stepSituation([utg(2), hj(0), co(2), btn()], 3).tab, 'VS 3-BET+');
assert.deepEqual(TABS, ['UNOPENED', 'VS LIMPS', 'VS RAISE', 'SQUEEZE', 'VS 3-BET+']);
assert.equal(stepSituation([utg(2)], 5), null);

// a cold call nobody makes
const cold = studyTarget(view([utg(2), hj(0), co(1, 0.00003), btn()], 0.000005));
assert.deepEqual([cold.pos, cold.kind, cold.tab, cold.entered], ['CO', 'call', 'VS RAISE', null]);
const coldSteps = studyGuide(cold, { state: 'solver' }, TYPES, UI).steps;
assert.match(coldSteps[0].text, /change CO from "Solver" to a player type that calls here, for example "Whale \(loose-passive\)"\.$/);
assert.match(coldSteps[1].text, /On the VS RAISE tab, the green hands call\. To change them, pick the CALL brush and click hands, or lower "fold vs raise %"\.$/);
// an overcall in the squeeze spot
const over = studyTarget(view([utg(2), hj(0), co(1), btn(1), node('SB', [['Fold', 'fold', 1]])], 0.0000004));
assert.match(studyGuide(over, { state: 'solver' }, TYPES, UI).steps[1].text, /On the SQUEEZE tab, .* or lower "fold vs squeeze %"\.$/);
// limping behind two limpers names the "Facing" entry
const behind = node('CO', [['Fold', 'fold', 0.9], ['Limp 1 bb', 'call', 0.00001], ['Raise 5x', 'raise', 0.1]], 1);
const limped = studyTarget(view([utg(1), hj(1), behind, btn()], 1e-9));
assert.equal(limped.pos, 'UTG'); // the first step that led off the solution is the one to fix
const second = { ...stepSituation([utg(1), hj(1), behind, btn()], 2), pos: 'CO', label: 'Limp 1 bb', kind: 'call', single: true };
assert.deepEqual([second.tab, second.limpers, second.freeCheck], ['VS LIMPS', 2, false]);
assert.match(studyGuide(second, { state: 'solver' }, TYPES, UI).steps[1].text, /On the VS LIMPS tab \(Facing: 2 limpers\), the green hands limp\. .* or raise "limp behind %"\.$/);

// a seat that already put chips in: no tab to paint, only the number that moves it
const utgBack = node('UTG', [['Fold', 'fold', 0.9], ['Call 4 bb', 'call', 0.00001], ['3-bet 3x', 'raise', 0.1]], 1);
const limpCall = { ...stepSituation([utg(1), hj(3), utgBack, hj()], 2), pos: 'UTG', label: 'Call 4 bb', kind: 'call', single: true };
assert.equal(limpCall.entered, 'limped');
assert.equal(studyGuide(limpCall, { state: 'solver' }, TYPES, UI).steps[1].text,
  'Click "edit" beside UTG to see how that player type plays. This spot comes later in the hand, where single hands cannot be set: lower "fold vs raise after limping %" to make UTG call more.');

// no single dropped step: start with the rarest one
const thin = view([
  node('UTG', [['Fold', 'fold', 0.98], ['Raise 3x', 'raise', 0.02]], 1),
  node('HJ', [['Fold', 'fold', 0.98], ['3-bet 3x', 'raise', 0.015], ['Call 3 bb', 'call', 0.005]], 2),
  node('CO', [['Fold', 'fold', 0.99], ['Call 3 bb', 'call', 0.004], ['4-bet 3x', 'raise', 0.006]], 1),
  node('BTN', [['Fold', 'fold', 0.99], ['Call 3 bb', 'call', 0.01]]),
], 4e-7);
const rarest = studyTarget(thin);
assert.deepEqual([rarest.pos, rarest.label, rarest.single, rarest.tab], ['CO', 'Call 3 bb', false, 'SQUEEZE']);
assert.match(studyGuide(rarest, { state: 'solver' }, TYPES, UI).why, /^No single step is to blame here.*Start with its rarest step, CO's Call 3 bb: make CO a player who takes it\./);

// inside the editor: the same step in one line
assert.equal(studyEditorHint(limp), 'To study UTG\'s Limp 1 bb: UNOPENED tab, CALL brush, then click the hands that should limp. Or raise "open-limp %".');
assert.equal(studyEditorHint(jam), 'To study UTG\'s All-in 150x: UNOPENED tab, JAM brush, then click the hands that should go all-in.');
assert.match(studyEditorHint(big), /RAISE brush, then click the hands that should raise\. Or raise "open-raise %"\. Its raises use one size: set "fallback raise size" to max/);
assert.equal(studyEditorHint(limpCall), 'To study UTG\'s Call 4 bb: this spot comes later in the hand, where single hands cannot be set. Lower "fold vs raise after limping %" to make UTG call more.');
assert.equal(studyEditorHint(null), '');
assert.equal(studyGuide(null), null);
console.log('preflop study steps tests passed');
