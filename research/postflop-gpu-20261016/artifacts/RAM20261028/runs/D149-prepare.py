import sys, re, shutil, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
import numpy as np
h.custody()
assert not (ROOT / 'gpu-run.lock').exists()
h.ar.refuse_active(h.ar.live_status())
assert h.read(ROOT / 'comparisons/D148-packet-model/report.json')['status'] == 'pass_finite_integer_packet_model'
assert shutil.disk_usage(ROOT).free >= 162 * 1024**3
H = ROOT / 'runs/D149-CFV-liveness'
H.mkdir(exist_ok=False)
gpu = H / 'gpu'
gpu.mkdir()
parent = ROOT / 'runs/E090-engine-control/reference/D134-observer-parent.rs'
t = parent.read_text(encoding='utf-8')
shim = t[t.index('pub mod plan {'):t.index('\nmod arena;')]
validator = t[t.index('impl GpuSolver {\n    pub fn d134_validate'):].replace('d134_validate', 'd149_validate').replace('D134', 'D149')
production = (h.REPO / 'crates/solver/src/gpu/mod.rs').read_text(encoding='utf-8')
assert production.count('pub mod plan;') == production.count('plan.use_full_action_arenas(&solver.spot);') == 1
prefix_end = production.index('    pub fn new(solver:')
start = production.index('    /// Research-only counterpart')
section = production[start:prefix_end]
annotation = '    #[cfg(feature = "preflop-research")]\n'
assert section.count(annotation) == 2
exposed = section.replace(annotation, '')
adapted = production[:start] + exposed + production[prefix_end:]
adapted = adapted.replace('pub mod plan;', shim, 1).replace('plan.use_full_action_arenas(&solver.spot);', 'plan::full_arena_adapter(&mut plan, &solver.spot);', 1)
reverse = adapted.replace(shim, 'pub mod plan;', 1).replace('plan::full_arena_adapter(&mut plan, &solver.spot);', 'plan.use_full_action_arenas(&solver.spot);', 1)
assert reverse.replace(exposed, section, 1) == production
body = production[production.index('pub struct GpuSolver {'):production.index('\nfn checks_with_setup')]
fields = []
for name, kind, size in re.findall(r'^\s*(\w+):\s*(CudaSlice<\w+>|\[CudaSlice<\w+>;\s*(\d+)\])', body, re.M):
    if size:
        fields.extend((f'{name}[{i}]', f'&self.{name}[{i}]') for i in range(int(size)))
    else:
        fields.append((name, '&self.' + name))
assert len(fields) == 66 and len({x[0] for x in fields}) == 66
observer = (ROOT / 'runs/D149-observer-template.rs').read_text(encoding='utf-8')
assert observer.count('// D149_ALL_DEVICE_FIELDS') == 1
observer = observer.replace('// D149_ALL_DEVICE_FIELDS', '\n        '.join(f'field!("{name}", {expr});' for name, expr in fields), 1)
(gpu / 'mod.rs').write_bytes((adapted + '\n' + validator + '\n' + observer).encode())
for name in ['arena.rs', 'kernels.cu']:
    shutil.copyfile(h.REPO / 'crates/solver/src/gpu' / name, gpu / name)
capture_parent = ROOT / 'runs/E090-engine-control/probe.rs'
capture = capture_parent.read_text(encoding='utf-8')
helpers = capture[capture.index('pub trait Word'):capture.index('fn emit(')].replace('E090', 'D149')
prefix = '''#![allow(dead_code,unused_imports,unused_mut,hidden_glob_reexports)]
pub use solver::*;
use solver::store::{Store,Storage};
use cudarc::driver::{CudaContext,CudaSlice,CudaStream,DeviceRepr};
use serde_json::{json,Value};
use std::{fs::{File,OpenOptions},io::{BufWriter,Write},path::{Path,PathBuf},sync::Arc};
#[path="gpu/mod.rs"]mod observed;
'''
(H / 'probe.rs').write_bytes((prefix + helpers + (ROOT / 'runs/D149-main.rs').read_text(encoding='utf-8')).encode())
h.save(H / 'source-review.json', {'at': h.now(), 'accepted_source_reversal_exact_after_standalone_plan_and_cfg_exposure_adapters': True, 'production_numerical_work_and_main_kernel_unchanged': True, 'appended_observer_writes_only_d_cfv': True, 'same_GPU_type_both_arms': True, 'device_field_inventory': [x[0] for x in fields], 'constructor_validator': 'Exact retained D134/E090 all66 actual buffer validator renamed only.', 'continuation_exposure': 'Remove exactly two cfg attributes around unchanged plain continuation methods in standalone copy. Child continuation modules remain cfg excluded. No application source feature is activated.', 'readback_contract': 'Poison the whole CFV allocation at entry. Never change learning/reach/weights/metadata. All65 nonCFV device fields and host state must remain exact. After training/evaluation compare every current-player logical CFV word; all physical words retained, padding not claimed equivalent. Strategy/full sync leave poisoned CFV scratch until subsequent regeneration.', 'scope': 'Finite runtime liveness control. Both arms execute original numerical work, not any proposed packing. No new readback kernel, candidate optimization, performance observation, actual paging or universal safety proof.'})
for name in ['D149-audit.py', 'D149-execute.py']:
    p = ROOT / 'runs' / name
    compile(p.read_text(encoding='utf-8'), str(p), 'exec')
    shutil.copyfile(p, H / name.removeprefix('D149-'))
deps = ROOT / 'reference/accepted-e080-deps'
cmd = ['rustc', str(H/'probe.rs'), '--edition=2021', '-C', 'opt-level=3', '-C', 'codegen-units=1', '-C', 'lto=thin', '-L', 'dependency=' + str(deps)]
for crate, name in [('solver','libsolver-e2d3113d740308c1.rlib'),('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib'),('rayon','librayon-8ab48cfec9cf00f9.rlib')]:
    cmd += ['--extern', crate + '=' + str(deps/name)]
cmd += ['-o', str(H/'probe.exe')]
np_root = Path(np.__file__).parent
native = list(np_root.rglob('*multiarray_umath*.pyd'))
assert len(native) == 1
files = [Path(__file__), ROOT/'runs/D149-main.rs', ROOT/'runs/D149-observer-template.rs', parent, capture_parent, ROOT/'comparisons/D148-packet-model/report.json', ROOT/'runs/D148-packed-readback-design/design-review.json', ROOT/'reference/D141-cfv-width/report.json', ROOT/'epoch/common.py', ROOT/'epoch/accepted-source.json', ROOT/'epoch/protected-main.json', ROOT/'epoch/preexisting-target-artifacts.json', Path(np.__file__)] + native
files += [p for p in H.rglob('*') if p.is_file()] + [p for p in deps.iterdir() if p.is_file()]
h.save(H/'protocol.json', {'id': 'D149', 'at': h.now(), 'status': 'FROZEN_PRE_COMPILER_AND_GPU_CONTROL', 'rustc_command': cmd, 'cases': 36, 'ordinary_phases_per_case': 20, 'clobbers': 752, 'phase_pairs': 752, 'constructor_pairs': 36, 'exploitability_pairs': 324, 'continuation_root_pairs': 32, 'raw_GPU_frames': 3008, 'required_free_bytes': 162*1024**3, 'conservative_raw_reservation_bytes': 96*1024**3, 'numpy_version': np.__version__, 'input_sha256': {str(p): h.sha(p) for p in files}, 'scope': 'One native compiler, one finite serialized GPU liveness process, then independent full raw-word reader. Fixed36case matrix, pattern, stage order and gates. No new case/source/shape variant after an actual failure. Reader/pre-native adapter repairs preserve originals and cannot alter scientific observations. No performance or optimization claim. All output on X; S historical inputs already localized and read-only.', 'candidate_accepted': False})
h.custody()
print(h.sha(H/'protocol.json'), flush=True)
