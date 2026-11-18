// Which leaf net "learned flop values" uses. There is no picker: a new game
// uses the shipped default net, and a loaded game keeps the net it was solved
// with, so a re-solve of an old save prices it as before. (The server can still
// load other nets named in a game's `leaf_net`, e.g. from the leaf-net harness,
// through the API.)

/** The first shipped net: what a game that names no net was solved with. */
export const FIRST_NET = 'v1';
/** The net a new game uses. */
export const DEFAULT_NET = 'v3';

/** The value model of a game built from the form: learned flop values when
 *  ticked, except with ICM payouts, which the leaf net does not price. */
export const modelFor = (learned, icm) => (learned && !icm ? 'leafnet' : 'balanced');
/** Engine fields for a net: none when learned values are off. v1 stays
 *  unnamed, as in every game saved before a second net shipped. */
export const netConfig = (on, id) => (on && id && id !== FIRST_NET ? { leaf_net: id } : {});
/** The net for a game: its own when it uses learned values (no name means
 *  v1), else the default. */
export const netOf = cfg =>
  (cfg?.realization === 'leafnet' ? (cfg.leaf_net || FIRST_NET) : DEFAULT_NET);

/** Tracks the net of the game on the form. */
export function createLeafNet() {
  let net = DEFAULT_NET;
  return {
    // fields for the engine config; `on` is whether this game uses learned values
    config: on => netConfig(on, net),
    // a loaded game keeps its net; no game (a fresh scenario) goes back to the default
    load(cfg) { net = netOf(cfg); },
  };
}
