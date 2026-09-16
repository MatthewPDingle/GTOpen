"""Predeclared fresh-board check for the two expanded-data training screens."""
import collections
import datetime as dt
import hashlib
import importlib.util
import msvcrt
import os
import sys
import numpy as np
import continuation_bridge_run as bridge

study=bridge.study
OUT=study.ROOT/'research/preflop-evolution/continuation/expanded-validation-20260916'
MODELS={'N06b':'nonlinear-expanded-20260916','N08':'precision-weighted-20260916'}


def adapter():
    # A separate module namespace keeps the existing study's paths unchanged.
    spec=importlib.util.spec_from_file_location('_expanded_reference_runner',bridge.__file__)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.OUT=OUT
    return module


def board_pool():
    manifests=[study.night.OUT/'manifest.json',study.pilot.OUT/'manifest.json',
        study.pilot.AUDIT/'manifest.json',study.pilot.AUDIT/'extension/manifest.json',
        study.OUT/'development/manifest.json',study.OUT/'evaluation/manifest.json',
        bridge.OUT/'training/manifest.json',bridge.OUT/'evaluation/manifest.json']
    excluded=set()
    for path in manifests:
        m=study.read(path)
        excluded.update(b['board'] for b in m.get('boards',m['jobs']))
    groups=collections.defaultdict(list)
    for board,iso in study.read(study.pilot.AUDIT/'fixtures.json')['canonical_flops']:
        if board in excluded:continue
        cards=[board[i:i+2] for i in range(0,6,2)]
        key=('paired' if len({c[0] for c in cards})<3 else 'unpaired')+'/'+str(len({c[1] for c in cards}))+'suits'
        groups[key].append((board,iso))
    selected=[]
    for key,items in sorted(groups.items()):
        assert len(items)>=10,(key,len(items))
        items.sort(key=lambda x:hashlib.sha256(('expanded-final-evaluation-20260916'+x[0]).encode()).digest())
        selected.extend(dict(board=b,iso_weight=i,stratum=key,inclusion_probability=10/len(items)) for b,i in items[:10])
    assert len(selected)==50 and len({b['board'] for b in selected})==50
    assert not excluded.intersection(b['board'] for b in selected)
    return selected,manifests


def prepare():
    source=bridge.checked('evaluation');boards,paths=board_pool()
    paths += [study.ROOT/'tools/research/continuation_final_evaluation.py',
        study.ROOT/'tools/research/continuation_bridge_run.py',
        study.ROOT/'tools/research/continuation_nonlinear_residual.py',
        study.ROOT/'tools/research/continuation_overnight_fit.py',
        study.ROOT/'tools/research/range_value_pilot.py',OUT/'README.md']
    inputs=dict(source['inputs'])
    inputs.update({str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in paths})
    templates={j['case']:j for j in source['jobs']};jobs=[]
    for board in boards:
        for case in source['cases']:
            template=templates[case['id']]
            jobs.append(dict(**board,case=case['id'],id=case['id']+'-'+board['board'],
                config=dict(template['config'],board=board['board'])))
    manifest=study.signed(dict(cases=source['cases'],boards=boards,jobs=jobs,partition='prospective',inputs=inputs,
        binary_path=source['binary_path'],binary_sha256=source['binary_sha256'],target_gap_pct=.1,max_iterations=2000,
        protocol='Both fixed training screens must finish and eligible models must be registered before any reference is generated.'))
    study.freeze(OUT/'prospective/manifest.json',manifest)
    print('Reserved 400 fresh references. No reference generation or model selection performed.',flush=True)


def register():
    manifest=adapter().checked('prospective')
    path=OUT/'registered-models.json'
    if path.exists():
        result=study.read(path)
        assert result['manifest_id']==manifest['id']
        for model in result['models']:
            for relative,digest in model['inputs'].items():assert study.pilot.sha(study.ROOT/relative)==digest
        return result
    assert not list((OUT/'prospective/jobs').glob('*.json')),'Reference generation predates registration'
    records=[]
    for name,folder in MODELS.items():
        root=OUT.parent/folder;screen=study.read(root/'training-screen.json')
        if screen['selected'] is None:continue
        assert screen['selected']['eligible']
        model=study.read(root/'candidate.json');freeze=study.read(root/'candidate-freeze.json')
        assert model['production_enabled'] is False
        assert study.pilot.sha(root/'candidate.json')==freeze['sha256']
        assert freeze['prospective_references_generated']==0
        assert not set(model['training_families']).intersection(c['family'] for c in manifest['cases'])
        paths=[root/'training-screen.json',root/'candidate.json',root/'candidate-freeze.json',root/'implementation-freeze.json']
        records.append(dict(name=name,candidate=str((root/'candidate.json').relative_to(study.ROOT)).replace('\\','/'),
            inputs={str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in paths}))
    result=dict(models=records,manifest_id=manifest['id'],registered_at=study.night.now(),
        production_enabled=False,note='All eligible fixed-screen candidates registered together; no selection or refitting using these labels.')
    study.freeze(path,result)
    return result


def accuracy_gate(families,cases):
    return all(f['improvement_vs_balanced']>=.15 for f in families) and all(c['regression_vs_previous']<=.1 for c in cases)


def evaluate():
    registration=register();runner=adapter();cases=runner.contexts('prospective')
    registered=dt.datetime.fromisoformat(registration['registered_at']).timestamp()
    for path in (OUT/'prospective/jobs').glob('*.json'):assert path.stat().st_mtime>=registered
    old=study.read(study.night.OUT/'candidate.json');evaluations=[]
    for record in registration['models']:
        model=study.read(study.ROOT/record['candidate']);rows=[];boots=[]
        if record['name']=='N06b':
            from continuation_nonlinear_residual import predict
        else:predict=study.fit.predict
        for c in cases:
            pred=predict(c,model);previous=study.fit.predict(c,old)
            assert np.isfinite(pred).all() and abs((pred*c['mass']).sum()-1)<1e-9
            errors=study.pilot.metrics(c,pred);errors['previous']=study.pilot.metrics(c,previous)['candidate']
            boot=study.fit.bootstrap(c,pred);boot['previous']=study.fit.bootstrap(c,previous)['candidate'];boots.append(boot)
            quality=study.fit.quality(c)
            rows.append(dict(case=c['case']['id'],family=c['case']['family'],mae_pct_pot=errors,
                regression_vs_previous=errors['candidate']/errors['previous']-1,
                paired_90_improvement_ci={n:np.quantile(1-boot['candidate']/boot[n],[.05,.95]).tolist() for n in ['balanced','previous']},
                max_probe_br_gain_pct_pot=float(quality[:,[study.pilot.INDEX[h] for h in study.night.PROBES]].max())))
        families=[]
        for family in sorted({c['family'] for c in rows}):
            ids=[i for i,c in enumerate(rows) if c['family']==family]
            errors={n:float(np.mean([rows[i]['mae_pct_pot'][n] for i in ids])) for n in ['candidate','balanced','previous','raw']}
            bootstrap={n:np.mean([boots[i][n] for i in ids],axis=0) for n in errors}
            families.append(dict(family=family,mae_pct_pot=errors,improvement_vs_balanced=1-errors['candidate']/errors['balanced'],
                paired_90_improvement_ci={n:np.quantile(1-bootstrap['candidate']/bootstrap[n],[.05,.95]).tolist() for n in ['balanced','previous']}))
        evaluations.append(dict(model=record['name'],candidate_sha256=study.pilot.sha(study.ROOT/record['candidate']),
            accuracy_screen_passed=accuracy_gate(families,rows),families=families,cases=rows))
    result=dict(models=evaluations,reference_jobs=sum(len(c['rows']) for c in cases),production_enabled=False,
        caveat='Fresh-board evidence on historically used held-out case identities. Conditional bootstrap intervals exclude training uncertainty. No action-frequency or full-game exploitability guarantee.')
    study.night.dump(OUT/'evaluation.json',result)
    return result


def run():
    with (OUT/'run.lock').open('a+b') as lock:
        lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        try:
            registration=register()
            if not registration['models']:
                study.night.dump(OUT/'status.json',dict(stage='no_eligible_candidate',updated=study.night.now(),production_enabled=False))
                return
            assert not bridge.other_research(),'Another research controller or GPU child is alive'
            runner=adapter();runner.run_partition('prospective');evaluate()
            study.night.dump(OUT/'status.json',dict(stage='complete',updated=study.night.now(),production_enabled=False))
        finally:
            lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)


if __name__=='__main__':{'prepare':prepare,'register':register,'run':run,'evaluate':evaluate}[sys.argv[1]]()
