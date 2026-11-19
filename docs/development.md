# Notes for developers

For installing and using the app, start with the [README](../README.md). For working in this repository as a coding agent, read [AGENTS.md](../AGENTS.md).

## Layout

| Path | Contents |
| --- | --- |
| `crates/solver` | The Rust engine: the postflop solver, the Preflop Lab and the CUDA kernels |
| `crates/server` | The local HTTP server and API; it also serves `web/` |
| `web` | The browser page: plain HTML, CSS and JavaScript modules, no build step |
| `tools` | Launchers, page tests (`test_*.mjs`), the data generator and the leaf-net training harness |
| `research` | Records and tools from performance and modeling studies |
| `docs` | Guides and reference |

[Engine, runtime settings, CLI and API](technical_reference.md) is the main reference.

## Tests

```sh
# CPU tests
cargo test --release -p solver

# GPU integration tests (requires CUDA)
cargo test --release --features gpu --test gpu --test preflop_gpu -- --test-threads=1

# Page tests, one file each
node tools/test_version.mjs
```

## Versions

The newest entry of [CHANGELOG.md](../CHANGELOG.md) is the app's version. Every change a user of the app can see adds an entry on top. The rules are in [AGENTS.md](../AGENTS.md#versions-and-the-change-log).

## Research records

| Topic | Where |
| --- | --- |
| Performance | [GPU benchmarks](../research/autoresearch/gpu-pass.md) · [Preflop performance results](../research/autoresearch/passes/03-preflop-20260910/README.md) · [Research setup](../research/autoresearch/setup.md) |
| Preflop modeling | [Preflop research](../research/preflop-evolution/README.md) · [Contextual preflop](contextual_preflop.md) · [Contextual postflop](postflop_contextual_model.md) |
| Leaf net | [Contribute compute](contribute-compute.md) · `tools/leafnet/README.md` |

### Local workspace and GPU research

The maintainer's desktop uses two folders:

| Folder | Contents |
| --- | --- |
| `X:\Dev\GTOpen` | The application, source, research tools, dashboard and published reports. This is the only working Git checkout. |
| `X:\Dev\GTOpen-research` | Raw dumps, saved research fixtures, build outputs and checksum-verified backups. These stay local. |

The current application and consolidated reports are on
[`master`](https://github.com/MatthewPDingle/GTOpen/tree/master).
The [postflop GPU dashboard](../web/research/postflop-gpu-20261016/index.html),
[experiment ledger](../research/postflop-gpu-20261016/experiments.md) and
[workspace record](../research/postflop-gpu-20261016/workspace-layout.json) explain the results and retained local evidence.
Open the dashboard through the local server at `/research/postflop-gpu-20261016/`.
Links marked **local dump** require that desktop's research data; the raw dumps are not distributed through GitHub.

The former `GTOpen-fix` and `GTOpen-gpu-research-20261016` checkouts are preserved as archive tags:
[`archive/unfinished-hero-fix-20261030`](https://github.com/MatthewPDingle/GTOpen/tree/archive/unfinished-hero-fix-20261030)
and [`archive/research-through-E127-20261030`](https://github.com/MatthewPDingle/GTOpen/tree/archive/research-through-E127-20261030).
The adaptive-HERO fix is unfinished and is not applied to the running app.
Historical research records retain their original paths and hashes; consult the workspace record before attempting to replay them.

The active research tools default to the local `GTOpen-research/postflop-gpu-20261028` data folder.
Set `GTOPEN_RESEARCH_DIR` to choose a different data directory for a new, explicitly started research pass.
The older archive on `S:` is read-only; the retired `T:` paths are historical references.
