// Presentation only: solver actions and amounts remain in big blinds.
const number = value => String(Number(value.toFixed(2)));

export function formatPreflopView(view) {
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
      return { ...action, label: action.kind === 'call' ? `${action.label} bb` : action.label };
    });
    const chosen = step.actions[step.chosen];
    if (chosen && (chosen.kind === 'raise' || chosen.kind === 'jam')) {
      previousRaise = chosen.to;
    }
    return { ...step, actions };
  });
  // Each response includes the full root-to-cursor history, ending at this node.
  // Format it independently of the longer ribbon line when browsing backwards.
  return { ...view, history, actions: history.at(-1)?.actions ?? view.actions };
}
