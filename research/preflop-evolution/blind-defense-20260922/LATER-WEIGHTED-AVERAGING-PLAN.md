# Fixed fresh-bank averaging experiment

Prepared before control and training on 23 September 2026. This implements the
prospective design in LATER-WEIGHTED-AVERAGING-DESIGN.md. No result is available
at registration. No previously inspected generation is reweighted or selected.

## Fixed intervention

Use the unchanged visible 302-input training algorithm, direct preflop tables,
512 fit steps per player, 262,144-record reservoirs, and fixed BB-versus-BTN
200 bb game. Train exactly 78 updates of 512 new physical deals. Seeds are:
sampler 121301, action 121302, reservoirs 121303/121304, fit base 121305.
The separate four-update execution control uses 131301–131305 in the same roles.

The previous cache covered only the previous training sample. Load the audited
complete 47,478-canonical-pair cache so fresh private pairs receive the same
exact board-enumerated labels. There is no new equity approximation or missing-
pair fallback. The full cache's population, source and artifact hashes are checked.

Training targets, fits and sampling remain equally weighted as before. Form two
outputs from the same complete played bank: generation weights 1 for equal;
weights g+1 for later-weighted, g=0..77. Both players use the schedule, with
own-action-reach weighting at later histories. Generation 78 was not played and
is excluded. Keep all played policies; no cutoff or weight tuning is permitted.

## Admission and exact screen

Before training, pass the weighting test using independent scalar history
arithmetic and CPU/CUDA comparisons. Pass the four-update fresh-run replay,
including dealt cards, action random states, reservoirs, table contents, model
bank order and checkpoint restoration. Controls do not establish poker quality.

After full training, replay and audit it, then construct both output policies.
Compare complete CPU/CUDA catalog probabilities for all 169 BB and 96 supported
BTN classes. Evaluate all four combinations of equal/linear BB and equal/linear
BTN, with the complete private-pair population and exact board cache. For each
pair recompute BTN fold/call and BB fold/shove values under that pair's opponent.
No reuse of opponent-dependent old values is allowed.

Report both unilateral gains separately for every pairing, and all hand-class
rows. The BB test preserves call/ordinary-raise probabilities. These gains are
restricted lower bounds on available improvement, not full exploitability.

The practical screen passes only if both gains for the linear/linear pair are
at most 75% of the corresponding equal/equal gain. If a baseline is below
1e-10 bb, require the new value to be at most 1e-10 for that endpoint instead.
Publish cross-pairings regardless of outcome. There is one new seed run; no
claim of seed robustness or cross-context accuracy follows.

A passing screen authorizes preparation of the separately registered wider
call/raise/postflop evaluation. It does not authorize promotion or deployment.
A failing screen ends this candidate's automatic evaluation path; preserve all
results and assess the cause before further training changes.

## Resource and stopping rules

Full training: at most four hours and 40 GB stored, exactly 78 updates if complete.
Control: at most 20 minutes, four updates. Full replay: at most 20 minutes.
Exact evaluation and its independent arithmetic review: at most 20 minutes each.
Maintain 20 GB host RAM, 3 GB VRAM for GPU work, and 40 GB free SSD. Stop on
production activity, integrity/numeric failure, resource limit or deadline.
Preserve completed immutable checkpoints and failed attempts; no automatic retry.

The runner's registration records byte hashes of source, prior evidence and this
plan. Freeze all executable evaluation sources before full training admission.
Production 56708 and the range preview remain unchanged throughout.
