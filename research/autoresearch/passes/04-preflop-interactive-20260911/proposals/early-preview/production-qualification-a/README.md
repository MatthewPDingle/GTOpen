# Production compilation and test evidence

Source `53ce9dec08de9fa2f93f246d7f5efcccc8c22c68`; completed `2026-09-11T02:30:48.975956+00:00`.

41 frozen test executables plus one doctest invocation completed successfully. Counts: {'passed': 232, 'failed': 0, 'ignored': 5, 'measured': 0, 'filtered_out': 90}.

| Group | Passed | Failed | Ignored | Filtered |
| --- | ---: | ---: | ---: | ---: |
| gpu_solver | 20 | 0 | 0 | 81 |
| gpu_server | 12 | 0 | 0 | 9 |
| cpu_solver | 181 | 0 | 5 | 0 |
| cpu_server | 19 | 0 | 0 | 0 |
| doctests | 0 | 0 | 0 | 0 |

Every test log is copied alongside this summary. `summary.json` pins its SHA, original path, exact command/cwd, duration and frozen executable SHA. Binary hashes were rechecked while collecting this report. Large compiler JSONL and EXEs remain in the private qualification directory, with their paths/provenance retained.

API, UI and deployment are not established by these results.
