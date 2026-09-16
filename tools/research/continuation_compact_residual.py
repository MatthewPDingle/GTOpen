"""One fixed half-width variant, trained without prospective labels."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import copy
import sys
import numpy as np
import continuation_nonlinear_residual as network
import continuation_equity_moments as timing
import continuation_night_queue as queue

study=network.study
OUT=network.OUT.parent/'compact-residual-20260916'


def shrink(model):
    assert model['width']==4 and model['output_penalty']==.1 and len(model['networks'])==2
    result=copy.deepcopy(model)
    for net in result['networks']:net['output']=(.75*np.array(net['output'])).tolist()
    result['unshrunk_training_losses']=result.pop('losses')
    result.update(kind='compact_shrunk_nonlinear_residual',residual_scale=.75,production_enabled=False)
    return result


def require_no_timing():
    timing.require_no_timing()
    for p in queue.processes():
        cmd=(p['CommandLine'] or '').lower()
        if p['Name'].lower() in ['python.exe','pythonw.exe']:
            assert not any(t in cmd for t in ['continuation_shrunk_gpu.py benchmark',
                'continuation_shrunk_mixed_gpu.py benchmark','continuation_pair_reductions.py benchmark']), 'GPU timing is active'


def prepare():
    assert not (network.OUT.parent/'shrunk-residual-20260916/evaluation.json').exists(),'N18 protocol must predate final N15 outcomes'
    paths=[OUT/'README.md',study.ROOT/'tools/research/continuation_compact_residual.py',
        study.ROOT/'tools/research/continuation_nonlinear_residual.py',
        study.ROOT/'tools/research/continuation_overnight_fit.py',study.ROOT/'tools/research/range_value_pilot.py',
        study.night.OUT/'manifest.json',study.OUT/'development/manifest.json',
        study.ROOT/'cache/realization_fit.json',study.ROOT/'cache/preflop_eq169.bin',
        network.OUT/'training-screen.json',network.OUT.parent/'shrunk-residual-20260916/training-screen.json']
    study.freeze(OUT/'implementation-freeze.json',dict(registered_at=study.night.now(),
        inputs={str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in paths},
        width=4,penalty=.1,residual_scale=.75,n15_final_evaluation_at_registration=False,production_enabled=False))


def checked():
    frozen=study.read(OUT/'implementation-freeze.json')
    for path,sha in frozen['inputs'].items():assert study.pilot.sha(study.ROOT/path)==sha,path
    assert frozen['n15_final_evaluation_at_registration'] is False
    return frozen


def gate(means,linear,teacher):
    mean=float(np.mean(list(means.values())))
    improvement=1-mean/linear['mean']
    worst_linear=max(means[f]/linear['family_means'][f] for f in means)
    ratio=mean/teacher['mean'];worst_teacher=max(means[f]/teacher['family_means'][f] for f in means)
    return dict(mean=mean,improvement_vs_linear=improvement,worst_linear_family_ratio=worst_linear,
        ratio_vs_n15=ratio,worst_n15_family_ratio=worst_teacher,
        eligible=improvement>=.05 and worst_linear<=1.05 and ratio<=1.05 and worst_teacher<=1.05)


def screen():
    require_no_timing();checked()
    assert not (OUT/'training-screen.json').exists(),'Fixed screen already completed'
    cases=study.fit.load_cases('train')+study.contexts('development')
    assert len(cases)==26 and all(c['case']['partition']=='train' for c in cases)
    families=sorted({c['case']['family'] for c in cases});assert len(families)==4
    linear=study.read(network.OUT/'training-screen.json')['scores'][0]
    teacher=study.read(network.OUT.parent/'shrunk-residual-20260916/training-screen.json')
    rows=[]
    for family in families:
        require_no_timing()
        model=shrink(network.fit([c for c in cases if c['case']['family']!=family],4,.1))
        for c in cases:
            if c['case']['family']==family:
                control=study.pilot.metrics(c,study.fit.predict(c,model['base']))['candidate']
                expected=next(r['candidate'] for r in linear['cases'] if r['case']==c['case']['id'])
                assert abs(control-expected)<1e-9,'Original control did not reproduce; inspect numerical environment'
                rows.append(dict(case=c['case']['id'],family=family,linear_control=control,
                    **study.pilot.metrics(c,network.predict(c,model))))
        print('Finished N18 excluded family',family,flush=True)
    means={f:float(np.mean([r['candidate'] for r in rows if r['family']==f])) for f in families}
    result=dict(cases=rows,family_means=means,production_enabled=False,**gate(means,linear,teacher))
    if result['eligible']:
        require_no_timing();model=shrink(network.fit(cases,4,.1))
        model.update(training_case_ids=[c['case']['id'] for c in cases],training_families=families)
        study.freeze(OUT/'candidate.json',model)
        study.freeze(OUT/'candidate-freeze.json',dict(sha256=study.pilot.sha(OUT/'candidate.json'),frozen_at=study.night.now(),
            prospective_references_generated=0,production_enabled=False))
    study.freeze(OUT/'training-screen.json',result)
    print('N18:',{k:v for k,v in result.items() if k not in ['cases','family_means']},flush=True)


if __name__=='__main__':{'prepare':prepare,'screen':screen}[sys.argv[1]]()
