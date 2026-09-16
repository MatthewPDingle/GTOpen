"""One conservative revision selected from N06 training results, not test data."""
import copy
import numpy as np
import continuation_nonlinear_residual as network
import continuation_equity_moments as timing

study=network.study
OUT=study.ROOT/'research/preflop-evolution/continuation/shrunk-residual-20260916'
SCALE=.75


def shrink(model):
    result=copy.deepcopy(model)
    assert model['width']==8 and model['output_penalty']==.1 and len(model['networks'])==2
    for net in result['networks']:net['output']=(SCALE*np.array(net['output'])).tolist()
    if 'losses' in result:result['unshrunk_training_losses']=result.pop('losses')
    result.update(kind='shrunk_nonlinear_residual',residual_scale=SCALE,production_enabled=False)
    return result


def screen():
    timing.require_no_timing()
    paths=[OUT/'README.md',study.ROOT/'tools/research/continuation_shrunk_residual.py',
        study.ROOT/'tools/research/continuation_nonlinear_residual.py',
        study.ROOT/'tools/research/continuation_overnight_fit.py',study.ROOT/'tools/research/range_value_pilot.py',
        study.ROOT/'tools/research/continuation_policy_refinement.py',
        study.night.OUT/'manifest.json',study.OUT/'development/manifest.json',
        network.OUT/'training-screen.json',study.ROOT/'cache/preflop_eq169.bin',study.ROOT/'cache/realization_fit.json']
    study.freeze(OUT/'implementation-freeze.json',dict(inputs={str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in paths},production_enabled=False))
    cases=study.fit.load_cases('train')+study.contexts('development')
    assert len(cases)==26 and all(c['case']['partition']=='train' for c in cases)
    recorded=study.read(network.OUT/'training-screen.json')['scores']
    baseline=recorded[0];old=next(r for r in recorded if r['width']==8 and r['output_penalty']==.1)
    baseline_rows={r['case']:r for r in baseline['cases']};old_rows={r['case']:r for r in old['cases']}
    families=sorted({c['case']['family'] for c in cases});rows=[]
    for family in families:
        raw=network.fit([c for c in cases if c['case']['family']!=family],8,.1);model=shrink(raw)
        for c in cases:
            if c['case']['family']!=family:continue
            unshrunk=study.pilot.metrics(c,network.predict(c,raw))['candidate']
            base=study.pilot.metrics(c,study.fit.predict(c,raw['base']))['candidate']
            assert abs(unshrunk-old_rows[c['case']['id']]['candidate'])<1e-9,'N06 control changed'
            assert abs(base-baseline_rows[c['case']['id']]['candidate'])<1e-9,'Ordinary control changed'
            rows.append(dict(case=c['case']['id'],family=family,**study.pilot.metrics(c,network.predict(c,model)),original=base,unshrunk=unshrunk))
        print('Shrunk residual excluded family',family,flush=True)
    means={f:float(np.mean([r['candidate'] for r in rows if r['family']==f])) for f in families}
    mean=float(np.mean(list(means.values())));gain=1-mean/baseline['mean']
    worst=max(means[f]/baseline['family_means'][f] for f in families);eligible=gain>=.05 and worst<=1.05
    study.freeze(OUT/'training-screen.json',dict(cases=rows,family_means=means,mean=mean,improvement=gain,
        worst_family_ratio=worst,eligible=eligible,production_enabled=False,
        note='0.75 correction selected from prior N06 training results; fresh evaluation is still required.'))
    if eligible:
        model=shrink(network.fit(cases,8,.1))
        model.update(training_case_ids=[c['case']['id'] for c in cases],training_families=families)
        study.freeze(OUT/'candidate.json',model)
        study.freeze(OUT/'candidate-freeze.json',dict(sha256=study.pilot.sha(OUT/'candidate.json'),
            frozen_at=study.night.now(),prospective_references_generated=0))
    print('Shrunk residual eligible:',eligible,'gain',gain,'worst family',worst,flush=True)


if __name__=='__main__':screen()
