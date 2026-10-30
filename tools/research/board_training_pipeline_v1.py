"""Transactional board-root pipeline; GPU integration control still required."""
import copy
import json
from pathlib import Path
import subprocess
import time
import numpy as np
import board_training_checkpoint_v1 as checkpoint
import sampled_visible_hybrid_checkpoint_v1 as storage
from board_training_targets_v1 import prepare,generation_evidence
from board_training_board_workers_v1 import pool as board_pool,complete as complete_board
from board_root_accumulator_v1 import BoardRootRegrets,CHANCE
from class_stratified_physical_deals_v1 import ClassStratifiedDeals
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir
from exact_btn_regret_accumulator_v1 import ExactBtnRegrets
from weighted_training_v1 import first_action_view
from board_training_policy_v1 import probabilities
from weighted_training_graph_fit_v2 import fit
from weighted_deal_binding_v1 import DealWeightGeneration
from weighted_preflop_table_v1 import build
from exact_initial_training_ingest_v2 import InitialTargets
from preflop_allin_matrix_v1 import AllinMatrix
from sampled_allin_protocol_v3 import policy_document
from sampled_physical_root_evaluation_v1 import save
from weighted_training_workers_v1 import pool,complete,commit



def initialize(objects,config,**args):
    checkpoint.require_config(config);source=args['context_source']
    root_config=dict(config['board_root']);assert root_config.pop('chance')==CHANCE
    root=BoardRootRegrets(**root_config)
    exact=ExactBtnRegrets(storage.digest(source),args['entry_mass'])
    ref=checkpoint.write_model(objects,0,storage.uniform_networks(),[1.,1.],[None,None],root,exact,**args)
    return dict(completed_iterations=0,sampler=ClassStratifiedDeals(source,seed=config['sampler_seed']),
        action_rng=np.random.Generator(np.random.PCG64(config['action_seed'])),
        reservoirs=[WeightedPhysicalReservoir(config['reservoir_capacity'],p,config['reservoir_seeds'][p],source) for p in (0,1)],
        played_bank=[],next_model=ref,root_regret_state=root,exact_btn_state=exact)


def update(folder,objects,state,config,*,context_path,catalog_source,matrix_source,matrix_sha256,
           cache,executable,integration_executable,trace_executable,batch_prefix,guard,workers,
           physical_catalog_source,board_executable,board_workers,on_stage=lambda stage:None):
    guard();began=time.monotonic();source=Path(context_path).read_text()
    caller_state=state;state=copy.deepcopy(state)
    on_stage('staged')
    matrix=AllinMatrix(json.loads(matrix_source),source)
    args=dict(context_source=source,catalog_source=catalog_source,matrix_sha256=matrix_sha256,entry_mass=matrix.btn_mass,root_config=config['board_root'])
    model=checkpoint.validate_state(objects,state,config,**args)
    if cache.sha256!=config['allin_cache_sha256']:raise ValueError('Wrong all-in cache')
    generation=state['completed_iterations'];iteration=generation+1;used=state['next_model']
    response_hi=json.loads(source)['nodes'][0]['children'][3]+1
    catalog=json.loads(catalog_source)
    catalog_query=dict(context_source=source,observations=[r['observation'] for r in catalog['native_observations']])
    p,coverage=probabilities(catalog_query,model,device=config['device'],catalog_source=catalog_source,
        matrix_sha256=matrix_sha256,entry_mass=matrix.btn_mass,root_config=config['board_root'])
    root=np.zeros((169,4));calls=np.zeros(169)
    for item,row in zip(catalog['native_observations'],p):
        if item['player']==0:root[item['hand_class']]=row
        else:calls[item['hand_class']]=row[1]
    exact_values=matrix.evaluate(root,calls)
    targets=InitialTargets(matrix_source,source,root,calls,matrix_sha256=matrix_sha256,generation=generation)
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=False)
    save(folder/'current-initial-policy.json',dict(used_model=used,root=root.tolist(),calls=calls.tolist(),target_identity=targets.identity,coverage=coverage))
    board_plan=state['root_regret_state'].plan()
    payload=dict(model_source=storage.read_object(objects,used).decode(),context_source=source,
        catalog_source=catalog_source,physical_catalog_source=physical_catalog_source,
        matrix_source=matrix_source,root_config=config['board_root'])
    prepared=prepare(**payload)
    if not np.allclose(prepared['pre'][0],root,rtol=0,atol=1e-10):
        raise ValueError('CPU board root disagrees with played CUDA root')
    save(folder/'board-plan.json',board_plan)
    board_folder=folder/'board-targets';board_folder.mkdir()

    with board_pool(board_workers,payload=payload,context_path=context_path,executable=board_executable,folder=board_folder) as board_executor:
        board_futures=[board_executor.submit(complete_board,i,b) for i,b in enumerate(board_plan['boards'])]
        timings=dict(sampling=0.,native_queries=0.,inference=0.,native_updates=0.,native_trace=0.,ingestion=0.,root_integration=0.,fit=0.,publication=0.,queue_wait=0.,ordered_insertion=0.)
        before=time.monotonic();sample=state['sampler'].sample(config['deals_per_generation'])
        weighted=DealWeightGeneration(sample,source);timings['sampling']=time.monotonic()-before
        save(folder/'source-generation.json',sample)
        audits=[];bindings=[];subbatches=[];pending=[];worker_stats=[];peak_pending=0
        subsize=config['deals_per_subbatch'];pipeline_began=time.monotonic()
        def consume():
            chunk,cov,future=pending.pop(0);guard();t=time.monotonic();result=future.result(timeout=120)
            timings['queue_wait']+=time.monotonic()-t;t=time.monotonic()
            commit(result,state['reservoirs'],expected_start=chunk*subsize,iteration=iteration)
            timings['ordered_insertion']+=time.monotonic()-t
            audits.append(result['integrated']);bindings.append(result['binding'])
            for k,v in result['timings'].items():timings[k]+=v
            worker_stats.append(dict(pid=result['pid'],rss_bytes=result['rss_bytes'],seconds=result['seconds']))
            subbatches.append(dict(chunk=chunk,counts=result['counts'],coverage=cov,artifacts=result['artifacts']))
        with pool(workers,context_path=context_path,cache=cache,targets=targets,generation=weighted,iteration=iteration,
                  executable=executable,trace_executable=trace_executable,integration_executable=integration_executable) as executor:
            for chunk,start in enumerate(range(0,config['deals_per_generation'],subsize)):
                guard();part=folder/f'batch-{chunk:02d}';part.mkdir()
                batch=cache.batch(dict(format=2,batch_id=f'{batch_prefix}-iteration-{iteration}-batch-{chunk}',
                    query_limit=config['query_limit'],seed=int(state['action_rng'].integers(0,2**63)),deals=sample['deals'][start:start+subsize]))
                bp=part/'batch.json';qp=part/'queries.json';pp=part/'policies.json';save(bp,batch)
                before=time.monotonic()
                result=subprocess.run([str(executable),'queries',str(context_path),str(bp),'-',str(qp)],timeout=120,
                    capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
                timings['native_queries']+=time.monotonic()-before
                if result.returncode:raise RuntimeError(result.stderr[-2000:])
                queries=json.loads(qp.read_text());before=time.monotonic()
                p,cov=probabilities(first_action_view(queries,response_hi),model,device=config['device'],
                    catalog_source=catalog_source,matrix_sha256=matrix_sha256,entry_mass=matrix.btn_mass,root_config=config['board_root'])
                timings['inference']+=time.monotonic()-before;save(pp,policy_document(queries,p))
                pending.append((chunk,cov,executor.submit(complete,str(part),start)))
                peak_pending=max(peak_pending,len(pending))
                if len(pending)>=2*workers:consume()
            while pending:consume()
        timings['pipeline_wall']=time.monotonic()-pipeline_began
        on_stage('physical-targets-complete')
        networks=[];fits=[];before=time.monotonic()
        for player,reservoir in enumerate(state['reservoirs']):
            net,metric=fit(reservoir,seed=config['fit_seed_base']+iteration*200003+player,steps=config['fit_steps'],
                device=config['device'],chunk_size=config['chunk_size'],learning_rate=config['learning_rate'],guard=guard)
            networks.append(net);fits.append(metric)
        timings['fit']=time.monotonic()-before;before=time.monotonic()
        on_stage('fits-complete')
        exact=copy.deepcopy(state['exact_btn_state'])
        delta=exact.step(iteration,calls,exact_values['btn_jam_mass'],exact_values['btn_fold_entries'],exact_values['btn_call_entries'])
        board_results=[];wait_began=time.monotonic()
        for future in board_futures:
            guard();board_results.append(future.result(timeout=180))
        timings['board_wait']=time.monotonic()-wait_began
    evidence=generation_evidence(state['root_regret_state'],prepared,board_plan,[x['result']['record'] for x in board_results])
    save(folder/'board-generation-evidence.json',evidence)
    on_stage('boards-complete')
    before=time.monotonic()
    root_state=copy.deepcopy(state['root_regret_state'])
    root_state.step(board_plan,evidence,played_policy=prepared['pre'][0],exact_terms=prepared['exact'])
    on_stage('root-update-complete')
    current=checkpoint.write_model(objects,iteration,networks,[m['advantage_scale'] for m in fits],
        [build(r,source) for r in state['reservoirs']],root_state,exact,**args)
    state.update(completed_iterations=iteration,next_model=current,exact_btn_state=exact,root_regret_state=root_state,
        played_bank=[*state['played_bank'],used])
    on_stage('ready-to-publish')
    reference=checkpoint.save_checkpoint(objects,state,config,**args);timings['publication']=time.monotonic()-before
    metric=dict(iteration=iteration,used_model=used,next_model=current,checkpoint=reference,timings=timings,
        seconds=time.monotonic()-began,fits=fits,subbatches=subbatches,board_draws=root_state.document()['board_draws'],
        root_covered_classes=169,board_results=board_results,exact_btn_updates=exact.steps,
        exact_btn_delta=delta.tolist(),reservoirs=[r.summary() for r in state['reservoirs']],
        workers=workers,board_workers=board_workers,peak_pending=peak_pending,worker_stats=worker_stats,fit_runtime='ordered-weighted-cuda-gradient-graph-v2',
        timing_note='Worker category totals overlap; use seconds and pipeline_wall for wall-clock comparisons, including startup and shutdown.')
    save(folder/'metrics.json',metric)
    caller_state.clear();caller_state.update(state)
    return metric
