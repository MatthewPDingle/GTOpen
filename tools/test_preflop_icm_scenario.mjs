import assert from 'node:assert/strict';
import { icmScenario, icmFromConfig } from '../web/js/preflop_icm.js';

const state = {
  on: true, payouts: '60, 25, 15', fieldCount: '144', fieldStack: '25',
  stage: 'mid', stackOff: '0.4', edited: true, rakePct: '5', rakeCap: '2',
};
const saved = icmScenario(state, state.rakePct, state.rakeCap);
assert.equal(saved.icm.stage, 'mid', 'the selected preset round-trips');
assert.equal(saved.icm.edited, true, 'a customized preset stays marked edited');
assert.equal(saved.icm.payouts, '60, 25, 15', 'custom payouts round-trip');
assert.deepEqual([saved.rakePct, saved.rakeCap], [5, 2], 'entered rake rides along separately');

// An untouched preset is not marked edited, so the player-count listener may
// refresh it from the stage defaults.
const preset = icmScenario({ ...state, edited: false }, '0', '0');
assert.equal(preset.icm.edited, false);
assert.deepEqual([preset.rakePct, preset.rakeCap], [0, 0]);

// Legacy scenarios have no `edited` key: they must load as "not edited" so a
// player-count change still refreshes an untouched preset.
const legacy = icmFromConfig({ icm: { payouts: [50, 30, 20], field_groups: [{ count: 144, stack: 25 }] } });
assert.equal(legacy.edited, false);
assert.equal(legacy.stage, '', 'config shapes carry no stage');
assert.equal(legacy.fieldCount, '144');
assert.equal(icmFromConfig({}).edited, false, 'the no-ICM shape is uniform');

console.log('test_preflop_icm_scenario: ok');
