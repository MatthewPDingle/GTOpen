# Curated production qualification

Before final production outcomes: qualify source53ce9de with the strict Reference-only mode. Retain paired full50 early-off/early-on, exact native/gap/EV comparison, matched20,000-sample cache and frozen eight-seat input; then exercise the full-model small stop/evaluate/save/reload/resume lifecycle. All numerical gates remain unchanged.

Use an explicit480-second cap per large case and the unchanged240-second small cap, plus120 seconds reserved for setup/cleanup. The earlier API-c cases completed in327.125 and329.469 seconds respectively, so480 retains more than45% margin while allowing final qualification within the four-hour window. Default research protocols remain600 seconds. A cap failure stays a failure/incomplete result; it does not authorize changing the expected strategy or skipping parity. The helper's02:53:27UTC deadline is unchanged.

Pin the final curated executable SHA from the production build manifest and pass --production-reference-only --large-case-seconds480 with a new run ID. Verify its final Reference native SHA also matches API-c/standalone (6162be87527d2263ad1655c6565b91f8805d169190f99ec18c8eae0a15b51a5e), not only the two new cases against each other. Source/web provenance must come from the curated worktree. Browser smoke follows using its fresh full-model small input; no experimental model choice may appear.

Scheduling allowance recorded before final API results: the paired Reference cases and the small lifecycle case may run as two separately named invocations if the combined reservation no longer fits. Both remain required before installation, with identical case caps, numerical checks, runtime SHA and helper deadline. This splits reservations only; no incomplete case is accepted or omitted.
