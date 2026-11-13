import assert from 'node:assert/strict';

// Minimal DOM: the module touches document only when it renders or navigates.
// `#rep-library .report-item` deliberately renders nothing — this is the
// maintainer's case where the Reports search hides the sweep's card.
const tabClick = [];
const openCalls = [];
globalThis.document = {
  querySelector: sel => sel === '.tab[data-tab="reports"]' ? { click: () => tabClick.push(sel) } : null,
  querySelectorAll: () => [],
};

const { openSavedReport } = await import('../web/js/best_size.js');

const name = 'Find best size Ks7h2d OOP';
await openSavedReport(name, {
  refreshReports: async () => { openCalls.push('refresh'); },
  openReport: async n => { openCalls.push(n); },
});

assert.deepEqual(tabClick, ['.tab[data-tab="reports"]'], 'switches to Reports first');
assert.deepEqual(openCalls, ['refresh', name],
  'opens the report through the direct loader, not by clicking a filtered-out card');

// A host without the direct loader still falls back to a rendered card.
const clicked = [];
globalThis.document.querySelectorAll = () => [{
  dataset: { name },
  click: () => clicked.push(name),
}];
await openSavedReport(name, {});
assert.deepEqual(clicked, [name], 'older hosts click the card when it is rendered');

console.log('test_best_size_report_link: ok');
