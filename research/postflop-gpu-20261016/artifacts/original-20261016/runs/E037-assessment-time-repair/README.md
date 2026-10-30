# E037 assessment-only timestamp repair

Preserve all original policy/source/build/run files and the failed assessment record. Root runs only:

`python -I -B assess.py ORIGINAL_POLICY_AUTH_SHA REVIEWED_REPAIR_MANIFEST_SHA`

The copied assessor/helper route through a copied guard that still verifies the original policy authorization and all original seals. The sole semantic repair treats each whole-second native started_at as an interval: floor(receipt)<=reported second. The original wrapper's checked absence of all seven run directories and its receipt-before-run sequencing establish order when timestamps share a second; rounded timestamps alone do not establish subsecond order. No blanket tolerance, chronology bypass, new native run or threshold change.

All original18/138 raw-result checks,1%/zero-repeatable-slowdown gates and publishing remain unchanged. The output records this repair manifest/policy and preserved failure. No outcomes were read while preparing the repair.
