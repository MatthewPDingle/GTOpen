// The Preflop Lab's rake type: which pots the configured rake is charged on.
//
// The engine has two switches. `no_flop_no_drop` is the live-cash rule (a pot
// that ends before the flop is not raked; false rakes every pot, "Full").
// `rake_threebet` is GG Network's rule: while no-flop-no-drop is on, a
// preflop fold-out is raked once the line had a 3-bet or more. The form
// offers the three combinations as one choice, so it never sends the
// meaningless pair (no_flop_no_drop false + rake_threebet true).
//
// Postflop pots are raked the same way under every type; a scenario saved
// before the choice existed keeps the old game, No Flop, No Drop. With no
// rake (ICM forces it to zero) the form builds the plain no-rake game: the
// choice changes nothing then, and the game saves in a format older programs
// read.

export const RAKE_TYPES = ['noflop', 'full', 'gg'];

/** What the select's label says on hover: the rule of the choice in view. */
export const RAKE_TYPE_TIPS = {
  noflop: 'Rake is charged only on pots that reach the flop.',
  full: 'Rake is charged on every pot, including one that ends before the flop.',
  gg: 'Rake is charged on preflop 3-bet pots and on every pot that reaches the flop.',
};

const known = (type) => (RAKE_TYPES.includes(type) ? type : 'noflop');

/**
 * The type a game actually plays. With no rake nothing is charged, and ICM
 * forces the rate to zero, so the choice has no effect and the game is the
 * plain No Flop, No Drop one.
 */
export function effectiveRakeType(type, rakePct, icm) {
  return Number(rakePct) > 0 && !icm ? known(type) : 'noflop';
}

/** The engine fields for a choice. Full never carries the 3-bet flag. */
export function rakeTypeConfig(type) {
  const t = known(type);
  return {
    no_flop_no_drop: t !== 'full',
    ...(t === 'gg' ? { rake_threebet: true } : {}),
  };
}

/** What the form shows for a built or loaded game. Full wins if both are set. */
export function rakeTypeOf(cfg) {
  if (cfg?.no_flop_no_drop === false) return 'full';
  return cfg?.rake_threebet ? 'gg' : 'noflop';
}

/** What the form shows for a scenario; one saved before the choice keeps the old game. */
export function scenarioRakeType(scenario) {
  return known(scenario?.rakeType);
}

/** Whether a saved scenario's choice is the form's (`cur` is the form). */
export const sameRakeType = (scenario, cur) => scenarioRakeType(scenario) === scenarioRakeType(cur);

/** Whether a config asks for the 3-bet rule (a program older than the page ignores it). */
export const usesThreeBetRake = (cfg) => cfg?.rake_threebet === true;
