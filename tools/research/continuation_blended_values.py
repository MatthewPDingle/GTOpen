"""N33 fixed conservative blend screen on training families only."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import numpy as np
import continuation_shrunk_residual as shrunk
import continuation_pairwise_values as guard

study=shrunk.study
OUT=shrunk.OUT.parent/'blended-values-20260916'
ALPHAS=[0.,.125,.25,.5,1.]

def check_idle():
    guard.require_no_timing()
    path=OUT.parent/'zero-fallback-20260916/status.json'
    if path.exists():assert study.read(path)['stage']=='waiting_for_N21','N32 timing now active'

def run():
    check_idle();OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'training-screen.json').exists(),'Already completed'
    inputs=dict(study.read(shrunk.OUT/'implementation-freeze.json')['inputs'])
    for p in [Path(__file__),OUT/'README.md',Path(shrunk.__file__),shrunk.OUT/'training-screen.json']:
        inputs[str(p.resolve().relative_to(study.ROOT)).replace('\\','/')]=study.pilot.sha(p)
    for p,h in inputs.items():assert study.pilot.sha(study.ROOT/p)==h,p
    study.freeze(OUT/'protocol-freeze.json',dict(registered_at=study.night.now(),inputs=inputs,alphas=ALPHAS,production_enabled=False))
    cases=study.fit.load_cases('train')+study.contexts('development')
    assert len(cases)==26 and all(c['case']['partition']=='train' for c in cases)
    families=sorted({c['case']['family'] for c in cases})
    expected={r['case']:r['candidate'] for r in study.read(shrunk.OUT/'training-screen.json')['cases']}
    rows={a:[] for a in ALPHAS}
    for family in families:
        check_idle()
        model=shrunk.shrink(shrunk.network.fit([c for c in cases if c['case']['family']!=family],8,.1))
        for c in cases:
            if c['case']['family']!=family:continue
            predicted=shrunk.network.predict(c,model)
            error=study.pilot.metrics(c,predicted)['candidate']
            assert abs(error-expected[c['case']['id']])<1e-9,'N15 held-out control changed'
            for a in ALPHAS:
                blend=(1-a)*c['balanced']+a*predicted
                assert np.isfinite(blend).all() and abs((c['mass']*blend).sum()-1)<1e-9
                rows[a].append(dict(case=c['case']['id'],family=family,candidate=study.pilot.metrics(c,blend)['candidate']))
        print('Held out',family,flush=True)
    scores=[]
    for a in ALPHAS:
        means={f:float(np.mean([r['candidate'] for r in rows[a] if r['family']==f])) for f in families}
        scores.append(dict(alpha=a,cases=rows[a],family_means=means,mean=float(np.mean(list(means.values())))))
    for s in scores:
        s['improvement_over_balanced']=1-s['mean']/scores[0]['mean']
        s['worst_family_ratio_vs_balanced']=max(s['family_means'][f]/scores[0]['family_means'][f] for f in families)
        s['ratio_vs_full_N15']=s['mean']/scores[-1]['mean']
        s['eligible_for_settling_test']=bool(s['alpha']>0 and s['improvement_over_balanced']>=.15 and s['worst_family_ratio_vs_balanced']<=.95)
    selected=next((s['alpha'] for s in scores if s['eligible_for_settling_test']),None)
    for p,h in inputs.items():assert study.pilot.sha(study.ROOT/p)==h,p
    study.freeze(OUT/'training-screen.json',dict(scores=scores,selected_alpha=selected,controls_reproduced=26,inputs_unchanged=True,
        production_enabled=False,note='New tradeoff screen, not N15 predictor-selection qualification. Training families only; selected blend needs fresh accuracy and GPU end-to-end qualification.'))
    print('Selected alpha:',selected,flush=True)

if __name__=='__main__':run()
