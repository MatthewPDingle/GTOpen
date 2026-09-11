# Private UI smoke helper

`serve_ui_smoke.py` is separate from the frozen API qualification runner. It imports that runner's environment, native/hash inspection, private-listener ownership and read-only live-activity guards. It does not start a solve. Launch requires `--execute` on Windows, an explicitly pinned candidate executable under the lab's `target`, and a SHA-pinned fresh three-seat all-solver native under the same tree.

Known small input: `target/interactive-api/preview-api-a/small-api/saves/preflop/loaded-input.gtop` in the lab (134,428 bytes when inspected). Pin its actual SHA before launch. The original large `input.gtop` in that directory is deliberately rejected. Candidate source ref is a declared build provenance field; current source and copied web hashes are separately recorded and do not prove which source produced a binary.

From this directory, parent may run:

```powershell
python serve_ui_smoke.py --execute --id ui-preview-a --exe <lab-target-gto-server.exe> --sha256 <candidate-sha> --binary-source-ref <build-ref> --input <small-loaded-input.gtop> --input-sha256 <input-sha> --seconds 300
```

Keep that process alive while operating the private URL printed in its ready JSON. The same record appears at `<lab>/target/interactive-ui/ui-preview-a/owner.json`. Inspect the controls, start a tiny preview and export manually. This is UI smoke evidence, not a convergence or quality benchmark. The only automatic API mutation is loading the private input. The live port 56708 receives read-only status requests.

The helper copies `web`, executable, input and both caches into its new private directory. Frozen cache SHA and the 20,000-sample header are mandatory; environment pins that count so load/build cannot silently rebuild an incompatible cache. `protocol.json` records provenance before launch; `result.json` records termination and final cache hashes. It does not overwrite pass-wide `active.json` or any API qualification artifact.

Stop early by creating the exact `stop_file` from the owner record, or:

```powershell
python serve_ui_smoke.py --stop-owner <owner.json> --token <owner-token>
```

Stop CLI only writes the validated sentinel; it never resolves or kills an externally supplied PID. The retained child is killed on timeout (maximum requested lifetime 300 seconds, plus OS scheduling/teardown), owner stop, research deadline, live work or an unreadable live guard. Live polling has the existing HTTP timeout; an independent loop enforces the runtime clock even if live polling blocks. Startup requests have bounded timeouts. Browser automation should still wrap the helper with an external process-tree timeout as a backstop against interpreter termination or OS failure. Never target the user's server.

Pure mocked tests: `python -m unittest test_serve_ui_smoke.py`. They launch no server and use no network or GPU.

## Curated production reference-only qualification

Add `--production-reference-only` to select source/web from the fixed worktree `target/autoresearch/preflop-interactive-production-20260911`. The private output remains under the original lab's `target/interactive-ui`; ownership, timeout and live-work guards are unchanged. The candidate binary must be SHA-pinned under either owned worktree's `target` (a shared lab build directory is permitted). Its declared build ref and actual source/web hashes are recorded separately. Only a fresh `coupled_deck_v1` three-seat native may be loaded; use the production API qualification's `small-api/saves/preflop/loaded-input.gtop`, not the earlier64-particle fixture. Capabilities must offer exactly the reference model. No solve starts automatically.

The same flag on `verify_api.py` defaults to `reference-control reference-preview small-api`; an explicitly requested `fast-preview` is rejected before launch. The small fixture builds the full reference model and additionally checks that64/128/32 preview-model build queries reject without changing the session/native. Reference numerical parity, stopped-snapshot notice/stale-accuracy checks, frozen cache headers and the existing research deadline remain unchanged. Older research protocol/results are retained as written.

Production `small-api` also verifies GET evaluate is rejected while running, then calls it immediately after stopped and before save/reload. It requires three finite gaps/EVs at the paused iteration, with at least one absolute EV above0.000001bb to catch attached-cancellation zero results (not an accuracy tolerance). After preserving the paused native and its exact reload, it resumes exactly50 iterations at target0/check50/early-preview, requires a fresh completed accuracy checkpoint and finite values, then saves/reloads `resumed.gtop` exactly. Resume evidence is stored under `resume`; original paused `native`, `output`, and `final_status` stay intact. All work stays under the unchanged240-second small-case guard. Research mode retains its previous lifecycle.
