"""New paired short/long training-budget experiment on the fixed broad dataset."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',
                  CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONDONTWRITEBYTECODE='1')
import argparse
import gc
import json
from pathlib import Path
import random
import sys
import time
import traceback
import uuid
import numpy as np
import torch
import river_matched_training_pilot_v1 as pilot
import global_research_inventory_v3 as inventory_module
from stack_price_reference_v1 import board_group,price
from stack_price_reference_control_v1 import native,public_key,RANKS,NATIVE
from stack_price_learning_data_v2 import public_factors
from stack_price_learning_fit_v1 import Dataset,load_models,evaluate,MODEL_TYPE
from stack_price_learning_long_fit_v1 import fit_chain,CHECKPOINTS
from stack_board_batches_v1 import prepare_boards,load_boards

ROOT=pilot.ROOT;OUT=pilot.OUT;NAME='stack-board-training-budget-v1'
STORE=Path('S:/GTOpen-research')/NAME
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json');STATUS=OUT/(NAME+'-status.json')
GEOMETRY=Path('S:/GTOpen-research/stack-geometry-control-v1')
DEPTHS=(20,40,100,200,400);HELDOUT=(60,150);SEEDS=(9296701,9296702)
LIMIT=256_000_000;RESERVE=128_000_000;SECONDS=3600
read=pilot.read;sha=pilot.sha;write=pilot.atomic_json

def specification():
    previous=OUT/'stack-board-coverage-v1-registration.json';old=read(previous)
    rp=OUT/'stack-board-coverage-v1-result.json';result=read(rp)
    assert result['complete'] and result['registration_sha256']==sha(previous)
    review=OUT/'stack-board-coverage-v1-readback-v1.json';assert read(review)['passed']
    pilot.verify(old['inputs'])
    inventory_proof=OUT/'global-research-inventory-v3-control-v2.json';proof=read(inventory_proof)
    inventory_reg=OUT/'global-research-inventory-v3-registration-v2.json'
    assert proof['passed'] and proof['registration_sha256']==sha(inventory_reg)
    pilot.verify(read(inventory_reg)['inputs'])
    excluded={tuple(b) for b in old['excluded_probe_groups']}
    excluded.update(tuple(b['canonical_group']) for b in old['boards']);assert len(excluded)==596
    training=[b for b in result['board_records'] if b['split']=='fit'];assert len(training)==512
    training=sorted(training,key=lambda b:b['index']);assert [b['index'] for b in training]==list(range(512))
    for b in training:assert sha(b['file'])==b['sha256']
    rng=random.Random(9296700);seen=set(excluded);boards=[]
    while len(boards)<96:
        board=rng.sample(range(52),5);key=board_group(board)
        if key in seen:continue
        seen.add(key);i=len(boards)
        boards.append(dict(index=i,board=board,canonical_group=key,split='validation' if i<32 else 'test'))
    paths=[Path(__file__),OUT/'STACK-BOARD-TRAINING-BUDGET-PLAN.md',previous,rp,review,inventory_proof,inventory_reg,RANKS,NATIVE]
    paths.extend(Path(b['file']) for b in training)
    for d in (*DEPTHS,*HELDOUT):
        paths.extend((GEOMETRY/f'stack-{d}-public.json',GEOMETRY/'fixtures'/f'stack-{d}-context.json'))
    for mod in list(sys.modules.values()):
        p=getattr(mod,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py':paths.append(Path(p))
    return dict(format=1,inputs={str(p):sha(p) for p in paths},board_seed=9296700,boards=boards,
        excluded_probe_groups=sorted(excluded),reused_training_boards=training,seeds=list(SEEDS),
        fitting_depths=list(DEPTHS),heldout_depths=list(HELDOUT),arms={'short':8192,'long':32768},
        validation_boards=32,test_boards=64,fitting_boards=512,order=list(SEEDS),
        training_chains=2,selected_models=4,paired_shared_prefix=True,batch_size=4096,width=362,
        optimizer=dict(type='Adam',learning_rate=.001,betas=[.9,.999],eps=1e-8,weight_decay=0,foreach=False),
        validation_steps=list(CHECKPOINTS),selection='Lowest context-balanced normalized validation regret within each budget, then earliest step',
        relative_improvement_required=.2,heldout_mean_regret_stack_fraction_maximum=.001,
        near_indifference_stack_fraction=.0001,maximum_seconds=SECONDS,maximum_new_bytes=LIMIT,reserve_bytes=RESERVE,
        global_allocated_cap=pilot.GLOBAL_LIMIT,model_type=MODEL_TYPE,
        gpu_sharing='Light desktop permitted; production/heavy work first; research CUDA4GB, external headroom2GB.',
        scope='Restricted learning-budget diagnostic; no full-game or preflop accuracy qualification.',
        depth_limitation='60/150 excluded from fitting/selection; their geometry appeared in earlier experiments.',
        production_modified=False)

def main(run):
    spec=specification()
    if not run:
        print(json.dumps(dict(preflight_passed=True,reused_training_boards=512,new_validation_boards=32,
            new_test_boards=64,chains=2,selected_models=4,gpu_started=False)),flush=True);return
    assert not any(p.exists() for p in (STORE,REG,RESULT)),'Preserve earlier attempts'
    ready,probe=pilot.available();assert ready,'Other work has priority'
    started=time.monotonic();acquired=False
    try:
        with pilot.LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;pilot.STATUS=STATUS;pilot.status('storage_admission')
        inv_start=time.monotonic();inventory=inventory_module.measure();inventory_seconds=time.monotonic()-inv_start
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
        records,preparation=prepare_boards([b for b in spec['boards'] if b['split']=='validation'],STORE,guard,progress)
        train=Dataset(load_boards(spec['reused_training_boards']),contexts)
        validation=Dataset(load_boards(records),contexts)
        cache_bytes=sum(t.numel()*t.element_size() for d in (train,validation) for t in (d.cards,d.public,d.equity,d.economics,d.lengths_gpu,d.offsets_gpu))
        progress('data_ready',preparation_seconds=preparation['seconds'],cuda_dataset_bytes=cache_bytes)
        chains=[];fits=[]
        for seed in SEEDS:
            guard();progress('starting_chain',seed=seed,width=362,steps=32768)
            directory=STORE/f'seed-{seed}';pilot.create(directory)
            chain=fit_chain(seed,train,validation,directory,guard,progress)
            write(STORE/f'chain-{seed}.json',chain);chains.append(chain);fits.extend(chain['arms'])
        for seed in SEEDS:
            paired=[next(f for f in fits if f['seed']==seed and f['arm']==arm) for arm in ('short','long')]
            assert paired[0]['checkpoints']==paired[1]['checkpoints'][:4]
            assert [c['step'] for c in paired[0]['checkpoints']]==[0,1024,4096,8192]
            assert [c['step'] for c in paired[1]['checkpoints']]==list(CHECKPOINTS)
        selection=dict(registration_sha256=sha(REG),model_type=MODEL_TYPE,
            candidates=[dict(seed=f['seed'],width=362,arm=f['arm'],selected=f['selected']) for f in fits],
            paired_initial_weights_identical=True,paired_shared_prefix=True,
            test_labels_prepared=False,heldout_labels_prepared=False)
        chosen=STORE/'frozen-selection.json';write(chosen,selection)
        del train,validation;gc.collect();torch.cuda.empty_cache()
        progress('selection_frozen',selection_sha256=sha(chosen))
        test_records,test_preparation=prepare_boards([b for b in spec['boards'] if b['split']=='test'],STORE,guard,progress)
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
            paired=[next(t for t in tests if t['seed']==seed and t['arm']==arm) for arm in ('short','long')]
            groups=[[c for c in t['score']['contexts'] if c['stack'] in HELDOUT] for t in paired]
            before,after=[float(np.mean([c['mean_regret_stack_fraction'] for c in group])) for group in groups]
            absolute=all(c['mean_regret_stack_fraction']<=.001 for c in groups[1])
            gates.append(dict(seed=seed,baseline=before,candidate=after,relative_reduction=1-after/before if before>0 else None,
                absolute_gate=absolute,passed=bool(paired[1]['selected_step']>0 and before>0 and after<=.8*before and absolute)))
        pilot.verify(spec['inputs']);guard();storage=pilot.study_measure(STORE);assert storage['logical_bytes']<LIMIT
        result=dict(passed=True,complete=True,registration_sha256=sha(REG),selection=dict(file=str(chosen),sha256=sha(chosen)),
            chains=chains,fits=fits,tests=tests,diagnostic_gates=gates,diagnostic_gate_passed=all(g['passed'] for g in gates),
            board_records=records+test_records,preparation=preparation,test_preparation=test_preparation,
            inventory_seconds=inventory_seconds,cuda_dataset_bytes=cache_bytes,storage=storage,seconds=time.monotonic()-started,
            peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(),peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved(),
            resource_wait_seconds=resource.wait_seconds,artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()},
            training_started=True,final_test_evaluated=True,full_preflop_accuracy_qualified=False,production_modified=False)
        write(RESULT,result);progress('complete',diagnostic_gate_passed=result['diagnostic_gate_passed'])
        print(json.dumps(dict(gates=gates,seconds=result['seconds'],storage=storage,inventory_seconds=inventory_seconds,
            peak_cuda_allocated_bytes=result['peak_cuda_allocated_bytes'])),flush=True)
    except BaseException as error:
        write(OUT/(NAME+'-interruption-'+uuid.uuid4().hex[:8]+'.json'),dict(complete=False,error=repr(error),traceback=traceback.format_exc(),registration_sha256=sha(REG) if REG.exists() else None))
        raise
    finally:
        if acquired:
            assert pilot.LOCK.read_text()==str(os.getpid());pilot.LOCK.unlink()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');a=parser.parse_args();main(a.run)
