# Saved UTG versus LJ: conditional two-player adaptation

Registered before exporting or solving this experiment. Research only; no production writes.

Use frozen `wizard-nl25-baseline-20260919-refined.gtop` (SHA256
`5d3357ad4379871527af9916dd1313f585f709359331985c2ac23a24606fc190`),
path `[1,2,0,0,0,0,0,0]`. Preserve the entire remaining subtree, original
positions, incoming class distributions, investments, dead money, action menus,
configured rake, and Balanced terminal values. Export read-only, asserting arena
identity. No game saves, application changes, or reserved Wizard cases.

Compare two chance models: (1) independent incoming class distributions; (2)
the same distributions weighted by exact counts of compatible physical card
pairs and normalized once at the branch root. Earlier decisions remain fixed.
The six folded players' cards are excluded in both variants. Showdown equity
uses the same sampled equity cache in both, not newly exact board enumeration.
Non-all-in postflop values remain the fixed Balanced approximation.

Evaluate the saved policy and independently adapt both remaining players using
alternating CFR+ with linearly weighted own-reach average strategies. Run fresh
uniform initialization for both chance models, with checkpoints at 1,000,
10,000 and 50,000 iterations. For compatible chance also repeat with saved
policy used as an initial regret seed of weight one. This is an initialization
check, not a frozen-opponent solve. Preserve every checkpoint and failed gate.

Numerical acceptance: normalized nonnegative policies, terminal probability
within 1e-8 of one, expected net player utilities plus expected rake equal
original folded-player dead money within 1e-5 bb. Recompute exact best responses
to average policies separately from training. Target total response gain <=
0.001 bb conditional on reaching this branch; do not label unconverged results
equilibria. Raked play is not zero-sum, so CFR convergence is not presumed.

Record root action frequencies and per-hand policies/action values, including
AA and the LJ response to a jam (AKs, AKo, AQs, QQ, JJ). Cross-evaluate each
result under both chance models. Save hashes of inputs, exporter, runner and
binary before training. Report ranges and remaining limitations, not an
application deployment or a full eight-player equilibrium. CPU reference
timing is not a production performance claim.
