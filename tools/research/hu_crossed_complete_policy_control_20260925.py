"""CPU-only complete-profile transport gate on one previously inspected deal.

May coexist with the registered GPU training worker: no GPU, new deal draws,
training reads, shared checkpoint writes, or production changes. Small bounded
new output directory only. This is not a poker effectiveness experiment.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import hashlib
import json
from pathlib import Path
import subprocess
import time
import numpy as np
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read, load_complete_cache
from reboot_research_idle_v1 import idle
from crossed_complete_policy_batch_v1 import evaluate_batch

PREFIX='crossed-complete-policy-control-v1'
STORE=Path('T:/GTOpen-research')/PREFIX


class FixtureBank:
    def __init__(self, identity): self.identity=identity
    def average(self, query, *, guard):
        guard(); rows=[]
        for o in query['observations']:
            # Deliberately distinguish banks, players and legal menu sizes.
            legal=[float((a+1+self.identity+o['actor'])**2) for a in range(o['n'])]
            total=sum(legal); rows.append([x/total for x in legal]+[0.]*(4-o['n']))
        return np.array(rows),np.ones(len(rows))


def main():
    start=time.monotonic()
    def guard():
        assert time.monotonic()-start<120 and idle()
    guard(); assert not STORE.exists()
    source_result=OUT/'action-integrated-replication-v1-result.json'
    frozen=read(source_result)
    source_metrics=Path(frozen['store'])/'iteration-0001/metrics.json'
    assert sha(source_metrics)==frozen['steps'][0]['metrics_sha256']
    source_batch=source_metrics.parent/'batch-00/batch.json'
    assert sha(source_batch)==read(source_metrics)['subbatches'][0]['artifacts']['batch']
    context=OUT/'bb-context-candidate.json'
    query_exe=ROOT/'target/release/examples/hu_sampled_bank_bridge.exe'
    eval_exe=ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'
    paths=[Path(__file__).resolve(),source_result,source_metrics,source_batch,context,query_exe,eval_exe]
    paths.extend(ROOT/'tools/research'/name for name in (
        'crossed_complete_policy_batch_v1.py','crossed_complete_policy_comparison_v1.py',
        'sampled_batch_protocol_v2.py','sampled_evaluation_intervals_v1.py'))
    inputs={str(p):sha(p) for p in paths}
    registration=OUT/f'{PREFIX}-registration.json'
    save(registration,dict(inputs=inputs,deal_source=str(source_batch),deals=1,
        maximum_seconds=120,maximum_output_bytes=20_000_000,gpu_used=False,
        fresh_holdout=False,production_modified=False,
        scope='Previously inspected deal, artificial visible-only policies, complete-profile crossing and native transport equivalence. No trained-policy effectiveness evidence.'))
    STORE.mkdir(); cache=load_complete_cache()
    batch=dict(format=2,batch_id=PREFIX,seed=0,query_limit=100000,deals=read(source_batch)['deals'][:1])
    banks=[FixtureBank(i) for i in range(4)]
    summary=evaluate_batch(batch=batch,folder=STORE/'actual',context_path=context,banks=banks,
        cache=cache,query_executable=query_exe,evaluation_executable=eval_exe,guard=guard)
    query=read(STORE/'actual/queries.json'); actual=read(STORE/'actual/profiles.json')
    reference=[]
    # Independent scalar construction, intentionally not calling crossed_profiles.
    for seed in range(2):
        for bb in range(2):
            for btn in range(2):
                rows=[]
                for o in query['observations']:
                    identity=seed*2+(bb if o['actor']==0 else btn)
                    ws=[float((a+1+identity+o['actor'])**2) for a in range(o['n'])]
                    row={k:o[k] for k in ('hi','lo','actor','n')}
                    row['probabilities']=[w/sum(ws) for w in ws]+[0.]*(4-o['n'])
                    rows.append(row)
                reference.append(dict(name=actual['profiles'][len(reference)]['name'],policies=rows))
    assert actual['profiles']==reference
    rp=STORE/'reference-profiles.json'; npth=STORE/'reference-native.json'
    save(rp,dict(format=1,context_source=context.read_text(),
        batch_source=(STORE/'actual/conditional-batch.json').read_text(),profiles=reference))
    guard()
    native=subprocess.run([str(eval_exe),str(context),str(STORE/'actual/conditional-batch.json'),str(rp),str(npth)],
        capture_output=True,text=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
    assert native.returncode==0,native.stderr
    before=read(npth); after=read(STORE/'actual/native.json')
    assert before==after
    scalar=[]
    for seed in range(2):
        ps=[p['deals'][0]['values'] for p in before['profiles'][4*seed:4*seed+4]]
        scalar.extend([ps[2][0]-ps[0][0],ps[3][0]-ps[1][0],ps[1][1]-ps[0][1],ps[3][1]-ps[2][1]])
    assert read(STORE/'actual/residuals.json')['values']==[scalar]
    artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()}
    size=sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file()); assert size<=20_000_000
    for p,h in inputs.items(): guard(); assert sha(p)==h,p
    result=dict(passed=True,registration_sha256=sha(registration),deals=1,profiles=8,
        observations=len(query['observations']),profile_transport_exact=True,native_outputs_exact=True,
        paired_contrast_orientation_exact=True,artifacts=artifacts,logical_bytes=size,
        seconds=time.monotonic()-start,gpu_used=False,production_modified=False,accuracy_qualified=False)
    save(OUT/f'{PREFIX}-result.json',result); print(json.dumps(result))


if __name__=='__main__': main()
