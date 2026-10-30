import json, shutil, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
assert len(sys.argv) == 2
H = ROOT / 'runs/D269-host-layout'
P = h.read(H / 'protocol.json')
def verify():
    h.pin(H / 'protocol.json', sys.argv[1])
    for path, digest in P['input_sha256'].items(): h.pin(path, digest)
    for v in P['owned'].values():
        for arm in ['baseline', 'candidate']:
            if arm in v: h.pin(v[arm]['path'], v[arm]['sha256'])
def guard(arm):
    hashes = P['accepted_source_sha256'] | {n: v[arm]['sha256'] for n, v in P['owned'].items() if arm in v}
    assert h.ar.source_identity()['source_sha256'] == hashes
    targets = h.read(ROOT / 'epoch/preexisting-target-artifacts.json')
    for n, v in targets.items(): h.pin(h.REPO / n, v['sha256'])
    changed = {n for n, v in P['owned'].items() if v['original'] and v[arm]['sha256'] != v['original_sha256']}
    assert set(subprocess.check_output(['git', 'diff', '--name-only', 'HEAD', '--', 'crates/solver', 'Cargo.lock'], cwd=h.REPO, text=True).splitlines()) == changed
    new = {n for n, v in P['owned'].items() if not v['original'] and arm in v}
    assert set(subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '--', 'crates/solver'], cwd=h.REPO, text=True).splitlines()) == set(targets) | new
    main = h.read(ROOT / 'epoch/protected-main.json')
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=main['root'], text=True).strip() == main['git_head']
    for n, digest in main['source_sha256'].items(): h.pin(Path(main['root']) / n, digest)
    h.pin(main['live_path'], main['live_sha256'])
verify()
h.custody()
O = H / 'execution'
O.mkdir(exist_ok=False)
rows = {}
with h.ar.exclusive_lock(ROOT / 'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status())
    for phase in P['phases']:
        assert not Path(phase['target']).exists()
    for phase in P['phases']:
        arm = phase['arm']
        out = O / arm
        out.mkdir()
        verify(); h.custody(); h.ar.refuse_active(h.ar.live_status())
        assert shutil.disk_usage(ROOT).free >= P['required_free_bytes']
        assert not {k: v for k, v in h.env().items() if k in ['RUSTFLAGS', 'CARGO_ENCODED_RUSTFLAGS', 'RUSTC', 'RUSTC_WRAPPER', 'RUSTC_WORKSPACE_WRAPPER', 'CARGO_TARGET_DIR'] or k.startswith('CARGO_PROFILE_RELEASE_') or (k.startswith('CARGO_TARGET_') and k.endswith('_RUSTFLAGS'))}
        command = ['cargo', 'test', '--release', '--locked', '--offline', '--target-dir', phase['target'], '-p', 'solver', '--features', 'continuation-transfer-research', '--lib', '--no-run', '--message-format=json']
        fault = None
        try:
            for name, v in P['owned'].items():
                if arm in v: shutil.copyfile(v[arm]['path'], h.REPO / name)
            guard(arm)
            h.child(command, out, 'compile', 1800)
            verify(); guard(arm)
            events = [json.loads(line) for line in (out / 'compile.stdout.log').read_text(encoding='utf-8').splitlines()]
            assert any(e.get('reason') == 'build-finished' and e.get('success') for e in events)
            artifacts = [e for e in events if e.get('reason') == 'compiler-artifact' and e.get('executable') and e.get('profile', {}).get('test') and e['target']['name'] == 'solver']
            assert len(artifacts) == 1 and artifacts[0]['fresh'] is False
            original_exe = Path(artifacts[0]['executable'])
            assert original_exe.resolve().is_relative_to(Path(phase['target']).resolve())
            exe = out / 'host-layout.exe'
            shutil.copyfile(original_exe, exe)
            h.save(out / 'build-manifest.json', {'at': h.now(), 'source_sha256': h.ar.source_identity()['source_sha256'], 'binary_sha256': h.sha(exe), 'cargo_artifact': artifacts[0], 'protocol_sha256': sys.argv[1], 'ordinary_or_GPU_executions': 0})
        except BaseException as error:
            fault = repr(error)
            h.save(out / 'failure.json', {'at': h.now(), 'error': fault, 'ordinary_or_GPU_executions': 0})
            raise
        finally:
            for name, v in P['owned'].items():
                dest = h.REPO / name
                if v['original']:
                    assert h.sha(dest) in [v['original_sha256'], v[arm]['sha256']]
                    shutil.copyfile(v['original'], dest)
                elif arm in v and dest.exists():
                    h.pin(dest, v[arm]['sha256'])
                    assert dest.resolve().is_relative_to(h.REPO.resolve())
                    dest.unlink()
            h.custody()
            h.save(out / 'restoration.json', {'at': h.now(), 'accepted_main_live_protected_PTX_unchanged': True, 'error': fault})
        h.child([str(exe), '--exact', 'gpu::d269_host_types_only', '--nocapture', '--test-threads=1'], out, 'layout', 120)
        lines = (out / 'layout.stdout.log').read_text(encoding='utf-8').splitlines()
        parsed = [json.loads(line.split('D269_LAYOUT ', 1)[1]) for line in lines if line.startswith('D269_LAYOUT ')]
        assert len(parsed) == 1 and len(parsed[0]) == 8 and any('1 passed; 0 failed;' in line for line in lines)
        rows[arm] = parsed[0]
        print(arm, 'actual host sizes', rows[arm], flush=True)
    b, c = rows['baseline'], rows['candidate']
    gates = {'baseline_wrapper': b[0] == 4448, 'candidate_wrapper_bound': c[0] <= b[0] + 8,
             'wrapper_alignment': b[1] == c[1] == 8,
             'records_no_growth': b[2:6] == c[2:6] == [32, 8, 40, 8],
             'arena_layout_no_growth': b[6:] == c[6:]}
    h.custody()
    h.save(H / 'report.json', {'id': 'D269', 'at': h.now(), 'status': 'pass_actual_host_types_only' if all(gates.values()) else 'rejected_exact_layout_form', 'protocol_sha256': sys.argv[1], 'rows': rows, 'gates': gates, 'all_owned_children_terminal': True, 'fresh_compilers': 2, 'filtered_CPU_layout_helpers': 2, 'GpuSolver_constructors_CUDA_APIs_kernels_solves_performance_runs': 0, 'accepted_main_live_protected_PTX_unchanged': True, 'limits': P['scope']})
print(json.dumps({'gates': gates, 'rows': rows, 'no_GPU_or_performance_runs': True}), flush=True)
