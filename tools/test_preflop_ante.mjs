import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { anteBy, anteConfig, anteOf, sameAnte, usesBbAnte } from '../web/js/preflop_ante.js';

// A per-seat ante builds the config it always did: one `ante` key, no new one.
assert.deepEqual(anteConfig('0.125', 'each'), { ante: 0.125 });
assert.deepEqual(anteConfig('', 'each'), { ante: 0 });
assert.deepEqual(anteConfig('0.125', undefined), { ante: 0.125 });
assert.equal(JSON.stringify(anteConfig(0, 'bb')), '{"ante":0}');
// A big blind ante is one amount the big blind alone pays.
assert.deepEqual(anteConfig('1', 'bb'), { ante: 0, bb_ante: 1 });
assert.deepEqual(anteConfig(-1, 'bb'), { ante: 0 });
assert.deepEqual(anteConfig('x', 'bb'), { ante: 0 });
assert.equal(usesBbAnte(anteConfig(1, 'bb')), true);
assert.equal(usesBbAnte(anteConfig(1, 'each')), false);
assert.equal(usesBbAnte(null), false);

// A loaded game fills the form back in, older games included.
assert.deepEqual(anteOf({ ante: 0, bb_ante: 1 }), { amount: 1, by: 'bb' });
assert.deepEqual(anteOf({ ante: 0.125 }), { amount: 0.125, by: 'each' });
assert.deepEqual(anteOf({}), { amount: 0, by: 'each' });
for (const [amount, by] of [[1, 'bb'], [0.125, 'each'], [0, 'each']]) {
  assert.deepEqual(anteOf(anteConfig(amount, by)), { amount, by });
}

// Scenarios saved before the choice existed have no `anteBy`: each seat pays.
assert.equal(anteBy(undefined), 'each');
assert.equal(anteBy('bb'), 'bb');
assert.equal(anteBy('nonsense'), 'each');
assert.equal(sameAnte({ ante: 0.125 }, { ante: 0.125, anteBy: 'each' }), true);
assert.equal(sameAnte({ ante: 1 }, { ante: 1, anteBy: 'bb' }), false);
assert.equal(sameAnte({ ante: 1, anteBy: 'bb' }, { ante: 1, anteBy: 'bb' }), true);
assert.equal(sameAnte({ ante: 1, anteBy: 'bb' }, { ante: 0.5, anteBy: 'bb' }), false);
// with no ante the choice changes nothing
assert.equal(sameAnte({ ante: 0 }, { ante: 0, anteBy: 'bb' }), true);

// The form has the choice and the lab reads it.
const html = readFileSync(new URL('../web/index.html', import.meta.url), 'utf8');
assert.match(html, /<select id="pfl-ante-by">\s*<option value="each">each seat<\/option><option value="bb">big blind<\/option>/);
const lab = readFileSync(new URL('../web/js/preflop_lab.js', import.meta.url), 'utf8');
assert.ok(lab.includes('...anteConfig(els.ante.value, els.anteBy.value)'));
assert.ok(readFileSync(new URL('../web/js/app.js', import.meta.url), 'utf8').includes("anteBy: $('pfl-ante-by')"));
console.log('Ante amounts, who pays, loaded games and older scenarios passed.');
