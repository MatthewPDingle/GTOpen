# Changed-policy validation

This research-only follow-up is specified before its new reference outcomes.
It does not modify the app or train another model.

Only N09 or N15 candidates passing their registered fresh accuracy screen,
independent GPU oracle and repeated runtime target (at most 10% overhead) qualify.
For N15, choose the faster median of its serial and parallel implementations;
this choice uses runtime only, never new accuracy outcomes.

Resume repeat-zero ordinary and candidate policies from iteration 150 to 500,
with no additional warm-up. Compare the same inspected preflop nodes and record
action frequencies and per-hand probabilities. Five hundred iterations is a
fixed diagnostic budget, not a claim of convergence. The displayed gap holds
continuation values fixed and is not full-game exploitability.

Take both available heads-up BB-call leaves from each policy: versus the early
opener and versus the button. Freeze these four contexts, their provenance and
50 fresh stratified canonical flops before any new reference solves. Exclude
all boards already used or reserved in the earlier research manifests. The same
50 boards are used in all four contexts for paired comparisons. Preserve the
existing range cleaner: at most 0.1% removed combo mass and explicitly recorded
tiny probe additions. These cleaned ranges are not exactly the unmodified policy.

Generate 200 zero-rake heads-up references using the established restricted
postflop tree (half-pot bets, pot-size raises, one raise, no automatic all-in).
Require both CPU and GPU gap <=0.1% pot, full-enumeration query mode, legal pair
accounting, finite hand values and pot conservation. Use the unchanged reference
binary and <=2000 iterations. A failed audit stops the study.

Evaluate the frozen candidate on all four contexts. The fixed accuracy gate is
at least 15% lower weighted hand-value error than Balanced in **each context**,
and no context more than 10% worse than the previous conditional predictor.
Report paired 90% bootstrap intervals and rare-hand reference quality. No fitting,
threshold adjustment or selective dropping of contexts is allowed.

New ranges within a familiar source scenario test policy transfer, not untouched
scenario generalization. Success would still not establish agreement with GTO
Wizard, an exact multiway game, or a production-ready model. Experimental saves
retain Balanced metadata and must never be loaded in the ordinary app.

Execution uses a single controller, checks live-app idleness and actual research
process ownership before each GPU child, and respects the fixed 20:49:02 UTC
deadline. Do not begin a new candidate study with less than 60 minutes remaining.
No CPU fitting or numerical tests may overlap any GPU timing experiment.
