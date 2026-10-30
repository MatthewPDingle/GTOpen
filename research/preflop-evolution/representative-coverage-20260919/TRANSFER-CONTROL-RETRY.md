# Transfer control attempt 1

Both paged and streamed always-fold river controls passed all solver and
independent accounting checks. The single-board Python aggregation then
failed with `KeyError: hands`: the synthetic control source deliberately
contains only its policy, not the optional display summaries. No strategic
reserved boards were accessed. The correction derives hand labels directly
from the documented class order. No numerical formula or tolerance changed.

The first queue source and terminal status are preserved as
transfer-controls-v1.py and transfer-controls-v1-status.json. Per-worker
freezes, snapshots, logs and results remain under the original names.
The corrected queue uses transfer-v2-* outputs and a new parent freeze;
all controls are rerun before the longer two-board comparison.

## Attempt 2: exact probability import

The paged two-board solve reached 2,000 iterations with restricted postflop
residual 0.0013586882 bb and full deviation 0.0026439076 bb. Its exact source
policy identity audit FAILED: 820 values differed by one or two IEEE ULPs,
with maximum absolute difference 1.1102230246251565e-16. The solver's own
bit check showed its imported array was unchanged during learning; the
difference occurred when decimal JSON was initially read.

A regression using two actual offending values reproduces the error with
the default JSON parser. Enabling serde_json's `float_roundtrip` makes that
regression pass. The dedicated `continuation-transfer-research` Cargo
feature enables exact parsing only for the two transfer examples. Ordinary
preflop-research, the existing reference binary, and the production app are
unchanged. The passing reference/paging evidence is not replaced.

Attempt 3 uses newly built transfer binaries and new `transfer-v3-*` outputs.
It first imports the full nontrivial development policy in short river
runs with BOTH binaries and checks every probability bit externally. Then
it repeats the deterministic controls and full two-board comparison. All
numerical thresholds, source policies, boards and iteration targets remain
unchanged. No reserved strategic outcome was accessed. Parent controls and
the waiting overnight queue both stopped normally on the failed gate;
their terminal states and registration hashes are retained.
