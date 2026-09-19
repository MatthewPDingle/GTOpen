# Broader reference and independent transfer: overnight registration

Registered after the successful 47-board allocation/timing trial and before
training the 47-board reference or accessing any reserved strategic results.
No live app changes or production deployment are part of this study.

## Runtime evidence and budget

The 20-iteration trial passes the independent physical-card and chip/rake
audits. It retained at least 64.90 GB free host RAM and 17.47 GB free GPU RAM.
Its first-to-last checkpoint slope is 16.734 seconds per iteration, including
the second evaluation. Extrapolation gives 33,539 seconds (9.32 hours) for
2,000 iterations; this is an uncertain short-run estimate. The old two-board
paging run reproduced every original checkpoint exactly through 2,000.

Run the frozen `report-47.json` game from scratch for exactly 2,000 iterations
using the fully enumerated, unprojected paged executable. Record its existing
1, 20, 100, 500 and 2,000 checkpoints. Stop the owned child after 39,600 seconds
(11 hours), on insufficient resources, or if production becomes active.
Keep any incomplete output, label it incomplete, and do not silently use an
earlier checkpoint as the preregistered source.

Require the registered physical-pair audit, terminal probability within
1e-5, chip/rake conservation within 1e-4 bb, and combined full deviation gain
below 0.01 bb at iteration 2,000. If that convergence gate fails, retain the
result and stop the subsequent comparison queue for review. Do not loosen
the threshold or select the most attractive intermediate range.

## Frozen-policy implementation gates

Complete all controls in TRANSFER-CONTROLS.md and
STREAMED-TRANSFER-PROTOCOL.md before starting the broader reference. In
particular, compare the two-board streamed evaluator with its paged version
at 2,000 iterations. Source policies must stay bitwise unchanged; EV and
both kinds of gap must agree within 0.0001 bb, root frequencies within 1e-7.
Any failure stops the queue. Preserve failures and correct implementation
issues in a separately recorded retry; do not tune an evaluation to pass.

Implementation revision before any reserved outcomes: attempt 2 caught
one-to-two-ULP changes during JSON probability import. Attempt 3 uses the
dedicated exact-roundtrip transfer build and adds short full-policy import
checks before repeating the original controls. See TRANSFER-CONTROL-RETRY.md.
The existing reference binary, chance panels, thresholds and iteration
targets are unchanged. A new parent queue registration records this revision.

Controller-only revision: use the same three production status routes at
127.0.0.1 instead of localhost. On this machine the latter adds about two
seconds per request; direct loopback avoids the connection fallback. The
strict allowed states, report-running check, timeout, memory reserves and
owned-child termination behavior remain identical. Both wrapper and base
guard are frozen by the outer registration. No server/network setting changes.

## Independent transfer runs

Freeze the exact 2,000-iteration source results for the existing original
ten-board AB solve and the new 47-board reference. Evaluate BOTH unchanged
sources on BOTH the original reserved ten boards and the independently
registered 95-board sample. Selection, weights, private entry policies,
support cutoff, investments, rake, action menus and suit averaging remain
as specified in HOLDOUT-PROTOCOL.md and VALIDATION95-PROTOCOL.md.

With every preflop policy frozen, train each board's two postflop continuations
for exactly 2,000 iterations. Use the validated resident streamed evaluator,
then combine all per-hand terminal CFVs before preflop best-response
maximization. Preserve compressed leaf-value artifacts with hashes. Do not
average per-board maximized preflop values. Limit each owned worker to
900 seconds; the complete overnight sequence stops starting workers after
09:00 Adelaide on 20 September 2026. This is a compute budget, not a promise
that every panel finishes before the user returns.

For each complete source/panel pair require the same independent accounting
checks and aggregated restricted postflop residual below 0.01 bb. Report
unrestricted full deviation separately; it is intentionally not a numerical
convergence gate. If the postflop threshold fails, retain the result as
numerically incomplete and stop the queue for review. Do not selectively
extend boards based on strategic preferences.

Report both players' EVs, full deviation gains, postflop residuals, root
frequencies under each panel prior, and source-policy sensitivity under a
common prior. Do not select a production policy based only on the best
looking panel. These finite chance/menu games omit earlier folded-card
posteriors and are not full-deck accuracy certificates. Original reserved
and new eligible-complement samples have distinct interpretations.
