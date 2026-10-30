# Preserve completed maturity snapshots if more space is required

This bounded follow-up preserves the four historical binary snapshots in
`S:/GTOpen-research/hu-wide-maturity-v1`, at iterations 4, 100, 500 and 2000.
Their total logical size is 13,761,477,472 bytes. The successful historical
`wide-maturity-v1-review.json` contains all four original SHA-256 hashes.

The operation uses the already qualified Windows transparent LZX method and
the same full before/after hash, size, modification-time and path checks as
the replay preservation. It rejects redirected paths and shared hard links,
uses four low-priority workers, holds the research lock and respects production
activity and free-space guards. Each file has a ten-minute limit; the whole job
has a one-hour limit. No deletion, relocation or content conversion is allowed.
Only the operation's own mutable progress status uses explicit replacement.

Run only after the replay preservation exits and its readback finishes. The
separate maturity readback verifies all original logical bytes and reconciles
every allocation receipt. Actual savings, not projected compression ratios,
must determine whether another full-study storage admission can succeed.

This changes physical storage and future I/O timings, not saved strategy or
range accuracy. Preserve historical timing evidence with that caveat. It does
not repeat native checkpoint restoration or change the current study's fixed
learning budget, evaluation sample or 800 GB allocation ceiling.
