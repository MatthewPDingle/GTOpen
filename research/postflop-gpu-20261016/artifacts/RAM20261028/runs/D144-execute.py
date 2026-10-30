import sys, json, shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
assert len(sys.argv) == 2
H = ROOT / 'runs/D144-incidence'
P = h.read(H / 'protocol-r2.json')
O = H / 'execution-r2'
def verify():
    h.pin(H / 'protocol-r2.json', sys.argv[1])
    h.custody()
    for p, digest in P['input_sha256'].items():
        h.pin(p, digest)
verify()
assert not (ROOT / 'gpu-run.lock').exists() and not (H / 'probe-r2.exe').exists() and not (H / 'output').exists()
O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT / 'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status())
    assert shutil.disk_usage(ROOT).free >= P['required_free_bytes']
    gpu = h.ar.read_command(['nvidia-smi', '--query-gpu=name,uuid,driver_version,memory.total', '--format=csv,noheader'])
    assert gpu['returncode'] == 0 and P['GPU_uuid'] in gpu['stdout']
    h.save(O / 'before.json', {'at': h.now(), 'gpu': gpu, 'performance_measurement': False})
    h.child(P['rustc_command'], O, 'rustc', 1200)
    verify()
    binary = H / 'probe-r2.exe'
    manifest = binary.with_suffix('.manifest.json')
    h.save(manifest, {**h.ar.source_identity(), 'binary_sha256': h.sha(binary), 'control_only': True, 'underlying_accepted_source': 'E080', 'diagnostic_instrumentation': 'D144 local standalone module/evaluator and six read-only snapshots', 'instrumentation_sha256': {str(p): h.sha(p) for p in [H / 'probe-r2.rs', H / 'gpu/mod.rs', H / 'gpu/arena.rs', H / 'gpu/kernels.cu', H / 'source-review.json', H / 'comment-adapter-review.json']}, 'build_protocol_sha256': sys.argv[1], 'rustc_command': P['rustc_command'], 'candidate_accepted': False})
    (H / 'output').mkdir()
with h.ar.exclusive_lock(ROOT / 'epoch-sequence.lock'):
    command = [sys.executable, str(ROOT / 'runs/D144-launch.py'), '--id', 'D144R1', '--title', 'D144 actual reach snapshots; diagnostic timings only', '--kind', 'diagnostic', '--binary', str(binary), '--build-manifest', str(manifest), '--test', 'postflop_complete_cycle']
    h.child(command, O, 'solve', 1200)
    verify()
    r = h.read(ROOT / 'runs/D144R1/report.json')
    assert r['status'] == 'measured' and r['returncode'] == 0
    assert h.exact('D144R1') == h.read(h.EPOCH / 'exact-anchor.json')
    files = {str(p): h.sha(p) for p in (H / 'output').iterdir()}
    assert len(files) == 6 and sum(p.stat().st_size for p in (H / 'output').iterdir()) <= P['raw_reservation_bytes']
    h.save(O / 'native-complete.json', {'at': h.now(), 'all_native_children_terminal': True, 'raw_sha256': files, 'full_results_exact': 3, 'convergence_checkpoints_exact': 23, 'protocol_sha256': sys.argv[1], 'performance_measurement': False})
h.child([sys.executable, str(ROOT / 'runs/D144-audit.py')], O, 'audit', 1200)
verify()
h.save(O / 'complete.json', {'at': h.now(), 'all_owned_children_terminal': True, 'report_sha256': h.sha(ROOT / 'comparisons/D144-incidence/report.json'), 'source_main_live_PTX_custody_pass': True, 'performance_measurement': False})
print('D144 exact solves and retained reach-input incidence reader passed.', flush=True)
