"""Prospective bounded native pipeline software/resource qualification.

One initial uniform 20bb context cycle, real poker transport and two actual
short CUDA fits. This is neither an accuracy experiment nor a trained model for
deployment. Native artifacts/failures are retained; the started attempt cannot
be retried. Larger scientific budgets must be registered separately afterward.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',PYTHONDONTWRITEBYTECODE='1')
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time
import traceback

STAGE=Path(__file__).resolve().parent
TOOLS=Path(r'T:\Dev\GTOpen\tools\research')
sys.path.append(str(TOOLS))
import psutil
import numpy as np
import torch
from threadpoolctl import threadpool_limits
import preflop_expected_training_pipeline_v1 as pipeline
import preflop_expected_training_checkpoint_v1 as cp
from preflop_expected_regret_accumulator_v1 import PreflopExpectedRegrets
from stack_context_inputs_v1 import Registry
from sampled_allin_protocol_v3 import AllinCache
from bounded_parallel_evaluation_archive_v2 import production_available
import sampled_visible_hybrid_checkpoint_v1 as storage

ROOT=TOOLS.parents[1]; OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
POP=Path(r'S:\GTOpen-research\stack-context-population-v1')
NAME='preflop-expected-native-cycle-profile-v1'
STORE=Path(r'S:\GTOpen-research')/NAME
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
MAX_BYTES=8_000_000_000; MAX_SECONDS=3600
ALLOCATED_CAP=800_000_000_000


def write(path,value):
    path=Path(path)
    with path.open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n')
        stream.flush(); os.fsync(stream.fileno())


def read(path): return json.loads(Path(path).read_bytes())


def admission(inventory, *, expected=None):
    """Revalidate the actual recorded storage snapshot immediately at launch."""
    path=Path(inventory).resolve(); identity=pipeline.sha(path); snapshot=read(path)
    now=time.time(); observed=snapshot.get('observed_unix'); total=snapshot.get('allocated_total_bytes')
    roots=snapshot.get('roots',[])
    if (type(observed) not in (int,float) or not math.isfinite(observed)
            or not 0<=now-observed<=3600 or type(total) is not int or total<0
            or total+MAX_BYTES>ALLOCATED_CAP or snapshot.get('read_only') is not True
            or not isinstance(roots,list) or len(roots)!=3
            or {r.get('root') for r in roots} != {r'S:\GTOpen-research',r'T:\GTOpen-research',str(ROOT/'research')}
            or any(type(r.get('allocated_file_bytes')) is not int or r['allocated_file_bytes']<0 for r in roots)
            or sum(r['allocated_file_bytes'] for r in roots)!=total):
        raise ValueError('Fresh complete allocated-storage admission within the global cap required')
    result=dict(snapshot=snapshot,identity=identity,path=str(path))
    if expected is not None and result!=expected:
        raise ValueError('Recorded storage admission identity or content changed')
    return result


def gpu_snapshot():
    lines=subprocess.check_output(['nvidia-smi','--query-gpu=name,utilization.gpu,memory.used,memory.free',
        '--format=csv,noheader,nounits'],creationflags=subprocess.CREATE_NO_WINDOW,text=True,timeout=15).strip().splitlines()
    if len(lines)!=1: raise ValueError('One registered RTX 3090 required')
    name,*values=[v.strip() for v in lines[0].split(',')]
    if name!='NVIDIA GeForce RTX 3090' or len(values)!=3 or not all(v.isdigit() for v in values):
        raise ValueError('Registered GPU identity or numeric global telemetry unavailable')
    util,memory,free=map(int,values)
    return dict(gpu_name=name,gpu_utilization_percent=util,gpu_memory_used_mib=memory,gpu_memory_free_mib=free)


def specification():
    entries=[]; resources={}; inputs={}; pins={}
    def source(path):
        path=Path(path).resolve(); pins[str(path)]=pipeline.sha(path)
        return path.read_bytes().decode('utf-8')
    for depth,split in ((20,'fit'),(60,'heldout'),(150,'heldout')):
        folder=POP/f'stack-{depth}'; context=source(folder/'context.json')
        entries.append(dict(name=f'{depth}bb',split=split,context_source=context,public_document=json.loads(source(folder/'public.json'))))
        if split=='fit':
            key=hashlib.sha256(context.encode()).hexdigest(); physical=source(folder/'physical-catalog.json'); matrix=source(folder/'matrix.json')
            state=PreflopExpectedRegrets(context_source=context,matrix_source=matrix,generation_scale=169,
                boards_per_generation=2,board_seed=6100020)
            resources[key]=dict(physical_catalog_source=physical,physical_catalog_sha256=hashlib.sha256(physical.encode()).hexdigest(),
                               matrix_source=matrix,expected_config=state.config)
            inputs[key]=dict(context_path=str((folder/'context.json').resolve()),matrix=str((folder/'matrix.json').resolve()),
                physical_catalog=str((folder/'physical-catalog.json').resolve()),physical_catalog_sha256=resources[key]['physical_catalog_sha256'])
    registry=Registry(entries)
    review_path=OUT/'stack-context-complete-allin-cache-v1-readback.json'; review=json.loads(source(review_path))
    if not review.get('passed') or not review.get('complete') or review['canonical_keys']!=93769:
        raise ValueError('Complete exact all-in cache qualification required')
    cache_path=Path(review['cache_artifact']).resolve(); pins[str(cache_path)]=pipeline.sha(cache_path)
    if pins[str(cache_path)]!=review['cache_sha256']: raise ValueError('Qualified cache changed')
    native={k:ROOT/'target/release/examples'/v for k,v in dict(bridge='hu_sampled_allin_history_bridge_v1.exe',
        trace='hu_sampled_action_trace_v2.exe',river='hu_river_two_stage_stream_v1.exe',board='hu_fixed_board_tree_v1.exe').items()}
    old=json.loads(source(OUT/'stack-context-native-cycle-control-v4-registration.json'))
    for p in native.values():
        path=str(p.resolve()); pins[path]=pipeline.sha(p)
        if old['inputs'].get(path)!=pins[path]: raise ValueError('Native executable differs from previously qualified implementation')
        source(ROOT/'crates/solver/examples'/(p.stem+'.rs'))
    config=dict(format=1,checkpoint_type=cp.TYPE,execution_mode='software-control',registry_sha256=registry.sha256,
        representation=registry.manifest['representation'],target_units=cp.SCALE,fit_runtime=cp.RUNTIME,objective_method=cp.FIT_METHOD,
        preflop_fit_recipe=cp.DENSE_RECIPE,preflop_fraction=.25,initialization=cp.INITIALIZATION,optimizer=cp.OPTIMIZER,
        device='cuda',current_policy_inference='float64-widened-float32-weights-v1',fit_steps=4,chunk_size=512,
        learning_rate=.001,fit_seed_base=6500020,context_order=list(registry.fit_contexts),
        context_weights={k:1. for k in registry.fit_contexts},contexts={},source_identities=pins)
    for key in registry.fit_contexts:
        config['contexts'][key]=dict(sampler_seed=6200020,action_seed=6300020,reservoir_seeds=[6400020,6400021],
            reservoir_capacity=512,deals_per_generation=169,deals_per_subbatch=13,query_limit=1_000_000,
            expected_preflop=resources[key]['expected_config'],allin_cache_sha256=review['cache_sha256'],
            river_targets=dict(method=cp.RIVER_METHOD,K=64))
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).suffix=='.py' and Path(p).resolve().parent in (STAGE,TOOLS):
            pins[str(Path(p).resolve())]=pipeline.sha(p)
    cp.require_config(config,registry,resources); pipeline.verify_sources(config)
    limits=dict(board=dict(max_worker_seconds=MAX_SECONDS,native_timeout_seconds=120,max_output_bytes=2_000_000_000),
                river=dict(max_worker_seconds=MAX_SECONDS,native_timeout_seconds=120,river_native_timeout_seconds=60))
    spec=dict(format=1,name=NAME,purpose='Software/resource qualification only; not an accuracy or convergence trial',
        entries=entries,config=config,resources=resources,inputs=inputs,native={k:str(p.resolve()) for k,p in native.items()},
        cache_artifact=str(cache_path),cache_sha256=review['cache_sha256'],runtime_limits=limits,
        workers=3,board_workers=2,cycles=1,maximum_store_bytes=MAX_BYTES,maximum_seconds=MAX_SECONDS,
        global_allocated_cap_bytes=ALLOCATED_CAP,original_science_unchanged=True,
        scientific_accuracy_qualified=False,expected_gpu='NVIDIA GeForce RTX 3090',torch_version=torch.__version__,
        gpu_sharing='Quiesce own GPU for 1.2s every 30s; share light desktop use, yield at 65% external utilization or <8GiB free.',
        cancellation='Shared spawn event; cancel queued jobs and stop active native exports at cooperative guard checks.',
        source_sha256=pipeline.sha(__file__))
    return spec,registry,resources,config


def prepare(inventory):
    if STORE.exists(): raise ValueError('Preserve existing prepared profile/attempt')
    storage_admission=admission(inventory)
    if (psutil.disk_usage('S:/').free<40_000_000_000+MAX_BYTES
            or not production_available()): raise ValueError('Profile preparation resource reserve unavailable')
    spec,_,_,_=specification(); spec['storage_admission']=storage_admission
    STORE.mkdir(parents=True,exist_ok=False); write(STORE/'registration.json',spec)
    print(json.dumps(dict(prepared=True,registration=str(STORE/'registration.json'),sha256=pipeline.sha(STORE/'registration.json'))))


def run():
    registration=STORE/'registration.json'; spec=read(registration)
    actual,registry,resources,config=specification()
    if dict(spec,storage_admission=None)!=dict(actual,storage_admission=None): raise ValueError('Prepared native profile inputs changed')
    admission(spec['storage_admission']['path'],expected=spec['storage_admission'])
    if any((STORE/name).exists() for name in ('attempt.json','result.json','failure.json')):
        raise ValueError('A started software/native profile cannot be retried')
    if LOCK.exists() or OTHER.exists(): raise ValueError('Another research owner has priority')
    if psutil.disk_usage('S:/').free<40_000_000_000+MAX_BYTES or psutil.virtual_memory().available<28_000_000_000:
        raise ValueError('Native profile reserves unavailable')
    if not production_available(): raise ValueError('Production has priority')
    process=psutil.Process(); lock=dict(format=1,pid=process.pid,process_created=process.create_time(),name=NAME,
        registration_sha256=pipeline.sha(registration),store=str(STORE),source_sha256=pipeline.sha(__file__))
    write(LOCK,lock); lock_hash=pipeline.sha(LOCK); began=time.monotonic(); last=0.; last_gpu=0.; stages=[]; measured=[]; outcome=False
    def guard():
        nonlocal last,last_gpu
        now=time.monotonic()
        if now-began>MAX_SECONDS: raise TimeoutError('Prospective software profile deadline; no retry')
        if now-last>=3:
            if not production_available() or OTHER.exists() or pipeline.sha(LOCK)!=lock_hash:
                raise RuntimeError('Production or another research owner needs priority')
            if psutil.virtual_memory().available<20_000_000_000 or psutil.disk_usage('S:/').free<40_000_000_000:
                raise RuntimeError('Profile RAM/disk reserve exhausted')
            used=sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())
            if used>MAX_BYTES: raise RuntimeError('Prospective profile artifact ceiling exceeded')
            quiescent=now-last_gpu>=30
            if quiescent:
                if torch.cuda.is_initialized(): torch.cuda.synchronize()
                time.sleep(1.2)
            telemetry=gpu_snapshot()
            if telemetry['gpu_memory_free_mib']<8192: raise RuntimeError('GPU reserve needed by another application')
            if quiescent:
                last_gpu=time.monotonic()
                if telemetry['gpu_utilization_percent']>=65:
                    raise RuntimeError('Heavy external GPU use has priority during own-work quiescent probe')
            measured.append(dict(seconds=now-began,rss_bytes=process.memory_info().rss,available_ram_bytes=psutil.virtual_memory().available,
                store_logical_bytes=used,own_gpu_quiescent_probe=quiescent,**telemetry))
            last=now
    def stage(name,key=None):
        stages.append(dict(stage=name,context_sha256=key,seconds=time.monotonic()-began))
        print(json.dumps(stages[-1]),flush=True)
    try:
        write(STORE/'attempt.json',dict(**lock,argv=sys.argv,started_unix=time.time(),deadline_unix=time.time()+MAX_SECONDS,
            torch_threads=4,TF32=False,workers=spec['workers'],board_workers=spec['board_workers']))
        torch.set_num_threads(4); torch.backends.cuda.matmul.allow_tf32=False; torch.backends.cudnn.allow_tf32=False
        torch.cuda.reset_peak_memory_stats(); guard()
        cache=AllinCache(spec['cache_artifact'],spec['cache_sha256']); objects=STORE/'objects'
        with threadpool_limits(limits=4):
            previous=cp.initialize(objects,config,registry,resources)
            initial=cp.save_checkpoint(objects,previous,config,registry,resources)
            write(STORE/'initial-complete-checkpoint.json',dict(checkpoint=initial,config_sha256=cp.hash_document(config)))
            candidate,reference,metrics=pipeline.update(STORE/'cycle-0001',objects,previous,config,registry,resources,
                inputs=spec['inputs'],cache=cache,native=spec['native'],guard=guard,runtime_limits=spec['runtime_limits'],
                workers=spec['workers'],board_workers=spec['board_workers'],batch_prefix=NAME,on_stage=stage)
            restored=cp.restore_checkpoint(objects,reference,config,registry,resources)
            if (restored['next_model']!=candidate['next_model'] or restored['played_bank']!=[previous['next_model']]
                    or restored['completed_cycles']!=1): raise ValueError('Complete native cycle restart mismatch')
            for key in registry.fit_contexts:
                if cp.local_fit_identity(restored['contexts'][key])!=cp.local_fit_identity(candidate['contexts'][key]):
                    raise ValueError('Restored actual retained/native target data changed')
                a=restored['contexts'][key]; b=candidate['contexts'][key]
                if (a['sampler'].checkpoint()!=b['sampler'].checkpoint()
                        or a['action_rng'].bit_generator.state!=b['action_rng'].bit_generator.state
                        or any(r.rng.bit_generator.state!=s.rng.bit_generator.state for r,s in zip(a['reservoirs'],b['reservoirs']))):
                    raise ValueError('Actual sampler/action/retention restart state changed')
        guard(); pipeline.verify_sources(config)
        result=dict(passed=True,scope=spec['purpose'],registration_sha256=pipeline.sha(registration),
            attempt_sha256=pipeline.sha(STORE/'attempt.json'),metrics_sha256=pipeline.sha(STORE/'cycle-0001/metrics.json'),
            checkpoint=reference,stages=stages,resource_samples=measured,seconds=time.monotonic()-began,
            peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(),fit_metrics=metrics['fits'],
            context_count=1,starting_stack=20,complete_native_private_hands_per_actor=1081,completed_cycles=1,
            scientific_accuracy_qualified=False,production_changed=False)
        write(STORE/'result.json',result); outcome=True
        print(json.dumps(dict(passed=True,seconds=result['seconds'],result=str(STORE/'result.json'))),flush=True)
    except BaseException as exc:
        write(STORE/'failure.json',dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),
            seconds=time.monotonic()-began,stages=stages,resource_samples=measured,preserve_failed_evidence=True,automatic_retry=False))
        raise
    finally:
        if LOCK.exists() and pipeline.sha(LOCK)==lock_hash:
            # Exact owned nonrecursive lock, preserved owner record; never delete
            # an unchecked computed directory or another process's lock.
            if LOCK.resolve()!=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock':
                raise ValueError('Unexpected resolved global lock path')
            LOCK.unlink()
        if outcome: write(STORE/'released.json',dict(pid=process.pid,process_created=process.create_time(),terminal_unix=time.time()))


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--prepare',type=Path); parser.add_argument('--run',action='store_true')
    args=parser.parse_args()
    if (args.prepare is None)==(not args.run): parser.error('Choose preparation or the one native software profile')
    prepare(args.prepare) if args.prepare else run()
