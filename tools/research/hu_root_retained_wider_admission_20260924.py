"""Candidate-specific numeric and storage timing control; no new strength test."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',CUBLAS_WORKSPACE_CONFIG=':4096:8')
import json
from pathlib import Path
import shutil
import time
import numpy as np
import psutil
from later_average_support_v1 import OUT
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from root_retained_wider_inputs_v1 import admitted
import sys
from root_retained_policy_v1 import RootRetainedCpuBank64
from root_retained_policy_v1 import RootRetainedCudaBank64
from sampled_physical_deals_v1 import PhysicalDeals
from sampled_conditional_root_evaluation_v1 import batch_values

from reboot_research_idle_v1 import idle
from ntfs_research_storage_v1 import create_compressed_directory,measure_tree

PREFIX='root-retained-wider-admission-v1'
STORE=Path('T:/GTOpen-research')/PREFIX
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def main():
    global PREFIX,STORE
    control='--control' in sys.argv
    assert sys.argv[1:] in (['--run'],['--control','--run'])
    if control:PREFIX='root-retained-wider-admission-control-v1';STORE=Path('T:/GTOpen-research')/PREFIX
    seed=356031 if control else 356231
    start=time.monotonic();last=[0.];cuda_ready=[False]
    def guard():
        assert time.monotonic()-start<1200
        if time.monotonic()-last[0]>2:
            assert idle() and psutil.virtual_memory().available>20_000_000_000 and shutil.disk_usage('T:/').free>40_000_000_000
            if cuda_ready[0]:assert torch.cuda.mem_get_info()[0]>3_000_000_000
            last[0]=time.monotonic()
    guard();assert not LOCK.exists() and not OTHER.exists() and not STORE.exists()
    data=admitted(control=control);guard();inputs=data['inputs']
    for name in ('root_retained_wider_inputs_v1.py','root_retained_policy_v1.py','root_retained_checkpoint_v1.py','sampled_visible_hybrid_cpu64_v1.py','sampled_visible_hybrid_gpu_bank_v1.py',
                 'sampled_conditional_root_evaluation_v1.py','wider_root_evaluation_v2.py','wider_root_readback_v2.py','ntfs_research_storage_v1.py'):
        p=ROOT/'tools/research'/name;inputs[str(p)]=sha(p)
    for p in (Path(__file__),ROOT/'target/release/examples/hu_sampled_bank_bridge.exe',ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'):
        inputs[str(p)]=sha(p)
    rp=OUT/f'{PREFIX}-registration.json';assert not rp.exists()
    save(rp,dict(inputs=inputs,store=str(STORE),seed=seed,deals=64,maximum_seconds=1200,
        checkpoint=data['checkpoint'],policy_sha256=data['policy_sha256'],cache_sha256=data['cache'].sha256,
        policy_tolerance=1e-10,reach_tolerance=1e-10,payoff_tolerance_bb=1e-8,
        count=data['count'],control_only=control,
        scope='Complete linear root-retained bank CPU/CUDA numerical agreement and compressed output cost on independent control deals. Not a strategic holdout or candidate selection test.',production_modified=False))
    acquired=False;error=None
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True
        import torch
        torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        cuda_ready[0]=True;guard()
        assert not OTHER.exists() and idle()
        create_compressed_directory(STORE)
        cpu=RootRetainedCpuBank64(data['models'],completed_iterations=data['count'],weights_by_player=data['weights'],**data['bank_args'])
        gpu=RootRetainedCudaBank64(data['models'],data['weights'],completed_iterations=data['count'],models_per_chunk=8,guard=guard,**data['bank_args'])
        sampler=PhysicalDeals(data['context_source'],mode='full_deck',seed=seed)
        batch=dict(format=2,batch_id=PREFIX,seed=0,query_limit=100000,deals=sampler.sample(64)['deals'])
        compared={};saved={}
        class Compared:
            def average(self,q,*,guard):
                assert json.loads(q['batch_source'])==batch
                a=time.monotonic();cp,cr=cpu.average(q,guard=guard);cpu_seconds=time.monotonic()-a
                a=time.monotonic();gp,gr=gpu.average(q,guard=guard);torch.cuda.synchronize();gpu_seconds=time.monotonic()-a
                pe=float(np.max(abs(cp-gp)));re=float(np.max(abs(cr-gr)))
                assert pe<1e-10 and re<1e-10
                obs=q['observations'];phases=sorted({o['phase'] for o in obs})
                assert phases==[0,1,2,3] and any(o['own_history'] for o in obs)
                compared.update(observations=len(obs),phases=phases,own_history_rows=sum(bool(o['own_history']) for o in obs),
                    maximum_policy_error=pe,maximum_reach_error=re,cpu_average_seconds=cpu_seconds,gpu_average_seconds=gpu_seconds)
                saved.update(queries=q,policy=cp,reach=cr)
                return gp,gr
        before=time.monotonic()
        g=batch_values(data['context_path'],batch,STORE/'gpu',guard,Compared(),data['cache'])
        gpu_batch_seconds=time.monotonic()-before-compared['cpu_average_seconds']
        class CachedCpu:
            def average(self,q,*,guard):
                guard();assert q==saved['queries'];return saved['policy'],saved['reach']
        c=batch_values(data['context_path'],batch,STORE/'cpu',guard,CachedCpu(),data['cache'])
        payoff_error=max(float(np.max(abs(np.asarray(g[k])-np.asarray(c[k])))) for k in ('action_values','baseline_values'))
        assert payoff_error<1e-8 and g['classes']==c['classes']
        for part in ('gpu','cpu'):
            for p in (STORE/part).rglob('*'):
                guard()
                if p.is_file():
                    with p.open('r+b') as f:os.fsync(f.fileno())
        physical=dict(**measure_tree(STORE/'gpu',guard),
                      file_hashes={str(p.relative_to(STORE/'gpu')):sha(p) for p in (STORE/'gpu').rglob('*') if p.is_file()})
        assert physical['compressed_files']==physical['files']
        for p,h in inputs.items():assert sha(p)==h,p
        guard();save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(rp),numerics=compared,control_only=control,count=data['count'],
            maximum_payoff_error_bb=payoff_error,gpu_batch_seconds_excluding_cpu_comparison=gpu_batch_seconds,
            gpu_batch_storage=physical,seconds=time.monotonic()-start,
            gpu_summary_sha256=sha(STORE/'gpu/summary.json'),cpu_summary_sha256=sha(STORE/'cpu/summary.json'),
            accuracy_qualified=False,production_modified=False,
            limitation='One 64-deal control: timing/storage are admission estimates, not guaranteed full-run bounds or accuracy results.'))
        print(dict(passed=True,numerics=compared,payoff_error=payoff_error,gpu_batch_seconds=gpu_batch_seconds,
            logical_bytes=physical['logical_bytes'],seconds=time.monotonic()-start),flush=True)
    except BaseException as exc:error=repr(exc);raise
    finally:
        status=OUT/f'{PREFIX}-status.json'
        save(status,dict(state='stopped' if error else 'complete',error=error,seconds=time.monotonic()-start,production_modified=False))
        if acquired:
            assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':main()
