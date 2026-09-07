# Updating GTOpen on Windows

The Start menu shortcut should launch `GTOpen.cmd` in the repository root.
That launcher adds the local CUDA runtime to PATH, builds the current release
with GPU support when an NVIDIA driver is available, and opens the local UI.
Cargo builds incrementally, so unchanged launches do not recompile everything.

## Applying source updates

1. Stop any solve or report and save the sessions you want to keep. A browser
   refresh preserves a running server session; restarting the server does not.
2. Close the GTOpen server window before rebuilding. Windows locks a running
   executable, and it continues to use the old code until restarted. If the
   server was started in the background, stop `gto-server.exe` in Task Manager
   after saving instead.
3. Update the repository, then launch the existing Start menu shortcut or
   `GTOpen.cmd`. Wait for the build to finish and the browser to open.
4. Load your saved sessions. Refresh an already-open browser tab to load any
   updated UI text or JavaScript.

The September 2026 performance changes need a rebuild and restart, but no
new shortcut, graphics assets, CUDA runtime, or save-file conversion.
The recorded validation includes resuming both compressed and f32 saves.

## Shortcut settings

For the desktop installation at `T:\Dev\GTOpen`:

- Target: `C:\Windows\System32\cmd.exe`
- Arguments: `/c ""T:\Dev\GTOpen\GTOpen.cmd""`
- Start in: `T:\Dev\GTOpen`

Use your own repository path on another machine. Point at the launcher rather
than directly at `target\release\gto-server.exe`, so source updates are rebuilt
and CUDA runtime discovery runs before the server starts.

## Verify the running engine

The compute indicator identifies GPU or CPU after a solve begins. A built or
loaded session alone does not mean CUDA has run; `gpu: false` before solving
is normal. A fallback reason is displayed if GPU initialization fails.
The speed readout uses live progress timings, not the published benchmark rate.

Memory labels distinguish CPU solver arenas from a conservative GPU estimate.
The GPU budget uses available device memory minus safety headroom unless
`SOLVER_GPU_MEM_MB` is set. Packing and scratch reuse can make the final GPU
plan smaller than the full-tree estimate; actual fit is checked at solve time.

For current measured results and validation, see the
[GPU performance report](../research/autoresearch/gpu-pass.md).
