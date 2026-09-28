"""Future full-fit parity check; refuses competing research and production work."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',
    CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONDONTWRITEBYTECODE='1')
import argparse,gc,hashlib,json,sys,time,traceback,uuid
from pathlib import Path
import numpy as np
import psutil
from weighted_training_graph_fit_v2 import fit as reference_fit
from weighted_training_graph_fit_vector_v1 import fit as vector_fit
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir
from board_river_bounds_pilot_support_v2 import Guard,memory_admitted,gpu_snapshot,CUDA_BUDGET_BYTES,LOCK,OTHER
from bounded_parallel_evaluation_archive_v2 import production_available
from board_prefix_publication_v1 import atomic_json

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='visible-features-vector-gpu-control-v1'
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json')
PLAN=OUT/'VISIBLE-FEATURE-VECTOR-GPU-PLAN.md'
CPU_REG=OUT/'visible-features-vector-control-v1-registration.json'
CPU_RESULT=OUT/'visible-features-vector-control-v1-result.json'
PARENT='river-matched-training-pilot-v1';CONTEXT=OUT/'bb-context-candidate.json'
IGNORED={'setup_seconds','optimizer_seconds','graph_capture_seconds','runtime'}

def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def verify(inputs):
    for path,expected in inputs.items():assert sha(path)==expected,path
def metric_math(metric):return {k:v for k,v in metric.items() if k not in IGNORED}

def specification():
    cpu=read(CPU_RESULT);cpu_reg=read(CPU_REG)
    assert cpu['passed'] and cpu['exact_features'] and cpu['registration_sha256']==sha(CPU_REG)
    assert len(cpu['cases'])==8 and cpu['rows']==1558846
    inputs=dict(cpu_reg['inputs']);verify(inputs)
    parent_reg=OUT/(PARENT+'-registration.json');parent=read(parent_reg)
    paths=[Path(__file__),PLAN,CPU_REG,CPU_RESULT,CONTEXT,parent_reg];fixtures=[]
    for fixture in cpu_reg['fixtures']:
        arm=fixture['arm'];player=fixture['player'];cfg=parent['arms'][arm]['config']
        folder=Path(parent['store'])/arm;pp=folder/'progress.json';p=read(pp)
        assert p['completed']==80 and p['registration_sha256']==sha(parent_reg)
        cp=folder/'objects'/p['checkpoint']['file'];assert sha(cp)==p['checkpoint']['sha256']
        state=read(cp);assert state['config']==cfg
        assert Path(fixture['path'])==folder/'objects'/state['reservoirs'][player]['file']
        model=folder/'objects'/state['next_model']['file'];assert sha(model)==state['next_model']['sha256']
        assert read(model)['generation']==80
        metric_path=folder/p['updates'][-1]['metrics'];assert sha(metric_path)==p['updates'][-1]['sha256']
        assert read(metric_path)['iteration']==80
        fixtures.append(dict(fixture,model=str(model),saved_metrics=str(metric_path),config=cfg,
            seed=cfg['fit_seed_base']+80*200003+player))
        paths.extend((pp,cp,model,metric_path))
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path and Path(path).is_relative_to(ROOT) and Path(path).suffix=='.py':paths.append(Path(path))
    inputs.update({str(path):sha(path) for path in paths});verify(inputs)
    return dict(inputs=inputs,fixtures=fixtures,steps=512,maximum_seconds=1200,
        own_cuda_cap_bytes=CUDA_BUDGET_BYTES,exact_saved_networks_required=True,
        exact_numeric_fit_metrics_required=True,paired_order='Alternate reference/vector first by fixture',
        new_payoff_test_deals=0,learning_bank_modified=False,production_modified=False,
        limitation='One paired full fit per fixture; no full-update or end-to-end speed qualification.')

def main(run=False):
    spec=specification()
    if not run:
        print(json.dumps(dict(ready=True,fixtures=len(spec['fixtures']),execution_requires_idle_gpu=True,
            research_lock_present=LOCK.exists() or OTHER.exists(),gpu_fit_started=False)),flush=True);return
    assert not REG.exists() and not RESULT.exists(),'Preserve existing attempts; version an explicit recovery if required'
    assert not LOCK.exists() and not OTHER.exists(),'Existing research has priority'
    assert production_available() and psutil.cpu_percent(interval=1)<50 and psutil.virtual_memory().available>28_000_000_000
    probe=gpu_snapshot();assert probe['utilization_percent']<65 and memory_admitted(probe['free_bytes'],0)
    acquired=False;guard=None
    try:
        with LOCK.open('x') as stream:stream.write(str(os.getpid()))
        acquired=True;verify(spec['inputs']);atomic_json(REG,spec)
        import torch
        assert torch.cuda.is_available()
        assert all(f['config']['torch_version']==torch.__version__ and f['config']['numpy_version']==np.__version__ for f in spec['fixtures'])
        torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        guard=Guard(limit=spec['maximum_seconds']);guard();cases=[]
        for index,fixture in enumerate(spec['fixtures']):
            guard();cfg=fixture['config'];player=fixture['player']
            assert cfg['fit_steps']==512 and cfg['chunk_size']==4096
            reservoir=WeightedPhysicalReservoir.load(fixture['path'],CONTEXT.read_text())
            expected=read(fixture['model']);saved=read(fixture['saved_metrics'])['fits'][player]
            options=dict(seed=fixture['seed'],steps=cfg['fit_steps'],device='cuda',chunk_size=cfg['chunk_size'],
                learning_rate=cfg['learning_rate'],guard=guard)
            implementations=[('reference',reference_fit),('vector',vector_fit)]
            if index%2:implementations.reverse()
            outputs={};details={}
            for label,implementation in implementations:
                gc.collect();torch.cuda.synchronize();torch.cuda.empty_cache();guard()
                torch.cuda.reset_peak_memory_stats();began=time.monotonic()
                network,metric=implementation(reservoir,**options)
                elapsed=time.monotonic()-began
                assert network==expected['networks'][player],'Fitted network differs from original saved model 80'
                assert metric['advantage_scale']==expected['advantage_scales'][player]
                assert metric_math(metric)==metric_math(saved),'Numeric objective or fit settings changed'
                outputs[label]=network
                details[label]=dict(seconds=elapsed,peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                    peak_reserved_bytes=torch.cuda.max_memory_reserved(),metric=metric)
            assert outputs['reference']==outputs['vector']
            assert all(d['peak_allocated_bytes']<=CUDA_BUDGET_BYTES and d['peak_reserved_bytes']<=CUDA_BUDGET_BYTES for d in details.values())
            row=dict(arm=fixture['arm'],player=player,exact_saved_network=True,exact_numeric_fit_metrics=True,
                network_sha256=digest(outputs['vector']),first=implementations[0][0],fits=details,
                observed_wall_ratio=details['reference']['seconds']/details['vector']['seconds'])
            cases.append(row)
            atomic_json(OUT/(NAME+f'-case-{index:02d}.json'),dict(registration_sha256=sha(REG),**row))
            print(json.dumps(dict(arm=fixture['arm'],player=player,passed=True,observed_wall_ratio=row['observed_wall_ratio'])),flush=True)
            del reservoir,expected,outputs,network;gc.collect();torch.cuda.synchronize();torch.cuda.empty_cache();guard()
        verify(spec['inputs'])
        result=dict(passed=True,registration_sha256=sha(REG),cases=cases,seconds=time.monotonic()-guard.started,
            resource_probes=guard.probes,gpu_used=True,new_payoff_test_deals=0,learning_bank_modified=False,
            production_modified=False,accuracy_claim=False,
            next_requirement='Complete-update/checkpoint equality before adopting this runtime in a future study.')
        atomic_json(RESULT,result);print(json.dumps(dict(passed=True,result=str(RESULT))),flush=True)
    except BaseException as error:
        if acquired:
            atomic_json(OUT/(NAME+'-interruption-'+uuid.uuid4().hex[:8]+'.json'),dict(error=repr(error),
                traceback=traceback.format_exc(),preserve_completed_cases=True))
        raise
    finally:
        if acquired:
            assert LOCK.read_text()==str(os.getpid());LOCK.unlink()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');main(parser.parse_args().run)
