import assert from 'node:assert/strict';
import { evidenceParts, evidenceText } from '../web/js/model_evidence.js';

// The Preflop Lab's "Evidence" link keeps everything the evidence box said in its tooltip.
assert.equal(evidenceParts(null), null);
assert.equal(evidenceText(undefined), '');

const solver = { kind: 'solver', label: 'Solver', summary: 'Strategy from the configured solver model; no fixed player policy applies here.', details: [] };
assert.equal(evidenceText(solver),
  'Evidence · solver · Solver\nStrategy from the configured solver model; no fixed player policy applies here.\n\nThis says where the play comes from, not how sure it is.');

// source, pooled coverage and details follow the summary; repeated lines appear once
const measured = { kind: 'measured', label: 'Measured opens', summary: 'From real decisions.', source: 'pool A',
  sample_count: 1200, session_count: 30, observed_classes: 150, details: ['From real decisions.', 'Second detail.'] };
const lines = evidenceText(measured).split('\n');
assert.equal(lines[0], 'Evidence · measured · Measured opens');
assert.deepEqual(lines.slice(1, 5), ['From real decisions.', 'Source: pool A',
  'Pooled source coverage: 1,200 decisions · 30 sessions · 150 of 169 hand classes. Prices, stacks and earlier entry details are pooled.',
  'Second detail.']);
assert.equal(lines.at(-1), 'This says where the play comes from, not how sure it is.');

// hands and sizing each get a headline; the sizing notes follow under their own heading
const sized = { kind: 'stat_derived', label: 'From stats', summary: 'Generated from HUD numbers.', details: [],
  sizing: { kind: 'fallback', label: 'Default sizes', summary: 'Table default.', source: 'defaults', details: [] } };
const parts = evidenceParts(sized);
assert.deepEqual(parts.head, ['Hands · from stats · From stats', 'Sizing · fallback · Default sizes']);
assert.deepEqual(parts.lines, ['Generated from HUD numbers.', 'Raise sizing:', 'Table default.', 'Sizing source: defaults']);

// an unknown kind and a missing label read as before
assert.equal(evidenceParts({ kind: 'mystery' }).head[0], 'Evidence · saved policy · Source not recorded');
console.log('model evidence tooltip text tests passed');
