"""Post-hoc accounting of initial uniform play in forced root continuations.

No evaluation outcomes, policy selection, fitting, GPU use or deployment.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import time
import numpy as np
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from sampled_visible_hybrid_checkpoint_v1 import read_object
from action_integrated_checkpoint_v1 import model_document
from action_integrated_policy_v1 import predict
from hu_action_integrated_exact_20260925 import bank_args
from reboot_research_idle_v1 import idle

PREFIX='initial-generation-share-v1'


def main():
    assert idle();started=time.monotonic()
    rp=OUT/f'{PREFIX}-registration.json';assert not rp.exists()
    inputs={str(p):sha(p) for p in [Path(__file__).resolve(),
        OUT/'paired-continuation-v1-registration.json',OUT/'paired-continuation-v1-result.json',
        ROOT/'tools/research/action_integrated_policy_v1.py',
        ROOT/'tools/research/action_integrated_checkpoint_v1.py',
        ROOT/'tools/research/exact_initial_single_policy64_v1.py']}
    trials=[]
    for tag,name in [('first','action-integrated-fresh-pilot-v1'),('replication','action-integrated-replication-v1')]:
        paths=[OUT/f'{name}-{s}.json' for s in ('registration','result','independent-review')]
        reg,result,audit=map(read,paths)
        assert result['passed'] and audit['passed'] and result['completed_iterations']==78
        assert audit['source_result_sha256']==sha(paths[1])
        assert result['registration_sha256']==audit['source_registration_sha256']==sha(paths[0])
        policy=Path(f'T:/GTOpen-research/action-integrated-{tag}-exact-v1/linear-policy.json')
        ep=OUT/f'action-integrated-{tag}-exact-v1-result.json'
        assert read(ep)['artifacts'][str(policy)]==sha(policy)
        inputs.update({str(p):sha(p) for p in [*paths,policy,ep]})
        trials.append(dict(name=name,result=str(paths[1]),policy=str(policy)))
    save(rp,dict(inputs=inputs,trials=trials,production_modified=False,gpu_used=False,
        analysis='All 169 classes and four root actions. Exact share contributed by generation 0 in the full linear played-bank root realization weight. Report >=50%, >=95%, and numerically all-generation-0 classes/mass, without policy selection.',
        motivation='Post-hoc follow-up to zero BB-policy effect for forced AKs calls in the preliminary paired continuation diagnostic; not a new predeclared accuracy test.',
        maximum_seconds=300,maximum_output_bytes=1_000_000))
    source=(OUT/'bb-context-candidate.json').read_text();args=bank_args(source)
    catalog=json.loads(args['catalog_source'])['native_observations']
    query=dict(context_source=source,observations=[x['observation'] for x in catalog])
    masses=read('T:/GTOpen-research/root-retained-wider-study-v1/evaluation/training-deals.json')['original_class_masses']
    rows=[]
    for t in trials:
        assert idle() and time.monotonic()-started<300
        result=read(t['result']);objects=Path(result['store'])/'objects'
        checkpoint=json.loads(read_object(objects,result['final_checkpoint']))
        assert len(checkpoint['played_bank'])==78
        ref=checkpoint['played_bank'][0];assert ref['generation']==0
        model=model_document(objects,ref,**args)
        _,p,_=predict(query,model,device='cpu',**{k:v for k,v in args.items() if k!='context_source'})
        initial=np.zeros((169,4))
        for item,prob in zip(catalog,p):
            if item['player']==0:initial[item['hand_class']]=prob
        assert np.max(abs(initial-.25))<1e-15
        policy=read(t['policy']);assert policy['played_generations']==list(range(78)) and policy['excluded_generation']==78
        assert policy['checkpoint']==result['final_checkpoint']
        assert policy['weights']==[list(range(1,79)),list(range(1,79))]
        average=np.asarray(policy['root_probabilities']);total_weight=sum(range(1,79))
        assert np.all(average>0) and total_weight==3081
        share=initial/(total_weight*average)
        assert np.all(share>=0) and np.all(share<=1+1e-12)
        groups=[]
        for action in range(4):
            subsets={name:share[:,action]>=threshold for name,threshold in [('at_least_half',.5),('at_least_95_percent',.95),('all_within_1e12',1-1e-12)]}
            groups.append(dict(action=action,thresholds={name:dict(classes=np.flatnonzero(mask).tolist(),count=int(mask.sum()),incoming_class_mass=float(np.asarray(masses)@mask)) for name,mask in subsets.items()},
                actual_action_mass_from_initial_generation=float(np.asarray(masses)@initial[:,action]/(total_weight*(np.asarray(masses)@average[:,action])))))
        rows.append(dict(trial=t['name'],initial_model_reference=ref,initial_probabilities=initial.tolist(),
            average_probabilities=average.tolist(),generation_zero_share=share.tolist(),summary=groups))
    for path,digest in inputs.items():assert sha(path)==digest,path
    save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(rp),trials=rows,
        class_masses=masses,seconds=time.monotonic()-started,production_modified=False,gpu_used=False,accuracy_qualified=False,
        scope='Generation-zero root-action realization accounting only. Correct behavioral averaging can preserve early continuation play when later models almost never take an action. Does not reconstruct deeper own-history support or establish optimal continuation values.'))
    print(json.dumps({r['trial']:{str(x['action']):{k:v['count'] for k,v in x['thresholds'].items()} for x in r['summary']} for r in rows}),flush=True)


if __name__=='__main__':main()
