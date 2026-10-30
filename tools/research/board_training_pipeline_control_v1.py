"""Bounded complete GPU update, interruption and restart qualification."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',CUBLAS_WORKSPACE_CONFIG=':4096:8')
import argparse
import copy
import json
from pathlib import Path
import subprocess
import time
import numpy as np
import psutil
from later_average_support_v1 import OUT,read,load_complete_cache
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from weighted_learning_cuda_control_20260927 import safe_read_only_resources,LOCK,OTHER
from preflop_allin_matrix_v1 import AllinMatrix
from board_root_accumulator_v1 import BoardRootRegrets
import board_training_checkpoint_v1 as checkpoint
import sampled_visible_hybrid_checkpoint_v1 as storage
from board_training_pipeline_v1 import initialize,update
from board_training_policy_v1 import probabilities
from weighted_physical_reservoir_v1 import ARRAYS

PREFIX='board-training-pipeline-control-v1'
STORE=Path('S:/GTOpen-research')/PREFIX


def dependencies():
    paths=[]
    for prefix in ('board-root-accumulator-control-v1','board-training-checkpoint-control-v2',
                   'board-training-targets-control-v1','board-training-workers-control-v2',
                   'weighted-parallel-graph-control-v2'):
        rp=OUT/f'{prefix}-registration.json';result=OUT/f'{prefix}-result.json'
        r=read(result);assert r['passed'] and r['registration_sha256']==sha(rp)
        for p,h in read(rp)['inputs'].items():assert sha(p)==h,p
        paths.extend((rp,result))
    return paths


def compare_states(a,b):
    assert a['completed_iterations']==b['completed_iterations']
    assert a['played_bank']==b['played_bank'] and a['next_model']==b['next_model']
    assert a['sampler'].checkpoint()==b['sampler'].checkpoint()
    assert a['action_rng'].bit_generator.state==b['action_rng'].bit_generator.state
    assert a['root_regret_state'].document()==b['root_regret_state'].document()
    assert a['exact_btn_state'].document()==b['exact_btn_state'].document()
    for x,y in zip(a['reservoirs'],b['reservoirs']):
        assert x.summary()==y.summary() and x.rng.bit_generator.state==y.rng.bit_generator.state
        assert all(np.array_equal(getattr(x,k),getattr(y,k)) for k in ARRAYS)


def main(check_ready=False):
    paths=dependencies()
    cp=OUT/'bb-context-candidate.json';mp=OUT/'preflop-allin-matrix-control-v1-matrix.json'
    cat=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    physical=Path('S:/GTOpen-research/board-root-components-control-v1/preflop-catalog.json')
    source=cp.read_text();matrix_source=mp.read_text();matrix=AllinMatrix(json.loads(matrix_source),source)
    root=BoardRootRegrets(context_sha256=storage.digest(source),matrix_sha256=sha(mp),
        entry_mass=matrix.bb_mass,physical_budget=512,boards_per_generation=4,board_seed=9280301)
    reference=OUT/'weighted-training-pilot-v1-result.json'
    config=copy.deepcopy(read(reference)['config']);config.update(policy_type=checkpoint.POLICY_TYPE,
        board_root=root.config,sampler_seed=9280302,action_seed=9280303,fit_seed_base=9280304,
        reservoir_seeds=[9280310,9280311])
    checkpoint.require_config(config)
    assert config['fit_steps']==8 and config['reservoir_capacity']==8192
    args=dict(context_source=source,catalog_source=cat.read_text(),matrix_sha256=sha(mp),
              entry_mass=matrix.btn_mass,root_config=root.config)
    exe=ROOT/'target/release/examples/hu_sampled_allin_bridge_v3.exe'
    trace=ROOT/'target/release/examples/hu_sampled_action_trace_v2.exe'
    integrated=ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'
    board_exe=ROOT/'target/release/examples/hu_fixed_board_tree_v1.exe'
    paths.extend([cp,mp,cat,physical,reference,exe,trace,integrated,board_exe,
                  OUT/'BOARD-TRAINING-PIPELINE-CONTROL-PLAN.md',*Path(__file__).parent.glob('*.py')])
    inputs={str(p):sha(p) for p in paths}
    if check_ready:
        print(json.dumps(dict(ready=True,dependencies=len(inputs),config=config,
            scope='Read-only preflight; no GPU work, training or registration.')));return
    assert not STORE.exists() and not LOCK.exists() and not OTHER.exists()
    assert safe_read_only_resources() and psutil.cpu_percent(interval=1)<50 and psutil.disk_usage('S:/').free>50*2**30
    status=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.free','--format=csv,noheader,nounits'],
        capture_output=True,text=True,timeout=5,creationflags=subprocess.CREATE_NO_WINDOW)
    assert status.returncode==0
    utilization,free=map(float,status.stdout.strip().splitlines()[0].split(','));assert utilization<20 and free>6000
    import torch
    assert torch.cuda.is_available()
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    STORE.mkdir();objects=STORE/'objects';objects.mkdir()
    rp=OUT/f'{PREFIX}-registration.json'
    save(rp,dict(inputs=inputs,store=str(STORE),config=config,maximum_seconds=1800,maximum_bytes=6_000_000_000,
        workers=2,board_workers=4,two_trained_generations=True,failed_prefixes=2,
        scope='Eight optimizer steps per fit: mechanical qualification, not range quality.',production_modified=False))
    acquired=False;started=time.monotonic();last=size_at=0.;metrics=[];failures=[]
    def guard():
        nonlocal last,size_at
        now=time.monotonic();assert now-started<1800
        if now-last>3:
            assert safe_read_only_resources() and psutil.virtual_memory().available>24_000_000_000
            assert psutil.disk_usage('S:/').free>40_000_000_000 and torch.cuda.mem_get_info()[0]>3_000_000_000
            last=now
        if now-size_at>30:
            assert sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())<6_000_000_000
            size_at=now
    class InjectedStop(RuntimeError):pass
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;cache=load_complete_cache();guard()
        step=dict(context_path=cp,catalog_source=cat.read_text(),matrix_source=matrix_source,matrix_sha256=sha(mp),
            cache=cache,executable=exe,integration_executable=integrated,trace_executable=trace,
            physical_catalog_source=physical.read_text(),board_executable=board_exe,
            batch_prefix=PREFIX,guard=guard,workers=2,board_workers=4)
        state=initialize(objects,config,**args);initial=checkpoint.save_checkpoint(objects,state,config,**args)
        first=update(STORE/'generation-0001',objects,state,config,**step);metrics.append(first)
        saved=copy.deepcopy(state)
        # The first stop happens before fitting; the second after both fits and root update.
        for index,stage in enumerate(('physical-targets-complete','root-update-complete')):
            def stop(value):
                if value==stage:raise InjectedStop(stage)
            folder=STORE/f'interrupted-{index+1}'
            try:update(folder,objects,state,config,on_stage=stop,**step)
            except InjectedStop:pass
            else:raise AssertionError('Expected deliberate interrupted update')
            compare_states(state,saved)
            restored=checkpoint.restore_checkpoint(objects,first['checkpoint'],config,**args)
            compare_states(restored,saved)
            assert not (folder/'metrics.json').exists()
            failures.append(stage);print(json.dumps(dict(interruption_recovery_passed=stage)),flush=True)
        second=update(STORE/'generation-0002',objects,state,config,**step);metrics.append(second)
        resumed=checkpoint.restore_checkpoint(objects,first['checkpoint'],config,**args)
        replay=update(STORE/'generation-0002-replay',objects,resumed,config,**dict(step,workers=4))
        compare_states(state,resumed)
        assert second['checkpoint']==replay['checkpoint'] and second['subbatches']==replay['subbatches']
        assert second['next_model']==replay['next_model'] and state['played_bank'][-1]==first['next_model']
        query_path=STORE/'generation-0002/batch-00/queries.json';queries=read(query_path)
        model=checkpoint.model_document(objects,second['next_model'],**args)
        policy_args={k:v for k,v in args.items() if k!='context_source'}
        cpu,_=probabilities(queries,model,device='cpu',**policy_args)
        gpu,_=probabilities(queries,model,device='cuda',**policy_args)
        error=float(np.max(abs(cpu-gpu)));assert error<1e-10
        for p,h in inputs.items():assert sha(p)==h,p
        guard()
        result=dict(passed=True,registration_sha256=sha(rp),config=config,
            initial_checkpoint=initial,final_checkpoint=second['checkpoint'],exact_restart_replay=True,
            interruption_stages=failures,maximum_cpu_gpu_policy_error=error,
            trained_generations=2,played_generations=[0,1],unplayed_excluded=second['next_model'],
            metrics=[dict(path=str(STORE/f'generation-{i+1:04d}/metrics.json'),sha256=sha(STORE/f'generation-{i+1:04d}/metrics.json'),
                          seconds=m['seconds'],timings=m['timings']) for i,m in enumerate(metrics)],
            replay_metrics_sha256=sha(STORE/'generation-0002-replay/metrics.json'),
            seconds=time.monotonic()-started,gpu_used=True,accuracy_qualified=False,
            independent_readback_required=True,training_experiment_admitted=False,production_modified=False)
        save(OUT/f'{PREFIX}-result.json',result);print(json.dumps(result),flush=True)
    except BaseException as error:
        save(OUT/f'{PREFIX}-failure.json',dict(passed=False,error=repr(error),registration_sha256=sha(rp),
            completed_updates=len(metrics),verified_interruptions=failures,seconds=time.monotonic()-started,production_modified=False))
        raise
    finally:
        if acquired:
            assert LOCK.read_text()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check-ready',action='store_true')
    main(parser.parse_args().check_ready)
