"""Compile-only final code generation; no native/GPU execution."""
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
