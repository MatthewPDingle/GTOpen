// Blind stakes are entered in the same units; the engine always uses bb.
export function blindSizes(scenario = {}) {
  return { smallBlind: Number(scenario.smallBlind ?? 1), bigBlind: Number(scenario.bigBlind ?? 2) };
}

export function blindPosts(positions, scenario) {
  const { smallBlind, bigBlind } = blindSizes(scenario);
  if (!Number.isFinite(smallBlind) || !Number.isFinite(bigBlind) ||
      smallBlind <= 0 || bigBlind <= 0 || smallBlind > bigBlind) {
    throw new Error('Blinds must be positive, with the small blind no larger than the big blind.');
  }
  const posts = positions.map(p => p === 'SB' ? smallBlind / bigBlind : p === 'BB' ? 1 : 0);
  const straddle = Number(scenario.straddle ?? 0);
  if (!Number.isFinite(straddle) || straddle < 0 || (straddle > 0 &&
      (positions.length < 3 || straddle < 2 || ['SB', 'BB'].includes(positions[0])))) {
    throw new Error('A live UTG straddle requires 3+ players and an amount of at least 2 bb.');
  }
  if (straddle) posts[0] = straddle;
  return posts;
}

export function unraisedWinner(config, positions) {
  return config?.utg_straddle ? 0 : positions.indexOf('BB');
}
