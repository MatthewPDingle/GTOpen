"""Registered fixed-policy precision/cost pilot; no training, GPU or promotion."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
from concurrent.futures import ProcessPoolExecutor,wait,FIRST_COMPLETED
import json
from pathlib import Path
import subprocess
import time
import numpy as np
import psutil
from board_fixed_policy_control_v1 import ROOT,OUT,read,save,sha,policy_rows
from board_root_components_control_v1 import preflop_policy
from board_root_components_v1 import board_terms,exact_terms,validate_context
from board_variable_pairs_control_v1 import native_pair_values
from class_stratified_physical_deals_v1 import ClassStratifiedDeals
from sampled_physical_deals_v1 import PhysicalDeals
from preflop_allin_matrix_v1 import AllinMatrix
from storage_strategic_common_prior_20260920 import PAIRS,CLASSES
from bounded_parallel_evaluation_archive_v2 import production_available

PREFIX='board-precision-pilot-v1'
STORE=Path('S:/GTOpen-research')/PREFIX
REG=OUT/f'{PREFIX}-registration.json'
STATE=None


def initialize(reg):
    global STATE
    from threadpoolctl import threadpool_limits
    limit=threadpool_limits(limits=1)
    source=Path(reg['context']).read_text();context=json.loads(source);validate_context(context)
    model=read(reg['model']);matrix=AllinMatrix(read(reg['matrix']),source)
    args=dict(catalog_source=Path(reg['catalog']).read_text(),matrix_sha256=sha(reg['matrix']),entry_mass=matrix.btn_mass)
    pre,_=preflop_policy(read(reg['physical_catalog']),context,model,args)
    sampler=PhysicalDeals(source,mode='full_deck',seed=0)
    STATE=dict(source=source,context=context,model=model,args=args,pre=pre,sampler=sampler,
               class_mass=matrix.bb_mass,exact=exact_terms(matrix,pre),limit=limit)


def task(job):
    started=time.perf_counter();cpu_started=time.process_time();s=STATE
    assert psutil.virtual_memory().available>20*2**30 and psutil.disk_usage('S:/').free>40*2**30
    folder=STORE/job['id'];folder.mkdir(exist_ok=False)
    if job['kind']=='board':
        legal=~np.isin(PAIRS,job['board']).any(1)
        ids=[np.flatnonzero(legal&(s['sampler'].weights[p]>0)) for p in (0,1)]
        weights=[s['sampler'].weights[p,i] for p,i in enumerate(ids)]
        request=folder/'request.json';save(request,dict(board=job['board'],hands=[PAIRS[i].tolist() for i in ids]))
        raw=subprocess.check_output([str(ROOT/'target/release/examples/hu_fixed_board_tree_v1.exe'),
              str(OUT/'bb-context-candidate.json'),str(request)],creationflags=subprocess.CREATE_NO_WINDOW,timeout=120)
        import hashlib
        tree_sha=hashlib.sha256(raw).hexdigest();tree=json.loads(raw);del raw
        post=policy_rows(tree,s['model'],'saved-network')
        values=board_terms(tree,post,s['pre'],weights,[CLASSES[i] for i in ids],s['sampler'].masses[0],s['class_mass'])
        evidence=dict(native_tree_sha256=tree_sha,request_sha256=sha(request),supported_holdings=[len(i) for i in ids])
    else:
        values,paths=native_pair_values(folder,job['deals'],s['model'],s['args'],s['source'],
                 ROOT/'target/release/examples/hu_variable_continuation_pairs_v1.exe')
        evidence=dict(artifacts={str(p):sha(p) for p in paths},hand_classes=job['hand_classes'])
    result=dict(id=job['id'],kind=job['kind'],variable_values=values.tolist(),evidence=evidence,
                worker_wall_seconds=time.perf_counter()-started,python_cpu_seconds=time.process_time()-cpu_started)
    assert result['worker_wall_seconds']<180
    path=STORE/(job['id']+'-result.json');save(path,result)
    return dict(id=job['id'],result=str(path),sha256=sha(path),seconds=result['worker_wall_seconds'])


def main():
    assert not REG.exists(), 'Existing pilot must be inspected, never implicitly restarted'
    assert production_available() and psutil.virtual_memory().available>28*2**30
    assert psutil.cpu_percent(interval=3)<50 and psutil.disk_usage('S:/').free>40*2**30
    control_path=OUT/'board-variable-pairs-control-v1-result.json';control=read(control_path)
    assert control['passed']
    for path,digest in control['inputs'].items():assert sha(path)==digest,path
    model_paths=[p for p in control['inputs'] if '/objects/' in p.replace('\\','/')];assert len(model_paths)==1
    cp=OUT/'bb-context-candidate.json';source=cp.read_text();sampler=ClassStratifiedDeals(source,seed=9279702)
    private=sampler.sample(169*32);assert private['class_counts']==[32]*169
    rng=np.random.default_rng(9279701);boards=[]
    for _ in range(32):
        b=rng.choice(52,size=5,replace=False).tolist();b[:3]=sorted(b[:3]);boards.append(b)
    private_jobs=[dict(kind='private',id=f'private-{i//64:03d}',deals=private['deals'][i:i+64],
                     hand_classes=private['hand_classes'][i:i+64]) for i in range(0,len(private['deals']),64)]
    jobs=[]
    # Interleave estimator work to reduce drift from the concurrent audit.
    for i,board in enumerate(boards):
        jobs.append(dict(kind='board',id=f'board-{i:03d}',board=board))
        jobs.extend(private_jobs[i*3:(i+1)*3])
    assert len(jobs)==32+len(private_jobs) and len({j['id'] for j in jobs})==len(jobs)
    STORE.mkdir(exist_ok=False);sample_path=STORE/'private-sample.json';save(sample_path,private)
    paths=[control_path,Path(__file__),sample_path,OUT/'BOARD-PRECISION-PILOT-PLAN.md',
           *Path(__file__).parent.glob('*.py')]
    inputs=dict(control['inputs']);inputs.update({str(p):sha(p) for p in paths})
    registration=dict(format=1,model=model_paths[0],context=str(cp),
        matrix=str(OUT/'preflop-allin-matrix-control-v1-matrix.json'),
        catalog='S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json',
        physical_catalog='S:/GTOpen-research/board-root-components-control-v1/preflop-catalog.json',
        inputs=inputs,jobs=jobs,workers=4,maximum_seconds=3600,
        board_seed=9279701,private_seed=9279702,boards=32,private_deals=5408,
        comparison='Descriptive class variance, entry-weighted mean variance, and summed-worker-wall-time efficiency for call-fold, raise-fold, raise-call; no playing-strength inference.',
        no_optional_stopping=True,gpu_used=False,training_changed=False,production_modified=False)
    save(REG,registration)
    began=time.monotonic();remaining=iter(jobs);pending={};finished=[]
    try:
        with ProcessPoolExecutor(max_workers=4,initializer=initialize,initargs=(registration,)) as pool:
            while True:
                assert time.monotonic()-began<3600
                ready=production_available() and psutil.virtual_memory().available>24*2**30 and psutil.disk_usage('S:/').free>40*2**30
                while ready and len(pending)<4:
                    job=next(remaining,None)
                    if job is None:break
                    pending[pool.submit(task,job)]=job['id']
                if not pending:
                    if ready:break
                    time.sleep(5);continue
                done,_=wait(pending,timeout=5,return_when=FIRST_COMPLETED)
                for future in done:
                    item=future.result();del pending[future];finished.append(item)
                    print(json.dumps(dict(completed=len(finished),total=len(jobs),**item)),flush=True)
        assert len(finished)==len(jobs)
        for path,digest in inputs.items():assert sha(path)==digest,path
        save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(REG),results=finished,
             seconds=time.monotonic()-began,analysis_pending=True,accuracy_qualified=False,production_modified=False))
    except BaseException as error:
        save(OUT/f'{PREFIX}-failure.json',dict(passed=False,registration_sha256=sha(REG),error=repr(error),completed=finished))
        raise


if __name__=='__main__':main()
