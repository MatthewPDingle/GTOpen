"""Combine the qualified CPU pipeline and weighted captured fitter."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',CUBLAS_WORKSPACE_CONFIG=':4096:8')
import argparse
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
from weighted_training_parallel_graph_v2 import update
from weighted_physical_reservoir_v1 import ARRAYS
from ntfs_research_storage_v1 import create_compressed_directory,measure_tree

PREFIX='weighted-parallel-graph-control-v2'


def main(publish=False):
    import torch
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    assert torch.cuda.is_available() and safe_read_only_resources()
    assert not LOCK.exists() and not OTHER.exists()
    status=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.free','--format=csv,noheader,nounits'],
        capture_output=True,text=True,timeout=5,creationflags=subprocess.CREATE_NO_WINDOW)
    assert status.returncode==0
    utilization,free=[float(s.strip()) for s in status.stdout.strip().splitlines()[0].split(',')]
    assert utilization<20 and free>4000 and psutil.cpu_percent(interval=1)<50
    started=time.monotonic();last=0.
    def guard():
        nonlocal last
        assert time.monotonic()-started<900
        if time.monotonic()-last>3:
            assert safe_read_only_resources() and psutil.disk_usage('T:/').free>40_000_000_000
            assert torch.cuda.mem_get_info()[0]>3_000_000_000
            last=time.monotonic()
    assert read(OUT/'weighted-graph-fit-control-v2-result.json')['passed']
    reference_path=OUT/'weighted-training-pilot-v1-result.json';reference=read(reference_path)
    registration_path=OUT/'weighted-training-pilot-v1-registration.json'
    assert reference['passed'] and reference['exact_restart_replay'] and reference['registration_sha256']==sha(registration_path)
    for p,h in read(registration_path)['inputs'].items():assert sha(p)==h,p
    original=Path(reference['store']);original_objects=original/'objects';cfg=reference['config']
    cp=OUT/'bb-context-candidate.json';mp=OUT/'preflop-allin-matrix-control-v1-matrix.json'
    cat=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    source=cp.read_text();catalog_source=cat.read_text();matrix_source=mp.read_text()
    matrix=AllinMatrix(json.loads(matrix_source),source);cache=load_complete_cache()
    args=dict(context_source=source,catalog_source=catalog_source,matrix_sha256=sha(mp),entry_mass=matrix.btn_mass)
    final=checkpoint.restore_checkpoint(original_objects,reference['final_checkpoint'],cfg,**args)
    expected_path=original/'iteration-0002/metrics.json'
    assert sha(expected_path)==reference['steps'][1]['metrics_sha256'];expected=read(expected_path)
    paths=[reference_path,registration_path,cp,mp,cat,expected_path,
        *original_objects.iterdir(),*Path(__file__).parent.glob('*.py'),OUT/'WEIGHTED-PARALLEL-GRAPH-V2-CONTROL-PLAN.md',OUT/'weighted-graph-fit-control-v2-result.json']
    exe=ROOT/'target/release/examples/hu_sampled_allin_bridge_v3.exe'
    trace=ROOT/'target/release/examples/hu_sampled_action_trace_v2.exe'
    full=ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'
    paths.extend((exe,trace,full));inputs={str(p):sha(p) for p in paths}
    store=Path('T:/GTOpen-research')/(PREFIX if publish else PREFIX+'-dev-'+str(time.time_ns()))
    create_compressed_directory(store);objects=store/'objects';objects.mkdir()
    for p in original_objects.iterdir():
        assert p.is_file();assert reference['artifacts'][str(p)]==sha(p)
        (objects/p.name).write_bytes(p.read_bytes())
    reg=OUT/f'{PREFIX}-registration.json'
    counts=[2]
    if publish:save(reg,dict(inputs=inputs,store=str(store),worker_counts=counts,maximum_pending_per_worker=2,
        reference_generation=2,reference_config=cfg,maximum_seconds=900,maximum_logical_bytes=2_000_000_000,
        utilization_before=utilization,free_vram_MiB_before=free,
        exact_state_required=True,accuracy_claim=False,production_modified=False))
    acquired=False;results=[]
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;guard()
        step=dict(context_path=cp,catalog_source=catalog_source,matrix_source=matrix_source,matrix_sha256=sha(mp),
            cache=cache,executable=exe,integration_executable=full,trace_executable=trace,
            batch_prefix='weighted-training-pilot-v1',guard=guard)
        for index,workers in enumerate(counts):
            guard();assert psutil.cpu_percent(interval=1)<50
            state=checkpoint.restore_checkpoint(objects,reference['steps'][0]['checkpoint'],cfg,**args)
            folder=store/f'run-{index+1}-workers-{workers}'
            metric=update(folder,objects,state,cfg,workers=workers,**step)
            assert metric['checkpoint']==reference['final_checkpoint'] and metric['next_model']==final['next_model']
            assert metric['subbatches']==expected['subbatches']
            assert state['played_bank']==final['played_bank'] and state['sampler'].checkpoint()==final['sampler'].checkpoint()
            assert state['action_rng'].bit_generator.state==final['action_rng'].bit_generator.state
            for a,b in zip(state['reservoirs'],final['reservoirs']):
                assert a.seen==b.seen and a.rng.bit_generator.state==b.rng.bit_generator.state
                assert all(np.array_equal(getattr(a,k),getattr(b,k)) for k in ARRAYS)
            ignored={'setup_seconds','optimizer_seconds','graph_capture_seconds','runtime'}
            for a,b in zip(metric['fits'],expected['fits']):
                assert {k:v for k,v in a.items() if k not in ignored}=={k:v for k,v in b.items() if k not in ignored}
            assert metric['peak_pending']<=2*workers
            pids=sorted({r['pid'] for r in metric['worker_stats']});assert 1<=len(pids)<=workers
            assert not any(psutil.pid_exists(pid) for pid in pids)
            record=dict(run=index+1,workers=workers,seconds=metric['seconds'],timings=metric['timings'],
                peak_pending=metric['peak_pending'],worker_pids=pids,
                largest_worker_rss_bytes=max(r['rss_bytes'] for r in metric['worker_stats']),
                exact_checkpoint_model_native_artifacts_and_reservoirs=True,
                metrics_sha256=sha(folder/'metrics.json'))
            results.append(record);print(json.dumps(record),flush=True)
        for p,h in inputs.items():assert sha(p)==h,p
        disk=measure_tree(store,guard)
        artifacts={str(p):sha(p) for p in store.rglob('*') if p.is_file()}
        logical=sum(Path(p).stat().st_size for p in artifacts);assert logical<2_000_000_000
        result=dict(passed=True,results=results,reference_seconds=expected['seconds'],storage=disk,
            artifacts=artifacts,seconds=time.monotonic()-started,accuracy_qualified=False,production_modified=False)
        if publish:
            result['registration_sha256']=sha(reg);save(OUT/f'{PREFIX}-result.json',result)
        print(json.dumps({k:v for k,v in result.items() if k not in ('artifacts','results')}),flush=True)
    finally:
        if acquired:
            assert LOCK.read_text()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--publish',action='store_true')
    main(parser.parse_args().publish)
