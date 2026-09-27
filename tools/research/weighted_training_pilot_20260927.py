"""Full-generation weighted trainer, restart and policy-averaging control."""
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
import weighted_training_checkpoint_v1 as checkpoint
import sampled_visible_hybrid_checkpoint_v1 as storage
from weighted_training_v1 import initialize,update,first_action_view
from weighted_training_policy_v1 import probabilities,average
from weighted_physical_reservoir_v1 import ARRAYS
from sampled_physical_bank_v1 import histories

PREFIX = 'weighted-training-pilot-v1'


def main(publish=False):
    import torch
    torch.set_num_threads(2); torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False; torch.backends.cudnn.allow_tf32=False
    assert torch.cuda.is_available() and safe_read_only_resources()
    assert not LOCK.exists() and not OTHER.exists()
    status = subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.free','--format=csv,noheader,nounits'],
        capture_output=True,text=True,timeout=5,creationflags=subprocess.CREATE_NO_WINDOW)
    assert status.returncode == 0
    utilization,free = [float(s.strip()) for s in status.stdout.strip().splitlines()[0].split(',')]
    assert utilization < 20 and free > 4000 and psutil.cpu_percent(interval=1) < 70
    started = time.monotonic(); last = 0.
    store = Path('T:/GTOpen-research')/(PREFIX if publish else PREFIX+'-dev-'+str(time.time_ns()))
    store.mkdir(exist_ok=False); objects = store/'objects'; objects.mkdir()
    def guard():
        nonlocal last
        if time.monotonic()-started > 1200: raise RuntimeError('Pilot time limit reached')
        if time.monotonic()-last > 3:
            assert safe_read_only_resources() and psutil.disk_usage('T:/').free > 40_000_000_000
            assert torch.cuda.mem_get_info()[0] > 3_000_000_000
            last = time.monotonic()
    cp = OUT/'bb-context-candidate.json'; mp = OUT/'preflop-allin-matrix-control-v1-matrix.json'
    cat = Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    source = cp.read_text(); catalog_source = cat.read_text(); matrix_source = mp.read_text()
    matrix = AllinMatrix(json.loads(matrix_source),source); cache = load_complete_cache()
    args = dict(context_source=source,catalog_source=catalog_source,matrix_sha256=sha(mp),entry_mass=matrix.btn_mass)
    exe = ROOT/'target/release/examples/hu_sampled_allin_bridge_v3.exe'
    trace = ROOT/'target/release/examples/hu_sampled_action_trace_v2.exe'
    full = ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'
    bank = ROOT/'target/release/examples/hu_sampled_bank_bridge.exe'
    config = dict(policy_type=checkpoint.POLICY_TYPE,fit_implementation=checkpoint.FIT,device='cuda',
        architecture=[302,64,64,4],representation=storage.FEATURE_SPEC,
        current_policy_inference='float64-widened-float32-weights-v1',deals_per_generation=512,
        deals_per_subbatch=32,reservoir_capacity=8192,query_limit=500000,fit_steps=8,chunk_size=16384,
        learning_rate=.003,sampler_seed=9275001,action_seed=9275002,fit_seed_base=9275003,
        reservoir_seeds=[9275010,9275011],allin_cache_sha256=cache.sha256,
        torch_version=torch.__version__,numpy_version=np.__version__,device_name=torch.cuda.get_device_name())
    controls = [OUT/f'{n}-result.json' for n in ('weighted-root-table-control-v1','weighted-native-ingest-control-v1','weighted-learning-cuda-control-v1')]
    for p in controls: assert read(p)['passed']
    paths = [cp,mp,cat,exe,trace,full,bank,*controls,*Path(__file__).parent.glob('*.py'),OUT/'WEIGHTED-TRAINING-PILOT-PLAN.md']
    inputs = {str(p):sha(p) for p in paths}; reg = OUT/f'{PREFIX}-registration.json'
    if publish:
        save(reg,dict(inputs=inputs,config=config,store=str(store),completed_generations=2,replay_generation=2,
            inference_tolerance=1e-10,maximum_seconds=1200,maximum_bytes=2_000_000_000,
            utilization_before=utilization,free_vram_MiB_before=free,control_only=True,production_modified=False))
    acquired = False
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True; guard()
        state=initialize(objects,config,**args); initial=checkpoint.save_checkpoint(objects,state,config,**args)
        checkpoint.restore_checkpoint(objects,initial,config,**args)
        step=dict(context_path=cp,catalog_source=catalog_source,matrix_source=matrix_source,matrix_sha256=sha(mp),
            cache=cache,executable=exe,integration_executable=full,trace_executable=trace,batch_prefix=PREFIX,guard=guard)
        metrics=[]; max_policy_error=0.; rejections=[]
        def reject(label,call):
            try:call()
            except (ValueError,KeyError,TypeError):rejections.append(label)
            else:raise AssertionError('Invalid input accepted: '+label)
        reject('changed configuration',lambda:checkpoint.restore_checkpoint(objects,initial,dict(config,fit_steps=9),**args))
        reject('old reader rejects weighted model',lambda:storage.validate_model(checkpoint.model_document(objects,state['next_model'],**args),source))
        iterations=(1,2) if publish else (1,)
        for iteration in iterations:
            metric=update(store/f'iteration-{iteration:04d}',objects,state,config,**step); metrics.append(metric)
            assert metric['root_samples']==iteration*512 and metric['root_covered_classes']==169 and metric['exact_btn_updates']==iteration
            restored=checkpoint.restore_checkpoint(objects,metric['checkpoint'],config,**args)
            assert restored['next_model']==state['next_model'] and restored['sampler'].checkpoint()==state['sampler'].checkpoint()
            doc=checkpoint.model_document(objects,state['next_model'],**args)
            raw=read(store/f'iteration-{iteration:04d}/batch-00/queries.json')
            query=first_action_view(raw,json.loads(source)['nodes'][0]['children'][3]+1)
            policy_args={k:v for k,v in args.items() if k!='context_source'}
            cpu,_=probabilities(query,doc,device='cpu',**policy_args)
            gpu,_=probabilities(query,doc,device='cuda',**policy_args)
            max_policy_error=max(max_policy_error,float(np.max(abs(cpu-gpu))))
            assert max_policy_error<1e-10
            print(json.dumps(dict(iteration=iteration,seconds=metric['seconds'],timings=metric['timings'],
                visits=[r.seen for r in state['reservoirs']],covered_classes=169)),flush=True)
        if publish:
            resumed=checkpoint.restore_checkpoint(objects,metrics[0]['checkpoint'],config,**args)
            replay=update(store/'replay-0002',objects,resumed,config,**step)
            assert state['next_model']==resumed['next_model'] and state['played_bank']==resumed['played_bank']
            assert metrics[1]['checkpoint']==replay['checkpoint']
            assert state['sampler'].checkpoint()==resumed['sampler'].checkpoint()
            assert state['action_rng'].bit_generator.state==resumed['action_rng'].bit_generator.state
            for a,b in zip(state['reservoirs'],resumed['reservoirs']):
                assert a.seen==b.seen and a.rng.bit_generator.state==b.rng.bit_generator.state
                assert all(np.array_equal(getattr(a,k),getattr(b,k)) for k in ARRAYS)
            assert metrics[1]['subbatches']==replay['subbatches']
            # A native bank query includes actual own-action ancestry.
            batch=read(store/'iteration-0002/batch-00/batch.json')
            plain={k:v for k,v in batch.items() if k not in ('allin_counts','allin_cache_sha256','terminal_estimator')}
            plain['format']=2; bp=store/'average-batch.json'; qp=store/'average-queries.json';save(bp,plain)
            native=subprocess.run([str(bank),'queries',str(cp),str(bp),'-',str(qp)],capture_output=True,text=True,
                timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
            assert native.returncode==0,native.stderr[-2000:]
            q=read(qp); docs=[checkpoint.model_document(objects,r,**args) for r in state['played_bank']]
            assert [d['generation'] for d in docs]==[0,1]
            weights=np.tile([1.,2.],(2,1))
            av,reach=average(q,docs,completed_iterations=2,weights_by_player=weights,guard=guard,device='cpu',**policy_args)
            gav,greach=average(q,docs,completed_iterations=2,weights_by_player=weights,guard=guard,device='cuda',**policy_args)
            history=histories(q['observations']); assert any(history)
            # Independent scalar average after final table/root overrides.
            policies=[probabilities(q,d,device='cpu',**policy_args)[0] for d in docs]
            oracle=[]; oracle_reach=[]
            for i,o in enumerate(q['observations']):
                w=[]
                for g,p in enumerate(policies):
                    value=weights[o['actor'],g]
                    for ancestor,action in history[i]:value*=p[ancestor,action]
                    w.append(value)
                total=sum(w);oracle_reach.append(total)
                oracle.append(sum(w[g]*policies[g][i] for g in range(2))/total if total>0 else
                    np.array([1./o['n'] if a<o['n'] else 0. for a in range(4)]))
            average_error=max(float(np.max(abs(av-gav))),float(np.max(abs(av-oracle))))
            reach_error=max(float(np.max(abs(reach-greach))),float(np.max(abs(reach-oracle_reach))))
            assert average_error<1e-10 and reach_error<1e-10
            reject('unplayed model in average',lambda:average(q,docs+[doc],completed_iterations=2,weights_by_player=weights,guard=guard,device='cpu',**policy_args))
        else: average_error=reach_error=None
        for p,h in inputs.items():assert sha(p)==h,p
        artifacts={str(p):sha(p) for p in store.rglob('*') if p.is_file()}
        size=sum(Path(p).stat().st_size for p in artifacts); assert size<2_000_000_000
        result=dict(passed=True,completed_generations=len(iterations),config=config,store=str(store),initial_checkpoint=initial,
            final_checkpoint=metrics[-1]['checkpoint'],steps=[dict(iteration=i+1,checkpoint=m['checkpoint'],
                metrics_sha256=sha(store/f'iteration-{i+1:04d}/metrics.json')) for i,m in enumerate(metrics)],
            exact_restart_replay=publish,maximum_current_policy_error=max_policy_error,
            maximum_average_policy_error=average_error,maximum_average_reach_error=reach_error,rejections=rejections,
            artifacts=artifacts,bytes_written=size,seconds=time.monotonic()-started,
            control_only=True,accuracy_qualified=False,production_modified=False)
        if publish:
            result['registration_sha256']=sha(reg);save(OUT/f'{PREFIX}-result.json',result)
        print(json.dumps({k:v for k,v in result.items() if k not in ('artifacts','config','steps')}),flush=True)
    finally:
        if acquired:
            assert LOCK.read_text()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--publish',action='store_true')
    main(parser.parse_args().publish)
