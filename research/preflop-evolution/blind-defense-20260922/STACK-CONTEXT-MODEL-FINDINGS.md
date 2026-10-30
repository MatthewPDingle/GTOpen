# Stack-aware model interface: implementation checks passed

Completed 2026-09-29. This qualifies an input/inference/model-object interface,
not learned ranges or a resumable training system. Production is unchanged.

The shared research policy receives the existing 302 visible card/history
features plus 60 public stack, pot, call-price and legal-action descriptors.
Exact context identities keep otherwise identical observation/table keys apart.
This permits a network to distinguish depths without treating arbitrary context
hashes as numeric inputs. Models remain tied to a checked context registry.

The native control reused two physical deals at seven equal-stack BB/BTN
geometries. It did not train a model or generate fresh evaluation deals.

| Starting stack | Role for future fitting | Observations | Public states |
|---|---|---:|---:|
| 20 bb | Fitting | 296 | 148 |
| 40 bb | Fitting | 526 | 263 |
| 60 bb | Held out | 622 | 311 |
| 100 bb | Fitting | 798 | 399 |
| 150 bb | Held out | 846 | 423 |
| 200 bb | Fitting | 910 | 455 |
| 400 bb | Fitting | 1,030 | 515 |

All 5,028 observations / 2,514 public states and 17,724 own-history links
passed. There were 3,996 collisions if context was omitted from observation
identity; all context-qualified keys were distinct. The old 302 inputs were
preserved exactly. The new public inputs distinguished all seven root depths.
Changing hidden batch text and target fields did not change model inputs.

Two synthetic model objects survived hashed save/load. Context-local test tables
were confined to their fitting contexts. Seventeen invalid cases were refused,
including wrong games, keys, actors, action counts, histories, held-out fitting,
held-out tables, changed registries and corrupt model references. These checks
are not proof against every possible malformed native history.

Maximum CPU/CUDA discrepancy was 4.44e-16. Mixture inference used each model's
own-action reach. On this deliberately synthetic case it differed from naive
model averaging by 0.148863; the reach calculation matched direct multiplication.
These numerical checks do not establish that either synthetic policy plays well.

An independent readback verified 156 source/evidence files, reconstructed public
inputs directly from ledger amounts (zero discrepancy), and recomputed recorded
root network/table policies (maximum discrepancy 1.67e-16). It used no GPU.

The control took 199.687 seconds including the global storage inventory. Peak
CUDA allocation was 35.58 MB; peak reserved memory was 56.62 MB. Its 11 compressed
evidence files occupy 1.36 MB allocated (2.98 MB logical). Light desktop GPU
sharing was enabled, with active production/heavy workloads retaining priority.

## What remains

- Actual fitting and model selection have not happened. Geometry/interface tests
  at 60/150 bb are not strategic generalization tests.
- Model-object persistence is not a training checkpoint. A shared trainer must
  preserve per-context samplers, reservoirs and accumulators, plus complete
  balanced-cycle boundaries and source-deal weights.
- Current fitting preparation expects native observations with own histories.
  Existing grouped reservoir rows do not contain those histories. Add an explicit
  versioned feature-only training adapter, or provide genuine native queries;
  do not invent empty inference histories to make the adapter run.
- Training loss, context weights and compute budgets need a prospective plan.
  The recorded stack-normalized target convention alone does not choose them.
- Incoming fixture ranges are uniform. These are equal-stack heads-up games;
  they do not establish full-table, unequal-stack or multiway play.

## Decision

Keep this completed interface as an engineering prerequisite. The earlier
RESEARCH-DECISION-CHECKPOINT.md and RIVER-MATCHED-CONTINUATION-DECISION.md still
require useful quality evidence before broad expensive self-play. The latest
reach-only evaluation envelope was too loose to justify another large test.
Accordingly, the next step is a bounded exact-reference learning diagnostic,
described in STACK-PRICE-REFERENCE-DESIGN.md. It is not a promotion of the larger
candidate or a claim that expanding stack coverage fixes its uncertainty.

Evidence:

- stack-context-model-control-v1-registration.json
  SHA256 c6f728a810612b77df1569c2afbc65eff92031cf92aabc81617da394df6f94bd
- stack-context-model-control-v1-result.json
- stack-context-model-control-v1-readback-v1.json
- tools/research/stack_context_inputs_v1.py
- tools/research/stack_context_policy_v1.py
- tools/research/stack_context_model_control_v1.py
- tools/research/stack_context_model_readback_v1.py

Executed sources and their registered inputs remain immutable. No new GitHub
push, deployment, application-session change or accuracy qualification follows.
