"""Generate a diagnostic-only patch without writing to the research checkout."""
from pathlib import Path
import datetime
import difflib
import hashlib
import json
import subprocess

ROOT = Path(r"X:\Dev\GTOpen-gpu-research-20261016")
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "crates/solver/src/gpu/mod.rs"
raw = SOURCE.read_bytes()
base = raw.decode().replace("\r\n", "\n")
candidate = base


def replace(old, new):
    global candidate
    count = candidate.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one source anchor, got {count}: {old[:100]!r}")
    candidate = candidate.replace(old, new, 1)


helper = '''// Diagnostic-only host wall timers. No CUDA events or extra synchronization.
#[derive(serde::Serialize)]
struct LifecycleSpan {
    stage: &'static str,
    wall_ms: f64,
    player: Option<usize>,
    arena: Option<&'static str>,
    bytes: Option<usize>,
}

struct LifecycleTrace {
    phase: &'static str,
    started: Option<std::time::Instant>,
    last: Option<std::time::Instant>,
    spans: Vec<LifecycleSpan>,
}

impl LifecycleTrace {
    fn new(phase: &'static str) -> Self {
        let enabled = std::env::var_os("POSTFLOP_AUTORESEARCH_LIFECYCLE_PROFILE")
            .as_deref() == Some(std::ffi::OsStr::new("1"));
        let started = enabled.then(std::time::Instant::now);
        Self { phase, started, last: started,
            spans: Vec::with_capacity(if enabled { 16 } else { 0 }) }
    }

    fn mark(&mut self, stage: &'static str, player: Option<usize>,
            arena: Option<&'static str>, bytes: Option<usize>) {
        if let Some(last) = self.last {
            let now = std::time::Instant::now();
            self.spans.push(LifecycleSpan {
                stage, wall_ms: now.duration_since(last).as_secs_f64() * 1e3,
                player, arena, bytes,
            });
            self.last = Some(now);
        }
    }

    fn finish(self, completed: bool) {
        if let Some(started) = self.started {
            let wall_ms_before_logging = started.elapsed().as_secs_f64() * 1e3;
            use std::io::Write;
            let mut stderr = std::io::stderr().lock();
            let _ = writeln!(stderr, "LIFECYCLE_PROFILE {}", serde_json::json!({
                "schema_version": 1, "phase": self.phase, "completed": completed,
                "thread": format!("{:?}", std::thread::current().id()),
                "wall_ms_before_logging": wall_ms_before_logging, "spans": self.spans,
                "clock": "host_wall", "diagnostic_only": true,
                "extra_cuda_synchronizations": 0,
                "note": "Host-call spans may submit asynchronous work; only explicitly named wait spans measure existing completion waits. Logging and timers perturb timing; exclude this run from performance qualification."
            }));
        }
    }
}

'''
replace("pub struct GpuSolver {", helper + "pub struct GpuSolver {")
replace('''    pub fn new_with_budget(solver: &Solver, budget_bytes: u64) -> Result<GpuSolver, String> {
''', '''    pub fn new_with_budget(solver: &Solver, budget_bytes: u64) -> Result<GpuSolver, String> {
        let mut lifecycle = LifecycleTrace::new("init");
''')
replace('''        let ctx = CudaContext::new(0).map_err(e)?;
''', '''        lifecycle.mark("plan_and_budget_cpu", None, None, None);
        let ctx = CudaContext::new(0).map_err(e)?;
''')
replace('''        let ptx = PTX
''', '''        lifecycle.mark("context_stream_and_device_info_host_calls", None, None, None);
        let ptx = PTX
''')
replace('''        let module = ctx.load_module(ptx).map_err(e)?;
''', '''        lifecycle.mark("ptx_acquire_or_compile_cpu", None, None, None);
        let module = ctx.load_module(ptx).map_err(e)?;
        lifecycle.mark("module_load_host_call", None, None, None);
''')
replace('''        let mut h_staging = PinnedBuf::new(&ctx, data_len[0].max(data_len[1]))?;
''', '''        let mut h_staging = PinnedBuf::new(&ctx, data_len[0].max(data_len[1]))?;
        lifecycle.mark("pinned_alloc_host_call", None, None,
            Some(data_len[0].max(data_len[1]) * 4));
''')
replace('''        let d_regrets = [
''', '''        lifecycle.mark("arena_layouts_cpu", None, None, None);
        let d_regrets = [
''')
replace('''        let (lock_off, lock_sigma) = build_lock_table(solver);

        let n = plan.num_nodes;
''', '''        lifecycle.mark("arena_upload_calls_with_existing_waits", None, None,
            Some((data_len[0] + data_len[1]) * 8));
        let (lock_off, lock_sigma) = build_lock_table(solver);

        let n = plan.num_nodes;
''')
replace('''        Ok(GpuSolver {
''', '''        lifecycle.mark("locks_and_fold_tables_cpu", None, None, None);
        let gpu = GpuSolver {
''')
replace('''            _module: module,
        })
    }
''', '''            _module: module,
        };
        lifecycle.mark("function_lookup_metadata_upload_and_workbuffer_submit", None, None, None);
        lifecycle.finish(true);
        Ok(gpu)
    }
''')

old_readback = '''    pub fn sync_to_cpu(&mut self, solver: &mut Solver) -> Result<(), String> {
        self.stream.synchronize().map_err(e)?;
        for p in 0..2 {
            let len = self.d_regrets[p].len();
            self.stream
                .memcpy_dtoh(&self.d_regrets[p], &mut self.h_staging.as_mut_slice()[..len])
                .map_err(e)?;
            self.stream.synchronize().map_err(e)?;
            self.arena_layout[p].write(solver, p, 0, &self.h_staging.as_slice()[..len]);
            self.stream
                .memcpy_dtoh(&self.d_strat[p], &mut self.h_staging.as_mut_slice()[..len])
                .map_err(e)?;
            self.stream.synchronize().map_err(e)?;
            self.arena_layout[p].write(solver, p, 1, &self.h_staging.as_slice()[..len]);
        }
        solver.iteration = self.iteration;
        if self.iso_active {
            // only representative branches hold fresh data; queries/saves
            // re-materialize siblings via Solver::ensure_symmetric
            solver.mark_sym_dirty();
        }
        Ok(())
    }
'''
new_readback = old_readback.replace(
    '        self.stream.synchronize().map_err(e)?;\n        for p in 0..2 {',
    '        let mut lifecycle = LifecycleTrace::new("full_readback");\n'
    '        self.stream.synchronize().map_err(e)?;\n'
    '        lifecycle.mark("initial_stream_wait", None, None, None);\n        for p in 0..2 {', 1)
for which in ("regrets", "strat"):
    new_readback = new_readback.replace(
        f'                .memcpy_dtoh(&self.d_{which}[p], &mut self.h_staging.as_mut_slice()[..len])\n'
        '                .map_err(e)?;\n            self.stream.synchronize().map_err(e)?;',
        f'                .memcpy_dtoh(&self.d_{which}[p], &mut self.h_staging.as_mut_slice()[..len])\n'
        '                .map_err(e)?;\n'
        f'            lifecycle.mark("dtoh_host_call", Some(p), Some("{which}"), Some(len * 4));\n'
        '            self.stream.synchronize().map_err(e)?;\n'
        f'            lifecycle.mark("dtoh_stream_wait", Some(p), Some("{which}"), Some(len * 4));', 1)
    which_index = 0 if which == "regrets" else 1
    original = f'            self.arena_layout[p].write(solver, p, {which_index}, &self.h_staging.as_slice()[..len]);'
    new_readback = new_readback.replace(original, original +
        f'\n            lifecycle.mark("encode_scatter_restore_cpu", Some(p), Some("{which}"), Some(len * 4));', 1)
new_readback = new_readback.replace('''        Ok(())
    }
''', '''        lifecycle.mark("publish_iteration_and_symmetry_flag_cpu", None, None, None);
        lifecycle.finish(true);
        Ok(())
    }
''', 1)
replace(old_readback, new_readback)
replace('''    pub fn synchronize(&self) -> Result<(), String> {
        self.stream.synchronize().map_err(e)
    }
''', '''    pub fn synchronize(&self) -> Result<(), String> {
        let mut lifecycle = LifecycleTrace::new("caller_synchronize");
        let result = self.stream.synchronize().map_err(e);
        lifecycle.mark("existing_stream_wait", None, None, None);
        lifecycle.finish(result.is_ok());
        result
    }
''')

assert candidate.count(".synchronize()") == base.count(".synchronize()")
assert candidate.count("memcpy_dtoh(") == base.count("memcpy_dtoh(")
assert candidate.count("alloc_zeros::<") == base.count("alloc_zeros::<")
patch = "".join(difflib.unified_diff(base.splitlines(True), candidate.splitlines(True),
    fromfile="a/crates/solver/src/gpu/mod.rs", tofile="b/crates/solver/src/gpu/mod.rs", n=3))
for name, data in (("base-mod.rs", raw), ("candidate-mod.rs", candidate.encode()),
                   ("lifecycle-diagnostic.patch", patch.encode())):
    with (OUT / name).open("xb") as f:
        f.write(data)
syntax = subprocess.run(["rustfmt", "--edition", "2021", "--emit", "stdout", "--config", "skip_children=true",
                         str(OUT / "candidate-mod.rs")], capture_output=True, text=True)
assert syntax.returncode == 0, syntax.stderr
check = subprocess.run(["git", "apply", "--check", str(OUT / "lifecycle-diagnostic.patch")],
                       cwd=ROOT, capture_output=True, text=True)
assert check.returncode == 0, check.stderr
assert SOURCE.read_bytes() == raw, "Active checkout changed while preparing diagnostic"
manifest = {
    "prepared_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "source": str(SOURCE), "source_sha256": hashlib.sha256(raw).hexdigest(),
    "candidate_sha256": hashlib.sha256(candidate.encode()).hexdigest(),
    "patch_sha256": hashlib.sha256(patch.encode()).hexdigest(),
    "patch_applied": False, "production_files_changed": False,
    "rustfmt_syntax_parse_returncode": syntax.returncode,
    "rustfmt_stderr": syntax.stderr,
    "git_apply_check_returncode": check.returncode, "git_apply_check_stderr": check.stderr,
    "synchronize_calls_before": base.count(".synchronize()"),
    "synchronize_calls_after": candidate.count(".synchronize()"),
    "dtoh_calls_before": base.count("memcpy_dtoh("),
    "dtoh_calls_after": candidate.count("memcpy_dtoh("),
    "init_marks": 9, "full_readback_marks": 14, "caller_synchronize_marks": 1,
    "compile_or_gpu_execution_performed": False,
}
with (OUT / "manifest.json").open("x", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)
    f.write("\n")
print(json.dumps(manifest, indent=2))
