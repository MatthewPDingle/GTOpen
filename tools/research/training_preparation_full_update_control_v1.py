"""Queued full-update parity and paired timing; no live-study substitution."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',
                  CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONDONTWRITEBYTECODE='1')
import argparse
import gc
import json
from pathlib import Path
import sys
import time
import traceback
import uuid
import numpy as np
import psutil
import river_matched_training_pilot_v1 as pilot
import eight_worker_full_update_control_v1 as prior
from board_training_pipeline_eight_v2 import update as baseline_reference
from river_training_pipeline_eight_v2 import update as river_reference
from board_training_pipeline_preparation_v1 import update as baseline_candidate
from river_training_pipeline_preparation_v1 import update as river_candidate
from visible_features_vector_gpu_control_v1 import metric_math

ROOT=pilot.ROOT;OUT=pilot.OUT;NAME='training-preparation-full-update-control-v1'
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json')
STATUS=OUT/(NAME+'-status.json');PLAN=OUT/'TRAINING-PREPARATION-FULL-UPDATE-PLAN.md'
STORE=Path('S:/GTOpen-research')/NAME
LIMIT=12_000_000_000;RESERVE=2_000_000_000;SECONDS=5400
CONT='river-matched-continuation-v1'
CONT_REG_SHA='6b4b4dec4d0580d3aed5b3c2a38361eb91a58ab5dee778d929b919408ebbf14a'
CASES=(('baseline-reference','A-baseline',baseline_reference),
       ('baseline-candidate','A-baseline',baseline_candidate),
       ('river-candidate','A-river',river_candidate),
       ('river-reference','A-river',river_reference))


def prerequisites():
    pairs=(('continuation',OUT/(CONT+'-result.json')),
           ('continuation review',OUT/(CONT+'-independent-review-v1.json')),
           ('GPU fit control',OUT/'visible-features-vector-gpu-control-v1-result.json'))
    missing=[label for label,path in pairs if not path.exists()]
    if missing:return missing,[]
    result=pilot.read(pairs[0][1]);review=pilot.read(pairs[1][1]);fit=pilot.read(pairs[2][1])
    cr=OUT/(CONT+'-registration.json');rr=OUT/(CONT+'-review-v1-registration.json')
    fr=OUT/'visible-features-vector-gpu-control-v1-registration.json'
    assert pilot.sha(cr)==CONT_REG_SHA
    assert result['passed'] and result['complete'] and result['registration_sha256']==CONT_REG_SHA
    assert review['passed'] and review['source_result_sha256']==pilot.sha(pairs[0][1])
    assert review['readback_registration_sha256']==pilot.sha(rr)
    assert fit['passed'] and fit['registration_sha256']==pilot.sha(fr) and len(fit['cases'])==8
    assert all(row['exact_saved_network'] and row['exact_numeric_fit_metrics'] for row in fit['cases'])
    pilot.verify(pilot.read(fr)['inputs'])
    return [],[path for _,path in pairs]+[cr,rr,fr]


def specification(require_ready=False):
    qualified=prior.specification()
    proof=pilot.read(prior.RESULT)
    assert proof['passed'] and proof['complete'] and proof['registration_sha256']==pilot.sha(prior.REG)
    # The copies must differ only at the two explicitly qualified imports.
    for kind in ('board','river'):
        original=ROOT/f'tools/research/{kind}_training_pipeline_eight_v2.py'
        candidate=ROOT/f'tools/research/{kind}_training_pipeline_preparation_v1.py'
        text=original.read_text()
        needle='from weighted_training_graph_fit_v2 import fit'
        assert text.count(needle)==1
        text=text.replace(needle,'from weighted_training_graph_fit_vector_v1 import fit')
        if kind=='river':
            needle='from eight_worker_training_pools_v1 import river_pool as pool'
            assert text.count(needle)==1
            text=text.replace(needle,'from river_subset_training_pool_v1 import pool')
        assert candidate.read_text()==text,'Unexpected candidate pipeline edit'
    subset_reg=OUT/'river-preflop-subset-targets-control-v1-registration.json'
    subset_result=OUT/'river-preflop-subset-targets-control-v1-result.json'
    subset=pilot.read(subset_result)
    assert subset['passed'] and subset['registration_sha256']==pilot.sha(subset_reg)
    assert len(subset['cases'])==2 and all(c['all_artifact_bytes_identical'] for c in subset['cases'])
    pilot.verify(pilot.read(subset_reg)['inputs'])
    pending,ready_paths=prerequisites()
    if require_ready:assert not pending,'Pending: '+', '.join(pending)
    paths=[Path(__file__),PLAN,prior.REG,prior.RESULT,subset_reg,subset_result,*ready_paths]
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path and Path(path).is_relative_to(ROOT) and Path(path).suffix=='.py':paths.append(Path(path))
    inputs=dict(qualified['inputs']);inputs.update({str(path):pilot.sha(path) for path in paths})
    pilot.verify(inputs)
    return dict(format=1,inputs=inputs,oracles=qualified['oracles'],pending=pending,
        cases=[dict(case=name,arm=arm,workers=8) for name,arm,_ in CASES],board_workers=4,
        source_boundary=78,output_boundary=79,maximum_seconds=SECONDS,
        maximum_new_bytes=LIMIT,reserve_bytes=RESERVE,global_allocated_cap=pilot.GLOBAL_LIMIT,
        fresh_training_deals=0,new_evaluation_deals=0,production_modified=False,
        timing='One paired replay per method; opposite reference/candidate order for baseline and river.',
        requirements='Each complete checkpoint, restored state, model, subbatch artifacts and numeric fit metrics match the original saved oracle.')


def main(run=False):
    invocation_started=time.monotonic()
    spec=specification(require_ready=run)
    if not run:
        print(json.dumps(dict(source_preflight_passed=True,pending=spec['pending'],
            research_lock_present=pilot.LOCK.exists() or pilot.OTHER.exists(),gpu_started=False)),flush=True)
        return
    assert not any(path.exists() for path in (REG,RESULT,STORE)),'Preserve previous attempts; version recovery explicitly'
    ready,probe=pilot.available();assert ready,'Other research or production has priority'
    acquired=False;resources=None
    try:
        with pilot.LOCK.open('x') as handle:handle.write(str(os.getpid()))
        acquired=True
        inventory=pilot.global_measure();allocated=sum(row['allocated_file_bytes'] for row in inventory)
        assert allocated+LIMIT+RESERVE<=pilot.GLOBAL_LIMIT
        pilot.atomic_json(REG,spec);pilot.create(STORE)
        pilot.atomic_json(STORE/'admission.json',dict(allocated_bytes=allocated,inventory=inventory,
            reserved_bytes=LIMIT+RESERVE,gpu=probe,unix=time.time()))
        pilot.STORE=STORE;pilot.STATUS=STATUS;pilot.LIMIT=LIMIT
        original_reg=pilot.read(prior.PILOT_REG);source=pilot.CONTEXT.read_text()
        matrix=pilot.AllinMatrix(pilot.read(pilot.MATRIX),source)
        args=dict(context_source=source,catalog_source=pilot.CATALOG.read_text(),
            matrix_sha256=pilot.sha(pilot.MATRIX),entry_mass=matrix.btn_mass)
        cache_review=pilot.read(OUT/'complete-private-allin-cache-v2-independent-review.json')
        assert cache_review['passed']
        cache=pilot.AllinCache(cache_review['cache_artifact'],cache_review['cache_sha256'])
        import torch
        assert torch.cuda.is_available()
        for name in ('A-baseline','A-river'):
            cfg=original_reg['arms'][name]['config']
            assert cfg['torch_version']==torch.__version__ and cfg['numpy_version']==np.__version__
        torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        torch.cuda.set_per_process_memory_fraction(pilot.CUDA_BUDGET_BYTES/torch.cuda.get_device_properties(0).total_memory)
        resources=pilot.Guard()
        def guard():
            assert time.monotonic()-invocation_started<SECONDS
            resources()
        records=[]
        for case,name,update in CASES:
            guard();arm=dict(original_reg['arms'][name],name=name);folder=STORE/case;folder.mkdir()
            state,fork=pilot.copy_source(folder,arm,args)
            assert state['completed_iterations']==78
            oracle=pilot.read(spec['oracles'][name]['metrics']);destination=folder/'update-79'
            step=pilot.step_arguments(arm,args,cache,guard);step['workers']=8
            if arm['treatment']=='river':step['river_executable']=pilot.EXES['river_executable']
            pilot.status('full_update_parity',case=case);waited=resources.wait_seconds
            metric=update(destination,folder/'objects',state,arm['config'],**step)
            assert metric['workers']==8 and metric['board_workers']==4
            for sub in metric['subbatches']:
                part=destination/f"batch-{sub['chunk']:02d}"
                for filename,digest in sub['artifacts'].items():
                    guard();assert pilot.sha(part/filename)==digest
            prior.validate(folder,arm,metric,oracle,args,guard)
            assert len(metric['fits'])==len(oracle['fits'])==2
            for actual,expected in zip(metric['fits'],oracle['fits']):assert metric_math(actual)==metric_math(expected)
            restored=pilot.checkpoint.restore_checkpoint(folder/'objects',metric['checkpoint'],arm['config'],**pilot.model_args(args,arm))
            pilot.compare_states(restored,state)
            proof=dict(case=case,arm=name,source_fork=fork,checkpoint=metric['checkpoint'],
                seconds=metric['seconds'],external_gpu_wait_seconds=resources.wait_seconds-waited,
                metrics=str(destination/'metrics.json'),metrics_sha256=pilot.sha(destination/'metrics.json'),
                full_saved_state_identical=True,exact_numeric_fit_metrics=True)
            pilot.atomic_json(folder/'complete.json',dict(registration_sha256=pilot.sha(REG),**proof))
            records.append(proof);print(json.dumps(dict(case=case,passed=True,seconds=metric['seconds'])),flush=True)
            del state,restored,metric;gc.collect()
        comparisons=[]
        for method in ('baseline','river'):
            reference,candidate=[next(row for row in records if row['case']==method+'-'+kind) for kind in ('reference','candidate')]
            comparisons.append(dict(method=method,reference_seconds=reference['seconds'],candidate_seconds=candidate['seconds'],
                observed_ratio=reference['seconds']/candidate['seconds']))
        pilot.verify(spec['inputs']);guard();measurement=pilot.study_measure(STORE)
        assert measurement['logical_bytes']<LIMIT
        pilot.atomic_json(RESULT,dict(passed=True,complete=True,registration_sha256=pilot.sha(REG),
            cases=records,comparisons=comparisons,storage=measurement,gpu_used=True,
            seconds=time.monotonic()-invocation_started,new_evaluation_deals=0,
            learning_bank_modified=False,production_modified=False,accuracy_claim=False,
            limitation='One complete update per method/version from one A-seed boundary; descriptive timing, not universal equivalence or an accuracy test.'))
        pilot.status('complete',result=str(RESULT))
    except BaseException as error:
        failure=OUT/(NAME+'-interruption-'+uuid.uuid4().hex[:8]+'.json')
        pilot.atomic_json(failure,dict(registration_sha256=pilot.sha(REG) if REG.exists() else None,
            error=repr(error),traceback=traceback.format_exc(),preserve_partial_attempts=True))
        raise
    finally:
        if acquired:
            assert pilot.LOCK.read_text()==str(os.getpid());pilot.LOCK.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true')
    main(parser.parse_args().run)
