"""Larger, independently seeded repeat of the completed estimator pilot."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
from concurrent.futures import ProcessPoolExecutor,wait,FIRST_COMPLETED
import json
from pathlib import Path
import time
import numpy as np
import psutil
import board_precision_pilot_v1 as base
from board_fixed_policy_control_v1 import ROOT,OUT,read,save,sha
from class_stratified_physical_deals_v1 import ClassStratifiedDeals
from bounded_parallel_evaluation_archive_v2 import production_available

PREFIX='board-precision-repeat-v1'
STORE=Path('S:/GTOpen-research')/PREFIX
REG=OUT/f'{PREFIX}-registration.json'
STATE=None


def initialize(reg):
    global STATE
    base.STORE=STORE
    base.initialize(reg)
    STATE=base.STATE


def main():
    assert not REG.exists(), 'Inspect existing run; do not restart implicitly'
    assert production_available() and psutil.virtual_memory().available>28*2**30
    assert psutil.cpu_percent(interval=3)<50 and psutil.disk_usage('S:/').free>40*2**30
    original_reg=base.REG;original_result=OUT/'board-precision-pilot-v1-result.json'
    review_path=OUT/'board-precision-pilot-v1-review.json';review=read(review_path)
    assert review['passed'] and review['registration_sha256']==sha(original_reg)
    assert review['pilot_result_sha256']==sha(original_result)
    prior=read(original_reg)
    for path,digest in prior['inputs'].items():assert sha(path)==digest,path
    source=Path(prior['context']).read_text()
    private=ClassStratifiedDeals(source,seed=9279802).sample(169*128)
    assert private['class_counts']==[128]*169
    rng=np.random.default_rng(9279801);boards=[]
    for _ in range(128):
        b=rng.choice(52,size=5,replace=False).tolist();b[:3]=sorted(b[:3]);boards.append(b)
    private_jobs=[dict(kind='private',id=f'private-{i//64:03d}',deals=private['deals'][i:i+64],
                      hand_classes=private['hand_classes'][i:i+64]) for i in range(0,21632,64)]
    jobs=[]
    for i,board in enumerate(boards):
        jobs.append(dict(kind='board',id=f'board-{i:03d}',board=board));jobs.extend(private_jobs[i*3:(i+1)*3])
    assert len(jobs)==466 and len({j['id'] for j in jobs})==466
    STORE.mkdir(exist_ok=False);sample_path=STORE/'private-sample.json';save(sample_path,private)
    paths=[original_reg,original_result,review_path,Path(__file__),sample_path,
           OUT/'BOARD-PRECISION-REPEAT-PLAN.md',*Path(__file__).parent.glob('*.py')]
    inputs=dict(prior['inputs']);inputs.update({str(p):sha(p) for p in paths})
    registration={k:prior[k] for k in ('format','model','context','matrix','catalog','physical_catalog')}
    registration.update(inputs=inputs,jobs=jobs,workers=4,maximum_seconds=3600,
        board_seed=9279801,private_seed=9279802,boards=128,private_deals=21632,
        comparison=prior['comparison'],no_optional_stopping=True,gpu_used=False,
        training_changed=False,production_modified=False,independent_repeat_of=str(original_reg))
    save(REG,registration)
    began=time.monotonic();remaining=iter(jobs);pending={};finished=[]
    try:
        with ProcessPoolExecutor(max_workers=4,initializer=initialize,initargs=(registration,)) as pool:
            while True:
                assert time.monotonic()-began<3600
                ready=(production_available() and psutil.virtual_memory().available>24*2**30
                       and psutil.disk_usage('S:/').free>40*2**30 and psutil.cpu_percent(interval=.2)<65)
                while ready and len(pending)<4:
                    job=next(remaining,None)
                    if job is None:break
                    pending[pool.submit(base.task,job)]=job['id']
                if not pending:
                    if ready:break
                    time.sleep(5);continue
                done,_=wait(pending,timeout=5,return_when=FIRST_COMPLETED)
                for future in done:
                    item=future.result();del pending[future];finished.append(item)
                    print(json.dumps(dict(completed=len(finished),total=466,**item)),flush=True)
        assert len(finished)==466
        for path,digest in inputs.items():assert sha(path)==digest,path
        save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(REG),results=finished,
            seconds=time.monotonic()-began,analysis_pending=True,accuracy_qualified=False,production_modified=False))
    except BaseException as error:
        save(OUT/f'{PREFIX}-failure.json',dict(passed=False,registration_sha256=sha(REG),error=repr(error),completed=finished))
        raise


if __name__=='__main__':main()
