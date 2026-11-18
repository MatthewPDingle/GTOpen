// Presentation only: solver actions and amounts remain in big blinds.
//
// Every size reads in bb. A raise names the total it goes to ("Raise 4 bb",
// "3-bet 11 bb"; `phrase` is the same inside a sentence, "3-bet to 11 bb");
// a call names what the seat adds ("Call 3 bb"). A re-raise also carries
// `note`, its size as a multiple of the raise it faces ("2.75x", or
// "2.75x + callers" when the callers' money is added on top), which the page
// shows in brackets after the amount.
const number = value => String(Number(value.toFixed(2)));

/** "3-bet 11 bb (2.75x)": the label with its note, for lists of choices. */
export const actionText = action => action.note ? `${action.label} (${action.note})` : action.label;

export function formatPreflopView(view, config = {}) {
  // Track live contributions through the line, excluding dead antes.
  const invested = Object.fromEntries(view.positions.map((p, i) =>
    [p, config.posts?.[i] ?? (p === 'SB' ? 0.5 : p === 'BB' ? 1 : 0)]));
  const callerExtra = Number(config.caller_extra) || 0;
  const limperExtra = Number(config.limper_extra) || 0;
  let previousRaise = null, raiser = null;
  let limpers = 0, callMoney = 0; // as the tree builder counts them
  const history = view.history.map(step => {
    const actions = step.actions.map(action => {
      if (action.kind === 'raise' || action.kind === 'jam') {
        const verb = action.label.replace(/\s+\S+$/, '');
        const to = `${number(action.to)} bb`;
        const total = `To ${to} in total`;
        if (action.kind === 'jam') {
          return { ...action, label: `${verb} ${to}`, phrase: `all-in for ${to}`,
            sizingHint: previousRaise == null ? '' : `${number(action.to / previousRaise)} times ${raiser}'s raise to ${number(previousRaise)} bb.` };
        }
        const base = { ...action, label: `${verb} ${to}`, phrase: `${verb.toLowerCase()} to ${to}` };
        if (previousRaise == null) {
          const extra = limperExtra * limpers;
          return { ...base, sizingHint: total +
            (extra > 0 ? `, ${number(extra)} bb of it for the ${limpers === 1 ? 'limper' : `${limpers} limpers`}.` : '.') };
        }
        // What the callers of this raise put in, when the game adds it on top.
        const added = callerExtra * callMoney;
        const withCallers = added > 0 && action.to - added > previousRaise;
        const multiple = number((withCallers ? action.to - added : action.to) / previousRaise);
        return {
          ...base,
          note: withCallers ? `${multiple}x + callers` : `${multiple}x`,
          sizingHint: `${total}: ${multiple} times ${raiser}'s raise to ${number(previousRaise)} bb` +
            (withCallers ? `, plus the ${number(added)} bb its callers put in.` : '.'),
        };
      }
      if (action.kind === 'call') {
        const added = Math.max(0, action.to - (invested[step.actor_pos] ?? 0));
        const verb = previousRaise != null ? 'Call' : invested[step.actor_pos] > 0 ? 'Complete' : 'Limp';
        // A short stack's call is its whole stack (the engine labels it).
        const allIn = action.label.startsWith('Call all-in') ? ' all-in' : '';
        return { ...action, label: `${verb}${allIn} ${number(added)} bb`,
          sizingHint: `Add ${number(added)} bb to reach ${number(action.to)} bb total (excluding ante).` };
      }
      return { ...action };
    });
    const chosen = step.actions[step.chosen];
    if (chosen && ['call', 'raise', 'jam'].includes(chosen.kind)) invested[step.actor_pos] = chosen.to;
    if (chosen && chosen.kind === 'call') {
      if (previousRaise == null) limpers += 1; else callMoney += chosen.to;
    }
    if (chosen && (chosen.kind === 'raise' || chosen.kind === 'jam')) {
      previousRaise = chosen.to;
      raiser = step.actor_pos;
      callMoney = 0;
    }
    return { ...step, actions };
  });
  // Each response includes the full root-to-cursor history, ending at this node.
  // Format it independently of the longer ribbon line when browsing backwards.
  return { ...view, history, actions: history.at(-1)?.actions ?? view.actions };
}
