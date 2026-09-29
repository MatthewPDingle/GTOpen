"""Collect all games against one frozen model, fit jointly, publish atomically."""
import copy
import json
from pathlib import Path
import subprocess
import time
from concurrent.futures import TimeoutError
import numpy as np
import stack_context_training_checkpoint_v1 as checkpoint
import sampled_visible_hybrid_checkpoint_v1 as storage
from stack_context_current_policy_v1 import CurrentPolicy
from stack_context_board_targets_v1 import prepare,generation_evidence
from stack_context_board_workers_v1 import pool as board_pool,complete as complete_board
from stack_context_river_workers_v1 import pool,complete,commit
from stack_context_training_fit_v1 import fit
from weighted_training_v1 import first_action_view
from weighted_deal_binding_v1 import DealWeightGeneration
from exact_initial_training_ingest_v2 import InitialTargets
from preflop_allin_matrix_v1 import AllinMatrix
from sampled_allin_protocol_v3 import policy_document
from sampled_physical_root_evaluation_v1 import save,sha


def wait(future,guard):
    # A reporting timeout is not a terminal worker result and never starts a retry.
    while True:
        guard()
        try:return future.result(timeout=1)
        except TimeoutError:
            if future.done():return future.result()


def identities(config,paths):
    result={str(p):sha(p) for p in paths}
    if any(config['source_identities'].get(p)!=h for p,h in result.items()):
        raise ValueError('Native source is absent from or differs from the frozen configuration')
    return result


def collect(folder,local,config,registry,resources,*,key,model_source,used,inputs,cache,native,
            guard,workers,board_workers,batch_prefix,on_stage):
    began=time.monotonic();c=config['contexts'][key];source=registry.source(key)
    context_path=Path(inputs['context_path']);matrix_source=Path(inputs['matrix']).read_text()
    physical_source=Path(inputs['physical_catalog']).read_text();args=resources[key]
    if context_path.read_text()!=source or sha(inputs['physical_catalog'])!=inputs['physical_catalog_sha256']:
        raise ValueError('Context-local collection sources changed')
    if cache.sha256!=c['allin_cache_sha256']:raise ValueError('Wrong exact all-in cache')
    native_ids=identities(config,[context_path,*native.values()])
    matrix=AllinMatrix(json.loads(matrix_source),source);generation=json.loads(model_source)['generation'];iteration=generation+1
    engine=CurrentPolicy(json.loads(model_source),registry,context_sha256=key,resources=resources,device=config['device'])
    catalog=json.loads(args['catalog_source']);observations=[r['observation'] for r in catalog['native_observations']]
    p=engine.infer(engine.prepare(dict(context_source=source,observations=observations)))
    root=np.zeros((169,4));calls=np.zeros(169)
    for row,probability in zip(catalog['native_observations'],p):
        if row['player']==0:root[row['hand_class']]=probability
        else:calls[row['hand_class']]=probability[1]
    exact_values=matrix.evaluate(root,calls)
    targets=InitialTargets(matrix_source,source,root,calls,matrix_sha256=args['matrix_sha256'],generation=generation)
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=False)
    save(folder/'current-initial-policy.json',dict(used_model=used,context_sha256=key,root=root.tolist(),calls=calls.tolist(),target_identity=targets.identity))
    payload=dict(model_source=model_source,registry=registry,context_sha256=key,resources=resources,
                 physical_catalog_source=physical_source,matrix_source=matrix_source)
    prepared=prepare(**payload)
    if not np.allclose(prepared['pre'][0],root,rtol=0,atol=1e-10):raise ValueError('CPU/CUDA initial policies differ')
    board_plan=local['root_regret_state'].plan();save(folder/'board-plan.json',board_plan)
    board_folder=folder/'board-targets';board_folder.mkdir()
    board_ids={str(p):native_ids[str(p)] for p in (context_path,native['board'])}
    river_ids={str(p):native_ids[str(p)] for p in (context_path,native['bridge'],native['trace'],native['integration'],native['river'])}
    river_payload=dict(model_source=model_source,policy_id=used['sha256'],registry=registry,context_sha256=key,resources=resources)
    with board_pool(board_workers,payload=payload,context_path=context_path,executable=native['board'],folder=board_folder,
                    expected_native_identities=board_ids) as board_executor:
        board_futures=[board_executor.submit(complete_board,i,b) for i,b in enumerate(board_plan['boards'])]
        sample=local['sampler'].sample(c['deals_per_generation']);weighted=DealWeightGeneration(sample,source)
        save(folder/'source-generation.json',sample)
        pending=[];subbatches=[];subsize=c['deals_per_subbatch'];peak_pending=0
        def consume():
            chunk,part,expected,future=pending.pop(0);result=wait(future,guard)
            if result['input_identities']!=expected or result['native_identities']!=river_ids:
                raise ValueError('Worker input provenance changed before insertion')
            for name,h in result['artifacts'].items():
                if sha(part/name)!=h:raise ValueError('Worker artifact changed before insertion')
            commit(result,local['reservoirs'],expected_start=chunk*subsize,iteration=iteration,
                expected_context_sha256=key,expected_model_sha256=used['sha256'],expected_registry_sha256=registry.sha256)
            record={k:v for k,v in result.items() if k!='events'}
            save(part/'worker-result.json',record);subbatches.append(dict(chunk=chunk,path=str(part/'worker-result.json'),sha256=sha(part/'worker-result.json'),counts=result['counts'],river=result['river']))
        with pool(workers,context_path=context_path,cache=cache,targets=targets,generation=weighted,iteration=iteration,
                  executable=native['bridge'],trace_executable=native['trace'],integration_executable=native['integration'],
                  river_payload=river_payload,river_executable=native['river'],expected_native_identities=river_ids) as executor:
            for chunk,start in enumerate(range(0,c['deals_per_generation'],subsize)):
                guard();part=folder/f'batch-{chunk:03d}';part.mkdir()
                batch=cache.batch(dict(format=2,batch_id=f'{batch_prefix}-{key}-cycle-{iteration}-batch-{chunk}',
                    query_limit=c['query_limit'],seed=int(local['action_rng'].integers(0,2**63)),deals=sample['deals'][start:start+subsize]))
                bp=part/'batch.json';qp=part/'queries.json';pp=part/'policies.json';save(bp,batch)
                done=subprocess.run([str(native['bridge']),'queries',str(context_path),str(bp),'-',str(qp)],
                    timeout=120,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
                if done.returncode:raise RuntimeError(done.stderr.decode(errors='replace')[-2000:])
                queries=json.loads(qp.read_bytes())
                view=first_action_view(queries,json.loads(source)['nodes'][0]['children'][3]+1)
                p=engine.infer(engine.prepare(view));save(pp,policy_document(queries,p))
                expected={name:sha(part/(name+'.json')) for name in ('batch','queries','policies')}
                pending.append((chunk,part,expected,executor.submit(complete,str(part),start,expected)))
                peak_pending=max(peak_pending,len(pending))
                if len(pending)>=2*workers:consume()
            while pending:consume()
        on_stage('physical-targets-complete',key)
        board_results=[wait(f,guard) for f in board_futures]
    for record in board_results:
        result=record['result']
        if (result['context_sha256']!=key or result['registry_sha256']!=registry.sha256 or result['model_sha256']!=used['sha256']
                or result['native_identities']!=board_ids or sha(record['path'])!=record['sha256']
                or sha(result['tree_artifact'])!=result['tree_sha256']):raise ValueError('Board result provenance differs')
    evidence=generation_evidence(local['root_regret_state'],prepared,board_plan,[r['result']['record'] for r in board_results])
    save(folder/'board-generation-evidence.json',evidence)
    root_delta=local['root_regret_state'].step(board_plan,evidence,played_policy=prepared['pre'][0],exact_terms=prepared['exact'])
    exact_delta=local['exact_btn_state'].step(iteration,calls,exact_values['btn_jam_mass'],exact_values['btn_fold_entries'],exact_values['btn_call_entries'])
    for path,h in native_ids.items():
        if sha(path)!=h:raise ValueError('Native source changed during collection')
    result=dict(context_sha256=key,model_sha256=used['sha256'],registry_sha256=registry.sha256,
        seconds=time.monotonic()-began,subbatches=subbatches,board_results=board_results,peak_pending=peak_pending,
        reservoirs=[r.summary() for r in local['reservoirs']],root_delta=root_delta.tolist(),exact_delta=exact_delta.tolist(),
        source_generation_sha256=sha(folder/'source-generation.json'),native_identities=native_ids)
    save(folder/'collection.json',result);on_stage('context-complete',key)
    return result


def update(folder,objects,state,config,registry,resources,*,inputs,cache,native,guard,workers=2,board_workers=1,
           batch_prefix,on_stage=lambda stage,key=None:None):
    guard();began=time.monotonic();checkpoint.validate_state(objects,state,config,registry,resources)
    if set(inputs)!=set(registry.fit_contexts):raise ValueError('All fitted game inputs required')
    if set(native)!={'bridge','trace','integration','river','board'}:raise ValueError('Complete native executable set required')
    for path,h in config['source_identities'].items():
        if sha(path)!=h:raise ValueError('Registered pipeline source changed')
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=False)
    used=state['next_model'];model_source=storage.read_object(objects,used).decode()
    staged=dict(contexts=copy.deepcopy(state['contexts']),collected_against={});collections=[]
    on_stage('staged')
    for key in registry.fit_contexts:
        guard();collections.append(collect(folder/key,staged['contexts'][key],config,registry,resources,key=key,
            model_source=model_source,used=used,inputs=inputs[key],cache=cache,native=native,guard=guard,
            workers=workers,board_workers=board_workers,batch_prefix=batch_prefix,on_stage=on_stage))
        staged['collected_against'][key]=used['sha256']
    on_stage('all-contexts-collected');networks=[];fits=[];iteration=state['completed_cycles']+1
    for actor in (0,1):
        net,metric=fit(registry,{k:s['reservoirs'][actor] for k,s in staged['contexts'].items()},player=actor,
            context_weights=config['context_weights'],seed=config['fit_seed_base']+iteration*200003+actor,
            steps=config['fit_steps'],device=config['device'],chunk_size=config['chunk_size'],learning_rate=config['learning_rate'],guard=guard)
        networks.append(net);fits.append(metric)
    on_stage('fits-complete')
    for path,h in config['source_identities'].items():
        if sha(path)!=h:raise ValueError('Pipeline source changed before publication')
    candidate,reference=checkpoint.complete_cycle(objects,state,staged,config,registry,resources,
        networks=networks,on_stage=lambda stage:on_stage(stage))
    metric=dict(completed_cycles=candidate['completed_cycles'],used_model=used,next_model=candidate['next_model'],
        checkpoint=reference,collections=collections,fits=fits,seconds=time.monotonic()-began)
    save(folder/'metrics.json',metric)
    # The caller publishes its resume marker only after this complete result exists.
    return candidate,reference,metric
