# Supplementary opponent-response diagnosis

Prepared after hybrid training and while its original evaluation is running.
No partial test outcomes were inspected to prepare this check. It is an extra
diagnostic, not part of the registered five-comparison confidence family and
not a fresh independent confirmation. The original experiment is unchanged.

The original evaluation subsequently stopped on a numerical control. This
diagnostic now targets only the separately audited float64 evaluation v2,
described in [the numerical repair](HYBRID-NUMERICAL-REPAIR.md). It will not run
against the partial v1 results.

A lower BB root-response gain can coexist with a weak BTN response to BB jams.
Apply the same diagnostic used for the dense candidate, after the complete
hybrid evaluation and its independent readback pass. Read all 8,192 existing
response-training deals, select BTN's class-based fold/call response using BB's
jam-reach weights, then read all 16,384 existing test deals. Retain the original
policy for classes with fewer than 16 training observations. Ties choose fold.

Only BTN's response at the node facing BB's initial jam changes. Every other
decision stays fixed. Independent five-card enumeration checks all 24,576
showdowns against the native forced-jam values. Report gains per original spot
entry, jam reach, conditional calling, and every observed hand class. Sparse
class outcomes remain diagnostic; do not patch hands or tune the next trial.
The separate arithmetic readback reconstructs response selection and weighted
gains, and rechecks source hashes without rerunning the showdown enumeration.

The prepared sources preserve the dense diagnostic's executable method exactly;
only source/output identities and descriptive text differ. Both scripts compile.
Their actual execution and readback remain pending. Current uniform initial
policy averaging gives positive jam reach; this method does not claim support
for unrelated zero-reach contexts.

Run sequentially after the original hybrid evaluation audit finishes:

```powershell
& 'C:\Program Files\Python312\python.exe' tools/research/hu_sampled_physical_hybrid_btn_jam_diagnosis_20260923.py
& 'C:\Program Files\Python312\python.exe' tools/research/hu_sampled_physical_hybrid_btn_jam_review_20260923.py
```

Both entry points retain production-idle and resource guards. No GPU training,
production deployment or preview update is performed. The all-in-estimator
experiment retains its already frozen configuration and separate predeclared
BB and BTN evaluation families.
