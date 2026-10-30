# Shared stack-aware model: first implementation contract

This separate research policy format joins the existing 302 visible-card/history
inputs to the checked 60 public stack/price/action inputs. The same two player
networks can evaluate several registered equal-stack BB/BTN contexts. Context
hashes route exact tables and histories; hashes are not network features.

The registry binds exact context source, public ledger, training/held-out role
and feature layout. A query must match its explicitly selected context, every
public actor/street/legal menu, and the visible key reconstructed from its card
and history features. Hidden batch text and opponent private cards are not read.
The existing own-action-history validator is retained. Each batch belongs to
one context; grouping or caching must use (context hash, hi, lo), never hi/lo alone.

Model objects have a new policy type and 362-input parameter layout. Direct
weighted preflop tables are keyed by fitting context and player. A missing table
uses that shared network; held-out contexts cannot own learned tables. Training
preparation explicitly refuses held-out contexts. A policy mixture still uses
own-history reach, including each model's context-local table overrides.

Targets in the future shared fitter will be advantages in bb divided by that
context's starting stack. This positive context-constant scaling leaves regret
matching unchanged and is recorded in model metadata. It does not by itself
choose the sampling/objective weights or establish good cross-depth learning.
That training objective and equal-compute comparison need a separate plan.

The initial model is uniform over legal actions. Model objects can be saved and
read with content hashes and full registry validation. This is **not yet a
resumable training checkpoint**. Before a shared training pilot, store separate
sampler/reservoir/accumulator states by context and bind the shared played bank
to complete cycles covering all fitting contexts and both players. Preserve
per-context source-deal weights and reject incomplete or mixed boundaries.

The first control will use retained native geometry at 20/40/60/100/150/200/400 bb
and two retained physical deals. It will export native visible observations for
those games, check feature/key/table separation and model-object roundtrips, and
exercise synthetic networks. These are implementation checks, not trained ranges.
Keep 60 and 150 bb outside any fitting or model selection. Their geometry may be
used to test the interface without inspecting strategic training targets.

The fixture incoming ranges are uniform and must not be mistaken for learned
preflop priors. No old models or studies are migrated. Production is unchanged.
