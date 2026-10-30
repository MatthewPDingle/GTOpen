import sys, json, shutil, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
assert not (ROOT / 'gpu-run.lock').exists()
h.ar.refuse_active(h.ar.live_status())
assert h.read(ROOT / 'comparisons/E091-raw-control/report.json')['status'] == 'pass_scoped_down_action_raw_equivalence'
H = ROOT / 'runs/D144-incidence'
H.mkdir(exist_ok=False)
gpu = H / 'gpu'
gpu.mkdir()
reference = ROOT / 'runs/E090-engine-control/reference/D134-observer-parent.rs'
text = reference.read_text(encoding='utf-8')
shim = text[text.index('pub mod plan {'):text.index('\nmod arena;')]
production = (h.REPO / 'crates/solver/src/gpu/mod.rs').read_text(encoding='utf-8')
adapted = production.replace('pub mod plan;', shim, 1).replace('plan.use_full_action_arenas(&solver.spot);', 'plan::full_arena_adapter(&mut plan, &solver.spot);', 1)
assert adapted.replace(shim, 'pub mod plan;', 1).replace('plan::full_arena_adapter(&mut plan, &solver.spot);', 'plan.use_full_action_arenas(&solver.spot);', 1) == production
observer = (ROOT / 'runs/D144-observer.rs').read_text(encoding='utf-8')
(gpu / 'mod.rs').write_text(adapted + '\n' + observer, encoding='utf-8', newline='\n')
for name in ['arena.rs', 'kernels.cu']:
    shutil.copyfile(h.REPO / 'crates/solver/src/gpu' / name, gpu / name)
bench = h.REPO / 'crates/solver/tests/postflop_autoresearch.rs'
original = bench.read_text(encoding='utf-8')
copy = original.replace('#![cfg(feature = "gpu")]\n', '', 1).replace('use solver::gpu::{GpuSolver, KERNEL_NAMES};', 'use observed::{GpuSolver, KERNEL_NAMES};', 1).replace('include_str!("../../../bench_spot.json")', 'include_str!("bench_spot.json")', 1)
needle = '            let exploit = gpu.exploitability(&host).unwrap();'
insertion = '''            if gpu.iteration == 20 || gpu.iteration == if name == "river" { 60 } else { 200 } {
                let output = std::path::Path::new(D144_OUTPUT);
                gpu.d144_sample(&output.join(format!("{name}-{}.bin", gpu.iteration)));
            }
'''
assert copy.count(needle) == 1
copy = copy.replace(needle, insertion + needle, 1)
assert copy.replace(insertion, '', 1).replace('use observed::{GpuSolver, KERNEL_NAMES};', 'use solver::gpu::{GpuSolver, KERNEL_NAMES};', 1).replace('include_str!("bench_spot.json")', 'include_str!("../../../bench_spot.json")', 1) == original.replace('#![cfg(feature = "gpu")]\n', '', 1)
old_probe = (ROOT / 'runs/E090-engine-control/probe.rs').read_text(encoding='utf-8')
helpers = old_probe[old_probe.index('pub trait Word'):old_probe.index('pub fn capture')]
host_field = old_probe[old_probe.index('fn host_field'):old_probe.index('fn state_frame')]
prefix = '''#![allow(dead_code,unused_imports,unused_mut)]
pub use solver::*;
use cudarc::driver::DeviceRepr;
use std::{fs::{File,OpenOptions},io::BufWriter};
#[path="gpu/mod.rs"]mod observed;
'''
prefix += 'const D144_OUTPUT: &str = r"' + str(H / 'output') + '";\n'
(H / 'probe.rs').write_text(prefix + helpers + host_field + copy, encoding='utf-8', newline='\n')
shutil.copyfile(h.REPO / 'bench_spot.json', H / 'bench_spot.json')
review = {'at': h.now(), 'underlying_source': 'accepted E080', 'production_and_evaluator_reversal_exact': True, 'observer': 'Append synchronized read-only snapshots after a full training iteration and before evaluation at20/200 for flops and20/60 for river. Kernel and training/evaluation/graph code unchanged. Snapshots contain all actual action/chance/owner/lock metadata and both complete physical reach images.', 'observed_subsets': 'Actor0 own reach consumed during p1 down; actor1 own reach consumed during p0 down and retained because p1 uses down_nh1=0 in root/action/chance. Every input row has a unique physical owner writer; all sources and actual metadata are checked. p0 actor0 is not observed.', 'limitations': 'No pre-normalization regret-sum finiteness measurement, all-iteration frequency, production time share, device-only cost or speed claim. Unchanged benchmark records/checkpoints must match the exact anchor. Diagnostic snapshots include I/O and are never performance qualification.', 'staged_E091_activated': False}
h.save(H / 'source-review.json', review)
deps = ROOT / 'reference/accepted-e080-deps'
cmd = ['rustc', str(H / 'probe.rs'), '--edition=2021', '--test', '--cfg', 'feature="gpu"', '-C', 'opt-level=3', '-C', 'codegen-units=1', '-C', 'lto=thin', '-L', 'dependency=' + str(deps)]
for crate, name in [('solver', 'libsolver-e2d3113d740308c1.rlib'), ('cudarc', 'libcudarc-ba3140064b5903a3.rlib'), ('serde_json', 'libserde_json-83a0670a02a34a4d.rlib'), ('rayon', 'librayon-8ab48cfec9cf00f9.rlib')]:
    cmd += ['--extern', crate + '=' + str(deps / name)]
cmd += ['-o', str(H / 'probe.exe')]
files = [Path(__file__), ROOT / 'runs/D144-observer.rs', ROOT / 'runs/D144-launch.py', ROOT / 'runs/D144-audit.py', ROOT / 'runs/D144-execute.py', reference, ROOT / 'runs/E090-engine-control/probe.rs', bench, ROOT / 'comparisons/E091-raw-control/report.json', ROOT / 'runs/E091-raw-control/execution/complete.json', ROOT / 'runs/E091-resource/report.json', ROOT / 'epoch/common.py', ROOT / 'epoch/accepted-source.json', ROOT / 'epoch/protected-main.json', ROOT / 'epoch/preexisting-target-artifacts.json', ROOT / 'epoch/exact-anchor.json']
files += [p for p in H.rglob('*') if p.is_file()] + [p for p in deps.iterdir() if p.is_file()]
for p in [ROOT / 'runs/D144-audit.py', ROOT / 'runs/D144-launch.py', ROOT / 'runs/D144-execute.py', Path(__file__)]:
    compile(p.read_text(encoding='utf-8'), str(p), 'exec')
P = {'id': 'D144', 'at': h.now(), 'status': 'FROZEN_PRE_COMPILER_AND_SOLVES', 'measurement_epoch': 'RAM20261028', 'rustc_command': cmd, 'GPU_uuid': 'GPU-a5459b5a-632b-3e73-d7f1-a06e167102ee', 'required_free_bytes': 74 * 1024**3, 'raw_reservation_bytes': 8 * 1024**3, 'snapshot_count': 6, 'samples': {'rainbow': [20, 200], 'two-tone': [20, 200], 'river': [20, 60]}, 'input_sha256': {str(p): h.sha(p) for p in files}, 'scope': 'One compiler and one accepted-source full fixture process with exactly six read-only snapshots, then retained-raw reader. No candidate activation, quality change, timing score, hardware counters or extra samples. Source owner uniqueness plus actual writer/bounds metadata proves the two observed down-input subsets. Any sampled flop zero reach merely permits a whole-solve screen, without predicted saving or guard-finiteness claim. If all sampled flop subsets have zero such hands, decline as unmotivated. All output X.'}
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
    assert not any(x['id'] in ['D144', 'D144R1'] for x in s['experiments'])
    s['experiments'].append({'id': 'D144', 'title': 'Actual zero-reach input incidence in E080', 'kind': 'diagnostic', 'status': 'running', 'accepted': False, 'correctness': 'pending', 'stage': 'Frozen six-snapshot diagnostic', 'reason': 'Read actual inputs from two declared training subsets at early/final iterations. Zero reach alone does not establish guard eligibility or time savings.', 'measurement_epoch': 'RAM20261028', 'evidence': [{'label': 'Frozen incidence diagnostic', 'url': 'evidence/D144-incidence/protocol.json'}]})
    x = next(x for x in s['experiments'] if x['id'] == 'E091')
    x.update(stage='Finite raw controls passed; production incidence next', correctness='raw_controls_pass', reason='1530 raw cases and3060 launches passed with full actual input/output images, guards and both zero signs. Resource prerequisites passed. Exact full solver behavior and speed remain unqualified.')
    x.setdefault('evidence', []).append({'label': 'Raw GPU comparison', 'url': 'evidence/E091-raw-control-result/report.json'})
    s.update(updated_at=h.now(), active_experiment='D144', stage='E091 production incidence diagnostic', activity='Check actual sampled zero-reach density in unchanged E080 solves before freezing a candidate speed screen.')
    h.ar.atomic_json(h.ar.STATUS, s)
dst = h.ar.DASHBOARD / 'evidence/E091-raw-control-result/report.json'
dst.parent.mkdir(parents=True, exist_ok=True)
assert not dst.exists()
shutil.copyfile(ROOT / 'comparisons/E091-raw-control/report.json', dst)
print(h.sha(H / 'protocol.json'), flush=True)
