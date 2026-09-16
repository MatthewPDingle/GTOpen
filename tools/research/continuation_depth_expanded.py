"""Fixed N12 repeat with newly collected training data; same-family exclusion."""
import continuation_depth_priors as depth
import continuation_bridge_run as bridge
import numpy as np

study=depth.study
OUT=depth.OUT.parent/'depth-priors-expanded-20260916'


def screen():
    paths=[study.ROOT/'tools/research/continuation_depth_expanded.py',OUT/'README.md',
        study.ROOT/'tools/research/continuation_depth_priors.py',
        study.ROOT/'tools/research/continuation_recalibrated_priors.py',
        depth.prior.OUT/'training-screen.json',depth.OUT/'training-screen.json',bridge.OUT/'training/manifest.json']
    study.freeze(OUT/'implementation-freeze.json',dict(inputs={str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in paths},production_enabled=False))
    original=study.fit.load_cases('train')+study.contexts('development')
    cases=original+bridge.contexts('training')
    assert len(original)==26 and len(cases)==62 and all(c['case']['partition']=='train' for c in cases)
    controls={c['case']:c for c in study.read(depth.prior.OUT/'training-screen.json')['cases']}
    assert set(controls)=={c['case']['id'] for c in original}
    counts,equity=study.pilot.matrices();families=sorted({c['case']['family'] for c in cases});rows=[]
    for family in families:
        training=[c for c in cases if c['case']['family']!=family]
        candidate=depth.fit(training,counts,equity)
        same_data=depth.prior.fit(training,counts,equity)
        for c in original:
            if c['case']['family']!=family:continue
            errors=study.pilot.metrics(c,depth.predict(c,candidate,counts,equity))
            same=study.pilot.metrics(c,depth.prior.predict(c,same_data,counts,equity))['candidate']
            control=controls[c['case']['id']]
            assert control['family']==family and abs(control['balanced']-errors['balanced'])<1e-10
            rows.append(dict(case=c['case']['id'],family=family,**errors,
                n09_original=control['candidate'],n09_expanded=same))
        print('Finished expanded excluded family',family,flush=True)
    family_means={name:{f:float(np.mean([r[name] for r in rows if r['family']==f])) for f in families}
        for name in ['candidate','n09_original','n09_expanded','balanced','raw']}
    means={name:float(np.mean(list(values.values()))) for name,values in family_means.items()}
    comparisons={name:dict(improvement=1-means['candidate']/means[name],
        worst_family_ratio=max(family_means['candidate'][f]/family_means[name][f] for f in families))
        for name in ['n09_original','n09_expanded','balanced']}
    eligible=(all(comparisons[n]['improvement']>=.05 for n in ['n09_original','n09_expanded'])
        and comparisons['balanced']['improvement']>=.15
        and all(v['worst_family_ratio']<=1.05 for v in comparisons.values()))
    result=dict(training_cases=62,validation_cases=26,cases=rows,family_means=family_means,means=means,
        comparisons=comparisons,eligible=eligible,production_enabled=False,note='Fixed expanded-data repeat; original validation contexts; three controls must pass.')
    study.freeze(OUT/'training-screen.json',result)
    if eligible:
        model=depth.fit(cases,counts,equity)
        model.update(training_case_ids=[c['case']['id'] for c in cases],training_families=families,
            selection_sha256=study.pilot.sha(OUT/'training-screen.json'))
        study.freeze(OUT/'candidate.json',model)
        study.freeze(OUT/'candidate-freeze.json',dict(sha256=study.pilot.sha(OUT/'candidate.json'),
            frozen_at=study.night.now(),prospective_references_generated=0))
    print('Expanded depth eligible:',eligible,'comparisons:',comparisons,flush=True)


if __name__=='__main__':screen()
