# Operational adjustment

19 September 2026, during the probe-floor sensitivity batch.

The read-only production-idle checks through `localhost` each took about
2.06 seconds. The identical endpoints on `127.0.0.1` took 0.000-0.016 seconds
and returned the same states: preflop done at iteration 1500, postflop idle at
iteration 0, reports not running. Both address the same production listener,
PID 26496 on port 56708. The delay is consistent with local address fallback;
no network or server configuration was changed.

Change only the research Python status-check URL to explicit IPv4. Preserve
all three checks, their timeout, and the wait-if-busy behavior. The existing
floor runner retains its already imported function. Restart only the waiting
four-bet pipeline to pick up the faster checks before it begins. Its frozen
numerical inputs, binary, protocol and source remain unchanged. There are no
reference result or model changes from this operational adjustment.
