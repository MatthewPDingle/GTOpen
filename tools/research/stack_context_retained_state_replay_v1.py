"""Reconstruct collection state from authenticated retained outputs, without fits.

Replays ordered reservoir insertions in memory from the previous complete
checkpoint. Native outputs, sampled deals and posterior draws are read, not
regenerated. Sampling RNG advancement must reproduce the retained deal document.
"""
import json
from pathlib import Path
import numpy as np
from stack_context_cycle_archive_v1 import sha
from stack_context_board_targets_v1 import prepare, generation_evidence
from stack_context_river_workers_v1 import CollectedVisits, commit
from river_weighted_overlay_ingest_v1 import ingest
from weighted_deal_binding_v1 import DealWeightGeneration
from exact_initial_training_ingest_v2 import InitialTargets, digest
from preflop_allin_matrix_v1 import AllinMatrix
from weighted_physical_reservoir_v1 import ARRAYS
from stack_context_training_checkpoint_v1 import local_document


def require(ok,message):
    if not ok:raise ValueError(message)


def checked_json(path, expected):
    path=Path(path)
    require(expected.get(str(path))==sha(path),'Retained file identity differs: '+str(path))
    return json.loads(path.read_bytes())


def replay_events(part, *, expected, generation, start, iteration, cache, targets,
                  policy_id, guard):
    part=Path(part)
    queries,updates,policies,trace=(checked_json(part/(n+'.json'),expected)
        for n in ('queries','updates','policies','action-trace'))
    overlay=checked_json(part/'conditional/overlay.json',expected)
    evidence=checked_json(part/'conditional/evidence.json',expected)
    for name,h in evidence['artifacts'].items():
        path=part/'conditional'/name
        require(path.resolve().parent==path.parent and expected.get(str(path))==h,
                'Conditional artifact detached from interruption inventory')
    events=[];receivers=[CollectedVisits(p,queries['context_source'],events) for p in (0,1)]
    counts,initial,later,weighted,river=ingest(queries,updates,policies,receivers,iteration,cache,targets,trace,
        generation=generation,start=start,overlay=overlay,expected_policy_id=policy_id,
        expected_evidence_sha256=digest(evidence),guard=guard)
    for name,value in (('derived-targets',initial),('postflop-targets',later),
                       ('weighted-targets',weighted),('river-targets',river)):
        require(value==checked_json(part/(name+'.json'),expected),'Retained target derivation differs: '+name)
    return events,counts


def replay_complete_context(folder,local,config,registry,resources,*,key,model_source,
                            used,inputs,cache,expected,batch_prefix,guard):
    folder=Path(folder);c=config['contexts'][key];source=registry.source(key)
    require((folder/'collection.json').exists(),'Complete retained context required')
    original=checked_json(folder/'collection.json',expected)
    generation=json.loads(model_source)['generation'];iteration=generation+1
    require(original['context_sha256']==key and original['model_sha256']==used['sha256']
            and original['registry_sha256']==registry.sha256,'Wrong retained collection model/context')
    for path,h in original['native_identities'].items():require(sha(path)==h,'Native identity changed')
    matrix_source=Path(inputs['matrix']).read_text();matrix=AllinMatrix(json.loads(matrix_source),source)
    initial=checked_json(folder/'current-initial-policy.json',expected)
    require(initial['used_model']==used and initial['context_sha256']==key,'Initial policy provenance differs')
    root=np.asarray(initial['root']);calls=np.asarray(initial['calls'])
    targets=InitialTargets(matrix_source,source,root,calls,matrix_sha256=resources[key]['matrix_sha256'],generation=generation)
    require(targets.identity==initial['target_identity'],'Initial target identity differs')
    prepared=prepare(model_source=model_source,registry=registry,context_sha256=key,resources=resources,
        physical_catalog_source=Path(inputs['physical_catalog']).read_text(),matrix_source=matrix_source)
    require(np.allclose(prepared['pre'][0],root,rtol=0,atol=1e-10),'Retained initial policy differs from model')
    plan=local['root_regret_state'].plan()
    require(plan==checked_json(folder/'board-plan.json',expected),'Board plan differs from previous complete state')
    sample=local['sampler'].sample(c['deals_per_generation'])
    require(sample==checked_json(folder/'source-generation.json',expected),'Restored RNG does not reproduce saved deals')
    weighted=DealWeightGeneration(sample,source);subsize=c['deals_per_subbatch'];total=[0,0]
    for chunk,start in enumerate(range(0,c['deals_per_generation'],subsize)):
        guard();part=folder/f'batch-{chunk:03d}'
        batch=cache.batch(dict(format=2,batch_id=f'{batch_prefix}-{key}-cycle-{iteration}-batch-{chunk}',
            query_limit=c['query_limit'],seed=int(local['action_rng'].integers(0,2**63)),deals=sample['deals'][start:start+subsize]))
        require(batch==checked_json(part/'batch.json',expected),'Action RNG or retained batch differs')
        record=checked_json(part/'worker-result.json',expected)
        for name,h in record['artifacts'].items():
            path=part/name
            require(path.resolve().is_relative_to(part.resolve()) and expected.get(str(path))==h
                    and sha(path)==h,'Worker artifact differs')
        events,counts=replay_events(part,expected=expected,generation=weighted,start=start,iteration=iteration,
            cache=cache,targets=targets,policy_id=used['sha256'],guard=guard)
        require(counts==record['counts'],'Worker insertion counts differ')
        commit(dict(record,events=events),local['reservoirs'],expected_start=start,iteration=iteration,
            expected_context_sha256=key,expected_model_sha256=used['sha256'],expected_registry_sha256=registry.sha256)
        total=[a+b for a,b in zip(total,counts)]
    board_records=[]
    for row in original['board_results']:
        result=checked_json(row['path'],expected)
        require(result==row['result'] and sha(row['path'])==row['sha256']
                and expected.get(result['tree_artifact'])==result['tree_sha256'], 'Board result binding differs')
        board_records.append(result['record'])
    evidence=generation_evidence(local['root_regret_state'],prepared,plan,board_records)
    require(evidence==checked_json(folder/'board-generation-evidence.json',expected),'Reconstructed board evidence differs')
    delta=local['root_regret_state'].step(plan,evidence,played_policy=prepared['pre'][0],exact_terms=prepared['exact'])
    values=matrix.evaluate(root,calls)
    exact=local['exact_btn_state'].step(iteration,calls,values['btn_jam_mass'],values['btn_fold_entries'],values['btn_call_entries'])
    require(delta.tolist()==original['root_delta'] and exact.tolist()==original['exact_delta']
            and [r.summary() for r in local['reservoirs']]==original['reservoirs'],'Reconstructed collection differs')
    return dict(context_sha256=key,iteration=iteration,ordered_insertions=total,
                collection_sha256=sha(folder/'collection.json'),native_calls=0,new_target_draws=0)


def compare_local(replayed,reference,args):
    require(replayed['sampler'].checkpoint()==reference['sampler'].checkpoint(),'Sampler RNG state differs')
    require(replayed['action_rng'].bit_generator.state==reference['action_rng'].bit_generator.state,'Action RNG state differs')
    require(local_document(replayed,args)==local_document(reference,args),'Root/exact accumulated state differs')
    for a,b in zip(replayed['reservoirs'],reference['reservoirs']):
        require(a.summary()==b.summary() and a.rng.bit_generator.state==b.rng.bit_generator.state,
                'Reservoir counters or RNG differ')
        for name in ARRAYS:
            require(np.array_equal(getattr(a,name)[:a.size],getattr(b,name)[:b.size]),
                    'Reservoir array differs: '+name)
    return True
