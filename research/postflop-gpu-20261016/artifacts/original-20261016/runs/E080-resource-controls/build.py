"""Two frozen resource observation harnesses; solver source never activated."""
from pathlib import Path
import sys,shutil
H=Path(__file__).resolve().parent;R=H.parent.parent;sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');B=H/'build'
def verify():
    for p,h in P['input_sha256'].items():old.pin(p,h)
    old.custody()
verify();assert not B.exists()
with old.ar.exclusive_lock(R/'gpu-run.lock'):
    old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3;B.mkdir();pins={}
    for row in P['compilers']:
        verify();out=B/row['arm'];out.mkdir();old.child(row['command'],out,'rustc',old.env(),600);verify();binary=Path(row['binary']);assert(old.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes()in binary.read_bytes();old.save(binary.with_suffix('.manifest.json'),{'at':old.now(),'arm':row['arm'],'binary_sha256':old.sha(binary),'source_sha256':row['source_sha256'],'harness_sha256':old.sha(H/'evaluator.rs'),'dependency_artifact_sha256':row['dependencies'],'build_command':row['command'],'protocol_sha256':sys.argv[1],'purpose':'OS resource observation only; no performance score','candidate_accepted':False});pins[str(binary)]=old.sha(binary);pins[str(binary.with_suffix('.manifest.json'))]=old.sha(binary.with_suffix('.manifest.json'));print('Compiled resource harness',row['arm'],flush=True)
    old.save(B/'complete.json',{'at':old.now(),'all_compilers_terminal':True,'solver_executions':0,'artifact_sha256':pins,'source_main_live_PTX_unchanged':True});verify()
