"""Complete the fixed replay check after a JSON reference-key ordering mismatch.

No GPU retry. Native calculation bytes, model/checkpoint identities, and all
numeric state must match. Only object-key ordering in the initial-policy
metadata is normalized; no numeric tolerance is added.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import time
import numpy as np
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read
from reboot_research_idle_v1 import idle
from hu_action_integrated_exact_20260925 import bank_args
from later_action_checkpoint_v1 import restore_checkpoint
from new_volume_research_store_v1 import measure_store

PREFIX='checkpoint-volume-replay-review-v2'
REPLAY='checkpoint-volume-replay-control-v1'
PILOT='later-action-joint-control-v1'


def main():
    start=time.monotonic();last=0.
    def guard():
        nonlocal last
        now=time.monotonic();assert now-start<600
        if now-last>2:
            assert idle() and psutil.virtual_memory().available>20_000_000_000
            last=now
    guard()
    import torch
    torch.set_num_threads(1);assert not torch.cuda.is_available()
    oldrp=OUT/f'{REPLAY}-registration.json';oldstatus=OUT/f'{REPLAY}-status.json';oldlog=OUT/f'{REPLAY}.log'
    oldreg,status=read(oldrp),read(oldstatus)
    assert status['state']=='failed' and status['exit_code']==1
    assert oldlog.read_text().rstrip().endswith('AssertionError: initial_policy_sha256')
    result=read(OUT/f'{PILOT}-result.json');cfg=result['config']
    source=Path(result['store']);target=Path(oldreg['store'])
    oldfolder=source/'iteration-0002';newfolder=target/'iteration-0002'
    inputs=dict(oldreg['inputs'])
    paths=[oldrp,oldstatus,oldlog,Path(__file__).resolve()]
    paths.extend(p for p in target.rglob('*') if p.is_file())
    inputs.update({str(p):sha(p) for p in paths})
    for p,h in inputs.items():guard();assert sha(p)==h,p
    rp=OUT/f'{PREFIX}-registration.json'
    save(rp,dict(inputs=inputs,config=cfg,original_replay_registration_sha256=sha(oldrp),maximum_seconds=600,
        gpu_used=False,production_modified=False,
        scope='Read-only completion of already executed fixed GPU replay. Compare canonical initial-policy metadata, exact native bytes and entire saved state; preserve original failed byte-order check.'))
    old=read(oldfolder/'metrics.json');new=read(newfolder/'metrics.json')
    a=read(oldfolder/'current-initial-policy.json');b=read(newfolder/'current-initial-policy.json')
    assert a==b
    # Prove the byte difference is exactly the ordering of used_model's keys.
    restored_order=dict(b,used_model={key:b['used_model'][key] for key in a['used_model']})
    assert (json.dumps(restored_order,separators=(',',':'),allow_nan=False)+'\n').encode()==(oldfolder/'current-initial-policy.json').read_bytes()
    assert old['initial_policy_sha256']==sha(oldfolder/'current-initial-policy.json')
    assert new['initial_policy_sha256']==sha(newfolder/'current-initial-policy.json')
    assert old['checkpoint']==new['checkpoint']==result['final_checkpoint']
    for key in old:
        if key not in ('fits','root_integration_seconds','initial_policy_sha256'):assert old[key]==new[key],key
    timing={'setup_seconds','optimizer_seconds','graph_capture_seconds'}
    for a,b in zip(old['fits'],new['fits']):
        assert {k:v for k,v in a.items() if k not in timing}=={k:v for k,v in b.items() if k not in timing}
    ignored={'metrics.json','current-initial-policy.json'}
    before={p.relative_to(oldfolder):sha(p) for p in oldfolder.rglob('*') if p.is_file() and p.name not in ignored}
    after={p.relative_to(newfolder):sha(p) for p in newfolder.rglob('*') if p.is_file() and p.name not in ignored}
    assert before==after
    args=bank_args((OUT/'bb-context-candidate.json').read_text())
    a=restore_checkpoint(source/'objects',old['checkpoint'],config=cfg,**args)
    b=restore_checkpoint(target/'objects',new['checkpoint'],config=cfg,**args)
    for key in ('completed_iterations','played_bank','next_model','next_model_document'):assert a[key]==b[key],key
    for key in ('exact_btn_state','root_regret_state'):assert a[key].document()==b[key].document(),key
    for x,y in zip(a['reservoirs'],b['reservoirs']):
        assert x.summary()==y.summary() and x.rng.bit_generator.state==y.rng.bit_generator.state
        for key in ('keys','active','arity','values','iterations'):assert getattr(x,key).tobytes()==getattr(y,key).tobytes(),key
    assert a['sampler'].checkpoint()==b['sampler'].checkpoint() and a['sampler'].sample(8)==b['sampler'].sample(8)
    assert a['action_rng'].bit_generator.state==b['action_rng'].bit_generator.state
    assert np.array_equal(a['action_rng'].integers(2**63,size=64),b['action_rng'].integers(2**63,size=64))
    storage=measure_store(target,guard);assert storage['files']==storage['compressed_files']
    for p,h in inputs.items():guard();assert sha(p)==h,p
    answer=dict(passed=True,registration_sha256=sha(rp),original_gpu_replay_check_failed=True,
        checkpoint=new['checkpoint'],exact_checkpoint=True,exact_native_artifacts=True,
        exact_reservoirs_and_accumulators=True,next_action_and_deal_streams_exact=True,
        exact_initial_policy_values=True,initial_metadata_raw_bytes_equal=False,
        difference='used_model reference dictionary key order only',native_files_compared=len(before),
        storage=storage,seconds=time.monotonic()-start,gpu_used=False,production_modified=False,
        accuracy_qualified=False,scope='Exact numerical replay and state continuation established from saved artifacts. No new GPU execution or strength conclusion.')
    save(OUT/f'{PREFIX}-result.json',answer)
    save(OUT/f'{PREFIX}-status.json',dict(state='complete',error=None,production_modified=False))
    print(json.dumps(answer),flush=True)


if __name__=='__main__':main()
