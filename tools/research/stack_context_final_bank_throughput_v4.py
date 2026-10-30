"""Prospective full-bank resource/reference check, using retained hands only.

--prepare freezes the first32 distinct physical deals from the already archived
A-baseline generation-one 20bb source. --run requires all actual final banks.
No fit, new physical draw, native payoff comparison or model selection occurs.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',
    CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONDONTWRITEBYTECODE='1')
import argparse
import copy
import gc
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
import queue
import subprocess
import sys
import time
import traceback
import numpy as np
import psutil
import torch
import stack_context_matched_evaluation_v5 as evaluation
import stack_context_final_bank_v4 as selection
import stack_context_parallel_continuation_v2 as continuation
import stack_context_pressure_provenance_v1 as pressure
import stack_context_full_policy_v1 as full
from stack_context_played_bank_v1 import PlayedBank
from stack_context_inputs_v1 import encoded
from owned_research_archive_v1 import unpack
from sampled_visible_hybrid_checkpoint_v1 import read_object
from sampled_physical_root_evaluation_v1 import sha,save
from board_prefix_publication_v1 import atomic_json
from board_study_storage_v1 import measure,create
from global_research_inventory_v3 import measure as inventory

NAME='stack-context-final-bank-throughput-v4'
OUT=continuation.legacy.OUT
STORE=Path('S:/GTOpen-research')/NAME
PLAN=OUT/'STACK-CONTEXT-FINAL-BANK-THROUGHPUT-V4-PLAN.md'
FIXTURE=OUT/'stack-context-final-bank-throughput-v2-retained-fixture.json'
FIXTURE_FAILURE=OUT/(NAME+'-fixture-failure.json')
CONTROL=OUT/'stack-context-pressure-consumer-check-v3-result.json'
REG,ATTEMPT,RESULT,FAILURE,STATUS=(OUT/(NAME+s+'.json') for s in ('-registration','-attempt','-result','-failure','-status'))
MAX_BYTES=3_000_000_000
MAX_SECONDS=4*3600


def require(ok,message):
    if not ok:raise ValueError(message)


def read(path):return json.loads(Path(path).read_bytes())


def status(stage,**values):
    atomic_json(STATUS,dict(stage=stage,pid=os.getpid(),process_created=psutil.Process().create_time(),unix=time.time(),**values),replace=True)


def retained_fixture():
    prepared=read(OUT/'stack-context-population-v1-result.json')
    row=next(r for r in prepared['contexts'].values() if r['depth']==20)
    key=row['context_sha256'];train=continuation.legacy.STORE
    progress=read(train/'A-baseline/progress.json');update=progress['updates'][0]
    folder=train/'A-baseline/archive-0001'
    require(update['cycle']==1 and sha(folder/'index.json')==update['archive_index_sha256'], 'Changed retained source archive')
    index=read(folder/'index.json');plan=read(folder/'plan.json')
    require(index['plan_sha256']==sha(folder/'plan.json'), 'Changed archive plan')
    name=key+'/source-generation.json'
    jobs=[(j,r) for j,r in zip(plan['jobs'],index['bundles']) if any(m['path']==name for m in j['members'])]
    require(len(jobs)==1, 'Missing or duplicated retained generation source')
    job,record=jobs[0];packed=Path(job['destination']);manifest=packed.with_suffix('.xz.json')
    require(packed.parent==folder and packed.name==record['archive'] and sha(manifest)==record['manifest_sha256'], 'Changed retained bundle')
    parts=unpack(packed,read(manifest),guard=lambda:None);raw=parts['source-generation.json']
    identity=hashlib.sha256(raw).hexdigest()
    require(identity==update['paired_sources'][name], 'Changed retained physical draws')
    source=json.loads(raw);deals=copy.deepcopy(source['deals'][:32])
    require(len(deals)==len({tuple(d) for d in deals})==32, 'First32 retained deals must be distinct')
    for d in deals:
        require(len(d)==9 and len(set(d))==9 and all(type(c) is int and 0<=c<52 for c in d)
            and d[:2]==sorted(d[:2]) and d[2:4]==sorted(d[2:4]) and d[4:7]==sorted(d[4:7]), 'Invalid retained physical deal')
    paths={Path(__file__).resolve(),PLAN,OUT/'stack-context-population-v1-result.json',folder/'index.json',folder/'plan.json',packed,manifest}
    return dict(format=1,source_arm='A-baseline',source_cycle=1,source_depth=20,source_generation_sha256=identity,
        choice='First32 complete physical deals in original order; no resampling, sorting or outcome-based selection',
        deals=deals,query_seed=0,depths=list(evaluation.DEPTHS),inputs={str(p):sha(p) for p in paths},
        new_physical_deals=False,scientific_test_stream_used=False,independent_accuracy_evidence=False)


def prepare():
    require(not FIXTURE.exists() and not FIXTURE_FAILURE.exists(), 'Preserve existing retained fixture')
    try:
        fixture=retained_fixture();save(FIXTURE,fixture)
        print(json.dumps(dict(prepared=True,retained_distinct_deals=32,depths=fixture['depths'],new_scientific_deals=False)))
    except BaseException as error:
        save(FIXTURE_FAILURE,dict(error=repr(error),traceback=traceback.format_exc(),preserve_evidence=True));raise


def terminal_banks():
    require(pressure.RESULT.exists() and not pressure.FAILURE.exists(), 'Complete successful continuation required')
    terminal=read(pressure.RESULT);spec=read(evaluation.TRAIN_REG)
    paths=set(selection.verify_correction(terminal))|{pressure.RESULT,evaluation.TRAIN_REG}
    continuation.legacy.verify(spec['inputs'])
    prepared=read(OUT/'stack-context-population-v1-result.json');continuation.legacy.verify(prepared['artifacts'])
    checkpoints={};runtime={};receipts={}
    for arm in selection.BANK_ORDER:
        progress=terminal['arms'][arm];folder=evaluation.TRAIN/arm
        require(progress['completed_cycles']==64 and read(folder/'progress.json')==progress, 'Incomplete or changed actual final bank')
        checkpoints[arm]=json.loads(read_object(folder/'objects',progress['checkpoint']))
        runtime[arm]=continuation.runtime_for(arm,spec,prepared);receipts[arm]=[]
        paths.update((folder/'progress.json',folder/'objects'/progress['checkpoint']['file']))
        for ref in [*checkpoints[arm]['played_bank'],checkpoints[arm]['next_model']]:
            read_object(folder/'objects',ref);paths.add(folder/'objects'/ref['file'])
        for cycle in range(1,65):
            receipt,evidence=selection.authenticate_cycle(evaluation.TRAIN,arm,cycle,progress,checkpoints[arm],spec,runtime[arm],guard=lambda:None)
            receipts[arm].append(receipt);paths.update(evidence)
    banks=selection.select_terminal(terminal,checkpoints,spec,training_registration_sha256=sha(evaluation.TRAIN_REG),
        receipts=receipts,amendment_sha256=sha(continuation.AMENDMENT),original_failure_sha256=sha(continuation.legacy.FAILURE),
        comparator_sha256=sha(Path(__file__).with_name('stack_context_paired_chance_v1.py')))
    return banks,runtime,prepared,spec,paths


def make_batch(fixture,depth):
    require(depth in evaluation.DEPTHS and fixture['depths']==list(evaluation.DEPTHS) and len(fixture['deals'])==32,
        'Prospective fixture/depth changed')
    return dict(format=2,batch_id=NAME+'/retained-32/'+str(depth),seed=fixture['query_seed'],query_limit=1_000_000,
        deals=copy.deepcopy(fixture['deals']))


def compare_arrays(probability,support,reference,reference_support):
    probability=np.asarray(probability);support=np.asarray(support);reference=np.asarray(reference);reference_support=np.asarray(reference_support)
    require(probability.ndim==2 and probability.shape[1]==4 and probability.shape==reference.shape
        and support.shape==reference_support.shape==(len(probability),), 'Reference shape differs')
    require(all(np.isfinite(a).all() for a in (probability,support,reference,reference_support)), 'Nonfinite score/reference')
    error=float(np.max(abs(probability-reference)));reach_error=float(np.max(abs(support-reference_support)))
    require(error<1e-10 and reach_error<1e-8 and np.array_equal(support>0,reference_support>0), 'Full-bank reference disagreement')
    require(np.all(probability>=0) and np.all(reference>=0) and np.all(support>=0) and np.all(reference_support>=0)
        and np.max(abs(probability.sum(1)-1))<1e-12 and np.max(abs(reference.sum(1)-1))<1e-12, 'Invalid normalized full-bank policy')
    return dict(maximum_probability_error=error,maximum_support_error=reach_error,zero_support_rows=int(np.sum(support==0)))


class Guard:
    def __init__(self,started,cuda=False):self.started=started;self.cuda=cuda;self.last=0.;self.last_gpu=0.
    def __call__(self):
        now=time.monotonic()
        require(time.time()-self.started<MAX_SECONDS, 'Resource check time bound')
        if now-self.last>2:
            require(continuation.legacy.production_available() and not continuation.legacy.OTHER.exists()
                and psutil.virtual_memory().available>=24_000_000_000 and psutil.disk_usage('S:/').free>=40_000_000_000,
                'Resource check yields to active work or memory/storage pressure')
            self.last=now
        if self.cuda:
            require(torch.cuda.memory_reserved()<=2_000_000_000, 'Full-bank CUDA allocation exceeds future evaluation cap')
            if now-self.last_gpu>30:
                torch.cuda.synchronize();time.sleep(1.2)
                while True:
                    probe=continuation.legacy.gpu_snapshot()
                    if probe['utilization_percent']<65 and continuation.legacy.memory_admitted(probe['free_bytes'],torch.cuda.memory_reserved()):break
                    require(time.time()-self.started<MAX_SECONDS and continuation.legacy.production_available()
                        and not continuation.legacy.OTHER.exists(), 'Competing work/check wait bound')
                    status('yielding-to-heavy-gpu-work',probe=probe);time.sleep(5)
                self.last_gpu=time.monotonic()


def reference_worker(arm,banks,spec,prepared,jobs,answers,started):
    os.environ['CUDA_VISIBLE_DEVICES']='-1'
    try:
        torch.set_num_threads(1);guard=Guard(started)
        rt=continuation.runtime_for(arm,spec,prepared);chosen=banks['arms'][arm]
        docs=selection.load_documents(evaluation.TRAIN/arm/'objects',chosen,rt['registry'],rt['resources'],guard=guard)
        answers.put(dict(arm=arm,ready=True,pid=os.getpid(),created=psutil.Process().create_time()))
        while True:
            task=jobs.get()
            if task is None:return
            depth,key,query_path=task;query=read(query_path);begin=time.monotonic()
            p,s=full.average(docs,rt['registry'],query,context_sha256=key,resources=rt['resources'],
                weights_by_player=chosen['weights_by_player'],device='cpu',guard=guard)
            prefix=STORE/f'depth-{depth}'/arm
            np.save(str(prefix)+'-reference-p.npy',p,allow_pickle=False)
            np.save(str(prefix)+'-reference-s.npy',s,allow_pickle=False)
            answers.put(dict(arm=arm,depth=depth,seconds=time.monotonic()-begin,pid=os.getpid(),
                probability_sha256=sha(str(prefix)+'-reference-p.npy'),support_sha256=sha(str(prefix)+'-reference-s.npy')))
    except BaseException as error:
        answers.put(dict(arm=arm,failed=True,error=repr(error),traceback=traceback.format_exc()));raise


def receive(answers,processes,guard):
    while True:
        guard()
        try:
            value=answers.get(timeout=.5)
            require(not value.get('failed'), 'Reference worker failed: '+repr(value));return value
        except queue.Empty:
            require(all(p.is_alive() for p in processes.values()), 'Reference worker exited before returning a result')


def run_check(banks,runtime,prepared,spec,fixture,started):
    guard=Guard(started,cuda=True);torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    torch.cuda.set_per_process_memory_fraction(2_000_000_000/torch.cuda.get_device_properties(0).total_memory)
    documents={}
    for arm in selection.BANK_ORDER:
        rt=runtime[arm]
        documents[arm]=selection.load_documents(evaluation.TRAIN/arm/'objects',banks['arms'][arm],rt['registry'],rt['resources'],guard=guard)
    ctx=mp.get_context('spawn');answers=ctx.Queue();jobs={};processes={};records=[];peak=0
    try:
        for arm in selection.BANK_ORDER:
            jobs[arm]=ctx.Queue();p=ctx.Process(target=reference_worker,args=(arm,banks,spec,prepared,jobs[arm],answers,started))
            p.start();processes[arm]=p
        ready=[receive(answers,processes,guard) for _ in selection.BANK_ORDER]
        require({r['arm'] for r in ready}==set(selection.BANK_ORDER) and all(r.get('ready') for r in ready), 'Incomplete reference initialization')
        for depth in evaluation.DEPTHS:
            guard();source=next(r for r in prepared['contexts'].values() if r['depth']==depth);key=source['context_sha256']
            folder=STORE/f'depth-{depth}';folder.mkdir();batch=make_batch(fixture,depth);bp=folder/'batch.json';qp=folder/'queries.json'
            save(bp,batch);status('retained-native-query',depth=depth)
            native=subprocess.run([str(evaluation.EXES['query']),'queries',source['context_path'],str(bp),'-',str(qp)],
                capture_output=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
            require(native.returncode==0, 'Retained native query failed: '+native.stderr.decode(errors='replace')[-2000:])
            query=read(qp)
            require(query['batch_source']==bp.read_text() and query['context_source']==Path(source['context_path']).read_text(), 'Query identity differs')
            torch.cuda.empty_cache();torch.cuda.reset_peak_memory_stats()
            begin=time.monotonic();engines=[]
            for arm in selection.BANK_ORDER:
                rt=runtime[arm]
                engines.append(PlayedBank(documents[arm],rt['registry'],context_sha256=key,resources=rt['resources'],
                    weights_by_player=banks['arms'][arm]['weights_by_player'],completed_cycles=64,device='cuda',guard=guard))
            load_seconds=time.monotonic()-begin
            for arm in selection.BANK_ORDER:jobs[arm].put((depth,key,str(qp)))
            cuda=[];status('full-bank-reference-comparison',depth=depth,rows=len(query['observations']),cpu_reference_processes=4)
            for arm,engine in zip(selection.BANK_ORDER,engines):
                guard();begin=time.monotonic();p,s=engine.average(query,guard=guard);torch.cuda.synchronize()
                prefix=folder/arm
                np.save(str(prefix)+'-cuda-p.npy',p,allow_pickle=False);np.save(str(prefix)+'-cuda-s.npy',s,allow_pickle=False)
                cuda.append(dict(arm=arm,seconds=time.monotonic()-begin))
            refs=[receive(answers,processes,guard) for _ in selection.BANK_ORDER]
            require({r['arm'] for r in refs}==set(selection.BANK_ORDER) and all(r.get('depth')==depth for r in refs), 'Reference result identity differs')
            comparisons=[]
            for arm in selection.BANK_ORDER:
                prefix=folder/arm;reference=next(r for r in refs if r['arm']==arm)
                require(sha(str(prefix)+'-reference-p.npy')==reference['probability_sha256']
                    and sha(str(prefix)+'-reference-s.npy')==reference['support_sha256'], 'Changed worker reference output')
                arrays=[np.load(str(prefix)+suffix,allow_pickle=False) for suffix in
                    ('-cuda-p.npy','-cuda-s.npy','-reference-p.npy','-reference-s.npy')]
                comparisons.append(dict(arm=arm,**compare_arrays(*arrays)))
            reserved=torch.cuda.max_memory_reserved();peak=max(peak,reserved)
            require(reserved<=2_000_000_000, 'Actual full-bank reservation exceeds evaluation cap')
            records.append(dict(depth=depth,retained_distinct_deals=32,query_rows=len(query['observations']),
                simultaneous_loaded_banks=4,models_per_bank=64,cuda_load_seconds=load_seconds,cuda_averaging=cuda,
                cpu_reference=refs,comparisons=comparisons,peak_cuda_reserved_bytes=reserved))
            save(folder/'result.json',records[-1]);print(json.dumps(dict(stage='depth-qualified',depth=depth,peak_cuda_bytes=reserved)),flush=True)
            del engines,engine,p,s,query,arrays;gc.collect();torch.cuda.empty_cache()
            require(continuation.logical_bytes(STORE)<MAX_BYTES, 'Implementation-check evidence size bound')
        return records,peak
    finally:
        for q in jobs.values():q.put(None)
        for p in processes.values():
            p.join(timeout=60)
            if p.is_alive():
                # These are read-only implementation-check workers, never a
                # training cycle or the production application.
                p.terminate();p.join(timeout=10)
        if sys.exc_info()[0] is None:require(all(p.exitcode==0 for p in processes.values()), 'Reference process did not finish normally')


def main(run=False,prepare_only=False):
    if prepare_only:return prepare()
    if not run:
        print(json.dumps(dict(prepared_check=True,fixture_present=FIXTURE.exists(),control_present=CONTROL.exists(),
            terminal_training_present=pressure.RESULT.exists(),started=ATTEMPT.exists(),complete=RESULT.exists(),failed=FAILURE.exists())));return
    require(not any(p.exists() for p in (continuation.legacy.LOCK,continuation.legacy.OTHER,ATTEMPT,RESULT,FAILURE,STORE)), 'Live owner or started check; preserve without retry')
    control=read(CONTROL)
    require(control['passed'] and control['complete'] and control['runner_sha256']==sha(__file__), 'Resource-check software control required')
    continuation.legacy.verify(control['inputs'])
    fixture=read(FIXTURE);continuation.legacy.verify(fixture['inputs'])
    ready,probe=continuation.legacy.available()
    if not ready or psutil.virtual_memory().available<40_000_000_000:
        print(json.dumps(dict(deferred=True,probe=probe,check_started=False)));return
    banks,runtime,prepared,spec,paths=terminal_banks()
    accounting=inventory();require(sum(r['allocated_file_bytes'] for r in accounting)+MAX_BYTES<=800_000_000_000, 'Global evidence cap')
    paths.update((Path(__file__).resolve(),PLAN,FIXTURE,CONTROL,evaluation.EXES['query']))
    paths.update(Path(p) for p in prepared['artifacts'])
    paths.update(Path(p) for p in fixture['inputs'])
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(continuation.legacy.ROOT) and Path(p).suffix=='.py':paths.add(Path(p))
    inputs={str(p):sha(p) for p in paths}
    registration=dict(inputs=inputs,selection=banks,selection_sha256=hashlib.sha256(encoded(banks)).hexdigest(),
        depths=list(evaluation.DEPTHS),retained_deals=32,per_depth_batch_size_matches_evaluation=True,models_per_bank=64,
        maximum_seconds=MAX_SECONDS,maximum_cuda_bytes=2_000_000_000,maximum_logical_bytes=MAX_BYTES,
        cpu_reference_workers=4,new_scientific_deals=False,scientific_fits=False,production_modified=False)
    with continuation.legacy.LOCK.open('x') as f:f.write(str(os.getpid()))
    started=time.time()
    try:
        create(STORE);save(REG,registration);save(ATTEMPT,dict(pid=os.getpid(),process_created=psutil.Process().create_time(),
            started_unix=started,registration_sha256=sha(REG)))
        records,peak=run_check(banks,runtime,prepared,spec,fixture,started)
        continuation.legacy.verify(inputs)
        answer=dict(complete=True,passed=True,seconds=time.time()-started,registration_sha256=sha(REG),
            bank_selection_sha256=registration['selection_sha256'],full_played_banks_64=True,cuda_passed=True,
            reference_agreement_passed=True,maximum_cuda_reserved_bytes=peak,records=records,new_scientific_deals=False,
            scientific_fits=False,retained_training_hands=True,accuracy_evidence=False,production_modified=False,
            full_evaluation_runtime_estimated=False,storage=measure(STORE),inputs=inputs,
            artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()})
        save(RESULT,answer);status('full-bank-check-complete')
    except BaseException as error:
        if ATTEMPT.exists():save(FAILURE,dict(error=repr(error),traceback=traceback.format_exc(),preserve_evidence=True,automatic_retry_allowed=False))
        raise
    finally:
        if continuation.legacy.LOCK.exists() and continuation.legacy.LOCK.read_text()==str(os.getpid()):continuation.legacy.LOCK.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');parser.add_argument('--prepare',action='store_true')
    args=parser.parse_args();main(run=args.run,prepare_only=args.prepare)
