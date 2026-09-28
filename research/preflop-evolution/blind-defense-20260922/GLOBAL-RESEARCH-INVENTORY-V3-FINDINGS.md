# Faster storage accounting preserves the measured budget

The candidate inventory scanned the same 468,268 files and returned exactly
the same per-root file counts, logical bytes and allocated bytes as the original.
The original took 189.797 seconds. Two candidate scans took 34.829 and 35.453
seconds: 5.45x and 5.35x faster for this accounting step. This is not a solver
speed measurement.

The candidate binds the Windows allocation API once, reuses directory-entry
metadata and resolves root paths once. It retains activity, time, allocation,
reparse-point and unavailable-input checks. Negative controls passed for an
unavailable activity check, relative root, file instead of directory, missing
root and directory reparse metadata. The reparse control used mocked metadata;
it did not create an actual junction. Earlier evidence was not changed.

Sources are global_research_inventory_v3.py and the successful control wrapper
global_research_inventory_control_v4.py. The first control wrapper, v3, had a
Python syntax error from using the reserved word `pass` as a keyword argument.
It failed before imports, scans or registration. Its source is preserved and
hashed by the successful registration; v4 uses `pass_condition` instead.
No successful evidence is attributed to that failed invocation.

Evidence: global-research-inventory-v3-registration-v2.json (SHA256
320fcfb44a79f5068fd856925b0e524ed5fcb9ce5176194dd5ed10ca39c19e7a) and
global-research-inventory-v3-control-v2.json. The successful control completed
in 260.109 seconds. All three scans covered S:/GTOpen-research,
T:/GTOpen-research and T:/Dev/GTOpen/research.

The new training-budget experiment verifies this evidence and its source hashes
before using the candidate. Previously executed inventory implementations remain
unchanged. No production application changes, deployment, deletion or new
GitHub push are part of this qualification.
