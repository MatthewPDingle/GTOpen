"""Evaluate N09 on a registered future reference set without rerunning N03 data."""
import datetime as dt
import importlib.util
import msvcrt
from types import SimpleNamespace
import sys
import continuation_bridge_run as bridge
import continuation_recalibrated_priors as prior

study=bridge.study
OUT=prior.OUT


def adapter():
    spec=importlib.util.spec_from_file_location('_prior_reference_runner',bridge.__file__)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.OUT=OUT
    return module


def prepare():
    assert not list((bridge.OUT/'evaluation/jobs').glob('*.json')),'N03 evaluation already observed; choose a genuinely fresh protocol instead'
    source=bridge.checked('evaluation');screen=study.read(OUT/'training-screen.json')
    assert screen['eligible'] and study.pilot.sha(OUT/'candidate.json')==study.read(OUT/'candidate-freeze.json')['sha256']
    paths=[OUT/'candidate.json',OUT/'candidate-freeze.json',OUT/'training-screen.json',OUT/'evaluation-protocol.md',
        study.ROOT/'tools/research/continuation_prior_evaluation.py',study.ROOT/'tools/research/continuation_recalibrated_priors.py',
        study.ROOT/'tools/research/continuation_bridge_run.py',bridge.OUT/'evaluation/manifest.json']
    inputs=dict(source['inputs']);inputs.update({str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in paths})
    manifest=study.signed(dict(cases=source['cases'],boards=source['boards'],jobs=source['jobs'],partition='prospective',
        inputs=inputs,binary_path=source['binary_path'],binary_sha256=source['binary_sha256'],target_gap_pct=.1,max_iterations=2000,
        source_manifest_id=source['id'],protocol='evaluation-protocol.md; model registered before any source outcomes exist.'))
    study.freeze(OUT/'prospective/manifest.json',manifest)
    study.freeze(OUT/'evaluation-registration.json',dict(registered_at=study.night.now(),manifest_id=manifest['id'],
        candidate_sha256=study.pilot.sha(OUT/'candidate.json'),source_references_at_registration=0,production_enabled=False))
    print('N09 registered before reference generation; 400 future queries reserved or shared with N03.',flush=True)


def registered():
    manifest=adapter().checked('prospective');record=study.read(OUT/'evaluation-registration.json')
    assert manifest['id']==record['manifest_id'] and record['source_references_at_registration']==0
    assert study.pilot.sha(OUT/'candidate.json')==record['candidate_sha256']
    return manifest,record


def evaluate():
    manifest,record=registered()
    source=bridge.checked('evaluation');assert source['id']==manifest['source_manifest_id']
    available=[bridge.OUT/'evaluation/jobs'/f"{j['id']}.json" for j in source['jobs']]
    count=sum(p.exists() for p in available)
    assert count in [0,len(available)],'Partial N03 evaluation requires inspection'
    if count:
        contexts=bridge.contexts('evaluation');mode='unchanged_N03_references'
    else:
        contexts=adapter().contexts('prospective');mode='dedicated_N09_references'
        available=[OUT/'prospective/jobs'/f"{j['id']}.json" for j in manifest['jobs']]
    stamp=dt.datetime.fromisoformat(record['registered_at']).timestamp()
    assert all(p.stat().st_mtime>=stamp for p in available),'A reference predates candidate registration'
    provenance=dict(mode=mode,candidate_sha256=record['candidate_sha256'],registered_at=record['registered_at'],
        files={str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in available})
    study.freeze(OUT/'evaluation-provenance.json',provenance)
    module=adapter()
    # Isolated namespaces retain the already tested metrics, bootstrap and gate.
    # The shared fit module and all N03 input/output locations remain unchanged.
    module.study=SimpleNamespace(**study.__dict__)
    module.study.fit=SimpleNamespace(**study.fit.__dict__)
    original_predict=study.fit.predict
    module.study.fit.predict=lambda c,m:prior.predict(c,m) if 'class_base' in m else original_predict(c,m)
    module.contexts=lambda partition:contexts
    return module.evaluate()


def run():
    with (OUT/'evaluation.lock').open('a+b') as lock:
        lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        try:
            registered()
            assert not bridge.other_research(),'Another research controller or GPU process is active'
            source=bridge.checked('evaluation')
            count=sum((bridge.OUT/'evaluation/jobs'/f"{j['id']}.json").exists() for j in source['jobs'])
            assert count in [0,len(source['jobs'])],'Partial source evaluation requires inspection'
            if not count:adapter().run_partition('prospective')
            result=evaluate()
            study.night.dump(OUT/'status.json',dict(stage='complete',accuracy_screen_passed=result['accuracy_screen_passed'],production_enabled=False,updated=study.night.now()))
        finally:
            lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)


if __name__=='__main__':{'prepare':prepare,'run':run,'evaluate':evaluate}[sys.argv[1]]()
