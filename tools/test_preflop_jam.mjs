import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { JAM_PCT_BEFORE, JAM_PCT_DEFAULT, jamConfig, jamPct, jamPctOf, sameJam, scenarioJamPct } from '../web/js/preflop_jam.js';

// The box: a percent, or off when empty, 100 or nonsense.
assert.equal(jamPct('30'), 30);
assert.equal(jamPct(12.5), 12.5);
for (const off of ['', '  ', null, undefined, 'x', 0, -5, 100, 150]) assert.equal(jamPct(off), null, String(off));

// "Over 30%": the engine jams a raise AT or above its fraction, so the
// fraction sits a hair above 30%. A raise to exactly 30% stays a raise, and
// anything measurably bigger is all-in.
const engineJams = (to, stack, cfg) => to >= cfg.allin_threshold * stack;
const thirty = jamConfig('30');
assert.equal(engineJams(30, 100, thirty), false);
assert.equal(engineJams(7.5, 25, thirty), false);
assert.equal(engineJams(45, 150, thirty), false);
assert.equal(engineJams(30.01, 100, thirty), true);
assert.equal(engineJams(60, 150, thirty), true);
assert.equal(engineJams(36, 150, thirty), false);
assert.equal(engineJams(108, 150, thirty), true);
// Off: only the whole stack is all-in.
assert.deepEqual(jamConfig(''), { allin_threshold: 1 });
assert.deepEqual(jamConfig(100), { allin_threshold: 1 });
assert.equal(engineJams(149, 150, jamConfig('')), false);
// The engine accepts fractions in (0, 1] only.
for (const v of ['1', '30', '85', '99.9', '']) {
  const t = jamConfig(v).allin_threshold;
  assert.ok(t > 0 && t <= 1, String(v));
}

// A built or loaded game fills the box back in, older games included.
assert.equal(jamPctOf(jamConfig('30')), 30);
assert.equal(jamPctOf(jamConfig('12.5')), 12.5);
assert.equal(jamPctOf(jamConfig('')), '');
assert.equal(jamPctOf({ allin_threshold: 0.85 }), 85);
assert.equal(jamPctOf({}), JAM_PCT_BEFORE);
assert.equal(jamPctOf(null), JAM_PCT_BEFORE);
// The round trip is stable: what the box shows builds the same game again.
for (const v of ['30', '85', '12.5', '']) {
  assert.deepEqual(jamConfig(jamPctOf(jamConfig(v))), jamConfig(v));
}

// Scenarios saved before the box existed keep the 85% every game used.
assert.equal(scenarioJamPct({}), 85);
assert.equal(scenarioJamPct({ jamPct: 30 }), 30);
assert.equal(scenarioJamPct({ jamPct: '' }), '');
assert.equal(sameJam({}, { jamPct: 85 }), true);
assert.equal(sameJam({}, { jamPct: 30 }), false);
assert.equal(sameJam({ jamPct: '' }, { jamPct: '' }), true);
assert.equal(sameJam({ jamPct: 30 }, { jamPct: '30' }), true);
assert.equal(JAM_PCT_DEFAULT, 30);

// The form: one row with the three raise controls, new games at 30, and no
// separate "all-in over the last raise" box.
const html = readFileSync(new URL('../web/index.html', import.meta.url), 'utf8');
const row = /<div class="pfl-raises">([\s\S]*?)<\/div>/.exec(html)?.[1] ?? '';
for (const id of ['pfl-maxraises', 'pfl-allin', 'pfl-jampct']) assert.ok(row.includes(`id="${id}"`), id);
assert.match(row, /id="pfl-jampct"[^>]*value="30"/);
assert.match(row, /All-in as a raise size/);
assert.match(row, /Jam if a raise commits over/);
assert.equal(html.includes('pfl-lastallin'), false);
const lab = readFileSync(new URL('../web/js/preflop_lab.js', import.meta.url), 'utf8');
// every built-in scenario says 30 outright
const presets = /const PRESETS = \[([\s\S]*?)\n\];/.exec(lab)[1];
assert.equal((presets.match(/name: '/g) || []).length, (presets.match(/jamPct: JAM_PCT_DEFAULT/g) || []).length);

console.log('preflop jam rule tests passed');
