# Model evidence in the Preflop Lab

The evidence badge appears above the current action's range grid and in
**Manage models → Edit**. Expand it to see the source and its limitations.
The editor badge follows the selected position, range tab and response context.
The game badge follows the policy actually used at the selected action.

| Label | Meaning |
|---|---|
| History-backed | The stored hand probabilities match a supplied, smoothed history policy. Sparse hands can still borrow pooled estimates. |
| Extrapolated | History-backed probabilities are being transferred beyond the source's table-size, blind or ante coverage. That transfer is unvalidated. |
| Contextual estimate | The experimental predictor uses entry history, raise depth and call price. Its output is a prediction, not direct observations of that exact situation. |
| Contextual fallback / Pooled fallback | The requested contextual model or size-specific policy is unavailable; the displayed stored or pooled policy is used instead. |
| Stat-derived | A freshly generated range infers hand composition from aggregate tendencies and reference ordering. |
| Stored policy | The range is saved, copied or modified and its exact hand-history origin cannot be verified. Keeping source stats does not certify an edited range. |
| Solver / Adaptive solver / Frozen strategy | A solver strategy applies, possibly learned only above the profile's adaptive threshold or retained from an earlier solve. |
| Point lock | A node-specific lock overrides the player model. |

These labels describe **provenance, not confidence**. A large pooled sample is
not a large sample of every hand at every price and stack depth. Known-card
histories include folds, but a smoothed range can still have little direct
evidence for an individual hand. Source counts, where supplied, are labeled
with what they pool; they are not a percentage certainty or a guarantee of
profitable play.

An edited range is checked against its supplied history probabilities rather
than trusted simply because a dataset name remains attached. Older saved
stat-derived profiles may say **Stored policy** until regenerated: the old save
does not record whether someone painted over its generated probabilities.
This is conservative labeling, not a change to how that profile plays.

For a contextual preview above the adaptive threshold, the preview still shows
the underlying model estimate. The badge explains that the actual game learns
an adaptive solver response instead. Use the game ribbon to inspect that
solved response. A big blind in an unopened pot has no decision; the editor
continues to show **Not applicable** rather than a fictitious calling range.

The evidence API is read-only. Inspecting or expanding a badge does not train
a model, apply a profile, repaint ranges, or change either solve. Existing
profiles and saved games need no migration.

The [calling audit](../research/preflop-evolution/behavior/pass3/README.md)
explains why the new first-entry candidate was not installed: it did not improve
overall retrospective prediction, and cold-call and limp-first errors run in
opposite directions. The current model is retained while its limitations become
easier to inspect.
