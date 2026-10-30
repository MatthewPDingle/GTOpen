"""Measured, conservative storage admission for the fixed two-arm board study.

Default execution only reports readiness. --run inventories completed evidence,
then publishes an admission only if the complete remaining budget fits. No GPU,
training, deletion, compression change, or experiment selection occurs here.
"""
import argparse
import json
import math
from pathlib import Path
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
STORE = Path('S:/GTOpen-research/board-root-matched-prefix-v1')
ADMISSION = OUT / 'board-matched-full-storage-admission-v1.json'
PREFIX = 'board-root-matched-prefix-v1'
AUDIT = 'board-matched-prefix-readback-v1'
LIMIT = 800_000_000_000
FOLLOWUP = 8_000_000_000  # Full readback, numerical control and final evaluation.
THROUGHPUT = 2_000_000_000  # Separately prepared optional timing experiment.
HEADROOM = 2_000_000_000
SCRATCH = 2_000_000_000  # Native temporary trees and an unpublished generation.
CAPACITY = 262144
ROW_BYTES = 137  # 2*u64 keys, 36*u16 features, u8 arity, 4*f64 values, u64 iteration, f64 weight.


def positive(value):
    assert type(value) is int and value > 0
    return value


def projection(current, generation_sizes, model_sizes, checkpoint_sizes):
    """Use logical sizes for all future writes; take no compression credit."""
    for key in ('logical_bytes', 'allocated_file_bytes', 'files'):
        positive(current[key])
    assert len(generation_sizes) >= 4 and model_sizes and checkpoint_sizes
    for value in [*generation_sizes, *model_sizes, *checkpoint_sizes]:
        positive(value)
    remaining = 2 * (78 - 2)
    # Early candidate plus every mature historical generation inform the maximum.
    # Archive and JSON growth are estimates, backed by enforced runtime caps.
    archive = math.ceil(max(generation_sizes) * 1.5)
    model = 2 * max(model_sizes) + 65536
    checkpoint = 2 * max(checkpoint_sizes) + 65536
    # np.savez is uncompressed. Charge full buffers from the very next update;
    # source metadata and NPY/ZIP headers get 64 KiB per serialized reservoir.
    reservoir = CAPACITY * ROW_BYTES + 65536
    future = remaining * (archive + model + checkpoint + 2 * reservoir)
    projected_logical = max(current['logical_bytes'], current['allocated_file_bytes']) + future
    # Existing compressed bytes stay measured; every future byte is uncompressed.
    projected_allocated = current['allocated_file_bytes'] + future
    margin = max(SCRATCH, math.ceil(future * 0.10))
    maximum_allocated = max(4_000_000_000, projected_allocated + margin)
    maximum_logical = max(maximum_allocated, projected_logical + margin)
    return dict(generations_remaining=remaining, capacity=CAPACITY, row_payload_bytes=ROW_BYTES,
        generation_archive_budget=archive, model_budget=model, checkpoint_json_budget=checkpoint,
        each_full_reservoir_budget=reservoir, future_retained_bytes=future, scratch_and_growth_margin=margin,
        projected_full_allocated_bytes=projected_allocated, projected_full_logical_bytes=projected_logical,
        maximum_allocated_bytes=maximum_allocated, maximum_logical_bytes=maximum_logical,
        reserved_followup_bytes=FOLLOWUP, separate_throughput_reservation=THROUGHPUT,
        future_compression_credit_bytes=0,
        caveat='Archive and JSON growth remain estimates. Full reservoirs are charged at every generation; runtime limits remain mandatory.')


def admission_total(global_allocated, current_allocated, maximum_allocated):
    for value in (global_allocated, current_allocated, maximum_allocated): positive(value)
    assert global_allocated >= current_allocated and maximum_allocated >= current_allocated
    return global_allocated + maximum_allocated - current_allocated + FOLLOWUP + THROUGHPUT + HEADROOM


def readiness():
    names = [f'{p}-{s}.json' for p in (PREFIX, AUDIT, 'board-prefix-followup-queue-v1')
             for s in ('registration', 'result')]
    return [OUT / n for n in names], [n for n in names if not (OUT / n).exists()]


def main(run=False):
    paths, missing = readiness()
    if not run:
        print(json.dumps(dict(ready=not missing, pending=missing, admission_created=False,
            actual_prefix_measurements_required=True, future_compression_credit_bytes=0)))
        return
    assert not missing, 'Complete prefix, independent readback and terminal follow-up queue required'
    assert not ADMISSION.exists(), 'Preserve the existing admission'
    import psutil
    from sampled_physical_root_evaluation_v1 import sha
    from later_average_support_v1 import read
    from board_prefix_publication_v1 import atomic_json
    from board_study_storage_v1 import measure
    from hu_root_retained_storage_admitted_study_20260924 import measure as global_measure
    from weighted_learning_cuda_control_20260927 import LOCK, OTHER, safe_read_only_resources
    from weighted_complete_evaluation_support_v1 import complete_training_paths
    from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir
    import board_matched_prefix_v2 as prefix

    began = time.monotonic()
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    assert not LOCK.exists() and not OTHER.exists() and safe_read_only_resources()
    assert psutil.cpu_percent(interval=1) < 50 and psutil.virtual_memory().available > 28_000_000_000

    def guard():
        assert time.monotonic() - began < 1200
        assert not LOCK.exists() and not OTHER.exists() and safe_read_only_resources()

    records = []
    for registration, result in zip(paths[::2], paths[1::2]):
        reg, done = read(registration), read(result)
        assert done['passed'] and done['registration_sha256'] == sha(registration)
        for p, h in reg['inputs'].items(): assert sha(p) == h, p
        records.append((reg, done))
    original, done = records[0]
    audit = records[1][1]
    arms, source_paths, _, _ = prefix.specification()
    assert original['runner_version'] == done['runner_version'] == 2
    assert original['arms'] == arms and original['store'] == str(STORE)
    assert original['generations'] == 78 and original['prefix_generations'] == 2
    assert done['prefix_generations_per_arm'] == 2
    assert audit['mode'] == 'prefix' and audit['source_result_sha256'] == sha(paths[1])
    assert [a['arm'] for a in done['arms']] == [a['name'] for a in arms] == [a['arm'] for a in audit['arms']]
    paths.extend(source_paths)
    paths.extend(complete_training_paths())
    measurements = []
    evidence = {}
    generation_sizes, model_sizes, checkpoint_sizes = [], [], []

    def add_file(path, expected=None):
        path = Path(path)
        digest = sha(path)
        if expected is not None: assert digest == expected, path
        evidence[str(path)] = digest
        return read(path)

    def add_generation(path, expected=None):
        value = add_file(path, expected)
        measured = measure(Path(path).parent, guard=guard)
        # A full extra NTFS allocation cluster per file avoids assuming that
        # small future files allocate exactly their logical lengths.
        generation_sizes.append(measured['logical_bytes'] + 4096 * measured['files'])
        measurements.append(dict(path=str(Path(path).parent), **measured))
        return value

    # The genuine candidate measurements include board outputs and restart files.
    for arm, end, checked in zip(arms, done['arms'], audit['arms']):
        folder = STORE / arm['name']
        pp = Path(end['progress_path'])
        assert pp == folder / 'progress.json'
        progress = add_file(pp, end['progress_sha256'])
        assert progress['completed'] == len(progress['generations']) == checked['generations'] == 2
        assert checked['boards_checked'] == 8 and checked['physical_roots_checked'] == 1024
        assert checked['final_checkpoint'] == progress['checkpoint']
        for row in progress['generations']:
            assert Path(row['path']).parent.parent == folder
            metric = add_generation(row['path'], row['sha256'])
            assert all(r['capacity'] == CAPACITY and r['allocated_payload_bytes'] == CAPACITY * ROW_BYTES
                       for r in metric['reservoirs'])
        for path in (folder / 'objects').glob('*.json'):
            if path.name.startswith('boardrootmodel-'):
                add_file(path, path.stem.split('-')[-1]); model_sizes.append(path.stat().st_size)
            elif path.name.startswith('boardrootcheckpoint-'):
                add_file(path, path.stem.split('-')[-1]); checkpoint_sizes.append(path.stat().st_size)
        paths.extend((Path(end['replay_path']),))

    # Include all mature physical generation sizes from both preselected controls;
    # only byte counts are inspected, never policy gains or favored checkpoints.
    historical_reg = read(OUT / 'weighted-stratified-study-v1-registration.json')
    historical_result = read(OUT / 'weighted-stratified-study-v1-training-result.json')
    for arm in arms:
        old_folder = Path(historical_reg['store']) / arm['control']
        old_audit = read(OUT / f'weighted-training-readback-parallel-v1-w4-{arm["control"]}-0078-registration.json')
        assert old_audit['arm'] == arm['control'] and old_audit['completed'] == 78
        rows = []
        for folder in old_audit['folders']:
            path = Path(folder) / 'metrics.json'
            assert path.parent.parent == old_folder
            metric = add_file(path, old_audit['inputs'][str(path)])
            rows.append((metric['iteration'], path))
        assert sorted(g for g, _ in rows) == list(range(1, 79)), 'Ambiguous or incomplete historical generations'
        endpoint = historical_result['arms'][arm['control']]
        assert evidence[endpoint['metrics_path']] == endpoint['metrics_sha256']
        for _, path in sorted(rows): add_generation(path, evidence[str(path)])
        for path in (old_folder / 'objects').glob('*.json'):
            if path.name.startswith('weightedmodel-'):
                add_file(path, path.stem.split('-')[-1]); model_sizes.append(path.stat().st_size)
            elif path.name.startswith('weightedcheckpoint-'):
                add_file(path, path.stem.split('-')[-1]); checkpoint_sizes.append(path.stat().st_size)
    # Confirm the serializer's actual array geometry without allocating a full buffer.
    assert WeightedPhysicalReservoir(1, 0, 0, 'storage-geometry').summary()['allocated_payload_bytes'] == ROW_BYTES
    current = measure(STORE, guard=guard)  # Includes replay, failed and unpublished attempts.
    calculation = projection(current, generation_sizes, model_sizes, checkpoint_sizes)
    guard()
    inventory = global_measure()
    total = sum(row['allocated_file_bytes'] for row in inventory)
    projected_total = admission_total(total, current['allocated_file_bytes'], calculation['maximum_allocated_bytes'])
    disk_required = 40_000_000_000 + calculation['maximum_allocated_bytes'] - current['allocated_file_bytes'] + FOLLOWUP + THROUGHPUT
    free = psutil.disk_usage('S:/').free
    fits = projected_total <= LIMIT and free > disk_required
    paths.extend(Path(__file__).parent / n for n in (
        'board_full_storage_admission_v1.py', 'weighted_physical_reservoir_v1.py',
        'sampled_physical_reservoir_v1.py', 'board_training_checkpoint_v1.py',
        'board_matched_continuation_v1.py', 'board_study_storage_v1.py'))
    inputs = {str(p): sha(p) for p in paths}
    inputs.update(evidence)
    report = dict(format=1, passed=fits, full_study_storage_admitted=fits, store=str(STORE),
        arms=2, generations_per_arm=78, prefix_result_sha256=sha(paths[1]), prefix_audit_sha256=sha(paths[3]),
        scope='Measured full-budget prefix projection; fixed 78-generation study',
        inputs=inputs, measurement_evidence=evidence, current_measurement=current,
        generation_measurements=measurements, global_inventory=inventory,
        global_allocated_bytes=total, projected_global_allocated_bytes=projected_total,
        ceiling_bytes=LIMIT, s_free_bytes=free, s_required_free_bytes=disk_required,
        **calculation, seconds=time.monotonic()-began, training_started=False, production_modified=False)
    for p, h in inputs.items(): assert sha(p) == h, p
    guard()
    destination = ADMISSION if fits else OUT / ('board-matched-storage-rejected-' + uuid.uuid4().hex[:8] + '.json')
    atomic_json(destination, report)
    print(json.dumps(dict(path=str(destination), admitted=fits, projected_global_bytes=projected_total,
        headroom_bytes=LIMIT-projected_total, maximum_study_bytes=calculation['maximum_allocated_bytes'])))
    assert fits, 'Measured complete-study projection exceeds the disk budget; no admission published'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', action='store_true')
    main(parser.parse_args().run)
