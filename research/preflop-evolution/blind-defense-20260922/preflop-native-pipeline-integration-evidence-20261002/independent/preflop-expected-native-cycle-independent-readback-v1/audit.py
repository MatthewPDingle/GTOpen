"""One retained-evidence audit of the completed bounded native software profile.

Never imports/invokes the profile runner, exports native data, starts workers,
fits a model, writes profile/repository files, or publishes a checkpoint. Replays
use the pinned qualified CPU target/transport components. This is independent
artifact orchestration/readback, not an independent poker payoff implementation
or evidence of improved scientific accuracy or convergence.
"""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1', OPENBLAS_NUM_THREADS='1',
    OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', NUMEXPR_NUM_THREADS='1',
    PYTHONDONTWRITEBYTECODE='1')
import copy
import itertools
import json
import math
from pathlib import Path
import sys
import time
import traceback
from unittest.mock import patch

AUDIT = Path(__file__).resolve().parent
STAGE = AUDIT.parent
TOOLS = Path(r'T:\Dev\GTOpen\tools\research')
sys.path.insert(0,str(STAGE)); sys.path.append(str(TOOLS))
import numpy as np
from threadpoolctl import threadpool_limits
import preflop_expected_training_pipeline_v1 as pipeline
import preflop_expected_training_checkpoint_v1 as checkpoint
import preflop_expected_training_fit_v1 as fit_api
import preflop_expected_native_execution_v1 as execution
import preflop_expected_river_workers_v1 as river
from preflop_expected_native_targets_v2 import FrozenExpectedTargets
from preflop_expected_policy_v1 import ExpectedPolicy
from stack_context_inputs_v1 import Registry
from weighted_deal_binding_v1 import DealWeightGeneration
from sampled_allin_protocol_v3 import AllinCache, policy_document
from weighted_training_v1 import first_action_view
from exact_initial_training_ingest_v2 import InitialTargets
import sampled_visible_hybrid_checkpoint_v1 as storage
from board_root_accumulator_v1 import digest

PROFILE = Path(r'S:\GTOpen-research\preflop-expected-native-cycle-profile-v1')
EXPECTED_REGISTRATION = '22cb43489f0c9be4c4625639cf778ff7ac1b444765e22e376f025a6e21ac9e4a'
EXPECTED_OWNER = dict(pid=113248,creation_time=1790919929.039893)
SCOPE = ('Independent retained-artifact readback using the pinned qualified CPU '
    'components. No native export, profile rerun, worker launch, GPU fit, science, '
    'profile/repository write or publication. No independent poker payoff '
    'implementation and no improved accuracy/convergence claim.')
READS = {}; RECEIPTS = {}; CHECKS = []


def write(path,document):
    with Path(path).open('xb') as stream:
        stream.write((json.dumps(document,sort_keys=True,separators=(',', ':'),
            allow_nan=False)+'\n').encode('utf-8'))


def require(condition,message):
    if not condition: raise ValueError(message)


def read(path,expected=None,*,owned=False):
    path=Path(path).resolve()
    if owned: require(path.is_relative_to(PROFILE.resolve()),'Artifact escaped the retained profile: '+str(path))
    identity=execution.sha(path)
    if expected is not None: require(identity==expected,'Artifact/source identity changed: '+str(path))
    READS[str(path)]=identity
    return json.loads(path.read_bytes())


def ref(reference):
    require(set(reference)=={'path','sha256'},'Complete retained artifact reference required')
    return read(reference['path'],reference['sha256'],owned=True)


def note(stage,**details):
    value=dict(stage=stage,seconds=time.monotonic()-BEGAN,**details)
    CHECKS.append(value); print(json.dumps(value,sort_keys=True),flush=True)


def native(invocation,*,executable,arguments,identities,stdin=None,caller=None):
    for name in ('receipt_path','stdout_path','stderr_path'):
        require(Path(invocation[name]).resolve().is_relative_to(PROFILE.resolve()),'Process evidence escaped the retained profile')
    receipt=execution.verify_native(invocation,executable=executable,arguments=arguments,
        expected_identities=identities,stdin_path=stdin)
    if caller is not None: require(receipt['caller']==caller,'Native export caller differs from the recorded owning process')
    require(ATTEMPT['started_unix']<=receipt['started_unix']<=receipt['terminal_unix']<=RELEASED['terminal_unix'],
        'Native invocation escaped the retained attempt/release interval')
    require(receipt['process']['pid']!=receipt['caller']['pid'],'Native child has the caller PID')
    require(receipt['returncode']==0 and receipt['outcome']=='success','Native export lacks successful owned termination')
    path=str(Path(invocation['receipt_path']).resolve())
    require(path not in RECEIPTS,'Native invocation receipt was replayed as another work item')
    RECEIPTS[path]=dict(sha256=invocation['receipt_sha256'],argv=receipt['argv'],
        caller=receipt['caller'],process=receipt['process'],returncode=receipt['returncode'],
        started_unix=receipt['started_unix'],terminal_unix=receipt['terminal_unix'],
        stdout=receipt['stdout'],stderr=receipt['stderr'])
    return receipt


def restore_events(document):
    return [(event['player'],(tuple(event['row']['keys']),
        np.asarray(event['row']['active'],dtype=np.uint16),event['row']['arity'],
        np.asarray(event['row']['advantages'],dtype=np.float64)),
        event['iteration'],event['deal_weight']) for event in document['events']]


def compare_local(replayed,restored):
    require(checkpoint.local_fit_identity(replayed)==checkpoint.local_fit_identity(restored),
        'Complete replayed target/reservoir identity differs from the final checkpoint')
    require(replayed['sampler'].checkpoint()==restored['sampler'].checkpoint(),'Sampler RNG/state differs after replay')
    require(replayed['action_rng'].bit_generator.state==restored['action_rng'].bit_generator.state,
        'Action RNG state differs after source-order replay')
    require(replayed['preflop_state'].document()==restored['preflop_state'].document(),
        'Every cumulative preflop target/state differs after board replay')
    for left,right in zip(replayed['reservoirs'],restored['reservoirs']):
        require((left.capacity,left.player,left.seen)==(right.capacity,right.player,right.seen),
            'Retained reservoir ownership/capacity/visit count differs')
        require(left.rng.bit_generator.state==right.rng.bit_generator.state,'Retention RNG differs after ordered insertion')
        for name in checkpoint.ARRAYS:
            require(np.array_equal(getattr(left,name),getattr(right,name)),'Retained reservoir array differs: '+name)
        require(np.all(right.keys[:right.size,0]>=1<<63),'A sampled preflop visit entered retained training')


def audit():
    global ATTEMPT,RELEASED
    spec=read(PROFILE/'registration.json',EXPECTED_REGISTRATION,owned=True)
    result=read(PROFILE/'result.json',owned=True)
    ATTEMPT=read(PROFILE/'attempt.json',result['attempt_sha256'],owned=True)
    RELEASED=read(PROFILE/'released.json',owned=True)
    require(result['passed'] is True and result['registration_sha256']==EXPECTED_REGISTRATION,
        'Terminal result is not the identified successful profile')
    require(not (PROFILE/'failure.json').exists(),'A terminal failure exists alongside the passed result')
    require(dict(pid=ATTEMPT['pid'],creation_time=ATTEMPT['process_created'])==EXPECTED_OWNER,
        'Attempt process PID/creation differs from the identified profile owner')
    require(dict(pid=RELEASED['pid'],creation_time=RELEASED['process_created'])==EXPECTED_OWNER,
        'Release process differs from the exact attempt owner')
    require(ATTEMPT['process_created']<=ATTEMPT['started_unix']<RELEASED['terminal_unix']<=ATTEMPT['deadline_unix'],
        'Attempt/release timestamps do not form a bounded completed interval')
    require(ATTEMPT['registration_sha256']==EXPECTED_REGISTRATION and ATTEMPT['store']==str(PROFILE),
        'Attempt lacks exact registration/store ownership')
    runner=STAGE/'preflop_expected_native_cycle_profile_v1.py'
    require(ATTEMPT['argv']==[str(runner),'--run'] and ATTEMPT['source_sha256']==spec['source_sha256']==execution.sha(runner),
        'Recorded profile command/source differs')
    require(spec['cycles']==result['completed_cycles']==1 and result['context_count']==1 and result['starting_stack']==20,
        'Profile exceeded the declared one-context/one-cycle scope')
    require(spec['scientific_accuracy_qualified'] is False and result['scientific_accuracy_qualified'] is False
        and result['production_changed'] is False,'Software-only qualification scope changed')
    pins=spec['config']['source_identities']
    for path,identity in pins.items():
        require(str(Path(path).resolve())==path and execution.sha(path)==identity,'Registered source/executable/input changed: '+path)
        READS[path]=identity
    require(len(pins)==127,'Unexpected full registered pin count')
    config,resources=spec['config'],spec['resources']; registry=Registry(spec['entries'])
    checkpoint.require_config(config,registry,resources); pipeline.verify_sources(config)
    require(len(registry.fit_contexts)==1 and len([e for e in spec['entries'] if e['split']=='heldout'])==2,
        'Fitted/held-out registry split changed')
    for key,item in spec['inputs'].items():
        require(Path(item['context_path']).read_bytes().decode('utf-8')==registry.source(key),'Exact registered context bytes changed')
        require(Path(item['matrix']).read_bytes().decode('utf-8')==resources[key]['matrix_source'],'Exact terminal matrix bytes changed')
        require(Path(item['physical_catalog']).read_bytes().decode('utf-8')==resources[key]['physical_catalog_source'],
            'Exact complete physical catalog bytes changed')
        for name in ('context_path','matrix','physical_catalog'):
            require(str(Path(item[name]).resolve()) in pins,'Collection input is absent from registered full pins')
    for name,path in spec['native'].items(): require(pins.get(path)==execution.sha(path),'Native executable pin missing: '+name)
    require(pins.get(spec['cache_artifact'])==spec['cache_sha256']==execution.sha(spec['cache_artifact']),
        'Exact all-in cache registration changed')
    inventory=spec['storage_admission']
    require(read(inventory['path'],inventory['identity'])==inventory['snapshot'],'Original allocated-storage admission snapshot changed')
    note('registered-source-input-process-pins-verified',source_pins=len(pins),owner=EXPECTED_OWNER)

    objects=PROFILE/'objects'; initial_pointer=read(PROFILE/'initial-complete-checkpoint.json',owned=True)
    require(initial_pointer['config_sha256']==checkpoint.hash_document(config),'Initial complete pointer config changed')
    initial=checkpoint.restore_checkpoint(objects,initial_pointer['checkpoint'],config,registry,resources)
    final=checkpoint.restore_checkpoint(objects,result['checkpoint'],config,registry,resources)
    require(initial['completed_cycles']==0 and initial['played_bank']==[],'Initial restart boundary is not generation zero')
    require(final['completed_cycles']==1 and final['played_bank']==[initial['next_model']],
        'Final played bank includes the wrong model or final unplayed model')
    require(final['next_model']!=initial['next_model'],'Final unplayed model pointer did not advance')
    metrics=read(PROFILE/'cycle-0001/metrics.json',result['metrics_sha256'],owned=True)
    require(metrics['checkpoint']==result['checkpoint'] and metrics['used_model']==initial['next_model']
        and metrics['next_model']==final['next_model'] and metrics['completed_cycles']==1,'Stored complete metrics/pointers differ')
    require(metrics['config_sha256']==checkpoint.hash_document(config) and metrics['registry_sha256']==registry.sha256
        and metrics['resources_sha256']==digest(resources),'Metrics config/registry/resources differ')
    require(metrics['native_paths']==spec['native'] and metrics['workers']==spec['workers']
        and metrics['board_workers']==spec['board_workers'] and metrics['runtime_limits']==spec['runtime_limits'],
        'Complete metrics invocation/runtime scope differs from registration')
    require(metrics['fits']==result['fit_metrics'],'Terminal fit metrics differ from the complete metrics')
    model_source=storage.read_object(objects,initial['next_model']).decode('utf-8')
    final_model=json.loads(storage.read_object(objects,final['next_model']))
    replay=copy.deepcopy(initial); targets={}; board_details=[]; physical_details=[]
    require(len(metrics['collections'])==len(registry.fit_contexts),'Missing complete fitted context collection')
    note('initial-and-final-checkpoints-restored',initial_checkpoint=initial_pointer['checkpoint'],final_checkpoint=result['checkpoint'])

    for key,collection in zip(registry.fit_contexts,metrics['collections']):
        folder=PROFILE/'cycle-0001'/key; source=registry.source(key); c=config['contexts'][key]
        require(read(folder/'collection.json',owned=True)==collection,'Complete saved collection differs from metrics')
        require(collection['context_sha256']==key and collection['registry_sha256']==registry.sha256
            and collection['model_sha256']==initial['next_model']['sha256']
            and collection['resources_sha256']==digest(resources),'Collection lost frozen model/context/resource identity')
        native_ids={str(Path(path).resolve()):pins[str(Path(path).resolve())]
            for path in (spec['inputs'][key]['context_path'],*spec['native'].values(),
                spec['inputs'][key]['matrix'],spec['inputs'][key]['physical_catalog'])}
        require(collection['native_identities']==native_ids,'Collection lost full native/input pins')
        provider=FrozenExpectedTargets(state=initial['contexts'][key]['preflop_state'],
            model_source=model_source,registry=registry,resources=resources)
        plan=initial['contexts'][key]['preflop_state'].plan()
        require(read(folder/'board-plan.json',owned=True)==plan,'Saved ordered board plan changed')
        require(read(folder/'played-target-recipe.json',owned=True)==provider.recipe,'Saved frozen played recipe changed')
        board_ids={str(Path(path).resolve()):pins[str(Path(path).resolve())]
            for path in (spec['inputs'][key]['context_path'],spec['native']['board'])}
        require(len(collection['board_results'])==len(plan['boards'])==2,'Two complete planned native boards required')
        records=[]
        for index,(board,wrapped) in enumerate(zip(plan['boards'],collection['board_results'])):
            value=read(wrapped['path'],wrapped['sha256'],owned=True)
            require(value==wrapped['result'],'Returned board result differs from retained bytes')
            request=read(value['request_artifact'],value['request_sha256'],owned=True)
            legal=[list(hand) for hand in itertools.combinations([card for card in range(52) if card not in board],2)]
            require(request==dict(board=board,hands=[legal,legal]) and len(legal)==1081,
                'Native board request omitted, reordered or changed private hands')
            invocation_ids={**board_ids,str(Path(value['request_artifact']).resolve()):value['request_sha256']}
            r=native(value['native_invocation'],executable=spec['native']['board'],
                arguments=[spec['inputs'][key]['context_path'],value['request_artifact']],identities=invocation_ids,
                caller=dict(pid=value['pid'],creation_time=value['creation_time']))
            record=pipeline.verify_board(wrapped,folder=folder/'board-targets',index=index,board=board,
                provider=provider,native_ids=board_ids,context_path=spec['inputs'][key]['context_path'],
                executable=spec['native']['board'],limits=spec['runtime_limits']['board'],config=config)
            records.append(record)
            board_details.append(dict(index=index,board=board,private_hands_per_actor=1081,
                values_sha256=record['values_sha256'],tree_sha256=record['tree_sha256'],
                caller=r['caller'],process=r['process'],replayed_from_raw_tree=True))
            note('native-board-replayed',draw_index=index,board=board)
        target=ref(collection['board_evidence'])
        require(target==dict(plan=plan,evidence=provider.generation_evidence(initial['contexts'][key]['preflop_state'],plan,records),
            recipe=provider.recipe),'Retained complete board generation differs from raw-tree replay')
        delta=replay['contexts'][key]['preflop_state'].step(plan,target['evidence'],played_policy=provider.played_preflop())
        require(collection['update_delta']==replay['contexts'][key]['preflop_state'].encoded(delta)
            and collection['cumulative_state_sha256']==replay['contexts'][key]['preflop_state'].document()['state_sha256'],
            'Saved preflop delta/state differs from full generation replay')
        targets[key]=target

        local=replay['contexts'][key]; sample=local['sampler'].sample(c['deals_per_generation'])
        require(sample==ref(collection['source_generation']),'Retained source deals differ from the initial sampler/RNG replay')
        weighted=DealWeightGeneration(sample,source); cache=AllinCache(spec['cache_artifact'],spec['cache_sha256'])
        engine=ExpectedPolicy(json.loads(model_source),registry,context_sha256=key,resources=resources,device='cpu')
        pre=provider.played_preflop(); context=json.loads(source); jam=context['nodes'][0]['children'][3]
        initial_targets=InitialTargets(resources[key]['matrix_source'],source,pre[0],pre[jam][:,1],
            matrix_sha256=local['preflop_state'].config['matrix_sha256'],generation=0)
        require(len(collection['subbatches'])==len(collection['query_invocations'])==13,'Thirteen ordered physical subbatches required')
        totals=np.zeros(2,dtype=np.int64); observed=np.zeros(2,dtype=np.int64); excluded=np.zeros(2,dtype=np.int64)
        stop=0; workers={}
        river_ids={str(Path(path).resolve()):pins[str(Path(path).resolve())]
            for path in (spec['inputs'][key]['context_path'],*[spec['native'][name] for name in ('bridge','trace','river')])}
        for chunk,(subbatch,query_call) in enumerate(zip(collection['subbatches'],collection['query_invocations'])):
            part=folder/f'batch-{chunk:03d}'; start=chunk*c['deals_per_subbatch']
            require(subbatch['chunk']==query_call['chunk']==chunk and start==stop,'Physical batch source order or coverage changed')
            value=ref(subbatch['result']); event_doc=read(part/'ordered-events.json',owned=True)
            batch=read(part/'batch.json',owned=True); queries=ref(query_call['queries']); policy=read(part/'policies.json',owned=True)
            seed=int(local['action_rng'].integers(0,2**63))
            expected_batch=cache.batch(dict(format=2,batch_id=f'{spec["name"]}-{key}-cycle-1-batch-{chunk}',
                query_limit=c['query_limit'],seed=seed,deals=sample['deals'][start:start+c['deals_per_subbatch']]))
            require(batch==expected_batch,'Original action-seed/cache/source-deal batch differs')
            binding=weighted.bind(queries,start)
            require(value['binding']==binding,'Retained physical source binding differs from actual ordered queries')
            _,stop=weighted.verify(binding)
            probabilities=engine.infer(engine.prepare(first_action_view(queries,jam+1)))
            require(policy==policy_document(queries,probabilities),'Retained physical policy differs from the frozen model')
            expected_inputs={name:execution.sha(part/(name+'.json')) for name in ('batch','queries','policies')}
            query_ids={spec['inputs'][key]['context_path']:pins[spec['inputs'][key]['context_path']],
                spec['native']['bridge']:pins[spec['native']['bridge']],str(part/'batch.json'):expected_inputs['batch']}
            native(query_call['invocation'],executable=spec['native']['bridge'],
                arguments=['queries',spec['inputs'][key]['context_path'],str(part/'batch.json'),'-',str(part/'queries.json')],
                identities=query_ids,caller=EXPECTED_OWNER)
            require(value['qualified_ingest_identity']==dict(cache_sha256=spec['cache_sha256'],targets=initial_targets.identity,
                source_generation_sha256=weighted.sha256),'Qualified ingestion/source generation identity differs')
            expected_roles=dict(context_path=spec['inputs'][key]['context_path'],executable=spec['native']['bridge'],
                trace_executable=spec['native']['trace'],river_executable=spec['native']['river'])
            require(value['native_roles']==expected_roles,'Physical worker executable/context roles differ')
            for path,identity in value['worker_source_identities'].items():
                require(pins.get(path)==identity,'Worker source differs from prospective full pins')
            for invocation in value['native_invocations']:
                receipt=native(invocation['result'],executable=invocation['executable'],arguments=invocation['arguments'],
                    identities=invocation['expected_identities'],stdin=invocation['stdin_path'])
                require(receipt['caller']['pid']==value['pid'],'Physical native invocation belongs to another worker')
                worker_identity=receipt['caller']; known=workers.setdefault(value['pid'],worker_identity)
                require(worker_identity==known,'One retained worker PID has inconsistent creation identities')
            value['events']=restore_events(event_doc)
            counts=river.commit(value,local['reservoirs'],expected_start=start,iteration=1,
                expected_context_sha256=key,expected_model_sha256=initial['next_model']['sha256'],
                expected_registry_sha256=registry.sha256,expected_resources_sha256=digest(resources),
                expected_native_identities=river_ids,expected_runtime_limits=spec['runtime_limits']['river'],
                expected_artifact_root=part,expected_input_identities=expected_inputs)
            require(counts==subbatch['counts']==value['counts'],'Committed postflop visit counts changed')
            require(value['observed_counts']==subbatch['observed_counts']
                and value['excluded_preflop_counts']==subbatch['excluded_preflop_counts']
                and value['river']==subbatch['river'],'Observed/excluded/river summary differs from complete metrics')
            totals+=counts; observed+=value['observed_counts']; excluded+=value['excluded_preflop_counts']
            physical_details.append(dict(chunk=chunk,start=start,stop=stop,deal_count=stop-start,
                postflop_counts=counts,observed_counts=value['observed_counts'],excluded_preflop_counts=value['excluded_preflop_counts'],
                worker=workers[value['pid']],native_invocations=len(value['native_invocations']),
                river_replacements=value['river']['replacements'],query_receipt=query_call['invocation']['receipt_sha256']))
        require(stop==c['deals_per_generation']==169 and np.array_equal(totals+excluded,observed),
            'Physical source or positive-tag observed visit accounting is incomplete')
        require(collection['reservoirs']==[r.summary() for r in local['reservoirs']],
            'Collection reservoir summaries differ from exact ordered replay')
        compare_local(local,final['contexts'][key])
        note('ordered-physical-reservoir-and-rng-replay-complete',batches=13,deals=169,
            postflop_visits=totals.tolist(),excluded_preflop_visits=excluded.tolist(),workers=list(workers.values()))

    staged=dict(contexts=replay['contexts'],collected_against={key:initial['next_model']['sha256'] for key in registry.fit_contexts},
        board_targets=targets)
    checkpoint.require_fits(metrics['fit_receipts'],final_model['shared']['networks'],staged,initial,config,registry,resources)
    objectives=[]
    for actor in (0,1):
        objective=fit_api.prepare(registry,replay['contexts'],resources,player=actor,
            context_weights=config['context_weights'],preflop_fraction=config['preflop_fraction'])
        receipt=metrics['fit_receipts'][actor]; metric=metrics['fits'][actor]
        require(objective['objective_sha256']==receipt['objective_sha256'],'Actual fit objective hash differs from complete retained replay')
        require(objective['contexts']==metric['contexts'] and len(objective['keys'])==metric['rows'],
            'Stored fit row/context metrics differ from the complete objective')
        require(all(type(metric[name]) in (int,float) and math.isfinite(metric[name]) and metric[name]>=0
            for name in ('loss_before','loss_after','seconds','tensor_bytes')),'Invalid stored fit metrics')
        objectives.append(dict(player=actor,objective_sha256=receipt['objective_sha256'],
            network_sha256=receipt['network_sha256'],rows=metric['rows'],steps=receipt['steps'],
            note='Fit receipt/output/objective verified; optimizer execution not repeated'))
    for key in registry.fit_contexts: compare_local(replay['contexts'][key],final['contexts'][key])
    lock=Path(r'T:\Dev\GTOpen\research\preflop-evolution\representative-coverage-20260919\running.lock')
    lock_present=lock.exists()
    if lock_present:
        owner=read(lock)
        require(not (owner.get('pid')==EXPECTED_OWNER['pid'] and owner.get('process_created')==EXPECTED_OWNER['creation_time']),
            'Exact profile owner retains the global research lock')
    require([v['stage'] for v in result['stages']]==['staged','physical-targets-complete','context-complete',
        'all-contexts-collected','fits-complete','before-model-publication','before-checkpoint-publication','checkpoint-published'],
        'Terminal complete-cycle stage order differs')
    require(all(a['seconds']<=b['seconds'] for a,b in zip(result['stages'],result['stages'][1:])),
        'Recorded completion stages are out of time order')
    require(result['seconds']<=spec['maximum_seconds'] and result['seconds']>=result['stages'][-1]['seconds'],
        'Recorded complete profile lifetime is invalid')
    for sample in result['resource_samples']:
        require(sample['available_ram_bytes']>=20_000_000_000 and sample['store_logical_bytes']<=spec['maximum_store_bytes'],
            'Recorded profile crossed the registered RAM/storage reserve')
        require(sample['gpu_memory_free_mib']>=8192
            and (not sample['own_gpu_quiescent_probe'] or sample['gpu_utilization_percent']<65),
            'Recorded sharing probe crossed the declared external GPU guard')
    files=sorted(path for path in PROFILE.rglob('*') if path.is_file())
    manifest={str(path.relative_to(PROFILE)):dict(bytes=path.stat().st_size,sha256=execution.sha(path)) for path in files}
    logical=sum(item['bytes'] for item in manifest.values())
    require(len(files)==809 and logical==1_278_992_546,'Retained file count/logical footprint changed')
    write(AUDIT/'retained-files.json',manifest)
    for path,identity in pins.items(): require(execution.sha(path)==identity,'Registered source changed during independent readback')
    require(read(PROFILE/'registration.json',EXPECTED_REGISTRATION,owned=True)==spec
        and read(PROFILE/'result.json',owned=True)==result,'Retained terminal control changed during readback')
    note('joint-fit-objective-pointers-release-and-full-manifest-verified',receipts=len(RECEIPTS),files=len(files),logical_bytes=logical)
    return dict(passed=True,scope=SCOPE,registration_sha256=EXPECTED_REGISTRATION,
        profile=str(PROFILE),owner=EXPECTED_OWNER,source_pin_count=len(pins),
        retained_file_count=len(files),retained_logical_bytes=logical,board_replays=board_details,
        physical_batches=physical_details,native_receipt_count=len(RECEIPTS),native_receipts=RECEIPTS,
        initial_checkpoint=initial_pointer['checkpoint'],final_checkpoint=result['checkpoint'],
        initial_model=initial['next_model'],final_model=final['next_model'],played_bank=final['played_bank'],
        joint_fit_objectives=objectives,exact_rng_and_retained_array_replay=True,
        sampled_preflop_rows_retained=False,profile_owner_lock_released=True,current_lock_present=lock_present,
        checkpoints_pointers_and_metrics_agree=True,scientific_accuracy_qualified=False,
        independent_poker_payoff_implementation=False,reads=READS,checks=CHECKS,
        retained_manifest_sha256=execution.sha(AUDIT/'retained-files.json'),
        audit_source_sha256=execution.sha(__file__),seconds=time.monotonic()-BEGAN,
        limitation='Completed-process evidence is read from retained owned-handle receipts; no live PID ancestry reconstruction or optimizer refit is attempted.')


if __name__=='__main__':
    BEGAN=time.monotonic()
    require(not (AUDIT/'result.json').exists() and not (AUDIT/'failure.json').exists(),
        'Preserve the existing one-shot independent audit result/failure')
    forbidden=AssertionError('Independent retained readback cannot execute native work, fit, or publish')
    try:
        with threadpool_limits(limits=1), \
                patch.object(execution,'run_native',side_effect=forbidden), \
                patch.object(pipeline,'run_native',side_effect=forbidden), \
                patch.object(pipeline,'update',side_effect=forbidden), \
                patch.object(pipeline,'board_pool',side_effect=forbidden), \
                patch.object(pipeline,'river_pool',side_effect=forbidden), \
                patch.object(fit_api,'fit',side_effect=forbidden), \
                patch.object(checkpoint,'complete_cycle',side_effect=forbidden), \
                patch.object(checkpoint,'initialize',side_effect=forbidden), \
                patch.object(checkpoint,'save_checkpoint',side_effect=forbidden), \
                patch.object(storage,'publish',side_effect=forbidden):
            outcome=audit()
        write(AUDIT/'result.json',outcome)
        print(json.dumps(dict(passed=True,seconds=outcome['seconds'],boards=len(outcome['board_replays']),
            physical_batches=len(outcome['physical_batches']),native_receipts=outcome['native_receipt_count'],
            logical_bytes=outcome['retained_logical_bytes'],result=str(AUDIT/'result.json')),sort_keys=True),flush=True)
    except BaseException as exc:
        write(AUDIT/'failure.json',dict(passed=False,scope=SCOPE,error_type=type(exc).__name__,message=str(exc),
            traceback=traceback.format_exc(),checks=CHECKS,reads=READS,audit_source_sha256=execution.sha(__file__)))
        raise
