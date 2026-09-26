"""Exercise the actual resumable retention implementation on newly owned copies."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import time
import uuid
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read
from reboot_research_idle_v1 import idle
from completed_object_retention_v1 import retain
from archived_checkpoint_objects_v1 import ReadOnlyCheckpointObjects

PREFIX = 'completed-object-retention-control-v1'
STORE = Path('S:/GTOpen-research') / PREFIX


def main():
    start = time.monotonic()
    def guard():
        assert idle() and time.monotonic() - start < 300
        if STORE.exists():
            assert sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file()) < 40_000_000
    guard()
    rp, destination = [OUT / f'{PREFIX}-{s}.json' for s in ('registration', 'result')]
    assert not STORE.exists() and not rp.exists() and not destination.exists()
    sp = OUT / 'showdown-training-integration-control-v1-result.json'
    ap = OUT / 'showdown-training-integration-control-v1-independent-review.json'
    source, audit = read(sp), read(ap)
    assert source['passed'] and audit['passed'] and audit['source_result_sha256'] == sha(sp)
    files = sorted((Path(source['store']) / 'objects').iterdir())
    for p in files: assert sha(p) == source['artifacts'][str(p)]
    inputs = {str(p): sha(p) for p in [sp, ap, *files, Path(__file__).resolve(),
        ROOT / 'tools/research/completed_object_retention_v1.py',
        ROOT / 'tools/research/archived_checkpoint_objects_v1.py',
        ROOT / 'tools/research/owned_research_archive_v1.py']}
    save(rp, dict(inputs=inputs, maximum_seconds=300, maximum_output_bytes=40_000_000,
                  store=str(STORE), gpu_used=False, scope='New control copies only'))
    rejected = []
    def reject(label, fn):
        try: fn()
        except ValueError: rejected.append(label)
        else: raise AssertionError('Accepted ' + label)
    try:
        STORE.mkdir(); token = uuid.uuid4().hex
        save(STORE / 'archive-owner.json', dict(format=1, token=token, purpose='new-research-scratch-v1'))
        case = STORE / 'case'; objects = case / 'objects'; objects.mkdir(parents=True)
        for p in files:
            with (objects / p.name).open('xb') as f: f.write(p.read_bytes())
        evidence = dict(control_only=True, source_result_sha256=sha(sp), source_review_sha256=sha(ap))
        kwargs = dict(root=STORE, token=token, guard=guard, eligibility=lambda: evidence)
        reject('missing eligibility', lambda: retain(case, **dict(kwargs, eligibility=lambda: {})))
        assert not (case / 'objects-retention-intent.json').exists()
        reject('wrong owner', lambda: retain(case, **dict(kwargs, token='wrong')))
        class Interrupted(Exception): pass
        def interrupt(path): raise Interrupted('Simulated stop after first duplicate retirement')
        try: retain(case, **kwargs, after_retire=interrupt)
        except Interrupted: pass
        else: raise AssertionError('Interruption hook did not run')
        assert len(list(objects.iterdir())) == len(files) - 1
        assert (case / 'objects.xz.json').exists() and not (case / 'objects-retention.json').exists()
        reject('changed completion evidence', lambda: retain(case, **dict(kwargs, eligibility=lambda: dict(evidence, changed=True))))
        remaining = sorted(objects.iterdir()); conflict = remaining[0]; original = conflict.read_bytes()
        conflict.write_bytes(b'changed-control-copy')
        reject('changed surviving original', lambda: retain(case, **kwargs))
        assert len(list(objects.iterdir())) == len(files) - 1
        conflict.write_bytes(original)
        result = retain(case, **kwargs)
        assert not list(objects.iterdir())
        assert retain(case, **kwargs) == result
        reader = ReadOnlyCheckpointObjects(objects, guard=guard)
        for p in files: assert reader.read(dict(file=p.name, sha256=sha(p))) == p.read_bytes()
        for p, h in inputs.items(): guard(); assert sha(p) == h
        report = dict(passed=True, registration_sha256=sha(rp), **result,
            interruption_recovered=True, idempotent_retirement=True, rejections=rejected,
            original_inputs_unchanged=True, gpu_used=False, live_training_files_modified=False,
            production_modified=False, seconds=time.monotonic()-start,
            artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()},
            scope='Actual retention path on copied corrected-control objects; live-arm eligibility remains a separate gate.')
        save(destination, report); print(json.dumps({k:v for k,v in report.items() if k!='artifacts'}))
    except BaseException as exc:
        save(destination, dict(passed=False, error=repr(exc), registration_sha256=sha(rp)))
        raise


if __name__ == '__main__': main()
