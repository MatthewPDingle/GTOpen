"""Paired sensitivity of AA's connected call and 4-bet values."""
import numpy as np
import wizard_continuation_study as s


def run():
    four=s.OUT/'fourbet-call'
    assert s.read(four/'status.json')['stage']=='ready_for_review'
    original=s.read(s.OUT/'manifest.json');fm=s.read(four/'manifest.json');pm=s.read(s.OUT/'precision/manifest.json')
    refined={j['id'] for j in pm['jobs']};boards=original['boards'];index={b['board']:i for i,b in enumerate(boards)}
    audit=s.read(s.OUT/'premium-branches.json');root=[1,2,0,0,0,0,0,0]
    decision=next(n for n in audit['nodes'] if n['path']==root)
    reply=next(n for n in audit['nodes'] if n['path']==root+[2])
    probability=reply['view']['actions'][1]['freq']
    saved=np.array(next(h for h in decision['selected_action_values'] if h['hand']=='AA')['action_ev_bb'])
    rng=np.random.default_rng(19092026);draws=np.zeros((5000,len(boards)))
    for group in sorted({b['stratum'] for b in boards}):
        indices=[i for i,b in enumerate(boards) if b['stratum']==group]
        for row in draws:np.add.at(row,rng.choice(indices,len(indices)),1)
    results=[]
    for menu in ('half','large'):
        estimates=[];points=[];fast=[]
        for directory,manifest in ((s.OUT,original),(four,fm)):
            case,=s.read(directory/'fixtures.json')['cases']
            aa=next(i for i,h in enumerate(case['balanced']['hands'][0]) if h['hand']=='AA')
            fast.append(case['balanced']['hands'][0][aa]['value_bb'])
            control=case['pot']*s.compatible_equity(case)[aa]
            mass=np.zeros(len(boards));value=mass.copy();residual=mass.copy()
            for j in manifest['jobs']:
                if j['menu']!=menu:continue
                use_precision=directory==s.OUT and j['id'] in refined
                r=s.read(directory/('precision/jobs' if use_precision else 'jobs')/(j['id']+'.json'))
                s.validate(r,j,pm if use_precision else manifest)
                h=next((h for h in r['hands'][0] if h['hand']=='AA'),None)
                if h is None:continue
                assert h['br_ev_bb']-h['ev_bb']<=.05
                i=index[j['board']];mass[i]=j['iso_weight']/j['inclusion_probability']*h['pair_mass']
                value[i]=mass[i]*h['ev_bb'];residual[i]=mass[i]*(h['ev_bb']-case['pot']*h['equity'])
            den=draws@mass;assert (den>0).all()
            estimates.append((draws@value/den,draws@residual/den+control))
            points.append((value.sum()/mass.sum(),residual.sum()/mass.sum()+control))
        for k,label in enumerate(('direct','equity_control')):
            call=estimates[0][k]-12
            fourbet=saved[2]+probability*(estimates[1][k]-fast[1])
            point_call=points[0][k]-12
            point_fourbet=saved[2]+probability*(points[1][k]-fast[1])
            results.append(dict(menu=menu,estimator=label,call_bb=float(point_call),fourbet_bb=float(point_fourbet),jam_bb=float(saved[3]),
                call_ci95_bb=np.quantile(call,[.025,.975]).tolist(),fourbet_ci95_bb=np.quantile(fourbet,[.025,.975]).tolist(),
                fourbet_minus_call_bb=float(point_fourbet-point_call),fourbet_minus_call_ci95_bb=np.quantile(fourbet-call,[.025,.975]).tolist()))
    s.write(s.OUT/'connected-aa-sensitivity.json',dict(results=results,
        source_hashes={p.relative_to(s.ROOT).as_posix():s.sha(p) for p in [s.OUT/'manifest.json',s.OUT/'precision/manifest.json',four/'manifest.json',s.OUT/'premium-branches.json']},
        note='Exploratory fixed-policy action sensitivity, using matched board resamples. Two prepared ranges differ from the original by documented tiny changes. No preflop re-solve; all-in and fold branches unchanged; preflop reply probabilities retain independent-class convention.'))
    lines=['# AA: connected continuation sensitivity','',
        'This checks the call and called-4-bet continuations together. The postflop estimates use each branch\'s own prepared ranges. The saved opponent response frequencies, other preflop branches, and all-in values remain fixed. This is an exploratory sensitivity analysis, not a new solved strategy.','',
        '| Menu | Estimate | Call EV | 4-bet EV | Jam EV | 4-bet minus call [paired 95% interval] |','|---|---|---:|---:|---:|---:|']
    for r in results:
        lo,hi=r['fourbet_minus_call_ci95_bb']
        lines.append(f"| {r['menu']} | {r['estimator']} | {r['call_bb']:.2f} | {r['fourbet_bb']:.2f} | {r['jam_bb']:.2f} | {r['fourbet_minus_call_bb']:+.2f} [{lo:+.2f}, {hi:+.2f}] |")
    lines+=['',
        'Values are bb relative to folding at the original decision. Calling subtracts the additional 12bb from its postflop continuation. The 4-bet replaces only the fast called-branch price difference, weighted by LJ\'s saved call probability. Bootstrap draws are shared across both branches and menus; overlapping marginal intervals are not used to judge their difference.','',
        'The direct estimate is primary. Equity control uses a sampled cache and its intervals omit cache uncertainty. Both omit model uncertainty. A switch in the preferred action under frozen ranges would change those ranges and the opponent\'s behavior in a re-solve. Thus a favorable number here is not proof of improved full-game play or agreement with Wizard.','']
    (s.OUT/'CONNECTED-AA.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')


if __name__=='__main__':run()
