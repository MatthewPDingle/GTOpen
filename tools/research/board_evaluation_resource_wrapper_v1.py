"""Use qualified global inventory for the frozen full-bank control/evaluation.

Default mode is read-only readiness. This changes the operational inventory
dependency only; it does not alter the registered policies, chance stream,
numerical precision, stopping rule or storage/resource limits.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2', CUBLAS_WORKSPACE_CONFIG=':4096:8')
import numpy as np
import argparse
from pathlib import Path
import re
import time
import json
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import sha
from board_prefix_publication_v1 import atomic_json
from board_prefix_resource_wrapper_v2 import scientific_runtime
from global_research_inventory_v2 import measure


def main(stage, run=False, resume=False, attempt='initial'):
    if not re.fullmatch('[a-z0-9][a-z0-9-]{0,39}', attempt):
        raise ValueError('Simple bounded attempt name required')
    if resume and (stage != 'evaluation' or not run or attempt == 'initial'):
        raise ValueError('Resume requires evaluation --run and a distinct named attempt')
    if stage == 'control':
        import board_complete_evaluation_control_v1 as driver
        callback = lambda: driver.main(run=run)
    elif stage == 'evaluation':
        import board_complete_evaluation_study_v1 as driver
        callback = lambda: driver.run(resume=resume, execute=run)
    else:
        raise ValueError('Unknown evaluation stage')
    if not run:
        callback()
        return
    output = OUT / f'{driver.PREFIX}-result.json'
    assert not output.exists(), 'Preserve completed scientific output'
    proof_path = OUT / 'board-prefix-resource-wrapper-control-v2-result.json'
    inventory_path = OUT / 'global-research-inventory-control-v2-result.json'
    proof, inventory_proof = read(proof_path), read(inventory_path)
    assert proof['passed'] and proof['restoration_cases'] == proof['numerical_thread_cases'] == 2
    assert inventory_proof['passed'] and inventory_proof['activity_rejections'] == 3
    for document in (proof, inventory_proof):
        for path, digest in document['inputs'].items():
            assert sha(path) == digest, path
    name = f'board-{stage}-resource-wrapper-v1-{attempt}'
    rp = OUT / f'{name}-registration.json'
    assert not rp.exists(), 'Preserve every operational attempt'
    inputs = {str(p): sha(p) for p in [proof_path, inventory_path, *Path(__file__).parent.glob('*.py')]}
    atomic_json(rp, dict(inputs=inputs, stage=stage, resume=resume, attempt=attempt,
        scientific_script=Path(driver.__file__).name, numerical_blas_threads=2,
        dependency_replaced='hu_root_retained_storage_admitted_study_20260924.measure',
        replacement='global_research_inventory_v2.measure', expected_global_scans=1,
        scope='Operational inventory only; all scientific qualifications and limits remain mandatory.',
        production_modified=False))
    began = time.monotonic()
    scans = []
    def measured():
        rows = measure()
        scans.append(rows)
        print(json.dumps(dict(inventory_scan=len(scans),
            allocated_GB=sum(x['allocated_file_bytes'] for x in rows) / 1e9)), flush=True)
        return rows
    try:
        with scientific_runtime(measured):
            callback()
        result = read(output)
        registration = read(OUT / f'{driver.PREFIX}-registration.json')
        assert result['passed'] and result['complete']
        assert result['registration_sha256'] == sha(OUT / f'{driver.PREFIX}-registration.json')
        assert len(scans) == 1
        if stage == 'control':
            assert registration['global_storage']['roots'] == scans[0]
            assert result['control_only'] and result['deals'] == 64 and result['fresh_test_deals_drawn'] == 0
        else:
            if not resume:
                assert registration['admission']['roots'] == scans[0]
            assert result['deals'] == 65536 and result['test_seed'] == 9281101
            assert result['mode'] == 'study'
        for path, digest in inputs.items():
            assert sha(path) == digest, path
        atomic_json(OUT / f'{name}-result.json', dict(passed=True,
            registration_sha256=sha(rp), scientific_output=str(output),
            scientific_output_sha256=sha(output), scans=scans, seconds=time.monotonic()-began,
            dependency_restored=True, production_modified=False))
    except BaseException as error:
        atomic_json(OUT / f'{name}-failure.json', dict(passed=False,
            registration_sha256=sha(rp), error=repr(error), completed_scans=len(scans),
            seconds=time.monotonic()-began))
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', choices=('control', 'evaluation'), required=True)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--attempt', default='initial')
    args = parser.parse_args()
    main(args.stage, args.run, args.resume, args.attempt)
