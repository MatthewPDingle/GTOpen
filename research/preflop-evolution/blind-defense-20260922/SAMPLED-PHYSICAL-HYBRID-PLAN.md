# Direct preflop targets, learned postflop continuations

Prepared follow-up, not an admitted or executed training experiment. The current
dense neural trial must finish and receive its independent training audit first.
The hybrid CPU/CUDA control must also pass before this trial may start. Complete
the dense candidate's independent evaluation before occupying the GPU again.

## Question

Does removing neural fitting error at observed preflop information sets improve
the BB-versus-BTN policy? The old pilot's retained root targets and the network's
predictions disagreed materially. That does not make the targets true action EVs:
they are noisy sampled historical advantages under changing strategies.

Keep the dense trial's complete game, incoming ranges, 78 updates, 512 deals per
update, eight frozen 64-deal subbatches, seeds, reservoir capacity, network sizes,
512 full-gradient fitting steps, optimizer, and ordinary-CFR averaging. Rebuild
both networks exactly as before, including all retained preflop examples. This
isolates the policy representation rather than also changing the fitting loss.

After each completed update, group retained preflop visits by exact visible
information set. Use their count-weighted mean advantages directly for regret
matching. Unobserved preflop rows retain the neural fallback. All postflop rows
retain neural predictions. No hand-family smoothing, Wizard targets, hand edits,
or inspected test outcomes enter these tables. The reservoir's sampling error
remains; this is not an exact tabular-CFR solve.

Tables form part of each saved policy and must affect its own-action reach when
averaging. Save the new format explicitly; old network-only readers must reject
it. Average every played generation 0-77; exclude the unused generation 78. No
checkpoint selection, late-window substitution or visual promotion is allowed.

## Execution and assessment

Run from the uniform policy with a three-hour cap, 40 GB store cap, and reserves
of 20 GB host RAM, 3 GB VRAM and 40 GB SSD space. Production activity stops the
owned research workers. Do not restart or extend an incomplete run automatically.
The same chance prefix is shared with the dense trial; these are controlled
variants, not independent training replications.

The training reviewer must replay all deals, action seeds and reservoir inserts,
reconstruct every generation's preflop table, and check every supported preflop
policy row against its stored table. Native reference evidence and all artifact
hashes must agree. This does not independently rerun neural optimization.

Proposed separate evaluation streams are 69101 for 8,192 response-training deals
and 69102 for 16,384 held-out deals, minimum 16 observations per root class. These
are reserved only when the training registration is written. Freeze the responder
before test sampling. Use the same five comparisons and bounded paired intervals,
one final look, and fresh CPU/CUDA numerical controls. A smaller measured root
deviation would support progress, not certify full equilibrium or Wizard parity.

Neither production nor the range preview changes as part of this experiment.

## Preparation status

The separate trainer and reviewer are prepared, not run. The exact policy helper
used by the trainer passed its CPU control on 7,277 existing query observations
for each of three fixture policies. Both learned fixtures matched all 77 table
queries exactly; all 7,200 postflop rows remained unchanged. Initial, missing-row,
context, format and player-table dispatch behavior passed too. This establishes
dispatch correctness on the fixture, not training accuracy. The separate frozen
GPU averaging control has now passed. Its independent CPU reconstruction matches
to less than 5e-16; the GPU policy difference is below 3.7e-5 and native payoff
difference below 1.8e-6 bb on the synthetic fixture. This is numerical validation,
not evidence that a trained hybrid plays better.

The hybrid-specific evaluator and final readback are prepared before training
admission. They preserve the dense trial's fixed-count test, response selection,
and interval arithmetic, while explicitly loading version-2 policies including
their preflop tables. The first 256 response-training deals will be checked
against CPU averaging before drawing the held-out stream. No hybrid evaluation
has run yet. The evaluation sources are frozen in the training registration so
the assessment does not change after seeing the trained candidate.
