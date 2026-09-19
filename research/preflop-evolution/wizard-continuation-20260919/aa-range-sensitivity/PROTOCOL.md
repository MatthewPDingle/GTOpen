# Material AA inclusion: registered range sensitivity

19 September 2026. Exploratory development case, not held-out validation.

The original prepared UTG calling range includes AA at weight 0.001. The
tenfold floor check was stable, but still added less than 0.3% range mass.
That does not test the opponent's postflop adaptation to substantial AA traps.

Keep all inputs fixed except AA's normalized OOP range weight. Test 0.25 and
1.0, preserving every other hand weight and the entire LJ range. These are
relative range weights, not literal probabilities of calling at the preceding
preflop decision. Record their actual fraction of OOP combination mass.

Repeat all 40 registered flops under both existing menus for each variant
(160 solves). Same GPU and full-enumeration CPU global gap <=0.05% pot;
every original OOP probe's BR gain <=0.05bb; at most 5,000 iterations.
No changed threshold or silent removal of failed references. Check production
idle before every independent offline solve. Never modify its session.

Primary outcome: paired change in AA's explicit continuation value versus
the precision-refined original. Also report effects on all seven other probes.
Use the same 5,000 stratified paired bootstrap draws, compatible pair masses,
isomorphism weights and inclusion probabilities as the original panel.
Recalculate the fast baseline on each changed range for accounting only.

A falling AA value would demonstrate sensitivity to being a meaningful part
of the range. A stable value would show that this specific postflop adaptation
does not explain the gap. Neither outcome establishes a new preflop solution:
LJ's preflop actions, other UTG hand frequencies and all alternative branches
remain fixed. Intervals cover sampled-board variation only. No Wizard target
is fitted, and no production change follows automatically from this study.
