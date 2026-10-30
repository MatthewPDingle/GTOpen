"""CPU checkpoint round trip through an owned overlay; no fit or GPU work."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import shutil
import time
import uuid
import numpy as np
import psutil
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read
from reboot_research_idle_v1 import idle
from hu_action_integrated_exact_20260925 import bank_args
from compact_checkpoint_restore_v2 import restore
from checkpoint_overlay_store_v1 import overlay
from hu_root_retained_storage_admitted_study_20260924 import ROOTS, LIMIT, METADATA_RESERVE, stable_file, inventory_error
from ntfs_research_storage_v1 import allocated_bytes
import sampled_visible_hybrid_checkpoint_v1 as base
from sampled_physical_reservoir_v1 import PhysicalReservoir
import later_action_cadence_training_v1 as baseline
import showdown_cadence_training_v1 as corrected

PREFIX = 'checkpoint-overlay-control-v2'
STORE = Path('S:/GTOpen-research')/PREFIX
CAP = 160_000_000


def admission_inventory(training_store, guard):
    """Reserve the original full cap instead of racing its transient raw files."""
    rows = []; skipped = 0
    for root in ROOTS:
        count = logical = allocated = 0
        assert root.is_dir() and not root.lstat().st_file_attributes & 0x400
        for folder, dirs, files in os.walk(root, followlinks=False, onerror=inventory_error):
            guard()
            for name in list(dirs):
                path = Path(folder)/name
                assert not path.lstat().st_file_attributes & 0x400
                if path.resolve() == training_store:
                    dirs.remove(name); skipped += 1
            for name in files:
                path = Path(folder)/name
                try:
                    stable_file(path)
                    logical += path.stat().st_size; allocated += allocated_bytes(path); count += 1
                except FileNotFoundError:
                    assert path.suffix == '.tmp' or path.name.startswith('.partial-')
        rows.append(dict(root=str(root), files=count, logical_bytes=logical, allocated_file_bytes=allocated))
    assert skipped == 1
    return rows


def main():
    start = time.monotonic(); last = last_size = 0.
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    def guard():
        nonlocal last, last_size
        now = time.monotonic(); assert now-start < 1800
        if now-last > 2:
            assert idle() and psutil.virtual_memory().available >= 20_000_000_000
            assert shutil.disk_usage('S:/').free >= 40_000_000_000
            last = now
        if now-last_size > 5:
            assert sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file()) <= CAP
            last_size = now
    guard(); rp, dest = [OUT/f'{PREFIX}-{s}.json' for s in ('registration', 'result')]
    assert not STORE.exists() and not rp.exists() and not dest.exists()
    tr = OUT/'showdown-matched-training-v1-registration.json'; trial = read(tr)
    assert sha(tr) == '73305540181f7be96b5f5d68365408d89643c51d628966d2cb920aa423686eec'
    original = Path(trial['store']).resolve()
    assert original == Path('S:/GTOpen-research/showdown-matched-training-v1').resolve()
    assert trial['maximum_output_bytes'] == 4_250_000_000
    inputs = dict(trial['inputs'])
    for p, h in inputs.items(): assert sha(p) == h, p
    paths = [tr, Path(__file__).resolve(), ROOT/'tools/research/checkpoint_overlay_store_v1.py',
             ROOT/'tools/research/compact_checkpoint_restore_v2.py', ROOT/'tools/research/archived_checkpoint_objects_v1.py',
             OUT/'compact-checkpoint-restore-control-v1-result.json', original/'archive-owner.json']
    assert read(paths[-2])['passed']
    cases = [('9266201-baseline', 8), ('9266201-corrected', 8)]
    for label, n in cases:
        paths.extend([original/label/f'checkpoint-{n:04d}.json', original/label/f'retention-{n:04d}.json'])
    inputs.update({str(p):sha(p) for p in paths})
    inventory = admission_inventory(original, guard)
    projected = sum(r['allocated_file_bytes'] for r in inventory)+trial['maximum_output_bytes']+CAP+METADATA_RESERVE
    assert projected <= LIMIT, 'Admission failed; no cap increase'
    save(rp, dict(inputs=inputs, cases=cases, inventory_excluding_active_training=inventory,
        excluded_training_store=str(original), reserved_training_bytes=trial['maximum_output_bytes'],
        projected_allocated_bytes=projected, maximum_output_bytes=CAP, maximum_seconds=1800,
        gpu_used=False, scope='Native checkpoint publication and restore across raw read-only predecessor objects. No training or evaluation.'))
    STORE.mkdir(); token = uuid.uuid4().hex
    save(STORE/'archive-owner.json', dict(format=1, token=token, purpose='new-research-scratch-v1'))
    args = bank_args((OUT/'bb-context-candidate.json').read_text()); records = []
    read0, publish0, load0 = base.read_object, base.publish, PhysicalReservoir.load.__func__
    try:
        for label, n in cases:
            guard(); began = time.monotonic(); source = original/label
            arm = next(a for a in trial['arms'] if a['name'] == label); cfg = arm['config']
            state, identity = restore(source, n, treatment=arm['treatment'], config=cfg, bank_args=args, guard=guard)
            objects = STORE/label/'objects'; objects.mkdir(parents=True)
            module = baseline if arm['treatment'] == 'baseline' else corrected
            expected = read(source/f'checkpoint-{n:04d}.json')['checkpoint']
            with overlay(objects, source/'objects', root=STORE, token=token, guard=guard) as reused:
                saved = module.save_state(objects, state, cfg, **args)
                assert saved == expected, 'Native checkpoint bytes changed'
                restored = module.checkpoint.restore_checkpoint(objects, saved, config=cfg, **args)
                for key in ('next_model', 'played_bank'):
                    assert restored[key] == state[key]
                assert restored['sampler'].checkpoint() == state['sampler'].checkpoint()
                assert restored['action_rng'].bit_generator.state == state['action_rng'].bit_generator.state
                assert restored['root_regret_state'].document() == state['root_regret_state'].document()
                assert restored['exact_btn_state'].document() == state['exact_btn_state'].document()
                for a, b in zip(state['reservoirs'], restored['reservoirs']):
                    assert a.summary() == b.summary() and a.rng.bit_generator.state == b.rng.bit_generator.state
                    for key in ('keys', 'active', 'arity', 'values', 'iterations'):
                        assert np.array_equal(getattr(a,key)[:a.size], getattr(b,key)[:b.size])
                for ref in state['played_bank']:
                    assert ref['file'] in reused['reused_objects'] and not (objects/ref['file']).exists()
            assert base.read_object is read0 and base.publish is publish0 and PhysicalReservoir.load.__func__ is load0
            # Throw inside a second scope to verify restoration on failure too.
            try:
                with overlay(objects, source/'objects', root=STORE, token=token, guard=guard):
                    base.publish(source/'objects', 'probe', b'forbidden')
            except ValueError:
                pass
            else:
                raise AssertionError('Predecessor write accepted')
            assert base.read_object is read0 and base.publish is publish0 and PhysicalReservoir.load.__func__ is load0
            row = dict(arm=label, generation=n, original_restore=identity, checkpoint=saved,
                exact_checkpoint_bytes=True, exact_arrays_and_random_states=True,
                overlay=reused, logical_bytes=sum(p.stat().st_size for p in objects.iterdir() if p.is_file()),
                seconds=time.monotonic()-began)
            records.append(row)
            print(json.dumps({k:v for k,v in row.items() if k not in ('original_restore','checkpoint','overlay')}), flush=True)
            del state, restored
        for path, digest in inputs.items(): guard(); assert sha(path) == digest, path
        save(dest, dict(passed=True, registration_sha256=sha(rp), cases=records,
            gpu_used=False, original_files_modified=False, previous_models_copied=0,
            adapters_restored_after_failure=True, seconds=time.monotonic()-start,
            scope='Two generation-8 native checkpoint round trips with raw predecessors; fit replay, archived-predecessor overlay control and continuation controller remain unqualified.'))
    except BaseException as exc:
        save(dest, dict(passed=False, registration_sha256=sha(rp), error=repr(exc), seconds=time.monotonic()-start))
        raise


if __name__ == '__main__':
    main()
