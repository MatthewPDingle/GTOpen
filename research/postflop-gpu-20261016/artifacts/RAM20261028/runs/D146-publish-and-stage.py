import sys, json, re, shutil, subprocess, difflib, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
assert not (ROOT / 'gpu-run.lock').exists() and not (ROOT / 'epoch-sequence.lock').exists()
h.ar.refuse_active(h.ar.live_status())
H = ROOT / 'runs/D146-readback-diagnostic'
P = h.read(H / 'protocol.json')
for p, digest in P['input_sha256'].items():
    h.pin(p, digest)
assert h.read(H / 'execution/complete.json')['all_owned_children_terminal']
Q = ROOT / 'comparisons/D146-readback/report.json'
q = h.read(Q)
assert q['observer_usefulness_pass'] and q['full_scientific_records_exact'] == 18 and q['convergence_checkpoints_exact'] == 138
S = ROOT / 'runs/D147-arena-observer-source'
S.mkdir(exist_ok=False)
base_path = h.REPO / 'crates/solver/src/gpu/arena.rs'
raw = base_path.read_bytes()
base = base_path.read_text(encoding='utf-8')
def method(text, marker):
    start = text.index(marker)
    at = text.index('{', start)
    depth = 0
    for i in range(at, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    raise AssertionError('unterminated method')
original = method(base, '    pub(super) fn write(')
entry = original.index('{') + 1
modified = original[:entry] + '''
        let d147_started = (std::env::var_os("POSTFLOP_AUTORESEARCH_LIFECYCLE_PROFILE")
            .as_deref() == Some(std::ffi::OsStr::new("1")))
            .then(std::time::Instant::now);
''' + original[entry:]
needle = '            write_arena(solver, which != 0, p, data);\n            return;'
assert modified.count(needle) == 1
modified = modified.replace(needle, '            write_arena(solver, which != 0, p, data);\n            self.d147_emit_profile(d147_started, None, p, which, "full");\n            return;', 1)
modified, splits = re.subn(r'^( +)self\.inactive\.par_iter\(\)', lambda m: m[1] + 'let d147_split = d147_started.map(|_| std::time::Instant::now());\n' + m[0], modified, flags=re.MULTILINE)
assert splits == 2
needle = '            });\n            return;'
assert modified.count(needle) == 1
modified = modified.replace(needle, '            });\n            self.d147_emit_profile(d147_started, d147_split, p, which, "compact_f32");\n            return;', 1)
last = modified.rfind('    }')
modified = modified[:last] + '        self.d147_emit_profile(d147_started, d147_split, p, which, "compact_compressed");\n' + modified[last:]
helper = '''    // Diagnostic host wall clocks only; all original writes and joins remain.
    fn d147_emit_profile(&self, started: Option<std::time::Instant>,
        split: Option<std::time::Instant>, player: usize, which: usize, mode: &str) {
        if let Some(started) = started {
            let ended = std::time::Instant::now();
            let full_ms = ended.duration_since(started).as_secs_f64() * 1e3;
            let active_ms = split.map(|s| s.duration_since(started).as_secs_f64() * 1e3);
            let inactive_ms = split.map(|s| ended.duration_since(s).as_secs_f64() * 1e3);
            use std::io::Write;
            let mut stderr = std::io::stderr().lock();
            let _ = writeln!(stderr, "CPU_ARENA_PROFILE {}", serde_json::json!({
                "schema_version": 1, "player": player, "which": which,
                "mode": mode, "full_wall_ms_before_logging": full_ms,
                "active_wall_ms": active_ms, "inactive_wall_ms": inactive_ms,
                "active_blocks": self.active.len(), "inactive_blocks": self.inactive.len(),
                "copy_spans": self.copies.len(), "device_f32_elements": self.len,
                "diagnostic_only": true, "extra_gpu_operations": 0,
                "scope": "Host wall around unchanged CPU write stages; includes Rayon scheduling. Logging perturbs enclosing readback. No isolated encoder, removed-work or speed claim."
            }));
        }
    }

'''
assert 'd147_' not in base
instrumented = base.replace(original, helper + modified, 1)
assert instrumented.replace(helper + modified, original, 1) == base
newline = '\r\n' if b'\r\n' in raw else '\n'
(S / 'baseline.rs').write_bytes(raw)
(S / 'diagnostic.rs').write_bytes(instrumented.replace('\n', newline).encode())
(S / 'arena.rs.patch').write_text(''.join(difflib.unified_diff(base.splitlines(True), instrumented.splitlines(True), fromfile='accepted-E080/arena.rs', tofile='D147-diagnostic/arena.rs')), encoding='utf-8', newline='\n')
review = {'id': 'D147', 'at': h.now(), 'kind': 'diagnostic_only_not_optimization', 'status': 'staged_not_compiled', 'source_reversal_exact': True, 'underlying_source': 'accepted E080', 'scope': 'Retain every original write, iteration order, join, branch, quantizer and address. Add optional host timestamps around complete write calls and compact active/inactive subregions; publish O(1) layout lengths after timing. No metadata scan, GPU call, synchronization, numerical/quality/layout/store or persistence change. Full/noncompact and compact F32 writes remain fully measured. Counter/logger work is observer overhead; matched usefulness controls and full exact records/checkpoints are required before interpreting the clocks.', 'clock_meaning': 'CPU wall including Rayon scheduling, source scans and destination writes. Active and inactive timings are descriptive, not isolated quantizer or achievable saving. Broad source layout cases are not universally proved by this stage.', 'motivation': 'Fresh D146 reports415.0981ms in independent CPU-stage medians versus195.7499ms in wait medians. Inspect whether inactive restoration has enough observed work to motivate the unimplemented E011 design; no optimization is selected or admitted from these timings.', 'must_remain_closed': ['E091 zero-reach normalization shortcut', 'E003 alias hints', 'E012/E013 codec wrappers', 'E087 bounded pinned-window transfer', 'other numerical or complete-cycle failures'], 'next': 'Review/parse standalone adapter, then freeze a fresh matched diagnostic cohort before any compile or native work.'}
h.save(S / 'source-review.json', review)
h.save(S / 'manifest.json', {'id': 'D147', 'at': h.now(), 'accepted_source_sha256': h.custody(), 'baseline_arena_sha256': h.sha(S / 'baseline.rs'), 'diagnostic_arena_sha256': h.sha(S / 'diagnostic.rs'), 'parent_D146_instrumented_mod_sha256': h.sha(ROOT / 'runs/D146-readback-source/diagnostic.rs'), 'parent_observation_sha256': h.sha(Q), 'patch_sha256': h.sha(S / 'arena.rs.patch'), 'source_review_sha256': h.sha(S / 'source-review.json'), 'script_sha256': h.sha(__file__), 'production_source_activated': False, 'compiler_or_native_children_started': 0, 'performance_candidate': False})
pub = []
for folder in [H, Q.parent, S]:
    for p in folder.rglob('*'):
        if not p.is_file() or p.suffix not in ['.json', '.rs', '.cu', '.py', '.patch', '.log']:
            continue
        key = folder.name + '/' + p.relative_to(folder).as_posix()
        dst = h.ar.DASHBOARD / 'evidence' / key
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            assert dst.read_bytes() == p.read_bytes(), key
        else:
            shutil.copyfile(p, dst)
        with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/evidence/' + key, timeout=20) as response:
            assert response.read() == p.read_bytes()
        pub.append(key)
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'), timeout=3):
    s = h.read(h.ar.STATUS)
    x = next(x for x in s['experiments'] if x['id'] == 'D146')
    x.update(status='measured', correctness='pass', stage='Fresh readback observation complete', reason='All18 result records and138 checkpoints match exactly. Three matched observer pairs show0.439% aggregate perturbation within the coarse10% usefulness guard. CPU encoding/scatter/restoration medians total415.098ms; copy calls0.988ms and existing waits195.750ms. Host spans are diagnostic only; no optimization or gain adopted.')
    x.setdefault('evidence', []).append({'label': 'Fresh current-RAM readback breakdown', 'url': 'evidence/D146-readback/report.json'})
    assert not any(x['id'] == 'D147' for x in s['experiments'])
    s['experiments'].append({'id': 'D147', 'title': 'Separate active encoding and inactive restoration costs', 'kind': 'diagnostic', 'status': 'staged', 'accepted': False, 'correctness': 'not_run', 'stage': 'Diagnostic source review before cohort', 'measurement_epoch': 'RAM20261028', 'reason': 'Staged optional host-only timers around unchanged CPU write stages. No source activation, compiler or native execution. Fresh exactness and observer controls are needed before interpreting clocks.', 'evidence': [{'label': 'Exact observation scope', 'url': 'evidence/D147-arena-observer-source/source-review.json'}, {'label': 'Staged source identity', 'url': 'evidence/D147-arena-observer-source/manifest.json'}]})
    s.update(updated_at=h.now(), active_experiment='D147', stage='Prepare CPU readback substage observation', activity='Fresh profiling isolates about415ms in CPU encoding/scatter/restoration and196ms in existing waits. Next separate active work from inactive restoration before choosing an optimization. E080 remains live; no new gain claimed.')
    h.ar.atomic_json(h.ar.STATUS, s)
O = ROOT / 'runs/D146-readback-checkpoint'
O.mkdir(exist_ok=False)
h.save(O / 'publication.json', {'at': h.now(), 'HTTP_verified_artifacts': pub, 'source_main_live_PTX_custody_pass': True, 'all_owned_children_terminal': True, 'all_new_artifacts_physical_X': True, 'D147_no_native_or_compiler_execution': True})
ledger = h.REPO / 'research/postflop-gpu-20261016/experiments.md'
old = ledger.read_bytes()
assert b'### D146 fresh readback observations and D147 staging' not in old
entry = f"""

### D146 fresh readback observations and D147 staging

Previous turn rejected E091 and staged the byte-reversible D06514-span readback helper on accepted E080. Fresh protocol {h.sha(H/'protocol.json')} froze one standalone compiler and six native solves: D146B1/P1,P2/B2,B3/P3. Underlying GPU source and every numerical/quality operation remain unchanged; public-plan visibility, local imports/include path and seven documentation comments normalize back exactly. No events, extra waits or omitted work. Compiler/native/assessment children all terminal0, with no adapter repair needed.

All18 full scientific results/full arena fingerprints and138 convergence checkpoints match E020C1. Separate retained-log reader passed{q['reader_checks']} checks on nine traces/126 ordered spans, actual byte geometry and outer containment. Ordinary aggregate{q['baseline_aggregate_ms']}ms versus instrumented{q['instrumented_aggregate_ms']}ms, observer difference {q['observer_aggregate_perturbation_pct']}%, within the prespecified absolute10% usefulness guard. This coarse aggregate bound neither proves unbiased per-component clocks nor bounds small-fixture error; river outer readback grew from roughly0.66-1.05ms to2.09-2.35ms with logging.

Independent per-fixture CPU encoding/scatter/restoration medians total {q['sum_independent_instrumented_cpu_encode_medians_ms']}ms; copy host-call medians {q['sum_independent_instrumented_copy_call_medians_ms']}ms and existing wait medians {q['sum_independent_instrumented_copy_wait_medians_ms']}ms. CPU split rainbow229.4604ms/two-tone185.0307ms/river0.607ms. These are host wall spans including scheduling, not isolated codec or PCIe latency. Component medians need not sum to whole median wall time. No historical/epoch-baseline pooling, exclusions, extensions, significance or performance gain/adoption. Current five-run E080 baseline remains10.4564109s, prior14.7414% gain historical only.

Stage D147 arena observer SHA {h.sha(S/'diagnostic.rs')} to separate full writes and compact active/inactive subregions. Exact original writes/joins/branches/quantizers/addressing remain, with optional host timestamps and O(1) layout counters/logging only. Reversal is exact; no GPU operation, metadata scan, source activation, compile or native sample. Next freeze an exactness/usefulness cohort before interpreting this substage evidence. The old E011 design remains unimplemented and unadmitted; E091/E003/E012/E013/E087 and other closed forms are not reopened.

{len(pub)} small artifacts HTTP byte-verified. All owned children terminal, GPU/sequence locks absent, accepted/main/live/protected PTX custody passed. All new artifacts physically X, archive unchanged. No push or live replacement; goal active.
"""
nl = b'\r\n' if b'\r\n' in old else b'\n'
ledger.write_bytes(old + entry.encode().replace(b'\n', nl))
subprocess.run(['git', '-c', 'gc.auto=0', 'commit', '--only', '-m', 'research: measure current-RAM readback stage costs', '--', 'research/postflop-gpu-20261016/experiments.md'], cwd=h.REPO, check=True)
h.custody()
h.save(O / 'report.json', {'at': h.now(), 'research_git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=h.REPO, text=True).strip(), 'D146_report_sha256': h.sha(Q), 'D146_status': q['status'], 'records_exact': 18, 'checkpoints_exact': 138, 'observer_perturbation_pct': q['observer_aggregate_perturbation_pct'], 'D147_source_only': True, 'D147_manifest_sha256': h.sha(S/'manifest.json'), 'source_main_live_PTX_custody_pass': True, 'all_owned_children_terminal': True, 'locks_absent': True, 'current_baseline_ms': 10456.4109, 'new_speed_gain_claimed': False, 'goal_status': 'active'})
with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/status.json', timeout=20) as response:
    served = json.load(response)
assert served['active_experiment'] == 'D147' and served['current_hardware_baseline']['aggregate_ms'] == 10456.4109
print(json.dumps({'status': q['status'], 'observer_difference_pct': q['observer_aggregate_perturbation_pct'], 'CPU_ms': q['sum_independent_instrumented_cpu_encode_medians_ms'], 'copy_wait_ms': q['sum_independent_instrumented_copy_wait_medians_ms'], 'D147_staged_only': True, 'HTTP_artifacts': len(pub)}), flush=True)
