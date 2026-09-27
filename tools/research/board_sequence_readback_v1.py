"""General board-training sequence auditor, adapted from the bounded readback.

Only saved complete generation sequences are accepted. No fitting or training
updates. The caller binds artifacts, supplies resource guards and publishes.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import math
from pathlib import Path
import time
import numpy as np
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from sampled_visible_hybrid_checkpoint_v1 import read_object
from weighted_training_readback_parallel_v1 import initialize_batch_worker, verify_batch
from board_training_readback_support_v1 import prepare_readback, check_draw
from board_training_checkpoint_v1 import restore_checkpoint, POLICY_TYPE
from board_root_accumulator_v1 import digest
from board_root_components_v1 import exact_terms
from preflop_allin_matrix_v1 import AllinMatrix
from class_stratified_physical_deals_v1 import ClassStratifiedDeals
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir
from bounded_parallel_evaluation_archive_v2 import production_available

def audit_sequence(*, objects, cfg, initial_checkpoint, final_checkpoint, generations, workers, guard):
    assert type(workers) is int and 1<=workers<=8
    assert 1<=len(generations)<=78
    assert len({str(Path(g['path']).resolve()) for g in generations})==len(generations)
    objects=Path(objects)
    cp=OUT/'bb-context-candidate.json'; mp=OUT/'preflop-allin-matrix-control-v1-matrix.json'
    cat=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    physical=Path('S:/GTOpen-research/board-root-components-control-v1/preflop-catalog.json')
    source=cp.read_text(); context=json.loads(source); matrix=read(mp)
    mass=np.asarray(matrix['class_mass']); btnmass=mass.sum(0); classmass=mass.sum(1)
    root_config=cfg['board_root']; assert np.array_equal(root_config['entry_mass'],classmass)
    args=dict(context_source=source,catalog_source=cat.read_text(),matrix_sha256=sha(mp),
        entry_mass=btnmass,root_config=root_config)
    sampler=ClassStratifiedDeals(source,seed=cfg['sampler_seed'])
    action=np.random.Generator(np.random.PCG64(cfg['action_seed']))
    reservoirs=[WeightedPhysicalReservoir(cfg['reservoir_capacity'],p,cfg['reservoir_seeds'][p],source) for p in (0,1)]
    root_sums=np.zeros((169,4)); regrets=np.zeros((169,2)); reach=np.zeros(169)
    counts=[0,0]; roots_checked=postflop_checked=boards_checked=0
    maxroot=maxexact=maxpolicy=maxtarget=maxboard=0.; previous=None; history=[]; played=[]
    initial=restore_checkpoint(objects,initial_checkpoint,cfg,**args)
    assert initial['completed_iterations']==0 and initial['played_bank']==[]
    assert not np.any(initial['root_regret_state'].regrets) and not np.any(initial['exact_btn_state'].regrets)
    assert sampler.checkpoint()==initial['sampler'].checkpoint()
    assert action.bit_generator.state==initial['action_rng'].bit_generator.state
    previous=initial['next_model']
    for iteration,item in enumerate(generations,1):
        metric_path=Path(item['path']); assert sha(metric_path)==item['sha256']
        folder=metric_path.parent
        guard(); metric=read(metric_path); assert metric['iteration']==iteration
        assert sorted(b['chunk'] for b in metric['subbatches'])==list(range(cfg['deals_per_generation']//cfg['deals_per_subbatch']))
        assert metric['used_model']==previous
        for batch in metric['subbatches']:
            for name,h in batch['artifacts'].items(): assert sha(folder/f"batch-{batch['chunk']:02d}"/name)==h
        model_source=read_object(objects,metric['used_model']).decode(); model=json.loads(model_source)
        assert model['policy_type']==POLICY_TYPE and model['generation']==iteration-1
        assert np.max(abs(root_sums-model['board_root_state']['regret_sums']))<1e-8
        assert np.max(abs(regrets-model['exact_btn_state']['regret_sums']))<1e-10
        assert np.max(abs(reach-model['exact_btn_state']['conditional_reach_sums']))<1e-12
        payload=dict(model_source=model_source,context_source=source,catalog_source=cat.read_text(),
            physical_catalog_source=physical.read_text(),matrix_source=mp.read_text(),root_config=root_config)
        prepared=prepare_readback(payload); frozen=read(folder/'current-initial-policy.json')
        root=np.asarray(frozen['root']); calls=np.asarray(frozen['calls'])
        assert frozen['used_model']==metric['used_model']
        assert np.max(abs(root-prepared['pre'][0]))<1e-10
        supported=btnmass>0
        assert np.max(abs(calls[supported]-prepared['pre'][12][supported,1]))<1e-10
        plan=read(folder/'board-plan.json'); evidence=read(folder/'board-generation-evidence.json')
        rng=np.random.Generator(np.random.PCG64(np.random.SeedSequence([root_config['board_seed'],iteration-1])))
        boards=[]
        for _ in range(root_config['boards_per_generation']):
            b=rng.choice(52,size=5,replace=False).tolist(); b[:3]=sorted(b[:3]); boards.append(b)
        assert plan['boards']==boards and plan['generation']==iteration-1
        assert plan['parent_state_sha256']==model['board_root_state']['state_sha256']
        assert plan['config_sha256']==digest(root_config)
        assert evidence['plan_sha256']==digest(plan) and evidence['generation']==iteration-1
        assert evidence['context_sha256']==sha(cp) and evidence['matrix_sha256']==sha(mp)
        assert evidence['model_sha256']==hashlib.sha256(model_source.encode()).hexdigest()
        assert evidence['played_policy_sha256']==digest(prepared['pre'][0].tolist())
        # Vector arithmetic is used only to verify the provider's byte seal.
        # Scalar exact terms above supply the separate numerical check.
        exact_identity=exact_terms(AllinMatrix(matrix,source),prepared['pre'])
        maxexact=max(maxexact,float(np.max(abs(exact_identity-prepared['exact_scalar'])))); assert maxexact<1e-10
        assert evidence['exact_terms_sha256']==digest(exact_identity.tolist())
        recipe=dict(method='typed-board-model-widened-f32-network-f64-inference-v1',
            model_sha256=evidence['model_sha256'],context_sha256=sha(cp),catalog_sha256=sha(cat),
            physical_catalog_sha256=sha(physical),matrix_sha256=sha(mp),
            provider_sha256=sha(Path(__file__).with_name('board_training_targets_v1.py')))
        assert len(evidence['draws'])==len(boards)==len(metric['board_results'])
        sample=read(folder/'source-generation.json'); assert sample==sampler.sample(cfg['deals_per_generation'])
        allocation=np.bincount(sample['hand_classes'],minlength=169)
        assert allocation.tolist()==sample['class_counts'] and np.min(allocation)>=3
        weights=[cfg['deals_per_generation']*classmass[c]/allocation[c] for c in sample['hand_classes']]
        assert np.max(abs(np.asarray(weights)-sample['deal_weights']))<1e-12
        chunks=cfg['deals_per_generation']//cfg['deals_per_subbatch']
        seeds=[int(action.integers(0,2**63)) for _ in range(chunks)]
        expected_jam=np.array([math.fsum(m*(1-c)*matrix['bb_uncontested']+b*c for m,b,c in
            zip(matrix['class_mass'][h],matrix['bb_showdown_entries'][h],calls))/math.fsum(matrix['class_mass'][h]) for h in range(169)])
        state=dict(folder=folder,cfg=cfg,source=source,model=model,root=root,calls=calls,regrets=regrets,
            reach=reach,response_hi=context['nodes'][0]['children'][3]+1,matrix=matrix,expected_jam=expected_jam,
            sample=sample,expected_seeds=seeds,iteration=iteration)
        # CPU tasks overlap; a maximum of workers + min(workers,4) children.
        with ProcessPoolExecutor(max_workers=min(4,workers)) as bp, ProcessPoolExecutor(max_workers=workers,
                initializer=initialize_batch_worker,initargs=(state,)) as tp:
            futures=[]
            for i,(board,record,artifact) in enumerate(zip(boards,evidence['draws'],metric['board_results'])):
                rp_draw=folder/'board-targets'/f'board-{i:03d}'/'result.json'
                request=rp_draw.with_name('request.json'); actual=read(rp_draw)
                assert Path(artifact['path']).resolve()==rp_draw.resolve() and sha(rp_draw)==artifact['sha256']
                assert artifact['result']==actual and actual['record']==record
                assert actual['request_sha256']==sha(request)
                assert record['draw_index']==i and record['board']==board
                assert record['policy_recipe_sha256']==digest(recipe)
                futures.append(bp.submit(check_draw,payload,request,record))
            for checked in tp.map(verify_batch,range(chunks)):
                guard()
                for o,v,it,w in checked['events']: reservoirs[o['actor']].add(o,v,it,deal_weight=w)
                counts=[a+b for a,b in zip(counts,checked['counts'])]
                roots_checked+=checked['roots_checked']; postflop_checked+=checked['postflop_checked']
                maxpolicy=max(maxpolicy,checked['maximum_policy']); maxtarget=max(maxtarget,checked['maximum_target'])
                # Sampled root_events are audited but deliberately NOT applied.
            checked_boards=[f.result(timeout=180) for f in futures]
        for b in checked_boards: maxboard=max(maxboard,b['maximum_error']); boards_checked+=1
        delta=np.zeros((169,4))
        for c in range(169):
            q=[float(prepared['exact_scalar'][c,a])+math.fsum(x['values'][c][a] for x in checked_boards)/len(boards) for a in range(4)]
            baseline=math.fsum(float(p*v) for p,v in zip(root[c],q))
            for a in range(4): delta[c,a]=cfg['deals_per_generation']*classmass[c]*(q[a]-baseline)
        root_sums+=delta
        for h in np.flatnonzero(btnmass>0):
            entry=math.fsum(r[h] for r in matrix['class_mass'])
            jam=math.fsum(r[h]*p[3] for r,p in zip(matrix['class_mass'],root))
            call=math.fsum(r[h]*p[3] for r,p in zip(matrix['btn_showdown_entries'],root))
            fold=jam*matrix['btn_fold']; mean=(1-calls[h])*fold+calls[h]*call
            regrets[h]+=(np.array([fold,call])-mean)/entry; reach[h]+=jam/entry
        saved=restore_checkpoint(objects,metric['checkpoint'],cfg,**args)
        played.append(metric['used_model']); assert saved['played_bank']==played
        assert saved['completed_iterations']==iteration and saved['next_model']==metric['next_model']
        previous=metric['next_model']; assert sampler.checkpoint()==saved['sampler'].checkpoint()
        assert action.bit_generator.state==saved['action_rng'].bit_generator.state
        maxroot=max(maxroot,float(np.max(abs(root_sums-saved['root_regret_state'].regrets)))); assert maxroot<1e-8
        assert np.max(abs(regrets-saved['exact_btn_state'].regrets))<1e-10
        assert np.max(abs(reach-saved['exact_btn_state'].reach))<1e-12
        q_identity=exact_identity+np.mean([d['values'] for d in evidence['draws']],axis=0)
        d_identity=(cfg['deals_per_generation']*classmass)[:,None]*(q_identity-np.sum(prepared['pre'][0]*q_identity,axis=1)[:,None])
        history.append(dict(generation=iteration-1,plan_sha256=digest(plan),evidence_sha256=digest(evidence),
            model_sha256=evidence['model_sha256'],played_policy_sha256=evidence['played_policy_sha256'],
            exact_terms_sha256=evidence['exact_terms_sha256'],delta_sha256=digest(d_identity.tolist())))
        assert saved['root_regret_state'].history==history
        assert metric['board_draws']==iteration*len(boards)
        for a,b in zip(reservoirs,saved['reservoirs']):
            assert a.summary()==b.summary() and a.rng.bit_generator.state==b.rng.bit_generator.state
            for name in ('keys','active','arity','iterations','deal_weights'): assert np.array_equal(getattr(a,name),getattr(b,name))
            maxtarget=max(maxtarget,float(np.max(abs(a.values-b.values)))); assert maxtarget<1e-9
        print(json.dumps(dict(reviewed_generation=iteration,boards_checked=boards_checked,
            physical_roots_checked=roots_checked,postflop_targets_checked=postflop_checked)),flush=True)
    assert metric['checkpoint']==final_checkpoint
    assert roots_checked==len(generations)*cfg['deals_per_generation']
    assert boards_checked==len(generations)*root_config['boards_per_generation']
    return dict(generations=len(generations),boards_checked=boards_checked,physical_roots_checked=roots_checked,
        postflop_targets_checked=postflop_checked,insertion_counts=counts,
        maximum_root_state_error=maxroot,maximum_exact_error=maxexact,maximum_board_error=maxboard,
        maximum_target_error=maxtarget,maximum_policy_error=maxpolicy,final_checkpoint=metric['checkpoint'])
