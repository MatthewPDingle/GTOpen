"""Qualified operational inventory for full admission and fixed continuation.

Explicit --run is required; default mode is the frozen driver's readiness.
Each invocation has its own record, including explicit resume attempts.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',CUBLAS_WORKSPACE_CONFIG=':4096:8')
import numpy as np
import argparse
import json
from pathlib import Path
import re
import time
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import sha
from board_prefix_publication_v1 import atomic_json
from board_prefix_resource_wrapper_v2 import scientific_runtime
from global_research_inventory_v2 import measure


def main(stage, run=False, resume=False, attempt='initial'):
    if not re.fullmatch('[a-z0-9][a-z0-9-]{0,39}',attempt): raise ValueError('Simple bounded attempt name required')
    if resume and (stage!='training' or not run or attempt=='initial'):
        raise ValueError('Resume requires training --run and a distinct named attempt')
    if stage=='admission':
        import board_full_storage_admission_v1 as driver
        output=driver.ADMISSION
        callback=lambda:driver.main(run=run)
    elif stage=='training':
        import board_matched_continuation_v1 as driver
        output=OUT/f'{driver.PREFIX}-result.json'
        callback=lambda:driver.main(run=run,resume=resume)
    else: raise ValueError('Unknown full-study stage')
    if not run:
        callback();return
    assert not output.exists(),'Preserve completed scientific output'
    for prefix in ('board-prefix-followup-recovery-v3','board-prefix-resource-wrapper-v2'):
        rp=OUT/f'{prefix}-registration.json'; path=OUT/f'{prefix}-result.json'
        value=read(path); reg=read(rp)
        assert value['passed'] and value['registration_sha256']==sha(rp)
        for p,h in reg['inputs'].items():assert sha(p)==h,p
    if stage=='admission':
        _,missing=driver.readiness();assert not missing
    else:
        *_,missing=driver.preparation();assert not missing
    name=f'board-full-{stage}-resource-wrapper-v1-{attempt}'
    rp=OUT/f'{name}-registration.json';assert not rp.exists()
    proof_path=OUT/'board-prefix-resource-wrapper-control-v2-result.json';proof=read(proof_path)
    assert proof['passed'] and proof['restoration_cases']==proof['numerical_thread_cases']==2
    for p,h in proof['inputs'].items():assert sha(p)==h,p
    inventory_path=OUT/'global-research-inventory-control-v2-result.json';ip=read(inventory_path)
    assert ip['passed'] and ip['activity_rejections']==3
    for p,h in ip['inputs'].items():assert sha(p)==h,p
    paths=[proof_path,inventory_path,*Path(__file__).parent.glob('*.py')]
    for prefix in ('board-prefix-followup-recovery-v3','board-prefix-resource-wrapper-v2'):
        paths.extend((OUT/f'{prefix}-registration.json',OUT/f'{prefix}-result.json'))
    inputs={str(p):sha(p) for p in paths};began=time.monotonic();scans=[]
    atomic_json(rp,dict(inputs=inputs,stage=stage,resume=resume,attempt=attempt,
        scientific_script=Path(driver.__file__).name,numerical_blas_threads=2,
        dependency_replaced='hu_root_retained_storage_admitted_study_20260924.measure',
        replacement='global_research_inventory_v2.measure',expected_global_scans=1 if stage=='admission' else 2,
        scope='Operational inventory only; fixed design, source bindings, resource and storage gates remain unchanged.',
        production_modified=False))
    def measured():
        rows=measure();scans.append(rows)
        print(json.dumps(dict(inventory_scan=len(scans),allocated_GB=sum(x['allocated_file_bytes'] for x in rows)/1e9)),flush=True)
        return rows
    try:
        with scientific_runtime(measured):callback()
        value=read(output);assert value['passed']
        if stage=='admission':
            assert len(scans)==1 and value['global_inventory']==scans[0]
            assert value['full_study_storage_admitted'] and not value['training_started']
        else:
            reg=read(OUT/f'{driver.PREFIX}-registration.json')
            assert len(scans)==2 and value['final_global_storage']['roots']==scans[1]
            if not resume:assert reg['admission']['roots']==scans[0]
            assert value['training_complete'] and value['generations_per_arm']==78
        for p,h in inputs.items():assert sha(p)==h,p
        atomic_json(OUT/f'{name}-result.json',dict(passed=True,registration_sha256=sha(rp),
            scientific_output=str(output),scientific_output_sha256=sha(output),scans=scans,
            seconds=time.monotonic()-began,dependency_restored=True,production_modified=False))
    except BaseException as error:
        atomic_json(OUT/f'{name}-failure.json',dict(passed=False,registration_sha256=sha(rp),
            error=repr(error),completed_scans=len(scans),seconds=time.monotonic()-began))
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--stage',choices=('admission','training'),required=True)
    parser.add_argument('--run',action='store_true');parser.add_argument('--resume',action='store_true')
    parser.add_argument('--attempt',default='initial');a=parser.parse_args()
    main(a.stage,a.run,a.resume,a.attempt)
