"""Training-only finite-population flop-sampling diagnostic; no model selection."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import collections
import numpy as np
import continuation_policy_refinement as study

OUT=study.ROOT/'research/preflop-evolution/continuation/night-shift-20260916'


def arrays(c):
    n=len(c['rows']);numerator=np.zeros((n,2,169));denominator=np.zeros_like(numerator)
    strata=collections.defaultdict(list)
    for i,row in enumerate(c['rows']):
        job=row['job'];strata[job['stratum']].append(i)
        for player in range(2):
            for hand in row['hands'][player]:
                k=study.pilot.INDEX[hand['hand']]
                mass=job['iso_weight']/job['inclusion_probability']*hand['pair_mass']
                denominator[i,player,k]=mass
                numerator[i,player,k]=mass*(hand['ev_bb']/c['case']['pot']-hand['equity'])
    target=denominator.sum(axis=0)
    residual=np.divide(numerator.sum(axis=0),target,out=np.zeros_like(target),where=target>0)
    np.testing.assert_allclose(residual,c['residual'],atol=1e-12,rtol=0)
    assert sorted(map(len,strata.values()))==[20]*5
    return numerator,denominator,strata


def sample(c,boards):
    numerator,denominator,strata=arrays(c)
    rng=np.random.default_rng(20260916+boards)
    draws=np.zeros((200,len(c['rows'])))
    for b in range(200):
        for ids in strata.values():draws[b,rng.choice(ids,boards//5,replace=False)]=1
    num=np.einsum('bi,iph->bph',draws,numerator)
    den=np.einsum('bi,iph->bph',draws,denominator)
    subset=np.divide(num,den,out=np.zeros_like(num),where=den>0)
    observed=den>0;weight=observed*c['mass'];weight/=weight.sum(axis=(1,2),keepdims=True)
    differences=(abs(subset-c['residual'])*weight).sum(axis=(1,2))*100
    return dict(boards=boards,draws=200,mean_deviation_pct_pot=float(differences.mean()),
        median_deviation_pct_pot=float(np.median(differences)),
        central_90_deviation_pct_pot=np.quantile(differences,[.05,.95]).tolist(),
        largest_missing_compatible_mass_fraction=float(((~observed)*c['mass']).sum(axis=(1,2)).max()/2))


def main():
    cases=study.fit.load_cases('train')+study.contexts('development')
    assert len(cases)==26 and all(c['case']['partition']=='train' for c in cases)
    control=study.read(OUT/'curvature-final-selection.json')
    control=next(s for s in control['scores'] if s['kind']=='shape' and s['alpha']==.1)
    errors={c['case']:c['candidate'] for c in control['cases']}
    rows=[]
    for c in cases:
        quality=study.fit.quality(c)
        rows.append(dict(case=c['case']['id'],family=c['case']['family'],
            ordinary_family_cv_mae_pct_pot=errors[c['case']['id']],
            subsamples=[sample(c,n) for n in [20,50,100]],
            mean_reference_br_gain_pct_pot=float((quality*c['mass']).sum()/2)))
    families=[]
    for family in sorted({r['family'] for r in rows}):
        selected=[r for r in rows if r['family']==family]
        families.append(dict(family=family,model_mae_pct_pot=float(np.mean([r['ordinary_family_cv_mae_pct_pot'] for r in selected])),
            mean_subsample_deviation_pct_pot={str(n):float(np.mean([next(s for s in r['subsamples'] if s['boards']==n)['mean_deviation_pct_pot'] for r in selected])) for n in [20,50,100]}))
    result=dict(cases=rows,families=families,production_enabled=False,
        interpretation='Subset versus full 100-board training labels; not error versus exact all-flop truth, not an irreducible error floor or model-selection score.',
        method='200 deterministic without-replacement stratified subsets, 4/10/20 boards per each of 5 strata; paired ratio estimator, equity control variate; original targets unchanged.')
    study.freeze(OUT/'label-precision.json',result)
    lines=['# Flop-sampling precision diagnostic','',result['interpretation'],'',result['method'],'',
        '| Training family | Model family-CV error | 20-board subset deviation | 50-board subset deviation |',
        '|---|---:|---:|---:|']
    for f in families:
        d=f['mean_subsample_deviation_pct_pot']
        lines.append(f"| {f['family']} | {f['model_mae_pct_pot']:.3f} | {d['20']:.3f} | {d['50']:.3f} |")
        assert d['100']<1e-10
    lines+=['','All figures are compatible-mass-weighted mean absolute deviations as a percentage of starting pot. '
        'The model column uses family-withheld predictions on the same 26 training cases. The other columns '
        'compare subsets with their containing 100-board sample, so their errors are correlated. They do not '
        'estimate the exact uncertainty of a separate 20-board sample or the full 100-board labels.', '',
        'No evaluation labels were read; no model, threshold or reference changed. This diagnosis guides later '
        'data collection. N03 remains on its original 20-board-per-context protocol. Per-case intervals, missing '
        'hand mass and range-average reference BR gains are in [the JSON record](label-precision.json).','']
    (OUT/'label-precision.md').write_text('\n'.join(lines),encoding='utf-8')
    print(families)


if __name__=='__main__':main()
