"""Scalar readback of stratified sources, weighted targets and saved training state.

Reconstructs targets from native cashflows/conditional action values without
calling weighted ingestion, training update, matrix.evaluate or regret.step.
Sampling and reservoir implementations are replayed, not independently replaced.
No GPU or parameter refitting; this is not playing-strength evidence.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import argparse
import hashlib
import json
import math
from pathlib import Path
import time
import numpy as np
import psutil
from later_average_support_v1 import OUT,read,load_complete_cache
from sampled_physical_root_evaluation_v1 import sha,save,hand_class
from class_stratified_physical_deals_v1 import ClassStratifiedDeals
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir
from sampled_visible_initialization_v1 import features
from weighted_preflop_table_v1 import Table
from sampled_visible_hybrid_checkpoint_v1 import read_object
from weighted_training_checkpoint_v1 import restore_checkpoint
from reboot_research_idle_v1 import idle


def target_digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


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



def review(arm_name,completed,*,publish=False):
    started=time.monotonic();last=0.
    def guard():
        nonlocal last
        assert time.monotonic()-started<43200
        if time.monotonic()-last>3:
            listening=any(c.status==psutil.CONN_LISTEN and c.laddr.port==56708 for c in psutil.net_connections(kind='tcp'))
            assert not listening or idle()
            assert psutil.virtual_memory().available>20_000_000_000
            last=time.monotonic()
    guard()
    rp=OUT/'weighted-stratified-study-v1-registration.json';reg=read(rp)
    arm=next(a for a in reg['arms'] if a['name']==arm_name)
    cfg=arm['config'];store=Path(reg['store'])/arm_name;objects=store/'objects'
    progress=read(store/'progress.json')
    assert type(completed) is int and 1<=completed<=progress['completed']<=78
    folders=[]
    for i in range(1,completed+1):
        candidates=[p for p in store.glob(f'iteration-{i:04d}-*') if (p/'metrics.json').is_file()]
        assert len(candidates)==1,'Ambiguous complete iteration; explicit retry routing required'
        folders.append(candidates[0])
    cp=OUT/'bb-context-candidate.json';source=cp.read_text();context=json.loads(source)
    matrixpath=OUT/'preflop-allin-matrix-control-v1-matrix.json';matrix=read(matrixpath)
    mass=np.asarray(matrix['class_mass']);btnmass=mass.sum(axis=0);class_mass=mass.sum(axis=1)/mass.sum()
    catalogpath=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json');catalog=catalogpath.read_text()
    args=dict(context_source=source,catalog_source=catalog,matrix_sha256=sha(matrixpath),entry_mass=btnmass)
    inputs=dict(reg['inputs']);inputs[str(rp)]=sha(rp)
    for p in [*Path(__file__).parent.glob('*.py'),cp,matrixpath,catalogpath]:inputs[str(p)]=sha(p)
    for folder in folders:
        for p in folder.rglob('*'):
            if p.is_file():inputs[str(p)]=sha(p)
    # Models/checkpoint payloads are immutable hash-addressed objects and checked by their readers.
    for p,h in inputs.items():guard();assert sha(p)==h,p
    prefix=f'weighted-training-readback-v1-{arm_name}-{completed:04d}'
    reviewrp=OUT/f'{prefix}-registration.json'
    if publish:save(reviewrp,dict(inputs=inputs,arm=arm_name,completed=completed,folders=[str(p) for p in folders],
        maximum_seconds=43200,policy_tolerance=1e-10,target_tolerance=1e-9,root_tolerance=1e-8,
        gpu_used=False,refit_performed=False,production_modified=False))
    response_hi=context['nodes'][0]['children'][3]+1
    sampler=ClassStratifiedDeals(source,seed=cfg['sampler_seed'])
    action=np.random.Generator(np.random.PCG64(cfg['action_seed']))
    reservoirs=[WeightedPhysicalReservoir(cfg['reservoir_capacity'],p,cfg['reservoir_seeds'][p],source) for p in (0,1)]
    cache=load_complete_cache()
    regrets=np.zeros((169,2));reach=np.zeros(169)
    root_sums=np.zeros((169,4));root_counts=np.zeros(169,dtype=np.int64);root_mass=np.zeros(169)
    maximum_root_state=maximum_target=maximum_policy=0.;counts=[0,0];roots_checked=postflop_checked=0
    previous_next=None
    try:
        for iteration in range(1,completed+1):
            folder=folders[iteration-1];metrics=read(folder/'metrics.json')
            assert iteration==metrics['iteration']
            if previous_next is not None:assert metrics['used_model']==previous_next
            for record in metrics['subbatches']:
                for name,digest in record['artifacts'].items():assert sha(folder/f"batch-{record['chunk']:02d}"/name)==digest
            model=json.loads(read_object(objects,metrics['used_model']))
            assert model['generation']==iteration-1 and model['format']==1
            assert model['policy_type']=='class-stratified-weighted-physical-poker-v1'
            assert model['root_state']['sample_counts']==root_counts.tolist()
            assert np.max(abs(np.asarray(model['root_state']['regret_sums'])-root_sums))<1e-8
            assert np.max(abs(np.asarray(model['exact_btn_state']['regret_sums'])-regrets))<1e-10
            frozen=read(folder/'current-initial-policy.json')
            assert frozen['used_model']==metrics['used_model']
            root=np.asarray(frozen['root']);calls=np.asarray(frozen['calls'])
            catalog_doc=json.loads(catalog)
            catalog_query=dict(context_source=source,observations=[r['observation'] for r in catalog_doc['native_observations']])
            _,catalog_p,_=base_predict(catalog_query,model,'cpu')
            for item,prob in zip(catalog_doc['native_observations'],catalog_p):
                h=item['hand_class']
                if item['player']==0:
                    if root_counts[h]>0:
                        positive=np.maximum(root_sums[h],0.)
                        prob[:]=positive/positive.sum() if positive.sum()>0 else np.eye(4)[np.argmax(root_sums[h])]
                    assert np.max(abs(prob-root[h]))<1e-10
                else:
                    if reach[h]>0:
                        positive=np.maximum(regrets[h],0.)
                        prob[:2]=positive/positive.sum() if positive.sum()>0 else np.eye(2)[np.argmax(regrets[h])]
                    assert abs(prob[1]-calls[h])<1e-10
            expected_jam=np.array([math.fsum(m*(1-c)*matrix['bb_uncontested']+b*c for m,b,c in
                zip(matrix['class_mass'][h],matrix['bb_showdown_entries'][h],calls))/math.fsum(matrix['class_mass'][h]) for h in range(169)])
            sample=read(folder/'source-generation.json')
            assert sample==sampler.sample(cfg['deals_per_generation'])
            assert np.max(abs(np.asarray(sample['class_mass'])-class_mass))<1e-12
            allocation=np.bincount(sample['hand_classes'],minlength=169)
            assert allocation.tolist()==sample['class_counts'] and np.min(allocation)>=3
            source_weights=[cfg['deals_per_generation']*class_mass[c]/allocation[c] for c in sample['hand_classes']]
            assert np.max(abs(np.asarray(source_weights)-sample['deal_weights']))<1e-12
            for chunk in range(cfg['deals_per_generation']//cfg['deals_per_subbatch']):
                guard();part=folder/f'batch-{chunk:02d}'
                batch,queries,policies,updates,audit=[read(part/f'{name}.json') for name in
                    ('batch','queries','policies','updates','derived-targets')]
                integrated,profiles,full=[read(part/f'{name}.json') for name in
                    ('integrated-targets','integrated-profiles','integrated-native')]
                assert integrated['method']=='action-integrated-bb-root-targets-v1'
                assert integrated['identity']['root_estimator']==integrated['method']
                assert integrated['iteration']==iteration
                assert profiles['format']==1 and full['format']==2
                assert profiles['context_source']==source and profiles['batch_source']==queries['batch_source']==policies['batch_source']
                names=['baseline',*[f'action-{a}' for a in range(4)]]
                assert [p['name'] for p in profiles['profiles']]==[p['name'] for p in full['profiles']]==names
                assert profiles['profiles'][0]['policies']==policies['policies']
                assert full['maximum_forward_cashflow_error']<1e-10 and full['maximum_conservation_error']<1e-10
                assert full['terminal_estimator']=='conditional-preflop-allin-v1' and full['postflop_outcomes']=='sampled-board'
                for a in range(4):
                    for oi,(old,new) in enumerate(zip(policies['policies'],profiles['profiles'][a+1]['policies'])):
                        o=queries['observations'][oi]
                        expected=old if o['phase']!=0 or o['hi']!='1' else dict(old,probabilities=[float(k==a) for k in range(4)])
                        assert new==expected
                    assert len(profiles['profiles'][a+1]['policies'])==len(policies['policies'])
                for profile in full['profiles']:
                    assert len(profile['deals'])==cfg['deals_per_subbatch']
                    assert [d['deal_index'] for d in profile['deals']]==list(range(cfg['deals_per_subbatch']))
                start=chunk*cfg['deals_per_subbatch'];stop=start+cfg['deals_per_subbatch']
                assert batch['deals']==sample['deals'][start:stop]
                weights=sample['deal_weights'][start:stop]
                weighted=read(part/'weighted-targets.json')
                assert weighted['iteration']==iteration and weighted['method']=='source-deal-weighted-later-action-ingest-v1'
                binding=weighted['binding']
                assert binding['start']==start and binding['stop']==stop
                assert binding['source_sha256']==target_digest(sample) and binding['queries_sha256']==target_digest(queries)
                assert binding['deal_weights']==weights and binding['hand_classes']==sample['hand_classes'][start:stop]
                assert weighted['initial_audit_sha256']==target_digest(audit)
                assert batch['seed']==int(action.integers(0,2**63))
                cache.check_batch(batch)
                obs=queries['observations']
                _,p,_=base_predict(queries,model,'cpu')
                for i,o in enumerate(obs):
                    if o['actor']==0 and int(o['hi'])==1:
                        lo=int(o['lo']);h=hand_class([lo&63,(lo>>6)&63])
                        p[i]=root[h]
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
                    integrated_q=np.array([x['deals'][deal]['values'][0] for x in full['profiles'][1:]])
                    assert abs(integrated_q[0]-matrix['bb_fold'])<1e-12
                    assert abs(math.fsum(float(a*b) for a,b in zip(integrated_q,actual[qi]))-full['profiles'][0]['deals'][deal]['values'][0])<1e-9
                    integrated_q[3]=expected_jam[h]
                    integrated_expected=integrated_q-math.fsum(float(a*b) for a,b in zip(integrated_q,actual[qi]))
                    iw=integrated['bb_root_corrections'][deal]
                    assert (iw['query'],iw['hand_class'],iw['deal'])==(qi,h,deal)
                    maximum_target=max(maximum_target,float(np.max(abs(integrated_expected-iw['advantages']))),float(np.max(abs(integrated_q-iw['action_values']))))
                    assert maximum_target<1e-9
                    root_sums[h]+=integrated_expected*weights[deal];root_counts[h]+=1;root_mass[h]+=weights[deal]
                trace=read(part/'action-trace.json');later=read(part/'postflop-targets.json')
                assert trace['format']==2 and trace['method']=='all-node-action-trace-v2'
                assert json.loads(trace['policy_source'])==policies
                assert trace['context_source']==source and trace['batch_source']==queries['batch_source']
                assert trace['sampled_records']==updates['records'] and trace['sampled_roots']==updates['roots']
                assert len(trace['traces'])==cfg['deals_per_subbatch']
                positive_indices=[i for i,r in enumerate(updates['records']) if r[2]>0]
                assert [t['record'] for t in trace['conditional_targets']]==positive_indices
                by_record={t['record']:t for t in trace['conditional_targets']}
                nodes=[]
                for did,d in enumerate(trace['traces']):
                    assert d['deal_index']==did
                    assert d['values']==full['profiles'][0]['deals'][did]['values']
                    m={n['query']:n for n in d['nodes']};assert len(m)==len(d['nodes']);nodes.append(m)
                witnesses=[];weighted_witnesses=[];group=0
                for index,(qi,player,tag,v) in enumerate(updates['records']):
                    while group+1<len(heads) and index>=heads[group+1]:group+=1
                    if tag>0:
                        did,updater=divmod(group,2);assert updater==player
                        t=by_record[index]
                        assert (t['deal'],t['query'],t['updater'])==(did,qi,player)
                        node=nodes[did][qi]
                        assert node['actor']==player and node['n']==tag
                        q=node['action_values'];assert len(q)==4 and all(len(pair)==2 for pair in q)
                        expectation=[math.fsum(actual[qi,a]*q[a][seat] for a in range(tag)) for seat in (0,1)]
                        expected=np.array([q[a][player]-expectation[player] if a<tag else 0. for a in range(4)])
                        maximum_target=max(maximum_target,float(np.max(abs(expected-t['advantages']))),
                            max(abs(a-b) for a,b in zip(expectation,node['values'])))
                        assert maximum_target<1e-9
                        if obs[qi]['phase']>0:
                            assert obs[qi]['phase'] in (1,2,3)
                            values_by_record[index]=expected;witnesses.append(index);postflop_checked+=1
                        reservoirs[player].add(obs[qi],values_by_record.get(index,v),iteration,deal_weight=weights[did])
                        weighted_witnesses.append(dict(record=index,deal=did,source_deal=start+did,updater=player,weight=weights[did]))
                        counts[player]+=1
                assert later['method']=='postflop-conditional-action-targets-v1' and later['iteration']==iteration
                assert [w['record'] for w in later['postflop_replacements']]==witnesses
                for w in later['postflop_replacements']:
                    assert np.max(abs(values_by_record[w['record']]-w['advantages']))<1e-9
                assert weighted_witnesses==weighted['records']
                assert weighted['later_audit_sha256']==target_digest(later)
                for key,value in [('trace',trace),('queries',queries),('raw_updates',updates),('policies',policies),('initial_audit',audit)]:
                    assert later[key+'_sha256']==target_digest(value)
            for h in np.flatnonzero(btnmass>0):
                entry=math.fsum(r[h] for r in matrix['class_mass'])
                jam=math.fsum(r[h]*p[3] for r,p in zip(matrix['class_mass'],root))
                call=math.fsum(r[h]*p[3] for r,p in zip(matrix['btn_showdown_entries'],root))
                fold=jam*matrix['btn_fold'];mean=(1-calls[h])*fold+calls[h]*call
                regrets[h]+=(np.array([fold,call])-mean)/entry
                reach[h]+=jam/entry
            saved=restore_checkpoint(objects,metrics['checkpoint'],config=cfg,**args)
            assert saved['completed_iterations']==iteration
            assert saved['played_bank'][-1]==metrics['used_model']
            previous_next=metrics['next_model']
            assert saved['next_model']==previous_next
            assert np.array_equal(saved['root_regret_state'].counts,root_counts)
            assert np.max(abs(saved['root_regret_state'].masses-root_mass))<1e-9
            maximum_root_state=max(maximum_root_state,float(np.max(abs(saved['root_regret_state'].regrets-root_sums))))
            assert maximum_root_state<1e-8
            assert sampler.checkpoint()==saved['sampler'].checkpoint()
            assert action.bit_generator.state==saved['action_rng'].bit_generator.state
            assert np.max(abs(regrets-saved['exact_btn_state'].regrets))<1e-10
            assert np.max(abs(reach-saved['exact_btn_state'].reach))<1e-12
            for a,b in zip(reservoirs,saved['reservoirs']):
                assert a.summary()==b.summary() and a.rng.bit_generator.state==b.rng.bit_generator.state
                for name in ('keys','active','arity','iterations','deal_weights'):
                    assert np.array_equal(getattr(a,name),getattr(b,name))
                maximum_target=max(maximum_target,float(np.max(abs(a.values-b.values))))
                assert maximum_target<1e-9
            print(json.dumps(dict(reviewed_iteration=iteration,roots_checked=roots_checked)),flush=True)
        assert roots_checked==completed*cfg['deals_per_generation']
        for p,h in inputs.items():guard();assert sha(p)==h,p
        result=dict(passed=True,arm=arm_name,completed_updates=completed,complete_arm=completed==78,
            source_registration_sha256=sha(rp),final_checkpoint=metrics['checkpoint'],
            bb_roots_reconstructed=roots_checked,postflop_targets_reconstructed=postflop_checked,
            insertion_counts=counts,maximum_root_state_error=maximum_root_state,
            maximum_target_error=maximum_target,maximum_policy_error=maximum_policy,
            seconds=time.monotonic()-started,gpu_used=False,production_modified=False,
            accuracy_qualified=False,refit_performed=False,
            scope='Scalar targets, policies, weighting and full checkpoint state. Shared sampler/reservoir replay and native evaluator; not an independent poker engine or strength certificate.')
        if publish:
            result['readback_registration_sha256']=sha(reviewrp)
            save(OUT/f'{prefix}-result.json',result)
        print(json.dumps(result),flush=True)
        return result
    except BaseException as exc:
        if publish:save(OUT/f'{prefix}-result.json',dict(passed=False,error=repr(exc),readback_registration_sha256=sha(reviewrp)))
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--arm',required=True,choices=['9266201-stratified','9266301-stratified'])
    parser.add_argument('--generations',type=int,required=True)
    parser.add_argument('--publish',action='store_true')
    options=parser.parse_args()
    review(options.arm,options.generations,publish=options.publish)
