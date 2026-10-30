"""Freeze final ThinLTO code generation from immutable accepted E051 inputs."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D089-zero-scan-codegen';H.mkdir();B=H/'build'
m=old.read(ROOT/'binaries/E051-postflop_autoresearch.manifest.json');deps=m['dependency_artifact_sha256'];assert m['source_sha256']==old.BASE
libs={name:next(p for p in deps if Path(p).name.startswith('lib'+name+'-') and p.endswith('.rlib')) for name in ['solver','cudarc','serde_json']}
cmd=['rustc','--edition=2021','--test','--cfg','feature="gpu"',str(old.REPO/'crates/solver/tests/postflop_autoresearch.rs'),'--crate-name','postflop_autoresearch','-C','opt-level=3','-C','lto=thin','-C','codegen-units=1','--emit=asm,link']
for name,path in libs.items():cmd+=['--extern',name+'='+path]
cmd+=['-L','dependency='+str(Path(libs['solver']).parent),'-o',str(B/'postflop-codegen.exe')]
script='''"""Compile-only final code generation; no native/GPU execution."""
import json,shutil,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
old.custody();B=Path(P['output_dir']);assert not B.exists()
with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=54*1024**3;B.mkdir()
 old.child(P['command'],B,'rustc',old.env(),600);old.custody()
 for p,h in P['input_sha256'].items():old.pin(p,h)
 exe=B/'postflop-codegen.exe';data=exe.read_bytes();assert (old.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes() in data and b'D088_INIT ' not in data
 assembly=list(B.glob('*.s'));assert len(assembly)>0
 files={str(p):{'sha256':old.sha(p),'bytes':p.stat().st_size} for p in B.iterdir() if p.is_file()}
 old.save(H/'complete.json',{'at':old.now(),'compiler_terminal':True,'protocol_sha256':sys.argv[1],'binary_sha256':old.sha(exe),'assembly_files':[str(p) for p in assembly],'all_artifacts':files,'native_executions':0,'gpu_executions':0,'accepted_source_main_live_ptx_unchanged':True,'optimization_accepted':False})
print(json.dumps({'status':'compile_terminal','assembly_files':len(assembly),'complete_sha256':old.sha(H/'complete.json')}),flush=True)
'''
(H/'execute.py').write_text(script,encoding='utf-8',newline='\n')
paths=[H/'execute.py',old.REPO/'crates/solver/tests/postflop_autoresearch.rs',old.REPO/'bench_spot.json',old.REPO/'crates/solver/src/gpu/arena.rs',ROOT/'comparisons/D088-constructor-root-check/report.json',ROOT/'binaries/E051-postflop_autoresearch.manifest.json',ROOT/'runs/accepted-E051/common_e051.py']
p={'id':'D089-final-zero-scan-codegen','at':old.now(),'status':'FROZEN_COMPILE_ONLY','output_dir':str(B),'command':cmd,'accepted_source':'E051','purpose':'Inspect actual final ThinLTO serial integer-OR implementation before admitting an optimizer. D088measured188ms nested scans; E045parallel/E049metadata/E038omission remain closed.','input_sha256':dict(deps)|{str(x):old.sha(x) for x in paths},'method':'Unmodified frozen primary evaluator linked against exact measured E051 RLIBs, opt3/thinLTO/codegen1, emit final assembly and executable. No source activation or native execution.','limits':'New compile-only analysis artifact, not a byte-identical reproduction of previously timed E051executable or performance evidence. Library-stage scalar/vector claims are insufficient; inspect emitted final host functions. D019encoder evidence does not describe current integer-OR code.'}
old.save(H/'protocol.json',p)
for src in [H/'execute.py',H/'protocol.json']:
 key=H.name+'/'+src.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(src.read_bytes());assert urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15).read()==src.read_bytes()
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);assert not any(e['id']=='D089' for e in st['experiments']);st['experiments'].append({'id':'D089','title':'Final integer zero-scan machine code','kind':'diagnostic','status':'preparing','stage':'Frozen compile-only codegen','reason':'Inspect exact accepted solver library final ThinLTO output before any distinct zero-scan prototype. No production algorithm/source or native timing change.','evidence':[{'label':'D089 frozen final codegen protocol','url':'evidence/D089-zero-scan-codegen/protocol.json'}]});st.update(state='running',updated_at=old.now(),stage='D089 final zero-scan code generation',activity='Compile unmodified evaluator against acceptedE051libraries; inspect actual integer scan instructions without re-running closed variants.',active_experiment='D089');old.ar.atomic_json(old.ar.STATUS,st)
print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'solver_rlib':libs['solver']}),flush=True)
