"""Type-check the actual arena source and run its CPU-only unit tests."""
from pathlib import Path
import ast
import shutil
import sys
import urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
C=R/'runs/accepted-E080-live-20261018'
sys.path.insert(0,str(C));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists()
S=R/'runs/E087-source';M=old.read(S/'manifest.json')
H=R/'runs/E087-host-type-check';H.mkdir(exist_ok=False)
arena=Path(M['owned']['crates/solver/src/gpu/arena.rs']['candidate'])
old.pin(arena,M['candidate_owned_sha256']['crates/solver/src/gpu/arena.rs'])
mod=(old.REPO/'crates/solver/src/gpu/mod.rs').read_text()
at=mod.index('fn write_arena(');opening=mod.index('{',at);end=opening+1;depth=1
while depth:
    depth+=(mod[end]=='{')-(mod[end]=='}');end+=1
writer=mod[at:end]
probe=(
    '#![allow(dead_code,unused_imports,unused_mut)]\n'
    'pub use solver::*;\n'
    'mod gpu {\n'
    ' use solver::{Solver,store::Store};\n'
    ' use rayon::prelude::*;\n'
    ' pub mod plan { pub use solver::gpu::plan::*; }\n'
    ' fn e(err:impl std::fmt::Debug)->String {format!("cuda: {err:?}")}\n'
    +writer+'\n'
    +f' #[path = r"{arena}"] mod arena;\n'
    +'}\n'
)
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
expected=arena.read_text().count('#[test]')
assert expected==7
code='''import json,re,sys
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'));import common_e080_live as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
def verify():
 old.custody();old.pin(H/'protocol.json',sys.argv[1])
 for p,h in P['input_sha256'].items():old.pin(p,h)
verify();O=H/'execution';O.mkdir(exist_ok=False);assert not(H/'probe.exe').exists()
with old.ar.exclusive_lock(R/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status())
 old.child(P['rustc_command'],O,'rustc',old.env(),600);verify()
 old.child([str(H/'probe.exe'),'--nocapture','--test-threads=1'],O,'units',old.env(),300);verify()
 raw=(O/'units.stdout.log').read_text()
 assert re.findall(r'test result: ok\\. (\\d+) passed; (\\d+) failed; (\\d+) ignored; (\\d+) measured; (\\d+) filtered out;',raw)==[('7','0','0','0','0')]
 old.save(O/'complete.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'binary_sha256':old.sha(H/'probe.exe'),'unit_tests_passed':7,'new_bounded_units':2,'GPU_contexts':0,'GPU_kernels':0,'performance_measurement':False,'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True})
 print('7 CPU arena units pass; actual bounded methods type-check',flush=True)
'''
ast.parse(code);(H/'execute.py').write_text(code,encoding='utf-8',newline='\n')
deps=old.read(R/'binaries/E080-postflop_autoresearch.manifest.json')['dependency_artifact_sha256']
libs={n:next(p for p in deps if Path(p).name.startswith('lib'+n+'-')and Path(p).suffix=='.rlib')for n in ['solver','rayon','cudarc']}
cmd=['rustc',str(H/'probe.rs'),'--edition=2021','--test','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(Path(libs['solver']).parent)]
for n,p in libs.items():cmd+=['--extern',n+'='+p]
cmd+=['-o',str(H/'probe.exe')]
paths=[Path(__file__),H/'probe.rs',H/'execute.py',S/'manifest.json',S/'source-review.json',
    *[Path(v['candidate'])for v in M['owned'].values()],C/'common_e080_live.py',C/'protected-main.json']
P={'id':'E087-host-type-check','at':old.now(),'status':'FROZEN_PRE_COMPILER_AND_CPU_UNITS',
    'rustc_command':cmd,'input_sha256':deps|{str(p):old.sha(p)for p in paths},
    'expected_cpu_units':7,'new_units':2,
    'scope':'Compile the exact candidate arena source against accepted Solver/Store/GpuPlan/CUDA types, with exact accepted full writer and parent error adapter. Run only5original CPU arena units+2new grouping/span units. No CUDA context/allocation, GPU call, production source activation or performance sample.',
    'candidate_accepted':False}
old.save(H/'protocol.json',P)
for p in H.iterdir():
    key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
    assert not dst.exists();shutil.copyfile(p,dst)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as response:assert response.read()==p.read_bytes()
old.custody();print(old.sha(H/'protocol.json'),flush=True)
