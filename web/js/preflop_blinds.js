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
  return positions.map(p => p === 'SB' ? smallBlind / bigBlind : p === 'BB' ? 1 : 0);
}
