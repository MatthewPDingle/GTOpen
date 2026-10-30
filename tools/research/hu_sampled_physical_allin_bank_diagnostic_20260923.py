"""Post-audit training-bank decomposition; never selects a replacement policy."""
import os
os.environ['OPENBLAS_NUM_THREADS']='2'
os.environ['OMP_NUM_THREADS']='2'
import json
from pathlib import Path
import time
import numpy as np
from sampled_physical_root_evaluation_v1 import ROOT,sha,save,hand_class
from sampled_physical_checkpoint_v1 import read_object,model_document,verify_bank
from sampled_physical_cpu64_v1 import CpuBank64
from loopback_research_validation import idle

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-physical-allin-bank-diagnostic-v1'
SOURCE='sampled-physical-allin-evaluation-v2'


def main():
    began=time.monotonic()
    def guard():assert idle() and time.monotonic()-began<300
    guard()
    paths={k:OUT/f'{SOURCE}-{k}.json' for k in ('registration','result','independent-review','status')}
    reg,result,review,status=[json.loads(paths[k].read_text()) for k in paths]
    assert review['passed'] and status['state']=='complete' and result['terminal']
    assert review['result_sha256']==sha(paths['result']) and review['registration_sha256']==sha(paths['registration'])
    comparison_path=OUT/'sampled-physical-allin-comparison-v1-result.json'
    comparison=json.loads(comparison_path.read_text());candidate=comparison['candidates']['allin']
    assert candidate['evidence'][str(paths['result'])]==sha(paths['result'])
    assert comparison['btn']['result']['passed']
    for p,h in reg['inputs'].items():assert sha(p)==h,p
    objects=Path(reg['objects']);checkpoint=json.loads(read_object(objects,reg['checkpoint']))
    verify_bank(objects,78,checkpoint['played_bank'],checkpoint['next_model'])
    docs=[model_document(objects,r) for r in checkpoint['played_bank']]
    bank=CpuBank64(docs,context_source=Path(reg['context']).read_text())
    observations={};query_hashes={}
    for offset in range(0,8192,16):
        guard();folder=Path(reg['store'])/f'{SOURCE}-train-{offset}'
        sp=folder/'summary.json';assert sha(sp)==result['batch_summary_hashes'][folder.name]
        summary=json.loads(sp.read_text());qp=folder/'queries.json'
        assert sha(qp)==summary['artifacts']['queries.json'];query_hashes[str(qp)]=sha(qp)
        for o in json.loads(qp.read_text())['observations']:
            if o['phase']!=0 or int(o['hi'])!=1:continue
            assert o['actor']==0 and o['n']==4 and not o['own_history']
            key=int(o['lo']);c=hand_class([key&63,(key>>6)&63])
            if c in observations:assert observations[c]['active_features']==o['active_features']
            observations[c]=o
        if len(observations)==169:break
    assert len(observations)==169
    source_paths=[Path(__file__),comparison_path,*paths.values(),
        ROOT/'tools/research/sampled_physical_cpu64_v1.py',
        ROOT/'tools/research/sampled_physical_checkpoint_v1.py']
    registration=dict(inputs={str(p):sha(p) for p in source_paths},query_artifacts=query_hashes,
        played_generations=list(range(78)),blocks=[[i,i+12] for i in range(0,78,13)],
        scope='Post-audit decomposition of all played root policies, retaining every generation and class. No replacement checkpoint, fresh strength test, training target or deployment. Later blocks face changing opponents and continuations, so drift is not proof of better play.',production_modified=False)
    rp=OUT/f'{PREFIX}-registration.json';save(rp,registration)
    obs=[observations[c] for c in range(169)]
    x=np.zeros((169,269))
    for i,o in enumerate(obs):x[i,o['active_features']]=1.
    policies=[]
    for networks in bank.models:
        guard();y=x
        for layer,(w,b) in enumerate(networks[0]):
            y=y@w.T+b
            if layer!=2:y=np.maximum(y,0.)
        p=np.maximum(y,0.);s=p.sum(1);positive=s>0;p[positive]/=s[positive,None]
        for i in np.flatnonzero(~positive):p[i,int(np.argmax(y[i]))]=1.
        assert np.max(np.abs(p.sum(1)-1))<1e-12
        policies.append(p)
    policies=np.array(policies);mean=policies.mean(0)
    expected=np.array([r['baseline_probabilities'] for r in candidate['classes']])
    error=float(np.max(np.abs(mean-expected)));assert error<1e-10
    weights=np.asarray(result['evaluation_class_counts'],float)/16384
    combos=np.array([6 if c//13==c%13 else 4 if c//13>c%13 else 12 for c in range(169)],float)/1326
    mixes=np.einsum('gca,c->ga',policies,weights)
    combo_mixes=np.einsum('gca,c->ga',policies,combos)
    assert np.max(np.abs(mixes.mean(0)-candidate['baseline_action_mix']))<1e-12
    blocks=[dict(first=i,last=i+12,test_deal_weighted_mix=mixes[i:i+13].mean(0).tolist(),
        combo_weighted_mix=combo_mixes[i:i+13].mean(0).tolist()) for i in range(0,78,13)]
    for p,h in {**registration['inputs'],**query_hashes}.items():assert sha(p)==h,p
    output=dict(passed=True,registration_sha256=sha(rp),maximum_average_reconstruction_error=error,
        action_order=['fold','call','raise','jam'],classes=[r['hand'] for r in candidate['classes']],
        policies_by_generation=policies.tolist(),blocks=blocks,
        uniform_generation_zero_mix_contribution=(mixes[0]/78).tolist(),
        full_test_deal_weighted_mix=mixes.mean(0).tolist(),
        full_combo_weighted_mix=combo_mixes.mean(0).tolist(),seconds=time.monotonic()-began,
        production_modified=False,scope=registration['scope'])
    save(OUT/f'{PREFIX}-result.json',output)
    print(json.dumps({k:v for k,v in output.items() if k not in ('policies_by_generation','classes')}))


if __name__=='__main__':main()
