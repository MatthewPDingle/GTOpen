"""Run the frozen scientific prefix with qualified closed-port-aware inventory.

The single process-local dependency replacement is explicit and recorded.
No source file, numerical function, source binding, seed, limit or result of
the original prefix is edited. The old dependency is restored on exit.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2', CUBLAS_WORKSPACE_CONFIG=':4096:8')
import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import time
import hu_root_retained_storage_admitted_study_20260924 as legacy
from global_research_inventory_v2 import measure
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import sha
from board_prefix_publication_v1 import atomic_json

NAME = 'board-prefix-resource-wrapper-v1'
PREFIX = 'board-root-matched-prefix-v1'


@contextmanager
def inventory_override(measurement):
    original = legacy.measure
    assert original.__module__ == legacy.__name__ and original.__name__ == 'measure'
    legacy.measure = measurement
    try: yield
    finally:
        assert legacy.measure is measurement, 'Unexpected concurrent dependency change'
        legacy.measure = original


def main(run=False):
    import board_matched_prefix_v2 as scientific
    if not run:
        scientific.main(run=False)
        return
    proof_path = OUT/'board-prefix-resource-wrapper-control-v1-result.json'
    proof = read(proof_path)
    assert proof['passed'] and proof['restoration_cases'] == 2
    inventory_path = OUT/'global-research-inventory-control-v2-result.json'
    inventory_proof = read(inventory_path)
    assert inventory_proof['passed'] and inventory_proof['activity_rejections'] == 3
    for document in (proof, inventory_proof):
        for path,digest in document['inputs'].items(): assert sha(path) == digest,path
    _, pending = scientific.qualifications()
    assert not pending
    rp = OUT/f'{NAME}-registration.json'; result_path = OUT/f'{PREFIX}-result.json'
    assert not rp.exists() and not result_path.exists()
    assert not (OUT/f'{PREFIX}-registration.json').exists() and not scientific.STORE.exists()
    paths = [proof_path, inventory_path, *Path(__file__).parent.glob('*.py')]
    inputs = {str(p):sha(p) for p in paths}
    atomic_json(rp, dict(inputs=inputs, scientific_script='board_matched_prefix_v2.py',
        dependency_replaced='hu_root_retained_storage_admitted_study_20260924.measure',
        replacement='global_research_inventory_v2.measure', maximum_seconds=14520,
        scope='Read-only resource inventory replacement only; all scientific limits and algorithms unchanged.',
        production_modified=False))
    began = time.monotonic(); scans = []
    def measured():
        assert time.monotonic()-began < 14520
        rows = measure(); scans.append(rows)
        print(json.dumps(dict(inventory_scan=len(scans), allocated_GB=sum(x['allocated_file_bytes'] for x in rows)/1e9)),flush=True)
        return rows
    try:
        with inventory_override(measured): scientific.main(run=True)
        assert len(scans) == 2
        original_reg = read(OUT/f'{PREFIX}-registration.json'); result = read(result_path)
        assert result['passed'] and result['registration_sha256'] == sha(OUT/f'{PREFIX}-registration.json')
        assert original_reg['admission']['roots'] == scans[0]
        assert result['final_global_storage']['roots'] == scans[1]
        assert result['prefix_generations_per_arm'] == 2 and result['runner_version'] == 2
        for path,digest in inputs.items(): assert sha(path) == digest,path
        atomic_json(OUT/f'{NAME}-result.json',dict(passed=True, registration_sha256=sha(rp),
            prefix_result=str(result_path), prefix_result_sha256=sha(result_path), scans=scans,
            seconds=time.monotonic()-began, dependency_restored=True, production_modified=False))
    except BaseException as error:
        atomic_json(OUT/f'{NAME}-failure.json',dict(passed=False, registration_sha256=sha(rp),
            error=repr(error), completed_scans=len(scans), seconds=time.monotonic()-began))
        raise


if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--run',action='store_true')
    main(parser.parse_args().run)
