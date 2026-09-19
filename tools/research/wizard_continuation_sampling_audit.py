"""Show small-panel instability using subsamples of the completed 40 flops."""
import numpy as np
import wizard_continuation_study as s


def run():
    m=s.read(s.OUT/'manifest.json');pm=s.read(s.OUT/'precision/manifest.json')
    assert s.read(s.OUT/'precision/status.json')['stage']=='ready_for_review'
    refined={j['id'] for j in pm['jobs']};fixtures=s.read(s.OUT/'fixtures.json');case,=fixtures['cases']
    boards=m['boards'];idx={b['board']:i for i,b in enumerate(boards)}
    rng=np.random.default_rng(1909202602);selection=np.zeros((5000,len(boards)))
    for group in sorted({b['stratum'] for b in boards}):
        options=[i for i,b in enumerate(boards) if b['stratum']==group]
        for row in selection:row[rng.choice(options,2,replace=False)]=1
    eq=s.compatible_equity(case);result=[]
    for menu in ('half','large'):
        rows=[]
        for j in m['jobs']:
            if j['menu']!=menu:continue
            r=s.read(s.OUT/('precision/jobs' if j['id'] in refined else 'jobs')/(j['id']+'.json'))
            s.validate(r,j,pm if j['id'] in refined else m);rows.append(r)
        for hand in fixtures['probes']:
            mass=np.zeros(len(boards));ev=mass.copy();residual=mass.copy()
            hidx=next(i for i,h in enumerate(case['balanced']['hands'][0]) if h['hand']==hand)
            for r in rows:
                h=next((h for h in r['hands'][0] if h['hand']==hand),None)
                if h is None:continue
                i=idx[r['job']['board']];mass[i]=r['job']['iso_weight']/r['job']['inclusion_probability']*h['pair_mass']
                ev[i]=mass[i]*h['ev_bb'];residual[i]=mass[i]*(h['ev_bb']-case['pot']*h['equity'])
            den=selection@mass;assert (den>0).all()
            direct=selection@ev/den;controlled=selection@residual/den+case['pot']*eq[hidx]
            full=ev.sum()/mass.sum();full_control=residual.sum()/mass.sum()+case['pot']*eq[hidx]
            result.append(dict(menu=menu,hand=hand,direct_40_bb=float(full),control_40_bb=float(full_control),
                direct_10_central90_bb=np.quantile(direct,[.05,.95]).tolist(),control_10_central90_bb=np.quantile(controlled,[.05,.95]).tolist(),
                direct_median_absolute_change_bb=float(np.median(abs(direct-full))),
                control_median_absolute_change_bb=float(np.median(abs(controlled-full_control)))))
    s.write(s.OUT/'small-panel-sensitivity.json',dict(results=result,seed=1909202602,draws=5000,flops_per_draw=10,
        note='Exploratory subsampling after completed results. Central ranges describe subsets of these 40 flops, not confidence intervals for all flops or an independent validation set.'))
    lines=['# Small-panel sensitivity','',
        'Earlier continuation experiments used small board panels. To assess how sensitive labels can be, this exploratory diagnostic takes 5,000 different ten-flop subsets (two per stratum) from the completed forty-flop study. No solver was rerun and no extra board outcomes were acquired.','',
        'The numbers below are the median absolute change from the forty-flop estimate, in bb. This is not an error estimate against the true value, an independent test, or a confidence interval. It measures instability from choosing a smaller panel within these observed boards.','',
        '| Hand | 50% menu direct | 50% menu equity control | 75% menu direct | 75% menu equity control |','|---|---:|---:|---:|---:|']
    for hand in fixtures['probes']:
        rr=[next(r for r in result if (r['hand'],r['menu'])==(hand,menu)) for menu in ('half','large')]
        cells=[f"{r[k]:.2f}" for r in rr for k in ('direct_median_absolute_change_bb','control_median_absolute_change_bb')]
        lines.append(f"| {hand} | {' | '.join(cells)} |")
    lines+=['',
        'This supports measuring label precision before treating small differences as training targets. Equity control helps some hands but does not eliminate the effect of uncommon high-value boards. This diagnostic alone cannot attribute the previous models\' transfer failures to sampling noise: those studies used different ranges, boards and targets.','']
    (s.OUT/'SAMPLING.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')


if __name__=='__main__':run()
