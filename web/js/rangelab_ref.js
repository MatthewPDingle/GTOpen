// CANONICAL GTO CHARTS: helpers for the Preflop Lab's "Ranges from" choice.
// The charts are private data: the server reads them from local folders
// (cache/rangelab/ or ../Range Lab/) and nothing here bundles them.

/** The chart game that best fits the Preflop Lab table. */
export function defaultGame(ctx, games) {
  const fits = (games || []).filter(g => !ctx || g.players === ctx.players);
  if (!fits.length) return null;
  const pick = tags => tags.map(t => fits.find(g => g.tag === t)).find(Boolean);
  if (ctx?.straddle) return pick(['str']) || null;
  if (ctx?.ante > 0) return pick(['cev9', 'icm8']) || fits[0];
  return pick(['reg']) || fits.find(g => g.tag !== 'str') || fits[0];
}
