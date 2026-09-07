# Portable research setup

From any ordinary checkout, with Python 3.10+ and Git installed:

```sh
python research/autoresearch/research.py setup
python research/autoresearch/research.py verify
python research/autoresearch/research.py lab --help
```

Setup creates `target/autoresearch/workspace` at the published retained commit
and installs the plotting/process dependencies in `target/autoresearch/venv`.
It fetches missing research history from `origin`. Existing worktrees and
uncommitted experiments are preserved. Every path comes from this checkout;
the original machine path in `run.json` is historical metadata, not configuration.
You do not need to activate the environment or edit a drive letter.

`verify` needs only Python and Git. It checks the **recorded** source, frozen
workloads, patches, accuracy outputs and test logs. Its output is written to
`target/autoresearch/gpu-validation.json`, leaving the original evidence intact.
This is not a new benchmark or a claim that subsequent source edits passed the
historical suites. For a strict comparison of the current registered source
against that snapshot, run `python research/autoresearch/verify_gpu_pass.py`;
later source changes intentionally fail that comparison.

The `lab` action passes arguments to the measurement harness in the managed
environment. New experiments still need Rust/Cargo and, for CUDA workloads,
an NVIDIA driver and NVRTC. Thread defaults use at most 16 physical cores;
`SOLVER_THREADS`, `RAYON_NUM_THREADS`, and explicit experiment `--env` options
override them. Compare timings only with controls on the same hardware and
settings. Historical replay scripts contain fixed experiment IDs and are not
general-purpose commands for starting a new research pass.

Follow [program.md](program.md) when proposing, measuring, accepting and tracking
new experiments. GPU work should not compete with an interactive solve/report.
