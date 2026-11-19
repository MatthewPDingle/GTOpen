// The Preflop Lab's jam rule: a raise that would put in more than a share of
// the stack is offered as all-in instead. Past that share the raiser cannot
// fold to a re-raise anyway, so a smaller raise only adds lines nobody plays.
//
// The game config holds it as `allin_threshold`, a fraction of the stack the
// raiser can lose (their own, or the biggest stack still able to call if that
// is smaller). The engine turns a raise into all-in when it is AT or above
// that fraction; the form says "over", so a raise to exactly 30% of the stack
// stays a raise. The hair `EDGE` added to the fraction makes the two agree.
//
// Before the box existed every game used 85%. A scenario saved then has no
// `jamPct` and a game built then holds 0.85, and both keep 85: they stay the
// game they were. New games and the built-in scenarios use 30.

export const JAM_PCT_DEFAULT = 30;
export const JAM_PCT_BEFORE = 85;
const EDGE = 1e-9;

/** The box's value as a percent in (0, 100), or null when the rule is off (empty, 100 or not a number). */
export function jamPct(value) {
  if (value === null || value === undefined || String(value).trim() === '') return null;
  const v = Number(value);
  return Number.isFinite(v) && v > 0 && v < 100 ? v : null;
}

/** Engine field. Off is 1: only a raise of the whole stack is all-in, which it is anyway. */
export function jamConfig(value) {
  const p = jamPct(value);
  return { allin_threshold: p === null ? 1 : p / 100 + EDGE };
}

/** What the box shows for a built or loaded game: a percent, or '' when the rule is off. */
export function jamPctOf(cfg) {
  const t = Number(cfg?.allin_threshold);
  if (!Number.isFinite(t) || t <= 0) return JAM_PCT_BEFORE;
  if (t >= 1) return '';
  return Math.round((t - EDGE) * 1e4) / 100;
}

/** What the box shows for a scenario: its own value, or 85 when it was saved before the box existed. */
export function scenarioJamPct(scenario) {
  if (scenario?.jamPct === undefined) return JAM_PCT_BEFORE;
  return jamPct(scenario.jamPct) ?? '';
}

/** Whether a saved scenario's rule is the form's (`cur` is the form). */
export const sameJam = (scenario, cur) => scenarioJamPct(scenario) === scenarioJamPct(cur);
