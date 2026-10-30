"""Actual typed native collection, joint fitting and complete-cycle publication.

Separate prospective runner component. Original experiments are untouched.
Contexts share one frozen played model; each complete ordered board generation
updates every preflop decision. Physical/posterior64 visits train postflop only.
No partial cycle is resumed or automatically retried by this module.
"""
import copy
import json
import math
import multiprocessing as mp
from pathlib import Path
import sys
import time
from concurrent.futures import TimeoutError

import numpy as np

import preflop_expected_training_checkpoint_v1 as checkpoint
import sampled_visible_hybrid_checkpoint_v1 as storage
import stack_context_inputs_v1 as inputs_api
from preflop_expected_native_targets_v2 import FrozenExpectedTargets
from preflop_expected_policy_v1 import ExpectedPolicy
from preflop_expected_training_fit_v1 import fit
import preflop_expected_board_workers_v1 as board_workers_api
import preflop_expected_river_workers_v1 as river_workers_api
from preflop_expected_board_workers_v1 import pool as board_pool, complete as complete_board
from preflop_expected_river_workers_v1 import pool as river_pool, complete as complete_river, commit
from preflop_expected_native_execution_v1 import run_native, verify_native, sha
from preflop_expected_worker_cancellation_v1 import coordinated_pool
from weighted_training_v1 import first_action_view
from weighted_deal_binding_v1 import DealWeightGeneration
from exact_initial_training_ingest_v2 import InitialTargets, digest
from sampled_allin_protocol_v3 import policy_document
from sampled_physical_root_evaluation_v1 import save

METHOD = 'typed-all-node-native-joint-cycle-v1'


def wait(future, guard):
    # An observation timeout cannot relaunch a worker or replay an insertion.
    while True:
        guard()
        try: return future.result(timeout=1)
        except TimeoutError:
            if future.done(): return future.result()


def verify_sources(config):
    for path, identity in config['source_identities'].items():
        if sha(path) != identity: raise ValueError('Frozen runner source changed: '+path)
    roots = {Path(__file__).resolve().parent, Path(checkpoint.__file__).resolve().parent,
             Path(inputs_api.__file__).resolve().parent}
    for module in list(sys.modules.values()):
        path = getattr(module, '__file__', None)
        if path and Path(path).suffix == '.py' and Path(path).resolve().parent in roots:
            path = str(Path(path).resolve())
            if config['source_identities'].get(path) != sha(path):
                raise ValueError('Imported research implementation is not pinned: '+path)


def identities(config, paths):
    result = {str(Path(p).resolve()):sha(p) for p in paths}
    if any(config['source_identities'].get(p) != h for p,h in result.items()):
        raise ValueError('Native/context source absent from frozen configuration')
    return result


def _artifact_ref(path):
    path = Path(path).resolve()
    return dict(path=str(path), sha256=sha(path))


def _read(ref, root):
    path = Path(ref['path']).resolve(); root = Path(root).resolve()
    if not path.is_relative_to(root) or sha(path) != ref['sha256']:
        raise ValueError('Changed or unowned runner artifact')
    return json.loads(path.read_bytes())


def verify_board(record, *, folder, index, board, provider, native_ids, context_path, executable, limits, config):
    folder = Path(folder).resolve(); result = _read(dict(path=record['path'],sha256=record['sha256']),folder)
    if result != record['result']: raise ValueError('Board worker result differs from saved terminal result')
    recipe = provider.recipe
    if (result['context_sha256'] != recipe['context_sha256']
            or result['registry_sha256'] != recipe['registry_sha256']
            or result['model_sha256'] != recipe['model_sha256']
            or result['native_identities'] != native_ids or result['runtime_limits'] != limits
            or result['record']['draw_index'] != index or result['record']['board'] != board
            or result['record']['policy_recipe_sha256'] != digest(recipe)):
        raise ValueError('Board result detached from complete frozen policy/plan')
    expected_worker_sources={str(Path(sys.modules[n].__file__).resolve()):sha(sys.modules[n].__file__)
        for n in ('preflop_expected_board_workers_v1','preflop_expected_native_execution_v1',
                  'preflop_expected_native_targets_v2','preflop_expected_native_targets_v1','preflop_expected_policy_v1')}
    plan=provider._plan
    if (expected_worker_sources != result['worker_source_identities']
            or any(config['source_identities'].get(p)!=h for p,h in result['worker_source_identities'].items())
            or result['recipe']!=recipe or result['draw_index']!=index or result['board']!=board
            or result['generation']!=recipe['generation'] or result['cuda_visible_devices']!='-1'
            or result['threadpool_limit']!=1 or result['recipe_sha256']!=digest(recipe)
            or result['plan_sha256']!=digest(plan) or result['parent_state_sha256']!=plan['parent_state_sha256']):
        raise ValueError('Board worker implementation or execution scope differs from the pinned runner')
    request_path = Path(result['request_artifact']).resolve()
    if not request_path.is_relative_to(folder) or sha(request_path) != result['request_sha256']:
        raise ValueError('Board request changed or escaped owned folder')
    request, _ = provider.request(board)
    if (json.loads(request_path.read_bytes()) != request or result['request_document_sha256']!=digest(request)):
        raise ValueError('Board request differs from original complete private domain')
    invocation_ids = dict(native_ids, **{str(request_path):sha(request_path)})
    if result['invocation_identities']!=invocation_ids: raise ValueError('Changed invocation source binding')
    invocation = result['native_invocation']
    verify_native(invocation, executable=executable,
        arguments=[str(Path(context_path).resolve()),str(request_path)], expected_identities=invocation_ids)
    for kind in ('receipt_path','stdout_path','stderr_path'):
        if not Path(invocation[kind]).resolve().is_relative_to(folder):
            raise ValueError('Native board artifact escaped ownership')
    if (result['tree_artifact'] != invocation['stdout_path']
            or result['tree_sha256'] != invocation['stdout_sha256']
            or result['record']['tree_sha256'] != invocation['stdout_sha256']):
        raise ValueError('Board contribution is not bound to authenticated native raw output')
    if (invocation['receipt']['caller'] != dict(pid=result['pid'],creation_time=result['creation_time'])
            or invocation['receipt']['timeout_seconds'] != limits['native_timeout_seconds']
            or invocation['receipt']['max_output_bytes'] != limits['max_output_bytes']):
        raise ValueError('Board process receipt detached from exact worker identity or limits')
    if (type(result['pid']) is not int or result['pid']<=0
            or any(type(result[n]) not in (int,float) or not math.isfinite(result[n]) or result[n]<0
                for n in ('creation_time','initialized_unix','started_unix','terminal_unix','seconds','worker_seconds'))
            or not result['creation_time']<=result['initialized_unix']<=result['started_unix']
                <=invocation['receipt']['started_unix']<=invocation['receipt']['terminal_unix']<=result['terminal_unix']
            or result['worker_seconds']>limits['max_worker_seconds']
            or result['seconds']>result['worker_seconds']):
        raise ValueError('Board worker timing or lifetime binding changed')
    # Replay the actual target construction, not only accumulator arithmetic.
    # Until profiling qualifies a less costly independent readback schedule, the
    # coordinator pays this explicit correctness cost before accepting a draw.
    replay=provider.draw_record(Path(invocation['stdout_path']).read_bytes(),
        expected_tree_sha256=invocation['stdout_sha256'],draw_index=index)
    if result['record']!=replay: raise ValueError('Board values differ from authenticated native-tree replay')
    return result['record']


def collect(folder, local, config, registry, resources, *, key, model_source, used,
            inputs, cache, native, guard, workers, board_workers, runtime_limits,
            batch_prefix, on_stage):
    began = time.monotonic(); c = config['contexts'][key]; source = registry.source(key); args=resources[key]
    if set(inputs) != {'context_path','matrix','physical_catalog','physical_catalog_sha256'}:
        raise ValueError('Exact context/matrix/physical input references required')
    context_path = Path(inputs['context_path']).resolve()
    if (context_path.read_bytes().decode('utf-8') != source
            or Path(inputs['matrix']).read_bytes().decode('utf-8') != args['matrix_source']
            or Path(inputs['physical_catalog']).read_bytes().decode('utf-8') != args['physical_catalog_source']
            or sha(inputs['physical_catalog']) != inputs['physical_catalog_sha256']
            or inputs['physical_catalog_sha256'] != args['physical_catalog_sha256']
            or cache.sha256 != c['allin_cache_sha256']):
        raise ValueError('Changed actual game inputs or exact all-in cache')
    native_ids=identities(config,[context_path,*native.values(),inputs['matrix'],inputs['physical_catalog']])
    provider=FrozenExpectedTargets(state=local['preflop_state'],model_source=model_source,
                                  registry=registry,resources=resources)
    if provider.recipe['model_sha256'] != used['sha256']: raise ValueError('Wrong frozen model source')
    pre=provider.played_preflop(); context=json.loads(source); jam=context['nodes'][0]['children'][3]
    # Existing physical ingestion checks root/all-in values. These targets are
    # diagnostics/transport validation only: no sampled preflop row is retained.
    targets=InitialTargets(args['matrix_source'],source,pre[0],pre[jam][:,1],
        matrix_sha256=local['preflop_state'].config['matrix_sha256'],generation=local['preflop_state'].steps)
    generation=json.loads(model_source)['generation']; iteration=generation+1
    engine=ExpectedPolicy(json.loads(model_source),registry,context_sha256=key,
                          resources=resources,device=config['device'])
    if any(np.max(abs(engine.played_preflop()[i]-p)) > 1e-10 for i,p in pre.items()):
        raise ValueError('CPU/CUDA complete preflop policy disagreement')
    folder=Path(folder).resolve(); folder.mkdir(parents=True,exist_ok=False)
    plan=local['preflop_state'].plan(); save(folder/'board-plan.json',plan)
    save(folder/'played-target-recipe.json',provider.recipe)
    board_folder=folder/'board-targets'; board_folder.mkdir()
    board_ids={str(p):native_ids[str(p)] for p in (context_path,Path(native['board']).resolve())}
    river_ids={str(p):native_ids[str(p)] for p in (context_path,*[Path(native[n]).resolve() for n in ('bridge','trace','river')])}
    payload=dict(state=local['preflop_state'],model_source=model_source,registry=registry,resources=resources)
    resources_sha=digest(resources)
    river_payload=dict(model_source=model_source,policy_id=used['sha256'],registry=registry,
        context_sha256=key,resources=resources,resources_sha256=resources_sha)
    query_invocations=[]; pending=[]; subbatches=[]; peak_pending=0
    cancellation=mp.get_context('spawn').Event()
    with coordinated_pool(board_pool(board_workers,payload=payload,context_path=context_path,executable=native['board'],
            folder=board_folder,expected_native_identities=board_ids,runtime_limits=runtime_limits['board'],
            cancel_event=cancellation),cancellation) as boards:
        board_futures=[boards.submit(complete_board,i,b) for i,b in enumerate(plan['boards'])]
        sample=local['sampler'].sample(c['deals_per_generation']); weighted=DealWeightGeneration(sample,source)
        save(folder/'source-generation.json',sample); subsize=c['deals_per_subbatch']
        def consume():
            chunk,part,expected,future=pending.pop(0); result=wait(future,guard)
            weighted.verify(result['binding'])
            roles=dict(context_path=str(context_path),executable=str(Path(native['bridge']).resolve()),
                trace_executable=str(Path(native['trace']).resolve()),river_executable=str(Path(native['river']).resolve()))
            if (result['native_roles']!=roles
                    or any(config['source_identities'].get(p)!=h for p,h in result['worker_source_identities'].items())
                    or result['worker_source_identities'].get(str(Path(river_workers_api.__file__).resolve()))
                        != sha(river_workers_api.__file__)):
                raise ValueError('Physical worker executable or implementation differs from registered runner')
            commit(result,local['reservoirs'],expected_start=chunk*subsize,iteration=iteration,
                expected_context_sha256=key,expected_model_sha256=used['sha256'],
                expected_registry_sha256=registry.sha256,expected_resources_sha256=resources_sha,
                expected_native_identities=river_ids,expected_runtime_limits=runtime_limits['river'],
                expected_artifact_root=part,expected_input_identities=expected)
            saved={k:v for k,v in result.items() if k!='events'}
            save(part/'worker-result.json',saved)
            subbatches.append(dict(chunk=chunk,result=_artifact_ref(part/'worker-result.json'),
                counts=result['counts'],observed_counts=result['observed_counts'],
                excluded_preflop_counts=result['excluded_preflop_counts'],river=result['river']))
        with coordinated_pool(river_pool(workers,context_path=context_path,cache=cache,targets=targets,
                generation=weighted,iteration=iteration,executable=native['bridge'],trace_executable=native['trace'],
                river_payload=river_payload,river_executable=native['river'],expected_native_identities=river_ids,
                runtime_limits=runtime_limits['river'],cancel_event=cancellation),cancellation) as rivers:
            for chunk,start in enumerate(range(0,c['deals_per_generation'],subsize)):
                guard(); part=folder/f'batch-{chunk:03d}'; part.mkdir()
                batch=cache.batch(dict(format=2,batch_id=f'{batch_prefix}-{key}-cycle-{iteration}-batch-{chunk}',
                    query_limit=c['query_limit'],seed=int(local['action_rng'].integers(0,2**63)),
                    deals=sample['deals'][start:start+subsize]))
                bp=part/'batch.json'; qp=part/'queries.json'; pp=part/'policies.json'; save(bp,batch)
                invoke_ids={str(p):native_ids[str(p)] for p in (context_path,Path(native['bridge']).resolve())}
                invoke_ids[str(bp)]=sha(bp)
                invocation=run_native(native['bridge'],['queries',str(context_path),str(bp),'-',str(qp)],
                    folder=part,label='native-queries',expected_identities=invoke_ids,guard=guard,
                    timeout=runtime_limits['river']['native_timeout_seconds'])
                queries=json.loads(qp.read_bytes())
                view=first_action_view(queries,context['nodes'][0]['children'][3]+1)
                probabilities=engine.infer(engine.prepare(view)); save(pp,policy_document(queries,probabilities))
                expected={name:sha(part/(name+'.json')) for name in ('batch','queries','policies')}
                query_invocations.append(dict(chunk=chunk,invocation=invocation,queries=_artifact_ref(qp)))
                pending.append((chunk,part,expected,rivers.submit(complete_river,str(part),start,expected)))
                peak_pending=max(peak_pending,len(pending))
                if len(pending)>=2*workers: consume()
            while pending: consume()
        on_stage('physical-targets-complete',key)
        board_results=[wait(f,guard) for f in board_futures]
    records=[verify_board(r,folder=board_folder,index=i,board=b,provider=provider,native_ids=board_ids,
        context_path=context_path,executable=native['board'],limits=runtime_limits['board'],config=config)
        for i,(b,r) in enumerate(zip(plan['boards'],board_results))]
    evidence=provider.generation_evidence(local['preflop_state'],plan,records)
    target=dict(plan=plan,evidence=evidence,recipe=provider.recipe)
    save(folder/'board-generation-evidence.json',target)
    delta=local['preflop_state'].step(plan,evidence,played_policy=pre)
    for path,h in native_ids.items():
        if sha(path)!=h: raise ValueError('Native/context source changed during collection')
    result=dict(method=METHOD,context_sha256=key,model_sha256=used['sha256'],registry_sha256=registry.sha256,
        resources_sha256=resources_sha,seconds=time.monotonic()-began,subbatches=subbatches,
        query_invocations=query_invocations,board_results=board_results,peak_pending=peak_pending,
        reservoirs=[r.summary() for r in local['reservoirs']],native_identities=native_ids,
        cumulative_state_sha256=local['preflop_state'].document()['state_sha256'],
        update_delta=local['preflop_state'].encoded(delta),source_generation=_artifact_ref(folder/'source-generation.json'),
        board_evidence=_artifact_ref(folder/'board-generation-evidence.json'),runtime_limits=runtime_limits)
    save(folder/'collection.json',result); on_stage('context-complete',key)
    return result,target


def update(folder, objects, state, config, registry, resources, *, inputs, cache, native,
           guard, runtime_limits, workers=2, board_workers=1, batch_prefix,
           on_stage=lambda stage,key=None:None):
    guard(); began=time.monotonic(); checkpoint.validate_state(objects,state,config,registry,resources)
    if (set(inputs)!=set(registry.fit_contexts) or set(native)!={'bridge','trace','river','board'}
            or set(runtime_limits)!={'board','river'}):
        raise ValueError('All fitted games, typed native tools and explicit worker limits required')
    runtime_limits=dict(board=board_workers_api._limits(runtime_limits['board']),
                        river=river_workers_api.runtime(runtime_limits['river']))
    verify_sources(config)
    folder=Path(folder).resolve(); folder.mkdir(parents=True,exist_ok=False)
    used=state['next_model']; model_source=storage.read_object(objects,used).decode()
    staged=dict(contexts=copy.deepcopy(state['contexts']),collected_against={},board_targets={})
    collections=[]; on_stage('staged')
    for key in registry.fit_contexts:
        guard(); record,target=collect(folder/key,staged['contexts'][key],config,registry,resources,key=key,
            model_source=model_source,used=used,inputs=inputs[key],cache=cache,native=native,guard=guard,
            workers=workers,board_workers=board_workers,runtime_limits=runtime_limits,
            batch_prefix=batch_prefix,on_stage=on_stage)
        collections.append(record); staged['collected_against'][key]=used['sha256']; staged['board_targets'][key]=target
    on_stage('all-contexts-collected'); networks=[]; receipts=[]; metrics=[]
    generation=state['completed_cycles']+1
    for actor in (0,1):
        network,receipt,metric=fit(registry,staged['contexts'],resources,config,player=actor,
            generation=generation,collected_against=used['sha256'],guard=guard)
        networks.append(network); receipts.append(receipt); metrics.append(metric)
    on_stage('fits-complete'); verify_sources(config)
    candidate,reference=checkpoint.complete_cycle(objects,state,staged,config,registry,resources,
        networks=networks,fit_receipts=receipts,on_stage=lambda stage:on_stage(stage))
    result=dict(format=1,method=METHOD,completed_cycles=candidate['completed_cycles'],used_model=used,
        next_model=candidate['next_model'],checkpoint=reference,collections=collections,
        fit_receipts=receipts,fits=metrics,seconds=time.monotonic()-began,
        config_sha256=checkpoint.hash_document(config),registry_sha256=registry.sha256,
        resources_sha256=digest(resources),native_paths={k:str(Path(p).resolve()) for k,p in native.items()},
        workers=workers,board_workers=board_workers,runtime_limits=runtime_limits)
    save(folder/'metrics.json',result)
    # Caller publishes a resume pointer only after authenticating this complete
    # metrics/checkpoint pair. Immutable orphan objects remain evidence.
    return candidate,reference,result
