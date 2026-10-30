# E020 qualification R3 path-binding correction

This additive revision preserves all eleven frozen R2 input files except the single canonical holdout cohort report path in cumulative.py, which now points to runs/E020-wide-turn-holdout-implementation-r2/cohort/report.json. Protocol, numerical gates, order, original/candidate binary pins, all seven broader build outputs and control inventories are byte-identical.

R1 holdout build evidence and the premature runs/E020-qualification-plan/all-builds-ready.json remain untouched and invalid: the shared Cargo target reused E015 artifacts for the E020 holdout. No native holdout resource/cohort run had occurred. R2 holdout preparation uses isolated per-arm targets and is independently reviewed separately. The earlier holdout source PASS missed the cache-identity failure.

Do not rerun build.py: all seven broader binaries already built successfully and remain valid at their existing paths with their original build manifests/authorization. This revision needs a new root authorization in this directory, bound to this prepared manifest and the additive independent review; its new HERE requires a fresh all-builds-ready.json and eventual qualification-ready.json here. Neither old authorization nor old readiness is copied. Root will list the unchanged broader binaries plus the new R2 holdout binaries/manifests after both arm builds are terminal.

Execute controls/cumulative/assess only under the original gates. No script was imported or executed for this revision. Validation was Python AST/JSON parsing plus exact byte comparison; no builds, GPU jobs, native tests or production edits. The copied README is the preserved R2 instructions; this revision note supersedes its already-completed build step.
