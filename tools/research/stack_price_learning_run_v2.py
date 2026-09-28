"""Registered exact-target 302/362-input CUDA learning comparison."""
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
import psutil
import torch
import river_matched_training_pilot_v1 as pilot
from owned_windows_job_v1 import OwnedJob
from stack_price_reference_v1 import board_group,conditional_counts,price
from stack_price_reference_control_v1 import native,public_key,RANKS,NATIVE
from stack_price_learning_data_v2 import card_factors,public_factors,qualify_native_inputs
from stack_price_learning_fit_v1 import Dataset,fresh,fit,load_models,evaluate,MODEL_TYPE

ROOT=pilot.ROOT;OUT=pilot.OUT;NAME='stack-price-learning-v2'
STORE=Path('S:/GTOpen-research')/NAME
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json');STATUS=OUT/(NAME+'-status.json')
GEOMETRY=Path('S:/GTOpen-research/stack-geometry-control-v1')
INPUT_CONTROL=Path('S:/GTOpen-research/stack-context-model-control-v1')
DEPTHS=(20,40,100,200,400);HELDOUT=(60,150);BOARD_SEED=9296500;SEEDS=(9296401,9296402)
LIMIT=512_000_000;RESERVE=128_000_000;SECONDS=3600
read=pilot.read;sha=pilot.sha;write=pilot.atomic_json

def worker(request):
    assert sys.stdin.readline().strip()=='OWNED_START'
    task=read(request);board=task['board'];index=task['index']
    raw=native(RANKS,board)
    hands=np.asarray([r['hand'] for r in raw['rows']],dtype=np.int64)
    ranks=np.asarray([r['rank'] for r in raw['rows']],dtype=np.int64)
    counts=conditional_counts(board,hands,ranks);factors=card_factors(board)
    assert np.array_equal(hands,factors['hands'])
    dest=STORE/f'board-{index}.npz'
    with dest.open('xb') as f:np.savez_compressed(f,features=factors['features'],counts=counts,
        hands=hands,canonical_cards=factors['canonical_cards'],lo_actor_zero=factors['lo_actor_zero'])
    print(json.dumps(dict(index=index,split=task['split'],board=board,canonical_group=board_group(board),
                         file=str(dest),sha256=sha(dest))),flush=True)

def prepare_boards(tasks,guard,progress):
    results=[];stopped=threading.Event()
    with OwnedJob() as job:
        def launch(task):
            if stopped.is_set():raise RuntimeError('Board workers cancelled')
            req=STORE/f"board-{task['index']}-request.json";write(req,task)
            env=dict(os.environ,CUDA_VISIBLE_DEVICES='-1')
            proc=subprocess.Popen([sys.executable,'-B',__file__,'--worker',str(req)],env=env,
                stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                job.assign(proc);stdout,stderr=proc.communicate(b'OWNED_START\n',timeout=120)
                if proc.returncode:raise RuntimeError(stderr.decode(errors='replace')[-3000:])
                return json.loads(stdout)
            except BaseException:
                if proc.poll() is None:proc.kill();proc.wait(timeout=10)
                raise
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures={pool.submit(launch,t) for t in tasks}
            try:
                while futures:
                    guard();done,futures=wait(futures,timeout=2,return_when=FIRST_COMPLETED)
                    for f in done:results.append(f.result())
                    if done:progress('preparing_boards',completed=len(results),total=len(tasks))
            except BaseException:
                stopped.set();job.close()
                for f in futures:f.cancel()
                raise
        accounting=job.accounting();assert accounting['active_processes']==0
    return sorted(results,key=lambda r:r['index']),accounting

def load_boards(records):
    rows=[]
    for ref in records:
        assert sha(ref['file'])==ref['sha256']
        with np.load(ref['file'],allow_pickle=False) as d:
            rows.append(dict(features=d['features'].copy(),counts=d['counts'].copy()))
    return rows

def specification():
    proof_path=OUT/'stack-price-reference-control-v1-result.json';proof=read(proof_path)
    proof_reg=OUT/'stack-price-reference-control-v1-registration.json'
    review=OUT/'stack-price-reference-control-v1-readback-v1.json'
    assert proof['passed'] and proof['registration_sha256']==sha(proof_reg) and read(review)['passed']
    pilot.verify(read(proof_reg)['inputs'])
    old=read(proof_reg);excluded={tuple(b) for b in old['probe_board_groups']};seen=set(excluded)
    rng=random.Random(BOARD_SEED);boards=[]
    while len(boards)<40:
        board=rng.sample(range(52),5);key=board_group(board)
        if key in seen:continue
        seen.add(key);i=len(boards);boards.append(dict(index=i,board=board,canonical_group=key,
            split='fit' if i<24 else 'validation' if i<32 else 'test'))
    paths=[Path(__file__),proof_path,proof_reg,review,RANKS,NATIVE,
        OUT/'STACK-PRICE-LEARNING-PLAN.md',OUT/'STACK-PRICE-LEARNING-REGISTRATION.md',OUT/'STACK-PRICE-LEARNING-V2-AMENDMENT.md',OUT/'stack-price-learning-v1-registration.json',ROOT/'tools/research/stack_price_learning_data_v1.py',ROOT/'tools/research/stack_price_learning_run_v1.py']
    input_result=OUT/'stack-context-model-control-v1-result.json';pr=read(input_result);assert pr['passed']
    paths.append(input_result)
    for p,h in pr['artifacts'].items():
        if p.endswith('queries.json') or p.endswith('retained-deals.json'):
            assert sha(p)==h;paths.append(Path(p))
    for depth in (*DEPTHS,*HELDOUT):
        paths.extend([GEOMETRY/f'stack-{depth}-public.json',GEOMETRY/'fixtures'/f'stack-{depth}-context.json'])
    paths.extend([ROOT/'crates/solver/examples/research_sampled/observation_v1.rs'])
    for mod in list(sys.modules.values()):
        p=getattr(mod,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py':paths.append(Path(p))
    return dict(format=1,inputs={str(p):sha(p) for p in paths},board_seed=BOARD_SEED,boards=boards,
        excluded_probe_groups=sorted(excluded),seeds=list(SEEDS),fitting_depths=list(DEPTHS),heldout_depths=list(HELDOUT),
        order=[[SEEDS[0],302],[SEEDS[0],362],[SEEDS[1],362],[SEEDS[1],302]],
        steps=8192,batch_size=4096,optimizer=dict(type='Adam',learning_rate=.001,betas=[.9,.999],eps=1e-8,weight_decay=0,foreach=False),
        validation_steps=[0,1024,4096,8192],selection='Lowest context-balanced normalized validation regret, then earliest step',
        relative_improvement_required=.2,heldout_mean_regret_stack_fraction_maximum=.001,
        near_indifference_stack_fraction=.0001,maximum_seconds=SECONDS,maximum_new_bytes=LIMIT,reserve_bytes=RESERVE,
        global_allocated_cap=pilot.GLOBAL_LIMIT,model_type=MODEL_TYPE,
        gpu_sharing='Light desktop permitted; active production/heavy work has priority; 4GB research CUDA, 2GB external headroom.',
        scope='Restricted exact-target river decision learning; no full-game or preflop accuracy qualification',production_modified=False)

def main(run):
    spec=specification()
    if not run:
        print(json.dumps(dict(preflight_passed=True,boards=40,fits=4,gpu_started=False)),flush=True);return
    assert not any(p.exists() for p in (REG,RESULT,STORE)), 'Preserve earlier attempts'
    ready,probe=pilot.available();assert ready,'Production or other resources have priority'
    started=time.monotonic();acquired=False
    try:
        with pilot.LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True
        pilot.STATUS=STATUS;pilot.status('storage_admission')
        inventory=pilot.global_measure();allocated=sum(r['allocated_file_bytes'] for r in inventory)
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
            pilot.status(stage,**values)
            print(json.dumps(dict(stage=stage,**values)),flush=True)
        guard();qualification=qualify_native_inputs(INPUT_CONTROL,GEOMETRY)
        write(STORE/'feature-qualification.json',qualification);progress('features_qualified',observations=qualification['native_observations_checked'])
        contexts=[public_factors(read(GEOMETRY/f'stack-{d}-public.json')) for d in DEPTHS]
        board_records,job=prepare_boards([b for b in spec['boards'] if b['split']!='test'],guard,progress)
        train=Dataset(load_boards([b for b in board_records if b['split']=='fit']),contexts)
        validation=Dataset(load_boards([b for b in board_records if b['split']=='validation']),contexts)
        init_errors=[]
        for seed in SEEDS:
            first=fresh(seed,302,'cpu');second=fresh(seed,362,'cpu')
            x=torch.as_tensor(train.card_np[:128]+contexts[0]['features'][0])
            with torch.no_grad():
                error=max(float((first[a](x[:,:302])-second[a](x)).abs().max()) for a in (0,1))
            assert error<1e-7;init_errors.append(error)
        write(STORE/'initial-function-qualification.json',dict(passed=True,maximum_errors=init_errors))
        fits=[]
        for seed,width in spec['order']:
            guard();progress('starting_fit',seed=seed,width=width)
            result=fit(seed,width,train,validation,STORE,guard,progress)
            write(STORE/f'fit-{seed}-{width}.json',result);fits.append(result)
        selected=dict(registration_sha256=sha(REG),model_type=MODEL_TYPE,
            candidates=[dict(seed=r['seed'],width=r['width'],selected=r['selected']) for r in fits],
            test_labels_prepared=False,heldout_labels_prepared=False)
        selection_path=STORE/'frozen-selection.json';write(selection_path,selected)
        del train,validation,first,second,x;gc.collect();torch.cuda.empty_cache()
        progress('selection_frozen',selection_sha256=sha(selection_path))
        # Only now prepare test boards and held-out terminal labels.
        test_records,test_job=prepare_boards([b for b in spec['boards'] if b['split']=='test'],guard,progress)
        heldout=[]
        for d in HELDOUT:
            guard();ledger=read(GEOMETRY/f'stack-{d}-public.json')
            terminal=native(NATIVE,['control',GEOMETRY/'fixtures'/f'stack-{d}-context.json'])
            assert terminal['passed'];write(STORE/f'heldout-{d}-native-terminal.json',terminal)
            public=public_factors(ledger);lookup={public_key(r):r for r in terminal['templates'] if r['legal_actions']==2}
            assert set(lookup)=={r['hi'] for r in public['rows']}
            for row in public['rows']:
                ref=price(row);actual=lookup[row['hi']]
                assert actual['actor']==row['actor'] and actual['call_ends_showdown']
                assert np.max(abs(np.asarray(ref['endpoints_loss_tie_win'])-actual['endpoints_loss_tie_win']))<1e-9
            heldout.append(public)
        test_boards=load_boards(test_records);test=Dataset(test_boards,contexts+heldout)
        tests=[]
        for candidate in selected['candidates']:
            guard();seed,width=candidate['seed'],candidate['width'];models=load_models(candidate['selected']['weights'],seed,width)
            progress('final_test',seed=seed,width=width)
            score=evaluate(models,test,width,guard,detail=True)
            record=dict(seed=seed,width=width,selected_step=candidate['selected']['step'],score=score)
            write(STORE/f'test-{seed}-{width}.json',record);tests.append(record)
            del models;gc.collect()
        gates=[]
        for seed in SEEDS:
            old=next(r for r in tests if r['seed']==seed and r['width']==302)
            new=next(r for r in tests if r['seed']==seed and r['width']==362)
            before=[c for c in old['score']['contexts'] if c['stack'] in HELDOUT]
            after=[c for c in new['score']['contexts'] if c['stack'] in HELDOUT]
            baseline=float(np.mean([c['mean_regret_stack_fraction'] for c in before]))
            candidate=float(np.mean([c['mean_regret_stack_fraction'] for c in after]))
            relative=1-candidate/baseline if baseline>0 else None
            absolute=all(c['mean_regret_stack_fraction']<=.001 for c in after)
            gates.append(dict(seed=seed,baseline=baseline,candidate=candidate,relative_reduction=relative,
                absolute_gate=absolute,passed=bool(new['selected_step']>0 and baseline>0 and candidate<=.8*baseline and absolute)))
        pilot.verify(spec['inputs']);guard();storage=pilot.study_measure(STORE);assert storage['logical_bytes']<LIMIT
        result=dict(passed=True,complete=True,registration_sha256=sha(REG),feature_qualification=qualification,
            initial_function_maximum_errors=init_errors,selection=dict(file=str(selection_path),sha256=sha(selection_path)),
            fits=fits,tests=tests,diagnostic_gates=gates,diagnostic_gate_passed=all(g['passed'] for g in gates),
            board_records=board_records+test_records,worker_jobs=[job,test_job],storage=storage,seconds=time.monotonic()-started,
            peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(),peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved(),
            resource_wait_seconds=resource.wait_seconds,artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()},
            training_started=True,final_test_evaluated=True,full_preflop_accuracy_qualified=False,production_modified=False)
        write(RESULT,result);progress('complete',diagnostic_gate_passed=result['diagnostic_gate_passed'])
        print(json.dumps(dict(gates=gates,seconds=result['seconds'],storage=storage,
            peak_cuda_allocated_bytes=result['peak_cuda_allocated_bytes'])),flush=True)
    except BaseException as error:
        write(OUT/(NAME+'-interruption-'+uuid.uuid4().hex[:8]+'.json'),dict(error=repr(error),traceback=traceback.format_exc(),
            registration_sha256=sha(REG) if REG.exists() else None,complete=False))
        raise
    finally:
        if acquired:
            assert pilot.LOCK.read_text()==str(os.getpid());pilot.LOCK.unlink()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');parser.add_argument('--worker')
    a=parser.parse_args()
    if a.worker:worker(a.worker)
    else:main(a.run)
