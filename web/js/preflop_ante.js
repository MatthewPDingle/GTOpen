// The Preflop Lab's ante: an amount in bb and who pays it.
//
// "each" is the ante every seat pays (`ante` in the game config). "bb" is a
// big blind ante: one ante, paid by the big blind alone (`bb_ante`). Either
// way it is dead money paid on top of the stack, so every seat still plays
// the stack on the form. A scenario saved before the choice existed has no
// `anteBy` and reads as "each", which is what it always was.

export const ANTE_EACH = 'each';
export const ANTE_BB = 'bb';

const amountOf = value => {
  const v = Number(value);
  return Number.isFinite(v) && v > 0 ? v : 0;
};

/** Who pays, from a scenario or the form's select. */
export const anteBy = value => (value === ANTE_BB ? ANTE_BB : ANTE_EACH);

/** Engine fields. A per-seat ante gives the same config it always did. */
export function anteConfig(amount, by) {
  const a = amountOf(amount);
  return anteBy(by) === ANTE_BB && a > 0 ? { ante: 0, bb_ante: a } : { ante: a };
}

/** The form's two values from a built or loaded game. */
export function anteOf(cfg) {
  const bb = amountOf(cfg?.bb_ante);
  return bb > 0 && !amountOf(cfg?.ante) ? { amount: bb, by: ANTE_BB } : { amount: amountOf(cfg?.ante), by: ANTE_EACH };
}

/** Whether a game needs a GTOpen program that knows the big blind ante. */
export const usesBbAnte = cfg => amountOf(cfg?.bb_ante) > 0;

/** Whether a saved scenario's ante is the form's (`cur` is the form). */
export function sameAnte(scenario, cur) {
  const a = amountOf(scenario?.ante), b = amountOf(cur?.ante);
  // with no ante there is nobody to pay it
  return a === b && (a === 0 || anteBy(scenario?.anteBy) === anteBy(cur?.anteBy));
}
