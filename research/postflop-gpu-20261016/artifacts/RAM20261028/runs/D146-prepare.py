import sys, json, re, shutil, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
assert not (ROOT / 'gpu-run.lock').exists() and not (ROOT / 'epoch-sequence.lock').exists()
h.ar.refuse_active(h.ar.live_status())
H = ROOT / 'runs/D146-readback-diagnostic'
H.mkdir(exist_ok=False)
gpu = H / 'gpu'
gpu.mkdir()
S = ROOT / 'runs/D146-readback-source'
m = h.read(S / 'manifest.json')
h.pin(S / 'baseline.rs', h.custody()['crates/solver/src/gpu/mod.rs'])
h.pin(S / 'diagnostic.rs', m['diagnostic_sha256'])
reference = ROOT / 'runs/E090-engine-control/reference/D134-observer-parent.rs'
text = reference.read_text(encoding='utf-8')
shim = text[text.index('pub mod plan {'):text.index('\nmod arena;')]
instrumented = (S / 'diagnostic.rs').read_text(encoding='utf-8')
adapted = instrumented.replace('pub mod plan;', shim, 1).replace('plan.use_full_action_arenas(&solver.spot);', 'plan::full_arena_adapter(&mut plan, &solver.spot);', 1)
assert adapted.replace(shim, 'pub mod plan;', 1).replace('plan::full_arena_adapter(&mut plan, &solver.spot);', 'plan.use_full_action_arenas(&solver.spot);', 1) == instrumented
(gpu / 'mod.rs').write_text(adapted, encoding='utf-8', newline='\n')
for name in ['arena.rs', 'kernels.cu']:
    shutil.copyfile(h.REPO / 'crates/solver/src/gpu' / name, gpu / name)
original = (h.REPO / 'crates/solver/tests/postflop_autoresearch.rs').read_text(encoding='utf-8')
bench, doc_count = re.subn(r'^//!', '//', original, flags=re.MULTILINE)
assert doc_count == 7
bench = bench.replace('#![cfg(feature = "gpu")]\n', '', 1).replace('use solver::gpu::{GpuSolver, KERNEL_NAMES};', 'use observed::{GpuSolver, KERNEL_NAMES};', 1).replace('include_str!("../../../bench_spot.json")', 'include_str!("bench_spot.json")', 1)
assert bench.replace('use observed::{GpuSolver, KERNEL_NAMES};', 'use solver::gpu::{GpuSolver, KERNEL_NAMES};', 1).replace('include_str!("bench_spot.json")', 'include_str!("../../../bench_spot.json")', 1) == re.sub(r'^//!', '//', original, flags=re.MULTILINE).replace('#![cfg(feature = "gpu")]\n', '', 1)
prefix = '#![allow(dead_code,unused_imports,unused_mut,hidden_glob_reexports)]\npub use solver::*;\n#[path="gpu/mod.rs"]mod observed;\n'
(H / 'probe.rs').write_text(prefix + bench, encoding='utf-8', newline='\n')
shutil.copyfile(h.REPO / 'bench_spot.json', H / 'bench_spot.json')
h.save(H / 'source-review.json', {'at': h.now(), 'instrumented_production_sha256': m['diagnostic_sha256'], 'private_plan_adapter_reversal_exact': True, 'benchmark_adapter_reversal_exact_after_doc_and_cfg_normalization': True, 'kernels_arena_and_all_numerical_work_unchanged': True, 'scope': 'The same staged fourteen-span D065 host-wall helper on accepted E080 sync_to_cpu. No added GPU work/events/waits or omitted operations. Standalone private-plan visibility shim and benchmark imports/include/docs/cfg adapted, with exact reversal. All timing is diagnostic; ordinary and instrumented native processes are compared only for observer usefulness.'})
deps = ROOT / 'reference/accepted-e080-deps'
cmd = ['rustc', str(H / 'probe.rs'), '--edition=2021', '--test', '--cfg', 'feature="gpu"', '-C', 'opt-level=3', '-C', 'codegen-units=1', '-C', 'lto=thin', '-L', 'dependency=' + str(deps)]
for crate, name in [('solver', 'libsolver-e2d3113d740308c1.rlib'), ('cudarc', 'libcudarc-ba3140064b5903a3.rlib'), ('serde_json', 'libserde_json-83a0670a02a34a4d.rlib'), ('serde', 'libserde-47b4d5f55b04d3b5.rlib'), ('rayon', 'librayon-8ab48cfec9cf00f9.rlib')]:
    cmd += ['--extern', crate + '=' + str(deps / name)]
cmd += ['-o', str(H / 'probe.exe')]
sequence = [{'id': name, 'instrumented': 'P' in name} for name in ['D146B1', 'D146P1', 'D146P2', 'D146B2', 'D146B3', 'D146P3']]
s = h.read(h.ar.STATUS)
for record in sequence:
    assert not (ROOT / 'runs' / record['id']).exists() and not any(x['id'] == record['id'] for x in s['experiments'])
files = [Path(__file__), ROOT / 'runs/D146-launch.py', ROOT / 'runs/D146-execute.py', ROOT / 'runs/D146-assess.py', reference, S / 'baseline.rs', S / 'diagnostic.rs', S / 'manifest.json', S / 'source-review.json', ROOT / 'epoch/common.py', ROOT / 'epoch/accepted-source.json', ROOT / 'epoch/protected-main.json', ROOT / 'epoch/preexisting-target-artifacts.json', ROOT / 'epoch/exact-anchor.json', ROOT / 'binaries/E080-postflop_autoresearch.exe', ROOT / 'binaries/E080-postflop_autoresearch.manifest.json', ROOT / 'comparisons/RAM20261028-baseline/report.json']
files += [p for p in H.rglob('*') if p.is_file()] + [p for p in deps.iterdir() if p.is_file()]
for p in [Path(__file__), ROOT / 'runs/D146-launch.py', ROOT / 'runs/D146-execute.py', ROOT / 'runs/D146-assess.py']:
    compile(p.read_text(encoding='utf-8'), str(p), 'exec')
P = {'id': 'D146', 'at': h.now(), 'status': 'FROZEN_PRE_COMPILER_AND_SOLVES', 'measurement_epoch': 'RAM20261028', 'rustc_command': cmd, 'accepted_source_sha256': h.custody(), 'instrumented_production_sha256': m['diagnostic_sha256'], 'GPU_uuid': 'GPU-a5459b5a-632b-3e73-d7f1-a06e167102ee', 'required_free_bytes': 74 * 1024**3, 'sequence': sequence, 'pairs': [{'baseline': f'D146B{i}', 'instrumented': f'D146P{i}'} for i in [1, 2, 3]], 'usefulness_max_absolute_aggregate_perturbation_pct': 10.0, 'expected_full_records_exact': 18, 'expected_checkpoints_exact': 138, 'expected_traces': 9, 'expected_spans': 126, 'input_sha256': {str(p): h.sha(p) for p in files}, 'scope': 'One compiler and six fresh fixed-order native solves, exact full results/checkpoints, three matched observer pairs. Analyze fourteen ordered host-wall spans per readback, with no GPU events, extra waits, source/evaluator/quality variants or extension samples. Absolute unrounded aggregate observer difference <=10% is a coarse usefulness gate, not significance/no-bias proof or per-component error bound. Failed instrumentation/usefulness stops this form; reader-only bookkeeping may replay retained observations. No performance acceptance or baseline update; all artifacts on X.'}
h.save(H / 'protocol.json', P)
for p in [H / 'protocol.json', H / 'source-review.json']:
    key = H.name + '/' + p.name
    dst = h.ar.DASHBOARD / 'evidence' / key
    dst.parent.mkdir(parents=True, exist_ok=True)
    assert not dst.exists()
    shutil.copyfile(p, dst)
    with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/evidence/' + key, timeout=20) as response:
        assert response.read() == p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'), timeout=3):
    s = h.read(h.ar.STATUS)
    x = next(x for x in s['experiments'] if x['id'] == 'D146')
    x.update(status='running', stage='Compiler and matched readback observer cohort', reason='Freeze three matched pairs before native work. The retained fourteen-span helper measures copy host calls, existing waits and CPU encoding/restoration; exact results and a10% aggregate usefulness bound are required. No optimization or gain claim.')
    x.setdefault('evidence', []).append({'label': 'Frozen observer cohort', 'url': 'evidence/D146-readback-diagnostic/protocol.json'})
    s.update(updated_at=h.now(), active_experiment='D146', stage='Fresh E080 readback observation', activity='Measure current-RAM copy, wait and CPU encoding/restoration spans using three matched diagnostic pairs. E080 remains live.')
    h.ar.atomic_json(h.ar.STATUS, s)
print(h.sha(H / 'protocol.json'), flush=True)
