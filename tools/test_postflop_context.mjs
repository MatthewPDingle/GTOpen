import assert from 'node:assert/strict';
import { editPostflopStats, hasContextualBetting, rootBettingEvidence } from '../web/js/postflop_context.js';
import { api } from '../web/js/api.js';

const stats = {
  cbet: [60, 50, 40], fold_to_bet: [40, 45, 50], raise_bet: 8, donk: 25.25, bet_size: 'min',
  contextual_betting: { version: 1, source: 'test histories', cells: [
    { street: 0, kind: 'donk', pot_type: 'three_bet_plus', opportunities: 100, bets: 5 },
  ] },
};
const edited = editPostflopStats(stats, { raise_bet: 10, bet_size: 'max' });
assert.deepEqual(edited.contextual_betting, stats.contextual_betting);
assert.notEqual(edited.contextual_betting, stats.contextual_betting);
edited.contextual_betting.cells[0].bets = 12;
assert.equal(stats.contextual_betting.cells[0].bets, 5, 'editing a copy must not change original source evidence');
assert.equal(edited.raise_bet, 10);
assert.equal(hasContextualBetting(stats), true);
assert.equal(hasContextualBetting({ donk: 25.25 }), false);

const calls = [];
globalThis.fetch = async (url, options) => {
  calls.push({ url, body: JSON.parse(options.body) });
  return { ok: true, json: async () => ({ locked: 1, rows: [] }) };
};
await api.profileLocks(0, stats, 1, 'three_bet_plus');
assert.equal(calls[0].body.pot_type, 'three_bet_plus');
assert.deepEqual(calls[0].body.stats.contextual_betting, stats.contextual_betting);
await api.profileLocks(0, stats, 1);
assert.equal(calls[1].body.pot_type, null, 'legacy transfers must not invent a pot context');
await api.reportsRun({ name: 'context fixture', villain: { player: 0, stats, aggressor: 1, pot_type: 'three_bet_plus' } });
assert.deepEqual(calls[2].body.villain.stats.contextual_betting, stats.contextual_betting);
assert.equal(calls[2].body.villain.pot_type, 'three_bet_plus');

const fallback = rootBettingEvidence({ kind: 'donk', opportunities: 0, observed: null, target: 0.02, achieved: 0.02 });
assert.match(fallback, /Root/);
assert.doesNotMatch(fallback, /observed/);
assert.match(rootBettingEvidence({ kind: 'donk', opportunities: 100, observed: 5, target: 2, achieved: 1.8 }), /observed 5.0%.*target 2.0%.*achieved 1.8%/);
console.log('Contextual evidence survives model edits and Browse/report requests; missing context and evidence labels passed.');
