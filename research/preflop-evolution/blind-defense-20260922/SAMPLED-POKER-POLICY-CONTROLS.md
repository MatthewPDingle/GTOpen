# Connecting observable policies to physical poker

Status: CPU policy-adapter and model-bank identity checks passed. These use
synthetic weights, not learned poker strategies. They prepare the physical BB
integration while the finite self-play comparisons run; they do not qualify
playing strength, CUDA inference or a production deployment.

## Policy inference and sampled updates

The adapter uses the [269-feature observable representation](SAMPLED-OBSERVATION-CONTROL.md)
with a 269–64–64–4 float32 network. A policy callback receives only the visible
observation key and legal action count. The separate simulator can evaluate
hidden hands and completed boards at terminal outcomes, but those cards are
not arguments to the policy callback. Legal actions are reconstructed from the
registered context and history before probabilities are returned.

Forty independently calculated NumPy examples agree with Rust inference within
1.79e-7 for network scores and 1.08e-7 for action probabilities, below the frozen
2e-6 tolerance. Four synthetic policy families exercise positive mixed scores,
all-negative highest-regret fallback, zero-score ties and a highest score in an
illegal action slot. The latter three use fixed synthetic output heads; they
are numerical controls rather than trained networks.

For 16 physical deals and both updating players, 128 traversals produced 3,617
records across preflop, flop, turn and river and all three postflop branches.
Their observation keys, action arities, record signs and sampled choices match
the frozen scalar reference. Maximum returned-value or record-value difference
is 2.85e-14. The test also verifies that every training record round-trips through
the observable encoder and that unused action labels remain zero.

The reference materializes 7,280 policy entries per synthetic family solely as
a verification oracle. The new traversal queries the policy as needed; it does
not require that table as its runtime representation. Evidence:
`sampled-network-adapter-v1`; 13 input hashes verified.

## Averaging saved models at an actual poker decision

The bank adapter derives a player's earlier own decisions from the fixed
preflop tree and postflop action history. Earlier observations contain that
player's cards and only the board available then. Each model is weighted by
its supplied iteration weight multiplied by its probability of taking those
earlier own actions. Opponent reach is not multiplied into this weight.

This prevents an unreachable hypothetical strategy from influencing the
displayed average later in the line. If all retained models have zero own
reach, the adapter returns zero support and a legal uniform fallback; the
fallback is not evidence of a solved policy.

The independent check selects one model for each player at the root and holds
each selection for the entire hand. For each of four physical deals it sums
all nine model-pair distributions, using unequal weights [1,2,4] and [3,2,1].
That terminal distribution matches the behavioral bank policy across 2,408
terminal outcomes in total, with maximum probability error **1.12e-16**.
Naively averaging action percentages at each decision fails the negative
control, differing by **0.01316** in terminal probability. A model that always
folds at entry correctly supplies no support at the later postflop query,
even when assigned weight 100.

Evidence: `sampled-poker-bank-v1`; 13 input hashes verified. The models include
an initial uniform policy and synthetic network/output-head policies. This is
an averaging identity check, not a learned equilibrium or exhaustive test of
all card deals. Global suit canonicalization is valid only under the registered
suit-symmetric context, and every model artifact must retain that context's
identity.

## Remaining work

The live finite experiments must still establish acceptable learning quality.
GPU observable-feature/inference equivalence and sampled-update integration
remain to be checked. Actual poker learning then needs a frozen budget,
resource admission, incoming ranges, action menus and independent evaluation.
No new BB ranges or changes to the experimental viewer follow from these
implementation checks alone.
