"""One bounded native joint training cycle; no scientific model comparison."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',
                  CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONDONTWRITEBYTECODE='1')
import copy
import gc
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback
import numpy as np
import psutil
import torch
import stack_context_training_checkpoint_v1 as cp
import stack_context_training_pipeline_v1 as pipeline
import stack_context_full_policy_v1 as full
import stack_context_current_policy_v1 as current
from stack_context_inputs_v1 import Registry,digest
from stack_context_relative_inputs_v1 import Registry as RelativeRegistry
from stack_context_board_targets_v1 import prepare,policy_rows,request
from stack_context_board_components_v1 import board_terms
from preflop_allin_matrix_v1 import AllinMatrix
from sampled_allin_protocol_v3 import AllinCache
from sampled_physical_root_evaluation_v1 import save,sha
from sampled_visible_hybrid_checkpoint_v1 import read_object,encoded
from storage_strategic_common_prior_20260920 import CLASSES
from weighted_physical_reservoir_v1 import ARRAYS
from board_root_accumulator_v1 import CHANCE
from river_weighted_overlay_ingest_v1 import METHOD
from board_prefix_publication_v1 import atomic_json
from board_study_storage_v1 import create,measure
from global_research_inventory_v3 import measure as inventory
from river_matched_training_pilot_v1 import ROOT,OUT,LOCK,OTHER,available,production_available,gpu_snapshot,memory_admitted

NAME='stack-context-native-cycle-control-v2';STORE=Path('S:/GTOpen-research')/NAME
REG,ATTEMPT,RESULT,FAILURE,STATUS=(OUT/(NAME+s+'.json') for s in ('-registration','-attempt','-result','-failure','-status'))
GEOMETRY=Path('S:/GTOpen-research/stack-geometry-control-v1')
QUERIES=Path('S:/GTOpen-research/stack-context-model-control-v1')
OLD=Path('S:/GTOpen-research/stack-context-full-control-v1')
DEPTHS=(20,40,60,100,150,200,400)


def read(path):return json.loads(Path(path).read_bytes())


def fingerprint(state):
    records=dict(completed_cycles=state['completed_cycles'],played_bank=state['played_bank'],next_model=state['next_model'],contexts={})
    for key,s in state['contexts'].items():
        reservoirs=[]
        for r in s['reservoirs']:
            arrays={n:hashlib.sha256(getattr(r,n).tobytes()).hexdigest() for n in ARRAYS}
            reservoirs.append(dict(summary=r.summary(),rng=r.rng.bit_generator.state,arrays=arrays))
        records['contexts'][key]=dict(sampler=s['sampler'].checkpoint(),action_rng=s['action_rng'].bit_generator.state,
            reservoirs=reservoirs,root=s['root_regret_state'].document(),exact=s['exact_btn_state'].document())
    return hashlib.sha256(encoded(records)).hexdigest()


def infer_capture(engine,prepared):
    original=current.policy;raw=[]
    def capture(scores,arity):raw.append(scores.copy());return original(scores,arity)
    current.policy=capture
    try:p=engine.infer(prepared)
    finally:current.policy=original
    if len(raw)!=1:raise ValueError('One current-policy score conversion required')
    return raw[0],p


def parity(entries,guard):
    guard()
    proof=read(OUT/'stack-context-native-cycle-control-v1-parity-readback.json')
    registration=OUT/'stack-context-native-cycle-control-v1-registration.json'
    failure=OUT/'stack-context-native-cycle-control-v1-failure.json'
    if not proof['complete'] or not proof['passed'] or proof['training_started'] or proof['registration_sha256']!=sha(registration) or proof['failure_sha256']!=sha(failure):
        raise ValueError('Completed independently verified pre-training parity evidence required')
    if {(r['width'],r['depth']) for r in proof['records']}!={(w,d) for w in (362,387) for d in DEPTHS}:
        raise ValueError('Incomplete parity coverage')
    for width,kind in ((362,Registry),(387,RelativeRegistry)):
        if read(OLD/f'{width}-fixture.json')['registry']!=kind(entries).manifest:raise ValueError('Changed parity registry')
    for r in proof['records']:
        if sha(r['artifact'])!=r['sha256'] or max(r['errors'].values())>1e-10:raise ValueError('Changed or failed parity evidence')
    return proof['records']

def inputs_and_resources(entries,prepared):
    registry=RelativeRegistry(entries);resources={};inputs={};contexts={}
    for i,key in enumerate(registry.fit_contexts):
        record=prepared['contexts'][key];source=registry.source(key)
        matrix=AllinMatrix(read(record['matrix']),source)
        root=dict(context_sha256=key,matrix_sha256=record['matrix_sha256'],entry_mass=matrix.bb_mass.tolist(),
                  physical_budget=169,boards_per_generation=1,board_seed=9300800+i,chance=CHANCE)
        resources[key]=dict(catalog_source=Path(record['initial_catalog']).read_text(),matrix_sha256=record['matrix_sha256'],
                            entry_mass=matrix.btn_mass.tolist(),root_config=root)
        inputs[key]=dict(context_path=record['context_path'],matrix=record['matrix'],physical_catalog=record['physical_catalog'],
                         physical_catalog_sha256=record['artifacts'][record['physical_catalog']])
        contexts[key]=dict(sampler_seed=9300900+i,action_seed=9301000+i,reservoir_seeds=[9301100+2*i,9301101+2*i],
            reservoir_capacity=4096,deals_per_generation=169,deals_per_subbatch=13,query_limit=1000000,
            board_root=root,allin_cache_sha256=prepared['cache_sha256'],river_targets=dict(method=METHOD,K=64))
    return registry,resources,inputs,contexts


def main():
    if any(p.exists() for p in (REG,ATTEMPT,RESULT,FAILURE,STORE,LOCK,OTHER)):raise ValueError('Existing attempt or owner')
    ready,admission=available()
    if not ready:print(json.dumps(dict(deferred=True,admission=admission)));return
    result_path=OUT/'stack-context-resources-v1-result.json';proof_path=OUT/'stack-context-resources-v1-readback.json'
    prepared=read(result_path);proof=read(proof_path)
    if not proof['passed'] or not proof['complete'] or proof['result_sha256']!=sha(result_path):raise ValueError('Prepared resources are unverified')
    paths={Path(__file__).resolve(),result_path,proof_path,OUT/'STACK-CONTEXT-NATIVE-CYCLE-CONTROL-V2-PLAN.md'}
    prior_path=OUT/'stack-context-full-control-v1-registration.json';prior=read(prior_path)['inputs'];paths.add(prior_path)
    prior_result=OUT/'stack-context-full-control-v1-result.json';prior_artifacts=read(prior_result)['artifacts'];paths.add(prior_result)
    entries=[]
    for d in DEPTHS:
        context=GEOMETRY/'fixtures'/f'stack-{d}-context.json';public=GEOMETRY/f'stack-{d}-public.json';queries=QUERIES/f'stack-{d}-queries.json'
        for p in (context,public,queries):
            if sha(p)!=prior[str(p)]:raise ValueError('Changed retained context or queries')
            paths.add(p)
        entries.append(dict(name=f'{d}bb',split='heldout' if d in (60,150) else 'fit',context_source=context.read_text(),public_document=read(public)))
    for width in (362,387):
        p=OLD/f'{width}-fixture.json'
        if sha(p)!=prior_artifacts[str(p)]:raise ValueError('Changed parity fixture')
        paths.add(p)
    for record in prepared['contexts'].values():
        for p,h in record['artifacts'].items():
            if sha(p)!=h:raise ValueError('Resource artifact changed')
            paths.add(Path(p))
    review_path=OUT/'stack-context-complete-allin-cache-v1-readback.json';review=read(review_path);paths.add(review_path)
    if not review['passed'] or review['cache_sha256']!=prepared['cache_sha256']:raise ValueError('Exact cache proof mismatch')
    cache_path=Path(review['cache_artifact']);paths.add(cache_path)
    native={k:ROOT/'target/release/examples'/v for k,v in dict(bridge='hu_sampled_allin_bridge_v3.exe',trace='hu_sampled_action_trace_v2.exe',
        integration='hu_sampled_profile_allin_evaluation_v1.exe',river='hu_river_two_stage_stream_v1.exe',board='hu_fixed_board_tree_v1.exe').items()}
    paths.update(native.values())
    for p in native.values():paths.add(ROOT/'crates/solver/examples'/(p.stem+'.rs'))
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py':paths.add(Path(p))
    parity_proof_path=OUT/'stack-context-native-cycle-control-v1-parity-readback.json'
    parity_proof=read(parity_proof_path)
    paths.update((parity_proof_path,OUT/'stack-context-native-cycle-control-v1-registration.json',OUT/'stack-context-native-cycle-control-v1-failure.json'))
    paths.update(Path(r['artifact']) for r in parity_proof['records'])
    identities={str(p):sha(p) for p in sorted(paths)}
    registry,resources,inputs,contexts=inputs_and_resources(entries,prepared)
    config=dict(format=1,checkpoint_type=cp.TYPE,registry_sha256=registry.sha256,representation=registry.manifest['representation'],
        target_units=cp.SCALE,fit_runtime=cp.RUNTIME,objective_method=cp.METHOD,initialization=cp.INITIALIZATION,optimizer=cp.OPTIMIZER,
        device='cuda',current_policy_inference='float64-widened-float32-weights-v1',fit_steps=16,chunk_size=512,learning_rate=.003,
        fit_seed_base=9301201,context_order=list(registry.fit_contexts),context_weights={k:1/len(registry.fit_contexts) for k in registry.fit_contexts},
        contexts=contexts,source_identities=identities)
    cp.require_config(config,registry,resources)
    accounting=inventory()
    if sum(r['allocated_file_bytes'] for r in accounting)+4_000_000_000>800_000_000_000:raise ValueError('Global allocated cap')
    spec=dict(inputs=identities,config=config,maximum_seconds=2400,maximum_new_bytes=4_000_000_000,maximum_cuda_bytes=2_000_000_000,
              workers=2,board_workers=1,raw_tolerance=1e-10,scientific_training=False,quality_qualification=False)
    with LOCK.open('x') as stream:stream.write(str(os.getpid()))
    began=time.monotonic()
    try:
        create(STORE);save(REG,spec);save(STORE/'admission.json',accounting)
        save(ATTEMPT,dict(pid=os.getpid(),process_created=psutil.Process().create_time(),registration_sha256=sha(REG),admission=admission))
        torch.set_num_threads(1);torch.use_deterministic_algorithms(True);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        torch.cuda.set_per_process_memory_fraction(2_000_000_000/torch.cuda.get_device_properties(0).total_memory)
        last_probe=0.;last_size=0.;last_gpu=0.
        def guard():
            nonlocal last_probe,last_size,last_gpu
            now=time.monotonic()
            if now-began>2400 or torch.cuda.memory_reserved()>2_000_000_000:raise RuntimeError('Control runtime/CUDA bound')
            if now-last_probe>2:
                if not production_available() or OTHER.exists() or psutil.virtual_memory().available<24_000_000_000 or psutil.disk_usage('S:/').free<40_000_000_000:
                    raise RuntimeError('Control yields to production/resource pressure')
                last_probe=now
            if now-last_size>20:
                if sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())>4_000_000_000:raise RuntimeError('Control storage cap')
                last_size=now
            if now-last_gpu>30:
                torch.cuda.synchronize();time.sleep(1.2)
                while True:
                    g=gpu_snapshot()
                    if g['utilization_percent']<65 and memory_admitted(g['free_bytes'],torch.cuda.memory_reserved()):break
                    if time.monotonic()-began>2400 or not production_available():raise RuntimeError('Control admission wait limit/production')
                    time.sleep(1)
                last_gpu=time.monotonic()
        def stage(name,key=None):
            atomic_json(STATUS,dict(stage=name,context_sha256=key,elapsed_seconds=time.monotonic()-began,pid=os.getpid()),replace=True)
            print(json.dumps(dict(stage=name,context_sha256=key)),flush=True)
        stage('verified-cached-parity-reused');parities=parity(entries,guard)
        objects=STORE/'objects';objects.mkdir();state=cp.initialize(objects,config,registry,resources)
        initial=cp.save_checkpoint(objects,state,config,registry,resources);before=fingerprint(state)
        save(STORE/'initial.json',dict(checkpoint=initial,model=state['next_model'],fingerprint=before))
        cache=AllinCache(cache_path,review['cache_sha256']);stage('native-joint-cycle')
        completed,reference,metrics=pipeline.update(STORE/'cycle-1',objects,state,config,registry,resources,inputs=inputs,
            cache=cache,native=native,guard=guard,workers=2,board_workers=1,batch_prefix=NAME,on_stage=stage)
        if fingerprint(state)!=before:raise ValueError('Caller state changed before complete publication')
        loaded=cp.restore_checkpoint(objects,reference,config,registry,resources)
        if fingerprint(loaded)!=fingerprint(completed):raise ValueError('Complete checkpoint restore differs')
        played=full.read_model(objects,completed['next_model'],registry,resources)
        staged=dict(contexts=completed['contexts'],collected_against={k:state['next_model']['sha256'] for k in registry.fit_contexts})
        for boundary in ('before-model-publication','before-checkpoint-publication'):
            def interrupt(name):
                if name==boundary:raise InterruptedError(boundary)
            try:cp.complete_cycle(objects,state,staged,config,registry,resources,networks=played['shared']['networks'],on_stage=interrupt)
            except InterruptedError:pass
            else:raise ValueError('Publication interruption was not exercised')
            if fingerprint(state)!=before:raise ValueError('Interrupted publication altered original state')
        again,replayed=cp.complete_cycle(objects,state,staged,config,registry,resources,networks=played['shared']['networks'])
        if replayed!=reference or fingerprint(again)!=fingerprint(completed):raise ValueError('Retained transaction replay differs')
        stage('upstream-connectivity')
        key=next(k for k,v in prepared['contexts'].items() if v['depth']==20);record=next(r for r in metrics['collections'] if r['context_sha256']==key)
        source_model=read_object(objects,state['next_model']).decode()
        prep=prepare(model_source=source_model,registry=registry,context_sha256=key,resources=resources,
            physical_catalog_source=Path(inputs[key]['physical_catalog']).read_text(),matrix_source=Path(inputs[key]['matrix']).read_text())
        board_record=record['board_results'][0]['result'];tree=read(board_record['tree_artifact']);post=policy_rows(tree,prep['engine'])
        changed=0
        for branch,policies in zip(tree['branches'],post):
            for node,p in policies.items():
                observation=branch['nodes'][node]['observations'][0]
                if observation['phase']==3 and observation['actor']==1:p[:]=0.;p[:,0]=1.;changed+=len(p)
        req,ids=request(prep,tree['board']);weights=[prep['sampler'].weights[p,i] for p,i in enumerate(ids)]
        altered=board_terms(prep['context'],tree,post,prep['pre'],weights,[CLASSES[i] for i in ids],prep['sampler'].masses[0],prep['class_mass'])
        original=np.asarray(board_record['record']['values']);difference=float(np.max(abs(altered-original)))
        if not changed or difference<=1e-8:raise ValueError('River intervention did not propagate to preflop values')
        save(STORE/'upstream-intervention.json',dict(context_sha256=key,tree_sha256=board_record['tree_sha256'],changed_rows=changed,
            original=original.tolist(),altered=altered.tolist(),maximum_root_value_difference=difference,quality_claim=False))
        guard()
        for p,h in identities.items():
            if sha(p)!=h:raise ValueError('Registered input changed')
        size=measure(STORE)
        save(RESULT,dict(complete=True,passed=True,registration_sha256=sha(REG),parity=parities,checkpoint=reference,
            restored_fingerprint=fingerprint(loaded),initial_fingerprint=before,publication_replay=True,native_recollection_replay=False,
            completed_cycles=1,fitting_contexts=5,trained_representation=387,maximum_upstream_intervention_difference=difference,
            storage=size,seconds=time.monotonic()-began,peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved(),
            artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()},scientific_comparison=False,accuracy_qualified=False,production_modified=False))
        stage('complete');print(json.dumps(dict(passed=True,seconds=time.monotonic()-began)),flush=True)
    except BaseException as error:
        save(FAILURE,dict(error=repr(error),traceback=traceback.format_exc(),retry_allowed=False));raise
    finally:
        if LOCK.exists() and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':main()
