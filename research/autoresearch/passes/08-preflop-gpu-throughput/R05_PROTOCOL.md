# R05: combined C23 and C24 app release

Registered before integration, 2026-09-14. User authorized deployment to 56708
after integration checks, then pausing research for a later overnight run.

Keep the qualified C23 shared path. Promote compatible ordinary fallback engines
using C24 with their original batch, samples, allocation plan and arithmetic.
Promotion owns private state; failure drops it and rebuilds the ordinary engine.
Do not change CUDA source or sample grouping. No new optimization credit.

Qualification: selector success and actual allocation-failure recovery; existing
C24 numerical/stop/reload tests; existing C23 tests; native GPU, default solver
and server tests; archived kernel equality. Each build/test is serial and guarded
by run07, initially capped at 300 seconds (release build 600 seconds).
Use a frozen test binary for saved-game checks, including the current native
batch-4 game, capped at 600 seconds per continuation. Compare checkpoints and
full arena fingerprints to frozen C24 results. Verify the release on isolated
56710 including real stop/save/reload behavior before replacing the idle app.

Save both live sessions and verify PID/path and no running reports before the
restart. Restore sessions and compare node results. Keep rollback executable and
backups. Push evidence and a restart guide; leave dashboard available, launch no
new experiments, and leave recurring research scheduling paused.
