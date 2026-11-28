import assert from 'node:assert/strict';
import { unsupportedPreflopFeatures } from '../web/js/version.js';
import { RAKE_TYPES, RAKE_TYPE_TIPS, effectiveRakeType, rakeTypeConfig, rakeTypeOf, scenarioRakeType, sameRakeType, usesThreeBetRake } from '../web/js/preflop_rake.js';

// The three choices map to the engine's two switches.
assert.deepEqual(rakeTypeConfig('noflop'), { no_flop_no_drop: true });
assert.deepEqual(rakeTypeConfig('full'), { no_flop_no_drop: false });
assert.deepEqual(rakeTypeConfig('gg'), { no_flop_no_drop: true, rake_threebet: true });
// The meaningless pair is never built: Full carries no 3-bet flag.
assert.equal('rake_threebet' in rakeTypeConfig('full'), false);
assert.equal('rake_threebet' in rakeTypeConfig('noflop'), false);

// Built and loaded games fill the select back in.
for (const type of RAKE_TYPES) assert.equal(rakeTypeOf(rakeTypeConfig(type)), type);
assert.equal(rakeTypeOf({ no_flop_no_drop: true }), 'noflop');
assert.equal(rakeTypeOf({}), 'noflop'); // older config: the field default
assert.equal(rakeTypeOf({ no_flop_no_drop: false }), 'full');
assert.equal(rakeTypeOf({ rake_threebet: true }), 'gg');
// If a hand-edited game carries both, Full is the game the engine plays.
assert.equal(rakeTypeOf({ no_flop_no_drop: false, rake_threebet: true }), 'full');

// A scenario saved before the choice existed keeps the old game.
assert.equal(scenarioRakeType({}), 'noflop');
assert.equal(scenarioRakeType({ rakeType: 'gg' }), 'gg');
for (const bad of ['', null, undefined, 'GG', 'nonsense']) {
  assert.equal(scenarioRakeType({ rakeType: bad }), 'noflop', String(bad));
  assert.deepEqual(rakeTypeConfig(bad), { no_flop_no_drop: true });
}
// A scenario still matches when its saved choice is the form's, including
// scenarios from before the choice existed.
assert.equal(sameRakeType({}, { rakeType: 'noflop' }), true);
assert.equal(sameRakeType({}, { rakeType: 'full' }), false);
assert.equal(sameRakeType({ rakeType: 'gg' }, { rakeType: 'gg' }), true);

// Only GG asks for the server that knows the flag.
assert.equal(usesThreeBetRake(rakeTypeConfig('gg')), true);
assert.equal(usesThreeBetRake(rakeTypeConfig('full')), false);
assert.equal(usesThreeBetRake({}), false);

// With no rake, or under ICM's forced zero, the choice is inert: the game is
// the plain No Flop, No Drop one, so no restart and no v9 save are needed.
assert.equal(effectiveRakeType('gg', 5, false), 'gg');
assert.equal(effectiveRakeType('full', 5, false), 'full');
assert.equal(effectiveRakeType('gg', 0, false), 'noflop');
assert.equal(effectiveRakeType('full', 0, false), 'noflop');
assert.equal(effectiveRakeType('gg', '', false), 'noflop');
assert.equal(effectiveRakeType('gg', 5, true), 'noflop');
assert.equal(effectiveRakeType('gg', 0, true), 'noflop');
assert.deepEqual(rakeTypeConfig(effectiveRakeType('gg', 0, false)), { no_flop_no_drop: true });

// Every choice explains itself in the label's tooltip.
for (const type of RAKE_TYPES) assert.ok(RAKE_TYPE_TIPS[type], type);
assert.equal(RAKE_TYPE_TIPS.full.includes('before the flop'), true);
assert.equal(RAKE_TYPE_TIPS.gg.includes('3-bet'), true);
// A level-8 server already supports the existing features, even with the new UI.
const oldFeatures = { sizing: true, bbAnte: true };
assert.deepEqual(unsupportedPreflopFeatures({ server_level: 8 }, oldFeatures), []);
const allFeatures = { ...oldFeatures, threeBetRake: true };
assert.deepEqual(unsupportedPreflopFeatures({ server_level: 8 }, allFeatures), ['GG Network rake']);
assert.deepEqual(unsupportedPreflopFeatures({ server_level: 9 }, allFeatures), []);
assert.deepEqual(unsupportedPreflopFeatures(null, allFeatures), [
  'the new raise sizes', 'a big blind ante', 'GG Network rake',
]);
assert.deepEqual(unsupportedPreflopFeatures(null, {}), []);
