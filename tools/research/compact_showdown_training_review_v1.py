"""CPU-only scalar readback of compact baseline/corrected training prefixes.

Independent of training update, corrected target adapter, and regret accumulator.
Uses saved native values, independent showdown scoring, and deterministic streams.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import hashlib
import io
import json
import math
from pathlib import Path
import sys
import time
import numpy as np
import psutil
from later_average_support_v1 import OUT,read,load_complete_cache
from sampled_physical_root_evaluation_v1 import ROOT,sha,save,hand_class
from sampled_physical_deals_v1 import PhysicalDeals
from sampled_physical_reservoir_v1 import PhysicalReservoir
from sampled_visible_hybrid_checkpoint_v1 import read_object
from hu_later_action_training_review_20260925 import base_predict
from owned_research_archive_v1 import unpack
from showdown_control_reference_v1 import score
from reboot_research_idle_v1 import idle


def target_digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def main(label,completed):
    assert label in ('9266201-baseline','9266201-corrected','9266301-baseline','9266301-corrected')
    assert 0<completed<=78
    started=time.monotonic()
    def guard():
        assert time.monotonic()-started<14400 and idle()
        assert psutil.virtual_memory().available>20_000_000_000
    guard()
    rp=OUT/'showdown-matched-training-v1-registration.json';reg=read(rp)
    arm=next(a for a in reg['arms'] if a['name']==label)
    corrected=arm['treatment']=='corrected'
    coefficients=read(OUT/'showdown-root-control-coefficients-v1.json')
    prefix=f'showdown-training-readback-{label}-{completed:04d}'
    rr=OUT/f'{prefix}-registration.json';destination=OUT/f'{prefix}-result.json'
    assert not rr.exists() and not destination.exists()
    # Freeze only completed retention markers; never inspect an unfinished update.
    evidence={}
    for iteration in range(1,completed+1):
        marker=Path(reg['store'])/label/f'retention-{iteration:04d}.json'
        assert marker.is_file();evidence[str(marker)]=sha(marker)
    inputs=dict(reg['inputs']);inputs.update(evidence)
    for p in (rp,Path(__file__).resolve(),ROOT/'tools/research/owned_research_archive_v1.py'):
        inputs[str(p)]=sha(p)
    for p,h in inputs.items():guard();assert sha(p)==h,p
    save(rr,dict(inputs=inputs,arm=label,completed_iterations=completed,maximum_seconds=14400,
        gpu_used=False,production_modified=False,scope='Fixed completed prefix, not a complete-trial or strength claim.'))
    try:
        cfg=arm['config'];store=Path(reg['store'])/arm['name'];objects=store/'objects'
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
        root_sums=np.zeros((169,4));root_counts=np.zeros(169,dtype=np.int64);maximum_root_state=0.
        maximum_target=0.;maximum_policy=0.;counts=[0,0];roots_checked=0;postflop_checked=0
        for iteration in range(1,completed+1):
            folder=store/f'iteration-{iteration:04d}';metrics=read(folder/'metrics.json')
            retained=read(store/f'retention-{iteration:04d}.json')
            assert retained['iteration']==iteration and retained['metrics_sha256']==sha(folder/'metrics.json')
            model=json.loads(read_object(objects,metrics['used_model']))
            assert model['generation']==iteration-1 and model['format']==(8 if corrected else 7)
            if corrected:
                assert model['policy_type']=='visible-hybrid-postflop-showdown-controlled-root-v1'
                assert model['integrated_root']['state']['coefficients_sha256']==target_digest(coefficients)
            else:
                assert model['policy_type']=='visible-hybrid-exact-initial-postflop-action-integrated-v1'
                assert model['postflop_learning_targets']=='postflop-conditional-action-targets-v1'
            assert model['integrated_root']['state']['sample_counts']==root_counts.tolist()
            assert np.max(abs(np.asarray(model['integrated_root']['state']['regret_sums'])-root_sums))<1e-8
            assert np.max(abs(np.asarray(model['exact_model']['exact_btn']['state']['regret_sums'])-regrets))<1e-10
            frozen=read(folder/'current-initial-policy.json')
            root=np.asarray(frozen['root']);calls=np.asarray(frozen['calls'])
            catalog_doc=json.loads(catalog)
            catalog_query=dict(context_source=source,observations=[r['observation'] for r in catalog_doc['native_observations']])
            _,catalog_p,_=base_predict(catalog_query,model['exact_model']['base_model'],'cpu')
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
            for chunk in range(cfg['subbatches_per_iteration']):
                guard();archive=Path(retained['archives'][chunk]['path'])
                manifest=read(archive.with_suffix('.xz.json'))
                assert sha(archive.with_suffix('.xz.json'))==retained['archives'][chunk]['manifest_sha256']
                payload=unpack(archive,manifest,guard=guard)
                read_part=lambda name:json.loads(payload[name])
                names=metrics['subbatches'][chunk]['artifacts']
                for key,expected_hash in names.items():
                    filename={'showdown_input':'showdown-input','showdown_output':'showdown-output','showdown_targets':'showdown-targets'}.get(key,key)+'.json'
                    assert hashlib.sha256(payload[filename]).hexdigest()==expected_hash,filename
                batch,queries,policies,updates,audit=[read_part(f'{name}.json') for name in
                    ('batch','queries','policies','updates','derived-targets')]
                integrated,profiles,full=[read_part(f'{name}.json') for name in
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
                assert batch['deals']==sampler.sample(cfg['deals_per_subbatch'])['deals']
                assert batch['seed']==int(action.integers(0,2**63))
                cache.check_batch(batch)
                obs=queries['observations']
                _,p,_=base_predict(queries,model['exact_model']['base_model'],'cpu')
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
                    if corrected:
                        record=batch['allin_counts'][deal]
                        share=score(batch['deals'][deal])/2
                        x=share-(record['wins']+.5*record['ties'])/record['boards']
                        controlled_q=integrated_q.copy()
                        controlled_q[1:3]-=np.asarray(coefficients['call_raise_coefficients'][h])*x
                        integrated_expected=controlled_q-math.fsum(float(a*b) for a,b in zip(controlled_q,actual[qi]))
                        controlled=read_part('showdown-targets.json')
                        assert controlled['identity']['control_coefficients_sha256']==target_digest(coefficients)
                        assert controlled['source_integrated_audit_sha256']==target_digest(integrated)
                        cw=controlled['bb_root_corrections'][deal]
                        maximum_target=max(maximum_target,float(np.max(abs(controlled_q-cw['action_values']))),float(np.max(abs(integrated_expected-cw['advantages']))))
                        assert maximum_target<1e-9
                    root_sums[h]+=integrated_expected;root_counts[h]+=1
                trace=read_part('action-trace.json');later=read_part('postflop-targets.json')
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
                witnesses=[];group=0
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
                        reservoirs[player].add(obs[qi],values_by_record.get(index,v),iteration)
                        counts[player]+=1
                assert later['method']=='postflop-conditional-action-targets-v1' and later['iteration']==iteration
                assert [w['record'] for w in later['postflop_replacements']]==witnesses
                for w in later['postflop_replacements']:
                    assert np.max(abs(values_by_record[w['record']]-w['advantages']))<1e-9
                for key,value in [('trace',trace),('queries',queries),('raw_updates',updates),('policies',policies),('initial_audit',audit)]:
                    assert later[key+'_sha256']==target_digest(value)
            for h in np.flatnonzero(btnmass>0):
                entry=math.fsum(r[h] for r in matrix['class_mass'])
                jam=math.fsum(r[h]*p[3] for r,p in zip(matrix['class_mass'],root))
                call=math.fsum(r[h]*p[3] for r,p in zip(matrix['btn_showdown_entries'],root))
                fold=jam*matrix['btn_fold'];mean=(1-calls[h])*fold+calls[h]*call
                regrets[h]+=(np.array([fold,call])-mean)/entry
                reach[h]+=jam/entry
            next_model=json.loads(read_object(objects,metrics['next_model']))
            assert next_model['generation']==iteration
            saved_root=next_model['integrated_root']['state'];saved_exact=next_model['exact_model']['exact_btn']['state']
            assert saved_root['sample_counts']==root_counts.tolist()
            maximum_root_state=max(maximum_root_state,float(np.max(abs(np.asarray(saved_root['regret_sums'])-root_sums))))
            assert maximum_root_state<1e-8
            assert np.max(abs(np.asarray(saved_exact['regret_sums'])-regrets))<1e-10
            assert np.max(abs(np.asarray(saved_exact['conditional_reach_sums'])-reach))<1e-12
            if metrics['checkpoint'] is not None:
                snap=read(store/f'checkpoint-{iteration:04d}.json')
                assert snap['checkpoint']==metrics['checkpoint'] and snap['completed_iterations']==iteration
                ref=metrics['checkpoint']
                while True:
                    document=json.loads(read_object(objects,ref))
                    if document.get('format')==3 and 'reservoirs' in document:break
                    key=next(k for k in ('action_integrated_checkpoint','exact_checkpoint','base_checkpoint') if k in document)
                    ref=document[key]
                assert document['completed_iterations']==iteration and document['config']==cfg
                assert document['sampler']==sampler.checkpoint()
                assert document['action_rng']==action.bit_generator.state
                pointer=snap['reservoir_archive'];archive=Path(pointer['path']);mp=archive.with_suffix('.xz.json')
                assert sha(mp)==pointer['manifest_sha256']
                saved_reservoirs=unpack(archive,read(mp),guard=guard)
                for a,ref in zip(reservoirs,document['reservoirs']):
                    raw=saved_reservoirs[ref['file']];assert hashlib.sha256(raw).hexdigest()==ref['sha256']
                    with np.load(io.BytesIO(raw),allow_pickle=False) as data:
                        meta=json.loads(str(data['metadata']))
                        assert meta['player']==a.player and meta['capacity']==a.capacity and meta['seen']==a.seen
                        assert meta['context_sha256']==a.context_sha256 and meta['rng']==a.rng.bit_generator.state
                        for name in ('keys','active','arity','iterations'):
                            assert np.array_equal(getattr(a,name)[:a.size],data[name])
                        maximum_target=max(maximum_target,float(np.max(abs(a.values[:a.size]-data['values']))))
                        assert maximum_target<1e-9
            print(json.dumps(dict(reviewed_iteration=iteration,roots_checked=roots_checked)),flush=True)
        assert roots_checked==cfg['max_iterations']*cfg['subbatches_per_iteration']*cfg['deals_per_subbatch']
        assert roots_checked==completed*cfg['subbatches_per_iteration']*cfg['deals_per_subbatch']
        for p,h in inputs.items():guard();assert sha(p)==h,p
        save(destination,dict(passed=True,arm=label,completed_updates=completed,
            source_registration_sha256=sha(rp),readback_registration_sha256=sha(rr),
            bb_roots_reconstructed=roots_checked,postflop_targets_reconstructed=postflop_checked,
            insertion_counts=counts,maximum_root_state_error=maximum_root_state,
            maximum_target_error=maximum_target,maximum_policy_error=maximum_policy,
            complete_arm=completed==78,accuracy_qualified=False,gpu_used=False,
            seconds=time.monotonic()-started,production_modified=False,
            scope='Scalar policy, chance/action streams, targets, root/exact state and checkpointed reservoir reconstruction. No refit or strength conclusion.'))
    except BaseException as exc:
        save(destination,dict(passed=False,error=repr(exc),readback_registration_sha256=sha(rr),
            seconds=time.monotonic()-started,gpu_used=False,production_modified=False))
        raise


if __name__=='__main__':
    assert len(sys.argv)==3;main(sys.argv[1],int(sys.argv[2]))
