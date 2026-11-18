import assert from 'node:assert/strict';
import { defaultGame } from '../web/js/rangelab_ref.js';

const ctx = { players: 8, straddle: false, ante: 0 };
const games = [{ tag: 'cev9', players: 9 }, { tag: 'reg', players: 8 }, { tag: 'str', players: 8 }];
assert.equal(defaultGame(ctx, games).tag, 'reg');
assert.equal(defaultGame({ ...ctx, straddle: true }, games).tag, 'str');
assert.equal(defaultGame({ ...ctx, players: 9, ante: 0.125 }, games).tag, 'cev9');
assert.equal(defaultGame({ ...ctx, players: 6 }, games), null);
assert.equal(defaultGame(null, games).tag, 'reg');
console.log('rangelab_ref ok');
