"""Frozen paired feature experiment with separately admitted CPU preparation."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',
                  CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONDONTWRITEBYTECODE='1')
import argparse,gc,json
from pathlib import Path
import random,sys,time,traceback,uuid
import numpy as np
import torch
import river_matched_training_pilot_v1 as pilot
from global_research_inventory_v3 import measure as inventory
from stack_price_reference_v1 import board_group,price
from stack_price_reference_control_v1 import native,public_key,NATIVE,RANKS
from stack_price_learning_data_v2 import public_factors
from stack_price_learning_fit_v1 import Dataset,scores,evaluate
from stack_board_relative_model_v1 import fresh,fit,load_models,MODEL_TYPE,CHECKPOINTS
from stack_board_relative_data_v1 import prepare,load,extended_context,cpu_admission,Guard

ROOT=pilot.ROOT;OUT=pilot.OUT;NAME='stack-board-relative-learning-v1'
STORE=Path('S:/GTOpen-research')/NAME
REG=OUT/(NAME+'-registration.json');PREPARED=OUT/(NAME+'-prepared.json')
RESULT=OUT/(NAME+'-result.json');STATUS=OUT/(NAME+'-status.json')
GEOMETRY=Path('S:/GTOpen-research/stack-geometry-control-v1')
DEPTHS=(20,40,100,200,400);HELDOUT=(60,150);SEEDS=(9296901,9296902)
ORDER=((SEEDS[0],362),(SEEDS[0],387),(SEEDS[1],387),(SEEDS[1],362))
LIMIT=256_000_000;RESERVE=128_000_000;SECONDS=3600
read=pilot.read;sha=pilot.sha;write=pilot.atomic_json

def progress(state,**values):
    pilot.STATUS=STATUS;pilot.status(state,**values)
    print(json.dumps(dict(state=state,**values)),flush=True)

def specification():
    previous=OUT/'stack-board-training-budget-v1-registration.json';old=read(previous)
    review=OUT/'stack-board-training-budget-v1-readback-v1.json';assert read(review)['passed']
    diagnosis=OUT/'stack-board-error-diagnosis-v2-result.json';assert read(diagnosis)['passed']
    excluded={tuple(v) for v in old['excluded_probe_groups']}
    excluded.update(tuple(b['canonical_group']) for b in old['boards']);assert len(excluded)==692
    training=old['reused_training_boards'];assert len(training)==512 and all(b['split']=='fit' for b in training)
    assert [b['index'] for b in training]==list(range(512))
    for b in training:assert sha(b['file'])==b['sha256']
    paths=[Path(__file__),previous,review,diagnosis,NATIVE,RANKS,
        OUT/'STACK-BOARD-RELATIVE-FEATURES-PLAN.md',OUT/'STACK-BOARD-RELATIVE-IMPLEMENTATION.md']
    for prefix in ('global-research-inventory-v3','stack-board-relative-feature-control-v1','stack-board-relative-model-control-v1'):
        suffix='-control-v2.json' if prefix=='global-research-inventory-v3' else '-result.json'
        pr=OUT/(prefix+suffix);proof=read(pr);assert proof['passed']
        rp=OUT/(prefix+('-registration-v2.json' if prefix=='global-research-inventory-v3' else '-registration.json'))
        assert proof['registration_sha256']==sha(rp);pilot.verify(read(rp)['inputs']);paths.extend((pr,rp))
        if prefix=='stack-board-relative-model-control-v1':
            assert proof['cpu_initial_outputs_exact'] and proof['extra_columns_learnable'] and proof['checkpoint_round_trips_exact']
    rng=random.Random(9296900);seen=set(excluded);boards=[]
    while len(boards)<96:
        b=rng.sample(range(52),5);key=board_group(b)
        if key in seen:continue
        seen.add(key);i=len(boards)
        boards.append(dict(index=i,board=b,canonical_group=key,split='validation' if i<32 else 'test'))
    paths.extend(Path(b['file']) for b in training)
    for d in (*DEPTHS,*HELDOUT):paths.extend((GEOMETRY/f'stack-{d}-public.json',GEOMETRY/'fixtures'/f'stack-{d}-context.json'))
    for mod in list(sys.modules.values()):
        p=getattr(mod,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py':paths.append(Path(p))
    return dict(format=1,inputs={str(p):sha(p) for p in paths},model_type=MODEL_TYPE,
        board_seed=9296900,seeds=list(SEEDS),order=list(ORDER),boards=boards,excluded_probe_groups=sorted(excluded),
        reused_training_boards=training,fitting_boards=512,validation_boards=32,test_boards=64,
        fitting_depths=list(DEPTHS),heldout_depths=list(HELDOUT),widths=[362,387],feature_extension_columns=25,
        hidden_layers=[64,64],extra_parameters_total=3200,initial_extension_weights_zero=True,
        first_layer='Original362-column GEMM plus separate25-column extension; exact neutral initial computation',
        steps=8192,batch_size=4096,validation_steps=list(CHECKPOINTS),
        optimizer=dict(type='Adam',learning_rate=.001,betas=[.9,.999],eps=1e-8,weight_decay=0,foreach=False),
        selection='Minimum context-balanced normalized validation regret; tie earliest checkpoint',
        relative_improvement_required=.2,heldout_mean_regret_stack_fraction_maximum=.001,
        near_indifference_stack_fraction=.0001,maximum_seconds=SECONDS,maximum_preparation_seconds=600,
        maximum_new_bytes=LIMIT,reserve_bytes=RESERVE,global_allocated_cap=pilot.GLOBAL_LIMIT,
        preparation_workers=8,initial_gpu_batch_controls=3,initial_gpu_batch_rows=1024,
        gpu_sharing='Light desktop permitted; production/heavy work first; research CUDA4GB, external headroom2GB',
        scope='Restricted representation comparison; no full-game or preflop qualification',
        depth_limitation='60/150 excluded from fitting/selection; their geometry appeared in earlier experiments',
        production_modified=False)

def admit_inventory():
    started=time.monotonic();rows=inventory();allocated=sum(r['allocated_file_bytes'] for r in rows)
    assert allocated+LIMIT+RESERVE<=pilot.GLOBAL_LIMIT
    return dict(inventory=rows,allocated_bytes=allocated,seconds=time.monotonic()-started)

def prepare_stage(spec):
    assert not any(p.exists() for p in (REG,PREPARED,RESULT,STORE)),'Preserve existing attempts'
    probe=cpu_admission()
    if not probe['admitted']:
        print(json.dumps(dict(state='deferred_before_preparation',probe=probe)),flush=True);return
    started=time.monotonic()
    with pilot.LOCK.open('x') as f:f.write(str(os.getpid()))
    try:
        progress('preparation_inventory');accounting=admit_inventory()
        write(REG,spec);pilot.create(STORE);write(STORE/'cpu-admission.json',dict(accounting=accounting,probe=probe))
        guard=Guard(STORE,600-(time.monotonic()-started),progress)
        tasks=spec['reused_training_boards']+[b for b in spec['boards'] if b['split']=='validation']
        records,timing=prepare(tasks,STORE,guard,progress)
        assert sorted((b['split'],b['index']) for b in records)==sorted((b['split'],b['index']) for b in tasks)
        # Qualify complete assembled prefixes/counts/order in bounded chunks.
        for lo in range(0,len(records),16):
            guard();chunk=load(records[lo:lo+16]);del chunk
        for depth in DEPTHS:extended_context(public_factors(read(GEOMETRY/f'stack-{depth}-public.json')))
        pilot.verify(spec['inputs']);guard();assert not torch.cuda.is_initialized()
        size=pilot.study_measure(STORE);assert size['logical_bytes']<LIMIT
        result=dict(passed=True,complete=True,registration_sha256=sha(REG),records=records,preparation=timing,
            seconds=time.monotonic()-started,inventory_seconds=accounting['seconds'],storage=size,
            original_feature_prefixes_exact=True,original_counts_retained=True,public_padding_and_actors_checked=True,
            gpu_used=False,training_started=False,test_labels_prepared=False,
            artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()})
        assert result['seconds']<600
        write(PREPARED,result);progress('prepared_for_gpu',seconds=result['seconds'],boards=len(records),gpu_used=False)
    except BaseException as error:
        write(OUT/(NAME+'-prepare-interruption-'+uuid.uuid4().hex[:8]+'.json'),dict(error=repr(error),traceback=traceback.format_exc()))
        raise
    finally:
        assert pilot.LOCK.read_text()==str(os.getpid());pilot.LOCK.unlink()

def gpu_pair_control(data,seed):
    left=fresh(seed,362,'cuda');right=fresh(seed,387,'cuda')
    generators=[torch.Generator(device='cuda').manual_seed(seed+100000) for _ in range(2)]
    for _ in range(3):
        x0,a0,y0=data.sample(1024,362,generators[0]);x1,a1,y1=data.sample(1024,387,generators[1])
        assert torch.equal(x0,x1[:,:362]) and torch.equal(a0,a1) and torch.equal(y0,y1)
        with torch.no_grad():assert torch.equal(scores(left,x0,a0),scores(right,x1,a1))
    del left,right;gc.collect()
    return dict(seed=seed,rows=3072,common_inputs_actors_targets_exact=True,initial_scores_exact=True)

def training_stage(spec):
    assert read(REG)==json.loads(json.dumps(spec)),'Frozen specification changed'
    prepared=read(PREPARED);assert prepared['passed'] and prepared['complete'] and prepared['registration_sha256']==sha(REG)
    assert not prepared['training_started'] and not prepared['test_labels_prepared']
    pilot.verify(prepared['artifacts']);pilot.verify(spec['inputs'])
    expected={(b['split'],b['index']):(b['board'],list(b['canonical_group'])) for b in spec['reused_training_boards']+spec['boards'] if b['split']!='test'}
    assert len(prepared['records'])==len(expected)
    for b in prepared['records']:assert (b['board'],b['canonical_group'])==expected[(b['split'],b['index'])]
    attempt=STORE/'gpu-attempt.json'
    assert not RESULT.exists() and not attempt.exists(),'Do not silently restart a started scientific attempt'
    ready,probe=pilot.available()
    if not ready:
        print(json.dumps(dict(state='prepared_waiting_for_gpu',gpu=probe,training_started=False)),flush=True);return
    started=time.monotonic()
    with pilot.LOCK.open('x') as f:f.write(str(os.getpid()))
    try:
        progress('gpu_inventory');accounting=admit_inventory()
        write(attempt,dict(registration_sha256=sha(REG),preparation_sha256=sha(PREPARED),probe=probe,accounting=accounting))
        remaining=SECONDS-prepared['seconds']-(time.monotonic()-started);assert remaining>0
        torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        torch.cuda.set_per_process_memory_fraction(pilot.CUDA_BUDGET_BYTES/torch.cuda.get_device_properties(0).total_memory)
        guard=Guard(STORE,remaining,progress,gpu=True);guard()
        contexts=[extended_context(public_factors(read(GEOMETRY/f'stack-{d}-public.json'))) for d in DEPTHS]
        fit_records=[b for b in prepared['records'] if b['split']=='fit']
        validation_records=[b for b in prepared['records'] if b['split']=='validation']
        train=Dataset(load(fit_records),contexts);validation=Dataset(load(validation_records),contexts)
        controls=[gpu_pair_control(train,seed) for seed in SEEDS];write(STORE/'gpu-pair-control.json',dict(passed=True,records=controls))
        cache=sum(t.numel()*t.element_size() for d in (train,validation) for t in (d.cards,d.public,d.equity,d.economics,d.lengths_gpu,d.offsets_gpu))
        progress('data_ready',cuda_dataset_bytes=cache);fits=[]
        for seed,width in ORDER:
            guard();progress('starting_fit',seed=seed,width=width)
            folder=STORE/f'seed-{seed}-width-{width}';pilot.create(folder)
            trained=fit(seed,width,train,validation,folder,guard,progress);fits.append(trained)
            write(STORE/f'fit-{seed}-{width}.json',trained)
        for seed in SEEDS:
            pair=[next(f for f in fits if f['seed']==seed and f['width']==width) for width in (362,387)]
            assert pair[0]['first_batch_common_columns_sha256']==pair[1]['first_batch_common_columns_sha256']
            assert [c['batch_rng_sha256'] for c in pair[0]['checkpoints']]==[c['batch_rng_sha256'] for c in pair[1]['checkpoints']]
            assert pair[0]['checkpoints'][0]['validation']==pair[1]['checkpoints'][0]['validation']
        selection=dict(registration_sha256=sha(REG),preparation_sha256=sha(PREPARED),model_type=MODEL_TYPE,
            candidates=[dict(seed=f['seed'],width=f['width'],selected=f['selected']) for f in fits],
            paired_initial_outputs_exact=True,paired_batch_generators_exact=True,
            test_labels_prepared=False,heldout_labels_prepared=False)
        chosen=STORE/'frozen-selection.json';write(chosen,selection)
        del train,validation;gc.collect();torch.cuda.empty_cache();progress('selection_frozen',sha256=sha(chosen))
        test_records,test_timing=prepare([b for b in spec['boards'] if b['split']=='test'],STORE,guard,progress)
        heldout=[]
        for depth in HELDOUT:
            guard();public=public_factors(read(GEOMETRY/f'stack-{depth}-public.json'))
            terminal=native(NATIVE,['control',GEOMETRY/'fixtures'/f'stack-{depth}-context.json'])
            assert terminal['passed'];write(STORE/f'heldout-{depth}-native-terminal.json',terminal)
            lookup={public_key(r):r for r in terminal['templates'] if r['legal_actions']==2}
            assert set(lookup)=={r['hi'] for r in public['rows']}
            for row in public['rows']:
                actual=lookup[row['hi']];assert actual['actor']==row['actor'] and actual['call_ends_showdown']
                assert np.max(abs(np.asarray(price(row)['endpoints_loss_tie_win'])-actual['endpoints_loss_tie_win']))<1e-9
            heldout.append(extended_context(public))
        test=Dataset(load(test_records),contexts+heldout);tests=[]
        for c in selection['candidates']:
            guard();progress('final_test',seed=c['seed'],width=c['width'])
            model=load_models(c['selected']['weights'],c['seed'],c['width'])
            record=dict(seed=c['seed'],width=c['width'],selected_step=c['selected']['step'],score=evaluate(model,test,c['width'],guard,detail=True))
            write(STORE/f"test-{c['seed']}-{c['width']}.json",record);tests.append(record);del model;gc.collect()
        gates=[]
        for seed in SEEDS:
            pair=[next(t for t in tests if t['seed']==seed and t['width']==w) for w in (362,387)]
            groups=[[c for c in t['score']['contexts'] if c['stack'] in HELDOUT] for t in pair]
            before,after=[float(np.mean([c['mean_regret_stack_fraction'] for c in g])) for g in groups]
            absolute=all(c['mean_regret_stack_fraction']<=.001 for c in groups[1])
            gates.append(dict(seed=seed,baseline=before,candidate=after,relative_reduction=1-after/before if before else None,
                absolute_gate=absolute,passed=bool(pair[1]['selected_step']>0 and before>0 and after<=.8*before and absolute)))
        pilot.verify(spec['inputs']);guard();storage=pilot.study_measure(STORE);assert storage['logical_bytes']<LIMIT
        result=dict(passed=True,complete=True,registration_sha256=sha(REG),preparation_sha256=sha(PREPARED),
            selection=dict(file=str(chosen),sha256=sha(chosen)),fits=fits,tests=tests,diagnostic_gates=gates,
            diagnostic_gate_passed=all(g['passed'] for g in gates),board_records=prepared['records']+test_records,
            test_preparation=test_timing,cuda_dataset_bytes=cache,storage=storage,
            preparation_seconds=prepared['seconds'],gpu_stage_seconds=time.monotonic()-started,
            total_work_seconds=prepared['seconds']+time.monotonic()-started,resource_wait_seconds=guard.wait_seconds,
            peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(),peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved(),
            artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()},training_started=True,
            full_preflop_accuracy_qualified=False,production_modified=False)
        assert result['total_work_seconds']<SECONDS
        write(RESULT,result);progress('complete',gates=gates,total_work_seconds=result['total_work_seconds'])
    except BaseException as error:
        write(OUT/(NAME+'-gpu-interruption-'+uuid.uuid4().hex[:8]+'.json'),dict(error=repr(error),traceback=traceback.format_exc()))
        raise
    finally:
        assert pilot.LOCK.read_text()==str(os.getpid());pilot.LOCK.unlink()

def main(stage):
    spec=specification()
    if stage=='prepare':prepare_stage(spec)
    elif stage=='run':training_stage(spec)
    else:print(json.dumps(dict(preflight_passed=True,fitting_boards=512,new_validation=32,new_test=64,widths=[362,387],gpu_started=False)))

if __name__=='__main__':
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group();g.add_argument('--prepare',action='store_true');g.add_argument('--run',action='store_true');a=p.parse_args()
    main('prepare' if a.prepare else 'run' if a.run else 'preflight')
