"""Small native/CPU joint training and deterministic restart integration gate."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import json
import math
import shutil
import time
from pathlib import Path
import numpy as np
import psutil
from later_average_support_v1 import OUT, read, load_complete_cache
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from preflop_allin_matrix_v1 import AllinMatrix
from exact_initial_training_v1 import initialize, save_state, update
from exact_initial_hybrid_checkpoint_v1 import restore_checkpoint, model_document, POLICY_TYPE, CONFIG_KEY
from sampled_visible_hybrid_checkpoint_v1 import FEATURE_SPEC, encoded
from reboot_research_idle_v1 import idle

PREFIX = 'exact-initial-joint-cpu-control-v1'
STORE = Path('T:/GTOpen-research')/PREFIX


def main():
    start = time.monotonic()
    def guard():
        assert time.monotonic()-start < 600 and idle()
        assert psutil.virtual_memory().available > 20_000_000_000
        assert shutil.disk_usage(STORE.anchor).free > 40_000_000_000
    guard()
    rp = OUT/f'{PREFIX}-registration.json'
    assert not rp.exists() and not STORE.exists(), 'Preserve previous attempts'
    import torch
    torch.set_num_threads(1); torch.use_deterministic_algorithms(True)
    assert not torch.cuda.is_available(), 'This gate cannot compete for CUDA'
    inputs = {}
    for prefix in ('exact-initial-checkpoint-control-v1', 'exact-initial-policy-cpu-control-v1',
                   'exact-initial-training-ingest-control-v4'):
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
    cache = load_complete_cache()
    for p in [Path(__file__), cp, mp, cat, exe, *[ROOT/'tools/research'/name for name in (
        'exact_initial_training_v1.py','exact_initial_training_ingest_v2.py',
        'exact_initial_hybrid_policy_v1.py','exact_initial_hybrid_checkpoint_v1.py',
        'sampled_visible_hybrid_fit_v1.py','sampled_visible_initialization_v1.py',
        'sampled_physical_deals_v1.py','sampled_physical_fit_v1.py')]]:
        inputs[str(p)] = sha(p)
    for p,h in inputs.items(): assert sha(p) == h, p
    cfg = dict(architecture=[302,64,64,4], representation=FEATURE_SPEC,
        **{CONFIG_KEY:POLICY_TYPE}, exact_bb_root_targets='exact-initial-bb-training-targets-v2',
        sampler_seed=340501, action_seed=340502, reservoir_seeds=[340503,340504], fit_seed_base=340505,
        reservoir_capacity=257, subbatches_per_iteration=2, deals_per_subbatch=16,
        query_limit=100000, device='cpu', fit_steps=4, chunk_size=128, learning_rate=.003,
        allin_cache_sha256=cache.sha256, torch_version=torch.__version__, numpy_version=np.__version__,
        iteration_weights='equal', max_iterations=2)
    save(rp,dict(inputs=inputs,config=cfg,store=str(STORE),maximum_seconds=600,
        plan='Two real joint updates, then restore update-one checkpoint and replay update two. Both exact state and learned models must match; chance/action/reservoir streams and raw native traces must match.',
        gpu_used=False, production_modified=False, strength_candidate=False,
        scope='Native/CPU correctness gate only, not CPU performance work or CUDA qualification. No active evaluator modifications.'))
    try:
        STORE.mkdir(); objects = STORE/'objects'; objects.mkdir()
        args = dict(context_source=source, catalog_source=catalog, matrix_sha256=sha(mp), entry_mass=matrix.btn_mass)
        step_args = dict(context_path=cp,catalog_source=catalog,matrix_source=matrix_source,
            matrix_sha256=sha(mp),cache=cache,executable=exe,batch_prefix=PREFIX,guard=guard)
        state = initialize(objects,cfg,**args)
        initial = save_state(objects,state,cfg,**args)
        metrics=[]; scalar_max=0.; prior_regrets=np.zeros((169,2)); prior_reach=np.zeros(169)
        mdoc=json.loads(matrix_source)
        for iteration in (1,2):
            folder=STORE/f'iteration-{iteration:04d}'
            row=update(folder,objects,state,cfg,**step_args);metrics.append(row)
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
            assert all(len(read(folder/f'batch-{i:02d}'/'derived-targets.json')['bb_root_corrections'])==16 for i in range(2))
            print(json.dumps(dict(completed_joint_update=iteration, seen=[r.seen for r in state['reservoirs']])),flush=True)
        replay_objects=STORE/'replay-objects';shutil.copytree(objects,replay_objects)
        restored=restore_checkpoint(replay_objects,metrics[0]['checkpoint'],config=cfg,**args)
        assert restored['completed_iterations']==1 and restored['exact_btn_state'].steps==1
        replay=update(STORE/'replay-iteration-0002',replay_objects,restored,cfg,**step_args)
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
        for p,h in inputs.items():assert sha(p)==h,p
        guard()
        files={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()}
        result=dict(passed=True,registration_sha256=sha(rp),seconds=time.monotonic()-start,
            completed_updates=2,fresh_training_deals=64,replayed_deals=32,
            initial_checkpoint=initial,final_checkpoint=metrics[-1]['checkpoint'],artifacts=files,
            maximum_independent_exact_state_error=scalar_max,
            resume_native_artifacts_identical=True,resume_models_identical=True,
            resume_reservoirs_and_rngs_identical=True,exact_update_once_per_generation=True,
            gpu_used=False,production_modified=False,accuracy_qualified=False,
            limitation='Two tiny CPU updates validate integration/restart only. No model performance or range-quality conclusion.')
        save(OUT/f'{PREFIX}-result.json',result)
        print(json.dumps({k:v for k,v in result.items() if k!='artifacts'}),flush=True)
    except BaseException as exc:
        save(OUT/f'{PREFIX}-result.json',dict(passed=False,registration_sha256=sha(rp),
            seconds=time.monotonic()-start,error=repr(exc),gpu_used=False,production_modified=False))
        raise


if __name__=='__main__':main()
