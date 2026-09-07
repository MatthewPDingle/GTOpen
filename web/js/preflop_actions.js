// Presentation only: solver actions and amounts remain in big blinds.
const number = value => String(Number(value.toFixed(2)));

export function formatPreflopView(view, config = {}) {
  // Track live contributions through the line, excluding dead antes.
  const invested = Object.fromEntries(view.positions.map((p, i) =>
    [p, config.posts?.[i] ?? (p === 'SB' ? 0.5 : p === 'BB' ? 1 : 0)]));
  let previousRaise = null;
  const history = view.history.map(step => {
    const actions = step.actions.map(action => {
      if (action.kind === 'raise' || action.kind === 'jam') {
        const base = previousRaise ?? 1;
        const multiple = action.to / base;
        const verb = action.label.replace(/\s+\S+$/, '');
        return {
          ...action,
          label: `${verb} ${number(multiple)}x`,
          sizingHint: `To ${number(action.to)} bb; ${number(multiple)}x ${previousRaise == null
            ? 'the big blind' : `the previous raise to ${number(base)} bb`}.`,
        };
      }
      if (action.kind === 'call') {
        const added = Math.max(0, action.to - (invested[step.actor_pos] ?? 0));
        const verb = previousRaise != null ? 'Call' : invested[step.actor_pos] > 0 ? 'Complete' : 'Limp';
        return { ...action, label: `${verb} ${number(added)} bb`,
          sizingHint: `Add ${number(added)} bb to reach ${number(action.to)} bb total (excluding ante).` };
      }
      return { ...action };
    });
    const chosen = step.actions[step.chosen];
    if (chosen && ['call', 'raise', 'jam'].includes(chosen.kind)) invested[step.actor_pos] = chosen.to;
    if (chosen && (chosen.kind === 'raise' || chosen.kind === 'jam')) {
      previousRaise = chosen.to;
    }
    return { ...step, actions };
  });
  // Each response includes the full root-to-cursor history, ending at this node.
  // Format it independently of the longer ribbon line when browsing backwards.
  return { ...view, history, actions: history.at(-1)?.actions ?? view.actions };
}
