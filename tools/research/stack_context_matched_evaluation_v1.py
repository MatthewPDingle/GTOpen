"""Prepared consumer for the frozen matched stack study; never launch training.

Default invocation describes readiness. --run requires successful completed
training, released ownership, pinned integration evidence and idle resources.
Fresh evaluation uses the already registered seven-depth scientific protocol.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',
                  CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONDONTWRITEBYTECODE='1')
import argparse
import gc
import json
from pathlib import Path
import sys
import time
import traceback
import uuid
import psutil
import torch
from stack_context_inputs_v1 import Registry,encoded
from stack_context_relative_inputs_v1 import Registry as RelativeRegistry
from stack_context_final_bank_v1 import select_terminal,load_documents,BANK_ORDER,CYCLES
from stack_context_matched_analysis_v1 import DEPTHS,DEALS,finish
from stack_context_played_bank_v1 import PlayedBank
from stack_context_preflop_export_v1 import export
from stack_context_evaluation_journal_v1 import EvaluationJournal
from stack_context_evaluation_driver_v1 import collect
from stack_context_matched_learning_v1 import resources_for
from sampled_visible_hybrid_checkpoint_v1 import read_object
from sampled_allin_protocol_v3 import AllinCache
from sampled_physical_root_evaluation_v1 import sha,save
from board_prefix_publication_v1 import atomic_json
from board_study_storage_v1 import create,measure
from global_research_inventory_v3 import measure as inventory
from river_matched_training_pilot_v1 import ROOT,OUT,LOCK,OTHER,available,production_available,gpu_snapshot,memory_admitted

NAME='stack-context-matched-evaluation-v1'
STORE=Path('S:/GTOpen-research')/NAME
TRAIN=Path('S:/GTOpen-research/stack-context-matched-learning-v1')
TRAIN_REG=OUT/'stack-context-matched-learning-v1-registration.json'
TRAIN_RESULT=OUT/'stack-context-matched-learning-v1-training-result.json'
TRAIN_FAILURE=OUT/'stack-context-matched-learning-v1-failure.json'
POPULATION=Path('S:/GTOpen-research/stack-context-population-v1')
REG,ATTEMPT,RESULT,FAILURE,STATUS=(OUT/(NAME+s+'.json') for s in ('-registration','-attempt','-result','-failure','-status'))
PLAN=OUT/'STACK-CONTEXT-MATCHED-EVALUATION-PLAN.md'
GATES=tuple(OUT/(name+'-result.json') for name in (
    'stack-context-matched-analysis-check-v1','stack-context-preflop-export-check-v1',
    'stack-context-matched-journal-check-v1','stack-context-final-bank-check-v1',
    'stack-context-evaluation-integration-check-v1'))
EXES=dict(query=ROOT/'target/release/examples/hu_sampled_bank_bridge.exe',
          evaluation=ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe')
LIMIT=20_000_000_000


def read(path):
    return json.loads(Path(path).read_bytes())


def verify(inputs):
    for path,identity in inputs.items():
        if sha(path)!=identity:
            raise ValueError('Pinned evaluation input changed: '+path)


def readiness():
    return dict(training_complete=TRAIN_RESULT.exists() and not TRAIN_FAILURE.exists(),
        training_failure=TRAIN_FAILURE.exists(),research_owner_present=LOCK.exists() or OTHER.exists(),
        missing_checks=[str(p) for p in GATES if not p.exists()],
        scientific_evaluation_started=ATTEMPT.exists(),scientific_evaluation_finished=RESULT.exists(),
        evaluation_failure=FAILURE.exists())


def status(stage,**values):
    atomic_json(STATUS,dict(stage=stage,pid=os.getpid(),process_created=psutil.Process().create_time(),
                           unix=time.time(),**values),replace=True)


def specification():
    ready=readiness()
    if (not ready['training_complete'] or ready['training_failure'] or ready['missing_checks']):
        raise ValueError('Completed training and all implementation gates are required: '+json.dumps(ready))
    source=read(TRAIN_REG);terminal=read(TRAIN_RESULT)
    verify(source['inputs'])
    for gate in GATES:
        proof=read(gate)
        if not proof.get('complete') or not proof.get('passed'):
            raise ValueError('Unpassed evaluation implementation gate: '+str(gate))
    integration=read(GATES[-1])
    if integration.get('controller_sha256')!=sha(Path(__file__).resolve()):
        raise ValueError('Integration evidence does not cover this controller source')
    prepared=read(OUT/'stack-context-population-v1-result.json')
    verify(prepared['artifacts'])
    entries=read(POPULATION/'entries.json')
    checkpoints={};paths={TRAIN_REG,TRAIN_RESULT,PLAN,Path(__file__).resolve(),POPULATION/'entries.json',*GATES,*EXES.values()}
    for arm in BANK_ORDER:
        progress=terminal['arms'][arm]
        progress_path=TRAIN/arm/'progress.json'
        if read(progress_path)!=progress:
            raise ValueError('Terminal and actual training progress differ')
        objects=TRAIN/arm/'objects'
        checkpoints[arm]=json.loads(read_object(objects,progress['checkpoint']))
        paths.update((progress_path,objects/progress['checkpoint']['file']))
        for item in [*checkpoints[arm]['played_bank'],checkpoints[arm]['next_model']]:
            # Authenticate every reference before fixing the evaluation manifest.
            read_object(objects,item)
            paths.add(objects/item['file'])
    banks=select_terminal(terminal,checkpoints,source,training_registration_sha256=sha(TRAIN_REG))
    runtime={}
    for arm in BANK_ORDER:
        registry=(RelativeRegistry if arm.endswith('relative') else Registry)(entries)
        resources,_,_=resources_for(registry,prepared,0 if arm.startswith('A-') else 1)
        if registry.sha256!=banks['arms'][arm]['registry_sha256']:
            raise ValueError('Selected registry and actual runtime differ')
        runtime[arm]=dict(registry=registry,resources=resources)
    paths.add(OUT/'stack-context-population-v1-result.json')
    paths.update(Path(p) for p in prepared['artifacts'])
    paths.add(Path(source['cache_artifact']))
    for executable in EXES.values():
        paths.add(ROOT/'crates/solver/examples'/(executable.stem+'.rs'))
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path and Path(path).is_relative_to(ROOT) and Path(path).suffix=='.py':
            paths.add(Path(path))
    identities={str(p):sha(p) for p in sorted(paths)}
    # Integrator pins all actual evaluator dependencies; changes require a new
    # transport/control check, never silent reuse of an old passing result.
    verify(integration['inputs'])
    identity=dict(selection=banks,training_result_sha256=sha(TRAIN_RESULT),training_registration_sha256=sha(TRAIN_REG))
    spec=dict(format=1,name=NAME,inputs=identities,banks=identity,
        training_evaluation_protocol=source['evaluation'],bank_order=list(BANK_ORDER),
        depths=list(DEPTHS),deals_per_depth=DEALS,batch_size=32,
        chance='full_deck',seed_by_depth={str(d):9309000+d for d in DEPTHS},
        alpha_per_depth=.05/7,one_final_look=True,
        maximum_new_logical_bytes=LIMIT,global_allocation_cap=800_000_000_000,
        maximum_invocation_seconds=12*3600,maximum_evaluation_seconds=72*3600,maximum_cuda_bytes=2_000_000_000,
        archive='Exact columnar/XZ byte restoration before retiring only newly owned raw duplicates',
        cache_artifact=source['cache_artifact'],cache_sha256=source['cache_sha256'],
        independent_readback_outstanding=True,prediction_diagnostic_outstanding=True,production_modified=False)
    return spec,runtime,prepared


class Guard:
    def __init__(self,admitted_unix):
        self.admitted=admitted_unix;self.last=0.;self.last_gpu=0.;self.last_storage=0.
    def __call__(self):
        now=time.monotonic()
        if time.time()-self.admitted>72*3600:
            raise RuntimeError('Registered evaluation time limit; preserve evidence')
        if torch.cuda.memory_reserved()>2_000_000_000:
            raise RuntimeError('Evaluation CUDA reservation limit')
        if now-self.last>2:
            if (not production_available() or OTHER.exists() or psutil.virtual_memory().available<24_000_000_000
                    or psutil.disk_usage('S:/').free<40_000_000_000):
                raise RuntimeError('Yield to production or resource pressure; preserve evidence')
            self.last=now
        if now-self.last_storage>30:
            if sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())>LIMIT:
                raise RuntimeError('Registered evaluation evidence budget')
            self.last_storage=now
        if now-self.last_gpu>30:
            torch.cuda.synchronize();time.sleep(1.2)
            while True:
                probe=gpu_snapshot()
                if probe['utilization_percent']<65 and memory_admitted(probe['free_bytes'],torch.cuda.memory_reserved()):
                    break
                if not production_available() or OTHER.exists() or time.time()-self.admitted>72*3600:
                    raise RuntimeError('Competing solve or evaluation wait bound')
                status('yielding-to-heavy-gpu-work',**probe);time.sleep(5)
            self.last_gpu=time.monotonic()


def evaluate(spec,runtime,prepared,guard):
    started=time.monotonic();identity_path=STORE/'bank-identities.json'
    identity=spec['banks']
    if identity_path.exists():
        if read(identity_path)!=identity:
            raise ValueError('Frozen bank identity manifest changed')
    else:
        atomic_json(identity_path,identity)
    bank_hash=sha(identity_path)
    cache=AllinCache(spec['cache_artifact'],spec['cache_sha256'])
    documents={}
    for arm in BANK_ORDER:
        guard();status('loading-complete-played-bank',arm=arm)
        rt=runtime[arm]
        documents[arm]=load_documents(TRAIN/arm/'objects',identity['selection']['arms'][arm],
            rt['registry'],rt['resources'],guard=guard)
    contexts=[];exports={};journals={}
    for depth in DEPTHS:
        guard();record=next(r for r in prepared['contexts'].values() if r['depth']==depth)
        source=Path(record['context_path']).read_text();key=record['context_sha256']
        args=dict(context_source=source,registration_sha256=sha(REG),bank_identities_sha256=bank_hash,
                  cache_sha256=cache.sha256,guard=guard)
        folder=STORE/f'stack-{depth}'
        journal=EvaluationJournal(folder,**args) if folder.exists() else EvaluationJournal.create(folder,**args)
        state=journal.prefix(verify_archives=True)
        banks=[]
        for arm in BANK_ORDER:
            rt=runtime[arm];selected=identity['selection']['arms'][arm]
            banks.append(PlayedBank(documents[arm],rt['registry'],context_sha256=key,resources=rt['resources'],
                weights_by_player=selected['weights_by_player'],completed_cycles=CYCLES,device='cuda',guard=guard))
        completed=collect(journal,context_path=record['context_path'],banks=banks,cache=cache,
            query_executable=EXES['query'],evaluation_executable=EXES['evaluation'],guard=guard,
            stop_requested=lambda:time.monotonic()-started>12*3600,
            on_progress=lambda count:status('evaluating',depth=depth,completed_deals=count,total_deals=DEALS))
        if not completed['complete']:
            status('complete-boundary-awaiting-resume',depth=depth,completed_deals=completed['completed_deals'])
            return None
        contexts.append(completed['analysis'])
        journals[str(depth)]=dict(journal_owner_sha256=journal.owner,last_commit_sha256=completed['last_commit_sha256'],completed_deals=DEALS)
        catalog=read(record['physical_catalog']);matrix=read(record['matrix'])
        for arm,bank in zip(BANK_ORDER,banks):
            guard();path=folder/(arm+'-preflop-ranges.json')
            if path.exists():
                value=read(path)
                if value['bank_identities_sha256']!=bank_hash or value['context_sha256']!=key or value['arm']!=arm:
                    raise ValueError('Changed range-export identity')
            else:
                value=dict(arm=arm,context_sha256=key,bank_identities_sha256=bank_hash,
                    range_export=export(source,catalog,matrix['class_mass'],bank,guard=guard))
                atomic_json(path,value)
            exports[str(path)]=sha(path)
        del banks,bank,state
        gc.collect();torch.cuda.empty_cache()
    comparison=finish(contexts)
    return dict(fixed_policy_evaluation_complete=True,independent_readback_complete=False,
        prediction_diagnostic_complete=False,accuracy_qualified=False,registration_sha256=sha(REG),
        bank_identities_sha256=bank_hash,journals=journals,range_exports=exports,comparison=comparison,
        storage=measure(STORE),production_modified=False)


def main(run=False,resume=False):
    if not run:
        print(json.dumps(dict(prepared_consumer=True,**readiness())));return
    if any(p.exists() for p in (LOCK,OTHER,RESULT,FAILURE)):
        raise ValueError('Live owner or terminal evaluation; do not duplicate or retry')
    spec,runtime,prepared=specification()
    if resume:
        if not ATTEMPT.exists() or read(REG)!=spec:
            raise ValueError('Resume only the unchanged admitted comparison')
    elif any(p.exists() for p in (REG,ATTEMPT,STORE)):
        raise ValueError('Existing attempt; complete-boundary resume must be explicit')
    ready,probe=available()
    if not ready:
        print(json.dumps(dict(deferred=True,probe=probe)));return
    accounting=inventory();allocated=sum(row['allocated_file_bytes'] for row in accounting)
    own=measure(STORE)['allocated_file_bytes'] if STORE.exists() else 0
    if allocated+max(0,LIMIT-own)>800_000_000_000:
        raise ValueError('Evaluation reservation exceeds global allocated storage cap')
    with LOCK.open('x') as stream:
        stream.write(str(os.getpid()))
    try:
        if not resume:
            create(STORE);save(REG,spec);save(STORE/'admission.json',accounting)
            save(ATTEMPT,dict(pid=os.getpid(),process_created=psutil.Process().create_time(),admitted_unix=time.time(),registration_sha256=sha(REG)))
        save(STORE/('invocation-'+uuid.uuid4().hex+'.json'),dict(pid=os.getpid(),process_created=psutil.Process().create_time(),unix=time.time(),resume=resume))
        torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        torch.cuda.set_per_process_memory_fraction(2_000_000_000/torch.cuda.get_device_properties(0).total_memory)
        guard=Guard(read(ATTEMPT)['admitted_unix'])
        result=evaluate(spec,runtime,prepared,guard)
        if result is not None:
            verify(spec['inputs']);save(RESULT,result);status('fixed-policy-evaluation-complete-awaiting-independent-readback')
    except BaseException as error:
        if ATTEMPT.exists():
            save(FAILURE,dict(error=repr(error),traceback=traceback.format_exc(),automatic_retry_allowed=False,registration_sha256=sha(REG)))
        raise
    finally:
        if LOCK.exists() and LOCK.read_text()==str(os.getpid()):
            LOCK.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');parser.add_argument('--resume',action='store_true')
    args=parser.parse_args();main(run=args.run,resume=args.resume)
