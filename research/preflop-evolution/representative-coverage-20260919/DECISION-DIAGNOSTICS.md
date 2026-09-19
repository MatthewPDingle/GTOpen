# Understanding the range differences

This is an additional descriptive analysis, prepared before any reserved
strategic outcomes. It does not change the registered experiment, convergence
gates, source policies, board selection, or running queue.

Action frequencies alone do not tell us how serious a disagreement is. Two
actions may have almost the same value, making a large frequency change cheap.
Alternatively, a small number of hands can account for substantial lost value.

`tools/research/transfer_decision_diagnostics.py` reads a **complete** panel of
saved transfer workers. It first runs the existing independent accounting and
exact source-policy checks. It then reports, for each supported opener hand:

- Its share of the entering range and current call frequency.
- The value difference between calling and folding.
- The difference between the two best class-average action values.
- The potential gain from changing only the entering action, with all later
  actions fixed, and its contribution to the whole range's gain.

The entire future-board panel is averaged before choosing an entering action.
Opponent actions are already included in the saved counterfactual reaches.
Later own actions remain at their frozen policy; this is deliberately a
root-only diagnostic, not another unrestricted best-response estimate.

Class-average margins describe the average value of each action. The gain
calculation retains individual physical combinations before averaging, so
suit-dependent choices are not silently replaced by one action for the class.
It reconciles the current value with the audited aggregate and requires the
root-only gain to lie between zero and the full OOP deviation, within the
existing numerical tolerances.

## Limits on interpretation

These are values against the particular evaluated opponent and postflop
continuations. Both players' policies differ between source solves; raw EV
differences are therefore not a head-to-head ranking of source strength.
Off-path continuations may be poorly determined. The numerical postflop
residual remains visible and must be considered before interpreting tiny
action margins. A small margin is not a confidence interval or proof of a
full-deck equilibrium mix. The larger study still freezes earlier entry
ranges and omits earlier folded-card posteriors.

Use this report to locate and explain sensitivity, then select a new,
separately registered investigation if necessary. Do not tune the current
reserved panel or choose a production policy from attractive-looking hands.

## Verification and execution

`transfer-decision-controls.json` records CPU-only validation against four
existing deterministic river controls, plus artificial values that detect
accidental optimization of later own actions and premature hidden-chance
maximization. No new reserved strategy outcomes were accessed.

The command takes these positional arguments:

```text
python tools/research/transfer_decision_diagnostics.py SUBTREE MANIFEST SOURCE OUTPUT_PREFIX WORKER...
```

Use the original manifest, matching frozen source, and every per-board worker
for one completed panel. Gzipped worker results are supported. Exclude the
combined aggregate result from the worker arguments. Output paths must be
unused. JSON and Markdown reports are written; no solver or saved game is
modified. Run after the queue finishes a complete source/panel evaluation.
