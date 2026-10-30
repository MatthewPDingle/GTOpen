"""Bounded synthetic CUDA fit controls; no scientific trial or native export."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import argparse
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import time
import traceback
import numpy as np
import psutil
import torch
import preflop_expected_training_control_fixture_v1 as f
cp,fit=f.cp,f.fit
from bounded_parallel_evaluation_archive_v2 import production_available
from sampled_physical_fit_v1 import export_network

def guard():
    if not production_available() or psutil.virtual_memory().available<20_000_000_000:
        raise RuntimeError('Yield to active solve or RAM pressure')
    if torch.cuda.mem_get_info()[0]<2_000_000_000:raise RuntimeError('Insufficient CUDA reserve')

def admission():
    guard()
    raw=subprocess.check_output(['nvidia-smi','--query-gpu=utilization.gpu,memory.used','--format=csv,noheader,nounits'])
    util,used=[int(v.strip()) for v in raw.decode().strip().split(',')]
    if util>35 or used>16000:raise RuntimeError('Yield to heavier existing GPU workload')
    return dict(gpu_utilization_percent=util,nvidia_memory_used_mib=used,available_ram_bytes=psutil.virtual_memory().available)

def main(output):
    torch.set_num_threads(1);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    admitted=admission();began=time.monotonic();torch.cuda.reset_peak_memory_stats();cases=[]
    for width in (362,387):
        with tempfile.TemporaryDirectory(prefix=f'expected-fit-{width}-',dir=output.parent) as directory:
            registry,resources,config,state=f.fixture(width,directory=directory,fit_steps=4)
            staged=f.stage(directory,state,registry,resources);networks=[];receipts=[];metrics=[]
            for actor in (0,1):
                guard()
                net,receipt,metric=fit.fit(registry,staged['contexts'],resources,config,player=actor,generation=1,
                    collected_against=state['next_model']['sha256'],guard=guard)
                # Independent eager tensor loss/backward/Adam; no captured-gradient function.
                g=fit.prepare(registry,staged['contexts'],resources,player=actor,
                    context_weights=config['context_weights'],preflop_fraction=config['preflop_fraction'])
                model=fit.fresh_network(config['fit_seed_base']+200003+actor,width).cuda()
                x=torch.tensor(g['features'],dtype=torch.float32,device='cuda')
                y=torch.tensor(g['targets'],dtype=torch.float32,device='cuda')
                w=torch.tensor(g['weights'],dtype=torch.float32,device='cuda')
                optimizer=torch.optim.Adam(model.parameters(),lr=config['learning_rate'],betas=(.9,.999),eps=1e-8,
                    weight_decay=0.,amsgrad=False,foreach=False,fused=False)
                before=float(((model(x)-y).square()*w).sum())
                for _ in range(config['fit_steps']):
                    guard();optimizer.zero_grad(set_to_none=False)
                    for start in range(0,len(x),config['chunk_size']):
                        stop=start+config['chunk_size'];((model(x[start:stop])-y[start:stop]).square()*w[start:stop]).sum().backward()
                    optimizer.step()
                eager=export_network(model)
                parameter_error=max(float(np.max(abs(np.asarray(net[k])-np.asarray(eager[k])))) for k in net)
                after=float(((model(x)-y).square()*w).sum())
                assert parameter_error<1e-5
                assert abs(metric['loss_before']-before)<1e-6 and abs(metric['loss_after']-after)<1e-6
                assert metric['loss_after']<metric['loss_before']
                assert receipt==f.receipts(staged,state,registry,resources,config,[net,net])[actor]
                networks.append(net);receipts.append(receipt);metrics.append(dict(metric,actor=actor,
                    captured_eager_maximum_parameter_error=parameter_error,captured_eager_loss_error=abs(metric['loss_after']-after)))
                del model,optimizer,x,y,w
            candidate,reference=cp.complete_cycle(directory,state,staged,config,registry,resources,
                networks=networks,fit_receipts=receipts)
            restored=cp.restore_checkpoint(directory,reference,config,registry,resources)
            f.same_local(candidate['contexts'],restored['contexts'])
            assert restored['completed_cycles']==1 and len(restored['played_bank'])==1
            cases.append(dict(input_width=width,fitted_stacks=[20,40,100,200,400],steps_per_actor=4,
                fits=metrics,complete_cycle_with_actual_synthetic_fits=True))
            print(json.dumps(dict(input_width=width,complete_cycle=True)),flush=True)
    torch.cuda.synchronize()
    result=dict(passed=True,seconds=time.monotonic()-began,cases=cases,inputs=f.inputs(),admission=admitted,
        torch_version=torch.__version__,cuda_version=torch.version.cuda,device=torch.cuda.get_device_name(),
        peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(),process_rss_bytes=psutil.Process().memory_info().rss,
        synthetic_only=True,scientific_attempt=False,native_invocations=0,accuracy_qualified=False,
        representative_speed_benchmark=False,actual_training_worker_qualified=False,production_modified=False)
    with output.open('x',encoding='utf-8') as out:json.dump(result,out,indent=2,allow_nan=False)
    print(json.dumps({k:v for k,v in result.items() if k not in ('inputs','cases')},indent=2),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--result',type=Path,required=True);args=parser.parse_args()
    try:main(args.result)
    except BaseException:
        with args.result.with_name(args.result.stem+'-failure.txt').open('x',encoding='utf-8') as out:out.write(traceback.format_exc())
        raise
