import assert from 'node:assert/strict';

// Browse's "find best size" opens the saved sweep in REPORTS. The regression:
// the navigation was a search through the rendered library rows, so a Reports
// search that filtered the sweep's card out left it clicking nothing (the old
// code retried on a timer and then gave up silently).
//
// The module is imported before any DOM exists: best_size.js reaches for
// document only when it navigates, never at import time.
const { openSavedReport } = await import('../web/js/best_size.js');

const NAME = 'Find best size Ks7h2d OOP';

// What the navigation did, in order, plus what it was allowed to touch.
let events = [];
let cardQueries = 0;   // lookups of a rendered `#rep-library .report-item`
let timers = 0;        // retry/poll timers a card-click navigation needs
let rows = [];         // what the library renders; [] = the search hid the card

globalThis.document = {
  querySelector(sel) {
    assert.equal(sel, '.tab[data-tab="reports"]', 'the tab is the only element it looks up');
    return { click: () => events.push('tab') };
  },
  querySelectorAll(sel) {
    cardQueries++;
    assert.equal(sel, '#rep-library .report-item');
    return rows;
  },
};

// Count timers: the old navigation waited on one, and a stray one would keep
// node alive after the run.
const realSetInterval = globalThis.setInterval;
const realSetTimeout = globalThis.setTimeout;
globalThis.setInterval = (...a) => { timers++; return realSetInterval(...a); };
globalThis.setTimeout = (...a) => { timers++; return realSetTimeout(...a); };

const reset = () => { events = []; cardQueries = 0; timers = 0; };

// Each hook yields twice before recording, so the order below also proves the
// navigation awaits the refresh and the open: a hook it merely fired off
// would still be pending when openSavedReport resolves.
const later = fn => async (...a) => { await null; await null; return fn(...a); };
const direct = () => ({
  refreshReports: later(() => events.push('refresh')),
  openReport: later(n => events.push(`open:${n}`)),
});

// The maintainer's case: the Reports search hides the sweep, so no row is
// rendered. The direct loader must be enough on its own.
reset();
rows = [];
await openSavedReport(NAME, direct());
assert.deepEqual(events, ['tab', 'refresh', `open:${NAME}`],
  'switch to Reports, refresh the library, then open the report by name');
assert.equal(cardQueries, 0, 'the direct loader must not search for the card the filter hid');
assert.equal(timers, 0, 'and must not wait for it on a retry timer');

// The loader is the primary path, not a last resort: even with a card
// rendered (say, one left over from an earlier search) it is not clicked.
reset();
rows = [{ dataset: { name: NAME }, click: () => events.push('card') }];
await openSavedReport(NAME, direct());
assert.deepEqual(events, ['tab', 'refresh', `open:${NAME}`], 'a rendered card never takes precedence');
assert.equal(cardQueries, 0, 'a card-first hybrid would search here and can still fail on a stale row');
assert.equal(timers, 0);

// A failed direct load is surfaced once, through the host's error surface,
// and is not downgraded to a card click or retried behind its back.
reset();
const errors = [];
rows = [{ dataset: { name: NAME }, click: () => events.push('card') }];
await openSavedReport(NAME, {
  refreshReports: later(() => events.push('refresh')),
  openReport: async () => { events.push('open'); throw new Error('no such report'); },
  toast: (msg, isErr) => errors.push([msg, isErr]),
});
assert.deepEqual(events, ['tab', 'refresh', 'open'], 'a failed open is not retried as a card click');
assert.deepEqual(errors, [['no such report', true]], 'the loader error reaches the user once');
assert.equal(cardQueries, 0, 'a failed loader must not fall back to the card');
assert.equal(timers, 0);

// The library list is decoration: a failed refresh must not block the jump,
// because the loader reads the report by name.
reset();
await openSavedReport(NAME, {
  refreshReports: async () => { throw new Error('list down'); },
  openReport: later(n => events.push(`open:${n}`)),
});
assert.deepEqual(events, ['tab', `open:${NAME}`], 'a stale library still opens the report');

// A host without the direct loader still clicks a rendered card, after the
// refresh that renders it — and needs no timer for a card already there.
reset();
rows = [{ dataset: { name: NAME }, click: () => events.push('card') }];
await openSavedReport(NAME, { refreshReports: later(() => events.push('refresh')) });
assert.deepEqual(events, ['tab', 'refresh', 'card']);
assert.equal(cardQueries, 1);
assert.equal(timers, 0, 'the card is there after the refresh; no retry loop');

// No loader and no rendered card: give up at once with a message. The old
// retry timer kept this case alive for two seconds before failing silently.
reset();
rows = [];
const noTarget = [];
await openSavedReport(NAME, { toast: (msg, isErr) => noTarget.push([msg, isErr]) });
assert.deepEqual(events, ['tab']);
assert.deepEqual(noTarget, [[`couldn’t open “${NAME}” in Reports`, true]], 'the dead end is reported');
assert.equal(timers, 0, 'nothing to wait for, so nothing is scheduled');

// Leave the process as it was found, in case a runner imports several files.
globalThis.setInterval = realSetInterval;
globalThis.setTimeout = realSetTimeout;
delete globalThis.document;

console.log('test_best_size_report_link: ok');
