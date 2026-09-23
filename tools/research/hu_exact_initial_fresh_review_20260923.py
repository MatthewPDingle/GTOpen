"""Independent file readback of the complete exact-initial fresh training trial.

Does not call the new training update, derived-target ingestion, matrix evaluate
or exact accumulator update. No GPU, fitting, new chance samples or live changes.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import hashlib
import json
import sys
import math
import time
from pathlib import Path
import numpy as np
import psutil
from later_average_support_v1 import OUT, read, load_complete_cache
from sampled_physical_root_evaluation_v1 import ROOT, sha, save, hand_class
from sampled_physical_deals_v1 import PhysicalDeals
from sampled_physical_reservoir_v1 import PhysicalReservoir
from sampled_visible_initialization_v1 import features
from sampled_physical_preflop_table_v1 import Table
from sampled_visible_hybrid_checkpoint_v1 import read_object
from exact_initial_hybrid_checkpoint_v1 import restore_checkpoint
from reboot_research_idle_v1 import idle

PREFIX = 'exact-initial-fresh-pilot-v1'


def base_predict(queries, model, device):
    assert device == 'cpu'
    obs=queries['observations'];x=features(obs).astype(np.float64)
    actors=np.array([o['actor'] for o in obs]);scores=np.zeros((len(obs),4))
    for player,net in enumerate(model['networks']):
        ids=np.flatnonzero(actors==player);y=x[ids]
        for layer,shape in enumerate(((64,302),(64,64),(4,64))):
            w=np.asarray(net[f'w{layer}'],dtype=np.float32).astype(float).reshape(shape)
            b=np.asarray(net[f'b{layer}'],dtype=np.float32).astype(float)
            y=y@w.T+b
            if layer<2:y=np.maximum(y,0.)
        scores[ids]=y
    legal=np.arange(4)[None,:]<np.array([o['n'] for o in obs])[:,None]
    p=np.maximum(scores,0.)*legal;total=p.sum(1);live=total>0
    p[live]/=total[live,None]
    rows=np.flatnonzero(~live);p[rows,np.argmax(np.where(legal,scores,-np.inf),axis=1)[rows]]=1.
    for table in model['preflop_tables']:
        if table is not None:p,_=Table(table,queries['context_source']).apply(obs,p)
    return scores,p,None


def main():
    started=time.monotonic()
    def guard():
        assert time.monotonic()-started<7200 and idle()
        assert psutil.virtual_memory().available>20_000_000_000
    guard()
    import torch
    torch.set_num_threads(1)
    assert not torch.cuda.is_available()
    rp,pp=[OUT/f'{PREFIX}-{s}.json' for s in ('registration','result')]
    reg,result=read(rp),read(pp)
    assert result['passed'] and result['registration_sha256']==sha(rp)
    inputs={**reg['inputs'],**result['artifacts'],str(rp):sha(rp),str(pp):sha(pp),str(Path(__file__)):sha(Path(__file__))}
    for name in ('sampled_visible_initialization_v1.py','sampled_physical_preflop_table_v1.py','sampled_visible_hybrid_checkpoint_v1.py',
                 'sampled_physical_reservoir_v1.py','sampled_physical_deals_v1.py',
                 'exact_initial_hybrid_checkpoint_v1.py','later_average_support_v1.py'):
        p=ROOT/'tools/research'/name;inputs[str(p)]=sha(p)
    for p,h in inputs.items():assert sha(p)==h,p
    reviewrp=OUT/f'{PREFIX}-readback-registration.json'
    assert not reviewrp.exists()
    save(reviewrp,dict(inputs=inputs,maximum_seconds=7200,gpu_used=False,
        scope='Independent scalar targets, native policy and full reservoir/chance replay. No refit, no new independent test set and no strength conclusion.',production_modified=False))
    try:
        cfg=result['config'];store=Path(reg['store']);objects=store/'objects'
        assert result['terminal'] and result['completed_iterations']==cfg['max_iterations']
        assert all(cfg[k]==v for k,v in reg['config'].items())
        cp=OUT/'bb-context-candidate.json';source=cp.read_text();context=json.loads(source)
        matrixpath=OUT/'preflop-allin-matrix-control-v1-matrix.json';matrix=read(matrixpath)
        mass=np.asarray(matrix['class_mass']);btnmass=np.sum(mass,axis=0)
        catalogpath=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
        catalog=catalogpath.read_text()
        args=dict(context_source=source,catalog_source=catalog,matrix_sha256=sha(matrixpath),entry_mass=btnmass)
        response_hi=context['nodes'][0]['children'][3]+1
        sampler=PhysicalDeals(source,mode='full_deck',seed=cfg['sampler_seed'])
        action=np.random.Generator(np.random.PCG64(cfg['action_seed']))
        reservoirs=[PhysicalReservoir(cfg['reservoir_capacity'],p,cfg['reservoir_seeds'][p],source) for p in (0,1)]
        cache=load_complete_cache()
        regrets=np.zeros((169,2));reach=np.zeros(169)
        maximum_target=0.;maximum_policy=0.;counts=[0,0];roots_checked=0
        for iteration in range(1,cfg['max_iterations']+1):
            folder=store/f'iteration-{iteration:04d}';metrics=read(folder/'metrics.json')
            model=json.loads(read_object(objects,metrics['used_model']))
            assert model['generation']==iteration-1
            assert np.max(abs(np.asarray(model['exact_btn']['state']['regret_sums'])-regrets))<1e-10
            frozen=read(folder/'current-initial-policy.json')
            root=np.asarray(frozen['root']);calls=np.asarray(frozen['calls'])
            catalog_doc=json.loads(catalog)
            catalog_query=dict(context_source=source,observations=[r['observation'] for r in catalog_doc['native_observations']])
            _,catalog_p,_=base_predict(catalog_query,model['base_model'],'cpu')
            for item,prob in zip(catalog_doc['native_observations'],catalog_p):
                h=item['hand_class']
                if item['player']==0:
                    assert np.max(abs(prob-root[h]))<1e-10
                else:
                    if reach[h]>0:
                        positive=np.maximum(regrets[h],0.)
                        prob[:2]=positive/positive.sum() if positive.sum()>0 else np.eye(2)[np.argmax(regrets[h])]
                    assert abs(prob[1]-calls[h])<1e-10
            expected_jam=np.array([math.fsum(m*(1-c)*matrix['bb_uncontested']+b*c for m,b,c in
                zip(matrix['class_mass'][h],matrix['bb_showdown_entries'][h],calls))/math.fsum(matrix['class_mass'][h]) for h in range(169)])
            for chunk in range(cfg['subbatches_per_iteration']):
                guard();part=folder/f'batch-{chunk:02d}'
                batch,queries,policies,updates,audit=[read(part/f'{name}.json') for name in
                    ('batch','queries','policies','updates','derived-targets')]
                assert batch['deals']==sampler.sample(cfg['deals_per_subbatch'])['deals']
                assert batch['seed']==int(action.integers(0,2**63))
                cache.check_batch(batch)
                obs=queries['observations']
                _,p,_=base_predict(queries,model['base_model'],'cpu')
                for i,o in enumerate(obs):
                    if o['actor']==1 and int(o['hi'])==response_hi:
                        lo=int(o['lo']);h=hand_class([lo&63,(lo>>6)&63])
                        if reach[h]>0:
                            positive=np.maximum(regrets[h],0.)
                            expected=positive/positive.sum() if positive.sum()>0 else np.eye(2)[np.argmax(regrets[h])]
                            p[i]=[*expected,0.,0.]
                actual=np.asarray([x['probabilities'] for x in policies['policies']])
                maximum_policy=max(maximum_policy,float(np.max(abs(p-actual))))
                assert maximum_policy<1e-10
                heads=[i for i,r in enumerate(updates['records']) if int(obs[r[0]]['hi'])==1 and obs[r[0]]['phase']==0]
                assert len(heads)==2*cfg['deals_per_subbatch'] and len(updates['roots'])==len(heads)
                values_by_record={}
                for k,(deal,player,value) in enumerate(updates['roots']):
                    assert (deal,player)==divmod(k,2)
                    if player!=0:continue
                    index=heads[k];qi,actor,tag,v=updates['records'][index]
                    assert actor==0 and tag==4
                    h=hand_class(batch['deals'][deal][:2])
                    assert abs(v[0]+value-matrix['bb_fold'])<1e-9
                    assert np.max(abs(actual[qi]-root[h]))<1e-12
                    q=np.asarray(v)+value;q[3]=expected_jam[h]
                    expected=q-math.fsum(float(a*b) for a,b in zip(q,actual[qi]))
                    values_by_record[index]=expected
                    w=audit['bb_root_corrections'][deal]
                    assert (w['record'],w['query'],w['hand_class'],w['deal'])==(index,qi,h,deal)
                    maximum_target=max(maximum_target,float(np.max(abs(expected-w['advantages']))))
                    assert maximum_target<1e-9
                    roots_checked+=1
                for index,(qi,player,tag,v) in enumerate(updates['records']):
                    if tag>0:
                        reservoirs[player].add(obs[qi],values_by_record.get(index,v),iteration)
                        counts[player]+=1
            for h in np.flatnonzero(btnmass>0):
                entry=math.fsum(r[h] for r in matrix['class_mass'])
                jam=math.fsum(r[h]*p[3] for r,p in zip(matrix['class_mass'],root))
                call=math.fsum(r[h]*p[3] for r,p in zip(matrix['btn_showdown_entries'],root))
                fold=jam*matrix['btn_fold'];mean=(1-calls[h])*fold+calls[h]*call
                regrets[h]+=(np.array([fold,call])-mean)/entry
                reach[h]+=jam/entry
            saved=restore_checkpoint(objects,metrics['checkpoint'],config=cfg,**args)
            assert saved['completed_iterations']==iteration
            assert sampler.checkpoint()==saved['sampler'].checkpoint()
            assert action.bit_generator.state==saved['action_rng'].bit_generator.state
            assert np.max(abs(regrets-saved['exact_btn_state'].regrets))<1e-10
            assert np.max(abs(reach-saved['exact_btn_state'].reach))<1e-12
            for a,b in zip(reservoirs,saved['reservoirs']):
                assert a.summary()==b.summary() and a.rng.bit_generator.state==b.rng.bit_generator.state
                for name in ('keys','active','arity','iterations'):
                    assert np.array_equal(getattr(a,name),getattr(b,name))
                maximum_target=max(maximum_target,float(np.max(abs(a.values-b.values))))
                assert maximum_target<1e-9
            print(json.dumps(dict(reviewed_iteration=iteration,roots_checked=roots_checked)),flush=True)
        assert roots_checked==cfg['max_iterations']*cfg['subbatches_per_iteration']*cfg['deals_per_subbatch']
        assert metrics['checkpoint']==result['final_checkpoint']
        for p,h in inputs.items():guard();assert sha(p)==h,p
        guard()
        review=dict(passed=True,source_registration_sha256=sha(rp),source_result_sha256=sha(pp),
            readback_registration_sha256=sha(reviewrp),completed_updates=cfg['max_iterations'],bb_roots_reconstructed=roots_checked,
            insertion_counts=counts,maximum_target_error=maximum_target,maximum_policy_error=maximum_policy,
            seconds=time.monotonic()-started,gpu_used=False,production_modified=False,
            accuracy_qualified=False,refit_performed=False,
            scope='Independent reconstruction of all complete-trial raw targets, policy overrides and checkpointed training state. Not strength evidence.')
        save(OUT/f'{PREFIX}-independent-review.json',review);print(json.dumps(review))
    except BaseException as exc:
        save(OUT/f'{PREFIX}-independent-review.json',dict(passed=False,error=repr(exc),
            readback_registration_sha256=sha(reviewrp),seconds=time.monotonic()-started,gpu_used=False,production_modified=False))
        raise


if __name__=='__main__':
    assert sys.argv[1:] in ([],['--control'])
    if sys.argv[1:]: PREFIX='exact-initial-fresh-control-v1'
    main()
