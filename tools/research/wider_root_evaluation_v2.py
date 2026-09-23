"""Fixed-count root response testing, including a previously frozen responder.

Injected bank and exact endpoints must be frozen and admitted by a controller.
This module cannot choose a checkpoint, extend a run, or deploy a candidate.
The controller supplies resource guards and retains every immutable artifact.
"""
import time
from pathlib import Path
import numpy as np
from sampled_physical_root_evaluation_v1 import sha,save
from sampled_player_stratified_response_deals_v2 import sample
from sampled_physical_deals_v1 import PhysicalDeals
from sampled_conditional_root_evaluation_v1 import batch_values
from exact_aware_root_response_v1 import fit,frozen_policy,admit_test_ids
from root_residual_evaluation_v1 import prepare,residuals,policy
from sampled_evaluation_intervals_v1 import Plan,PairedEvaluation
import json

SERIES=('trained-response','always-fold','always-call','always-raise','always-jam','previous-response')


def run(context_path,bank,cache,exact,config,folder,guard,*,prior_response_path):
    start=time.monotonic();guard();context_path=Path(context_path);folder=Path(folder)
    required={'id','train_seed','test_seed','per_class','test_deals','batch_size','minimum_training_deals','family_alpha'}
    if set(config)!=required:raise ValueError('An explicit complete evaluation config is required')
    if any(type(config[k]) is not int or config[k]<1 for k in ('train_seed','test_seed','per_class','test_deals','batch_size','minimum_training_deals')):
        raise ValueError('Positive integral counts and seeds required')
    if config['train_seed']==config['test_seed'] or config['per_class']%2 or config['test_deals']<2 or config['test_deals']%config['batch_size']:
        raise ValueError('Distinct streams, even class coverage and complete test batches required')
    if not isinstance(config['id'],str) or not config['id'] or not 0<config['family_alpha']<1:
        raise ValueError('Run identity and valid family error required')
    source=context_path.read_text();context=json.loads(source);context_hash=sha(context_path)
    if exact['context_sha256']!=context_hash:raise ValueError('Exact endpoint context mismatch')
    baseline=policy(exact['baseline']);mass=np.asarray(exact['masses'])
    fold=np.asarray(exact['fold_entries']);jam=np.asarray(exact['jam_entries'])
    prior_response_path=Path(prior_response_path)
    prior_bytes=prior_response_path.read_bytes()
    prior_response=json.loads(prior_bytes)
    prior=frozen_policy(prior_response,context_sha256=context_hash)
    prior_hash=sha(prior_response_path)
    folder.mkdir(exist_ok=False)
    (folder/'prior-response.json').write_bytes(prior_bytes)
    assert sha(folder/'prior-response.json')==prior_hash
    sampled=sample(source,player=0,seed=config['train_seed'],per_class=config['per_class'],classes=list(range(169)),guard=guard)
    save(folder/'training-deals.json',sampled)
    assert sampled['population_evaluation'] is False and sampled['conditioned_player']==0
    ids=[];classes=[];values=[];batches={};phase_timings={}
    before=time.monotonic()
    for offset in range(0,len(sampled['deals']),config['batch_size']):
        guard();name=f'train-{offset:06d}';deals=sampled['deals'][offset:offset+config['batch_size']]
        batch=dict(format=2,batch_id=f"{config['id']}-{name}",seed=0,query_limit=100000,deals=deals)
        summary=batch_values(context_path,batch,folder/name,guard,bank,cache)
        assert summary['classes']==sampled['hand_classes'][offset:offset+len(deals)]
        assert np.max(abs(np.asarray(summary['root_probabilities'])-baseline[summary['classes']]))<1e-10
        ids.extend(f"{batch['batch_id']}-{i}" for i in range(len(deals)))
        classes.extend(summary['classes']);values.extend(summary['action_values'])
        batches[name]=sha(folder/name/'summary.json')
    phase_timings['training_seconds']=time.monotonic()-before
    assert np.array_equal(np.bincount(classes,minlength=169),np.full(169,config['per_class']))
    response=fit(ids,classes,values,baseline,mass,fold,jam,context_sha256=context_hash,minimum_training_deals=config['minimum_training_deals'])
    rho=frozen_policy(response,context_sha256=context_hash)
    halves=[];middle=len(ids)//2
    for split in (slice(0,middle),slice(middle,None)):
        halves.append(fit(ids[split],classes[split],values[split],baseline,mass,fold,jam,
            context_sha256=context_hash,minimum_training_deals=config['minimum_training_deals']))
    eligible=np.minimum(halves[0]['training_counts'],halves[1]['training_counts'])>=config['minimum_training_deals']
    disagreement=eligible&(np.array(halves[0]['selected_actions'])!=np.array(halves[1]['selected_actions']))
    stability=dict(eligible_classes=int(eligible.sum()),disagreeing_classes=int(disagreement.sum()),
        disagreement_population_mass=float(mass[disagreement].sum()),half_actions=[h['selected_actions'] for h in halves],
        diagnostic_only=True,used_to_select_response=False)
    response_path=folder/'response.json';save(response_path,response);response_hash=sha(response_path)
    alternatives={'trained-response':rho}
    for a,name in enumerate(SERIES[1:5]):alternatives[name]=np.tile(np.eye(4)[a],(169,1))
    alternatives['previous-response']=prior
    lo=-context['config']['stack'];hi=context['config']['stack']+context['dead_money']
    prepared={name:prepare(baseline,p,mass,fold,jam,training_classes=classes,training_actions=values,
        centre=False,lower=lo,upper=hi) for name,p in alternatives.items()}
    preparation_path=folder/'residual-preparation.json';save(preparation_path,prepared);preparation_hash=sha(preparation_path)
    save(folder/'training-stability.json',stability)
    estimators={name:PairedEvaluation(Plan(p['residual_lower'],p['residual_upper'],SERIES,
        (config['test_deals'],),alpha=config['family_alpha']),name) for name,p in prepared.items()}
    # The IID population test sampler does not exist until the responder and
    # all residual bounds are saved and hashed. Class-balanced draws end here.
    guard();assert sha(response_path)==response_hash and sha(preparation_path)==preparation_hash
    assert sha(folder/'prior-response.json')==prior_hash
    test=PhysicalDeals(source,mode='full_deck',seed=config['test_seed'])
    save(folder/'test-start.json',dict(response_sha256=response_hash,preparation_sha256=preparation_hash,
        initial_rng=test.checkpoint(),response_frozen_before_test=True,prior_response_sha256=prior_hash))
    test_counts=np.zeros(169,dtype=np.int64);before=time.monotonic()
    for offset in range(0,config['test_deals'],config['batch_size']):
        guard();assert sha(response_path)==response_hash and sha(preparation_path)==preparation_hash
        name=f'test-{offset:06d}';batch_id=f"{config['id']}-{name}"
        batch=dict(format=2,batch_id=batch_id,seed=0,query_limit=100000,deals=test.sample(config['batch_size'])['deals'])
        summary=batch_values(context_path,batch,folder/name,guard,bank,cache)
        cs=summary['classes'];qs=summary['action_values']
        assert np.max(abs(np.asarray(summary['root_probabilities'])-baseline[cs]))<1e-10
        admit_test_ids(response,[f'{batch_id}-{i}' for i in range(len(cs))],context_sha256=context_hash)
        admit_test_ids(prior_response,[f'{batch_id}-{i}' for i in range(len(cs))],context_sha256=context_hash)
        assert sha(folder/'prior-response.json')==sha(prior_response_path)==prior_hash
        entries={}
        for label,p in prepared.items():
            entries[label]=residuals(p,cs,qs).tolist()
            for value in entries[label]:estimators[label].add_difference(value)
        save(folder/name/'residuals.json',dict(response_sha256=response_hash,preparation_sha256=preparation_hash,values=entries))
        test_counts+=np.bincount(cs,minlength=169);batches[name]=sha(folder/name/'summary.json')
    phase_timings['test_seconds']=time.monotonic()-before
    intervals={}
    for name,e in estimators.items():
        original=e.interval();offset=prepared[name]['total_offset']
        intervals[name]=dict(original,residual_mean=original['mean'],exact_offset=offset,
            mean=original['mean']+offset,lower=original['lower']+offset,upper=original['upper']+offset)
    guard();assert sha(response_path)==response_hash and sha(preparation_path)==preparation_hash
    result=dict(complete=True,training_deals=len(ids),test_deals=test.draws,training_counts=response['training_counts'],
        test_counts=test_counts.tolist(),response_sha256=response_hash,preparation_sha256=preparation_hash,
        stability=stability,intervals=intervals,prior_response_sha256=prior_hash,batch_summary_hashes=batches,phase_timings=phase_timings,
        seconds=time.monotonic()-start,population_test_only=True,production_modified=False,
        best_response_upper_bound=False,scope='Fixed BB root deviations with frozen later play; not full-game accuracy or a cross-context certificate.')
    save(folder/'result.json',result)
    return result
