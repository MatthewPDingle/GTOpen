"""CPU native checkpoint round trips using archived, newly copied predecessors."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import io
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
from checkpoint_overlay_store_v1 import overlay
from checkpoint_overlay_control_20260926_v2 import admission_inventory
from completed_object_retention_v1 import retain
from hu_root_retained_storage_admitted_study_20260924 import LIMIT, METADATA_RESERVE
import later_action_checkpoint_v1 as baseline
import showdown_root_checkpoint_v1 as corrected
import sampled_visible_hybrid_checkpoint_v1 as base
from sampled_physical_reservoir_v1 import PhysicalReservoir

PREFIX = 'checkpoint-archived-overlay-control-v1'
STORE = Path('S:/GTOpen-research')/PREFIX
CAP = 120_000_000


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
    previous = OUT/'checkpoint-overlay-control-v2-result.json'; previous_reg = OUT/'checkpoint-overlay-control-v2-registration.json'
    control = read(previous)
    assert control['passed'] and control['registration_sha256'] == sha(previous_reg)
    inputs = dict(read(previous_reg)['inputs'])
    for path, digest in inputs.items(): assert sha(path) == digest, path
    paths = [tr, previous, previous_reg, Path(__file__).resolve(),
             ROOT/'tools/research/checkpoint_overlay_control_20260926_v2.py',
             ROOT/'tools/research/completed_object_retention_v1.py']
    fixtures = []
    for case in control['cases']:
        assert case['generation'] == 8 and case['exact_checkpoint_bytes']
        sources = {}
        for name, digest in case['original_restore']['read_objects'].items():
            source = original/case['arm']/'objects'/name
            if not source.exists():
                source = Path(case['overlay']['directory'])/name
            assert sha(source) == digest; sources[name] = str(source); inputs[str(source)] = digest
        fixtures.append(dict(arm=case['arm'], generation=8, checkpoint=case['checkpoint'], sources=sources))
    inputs.update({str(p):sha(p) for p in paths})
    inventory = admission_inventory(original, guard)
    projected = sum(r['allocated_file_bytes'] for r in inventory)+trial['maximum_output_bytes']+CAP+METADATA_RESERVE
    assert projected <= LIMIT
    save(rp, dict(inputs=inputs, fixtures=fixtures, maximum_seconds=1800, maximum_output_bytes=CAP,
        inventory_excluding_active_training=inventory, reserved_training_bytes=trial['maximum_output_bytes'],
        projected_allocated_bytes=projected, gpu_used=False,
        scope='Owned copies of two generation-8 dependency closures; original training objects cannot be retired.'))
    STORE.mkdir(); source_root = STORE/'predecessors'; writer_root = STORE/'new-writes'
    tokens = {}
    for root in (source_root, writer_root):
        root.mkdir(); tokens[root] = uuid.uuid4().hex
        save(root/'archive-owner.json', dict(format=1, token=tokens[root], purpose='new-research-scratch-v1'))
    args = bank_args((OUT/'bb-context-candidate.json').read_text()); records = []
    read0, publish0, load0 = base.read_object, base.publish, PhysicalReservoir.load.__func__
    try:
        for fixture in fixtures:
            guard(); began = time.monotonic(); label = fixture['arm']
            case = source_root/label; objects = case/'objects'; objects.mkdir(parents=True)
            for name, path in fixture['sources'].items():
                with (objects/name).open('xb') as stream: stream.write(Path(path).read_bytes())
            frozen = dict(control_copy_only=True, source_control_sha256=sha(previous), checkpoint=fixture['checkpoint'],
                          copied_object_hashes={name:inputs[path] for name,path in fixture['sources'].items()})
            def eligible():
                guard(); assert sha(previous) == inputs[str(previous)]
                return frozen
            retained = retain(case, root=source_root, token=tokens[source_root], eligibility=eligible, guard=guard)
            assert not list(objects.iterdir())
            arm = next(a for a in trial['arms'] if a['name'] == label)
            module = baseline if arm['treatment'] == 'baseline' else corrected
            local = writer_root/label/'objects'; local.mkdir(parents=True)
            with overlay(local, objects, root=writer_root, token=tokens[writer_root], guard=guard) as record:
                state = module.restore_checkpoint(local, fixture['checkpoint'], config=arm['config'], **args)
                checked = set()
                for name,path in fixture['sources'].items():
                    if not name.endswith('.npz'): continue
                    with np.load(io.BytesIO(Path(path).read_bytes()), allow_pickle=False) as arrays:
                        meta = json.loads(str(arrays['metadata'])); player = meta['player']; actual = state['reservoirs'][player]
                        assert player not in checked; checked.add(player)
                        assert actual.seen == meta['seen'] and actual.rng.bit_generator.state == meta['rng']
                        for key in ('keys','active','arity','values','iterations'):
                            assert np.array_equal(getattr(actual,key)[:actual.size],arrays[key])
                assert checked == {0,1}
                saved = module.save_checkpoint(local, completed=state['completed_iterations'], config=arm['config'],
                    sampler=state['sampler'], action_rng=state['action_rng'], reservoirs=state['reservoirs'],
                    bank=state['played_bank'], current=state['next_model'], **args)
                assert saved == fixture['checkpoint']
            assert base.read_object is read0 and base.publish is publish0 and PhysicalReservoir.load.__func__ is load0
            assert not list(local.iterdir()) and not record['published_objects']
            assert record['predecessor_retention_sha256'] == retained['receipt_sha256']
            for path,digest in inputs.items(): guard(); assert sha(path) == digest,path
            row = dict(arm=label, generation=8, exact_checkpoint_bytes=True, exact_reservoir_arrays=True,
                no_objects_extracted_or_republished=True, retained=retained, overlay=record, seconds=time.monotonic()-began)
            records.append(row)
            print(json.dumps({k:v for k,v in row.items() if k not in ('retained','overlay')}),flush=True)
            del state
        save(dest, dict(passed=True, registration_sha256=sha(rp), cases=records,
            gpu_used=False, original_inputs_unchanged=True, training_interrupted=False,
            seconds=time.monotonic()-start,
            scope='Two generation-8 native checkpoint round trips with archived predecessor copies. GPU fit replay and continuation controller remain pending.'))
    except BaseException as exc:
        save(dest, dict(passed=False, registration_sha256=sha(rp), error=repr(exc), seconds=time.monotonic()-start))
        raise


if __name__ == '__main__':
    main()
