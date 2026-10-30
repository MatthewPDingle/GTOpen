"""Full-geometry two-update CUDA control of action-integrated root learning."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUBLAS_WORKSPACE_CONFIG=':4096:8')
import json
import math
import shutil
import time
import sys
from pathlib import Path
import numpy as np
import psutil
from later_average_support_v1 import OUT, read, load_complete_cache
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from preflop_allin_matrix_v1 import AllinMatrix
from action_integrated_training_v1 import initialize, save_state, update, first_action_view
from action_integrated_checkpoint_v1 import restore_checkpoint, model_document, POLICY_TYPE, CONFIG_KEY
from exact_initial_hybrid_checkpoint_v1 import POLICY_TYPE as EXACT_POLICY, CONFIG_KEY as EXACT_KEY
from sampled_visible_hybrid_checkpoint_v1 import FEATURE_SPEC, encoded
from reboot_research_idle_v1 import idle
from ntfs_research_storage_v1 import create_compressed_directory,measure_tree
from hu_root_retained_storage_admitted_study_20260924 import measure,LIMIT,METADATA_RESERVE
from action_integrated_policy_v1 import probabilities,ActionIntegratedCpuBank64,ActionIntegratedCudaBank64

PREFIX = 'action-integrated-joint-gpu-control-v1'
STORE = Path('T:/GTOpen-research')/PREFIX
LOCK = ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER = ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def main():
    start = time.monotonic()
    last_probe=0.;last_storage=0.;cuda_ready=False
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    def storage_check():
        value=measure_tree(STORE,lambda:None)
        assert value['allocated_file_bytes']<=3_000_000_000 and value['logical_bytes']<=10_000_000_000
        assert value['compressed_files']==value['files']
        return value
    def guard():
        nonlocal last_probe,last_storage
        now=time.monotonic();assert now-start < 1800
        if now-last_probe>2:
            assert idle() and psutil.virtual_memory().available > 20_000_000_000
            assert shutil.disk_usage(STORE.anchor).free > 40_000_000_000
            if cuda_ready:assert torch.cuda.mem_get_info()[0]>3_000_000_000
            last_probe=now
        if now-last_storage>15 and STORE.exists():
            storage_check();last_storage=now
    guard()
    rp = OUT/f'{PREFIX}-registration.json'
    assert not rp.exists() and not STORE.exists(), 'Preserve previous attempts'
    import torch
    torch.set_num_threads(1); torch.use_deterministic_algorithms(True)
    assert torch.cuda.is_available()
    cuda_ready=True
    torch.backends.cuda.matmul.allow_tf32=False; torch.backends.cudnn.allow_tf32=False
    inputs = {}
    for prefix in ('exact-initial-checkpoint-control-v1', 'exact-initial-policy-cpu-control-v1',
                   'exact-initial-training-ingest-control-v4', 'sampled-root-accumulator-control-v1', 'root-retained-joint-cpu-control-v1'):
        r, p = [OUT/f'{prefix}-{suffix}.json' for suffix in ('registration','result')]
        reg, result = read(r), read(p)
        assert result['passed'] and result['registration_sha256'] == sha(r)
        inputs.update(reg['inputs']); inputs.update({str(r):sha(r),str(p):sha(p)})
    cp = OUT/'bb-context-candidate.json'; source = cp.read_text()
    mp = OUT/'preflop-allin-matrix-control-v1-matrix.json'; matrix_source = mp.read_text()
    matrix = AllinMatrix(json.loads(matrix_source), source)
    cat = Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    catalog = cat.read_text()
    exe = ROOT/'target/release/examples/hu_sampled_allin_bridge_v3.exe'
    full_exe=ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'
    bank_exe=ROOT/'target/release/examples/hu_sampled_bank_bridge.exe'
    cache = load_complete_cache()
    for p in [Path(__file__), cp, mp, cat, exe, *[ROOT/'tools/research'/name for name in (
        'action_integrated_training_v1.py','action_integrated_checkpoint_v1.py','action_integrated_policy_v1.py',
        'action_integrated_root_accumulator_v1.py','action_integrated_root_table_v1.py',
        'exact_initial_single_policy64_v1.py','exact_initial_training_ingest_v2.py',
        'exact_initial_hybrid_policy_v1.py','exact_initial_hybrid_checkpoint_v1.py',
        'sampled_visible_hybrid_fit_v1.py','sampled_visible_initialization_v1.py',
        'sampled_physical_deals_v1.py','sampled_physical_fit_v1.py')]]:
        inputs[str(p)] = sha(p)
    for prefix in ('root-action-target-control-v1','root-action-integration-v1'):
        r,p=[OUT/f'{prefix}-{suffix}.json' for suffix in ('registration','result')]
        admitted,passed=read(r),read(p)
        assert passed['passed'] and passed['registration_sha256']==sha(r)
        inputs.update(admitted['inputs']);inputs.update({str(r):sha(r),str(p):sha(p)})
    for p in (full_exe,bank_exe,OUT/'ROOT-ACTION-INTEGRATED-TRAINING-PLAN.md',
              ROOT/'tools/research/action_integrated_root_targets_v1.py',
              ROOT/'tools/research/action_integrated_root_evaluation_v1.py',
              ROOT/'tools/research/hu_action_integrated_fresh_review_20260925.py',
              ROOT/'tools/research/ntfs_research_storage_v1.py'):
        inputs[str(p)]=sha(p)
    for p,h in inputs.items(): assert sha(p) == h, p
    inventory=measure();allocated=sum(r['allocated_file_bytes'] for r in inventory)
    assert allocated+3_000_000_000+METADATA_RESERVE<=LIMIT
    cfg = dict(architecture=[302,64,64,4], representation=FEATURE_SPEC,
        **{CONFIG_KEY:POLICY_TYPE,EXACT_KEY:EXACT_POLICY}, exact_bb_root_targets='exact-initial-bb-training-targets-v2',
        current_policy_inference='float64-widened-float32-weights-v1',
        integrated_bb_root_targets='action-integrated-bb-root-targets-v1',
        sampler_seed=368501, action_seed=368502, reservoir_seeds=[368503,368504], fit_seed_base=368505,
        reservoir_capacity=262144, subbatches_per_iteration=8, deals_per_subbatch=64,
        query_limit=100000, device='cuda', fit_steps=512, chunk_size=4096, learning_rate=.003,
        allin_cache_sha256=cache.sha256, torch_version=torch.__version__, numpy_version=np.__version__,
        iteration_weights='equal', max_iterations=2)
    save(rp,dict(inputs=inputs,config=cfg,store=str(STORE),maximum_seconds=1800,
        allocation_cap=3_000_000_000,logical_cap=10_000_000_000,
        storage_admission=dict(roots=inventory,allocated_bytes=allocated,limit_bytes=LIMIT,reserve_bytes=METADATA_RESERVE),
        plan='Two real joint updates, then restore update-one checkpoint and replay update two. Both accumulators and learned models must match; chance/action/reservoir streams and raw native traces must match.',
        gpu_used=True, production_modified=False, strength_candidate=False,
        scope='Native/CUDA correctness gate only, not CPU performance work or a quality claim. No active evaluator modifications.'))
    try:
        create_compressed_directory(STORE); objects = STORE/'objects'; objects.mkdir()
        args = dict(context_source=source, catalog_source=catalog, matrix_sha256=sha(mp), entry_mass=matrix.btn_mass)
        step_args = dict(context_path=cp,catalog_source=catalog,matrix_source=matrix_source,
            matrix_sha256=sha(mp),cache=cache,executable=exe,integration_executable=full_exe,batch_prefix=PREFIX,guard=guard)
        state = initialize(objects,cfg,**args)
        rejected=[]
        from action_integrated_root_accumulator_v1 import IntegratedRootRegrets
        from sampled_root_regret_accumulator_v1 import SampledRootRegrets
        from action_integrated_checkpoint_v1 import validate_model,require_config
        def reject(name,fn):
            try:fn()
            except ValueError:rejected.append(name)
            else:raise AssertionError('Accepted '+name)
        reject('old accumulator state',lambda:IntegratedRootRegrets.restore(
            SampledRootRegrets(sha(cp),sha(mp)).document(),context_sha256=sha(cp),matrix_sha256=sha(mp)))
        fresh=model_document(objects,state['next_model'],**args)
        reject('old model format',lambda:validate_model(dict(fresh,format=5),**args))
        reject('missing estimator config',lambda:require_config({k:v for k,v in cfg.items() if k!='integrated_bb_root_targets'}))
        initial = save_state(objects,state,cfg,**args)
        metrics=[]; root_rows=[[] for _ in range(169)]; root_scalar_max=0.; scalar_max=0.; policy_error=0.; prior_regrets=np.zeros((169,2)); prior_reach=np.zeros(169)
        mdoc=json.loads(matrix_source)
        for iteration in (1,2):
            folder=STORE/f'iteration-{iteration:04d}'
            row=update(folder,objects,state,cfg,**step_args);metrics.append(row)
            query=first_action_view(read(folder/'batch-00/queries.json'),json.loads(source)['nodes'][0]['children'][3]+1)
            used=model_document(objects,row['used_model'],**args)
            pa,ca=probabilities(query,used,catalog_source=catalog,matrix_sha256=sha(mp),entry_mass=matrix.btn_mass,device='cpu')
            pb,cb=probabilities(query,used,catalog_source=catalog,matrix_sha256=sha(mp),entry_mass=matrix.btn_mass,device='cuda')
            policy_error=max(policy_error,float(np.max(abs(pa-pb))))
            original=np.asarray([r['probabilities'] for r in read(folder/'batch-00/policies.json')['policies']])
            assert policy_error<1e-10 and np.max(abs(pa-original))<1e-10
            for b in range(8):
                for r in read(folder/f'batch-{b:02d}'/'integrated-targets.json')['bb_root_corrections']:
                    root_rows[r['hand_class']].append(r['advantages'])
            root_reference=np.array([[math.fsum(r[a] for r in rows) for a in range(4)] for rows in root_rows])
            root_scalar_max=max(root_scalar_max,float(np.max(abs(root_reference-state['root_regret_state'].regrets))))
            assert root_scalar_max<1e-10
            assert state['root_regret_state'].counts.tolist()==[len(rows) for rows in root_rows]
            frozen=read(folder/'current-initial-policy.json')
            root=np.asarray(frozen['root']);calls=np.asarray(frozen['calls'])
            # Scalar independent accumulator reconstruction; reach enters once.
            regret=prior_regrets.copy();reach=prior_reach.copy()
            for c in np.flatnonzero(matrix.btn_mass>0):
                mass=math.fsum(r[c] for r in mdoc['class_mass'])
                jam=math.fsum(r[c]*p[3] for r,p in zip(mdoc['class_mass'],root))
                call=math.fsum(r[c]*p[3] for r,p in zip(mdoc['btn_showdown_entries'],root))
                fold=jam*mdoc['btn_fold'];value=(1-calls[c])*fold+calls[c]*call
                regret[c] += (np.array([fold,call])-value)/mass
                reach[c] += jam/mass
            scalar_max=max(scalar_max,float(np.max(abs(regret-state['exact_btn_state'].regrets))),
                           float(np.max(abs(reach-state['exact_btn_state'].reach))))
            assert scalar_max<1e-10 and state['exact_btn_state'].steps==iteration
            prior_regrets,prior_reach=regret,reach
            assert all(x['used_model']==row['used_model'] for x in row['subbatches'])
            assert all(len(read(folder/f'batch-{i:02d}'/'integrated-targets.json')['bb_root_corrections'])==64 for i in range(8))
            print(json.dumps(dict(completed_joint_update=iteration, seen=[r.seen for r in state['reservoirs']])),flush=True)
        replay_objects=STORE/'replay-objects';shutil.copytree(objects,replay_objects)
        restored=restore_checkpoint(replay_objects,metrics[0]['checkpoint'],config=cfg,**args)
        assert restored['completed_iterations']==1 and restored['exact_btn_state'].steps==1
        replay=update(STORE/'replay-iteration-0002',replay_objects,restored,cfg,**step_args)
        assert state['root_regret_state'].document()==restored['root_regret_state'].document()
        assert state['next_model']==restored['next_model']
        assert state['played_bank']==restored['played_bank']
        assert state['exact_btn_state'].document()==restored['exact_btn_state'].document()
        assert state['sampler'].checkpoint()==restored['sampler'].checkpoint()
        assert state['action_rng'].bit_generator.state==restored['action_rng'].bit_generator.state
        for a,b in zip(state['reservoirs'],restored['reservoirs']):
            assert a.summary()==b.summary() and a.rng.bit_generator.state==b.rng.bit_generator.state
            for name in ('keys','active','arity','values','iterations'):
                assert np.array_equal(getattr(a,name),getattr(b,name))
        for a,b in zip(metrics[1]['subbatches'],replay['subbatches']):
            assert a==b
        for a,b in zip(metrics[1]['fits'],replay['fits']):
            assert {k:v for k,v in a.items() if k not in ('setup_seconds','optimizer_seconds')} == {
                k:v for k,v in b.items() if k not in ('setup_seconds','optimizer_seconds')}
        last=model_document(objects,state['next_model'],**args)
        assert any(np.ptp(row['advantages'])>0 for row in read(STORE/'iteration-0002/batch-00/derived-targets.json')['bb_root_corrections'])
        assert last['generation']==2 and len(state['played_bank'])==2
        # Final restore also checks regenerated sampled tables against corrected reservoirs.
        final=restore_checkpoint(objects,metrics[-1]['checkpoint'],config=cfg,**args)
        assert final['exact_btn_state'].document()==state['exact_btn_state'].document()
        assert final['root_regret_state'].document()==state['root_regret_state'].document()
        # Bank averaging uses native own-action histories, rather than inventing
        # histories for the original current-policy transport.
        import subprocess
        batch=read(STORE/'iteration-0002/batch-00/batch.json')
        plain={k:v for k,v in batch.items() if k not in ('allin_counts','allin_cache_sha256','terminal_estimator')};plain['format']=2
        bp=STORE/'average-batch.json';qp=STORE/'average-queries.json';save(bp,plain)
        guard();native=subprocess.run([str(bank_exe),'queries',str(cp),str(bp),'-',str(qp)],capture_output=True,text=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        assert native.returncode==0,native.stderr[-2000:]
        query=read(qp);documents=[model_document(objects,r,**args) for r in state['played_bank']]
        w=np.tile(np.arange(1,3,dtype=float),(2,1))
        cpu=ActionIntegratedCpuBank64(documents,completed_iterations=2,weights_by_player=w,**args)
        gpu=ActionIntegratedCudaBank64(documents,w,completed_iterations=2,models_per_chunk=2,guard=guard,**args)
        pc,rc=cpu.average(query,guard=guard);pg,rg=gpu.average(query,guard=guard)
        bank_policy_error=float(np.max(abs(pc-pg)));bank_reach_error=float(np.max(abs(rc-rg)))
        assert bank_policy_error<1e-10 and bank_reach_error<1e-10
        del gpu
        for p,h in inputs.items():assert sha(p)==h,p
        guard()
        files={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()}
        result=dict(passed=True,registration_sha256=sha(rp),seconds=time.monotonic()-start,
            terminal=True,config=cfg,completed_iterations=2,store=str(STORE),control_only=True,
            steps=[dict(iteration=i,checkpoint=m['checkpoint'],metrics_sha256=sha(STORE/f'iteration-{i:04d}'/'metrics.json')) for i,m in enumerate(metrics,1)],
            maximum_current_policy_error=policy_error,maximum_average_policy_error=bank_policy_error,maximum_average_reach_error=bank_reach_error,
            rejected_incompatible_inputs=rejected,storage=storage_check(),
            completed_updates=2,fresh_training_deals=1024,replayed_deals=512,
            initial_checkpoint=initial,final_checkpoint=metrics[-1]['checkpoint'],artifacts=files,
            maximum_independent_exact_state_error=scalar_max,maximum_root_sum_error=root_scalar_max,
            root_samples=int(state['root_regret_state'].counts.sum()),
            resume_native_artifacts_identical=True,resume_models_identical=True,
            resume_reservoirs_and_rngs_identical=True,exact_update_once_per_generation=True,
            gpu_used=True,production_modified=False,accuracy_qualified=False,
            limitation='Two CUDA updates validate integration/restart only. No model performance or range-quality conclusion.')
        save(OUT/f'{PREFIX}-result.json',result)
        print(json.dumps({k:v for k,v in result.items() if k!='artifacts'}),flush=True)
    except BaseException as exc:
        save(OUT/f'{PREFIX}-result.json',dict(passed=False,registration_sha256=sha(rp),
            seconds=time.monotonic()-start,error=repr(exc),gpu_used=True,production_modified=False))
        raise


if __name__=='__main__':
    assert sys.argv[1:]==['--run']
    assert idle() and not LOCK.exists() and not OTHER.exists()
    with LOCK.open('x') as f:f.write(str(os.getpid()))
    try:
        assert idle() and not OTHER.exists()
        main()
    finally:
        assert LOCK.read_text().strip()==str(os.getpid())
        LOCK.unlink()
