"""CPU checks of storage projection and actual full-capacity NPZ serialization."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

import board_full_storage_admission_v1 as admission


def main():
    from sampled_physical_root_evaluation_v1 import sha
    from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir
    from board_prefix_publication_v1 import atomic_json
    began = time.monotonic()
    current = dict(logical_bytes=2_000_000_000, allocated_file_bytes=1_000_000_000, files=1000)
    generations = [50_000_000, 60_000_000, 70_000_000, 80_000_000]
    models = [1_200_000]
    checkpoints = [20_000]
    projection = admission.projection(current, generations, models, checkpoints)
    assert projection['generations_remaining'] == 152
    assert projection['future_compression_credit_bytes'] == 0
    assert projection['maximum_allocated_bytes'] >= projection['projected_full_allocated_bytes']
    assert projection['maximum_logical_bytes'] >= projection['projected_full_logical_bytes']
    assert projection['projected_full_logical_bytes'] - projection['projected_full_allocated_bytes'] == 1_000_000_000
    mature = admission.projection(current, generations + [240_000_000], models, checkpoints)
    assert mature['maximum_allocated_bytes'] > projection['maximum_allocated_bytes']
    # Retained failed attempts cannot disappear from the admission calculation.
    failed = copy.deepcopy(current)
    failed['logical_bytes'] += 3_000_000_000
    failed['allocated_file_bytes'] += 2_000_000_000
    grown = admission.projection(failed, generations, models, checkpoints)
    assert grown['maximum_allocated_bytes'] - projection['maximum_allocated_bytes'] == 2_000_000_000
    # Existing candidate bytes are already in the global inventory; charge once.
    total = admission.admission_total(740_000_000_000, current['allocated_file_bytes'], projection['maximum_allocated_bytes'])
    assert total == 740_000_000_000 + projection['maximum_allocated_bytes'] - 1_000_000_000 + 12_000_000_000
    assert admission.admission_total(799_000_000_000, 1_000_000_000, 4_000_000_000) > admission.LIMIT
    # Round-trip the production serializer at actual capacity; no poker target
    # validity claim is made about the zero-filled mechanical fixture.
    payloads = []
    with tempfile.TemporaryDirectory(prefix='board-storage-control-') as tmp:
        fixture_root = Path(tmp).resolve()
        assert fixture_root.parent == Path(tempfile.gettempdir()).resolve()
        assert fixture_root.name.startswith('board-storage-control-')
        reservoir = WeightedPhysicalReservoir(admission.CAPACITY, 0, 927, 'storage-control')
        assert reservoir.summary()['allocated_payload_bytes'] == admission.CAPACITY * admission.ROW_BYTES
        for size in (0, 1, admission.CAPACITY):
            reservoir.seen = size
            path = fixture_root / f'fixture-{size}.npz'
            reservoir.save(path)
            length = path.stat().st_size
            assert length <= projection['each_full_reservoir_budget']
            payloads.append(dict(retained=size, serialized_bytes=length))
    rejected = 0
    for invalid in ([], [1, 2, 3], [1, 2, 3, -1], [1, 2, 3, True]):
        try: admission.projection(current, invalid, models, checkpoints)
        except AssertionError: rejected += 1
        else: raise AssertionError('Invalid measurement accepted')
    paths, pending = admission.readiness()
    assert pending, 'This preparation control must precede genuine prefix results'
    assert not admission.ADMISSION.exists()
    env_script = Path(admission.__file__).resolve()
    default = subprocess.run([sys.executable, str(env_script)], capture_output=True, text=True,
                             timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
    assert default.returncode == 0 and not json.loads(default.stdout)['ready']
    attempted = subprocess.run([sys.executable, str(env_script), '--run'], capture_output=True, text=True,
                               timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
    assert attempted.returncode != 0 and 'Complete prefix' in attempted.stderr
    assert not admission.ADMISSION.exists()
    bindings = [Path(__file__).resolve(), env_script,
        admission.ROOT/'tools/research/weighted_physical_reservoir_v1.py',
        admission.ROOT/'tools/research/sampled_physical_reservoir_v1.py']
    report = dict(passed=True, inputs={str(p):sha(p) for p in bindings}, serializer_payloads=payloads,
        invalid_measurements_rejected=rejected, mature_generation_growth_charged=True,
        retained_failures_charged=True, no_double_counted_existing_prefix=True,
        over_budget_rejected=True, missing_prefix_blocks_admission=True,
        sample_projection=projection, seconds=time.monotonic()-began,
        full_study_storage_admitted=False, gpu_used=False,
        scope='Mechanical storage calculations and serializer sizes only; genuine prefix measurements and fresh global inventory remain required.')
    destination = admission.OUT / 'board-full-storage-admission-control-v1-result.json'
    atomic_json(destination, report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('inputs','sample_projection')}), flush=True)


if __name__ == '__main__': main()
