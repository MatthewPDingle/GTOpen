import sys, json, shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
assert len(sys.argv) == 2
H = ROOT / 'runs/D147-readback-diagnostic'
P = h.read(H / 'protocol.json')
O = H / 'execution'
def verify():
    h.pin(H / 'protocol.json', sys.argv[1])
    h.custody()
    for p, digest in P['input_sha256'].items():
        h.pin(p, digest)
verify()
assert not (H / 'probe.exe').exists()
O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT / 'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status())
    assert shutil.disk_usage(ROOT).free >= P['required_free_bytes']
    gpu = h.ar.read_command(['nvidia-smi', '--query-gpu=name,uuid,driver_version,memory.total', '--format=csv,noheader'])
    assert gpu['returncode'] == 0 and P['GPU_uuid'] in gpu['stdout']
    h.save(O / 'before.json', {'at': h.now(), 'gpu': gpu, 'performance_candidate': False})
    h.child(P['rustc_command'], O, 'rustc', 1200)
    verify()
    binary = H / 'probe.exe'
    h.save(binary.with_suffix('.manifest.json'), {**h.ar.source_identity(), 'source_sha256': P['accepted_source_sha256'] | {'crates/solver/src/gpu/mod.rs': P['instrumented_production_sha256'], 'crates/solver/src/gpu/arena.rs': P['instrumented_arena_sha256']}, 'underlying_accepted_source_sha256': P['accepted_source_sha256'], 'binary_sha256': h.sha(binary), 'control_only': True, 'underlying_accepted_source': 'E080', 'diagnostic_instrumentation': 'D147 retained fourteen host-wall readback spans; private plan visibility and local test-harness adapters reverse exactly', 'instrumentation_sha256': {str(p): h.sha(p) for p in [H / 'probe.rs', H / 'gpu/mod.rs', H / 'gpu/arena.rs', H / 'gpu/kernels.cu', H / 'source-review.json']}, 'build_protocol_sha256': sys.argv[1], 'rustc_command': P['rustc_command'], 'candidate_accepted': False})
with h.ar.exclusive_lock(ROOT / 'epoch-sequence.lock'):
    previous_environment = None
    for record in P['sequence']:
        verify()
        h.ar.refuse_active(h.ar.live_status())
        assert shutil.disk_usage(ROOT).free >= P['required_free_bytes']
        instrumented = record['instrumented']
        binary = H / 'probe.exe' if instrumented else ROOT / 'binaries/E080-postflop_autoresearch.exe'
        manifest = binary.with_suffix('.manifest.json')
        m = h.read(manifest)
        h.pin(binary, m['binary_sha256'])
        expected = P['accepted_source_sha256'] | ({'crates/solver/src/gpu/mod.rs': P['instrumented_production_sha256'], 'crates/solver/src/gpu/arena.rs': P['instrumented_arena_sha256']} if instrumented else {})
        assert m['source_sha256'] == expected
        command = [sys.executable, str(ROOT / 'runs/D147-launch.py')]
        if instrumented:
            command += ['--instrumented']
        command += ['--id', record['id'], '--title', 'D147 readback observer ' + record['id'], '--kind', 'diagnostic', '--binary', str(binary), '--build-manifest', str(manifest), '--test', 'postflop_complete_cycle']
        h.child(command, O, record['id'], 1200)
        verify()
        report = h.read(ROOT / 'runs' / record['id'] / 'report.json')
        assert report['status'] == 'measured' and report['returncode'] == 0 and report['test_pass_count'] == 1
        assert report['binary_build_manifest']['data'] == m and report['binary_sha256'] == m['binary_sha256']
        assert report['provenance']['source_sha256'] == P['accepted_source_sha256']
        assert h.exact(record['id']) == h.read(h.EPOCH / 'exact-anchor.json')
        if previous_environment is None:
            previous_environment = report['environment']
        assert previous_environment == report['environment']
        log = (ROOT / 'runs' / record['id'] / 'stdout.log').read_text(encoding='utf-8')
        traces = [json.loads(line.partition('LIFECYCLE_PROFILE ')[2]) for line in log.splitlines() if 'LIFECYCLE_PROFILE ' in line]
        assert len(traces) == (3 if instrumented else 0)
        print('Completed', record['id'], 'exact; traces', len(traces), flush=True)
    h.save(O / 'native-complete.json', {'at': h.now(), 'protocol_sha256': sys.argv[1], 'all_native_children_terminal': True, 'sequence': P['sequence'], 'scientific_records_exact': 18, 'convergence_checkpoints_exact': 138, 'readback_traces': 9, 'spans': 126, 'all_samples_retained': True, 'performance_qualification_samples': 0, 'extension_runs': 0})
h.child([sys.executable, str(ROOT / 'runs/D147-assess.py'), sys.argv[1]], O, 'assessment', 600)
h.child([sys.executable, str(ROOT / 'runs/D147-subassess.py'), sys.argv[1]], O, 'subassessment', 600)
verify()
h.save(O / 'complete.json', {'at': h.now(), 'protocol_sha256': sys.argv[1], 'all_owned_children_terminal': True, 'report_sha256': h.sha(ROOT / 'comparisons/D147-readback/report.json'), 'substage_report_sha256': h.sha(ROOT / 'comparisons/D147-arena-substages/report.json'), 'source_main_live_PTX_custody_pass': True, 'candidate_accepted': False})
print('D147 fixed observer cohort and assessment finished.', flush=True)
