"""Run only the selected live-state continuation correctness controls."""
import json, os, subprocess, sys
from pathlib import Path
repo=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0,str(repo/'tools'))
import postflop_autoresearch as ar
controls=[
 ('V016-continuation-invalidation','E016-continuation-tests','gpu::tests::paired_reach_reuse_continuation_invalidates_before_validation_and_changed_roots'),
 ('V016-continuation-paging','E016-continuation_paging','paging_preserves_resident_trajectories_and_rejects_invalid_inputs'),
 ('V016-continuation-rejection','E016-continuation_symmetry','symmetric_continuation_rejects_unsupported_inputs_without_mutation'),
 ('V016-continuation-stored','E016-continuation-tests','gpu::continuation::storage::device_tests::direct_gpu_storage_preserves_720_full_state_passes'),
]
state=ar.RESEARCH/'runs/V016-stored-state'
state.mkdir(exist_ok=False)
ar.atomic_json(ar.RESEARCH/'runs/V016-feature-environment.json',{
 'created_at':ar.now(),'GTO_SSD_STUDY_DIR':str(state),'storage_scope':'Stored-state test uses u64::MAX remaining RAM, not forced SSD spill',
 'selected_tests':[{'id':i,'binary':b,'filter':t} for i,b,t in controls]})
for identity,binary,test in controls:
    env=os.environ.copy();env['GTO_SSD_STUDY_DIR']=str(state)
    for key in ('POSTFLOP_AUTORESEARCH_PROFILE','POSTFLOP_AUTORESEARCH_FIXTURE','POSTFLOP_AUTORESEARCH_STORAGE'):
        env.pop(key,None)
    cmd=[sys.executable,'tools/postflop_autoresearch.py','--id',identity,'--title','E016 continuation lifecycle correctness',
         '--kind','validation','--binary',str(ar.RESEARCH/'binaries'/(binary+'.exe')),
         '--build-manifest',str(ar.RESEARCH/'binaries'/(binary+'.manifest.json')),'--test',test,'--not-ignored']
    subprocess.run(cmd,cwd=repo,env=env,check=True)
    output=(ar.RESEARCH/'runs'/identity/'stdout.log').read_text(encoding='utf-8')
    assert '1 passed; 0 failed; 0 ignored' in output,(identity,output[-2000:])
    assert test in output
print('All four selected continuation controls passed.',flush=True)
