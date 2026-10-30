"""Freeze actual crate typechecks and filtered CPU-only private-type size probes."""
import ast, sys, urllib.request, shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists()
S = ROOT / 'runs/E115-source-v2'
M = h.read(S / 'manifest.json')
H = ROOT / 'runs/D269-host-layout'
H.mkdir(exist_ok=False)
arena_observer = b'''
#[cfg(test)]
pub(super) fn d269_sizes_only() -> [usize; 6] {
    [std::mem::size_of::<ActiveBlock>(), std::mem::align_of::<ActiveBlock>(),
     std::mem::size_of::<InactiveBlock>(), std::mem::align_of::<InactiveBlock>(),
     std::mem::size_of::<ArenaLayout>(), std::mem::align_of::<ArenaLayout>()]
}
'''
mod_observer = b'''
#[cfg(test)]
#[test]
fn d269_host_types_only() {
    let a = arena::d269_sizes_only();
    println!("D269_LAYOUT {:?}", [std::mem::size_of::<GpuSolver>(),
        std::mem::align_of::<GpuSolver>(), a[0], a[1], a[2], a[3], a[4], a[5]]);
}
'''
owned = {}
for name, v in M['owned'].items():
    if v['base']:
        h.pin(v['base'], v['base_sha256'])
        h.pin(h.REPO / name, v['base_sha256'])
    h.pin(v['candidate'], v['candidate_sha256'])
for arm in ['baseline', 'candidate']:
    folder = H / (arm + '-sources')
    folder.mkdir()
    for name, v in M['owned'].items():
        src = v['base'] if arm == 'baseline' else v['candidate']
        if src is None:
            continue
        data = Path(src).read_bytes()
        extra = arena_observer if name.endswith('/arena.rs') else mod_observer if name.endswith('/mod.rs') else b''
        dest = folder / Path(name).name
        with dest.open('xb') as f:
            f.write(data + extra)
        assert dest.read_bytes().removesuffix(extra) == data if extra else dest.read_bytes() == data
        owned.setdefault(name, {})[arm] = {'path': str(dest), 'sha256': h.sha(dest), 'observer_append_bytes': len(extra)}
for name in M['owned']:
    owned[name]['original'] = M['owned'][name]['base']
    owned[name]['original_sha256'] = M['owned'][name]['base_sha256']
runner = ROOT / 'runs/D269-execute-host-layout.py'
ast.parse(runner.read_text(encoding='utf-8'))
P = {
    'id': 'D269', 'at': h.now(), 'status': 'FROZEN_PRE_FULL_CRATE_HOST_TYPECHECK',
    'source_manifest_sha256': h.sha(S / 'manifest.json'), 'owned': owned,
    'input_sha256': {str(p): h.sha(p) for p in [Path(__file__), runner, S / 'manifest.json',
                                               ROOT / 'epoch/common.py', ROOT / 'runs/D268-record-layout/report.json',
                                               ROOT / 'runs/D267b-node-order-model/root-report.json',
                                               ROOT / 'runs/E115-source/generation-failure.json']},
    'accepted_source_sha256': h.custody(),
    'phases': [{'arm': arm, 'target': str(ROOT / ('build-d269-' + arm))} for arm in ['baseline', 'candidate']],
    'required_free_bytes': 66 * 1024**3,
    'prospective_gates': {'baseline_GpuSolver': 4448, 'max_GpuSolver_growth': 8,
                          'GpuSolver_alignment': 8, 'ActiveBlock': 32, 'InactiveBlock': 40,
                          'block_alignment': 8, 'ArenaLayout_unchanged': True},
    'scope': 'Two fresh offline locked release full library test builds with continuation-transfer-research, then each exact gpu::d269_host_types_only test once. Appended source observers only print actual private type sizes; source prefixes byte-exact and every build restored before filtered helper. No ordinary tests, GpuSolver constructors, CUDA context/API/kernel/solve or performance samples. Resource/layout gate only, not material neutrality or numerical/caller/capability proof.',
    'failure_rule': 'Genuine candidate compilation or prospective layout/resource failure closes exact implementation without helper/field/scope/flags/selection/source rescue. Observer failure preserved separately; no repeat of completed native cases.',
}
h.save(H / 'protocol.json', P)
dst = h.ar.DASHBOARD / 'evidence' / H.name / 'protocol.json'
dst.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(H / 'protocol.json', dst)
with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/evidence/' + H.name + '/protocol.json', timeout=20) as z:
    assert z.read() == (H / 'protocol.json').read_bytes()
print(h.sha(H / 'protocol.json'), flush=True)
