import assert from 'node:assert/strict';
import { fmtNum, modelLabel, reportCardFacts } from '../web/js/report_labels.js';

// A card is built from the list endpoint's summary only — no name parsing.
const full = {
  title: 'BTN vs BB SRP',
  players: 6, stakes: '2/5', bb: 100,
  pot: 6, stack: 100, rake_pct: 5, rake_cap: 10, max_raises: 3,
  target: 0.35,
  oop_sizes: ['33 75/r60', '75/r60', '75/r60'],
  ip_sizes: ['33 75/r60', '75/r60', '75/r60'],
};
const facts = reportCardFacts(full);
assert.equal(facts.context, '$2/5 · 100bb · 6-max · 5% rake');
assert.equal(facts.detail,
  'pot 6 · stack 100 · sizes F 33 75/r60 · T 75/r60 · R 75/r60 · target 0.35%');

// Different OOP/IP menus name the side; a swept grid is its own label.
const split = reportCardFacts({ ...full, ip_sizes: ['50/r60', '50/r60', '50/r60'], sweep_sizes: [25, 33.5, 50] });
assert.match(split.detail, /sizes OOP F 33 75\/r60 · T 75\/r60 · R 75\/r60 · IP F 50\/r60/);
assert.match(split.detail, /swept 25\/33\.5\/50/);

// A per-size variant and a legacy report each add only what they know.
assert.equal(reportCardFacts({ size: 12.5 }).detail, '');
assert.deepEqual(reportCardFacts({}), { context: '', detail: '' });
assert.deepEqual(reportCardFacts(), { context: '', detail: '' });

assert.equal(modelLabel(undefined), 'GTO');
assert.equal(modelLabel('Data · TAG · station'), 'vs TAG · station');
assert.equal(modelLabel('fish'), 'vs fish');

assert.equal(fmtNum(100), '100');
assert.equal(fmtNum(12.5), '12.5');
assert.equal(fmtNum(0.35), '0.35');
assert.equal(fmtNum(NaN), '—');

console.log('report card facts build from the list summary');
