"""Fixed-network 24-vs-512 fitting-board learning experiment, two paired seeds."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',
                  CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONDONTWRITEBYTECODE='1')
import argparse
from concurrent.futures import ThreadPoolExecutor,wait,FIRST_COMPLETED
import gc
import json
from pathlib import Path
import random
import subprocess
import sys
import threading
import time
import traceback
import uuid
import numpy as np
import torch
import river_matched_training_pilot_v1 as pilot
from owned_windows_job_v1 import OwnedJob
from stack_price_reference_v1 import board_group,conditional_counts,price
from stack_price_reference_control_v1 import native,public_key,RANKS,NATIVE
from stack_price_learning_data_v2 import card_factors,public_factors
from stack_price_learning_fit_v1 import Dataset,fit,load_models,evaluate,MODEL_TYPE

ROOT=pilot.ROOT;OUT=pilot.OUT;NAME='stack-board-coverage-v1'
STORE=Path('S:/GTOpen-research')/NAME
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json');STATUS=OUT/(NAME+'-status.json')
GEOMETRY=Path('S:/GTOpen-research/stack-geometry-control-v1')
DEPTHS=(20,40,100,200,400);HELDOUT=(60,150);SEEDS=(9296601,9296602)
LIMIT=256_000_000;RESERVE=128_000_000;SECONDS=3600
read=pilot.read;sha=pilot.sha;write=pilot.atomic_json

def worker(request):
    assert sys.stdin.readline().strip()=='OWNED_START'
    tasks=read(request);records=[]
    for task in tasks:
        start=time.monotonic();board=task['board'];index=task['index']
        raw=native(RANKS,board)
        hands=np.asarray([r['hand'] for r in raw['rows']],dtype=np.int64)
        ranks=np.asarray([r['rank'] for r in raw['rows']],dtype=np.int64)
        counts=conditional_counts(board,hands,ranks);factors=card_factors(board)
        assert np.array_equal(hands,factors['hands']) and np.all(counts.sum(1)==990)
        dest=STORE/f'board-{index}.npz'
        with dest.open('xb') as f:np.savez_compressed(f,features=factors['features'],counts=counts,
            hands=hands,canonical_cards=factors['canonical_cards'],lo_actor_zero=factors['lo_actor_zero'])
        records.append(dict(index=index,split=task['split'],board=board,canonical_group=board_group(board),
            file=str(dest),sha256=sha(dest),preparation_seconds=time.monotonic()-start))
    print(json.dumps(records),flush=True)

def prepare_boards(tasks,guard,progress):
    started=time.monotonic();results=[];cancel=threading.Event()
    # Import the helper stack once per batch instead of once per board.
    batches=[tasks[i::8] for i in range(min(8,len(tasks)))]
    with OwnedJob() as job:
        def launch(batch):
            if cancel.is_set():raise RuntimeError('Preparation cancelled')
            req=STORE/f"batch-{batch[0]['index']}-request.json";write(req,batch)
            proc=subprocess.Popen([sys.executable,'-B',__file__,'--worker',str(req)],
                env=dict(os.environ,CUDA_VISIBLE_DEVICES='-1'),stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                job.assign(proc);stdout,stderr=proc.communicate(b'OWNED_START\n',timeout=900)
                if proc.returncode:raise RuntimeError(stderr.decode(errors='replace')[-3000:])
                rows=json.loads(stdout)
                assert sorted(r['index'] for r in rows)==sorted(t['index'] for t in batch)
                return rows
            except BaseException:
                if proc.poll() is None:proc.kill();proc.wait(timeout=10)
                raise
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures={pool.submit(launch,b) for b in batches}
            try:
                while futures:
                    guard();done,futures=wait(futures,timeout=2,return_when=FIRST_COMPLETED)
                    for future in done:results.extend(future.result())
                    if done:progress('preparing_boards',completed=len(results),total=len(tasks))
            except BaseException:
                cancel.set();job.close()
                for future in futures:future.cancel()
                raise
        accounting=job.accounting();assert accounting['active_processes']==0
    return sorted(results,key=lambda r:r['index']),dict(seconds=time.monotonic()-started,job=accounting)

def load_boards(records):
    result=[]
    for ref in records:
        assert sha(ref['file'])==ref['sha256']
        with np.load(ref['file'],allow_pickle=False) as d:
            assert d['features'].shape==(1081,362) and d['counts'].shape==(1081,3)
            assert np.isfinite(d['features']).all() and np.all(d['counts'].sum(1)==990)
            result.append(dict(features=d['features'].copy(),counts=d['counts'].copy()))
    return result

def specification():
    previous=OUT/'stack-price-learning-v2-registration.json';old=read(previous)
    result_path=OUT/'stack-price-learning-v2-result.json';result=read(result_path)
    assert result['complete'] and result['registration_sha256']==sha(previous)
    assert result['feature_qualification']['maximum_visible_feature_error']==0
    review=OUT/'stack-price-learning-v2-readback-v1.json';assert read(review)['passed']
    diagnosis=OUT/'stack-price-learning-diagnosis-v1-result.json';assert read(diagnosis)['passed']
    pilot.verify(old['inputs'])
    excluded={tuple(b) for b in old['excluded_probe_groups']}
    excluded.update(tuple(b['canonical_group']) for b in old['boards'])
    assert len(excluded)==52
    rng=random.Random(9296600);seen=set(excluded);boards=[]
    while len(boards)<544:
        board=rng.sample(range(52),5);key=board_group(board)
        if key in seen:continue
        seen.add(key);i=len(boards)
        boards.append(dict(index=i,board=board,canonical_group=key,
            split='fit' if i<512 else 'validation' if i<528 else 'test'))
    paths=[Path(__file__),OUT/'STACK-BOARD-COVERAGE-PLAN.md',previous,result_path,review,diagnosis,RANKS,NATIVE]
    for d in (*DEPTHS,*HELDOUT):
        paths.extend((GEOMETRY/f'stack-{d}-public.json',GEOMETRY/'fixtures'/f'stack-{d}-context.json'))
    for mod in list(sys.modules.values()):
        p=getattr(mod,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py':paths.append(Path(p))
    return dict(format=1,inputs={str(p):sha(p) for p in paths},board_seed=9296600,boards=boards,
        excluded_probe_groups=sorted(excluded),seeds=list(SEEDS),fitting_depths=list(DEPTHS),heldout_depths=list(HELDOUT),
        arms={'narrow':24,'broad':512},validation_boards=16,test_boards=16,
        order=[[SEEDS[0],'narrow'],[SEEDS[0],'broad'],[SEEDS[1],'broad'],[SEEDS[1],'narrow']],
        steps=8192,batch_size=4096,width=362,optimizer=dict(type='Adam',learning_rate=.001,betas=[.9,.999],eps=1e-8,weight_decay=0,foreach=False),
        validation_steps=[0,1024,4096,8192],selection='Lowest context-balanced normalized validation regret, then earliest step',
        relative_improvement_required=.2,heldout_mean_regret_stack_fraction_maximum=.001,
        near_indifference_stack_fraction=.0001,maximum_seconds=SECONDS,maximum_new_bytes=LIMIT,reserve_bytes=RESERVE,
        global_allocated_cap=pilot.GLOBAL_LIMIT,model_type=MODEL_TYPE,
        gpu_sharing='Light desktop permitted; production/heavy work first; research CUDA4GB, external headroom2GB.',
        scope='Restricted board-coverage learning diagnostic; no full-game or preflop accuracy qualification.',
        depth_limitation='60/150 excluded from this fitting/selection, but their geometry was evaluated in the earlier trial.',
        production_modified=False)

def main(run):
    spec=specification()
    if not run:
        print(json.dumps(dict(preflight_passed=True,boards=544,fits=4,gpu_started=False)),flush=True);return
    assert not any(p.exists() for p in (STORE,REG,RESULT)),'Preserve prior attempts'
    ready,probe=pilot.available();assert ready,'Other work has priority'
    started=time.monotonic();acquired=False
    try:
        with pilot.LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;pilot.STATUS=STATUS;pilot.status('storage_admission')
        inv_start=time.monotonic();inventory=pilot.global_measure();inventory_seconds=time.monotonic()-inv_start
        allocated=sum(r['allocated_file_bytes'] for r in inventory)
        assert allocated+LIMIT+RESERVE<=pilot.GLOBAL_LIMIT
        write(REG,spec);pilot.create(STORE);write(STORE/'admission.json',dict(inventory=inventory,allocated_bytes=allocated,gpu=probe))
        pilot.STORE=STORE;pilot.LIMIT=LIMIT
        torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        torch.cuda.set_per_process_memory_fraction(pilot.CUDA_BUDGET_BYTES/torch.cuda.get_device_properties(0).total_memory)
        resource=pilot.Guard()
        def guard():
            assert time.monotonic()-started<SECONDS,'Registered one-hour execution limit'
            resource()
        def progress(stage,**values):
            pilot.status(stage,**values);print(json.dumps(dict(stage=stage,**values)),flush=True)
        guard();contexts=[public_factors(read(GEOMETRY/f'stack-{d}-public.json')) for d in DEPTHS]
        records,preparation=prepare_boards([b for b in spec['boards'] if b['split']!='test'],guard,progress)
        fit_records=[b for b in records if b['split']=='fit'];fit_boards=load_boards(fit_records)
        datasets={name:Dataset(fit_boards[:count],contexts) for name,count in spec['arms'].items()}
        validation=Dataset(load_boards([b for b in records if b['split']=='validation']),contexts)
        cache_bytes={name:sum(t.numel()*t.element_size() for t in (d.cards,d.public,d.equity,d.economics,d.lengths_gpu,d.offsets_gpu)) for name,d in datasets.items()}
        progress('data_ready',preparation_seconds=preparation['seconds'],cuda_dataset_bytes=cache_bytes)
        fits=[]
        for seed,arm in spec['order']:
            guard();progress('starting_fit',seed=seed,arm=arm,width=362)
            checkpoint_dir=STORE/f'{seed}-{arm}';pilot.create(checkpoint_dir)
            def fit_progress(stage,**values):progress(stage,arm=arm,**values)
            fitted=fit(seed,362,datasets[arm],validation,checkpoint_dir,guard,fit_progress)
            fitted['arm']=arm;fitted['fitting_boards']=spec['arms'][arm]
            write(STORE/f'fit-{seed}-{arm}.json',fitted);fits.append(fitted)
        for seed in SEEDS:
            paired=[next(f for f in fits if f['seed']==seed and f['arm']==arm) for arm in ('narrow','broad')]
            with np.load(paired[0]['checkpoints'][0]['weights']['file'],allow_pickle=False) as a,np.load(paired[1]['checkpoints'][0]['weights']['file'],allow_pickle=False) as b:
                assert a.files==b.files and all(np.array_equal(a[key],b[key]) for key in a.files),'Paired initial weights differ'
        selection=dict(registration_sha256=sha(REG),model_type=MODEL_TYPE,
            candidates=[dict(seed=f['seed'],width=362,arm=f['arm'],selected=f['selected']) for f in fits],
            paired_initial_weights_identical=True,test_labels_prepared=False,heldout_labels_prepared=False)
        chosen=STORE/'frozen-selection.json';write(chosen,selection)
        del datasets,validation,fit_boards;gc.collect();torch.cuda.empty_cache()
        progress('selection_frozen',selection_sha256=sha(chosen))
        test_records,test_preparation=prepare_boards([b for b in spec['boards'] if b['split']=='test'],guard,progress)
        heldout=[]
        for depth in HELDOUT:
            guard();public=public_factors(read(GEOMETRY/f'stack-{depth}-public.json'))
            terminal=native(NATIVE,['control',GEOMETRY/'fixtures'/f'stack-{depth}-context.json'])
            assert terminal['passed'];write(STORE/f'heldout-{depth}-native-terminal.json',terminal)
            lookup={public_key(r):r for r in terminal['templates'] if r['legal_actions']==2}
            assert set(lookup)=={r['hi'] for r in public['rows']}
            for row in public['rows']:
                reference=price(row);actual=lookup[row['hi']]
                assert actual['actor']==row['actor'] and actual['call_ends_showdown']
                assert np.max(abs(np.asarray(reference['endpoints_loss_tie_win'])-actual['endpoints_loss_tie_win']))<1e-9
            heldout.append(public)
        test=Dataset(load_boards(test_records),contexts+heldout);tests=[]
        for c in selection['candidates']:
            guard();progress('final_test',seed=c['seed'],arm=c['arm'])
            model=load_models(c['selected']['weights'],c['seed'],362)
            record=dict(seed=c['seed'],width=362,arm=c['arm'],selected_step=c['selected']['step'],score=evaluate(model,test,362,guard,detail=True))
            write(STORE/f"test-{c['seed']}-{c['arm']}.json",record);tests.append(record)
            del model;gc.collect()
        gates=[]
        for seed in SEEDS:
            paired=[next(t for t in tests if t['seed']==seed and t['arm']==arm) for arm in ('narrow','broad')]
            groups=[[c for c in t['score']['contexts'] if c['stack'] in HELDOUT] for t in paired]
            before,after=[float(np.mean([c['mean_regret_stack_fraction'] for c in group])) for group in groups]
            absolute=all(c['mean_regret_stack_fraction']<=.001 for c in groups[1])
            gates.append(dict(seed=seed,baseline=before,candidate=after,relative_reduction=1-after/before if before>0 else None,
                absolute_gate=absolute,passed=bool(paired[1]['selected_step']>0 and before>0 and after<=.8*before and absolute)))
        pilot.verify(spec['inputs']);guard();storage=pilot.study_measure(STORE);assert storage['logical_bytes']<LIMIT
        result=dict(passed=True,complete=True,registration_sha256=sha(REG),selection=dict(file=str(chosen),sha256=sha(chosen)),
            fits=fits,tests=tests,diagnostic_gates=gates,diagnostic_gate_passed=all(g['passed'] for g in gates),
            board_records=records+test_records,preparation=preparation,test_preparation=test_preparation,
            inventory_seconds=inventory_seconds,cuda_dataset_bytes=cache_bytes,storage=storage,seconds=time.monotonic()-started,
            peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(),peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved(),
            resource_wait_seconds=resource.wait_seconds,artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()},
            training_started=True,final_test_evaluated=True,full_preflop_accuracy_qualified=False,production_modified=False)
        write(RESULT,result);progress('complete',diagnostic_gate_passed=result['diagnostic_gate_passed'])
        print(json.dumps(dict(gates=gates,seconds=result['seconds'],storage=storage,preparation_seconds=preparation['seconds'],
            peak_cuda_allocated_bytes=result['peak_cuda_allocated_bytes'])),flush=True)
    except BaseException as error:
        write(OUT/(NAME+'-interruption-'+uuid.uuid4().hex[:8]+'.json'),dict(complete=False,error=repr(error),traceback=traceback.format_exc(),registration_sha256=sha(REG) if REG.exists() else None))
        raise
    finally:
        if acquired:
            assert pilot.LOCK.read_text()==str(os.getpid());pilot.LOCK.unlink()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');parser.add_argument('--worker');a=parser.parse_args()
    if a.worker:worker(a.worker)
    else:main(a.run)
