// Blockers in the Preflop Lab: card removal in the preflop model
// (`card_removal` in the game config; see docs/technical_reference.md).
// Each hand's own two cards come out of the deck before it is valued, so
// hands differ in how often the others fold. Every new game is built with
// it; there is no switch. A loaded game keeps what it was solved with, and
// saves from before blockers have none.

/** Engine fields for a new game: blockers, except with ICM payouts, which
 *  the engine does not combine with them. */
export const blockersConfig = icm => (icm ? {} : { card_removal: true });
/** Whether a built or loaded game was solved with blockers. */
export const blockersOf = cfg => !!cfg?.card_removal;
