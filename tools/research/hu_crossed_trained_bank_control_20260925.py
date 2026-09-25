"""CPU-only audited pilot-bank, complete-crossing and archive/readback control."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read,load_complete_cache
from reboot_research_idle_v1 import idle
from hu_action_integrated_exact_20260925 import bank_args
from frozen_complete_trial_bank_v1 import load_completed_trial
from action_integrated_policy_v1 import ActionIntegratedCpuBank64,probabilities
from sampled_physical_bank_v1 import histories
from crossed_complete_policy_batch_v1 import evaluate_batch
from owned_batch_archive_v1 import OwnedBatchArchive
from archived_evaluation_reader_v1 import ArchivedEvaluationReader

PREFIX='crossed-trained-bank-control-v1'
STORE=Path('T:/GTOpen-research')/PREFIX


class ScalarBank:
    def __init__(self,models,weights,args):self.models,self.weights,self.args=models,weights,args
    def average(self,q,*,guard):
        args={k:v for k,v in self.args.items() if k!='context_source'}
        ps=[probabilities(q,m,device='cpu',**args)[0] for m in self.models]
        past=histories(q['observations']);result=[];support=[]
        for i,o in enumerate(q['observations']):
            guard();num=[0.]*4;den=0.
            for g,p in enumerate(ps):
                w=self.weights[o['actor'],g]
                for j,a in past[i]:w*=p[j,a]
                den+=w
                for a in range(4):num[a]+=w*p[i,a]
            result.append([v/den for v in num] if den>0 else [float(a<o['n'])/o['n'] for a in range(4)])
            support.append(den)
        return np.array(result),np.array(support)


def main():
    start=time.monotonic();last=0.
    def guard():
        nonlocal last
        now=time.monotonic();assert now-start<600
        if now-last>2:assert idle();last=now
    guard();assert not STORE.exists()
    context=OUT/'bb-context-candidate.json';args=bank_args(context.read_text())
    source=Path('T:/GTOpen-research/crossed-complete-policy-control-v1/actual/query-batch.json')
    source_result=OUT/'crossed-complete-policy-control-v1-result.json'
    prior=read(source_result);assert prior['passed'] and prior['artifacts'][str(source)]==sha(source)
    paths=[Path(__file__).resolve(),context,source,source_result]
    paths.extend(ROOT/'tools/research'/name for name in (
        'frozen_complete_trial_bank_v1.py','crossed_complete_policy_batch_v1.py',
        'crossed_complete_policy_comparison_v1.py','owned_batch_archive_v1.py',
        'sampled_evidence_archive_v1.py','archived_evaluation_reader_v1.py'))
    paths.extend(OUT/f'later-action-joint-control-v1-{s}.json' for s in
        ('registration','result','readback-registration','independent-review'))
    query_exe=ROOT/'target/release/examples/hu_sampled_bank_bridge.exe'
    eval_exe=ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'
    paths.extend([query_exe,eval_exe]);inputs={str(p):sha(p) for p in paths}
    rp=OUT/f'{PREFIX}-registration.json'
    save(rp,dict(inputs=inputs,maximum_seconds=600,maximum_output_bytes=20_000_000,
        gpu_used=False,production_modified=False,fresh_holdout=False,
        scope='Two-update audited pilot versus its initial model for integration only; scalar own-reach and lossless archived native batch verification. No strength claim.'))
    models,weights,identity=load_completed_trial(OUT,'later-action-joint-control-v1',
        expected_updates=2,bank_args=args,guard=guard)
    assert identity['played_generations']==[0,1] and identity['excluded_generation']==2
    base=ActionIntegratedCpuBank64(models[:1],completed_iterations=1,weights_by_player=np.ones((2,1)),**args)
    candidate=ActionIntegratedCpuBank64(models,completed_iterations=2,weights_by_player=weights,**args)
    scalar=ScalarBank(models,weights,args)
    STORE.mkdir();archives=OwnedBatchArchive.create(STORE,guard=guard);folder=archives.begin('test-000000')
    batch=dict(read(source),batch_id=PREFIX);cache=load_complete_cache()
    summary=evaluate_batch(batch=batch,folder=folder,context_path=context,banks=[base,candidate,base,candidate],
        cache=cache,query_executable=query_exe,evaluation_executable=eval_exe,guard=guard)
    query=read(folder/'queries.json');p,s=candidate.average(query,guard=guard);q,t=scalar.average(query,guard=guard)
    policy_error=float(np.max(abs(p-q)));reach_error=float(np.max(abs(s-t)))
    assert policy_error<1e-10 and reach_error<1e-10
    assert np.array_equal(np.asarray(summary['values'])[:,0],np.asarray(summary['values'])[:,1])
    before={p.name:sha(p) for p in folder.iterdir()}
    sizes={p.name:p.stat().st_size for p in folder.iterdir()}
    manifest=archives.publish('test-000000');assert archives.release('test-000000')==manifest
    reader=ArchivedEvaluationReader(STORE,{'test-000000':manifest},external_files=[],guard=guard)
    for name,h in before.items():
        raw=reader.read_bytes(STORE/'test-000000'/name)
        assert hashlib.sha256(raw).hexdigest()==h and len(raw)==sizes[name]
    assert reader.read_json(STORE/'test-000000/summary.json')==summary
    assert not folder.exists()
    for p,h in inputs.items():guard();assert sha(p)==h,p
    from ntfs_research_storage_v1 import measure_tree
    storage=measure_tree(STORE,guard);assert storage['logical_bytes']<20_000_000
    result=dict(passed=True,registration_sha256=sha(rp),bank_identity=identity,
        maximum_scalar_policy_error=policy_error,maximum_scalar_reach_error=reach_error,
        duplicate_seed_profiles_exact=True,archive_manifest_sha256=manifest,
        owner_sha256=archives.owner_sha256,original_artifact_hashes=before,storage=storage,
        seconds=time.monotonic()-start,gpu_used=False,production_modified=False,accuracy_qualified=False)
    save(OUT/f'{PREFIX}-result.json',result);print(json.dumps(result))


if __name__=='__main__':main()
