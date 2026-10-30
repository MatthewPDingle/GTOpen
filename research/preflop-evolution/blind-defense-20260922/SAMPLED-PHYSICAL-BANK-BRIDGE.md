# Reading the average of saved played models

The saved-model bank now has a bounded reader that forms the physical behavioral
average using each model's own earlier reach. Its control passed against both
the existing Rust reference and an independent root-model mixture. This makes
the saved research policy usable for subsequent evaluation; it does not establish
its strategic quality.

## Why the weighting matters

At a later decision, a model that would almost never have taken its own earlier
actions contributes little to the average there. The reader weights each model's
current action probabilities by its iteration weight and the product of its own
prior action probabilities. Opponent reach does not enter this weighting. Simply
averaging action percentages at each node would generally describe a different
strategy.

The query exporter provides observable ancestor links: earlier own decision,
taken action and legal menu. Every ancestor must be in the bounded query batch.
The reader checks actor, menu, action bounds, chronology and complete prefix
consistency. Inference still receives only visible features; history links are
used to calculate reach, not to reveal future cards or opponent cards.

Model pairs stream through one at a time. The reader keeps accumulated action
numerators and reach denominators, rather than all models' query policies at once.
Zero own-reach support is explicitly returned with a uniform placeholder, not
treated as observed policy evidence. The actual ordinary-CFR bank includes the
uniform initial model and only models that were played; the unused final fit is
excluded.

## Registered control

The test reads played generations 0 and 1 from the completed-iteration-2
checkpoint. Generation 2 is the unused next model and is excluded. It exports
3,640 physical observations with 13,392 own-history links from eight fresh-deck
deals. The source networks come from the tiny checkpoint control and are not
strategically qualified.

The streamed Python average matches the independently reconstructed Rust
own-reach average within 2.23e-16 for both probabilities and support. For four
physical deals, the control separately enumerates every pairing of one fixed
model per player, drawn independently at the root and held throughout the hand.
That mixture and the streamed behavioral average agree on 2,408 terminal outcomes
within 2.78e-17. A naive percentage average differs by as much as 0.3333 at a
queried decision, confirming that the weighting is materially exercised here.

Three malformed histories and two wrong model-count cases are rejected. The
caller RNG is preserved, 18 registered inputs are verified and all output hashes
are recorded. The CPU control took 1.00 seconds. Production and the preview are
unchanged. Materializing all per-model probabilities is confined to this tiny
independent oracle, not the streaming reader.

## Remaining scope

The reader is ready to support the next independent policy evaluation. CUDA
execution of the complete average reader and large-bank resource use are not
qualified by this CPU result. No new exploitability bound or useful player range
follows from the mixture identity. The finite learning-method comparison,
combined CUDA pipeline control and substantive physical training pilot remain
separate gates.

Evidence prefix: `sampled-physical-bank-bridge-v1`.
