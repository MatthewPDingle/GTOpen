# Continue after the completed sequence audit

The version 2 general sequence audit passed and exactly reproduced the bounded
audit's counts and reported maximum discrepancies. It checked two generations,
eight boards, 1,024 physical roots and 35,100 postflop targets in 169 seconds.
That completed audit is reused; no training or sampling is repeated.

A prelaunch inspection found that the first resource wrapper's helper-import
order initialized BLAS with one thread rather than the original trainer's two.
Only the dispatcher was stopped, while the independent audit was allowed to
finish. Candidate training had not begun. The stopped dispatcher and its
source registration are preserved in an explicit controlled-stop record.

The version 2 resource wrapper initializes NumPy before helper imports and
explicitly sets a two-thread context around the original scientific driver.
Its mechanical control verifies both normal and exceptional dependency
restoration and the two-thread setting. The qualified inventory replacement
and all original scientific/storage/resource gates remain unchanged.

The version 3 dispatcher requires the completed, source-bound sequence audit,
the earlier completed pipeline review and the wrapper's updated control. It
then runs the original CPU/CUDA policy-bank control, the unchanged matched
two-generation prefix through the corrected wrapper, and the version 2
independent prefix audit. It stops on a failure for inspection and preserves
all evidence. It ends before full-study storage admission or further training.

The experiment still uses the original seeds, budgets, model definitions,
endpoint and registered comparison. This scheduling recovery does not change
production or establish improved playing strength.
