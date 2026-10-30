# Eight-worker audit check

The user's available 16-core CPU warrants checking more parallel audit workers.
A read-only two-generation audit was repeated with eight workers while the
registered trainer continued. Admission found 9.6% system CPU use and over
48 GB available RAM. The audit used no GPU and changed no production state.

The eight-worker run passed in 30.375 seconds. The earlier four-worker control
took 44.359 seconds: an observed 1.46x throughput ratio. These runs happened at
different times during live training, so this is preliminary evidence rather
than a controlled or full-arm speed claim.

The checked outputs agree exactly: source registration, endpoint checkpoint,
1,024 root reconstructions, 23,962 postflop targets, reservoir insertion counts,
and all maximum numerical errors. The comparison artifact lists the exact
fields and hashes both source results.

The already registered complete-audit queue keeps its four workers. Eight is
now a qualified candidate for a future queue version, subject to available
resources and full-arm verification. Do not launch a duplicate full audit or
change the four-worker result's identity to claim eight-worker qualification.
