// How a Preflop Lab game values flops, and which leaf net it uses. There is
// no switch and no picker: a new game uses learned flop values with the
// shipped default net, except with ICM payouts, which the leaf net does not
// price. A loaded game keeps what it was solved with, so a re-solve of an old
// save prices it as before. (Through the API a game can still ask for the
// simple estimate alone, `realization: "balanced"`, or name another net in
// `leaf_net`, e.g. one from the leaf-net harness.)

/** The first shipped net: what a game that names no net was solved with. */
export const FIRST_NET = 'v1';
/** The net a new game uses. */
export const DEFAULT_NET = 'v3';

/** The value model of a game built from the form: learned flop values,
 *  except with ICM payouts, which the leaf net does not price. */
export const modelFor = icm => (icm ? 'balanced' : 'leafnet');
/** The tooltip of the tag that says how a built or loaded game values flops:
 *  `model` is its value model, `icm` whether it has tournament payouts. */
export function valueTip(model, icm) {
  if (model === 'leafnet') {
    return 'Each hand is valued by how it plays after the flop, using the leaf net: a neural net trained on many thousands of real flop solves. ' +
      'It covers flops with two players. Bigger pots and all-in pots use a simpler estimate. Close decisions are the least reliable.';
  }
  return icm
    ? 'Games with tournament payouts value every pot with a simpler estimate. The leaf net, which learned from real flop solves, does not cover them.'
    : 'This game was solved with a simpler estimate, not the leaf net. RE-SOLVE continues it as it is. BUILD GAME starts a game with learned flop values.';
}
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
