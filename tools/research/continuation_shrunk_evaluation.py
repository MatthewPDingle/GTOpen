"""Separately registered N15 evaluation on the still-future expanded queries."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import datetime as dt
import importlib.util
import msvcrt
from types import SimpleNamespace
import sys
import continuation_bridge_run as bridge
import continuation_shrunk_residual as shrunk

study=bridge.study
OUT=shrunk.OUT
SOURCE=OUT.parent/'expanded-validation-20260916'


def adapter(directory=OUT):
    spec=importlib.util.spec_from_file_location('_shrunk_reference_runner',bridge.__file__)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.OUT=directory
    return module


def prepare():
    assert not list((SOURCE/'prospective/jobs').glob('*.json')),'Source outcomes already exist; use new data'
    assert not list((OUT/'prospective/jobs').glob('*.json'))
    source=adapter(SOURCE).checked('prospective')
    assert study.read(OUT/'training-screen.json')['eligible']
    assert study.pilot.sha(OUT/'candidate.json')==study.read(OUT/'candidate-freeze.json')['sha256']
    paths=[OUT/'candidate.json',OUT/'candidate-freeze.json',OUT/'training-screen.json',OUT/'README.md',
        OUT/'implementation-freeze.json',OUT/'training-runtime.json',
        study.ROOT/'tools/research/continuation_shrunk_run.py',
        study.ROOT/'tools/research/continuation_shrunk_evaluation.py',
        study.ROOT/'tools/research/continuation_shrunk_residual.py',
        study.ROOT/'tools/research/continuation_bridge_run.py',SOURCE/'prospective/manifest.json']
    inputs=dict(source['inputs'])
    training_inputs=study.read(OUT/'implementation-freeze.json')['inputs']
    for path,sha in training_inputs.items():
        assert study.pilot.sha(study.ROOT/path)==sha,'Frozen training input changed: '+path
        inputs[path]=sha
    inputs.update({str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in paths})
    manifest=study.signed(dict(cases=source['cases'],boards=source['boards'],jobs=source['jobs'],partition='prospective',
        inputs=inputs,binary_path=source['binary_path'],binary_sha256=source['binary_sha256'],target_gap_pct=.1,max_iterations=2000,
        source_manifest_id=source['id'],protocol='README.md; registered before source outcomes exist.'))
    study.freeze(OUT/'prospective/manifest.json',manifest)
    study.freeze(OUT/'evaluation-registration.json',dict(registered_at=study.night.now(),manifest_id=manifest['id'],
        candidate_sha256=study.pilot.sha(OUT/'candidate.json'),source_references_at_registration=0,production_enabled=False))
    print('N15 registered before 400 future reference outcomes.',flush=True)


def registered():
    manifest=adapter().checked('prospective');record=study.read(OUT/'evaluation-registration.json')
    assert manifest['id']==record['manifest_id'] and record['source_references_at_registration']==0
    assert study.pilot.sha(OUT/'candidate.json')==record['candidate_sha256']
    return manifest,record


def evaluate():
    manifest,record=registered();source=adapter(SOURCE).checked('prospective')
    assert source['id']==manifest['source_manifest_id']
    paths=[SOURCE/'prospective/jobs'/f"{j['id']}.json" for j in source['jobs']]
    count=sum(p.exists() for p in paths)
    assert count in [0,len(paths)],'Partial source outputs require inspection'
    if count:
        contexts=adapter(SOURCE).contexts('prospective');mode='unchanged_expanded_references'
    else:
        contexts=adapter().contexts('prospective');mode='dedicated_N15_references'
        paths=[OUT/'prospective/jobs'/f"{j['id']}.json" for j in manifest['jobs']]
    stamp=dt.datetime.fromisoformat(record['registered_at']).timestamp()
    assert all(p.stat().st_mtime>=stamp for p in paths),'Reference predates registration'
    study.freeze(OUT/'evaluation-provenance.json',dict(mode=mode,candidate_sha256=record['candidate_sha256'],
        registered_at=record['registered_at'],files={str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in paths}))
    module=adapter();module.study=SimpleNamespace(**study.__dict__)
    module.study.fit=SimpleNamespace(**study.fit.__dict__);old_predict=study.fit.predict
    module.study.fit.predict=lambda c,m:shrunk.network.predict(c,m) if m.get('kind')=='shrunk_nonlinear_residual' else old_predict(c,m)
    module.contexts=lambda partition:contexts
    return module.evaluate()


def require_queue_idle():
    # The frozen shared runner predates N09. Explicitly include its controller
    # and the sequencing parent, even in gaps between their GPU children.
    import continuation_night_queue as queue
    controllers=['continuation_night_queue.py','continuation_prior_evaluation.py run',
        'continuation_prior_gpu.py oracle','continuation_prior_gpu.py benchmark',
        'continuation_depth_evaluation.py run','continuation_final_evaluation.py run',
        'continuation_shrunk_evaluation.py run','continuation_warp_summary.py oracle',
        'continuation_warp_summary.py benchmark','continuation_moment_evaluation.py run']
    import os
    for process in queue.processes():
        if process['ProcessId']==os.getpid():continue
        command=(process['CommandLine'] or '').lower()
        if process['Name'].lower() in ['python.exe','pythonw.exe']:
            assert not any(name in command for name in controllers),'Another research controller owns the GPU queue'


def run():
    require_queue_idle()
    with (OUT/'evaluation.lock').open('a+b') as lock:
        lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        try:
            registered();assert not bridge.other_research(),'Another research GPU process is active'
            source=adapter(SOURCE).checked('prospective')
            count=sum((SOURCE/'prospective/jobs'/f"{j['id']}.json").exists() for j in source['jobs'])
            assert count in [0,len(source['jobs'])],'Partial source outputs require inspection'
            if not count:adapter().run_partition('prospective')
            result=evaluate()
            study.night.dump(OUT/'status.json',dict(stage='complete',accuracy_screen_passed=result['accuracy_screen_passed'],production_enabled=False,updated=study.night.now()))
        finally:
            lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)


if __name__=='__main__':{'prepare':prepare,'run':run,'evaluate':evaluate}[sys.argv[1]]()
