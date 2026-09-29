"""Frozen two-by-two board-coverage comparison, with one scientific attempt."""
import time
INVOKED = time.monotonic()
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
    CUBLAS_WORKSPACE_CONFIG=':4096:8', PYTHONDONTWRITEBYTECODE='1')
import argparse, gc, json, sys, time, traceback, uuid
from pathlib import Path
import numpy as np
import torch
import river_matched_training_pilot_v1 as pilot
from global_research_inventory_v3 import measure as inventory
from stack_price_reference_v1 import price
from stack_price_reference_control_v1 import native, public_key, NATIVE, RANKS
from stack_price_learning_data_v2 import public_factors
from stack_price_learning_fit_v1 import Dataset
from stack_board_relative_model_v1 import fit, load_models, MODEL_TYPE, CHECKPOINTS
from stack_board_relative_run_v1 import gpu_pair_control
from stack_board_balanced_sampler_v1 import select_boards, feasible_cells, board_cell, allocation
from stack_board_balanced_data_v1 import prepare, load, extended_context, cpu_admission, Guard
from stack_board_balanced_metrics_v1 import evaluate, TOLERANCE_POLICY as TOLERANCES

ROOT, OUT = pilot.ROOT, pilot.OUT
NAME = 'stack-board-balanced-learning-v1'
STORE = Path('S:/GTOpen-research')/NAME
REG, PREPARED, RESULT, STATUS = (OUT/(NAME+suffix+'.json') for suffix in ('-registration','-prepared','-result','-status'))
GEOMETRY = Path('S:/GTOpen-research/stack-geometry-control-v1')
DEPTHS, HELDOUT = (20,40,100,200,400), (60,150)
SEEDS = (9297101,9297102)
ORDER = ((SEEDS[0],'random',362),(SEEDS[0],'random',387),
    (SEEDS[0],'structured',387),(SEEDS[0],'structured',362),
    (SEEDS[1],'structured',362),(SEEDS[1],'structured',387),
    (SEEDS[1],'random',387),(SEEDS[1],'random',362))
LIMIT, RESERVE, SECONDS = 512_000_000, 128_000_000, 3600
read, sha, write = pilot.read, pilot.sha, pilot.atomic_json

def progress(state, **values):
    pilot.STATUS = STATUS
    pilot.status(state, **values)
    print(json.dumps(dict(state=state, **values)), flush=True)

def specification():
    previous = OUT/'stack-board-relative-learning-v1-registration.json'
    old = read(previous)
    review = OUT/'stack-board-relative-learning-v1-readback-v1.json'
    old_result = OUT/'stack-board-relative-learning-v1-result.json'
    old_prepared = OUT/'stack-board-relative-learning-v1-prepared.json'
    assert read(review)['passed'] and read(old_result)['complete']
    for p in (previous,old_result,old_prepared):
        assert read(review)['inputs'][str(p)] == sha(p)
    training = [b for b in read(old_prepared)['records'] if b['split']=='fit']
    assert len(training)==512 and [b['index'] for b in training]==list(range(512))
    excluded = {tuple(g) for g in old['excluded_probe_groups']}
    excluded.update(tuple(b['canonical_group']) for b in old['boards'])
    assert len(excluded)==788
    paths = [Path(__file__), previous, review, old_result, old_prepared, NATIVE, RANKS,
        OUT/'STACK-BOARD-BALANCED-COVERAGE-PROPOSAL.md', OUT/'STACK-BOARD-BALANCED-IMPLEMENTATION.md',
        ROOT/'tools/research/stack_board_balanced_readback_v1.py',
        ROOT/'tools/research/stack_board_relative_readback_v1.py']
    for name in ('stack-board-balanced-sampler-control-v1','stack-board-balanced-metrics-control-v1','stack-board-balanced-data-control-v1'):
        rp, proof_path = OUT/(name+'-registration.json'), OUT/(name+'-result.json')
        proof = read(proof_path)
        assert proof['passed'] and proof['registration_sha256']==sha(rp)
        pilot.verify(read(rp)['inputs'])
        paths.extend((rp,proof_path))
        excluded.update(tuple(g) for g in proof['retained_board_groups'])
    for record in training:
        assert sha(record['file'])==record['sha256'] and sha(record['extra_file'])==record['extra_sha256']
        paths.extend((Path(record['file']),Path(record['extra_file'])))
    boards = select_boards(9297100, excluded)
    sampler_proof=read(OUT/'stack-board-balanced-sampler-control-v1-result.json')
    board_manifest=sampler_proof['board_manifest']
    assert sha(board_manifest['file'])==board_manifest['sha256']
    assert boards==read(board_manifest['file'])
    paths.append(Path(board_manifest['file']))
    assert len(boards)==1344
    counts={split:sum(b['split']==split for b in boards) for split in ('fit_random','fit_structured','validation','test','stress')}
    assert counts==dict(fit_random=512,fit_structured=512,validation=128,test=128,stress=64)
    for d in (*DEPTHS,*HELDOUT):
        paths.extend((GEOMETRY/f'stack-{d}-public.json',GEOMETRY/'fixtures'/f'stack-{d}-context.json'))
    for module in list(sys.modules.values()):
        p=getattr(module,'__file__',None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix=='.py':
            paths.append(Path(p))
    return dict(format=1,inputs={str(p):sha(p) for p in paths},model_type=MODEL_TYPE,
        authorization='User 2026-09-29: Proceed with the study - I will check in later; approves saved balanced-coverage proposal.',
        board_seed=9297100,seeds=list(SEEDS),order=list(ORDER),boards=boards,
        excluded_probe_groups=sorted(excluded),reused_training_boards=training,
        structured_cells=feasible_cells(),structured_fit_allocation=allocation(512),stress_allocation=allocation(64),
        fitting_boards_per_arm=1024,shared_existing_fitting_boards=512,validation_boards=128,test_boards=128,stress_boards=64,
        fitting_depths=list(DEPTHS),heldout_depths=list(HELDOUT),widths=[362,387],arms=['random','structured'],
        primary_comparison='structured versus random training boards, 387 inputs, each seed separately',
        hidden_layers=[64,64],extra_parameters_total=3200,initial_extension_weights_zero=True,
        steps=8192,batch_size=4096,validation_steps=list(CHECKPOINTS),
        optimizer=dict(type='Adam',learning_rate=.001,betas=[.9,.999],eps=1e-8,weight_decay=0,foreach=False),
        selection='Minimum context-balanced normalized regret on128 shared random validation boards; tie earliest step',
        relative_improvement_required=.2,heldout_mean_regret_stack_fraction_maximum=.001,
        near_indifference_stack_fraction=.0001,maximum_seconds=SECONDS,maximum_preparation_seconds=600,
        readback_maximum_seconds=1800,readback_tolerances=TOLERANCES,
        maximum_new_bytes=LIMIT,reserve_bytes=RESERVE,global_allocated_cap=pilot.GLOBAL_LIMIT,
        preparation_workers=8,readback_workers=4,initial_gpu_batch_controls=3,initial_gpu_batch_rows=1024,
        gpu_sharing='Light desktop permitted; production/heavy work first; research CUDA4GB, external headroom2GB',
        training_distribution='Structured curriculum deliberately differs from physical board frequencies; not an unbiased deal sampler',
        scope='Restricted terminal river Fold/Call comparison against a uniform legal opponent; no full-game or preflop qualification',
        depth_limitation='60/150 excluded from fitting/selection; their geometry appeared earlier',production_modified=False)

def admit_inventory():
    started=time.monotonic()
    rows=inventory()
    allocated=sum(r['allocated_file_bytes'] for r in rows)
    assert allocated+LIMIT+RESERVE<=pilot.GLOBAL_LIMIT
    return dict(inventory=rows,allocated_bytes=allocated,seconds=time.monotonic()-started)

def prepare_stage(spec):
    assert not any(p.exists() for p in (REG,PREPARED,RESULT,STORE)), 'Preserve existing attempts'
    probe=cpu_admission()
    if not probe['admitted']:
        progress('deferred_before_preparation',probe=probe)
        return
    started=INVOKED
    with pilot.LOCK.open('x') as stream:stream.write(str(os.getpid()))
    try:
        progress('preparation_inventory')
        accounting=admit_inventory()
        write(REG,spec)
        pilot.create(STORE)
        write(STORE/'cpu-admission.json',dict(accounting=accounting,probe=probe))
        guard=Guard(STORE,600-(time.monotonic()-started),progress)
        tasks=[b for b in spec['boards'] if b['split'] in ('fit_random','fit_structured','validation')]
        generated,timing=prepare(tasks,STORE,guard,progress)
        records=spec['reused_training_boards']+generated
        assert len(generated)==1152 and len(records)==1664
        for lo in range(0,len(records),16):
            guard()
            chunk=load(records[lo:lo+16])
            del chunk
        for depth in DEPTHS:extended_context(public_factors(read(GEOMETRY/f'stack-{depth}-public.json')))
        pilot.verify(spec['inputs'])
        guard()
        assert not torch.cuda.is_initialized()
        size=pilot.study_measure(STORE)
        assert size['logical_bytes']<LIMIT
        artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()}
        result=dict(passed=True,complete=True,registration_sha256=sha(REG),records=records,preparation=timing,
            seconds=time.monotonic()-started,inventory_seconds=accounting['seconds'],storage=size,
            original_feature_prefixes_exact=True,original_counts_retained=True,public_padding_and_actors_checked=True,
            gpu_used=False,training_started=False,test_labels_prepared=False,stress_labels_prepared=False,
            artifacts=artifacts)
        assert result['seconds']<600
        write(PREPARED,result)
        progress('prepared_for_gpu',seconds=result['seconds'],boards=len(records),gpu_used=False)
    except BaseException as error:
        write(OUT/(NAME+'-prepare-interruption-'+uuid.uuid4().hex[:8]+'.json'),dict(error=repr(error),traceback=traceback.format_exc()))
        raise
    finally:
        assert pilot.LOCK.read_text()==str(os.getpid())
        pilot.LOCK.unlink()

def training_stage(spec):
    assert read(REG)==json.loads(json.dumps(spec)), 'Frozen specification changed'
    prepared=read(PREPARED)
    assert prepared['passed'] and prepared['complete'] and prepared['registration_sha256']==sha(REG)
    assert not prepared['training_started'] and not prepared['test_labels_prepared'] and not prepared['stress_labels_prepared']
    pilot.verify(prepared['artifacts'])
    pilot.verify(spec['inputs'])
    expected={(b['split'],b['index']):(b['board'],list(b['canonical_group'])) for b in spec['reused_training_boards']+spec['boards'] if b['split'] not in ('test','stress')}
    assert len(prepared['records'])==len(expected)
    for b in prepared['records']:assert (b['board'],b['canonical_group'])==expected[(b['split'],b['index'])]
    attempt=STORE/'gpu-attempt.json'
    assert not RESULT.exists() and not attempt.exists(), 'Do not restart a scientific attempt'
    ready,probe=pilot.available()
    if not ready:
        print(json.dumps(dict(state='prepared_waiting_for_gpu',gpu=probe,training_started=False)),flush=True)
        return
    started=INVOKED
    with pilot.LOCK.open('x') as stream:stream.write(str(os.getpid()))
    try:
        progress('gpu_inventory')
        accounting=admit_inventory()
        write(attempt,dict(registration_sha256=sha(REG),preparation_sha256=sha(PREPARED),probe=probe,accounting=accounting))
        remaining=SECONDS-prepared['seconds']-(time.monotonic()-started)
        assert remaining>0
        torch.set_num_threads(1)
        torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False
        torch.backends.cudnn.allow_tf32=False
        torch.cuda.set_per_process_memory_fraction(pilot.CUDA_BUDGET_BYTES/torch.cuda.get_device_properties(0).total_memory)
        guard=Guard(STORE,remaining,progress,gpu=True)
        guard()
        contexts=[extended_context(public_factors(read(GEOMETRY/f'stack-{d}-public.json'))) for d in DEPTHS]
        validation=Dataset(load([b for b in prepared['records'] if b['split']=='validation']),contexts)
        train=None
        current_arm=None
        fits=[]
        controls=[]
        cache_sizes=[]
        checked_pairs=set()
        for seed,arm,width in ORDER:
            guard()
            if current_arm!=arm:
                del train
                gc.collect()
                torch.cuda.empty_cache()
                records=[b for b in prepared['records'] if b['split'] in ('fit','fit_'+arm)]
                assert len(records)==1024
                train=Dataset(load(records),contexts)
                cache=sum(t.numel()*t.element_size() for data in (train,validation) for t in
                    (data.cards,data.public,data.equity,data.economics,data.lengths_gpu,data.offsets_gpu))
                assert cache<3_000_000_000
                cache_sizes.append(dict(arm=arm,bytes=cache))
                current_arm=arm
            if (seed,arm) not in checked_pairs:
                controls.append(dict(arm=arm,**gpu_pair_control(train,seed)))
                checked_pairs.add((seed,arm))
            progress('starting_fit',seed=seed,arm=arm,width=width)
            folder=STORE/f'seed-{seed}-{arm}-width-{width}'
            pilot.create(folder)
            def fit_progress(state,**values):progress(state,arm=arm,**values)
            trained=dict(arm=arm,**fit(seed,width,train,validation,folder,guard,fit_progress))
            fits.append(trained)
            write(STORE/f'fit-{seed}-{arm}-{width}.json',trained)
        write(STORE/'gpu-pair-control.json',dict(passed=True,records=controls))
        for seed in SEEDS:
            for arm in ('random','structured'):
                pair=[next(f for f in fits if (f['seed'],f['arm'],f['width'])==(seed,arm,w)) for w in (362,387)]
                assert pair[0]['first_batch_common_columns_sha256']==pair[1]['first_batch_common_columns_sha256']
                assert [c['batch_rng_sha256'] for c in pair[0]['checkpoints']]==[c['batch_rng_sha256'] for c in pair[1]['checkpoints']]
                assert pair[0]['checkpoints'][0]['validation']==pair[1]['checkpoints'][0]['validation']
            initial=[f['checkpoints'][0]['validation'] for f in fits if f['seed']==seed]
            assert all(v==initial[0] for v in initial)
        selection=dict(registration_sha256=sha(REG),preparation_sha256=sha(PREPARED),model_type=MODEL_TYPE,
            candidates=[dict(seed=f['seed'],arm=f['arm'],width=f['width'],selected=f['selected']) for f in fits],
            paired_initial_outputs_exact=True,paired_batch_generators_exact=True,
            test_labels_prepared=False,stress_labels_prepared=False,heldout_labels_prepared=False)
        chosen=STORE/'frozen-selection.json'
        write(chosen,selection)
        del train,validation
        gc.collect()
        torch.cuda.empty_cache()
        progress('selection_frozen',sha256=sha(chosen))
        test_records,test_timing=prepare([b for b in spec['boards'] if b['split'] in ('test','stress')],STORE,guard,progress)
        heldout=[]
        for depth in HELDOUT:
            guard()
            public=public_factors(read(GEOMETRY/f'stack-{depth}-public.json'))
            terminal=native(NATIVE,['control',GEOMETRY/'fixtures'/f'stack-{depth}-context.json'])
            assert terminal['passed']
            write(STORE/f'heldout-{depth}-native-terminal.json',terminal)
            lookup={public_key(r):r for r in terminal['templates'] if r['legal_actions']==2}
            assert set(lookup)=={r['hi'] for r in public['rows']}
            for row in public['rows']:
                actual=lookup[row['hi']]
                assert actual['actor']==row['actor'] and actual['call_ends_showdown']
                assert np.max(abs(np.asarray(price(row)['endpoints_loss_tie_win'])-actual['endpoints_loss_tie_win']))<1e-9
            heldout.append(extended_context(public))
        tests=[]
        for split in ('test','stress'):
            records=[b for b in test_records if b['split']==split]
            test=Dataset(load(records),contexts+heldout)
            for candidate in selection['candidates']:
                guard()
                seed,arm,width=(candidate[k] for k in ('seed','arm','width'))
                progress('final_test',split=split,seed=seed,arm=arm,width=width)
                model=load_models(candidate['selected']['weights'],seed,width)
                record=dict(split=split,seed=seed,arm=arm,width=width,selected_step=candidate['selected']['step'],
                    board_keys=[dict(index=b['index'],canonical_group=b['canonical_group']) for b in records],
                    score=evaluate(model,test,width,guard,detail=True))
                write(STORE/f'{split}-{seed}-{arm}-{width}.json',record)
                tests.append(record)
                del model
                gc.collect()
            del test
            gc.collect()
            torch.cuda.empty_cache()
        gates=[]
        for seed in SEEDS:
            pair=[next(t for t in tests if (t['split'],t['seed'],t['arm'],t['width'])==('test',seed,arm,387)) for arm in ('random','structured')]
            groups=[[c for c in t['score']['contexts'] if c['stack'] in HELDOUT] for t in pair]
            before,after=[float(np.mean([c['mean_regret_stack_fraction'] for c in group])) for group in groups]
            absolute=all(c['mean_regret_stack_fraction']<=.001 for c in groups[1])
            gates.append(dict(seed=seed,baseline=before,candidate=after,relative_reduction=1-after/before if before else None,
                absolute_gate=absolute,passed=bool(before>0 and after<=.8*before and absolute)))
        pilot.verify(spec['inputs'])
        guard()
        storage=pilot.study_measure(STORE)
        assert storage['logical_bytes']<LIMIT
        artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()}
        guard()
        result=dict(passed=True,complete=True,registration_sha256=sha(REG),preparation_sha256=sha(PREPARED),
            selection=dict(file=str(chosen),sha256=sha(chosen)),fits=fits,tests=tests,diagnostic_gates=gates,
            diagnostic_gate_passed=all(g['passed'] for g in gates),board_records=prepared['records']+test_records,
            test_preparation=test_timing,cuda_cache_sizes=cache_sizes,storage=storage,
            preparation_seconds=prepared['seconds'],gpu_stage_seconds=time.monotonic()-started,
            total_work_seconds=prepared['seconds']+time.monotonic()-started,resource_wait_seconds=guard.wait_seconds,
            peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(),peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved(),
            artifacts=artifacts,training_started=True,
            full_preflop_accuracy_qualified=False,production_modified=False)
        assert result['total_work_seconds']<SECONDS
        write(RESULT,result)
        progress('complete',gates=gates,total_work_seconds=result['total_work_seconds'])
    except BaseException as error:
        write(OUT/(NAME+'-gpu-interruption-'+uuid.uuid4().hex[:8]+'.json'),dict(error=repr(error),traceback=traceback.format_exc()))
        raise
    finally:
        assert pilot.LOCK.read_text()==str(os.getpid())
        pilot.LOCK.unlink()

def main(stage):
    spec=specification()
    if stage=='prepare':prepare_stage(spec)
    elif stage=='run':training_stage(spec)
    else:print(json.dumps(dict(preflight_passed=True,boards=len(spec['boards']),fits=8,gpu_started=False)))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    group=parser.add_mutually_exclusive_group()
    group.add_argument('--prepare',action='store_true')
    group.add_argument('--run',action='store_true')
    args=parser.parse_args()
    main('prepare' if args.prepare else 'run' if args.run else 'check')
