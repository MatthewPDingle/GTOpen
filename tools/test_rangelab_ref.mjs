import assert from 'node:assert/strict';
import { lineTokens, matchContext, defaultGame, actionColors } from '../web/js/rangelab_ref.js';

const act = (kind, to = 0) => ({ kind, to, label: kind });
const step = (pos, actions, chosen) => ({ kind: 'action', actor_pos: pos, actions, chosen });
// UTG opens 3, UTG1 folds, MP 3-bets to 9, the rest fold back to UTG (current node).
const history = [
  step('UTG', [act('fold'), act('call', 1), act('raise', 3)], 2),
  step('UTG1', [act('fold'), act('call', 3), act('raise', 9)], 0),
  step('MP', [act('fold'), act('call', 3), act('raise', 9), act('jam', 100)], 2),
  ...['HJ', 'CO', 'BTN', 'SB', 'BB'].map(p => step(p, [act('fold'), act('call', 9)], 0)),
  step('UTG', [act('fold'), act('call', 9), act('raise', 27)], null),
];
assert.deepEqual(lineTokens(history), ['R', 'F', 'R', 'F', 'F', 'F', 'F', 'F']);
assert.deepEqual(lineTokens([step('UTG', [act('fold')], null)]), []);
const positions = ['UTG', 'UTG1', 'MP', 'HJ', 'CO', 'BTN', 'SB', 'BB'];
const cfg = { stack: 150, open_raises: [3, 2.5], ante: 0 };
const ctx = matchContext({ kind: 'action', positions, history, actor_pos: 'UTG' }, cfg);
assert.equal(ctx.players, 8);
assert.equal(ctx.open_to, 3, 'the line opener sets the open size');
assert.equal(matchContext({ kind: 'action', positions, history: history.slice(0, 1), actor_pos: 'UTG' }, cfg).open_to, 2.5,
  'first in uses the smallest configured open');
assert.equal(matchContext({ kind: 'pot_share', positions, history }, cfg), null);

const games = [{ tag: 'cev9', players: 9 }, { tag: 'reg', players: 8 }, { tag: 'str', players: 8 }];
assert.equal(defaultGame(ctx, games).tag, 'reg');
assert.equal(defaultGame({ ...ctx, straddle: true }, games).tag, 'str');
assert.equal(defaultGame({ ...ctx, players: 9, ante: 0.125 }, games).tag, 'cev9');
assert.equal(defaultGame({ ...ctx, players: 6 }, games), null);
assert.equal(defaultGame(null, games).tag, 'reg');
assert.deepEqual(actionColors([act('fold'), act('call'), act('raise'), act('jam')]), ['#4a78c8', '#5ca75f', '#e8484c', '#7c3134']);
console.log('rangelab_ref ok');
