"""CPU-only recovery of generation 16 using archived generation-8 predecessors.

Copies only newer immutable objects and the compact reservoir archive. No fit,
new deals, original-file mutation, or training launch.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import copy
import json
from pathlib import Path
import shutil
import time
import uuid
import numpy as np
import psutil
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read
from hu_action_integrated_exact_20260925 import bank_args
from reboot_research_idle_v1 import idle
from checkpoint_overlay_control_20260926_v2 import admission_inventory
from hu_root_retained_storage_admitted_study_20260924 import LIMIT, METADATA_RESERVE
from compact_checkpoint_restore_v2 import restore as original_restore
from compact_checkpoint_restore_v3 import restore
from archived_checkpoint_objects_v1 import ReadOnlyCheckpointObjects
import sampled_visible_hybrid_checkpoint_v1 as base
from sampled_physical_reservoir_v1 import PhysicalReservoir

PREFIX = 'compact-mixed-restore-control-v1'
STORE = Path('S:/GTOpen-research')/PREFIX
CAP = 100_000_000
CASES = ['9266201-baseline', '9266201-corrected']


def equal_states(a, b):
    for key in ('completed_iterations', 'played_bank', 'next_model'):
        assert a[key] == b[key], key
    assert a['sampler'].checkpoint() == b['sampler'].checkpoint()
    assert a['action_rng'].bit_generator.state == b['action_rng'].bit_generator.state
    for key in ('root_regret_state', 'exact_btn_state'):
        assert a[key].document() == b[key].document(), key
    for x, y in zip(a['reservoirs'], b['reservoirs']):
        assert x.summary() == y.summary() and x.rng.bit_generator.state == y.rng.bit_generator.state
        for key in ('keys', 'active', 'arity', 'values', 'iterations'):
            assert np.array_equal(getattr(x, key)[:x.size], getattr(y, key)[:y.size]), key


def main():
    start = time.monotonic(); last = last_size = 0.
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    def guard():
        nonlocal last, last_size
        now = time.monotonic(); assert now-start < 1800
        if now-last >= 2:
            assert idle() and psutil.virtual_memory().available >= 20_000_000_000
            assert shutil.disk_usage('S:/').free >= 40_000_000_000
            last = now
        if now-last_size >= 5:
            assert sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file()) <= CAP
            last_size = now
    guard()
    rp, dest = [OUT/f'{PREFIX}-{s}.json' for s in ('registration', 'result')]
    assert not STORE.exists() and not rp.exists() and not dest.exists()
    tr = OUT/'showdown-matched-training-v1-registration.json'; trial = read(tr)
    assert sha(tr) == '73305540181f7be96b5f5d68365408d89643c51d628966d2cb920aa423686eec'
    original = Path(trial['store']).resolve()
    predecessor_result = OUT/'checkpoint-archived-overlay-control-v1-result.json'
    predecessor_reg = OUT/'checkpoint-archived-overlay-control-v1-registration.json'
    existing = read(predecessor_result)
    assert existing['passed'] and existing['registration_sha256'] == sha(predecessor_reg)
    inputs = dict(trial['inputs'])
    paths = [tr, predecessor_result, predecessor_reg, Path(__file__).resolve(),
             ROOT/'tools/research/compact_checkpoint_restore_v2.py',
             ROOT/'tools/research/compact_checkpoint_restore_v3.py',
             ROOT/'tools/research/checkpoint_overlay_control_20260926_v2.py',
             ROOT/'tools/research/archived_checkpoint_objects_v1.py']
    for label in CASES:
        case = original/label
        paths.extend([case/'result.json', case/'checkpoint-0016.json', case/'retention-0016.json',
                      case/'iteration-0016/metrics.json', case/'checkpoint-reservoirs-0016.xz',
                      case/'checkpoint-reservoirs-0016.xz.json'])
        old = next(c for c in existing['cases'] if c['arm'] == label)
        parent = Path(old['overlay']['predecessor']).parent
        paths.extend([parent/'objects-retention.json', parent/'objects.xz', parent/'objects.xz.json'])
    inputs.update({str(p):sha(p) for p in paths})
    for path, digest in inputs.items(): guard(); assert sha(path) == digest, path
    inventory = admission_inventory(original, guard)
    projected = sum(r['allocated_file_bytes'] for r in inventory)+trial['maximum_output_bytes']+CAP+METADATA_RESERVE
    assert projected <= LIMIT, 'Admission failed; no storage limit increase'
    save(rp, dict(inputs=inputs, cases=CASES, generation=16, predecessor_generation=8,
        maximum_output_bytes=CAP, maximum_seconds=1800, projected_allocated_bytes=projected,
        reserved_training_bytes=trial['maximum_output_bytes'], inventory_excluding_active_training=inventory,
        gpu_used=False, scope='Exact existing generation-16 state reconstructed from mixed local objects and archived generation-8 history.'))
    STORE.mkdir()
    save(STORE/'archive-owner.json', dict(format=1, token=uuid.uuid4().hex, purpose='new-research-scratch-v1'))
    args = bank_args((OUT/'bb-context-candidate.json').read_text()); records = []
    read0, load0 = base.read_object, PhysicalReservoir.load.__func__
    try:
        for label in CASES:
            guard(); began = time.monotonic(); source = original/label
            arm = next(a for a in trial['arms'] if a['name'] == label)
            kwargs = dict(treatment=arm['treatment'], config=arm['config'], bank_args=args, guard=guard)
            expected, source_identity = original_restore(source, 16, **kwargs)
            old = next(c for c in existing['cases'] if c['arm'] == label)
            predecessor = dict(directory=old['overlay']['predecessor'], retention_sha256=old['retained']['receipt_sha256'])
            reader = ReadOnlyCheckpointObjects(Path(predecessor['directory']), guard=guard)
            assert reader.retention_sha256 == predecessor['retention_sha256'] and reader.members is not None
            case = STORE/label; objects = case/'objects'; objects.mkdir(parents=True)
            copied = {}
            for name, digest in source_identity['read_objects'].items():
                if name.endswith('.npz') or name in reader.members:
                    continue
                path = source/'objects'/name
                assert sha(path) == digest
                with (objects/name).open('xb') as stream: stream.write(path.read_bytes())
                copied[name] = digest
            del reader
            (case/'iteration-0016').mkdir()
            for name in ('retention-0016.json', 'iteration-0016/metrics.json',
                         'checkpoint-reservoirs-0016.xz', 'checkpoint-reservoirs-0016.xz.json'):
                shutil.copyfile(source/name, case/name)
            snapshot = copy.deepcopy(read(source/'checkpoint-0016.json'))
            snapshot['reservoir_archive']['path'] = str(case/'checkpoint-reservoirs-0016.xz')
            save(case/'checkpoint-0016.json', snapshot)
            actual, identity = restore(case, 16, predecessor=predecessor, **kwargs)
            equal_states(expected, actual)
            assert {'local', 'predecessor', 'reservoir_archive'} == set(identity['object_locations'].values())
            assert all(not (objects/name).exists() for name, where in identity['object_locations'].items() if where != 'local')
            del actual
            for invalid in (None, dict(predecessor, retention_sha256='0'*64)):
                try:
                    restore(case, 16, predecessor=invalid, **kwargs)
                except (ValueError, FileNotFoundError):
                    pass
                else:
                    raise AssertionError('Missing or unauthenticated predecessor accepted')
                assert base.read_object is read0 and PhysicalReservoir.load.__func__ is load0
            # Damage only a new local fixture object, require refusal, then restore it.
            probe = objects/identity['checkpoint']['file']; raw = probe.read_bytes()
            try:
                probe.write_bytes(raw+b' ')
                try:
                    restore(case, 16, predecessor=predecessor, **kwargs)
                except (ValueError, AssertionError):
                    pass
                else:
                    raise AssertionError('Damaged local checkpoint accepted')
            finally:
                probe.write_bytes(raw)
            assert base.read_object is read0 and PhysicalReservoir.load.__func__ is load0
            row = dict(arm=label, generation=16, original_restore=source_identity, mixed_restore=identity,
                copied_newer_objects=copied, exact_complete_state=True, rejected_missing_predecessor=True,
                rejected_changed_predecessor_identity=True, rejected_damaged_local_checkpoint=True,
                logical_bytes=sum(p.stat().st_size for p in case.rglob('*') if p.is_file()),
                seconds=time.monotonic()-began)
            records.append(row)
            print(json.dumps(dict(arm=label, passed=True, seconds=row['seconds'], bytes=row['logical_bytes'])), flush=True)
            del expected
        for path, digest in inputs.items(): guard(); assert sha(path) == digest, path
        save(dest, dict(passed=True, registration_sha256=sha(rp), cases=records,
            original_inputs_unchanged=True, gpu_used=False, seconds=time.monotonic()-start,
            scope='Mixed archived/local checkpoint restoration only; no resumed fit, controller or poker accuracy claim.'))
    except BaseException as exc:
        save(dest, dict(passed=False, error=repr(exc), registration_sha256=sha(rp),
            cases=records, seconds=time.monotonic()-start))
        raise


if __name__ == '__main__':
    main()
