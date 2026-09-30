"""Registered matched full-continuation training; evaluation remains separate."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                  CUBLAS_WORKSPACE_CONFIG=':4096:8', PYTHONDONTWRITEBYTECODE='1')
import argparse
import gc
import json
from pathlib import Path
import sys
import time
import traceback
import uuid
import numpy as np
import psutil
import torch
import stack_context_training_checkpoint_v1 as checkpoint
import stack_context_training_pipeline_v1 as pipeline
import stack_context_full_policy_v1 as full
import stack_context_cycle_archive_v2 as archive
from stack_context_inputs_v1 import Registry
from stack_context_relative_inputs_v1 import Registry as RelativeRegistry
from preflop_allin_matrix_v1 import AllinMatrix
from sampled_allin_protocol_v3 import AllinCache
from sampled_visible_hybrid_checkpoint_v1 import read_object
from sampled_physical_root_evaluation_v1 import sha, save
from board_root_accumulator_v1 import CHANCE
from river_weighted_overlay_ingest_v1 import METHOD
from board_prefix_publication_v1 import atomic_json
from board_study_storage_v1 import create, measure
from global_research_inventory_v3 import measure as inventory
from river_matched_training_pilot_v1 import ROOT, OUT, LOCK, OTHER, available, production_available, gpu_snapshot, memory_admitted

NAME = 'stack-context-matched-learning-v1'
STORE = Path('S:/GTOpen-research') / NAME
POPULATION = Path('S:/GTOpen-research/stack-context-population-v1')
PLAN = OUT / 'STACK-CONTEXT-MATCHED-LEARNING-PLAN.md'
REG, ATTEMPT, RESULT, FAILURE, STATUS = (OUT / (NAME+s+'.json') for s in
                                        ('-registration', '-attempt', '-training-result', '-failure', '-status'))
TOKEN = NAME + '-new-evidence-only'
ORDER = ('A-baseline', 'A-relative', 'B-relative', 'B-baseline')
CYCLES = 64
LIMIT = 45_000_000_000


def read(path):
    return json.loads(Path(path).read_bytes())


def verify(identities):
    for path, expected in identities.items():
        if sha(path) != expected:
            raise ValueError('Registered input changed: ' + path)


def status(stage, **kwargs):
    atomic_json(STATUS, dict(stage=stage, pid=os.getpid(), process_created=psutil.Process().create_time(),
                unix=time.time(), **kwargs), replace=True)


def resources_for(registry, prepared, replication):
    resources = {}; inputs = {}; contexts = {}
    for key in registry.fit_contexts:
        record = prepared['contexts'][key]; depth = record['depth']
        matrix = AllinMatrix(read(record['matrix']), registry.source(key))
        stream_seed = 9400000 + replication*1000000 + depth*100
        root = dict(context_sha256=key, matrix_sha256=record['matrix_sha256'], entry_mass=matrix.bb_mass.tolist(),
                    physical_budget=169, boards_per_generation=1, board_seed=stream_seed, chance=CHANCE)
        resources[key] = dict(catalog_source=Path(record['initial_catalog']).read_text(),
            matrix_sha256=record['matrix_sha256'], entry_mass=matrix.btn_mass.tolist(), root_config=root)
        inputs[key] = dict(context_path=record['context_path'], matrix=record['matrix'],
            physical_catalog=record['physical_catalog'], physical_catalog_sha256=record['artifacts'][record['physical_catalog']])
        contexts[key] = dict(sampler_seed=stream_seed+1, action_seed=stream_seed+2,
            reservoir_seeds=[stream_seed+3,stream_seed+4], reservoir_capacity=32768,
            deals_per_generation=169, deals_per_subbatch=13, query_limit=1000000, board_root=root,
            allin_cache_sha256=prepared['cache_sha256'], river_targets=dict(method=METHOD,K=64))
    return resources, inputs, contexts


def specification():
    population_path = OUT / 'stack-context-population-v1-result.json'
    population_review = OUT / 'stack-context-population-v1-readback.json'
    proof_pairs = [(population_path, population_review),
        (OUT/'stack-context-native-cycle-control-v4-result.json', OUT/'stack-context-native-cycle-readback-v1-result.json')]
    paths = {Path(__file__).resolve(), PLAN, POPULATION/'entries.json'}
    for result_path, review_path in proof_pairs:
        result, review = read(result_path), read(review_path)
        if not result['passed'] or not result['complete'] or not review['passed'] or not review['complete']:
            raise ValueError('Completed implementation/resource evidence required')
        # These readers use their own explicit recorded result identity fields.
        if review_path == population_review and review['result_sha256'] != sha(result_path):
            raise ValueError('Population readback is stale')
        if review_path != population_review and review['source_result_sha256'] != sha(result_path):
            raise ValueError('Native-cycle readback is stale')
        paths.update((result_path, review_path))
    compression_path = OUT/'stack-context-cycle-archive-control-v1-result.json'
    compression_reg = OUT/'stack-context-cycle-archive-control-v1-registration.json'
    compression = read(compression_path)
    if (not compression['passed'] or not compression['complete']
            or compression['registration_sha256'] != sha(compression_reg)
            or not compression['partial_retirement_recovered'] or not compression['legacy_originals_unchanged']):
        raise ValueError('Exact archive/recovery control required')
    verify(read(compression_reg)['inputs']); paths.update((compression_path, compression_reg))
    parallel_path=OUT/'stack-context-cycle-archive-parallel-check-v1-result.json'
    parallel_reg=OUT/'stack-context-cycle-archive-parallel-check-v1-registration.json'
    parallel=read(parallel_path)
    if (not parallel['passed'] or not parallel['complete'] or not parallel['byte_identical_to_baseline_archives']
            or parallel['registration_sha256']!=sha(parallel_reg)):
        raise ValueError('Qualified dynamic archive scheduling required')
    verify(read(parallel_reg)['inputs']); paths.update((parallel_path,parallel_reg))
    prepared = read(population_path)
    for path, expected in prepared['artifacts'].items():
        if sha(path) != expected:
            raise ValueError('Prepared population artifact changed')
        paths.add(Path(path))
    review_path = OUT/'stack-context-complete-allin-cache-v1-readback.json'; review = read(review_path)
    if not review['passed'] or review['cache_sha256'] != prepared['cache_sha256']:
        raise ValueError('Exact all-in cache qualification required')
    paths.update((review_path, Path(review['cache_artifact'])))
    native = {key: ROOT/'target/release/examples'/name for key,name in dict(
        bridge='hu_sampled_allin_history_bridge_v1.exe', trace='hu_sampled_action_trace_v2.exe',
        integration='hu_sampled_profile_allin_evaluation_v1.exe', river='hu_river_two_stage_stream_v1.exe',
        board='hu_fixed_board_tree_v1.exe').items()}
    paths.update(native.values())
    paths.update(ROOT/'crates/solver/examples'/(path.stem+'.rs') for path in native.values())
    old_registration = read(OUT/'stack-context-native-cycle-control-v4-registration.json')
    for path in native.values():
        if old_registration['inputs'].get(str(path)) != sha(path):
            raise ValueError('Native executable differs from the qualified full-cycle implementation')
    paths.add(OUT/'stack-context-native-cycle-control-v4-registration.json')
    for module in list(sys.modules.values()):
        path = getattr(module, '__file__', None)
        if path and Path(path).is_relative_to(ROOT) and Path(path).suffix == '.py':
            paths.add(Path(path))
    identities = {str(path):sha(path) for path in sorted(paths)}
    for path,expected in identities.items():
        if path in old_registration['inputs'] and old_registration['inputs'][path]!=expected:
            raise ValueError('A reused qualified implementation source changed: '+path)
    entries = read(POPULATION/'entries.json'); arms = {}; runtime = {}
    for name in ORDER:
        replication = 0 if name.startswith('A-') else 1
        relative = name.endswith('relative')
        registry = (RelativeRegistry if relative else Registry)(entries)
        resources, inputs, contexts = resources_for(registry, prepared, replication)
        config = dict(format=1, checkpoint_type=checkpoint.TYPE, registry_sha256=registry.sha256,
            representation=registry.manifest['representation'], target_units=checkpoint.SCALE,
            fit_runtime=checkpoint.RUNTIME, objective_method=checkpoint.METHOD,
            initialization=checkpoint.INITIALIZATION, optimizer=checkpoint.OPTIMIZER,
            device='cuda', current_policy_inference='float64-widened-float32-weights-v1', fit_steps=256,
            chunk_size=512, learning_rate=.003, fit_seed_base=12000000+replication*1000000,
            context_order=list(registry.fit_contexts), context_weights={key:.2 for key in registry.fit_contexts},
            contexts=contexts, source_identities=identities)
        checkpoint.require_config(config, registry, resources)
        arms[name] = dict(config=config, representation=387 if relative else 362, replication=replication)
        runtime[name] = dict(registry=registry, resources=resources, inputs=inputs)
    spec = dict(format=1, name=NAME, inputs=identities, arms=arms, cycles=CYCLES, arm_order=list(ORDER),
        workers=4, board_workers=1, maximum_new_logical_bytes=LIMIT, global_allocation_cap=800_000_000_000,
        maximum_training_seconds=72*3600, maximum_invocation_seconds=12*3600, maximum_cuda_bytes=2_000_000_000,
        cache_sha256=prepared['cache_sha256'], cache_artifact=review['cache_artifact'],
        entry_origin='Fixed retained 200bb GTOpen BB/BTN entry across stacks; not measured or depth-optimal openings',
        final_bank_generations=list(range(CYCLES)), unplayed_excluded=CYCLES,
        evaluation=dict(deals_per_context=4096, seed_by_depth={str(d):9309000+d for d in (20,40,60,100,150,200,400)},
            complete_crossed_profiles=8, one_final_look=True, family_alpha=.05, alpha_per_context=.05/7,
            criterion='All eight equal-depth stack-normalized gains have positive simultaneous lower bounds and no negative per-depth mean',
            prediction_diagnostic='Outstanding separate correctly targeted protocol; never compare raw regret outputs to final-policy EV'),
        production_modified=False)
    return spec, runtime, native


class Guard:
    def __init__(self, admitted_unix):
        self.admitted_unix = admitted_unix; self.last = 0.; self.last_gpu = 0.; self.last_size = 0.
    def __call__(self):
        now = time.monotonic()
        if time.time()-self.admitted_unix > 72*3600:
            raise RuntimeError('Registered total training time bound')
        if torch.cuda.memory_reserved() > 2_000_000_000:
            raise RuntimeError('Registered CUDA memory bound')
        if now-self.last > 2:
            if (not production_available() or OTHER.exists() or psutil.virtual_memory().available < 24_000_000_000
                    or psutil.disk_usage('S:/').free < 40_000_000_000):
                raise RuntimeError('Research yields to active production or resource pressure; preserve current evidence')
            self.last = now
        if now-self.last_size > 30:
            if sum(path.stat().st_size for path in STORE.rglob('*') if path.is_file()) > LIMIT:
                raise RuntimeError('Registered new logical evidence budget')
            self.last_size = now
        if now-self.last_gpu > 30:
            torch.cuda.synchronize(); time.sleep(1.2)
            while True:
                probe = gpu_snapshot()
                if probe['utilization_percent'] < 65 and memory_admitted(probe['free_bytes'], torch.cuda.memory_reserved()):
                    break
                if not production_available() or OTHER.exists() or time.time()-self.admitted_unix > 72*3600:
                    raise RuntimeError('Competing workload or registered wait deadline')
                status('yielding-to-heavy-gpu-work', **probe); time.sleep(5)
            self.last_gpu = time.monotonic()


def cycle_metric(folder, dest, guard):
    metric = folder/'metrics.json'
    if metric.exists():
        return read(metric)
    if (dest/'index.json').exists():
        plan, index = archive.verify_index(dest, root=STORE, token=TOKEN, guard=guard)
        for job, record in zip(plan['jobs'], index['bundles']):
            if any(row['path']=='metrics.json' for row in job['members']):
                path = dest/record['archive']
                from owned_research_archive_v1 import unpack
                return json.loads(unpack(path, read(path.with_suffix('.xz.json')), guard=guard)['metrics.json'])
    raise RuntimeError('Partial scientific cycle has no complete checkpoint; do not recollect or retry it')


def paired_sources(raw, dest, contexts):
    if (dest/'plan.json').exists():
        originals={row['path']:row['sha256'] for row in read(dest/'plan.json')['members']}
    else:
        originals={path.relative_to(raw).as_posix():sha(path) for path in raw.rglob('*.json')
                   if path.name in ('source-generation.json','board-plan.json','batch.json')}
    expected=[]
    for key in contexts:
        expected.extend([key+'/source-generation.json',key+'/board-plan.json'])
        expected.extend(key+f'/batch-{index:03d}/batch.json' for index in range(13))
    if any(name not in originals for name in expected):
        raise ValueError('Missing paired deal/action/board source identity')
    return {name:originals[name] for name in expected}


def train(spec, runtime, native, guard):
    cache = AllinCache(spec['cache_artifact'], spec['cache_sha256']); began=time.monotonic()
    for cycle in range(1,CYCLES+1):
        for name in ORDER:
            folder=STORE/name; objects=folder/'objects'; progress_path=folder/'progress.json'
            cfg=spec['arms'][name]['config']; rt=runtime[name]
            registry,resources=rt['registry'],rt['resources']
            if progress_path.exists():
                progress=read(progress_path)
                if progress['registration_sha256']!=sha(REG):
                    raise ValueError('Progress registration changed')
                if progress['completed_cycles']>=cycle:
                    continue
                if progress['completed_cycles']!=cycle-1:
                    raise ValueError('Missing complete cycle boundary')
                state=checkpoint.restore_checkpoint(objects,progress['checkpoint'],cfg,registry,resources)
            else:
                if cycle!=1 or folder.exists():
                    raise ValueError('Unregistered or partial arm initialization')
                folder.mkdir(); objects.mkdir()
                state=checkpoint.initialize(objects,cfg,registry,resources)
                reference=checkpoint.save_checkpoint(objects,state,cfg,registry,resources)
                progress=dict(registration_sha256=sha(REG),completed_cycles=0,checkpoint=reference,updates=[])
                atomic_json(progress_path,progress)
            if time.monotonic()-began > 12*3600:
                status('complete-boundary-awaiting-resume', arm=name, next_cycle=cycle)
                return False
            guard(); raw=folder/f'cycle-{cycle:04d}'; dest=folder/f'archive-{cycle:04d}'
            def stage(phase,key=None):
                status('training',arm=name,cycle=cycle,phase=phase,context_sha256=key)
            stage('start')
            if raw.exists():
                metric=cycle_metric(raw,dest,guard)
                if metric['completed_cycles']!=cycle or metric['used_model']!=state['next_model']:
                    raise ValueError('Recovered cycle has the wrong source model')
                candidate=checkpoint.restore_checkpoint(objects,metric['checkpoint'],cfg,registry,resources)
            else:
                candidate,_,metric=pipeline.update(raw,objects,state,cfg,registry,resources,
                    inputs=rt['inputs'],cache=cache,native=native,guard=guard,workers=4,board_workers=1,
                    batch_prefix=NAME+'-'+name[0],on_stage=stage)
            restored=checkpoint.restore_checkpoint(objects,metric['checkpoint'],cfg,registry,resources)
            if restored['next_model']!=candidate['next_model'] or restored['completed_cycles']!=cycle:
                raise ValueError('Complete checkpoint restore differs')
            common=paired_sources(raw,dest,registry.fit_contexts)
            partner=name[0]+('-relative' if name.endswith('baseline') else '-baseline')
            partner_progress=STORE/partner/'progress.json'
            if partner_progress.exists():
                other=read(partner_progress)
                if other['completed_cycles']>=cycle and other['updates'][cycle-1]['paired_sources']!=common:
                    raise ValueError('Matched representations did not use identical physical/action/board streams')
            stage('archive-completed-evidence')
            if (dest/'index.json').exists():
                archive_result=archive.finish_retirement(dest,root=STORE,token=TOKEN,guard=guard)
            elif dest.exists():
                raise RuntimeError('Incomplete archive publication; preserve it for transport-only recovery')
            else:
                archive_result=archive.archive_cycle(raw,dest,root=STORE,token=TOKEN,guard=guard,workers=4)
            record=dict(cycle=cycle,checkpoint=metric['checkpoint'],archive=str(dest.relative_to(STORE)),
                archive_index_sha256=sha(dest/'index.json'),retirement_sha256=sha(dest/'retired.json'),
                collection_seconds=metric['seconds'],packed_bytes=archive_result['packed_bytes'],paired_sources=common)
            progress=dict(progress,completed_cycles=cycle,checkpoint=metric['checkpoint'],updates=[*progress['updates'],record])
            atomic_json(progress_path,progress,replace=True)
            print(json.dumps(dict(stage='complete-cycle',arm=name,cycle=cycle,seconds=metric['seconds'],packed_bytes=record['packed_bytes'])),flush=True)
            del restored,candidate,state; gc.collect()
    return True


def main(run=False,resume=False):
    spec,runtime,native=specification()
    if not run:
        print(json.dumps(dict(prepared=True,training_started=False,cycles_per_arm=CYCLES,arms=4,workers=4,store=str(STORE))))
        return
    if any(path.exists() for path in (LOCK,OTHER,RESULT,FAILURE)):
        raise ValueError('Live owner or terminal scientific outcome; do not duplicate/retry')
    if resume:
        if read(REG)!=spec or not ATTEMPT.exists():
            raise ValueError('Resume requires the unchanged admitted attempt')
    elif any(path.exists() for path in (REG,ATTEMPT,STORE)):
        raise ValueError('Existing scientific attempt; resume complete boundaries explicitly')
    ready,probe=available()
    if not ready:
        print(json.dumps(dict(deferred=True,probe=probe,training_started=False))); return
    accounting=inventory(); allocated=sum(row['allocated_file_bytes'] for row in accounting)
    own=measure(STORE)['allocated_file_bytes'] if STORE.exists() else 0
    if allocated+max(0,LIMIT-own)>800_000_000_000:
        raise ValueError('New study reservation exceeds the global allocation cap')
    with LOCK.open('x') as stream:
        stream.write(str(os.getpid()))
    try:
        if not resume:
            create(STORE); save(STORE/'archive-owner.json',dict(format=1,token=TOKEN,purpose='new-research-scratch-v1'))
            save(REG,spec); save(STORE/'admission.json',accounting)
            save(ATTEMPT,dict(pid=os.getpid(),process_created=psutil.Process().create_time(),admitted_unix=time.time(),registration_sha256=sha(REG),gpu=probe))
        invocation=STORE/('invocation-'+uuid.uuid4().hex+'.json')
        save(invocation,dict(pid=os.getpid(),process_created=psutil.Process().create_time(),unix=time.time(),resume=resume,registration_sha256=sha(REG)))
        torch.set_num_threads(1); torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False; torch.backends.cudnn.allow_tf32=False
        torch.cuda.set_per_process_memory_fraction(2_000_000_000/torch.cuda.get_device_properties(0).total_memory)
        guard=Guard(read(ATTEMPT)['admitted_unix']); status('admitted',resume=resume)
        complete=train(spec,runtime,native,guard)
        if complete:
            verify(spec['inputs'])
            progress={name:read(STORE/name/'progress.json') for name in ORDER}
            save(RESULT,dict(training_complete=True,scientific_evaluation_complete=False,accuracy_qualified=False,
                registration_sha256=sha(REG),arms=progress,storage=measure(STORE),production_modified=False))
            status('training-complete-awaiting-fresh-evaluation')
    except BaseException as error:
        if ATTEMPT.exists():
            save(FAILURE,dict(error=repr(error),traceback=traceback.format_exc(),retry_allowed=False,registration_sha256=sha(REG)))
        raise
    finally:
        if LOCK.exists() and LOCK.read_text()==str(os.getpid()):
            LOCK.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--run',action='store_true'); parser.add_argument('--resume',action='store_true')
    args=parser.parse_args(); main(run=args.run,resume=args.resume)
