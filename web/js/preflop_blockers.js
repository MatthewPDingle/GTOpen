// The Preflop Lab's "blockers" box: card removal in the preflop model
// (`card_removal` in the game config; see docs/technical_reference.md).
// Each hand's own two cards come out of the deck before it is valued, so
// hands differ in how often the others fold. A loaded game shows the
// setting it was solved with; old saves have none and stay without it.

/** Whether a new game uses blockers unless this browser turned them off. */
export const BLOCKERS_DEFAULT = true;
const STORE = 'pfl-blockers';

/** This browser's choice for new games. `store` is localStorage-like. */
export const blockersWanted = store => {
  const saved = store?.getItem(STORE);
  return saved == null ? BLOCKERS_DEFAULT : saved !== '0';
};
export const rememberBlockers = (store, on) => store?.setItem(STORE, on ? '1' : '0');

/** Engine fields: none when off (as in every older save) or with ICM
 *  payouts, which the engine does not combine with blockers. */
export const blockersConfig = (on, icm) => (on && !icm ? { card_removal: true } : {});
/** Whether a loaded game was solved with blockers. */
export const blockersOf = cfg => !!cfg?.card_removal;
