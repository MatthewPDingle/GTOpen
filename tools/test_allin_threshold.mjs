import assert from 'node:assert/strict';
import { allinThresholdPercent, allinThresholdRequest } from '../web/js/threshold.js';

for (const percent of [0.001, 0.85, 1, 85, 100]) {
  const wire = allinThresholdRequest(percent);
  assert.equal(allinThresholdPercent(wire), percent);
  assert.equal(allinThresholdPercent(JSON.parse(JSON.stringify(wire))), percent);
  assert.deepEqual(wire, percent < 1 ? { percent } : percent);
}
// Numeric historical requests and explicit-unit readbacks compare equally.
assert.equal(allinThresholdPercent(1), 1);
assert.equal(allinThresholdPercent({ percent: 1 }), 1);
console.log('All-in threshold UI request/readback checks passed.');
