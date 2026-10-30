"""Two full CUDA updates and exact checkpoint replay for integrated postflop targets."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',CUBLAS_WORKSPACE_CONFIG=':4096:8')
import copy
import json
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
from later_average_support_v1 import OUT,read,load_complete_cache
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from hu_paired_continuation_support_20260925 import guard_for,launch,setup_cuda
from later_action_training_v1 import initialize,save_state,update,first_action_view
from later_action_checkpoint_v1 import (restore_checkpoint,model_document,inner_model,
    require_config,CONFIG_KEY,POLICY_TYPE,FIT_IMPLEMENTATION)
from later_action_training_ingest_v1 import METHOD
from later_action_policy_v1 import probabilities
from action_integrated_policy_v1 import ActionIntegratedCpuBank64
from action_integrated_policy_bulk_v1 import ActionIntegratedCudaBankBulk64 as ActionIntegratedCudaBank64
from hu_action_integrated_exact_20260925 import bank_args
from sampled_visible_hybrid_checkpoint_v1 import encoded
import action_integrated_checkpoint_v1 as old_checkpoint

PREFIX='later-action-joint-control-v1'
STORE=Path('T:/GTOpen-research')/PREFIX
UPDATE=ROOT/'target/release/examples/hu_sampled_allin_bridge_v3.exe'
FULL=ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'
TRACE=ROOT/'target/release/examples/hu_sampled_action_trace_v2.exe'
BANK=ROOT/'target/release/examples/hu_sampled_bank_bridge.exe'


def worker(reg):
    import torch
    setup_cuda();guard=guard_for(reg);guard();started=time.monotonic()
    source_trial=read(reg['trials'][1]['result']);cfg=reg['config']
    assert cfg['torch_version']==torch.__version__ and cfg['numpy_version']==np.__version__
    assert cfg['device_name']==torch.cuda.get_device_name()
    store=Path(reg['store']);store.mkdir(exist_ok=False);objects=store/'objects';objects.mkdir()
    cp=OUT/'bb-context-candidate.json';args=bank_args(cp.read_text())
    matrix_source=(OUT/'preflop-allin-matrix-control-v1-matrix.json').read_text()
    cache=load_complete_cache();assert cache.sha256==cfg['allin_cache_sha256']
    step=dict(context_path=cp,catalog_source=args['catalog_source'],matrix_source=matrix_source,
        matrix_sha256=args['matrix_sha256'],cache=cache,executable=UPDATE,integration_executable=FULL,
        trace_executable=TRACE,batch_prefix=PREFIX,guard=guard)
    state=initialize(objects,cfg,**args);initial=save_state(objects,state,cfg,**args)
    rejections=[]
    def reject(name,fn):
        try:fn()
        except ValueError:rejections.append(name)
        else:raise AssertionError('Accepted '+name)
    reject('missing postflop target declaration',lambda:require_config({k:v for k,v in cfg.items() if k!='postflop_learning_targets'}))
    reject('unqualified fitter',lambda:require_config(dict(cfg,fit_implementation='old')))
    doc=model_document(objects,state['next_model'],**args)
    reject('old reader accepts new model',lambda:old_checkpoint.validate_model(doc,**args))
    reject('new reader accepts old model',lambda:inner_model(inner_model(doc,**args),**args))
    reject('old reader accepts new checkpoint',lambda:old_checkpoint.restore_checkpoint(objects,initial,config=cfg,**args))
    metrics=[];policy_error=0.;counts=[0,0];phase_counts={1:0,2:0,3:0}
    for iteration in (1,2):
        guard();folder=store/f'iteration-{iteration:04d}'
        metric=update(folder,objects,state,cfg,**step);metrics.append(metric)
        used=model_document(objects,metric['used_model'],**args)
        raw=read(folder/'batch-00/queries.json')
        response_hi=json.loads(cp.read_text())['nodes'][0]['children'][3]+1
        query=first_action_view(raw,response_hi)
        current_args={k:v for k,v in args.items() if k!='context_source'}
        cpu,_=probabilities(query,used,device='cpu',**current_args)
        gpu,_=probabilities(query,used,device='cuda',**current_args)
        original=np.array([r['probabilities'] for r in read(folder/'batch-00/policies.json')['policies']])
        policy_error=max(policy_error,float(np.max(abs(cpu-gpu))),float(np.max(abs(gpu-original))))
        assert policy_error<1e-10
        for chunk in range(cfg['subbatches_per_iteration']):
            f=folder/f'batch-{chunk:02d}';q=read(f/'queries.json');audit=read(f/'postflop-targets.json')
            assert audit['method']==METHOD
            for r in audit['postflop_replacements']:
                phase=q['observations'][r['query']]['phase'];assert phase in phase_counts
                phase_counts[phase]+=1
            counts=[a+b for a,b in zip(counts,audit['counts'])]
            if iteration==1:
                old=Path(source_trial['store'])/'iteration-0001'/f'batch-{chunk:02d}'
                before=read(old/'batch.json');now=read(f/'batch.json')
                assert before['deals']==now['deals'] and before['seed']==now['seed']
                assert read(old/'policies.json')['policies']==read(f/'policies.json')['policies']
                assert read(old/'updates.json')['records']==read(f/'updates.json')['records']
        assert state['exact_btn_state'].steps==state['root_regret_state'].steps==iteration
        assert state['root_regret_state'].counts.sum()==iteration*512
        print(json.dumps(dict(iteration=iteration,complete=True,postflop_targets=phase_counts,
            reservoir_counts=counts)),flush=True)
    restored=restore_checkpoint(objects,metrics[0]['checkpoint'],config=cfg,**args)
    replay=update(store/'replay-0002',objects,restored,cfg,**step)
    assert state['played_bank']==restored['played_bank'] and state['next_model']==restored['next_model']
    assert metrics[1]['checkpoint']==replay['checkpoint']
    assert state['action_rng'].bit_generator.state==restored['action_rng'].bit_generator.state
    assert state['exact_btn_state'].document()==restored['exact_btn_state'].document()
    assert state['root_regret_state'].document()==restored['root_regret_state'].document()
    for a,b in zip(state['reservoirs'],restored['reservoirs']):
        assert a.seen==b.seen and a.rng.bit_generator.state==b.rng.bit_generator.state
        for name in ('keys','active','arity','values','iterations'):assert np.array_equal(getattr(a,name),getattr(b,name))
    assert metrics[1]['subbatches']==replay['subbatches']
    for a,b in zip(metrics[1]['fits'],replay['fits']):
        excluded={'setup_seconds','optimizer_seconds','graph_capture_seconds'}
        assert {k:v for k,v in a.items() if k not in excluded}=={k:v for k,v in b.items() if k not in excluded}
    final=restore_checkpoint(objects,metrics[1]['checkpoint'],config=cfg,**args)
    assert final['next_model']==state['next_model'] and final['completed_iterations']==2
    batch=read(store/'iteration-0002/batch-00/batch.json')
    plain={k:v for k,v in batch.items() if k not in ('allin_counts','allin_cache_sha256','terminal_estimator')};plain['format']=2
    bp=store/'average-batch.json';qp=store/'average-queries.json';save(bp,plain)
    native=subprocess.run([str(BANK),'queries',str(cp),str(bp),'-',str(qp)],capture_output=True,text=True,
        timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
    assert native.returncode==0,native.stderr[-2000:]
    docs=[inner_model(model_document(objects,r,**args),**args) for r in state['played_bank']]
    assert [d['generation'] for d in docs]==[0,1]
    weights=np.tile(np.arange(1,3,dtype=float),(2,1))
    cpu=ActionIntegratedCpuBank64(docs,completed_iterations=2,weights_by_player=weights,**args)
    gpu=ActionIntegratedCudaBank64(docs,weights,completed_iterations=2,models_per_chunk=2,guard=guard,**args)
    pa,ra=cpu.average(read(qp),guard=guard);pb,rb=gpu.average(read(qp),guard=guard)
    bank_error=float(np.max(abs(pa-pb)));reach_error=float(np.max(abs(ra-rb)))
    assert bank_error<1e-10 and reach_error<1e-10
    del gpu
    assert all(phase_counts.values()) and counts==[r.seen for r in state['reservoirs']]
    for path,h in reg['inputs'].items():guard();assert sha(path)==h,path
    save(OUT/f'{PREFIX}-result.json',dict(passed=True,terminal=True,registration_sha256=sha(OUT/f'{PREFIX}-registration.json'),
        config=cfg,store=str(store),completed_iterations=2,initial_checkpoint=initial,final_checkpoint=metrics[1]['checkpoint'],
        steps=[dict(iteration=i+1,checkpoint=m['checkpoint'],metrics_sha256=sha(store/f'iteration-{i+1:04d}/metrics.json')) for i,m in enumerate(metrics)],
        rejections=rejections,maximum_current_policy_error=policy_error,maximum_average_policy_error=bank_error,
        maximum_average_reach_error=reach_error,postflop_targets_by_street=phase_counts,reservoir_counts=counts,
        exact_resume_models_and_reservoirs=True,exact_resume_native_artifacts=True,first_generation_matches_original_sampling=True,
        artifacts={str(p):sha(p) for p in store.rglob('*') if p.is_file()},seconds=time.monotonic()-started,
        production_modified=False,accuracy_qualified=False,control_only=True,
        scope='Two full updates plus restart replay, typed history, CPU/CUDA inference and complete played-bank averaging. No range quality claim.'))


if __name__=='__main__':
    if sys.argv[1:]==['--worker']:worker(read(OUT/f'{PREFIX}-registration.json'))
    else:
        assert sys.argv[1:]==['--run']
        extras=[str(p) for p in (UPDATE,FULL,TRACE,BANK,ROOT/'crates/solver/examples/hu_sampled_action_trace_v2.rs')]
        extras.extend(str(p) for p in (ROOT/'crates/solver/examples/research_sampled').glob('*.rs'))
        for name in ('later-action-ingest-control-v1','cuda-gradient-graph-control-v1','cuda-gradient-graph-early-control-v1'):
            p=OUT/f'{name}-result.json';assert read(p)['passed'];extras.append(str(p))
        trial=read(OUT/'action-integrated-replication-v1-result.json')
        cfg=dict(trial['config'],**{CONFIG_KEY:POLICY_TYPE},postflop_learning_targets=METHOD,
            fit_implementation=FIT_IMPLEMENTATION,max_iterations=2)
        metric_path=Path(trial['store'])/'iteration-0001/metrics.json'
        assert sha(metric_path)==trial['steps'][0]['metrics_sha256']
        metric=read(metric_path);extras.append(str(metric_path))
        for chunk in range(8):
            folder=Path(trial['store'])/'iteration-0001'/f'batch-{chunk:02d}'
            for name in ('batch','policies','updates'):
                p=folder/f'{name}.json';assert sha(p)==metric['subbatches'][chunk]['artifacts'][name]
                extras.append(str(p))
        launch(Path(__file__).resolve(),PREFIX,dict(extra_inputs=extras,store=str(STORE),config=cfg,
            scope='Two-update implementation gate with exact checkpoint restart, not a strength trial.'),
            cap=1_500_000_000,seconds=1800)
