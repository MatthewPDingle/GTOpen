"""Bounded implementation check of shared-context GPU fitting; synthetic targets."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',
                  CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONDONTWRITEBYTECODE='1')
import gc
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback
import numpy as np
import psutil
import torch
import test_stack_context_fit_rows_v1 as fixtures
from stack_context_training_fit_v1 import fit,fresh_network,PreparedContextObjective
from stack_context_fit_rows_v1 import prepare
from board_prefix_publication_v1 import atomic_json
from board_study_storage_v1 import create,measure
from global_research_inventory_v3 import measure as inventory
from river_matched_training_pilot_v1 import ROOT,OUT,LOCK,OTHER,available,production_available

NAME='stack-context-fitter-control-v1'
STORE=Path('S:/GTOpen-research')/NAME
REG,ATTEMPT,RESULT,FAILURE=(OUT/(NAME+s+'.json') for s in ('-registration','-attempt','-result','-failure'))


def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def loaded(net,width,device):
    model=fresh_network(0,width).double().to(device)
    with torch.no_grad():
        for i,j in enumerate((0,2,4)):
            model[j].weight.copy_(torch.tensor(net[f'w{i}'],device=device).double().reshape_as(model[j].weight))
            model[j].bias.copy_(torch.tensor(net[f'b{i}'],device=device).double())
    return model


def main():
    assert not any(p.exists() for p in (REG,ATTEMPT,RESULT,FAILURE,STORE,LOCK,OTHER))
    ready,admission=available()
    if not ready:
        print(json.dumps(dict(deferred=True,admission=admission)));return
    fixtures.FitRowsTests.setUpClass();fixture=fixtures.FitRowsTests()
    paths={Path(__file__).resolve(),OUT/'STACK-CONTEXT-FITTER-CONTROL-PLAN.md'}
    for d in fixtures.DEPTHS:
        paths.update((fixtures.GEOMETRY/'fixtures'/f'stack-{d}-context.json',
                      fixtures.GEOMETRY/f'stack-{d}-public.json',fixtures.QUERIES/f'stack-{d}-queries.json'))
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path and Path(path).is_relative_to(ROOT) and Path(path).suffix=='.py':paths.add(Path(path))
    source_proof=OUT/'stack-context-full-control-v1-registration.json'
    prior=json.loads(source_proof.read_bytes())['inputs'];paths.add(source_proof)
    for path in paths:
        if path.is_relative_to(Path('S:/GTOpen-research')):assert sha(path)==prior[str(path)]
    spec=dict(inputs={str(p):sha(p) for p in sorted(paths)},maximum_seconds=600,maximum_cuda_bytes=1_000_000_000,
              maximum_new_bytes=64_000_000,storage_reserve_bytes=16_000_000,steps=256,chunk_size=128,
              seed_base=9300201,learning_rate=.003,raw_absolute_tolerance=1e-10,
              exact_captured_network_required=True,synthetic_targets=True,scientific_training=False)
    with LOCK.open('x') as stream:stream.write(str(os.getpid()))
    began=time.monotonic()
    try:
        accounting=inventory()
        assert sum(r['allocated_file_bytes'] for r in accounting)+80_000_000 <= 800_000_000_000
        create(STORE);atomic_json(REG,spec)
        atomic_json(ATTEMPT,dict(pid=os.getpid(),process_created=psutil.Process().create_time(),registration_sha256=sha(REG),admission=admission))
        atomic_json(STORE/'admission.json',accounting)
        torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        torch.cuda.set_per_process_memory_fraction(spec['maximum_cuda_bytes']/torch.cuda.get_device_properties(0).total_memory)
        last_probe=0.
        def guard():
            nonlocal last_probe
            now=time.monotonic()
            assert now-began < spec['maximum_seconds']
            assert torch.cuda.memory_reserved() < spec['maximum_cuda_bytes']
            if now-last_probe > 2:
                assert not OTHER.exists() and production_available()
                assert psutil.virtual_memory().available > 24_000_000_000 and psutil.disk_usage('S:/').free > 40_000_000_000
                assert torch.cuda.mem_get_info()[0] > 2_000_000_000
                last_probe=now
        cpu_rng=torch.get_rng_state().clone();cuda_rng=torch.cuda.get_rng_state().clone();records=[]
        for registry in fixture.registries:
            width=registry.manifest['representation']['input_width']
            for actor,stores in enumerate(fixture.reservoirs):
                guard();weights=fixture.weights(registry)
                grouped=prepare(registry,stores,player=actor,context_weights=weights)
                raw={};gradients={};losses={}
                for device in ('cpu','cuda'):
                    model=fresh_network(spec['seed_base']+actor,width).double().to(device)
                    prepared=PreparedContextObjective(grouped,device,dtype=torch.float64,guard=guard)
                    raw[device]=model(prepared.x).detach().cpu().numpy()
                    losses[device]=prepared.objective(model,128,guard,backward=True)
                    gradients[device]=np.concatenate([p.grad.detach().cpu().numpy().reshape(-1) for p in model.parameters()])
                    del model,prepared
                forward_error=float(np.max(abs(raw['cpu']-raw['cuda'])))
                grad_error=float(np.max(abs(gradients['cpu']-gradients['cuda'])))
                assert max(forward_error,grad_error,abs(losses['cpu']-losses['cuda']))<=spec['raw_absolute_tolerance']
                options=dict(player=actor,context_weights=weights,seed=spec['seed_base']+actor,steps=spec['steps'],
                             device='cuda',chunk_size=spec['chunk_size'],learning_rate=spec['learning_rate'],guard=guard)
                a,ma=fit(registry,stores,captured=False,**options)
                b,mb=fit(registry,stores,captured=True,**options)
                assert a==b,'Direct/captured network differs'
                excluded={'captured','setup_seconds','optimizer_seconds','graph_capture_seconds'}
                assert {k:v for k,v in ma.items() if k not in excluded}=={k:v for k,v in mb.items() if k not in excluded}
                fitted={}
                for device in ('cpu','cuda'):
                    model=loaded(a,width,device)
                    with torch.no_grad():fitted[device]=model(torch.as_tensor(grouped['features'],dtype=torch.float64,device=device)).cpu().numpy()
                    del model
                fitted_error=float(np.max(abs(fitted['cpu']-fitted['cuda'])))
                assert fitted_error<=spec['raw_absolute_tolerance']
                stem=f'{width}-p{actor}'
                with (STORE/(stem+'-raw.npz')).open('xb') as stream:
                    np.savez_compressed(stream,cpu=raw['cpu'],gpu=raw['cuda'],gradient_cpu=gradients['cpu'],gradient_gpu=gradients['cuda'],
                                        fitted_cpu=fitted['cpu'],fitted_gpu=fitted['cuda'])
                atomic_json(STORE/(stem+'-networks.json'),dict(direct=a,captured=b,direct_metrics=ma,captured_metrics=mb))
                records.append(dict(width=width,actor=actor,rows=len(grouped['keys']),forward_error=forward_error,
                                    gradient_error=grad_error,loss_error=abs(losses['cpu']-losses['cuda']),
                                    fitted_error=fitted_error,objective_sha256=ma['objective_sha256'],
                                    loss_before=ma['normalized_grouped_loss_before'],loss_after=ma['normalized_grouped_loss_after']))
                print(json.dumps(dict(completed_case=stem,loss_before=records[-1]['loss_before'],loss_after=records[-1]['loss_after'])),flush=True)
                gc.collect();torch.cuda.empty_cache()
        memory=[];networks=[]
        for repeat in range(3):
            guard();net,_=fit(registry,stores,captured=True,**dict(options,steps=4))
            networks.append(net);gc.collect();torch.cuda.synchronize();torch.cuda.empty_cache()
            memory.append(dict(allocated=torch.cuda.memory_allocated(),reserved=torch.cuda.memory_reserved()))
        assert all(net==networks[0] for net in networks)
        assert all(r==memory[0] for r in memory)
        assert torch.equal(cpu_rng,torch.get_rng_state()) and torch.equal(cuda_rng,torch.cuda.get_rng_state())
        for path,identity in spec['inputs'].items():assert sha(path)==identity,path
        size=measure(STORE);assert size['logical_bytes'] < spec['maximum_new_bytes']
        result=dict(complete=True,passed=True,registration_sha256=sha(REG),cases=records,repeat_fit_memory=memory,
                    exact_captured_networks=True,rng_unchanged=True,storage=size,seconds=time.monotonic()-began,
                    peak_reserved_cuda_bytes=torch.cuda.max_memory_reserved(),artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()},
                    scientific_training=False,accuracy_qualified=False,training_checkpoint_qualified=False)
        atomic_json(RESULT,result)
        print(json.dumps({k:result[k] for k in ('passed','seconds','peak_reserved_cuda_bytes')}))
    except BaseException as error:
        atomic_json(FAILURE,dict(error=repr(error),traceback=traceback.format_exc(),retry_allowed=False));raise
    finally:
        assert LOCK.read_text()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':main()
