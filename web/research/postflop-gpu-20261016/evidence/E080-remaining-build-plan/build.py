"""Compile only the two missing candidate evaluators against frozen libraries."""
from pathlib import Path
import json,shutil,sys
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');O=R/'runs/E080-remaining-build'
def verify():
    old.pin(H/'protocol.json',sys.argv[1])
    for p,h in P['input_sha256'].items():old.pin(p,h)
    old.custody()
verify();assert not O.exists()
with old.ar.exclusive_lock(R/'gpu-run.lock'):
    old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3;O.mkdir();artifacts={}
    for row in P['compilers']:
        verify();dest=Path(row['binary']);assert not dest.exists()and not dest.with_suffix('.manifest.json').exists();out=O/row['id'];out.mkdir();old.child(row['command'],out,'rustc',old.env(),600);verify()
        assert(old.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes()in dest.read_bytes()
        manifest={'candidate':'E080','purpose':row['id'],'source_sha256':old.BASE|P['candidate_owned_sha256'],'binary_sha256':old.sha(dest),'built_at':old.now(),'build_command':row['command'],'build_protocol_sha256':sys.argv[1],'build_script_sha256':old.sha(__file__),'harness_source':row['source'],'harness_source_sha256':old.sha(row['source']),'dependency_artifact_sha256':row['dependencies'],'source_relationship':'Exact existing capacity or fixed wide-turn evaluator and input. Pinned candidate solver library; no solver source activation or edits.','CUDA_source_unchanged':True,'CUDA_source_embedded':True,'native_executions':0,'candidate_accepted':False,'build_stdout_sha256':old.sha(out/'rustc.stdout.log'),'build_stderr_sha256':old.sha(out/'rustc.stderr.log')};old.save(dest.with_suffix('.manifest.json'),manifest)
        artifacts[str(dest)]=old.sha(dest);artifacts[str(dest.with_suffix('.manifest.json'))]=old.sha(dest.with_suffix('.manifest.json'));old.save(out/'complete.json',{'at':old.now(),'returncode':0,'binary_sha256':old.sha(dest),'native_executions':0});print('Compiled candidate',row['id'],flush=True)
    verify();old.save(O/'complete.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'all_compilers_terminal':True,'native_executions':0,'artifact_sha256':artifacts,'source_main_live_PTX_custody_pass':True,'accepted_baseline_binaries_reused_without_recompilation':True})
print('E080 remaining evaluators built; no solver observations executed.',flush=True)
