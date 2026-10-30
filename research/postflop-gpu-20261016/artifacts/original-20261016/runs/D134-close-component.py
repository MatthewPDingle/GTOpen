"""Close the fixed E083 initialization experiment without integrated trials."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request

ROOT = Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0, str(ROOT / 'runs/accepted-E080-live-20261018'))
import common_e080_live as old

old.custody()
assert not (ROOT / 'gpu-run.lock').exists()
H = ROOT / 'runs/D134-zero-init-fences-r2'
q = old.read(H / 'report.json')
assert q['protocol_sha256'] == old.sha(H / 'protocol.json')
assert q['all_complete_frames_exact'] and q['ability_fresh_warm_compressed_F32_pass']
assert not q['admit_one_integrated_trial'] and not q['source_activated']
assert q['application_kernel_launches'] == q['full_solver_executions'] == 0
assert q['all_owned_children_terminal'] and q['source_main_live_PTX_custody_pass']
for name in ['component', 'assessment']:
    receipt = old.read(ROOT / f'runs/D134-manager-r2/{name}.exit.json')
    assert receipt['returncode'] == 0 and receipt['error'] is receipt['cleanup'] is None
failed = old.read(ROOT / 'runs/D134-zero-init-fences/execution/rustc.exit.json')
assert failed['returncode'] != 0

out = ROOT / 'comparisons/D134-component-closure'
out.mkdir(exist_ok=False)
reason = (
    'Rejected at the frozen initialization-component admission gate: summed fixture-median '
    'saving 40.0397 ms is below 94.215979 ms; rainbow median is 2.8987 ms slower; '
    'river all-thread CPU median 93.75 ms exceeds its 79.375 ms limit. Complete device '
    'images and fresh/warm compressed/F32 controls passed. This is component evidence, '
    'not an observed complete-solve gain. Close the zero-arena wait batching/final-fence '
    'form; no additional samples, threshold, caller, source-scope or placement variants.'
)
frames = {p: {k: v[k] for k in ['sha256', 'bytes', 'explicit_words', 'verified_positive_zero_words']}
          for p, v in q['timed_frames'].items()} if 'timed_frames' in q else {}
# The original full reader report remains authoritative for every field and frame.
decision = {
    'id': 'D134/E083', 'at': old.now(), 'decision': 'rejected_component_admission',
    'reason': reason, 'component_report_sha256': old.sha(H / 'report.json'),
    'protocol_sha256': q['protocol_sha256'], 'checks': q['checks'],
    'fixtures': q['fixtures'],
    'summed_fixture_median_component_saving_ms': q['sum_fixture_median_component_saving_ms'],
    'minimum_component_saving_ms': q['minimum_saving_ms'],
    'full_device_frames_exact': True, 'ability_fresh_warm_compressed_F32_pass': True,
    'compiler_attempts': 2, 'successful_compilers': 1,
    'original_pre_native_visibility_failure_preserved': True,
    'observer_adapter_repair_sha256': old.sha(H / 'visibility-adapter-repair.json'),
    'ability_processes': 1, 'timing_processes': 6, 'initialization_windows': 18,
    'application_kernel_launches': 0, 'full_solver_executions': 0,
    'source_activated': False, 'source_adopted': False, 'accepted_live_source': 'E080',
    'all_owned_children_terminal': True, 'source_main_live_PTX_custody_pass': True,
    'raw_frame_storage': 'S only; per-field full-word comparisons and SHA/bytes in component report',
    'limits': q['limits'],
}
old.save(out / 'report.json', decision)

published = []
folders = [ROOT / 'runs/E083-source', ROOT / 'runs/D134-zero-init-fences', H,
           ROOT / 'runs/D134-manager', ROOT / 'runs/D134-manager-r2', out]
for folder in folders:
    for p in sorted(folder.rglob('*')):
        if not p.is_file() or p.suffix not in ['.json', '.py', '.rs', '.cu', '.log', '.patch']:
            continue
        key = folder.name + '/' + p.relative_to(folder).as_posix()
        dst = old.ar.DASHBOARD / 'evidence' / key
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            assert dst.read_bytes() == p.read_bytes(), str(dst)
        else:
            shutil.copyfile(p, dst)
        with urllib.request.urlopen(old.ar.LIVE + '/research/postflop-gpu-20261016/evidence/' + key, timeout=20) as response:
            assert response.read() == p.read_bytes(), key
        published.append(key)

with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'), timeout=3):
    s = old.read(old.ar.STATUS)
    for ident in ['D134', 'E083']:
        e = next(x for x in s['experiments'] if x['id'] == ident)
        e.update(status='rejected', correctness='pass', accepted=False,
                 stage='Closed: initialization component failed admission',
                 reason=reason, updated_at=old.now())
        e['evidence'].extend([
            {'label': 'Full device-image reader and fixed component timings',
             'url': 'evidence/D134-zero-init-fences-r2/report.json'},
            {'label': 'Rejection and compiler-failure attribution',
             'url': 'evidence/D134-component-closure/report.json'},
        ])
    s.update(updated_at=old.now(), state='running', goal_status='active',
             active_experiment=None, stage='Investigating a distinct performance mechanism',
             activity=reason + ' Accepted and live E080 remain at 14.74% cumulative benchmark improvement.')
    old.ar.atomic_json(old.ar.STATUS, s)
old.save(out / 'publication.json', {'at': old.now(), 'HTTP_verified_artifacts': published,
    'all_owned_children_terminal': True, 'source_main_live_PTX_custody_pass': True})

ledger = old.REPO / 'research/postflop-gpu-20261016/experiments.md'
raw = ledger.read_bytes()
assert b'### D134 and E083 initialization fences' not in raw
entry = '''

### D134 and E083 initialization fences

One separate two-file hypothesis batches the four proven-positive-zero arena waits into one final stream readiness fence. Every allocation and zero fill stays; nonzero/F32/staging waits and the accepted E080 predicates/tokens remain. Candidate source was never activated. No kernels, graph schedule, solver math, precision, quality or save format change.

The first standalone compiler failed with Rust E0624 before producing a binary or running native observations: copied modules could not call the accepted plan's private full-arena helper. Original protocol, stderr and exit retained. A pre-native observer-only adapter copied that exact helper body and updated both copied constructors and reference validators; source, corpus, order and gates stayed fixed. Two compiler attempts total, one successful. Repaired protocol 9c3528ab494d2ad703d8c7e3d8d6b13c84528bd1b1a3460deff305881c7c66ad.

One ability process checked four baseline/candidate fresh/warm compressed/F32 constructors, four paired tiny-budget rejections and three wrong-zero injections. Six fixed fresh timing processes, B1/C1,C2/B2,B3/C3, each initialized all three canonical fixtures. The actual copied constructor plus readiness was timed; full post-timer validation covered all 66 exposed buffers against CPU references and paired frames. Every float word in all nine fresh-zero buffers was read and OR-checked, stored losslessly as positive-zero runs. Metadata and warm-state values retain full expected/actual images. 2.578 GiB timed frames stay physically on S. All 6,821 reader checks passed. No application kernels or complete solves ran; no forced hardware allocator-failure claim.

''' + reason + '\n\nRainbows 497.1966 -> 500.0953 ms; two-tone 365.1135 -> 325.8173 ms; river 88.6551 -> 85.0129 ms. River CPU 62.5 -> 93.75 ms. No pooling, extensions, resampling or variants. Original failed compiler and exact adapter repair are published alongside successful observations. Closure report SHA ' + old.sha(out / 'report.json') + '. ' + str(len(published)) + ' small artifacts HTTP byte-verified; bulk frames remain on S. All owned children terminal, GPU lock absent, accepted/main/live/protected PTX custody passed. E080 remains deployed with 14.7414188354% measured cumulative complete-cycle improvement. Goal active.\n'
newline = b'\r\n' if b'\r\n' in raw else b'\n'
ledger.write_bytes(raw + entry.encode().replace(b'\n', newline))
subprocess.run(['git', 'commit', '--only', '-m', 'research: reject zero initialization fence batching',
                '--', 'research/postflop-gpu-20261016/experiments.md'], cwd=old.REPO, check=True)
old.custody()
print(json.dumps({'decision': decision['decision'], 'HTTP_files': len(published),
                  'accepted_live_source': 'E080', 'full_solver_samples': 0}), flush=True)
