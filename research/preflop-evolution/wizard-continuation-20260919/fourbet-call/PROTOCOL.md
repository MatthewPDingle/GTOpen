# Called four-bet continuation

Registered after the original call-branch first pass and read-only premium
branch audit, before these references. Test the branch directly involved in
AA's 4-bet-versus-jam discrepancy: UTG opens 6, LJ raises 18, six players fold,
UTG raises 45, LJ calls. The pot is 93.5bb and remaining stacks 155bb.

Use the same saved 1000-iteration game and freeze both arriving ranges. Keep
the original 40 sampled boards, two separate menus, rake and convergence
checks. Normalize, trim below 0.005, and add the same OOP probes at 0.001 as in
the parent protocol; record all mass changes and require each below 0.5%.
AA naturally has material weight in this 4-betting range, unlike the original
calling range. Other low-weight probes remain sensitivity-limited.

Independently reproduce the fast pricing formula in double precision. Check
all 338 original call-branch prices against the frozen Rust implementation
within 0.0001bb before preparing this study. Validate original AA four-bet
pricing against the saved action-value decomposition separately.

Run 80 offline references, requiring GPU and materialized CPU gaps <=0.05%
pot and every OOP probe's best-response gain <=0.05bb, at most 5000 iterations.
Stop for review on failure. Use the parent's direct compatible-mass estimator,
secondary sampled-equity control and 5000 paired stratified bootstraps.

This is a fixed-policy sensitivity test, not a replacement preflop equilibrium.
Changing a continuation estimate would change earlier ranges and responses.
Do not label a substituted value as a solved improvement or Wizard-equivalent.
AA's tree also contains all-in branches, whose pricing is not changed here.

Wait until the parent precision and floor-sensitivity batches finish. Check
production is idle before each GPU job. Never modify port 56708 or reserved
Wizard cases. Preserve manifests, inputs and all failed references.
