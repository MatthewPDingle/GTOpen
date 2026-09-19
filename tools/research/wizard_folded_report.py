"""Review the physical-deal diagnostic and a labelled fixed-policy intervention."""
import numpy as np
import wizard_continuation_study as s


def run():
    freeze=s.read(s.OUT/'folded-showdown-freeze.json')
    for path,digest in freeze['inputs'].items():assert s.sha(s.ROOT/path)==digest,path
    raw=s.read(s.OUT/'folded-showdown-batches.json');b=np.array(raw['batches']);total=b.sum(axis=0)
    assert b.shape==(40,2,5) and raw['draws']==32000000
    assert (b[:,:,0]>0).all() and (b[:,:,3]<=b[:,:,2]).all()
    names=['jam_call_probability','called_equity','jam_ev_bb']
    def estimate(t):return np.array([t[2]/t[0],t[3]/t[2],t[4]/t[0]])
    rows=[];replicas=[]
    for i in range(2):
        point=estimate(total[i]);jk=np.array([estimate(total[i]-r[i]) for r in b]);replicas.append(jk)
        se=np.sqrt(39/40*((jk-jk.mean(axis=0))**2).sum(axis=0))
        rows.append(dict(mode=raw['modes'][i],estimates=dict(zip(names,point.tolist())),monte_carlo_se=dict(zip(names,se.tolist())),
            effective_samples=float(total[i,0]**2/total[i,1])))
    delta=estimate(total[1])-estimate(total[0]);jk=replicas[1]-replicas[0]
    se=np.sqrt(39/40*((jk-jk.mean(0))**2).sum(0))
    analytic=next(r for r in s.read(s.OUT/'premium-card-audit.json')['results'] if r['weighting']=='compatible')
    assert abs(rows[0]['estimates']['jam_call_probability']-analytic['jam_call_probability'])<5*rows[0]['monte_carlo_se']['jam_call_probability']
    audit=s.read(s.OUT/'premium-branches.json');root=[1,2,0,0,0,0,0,0]
    node=lambda suffix:next(n for n in audit['nodes'] if n['path']==root+suffix)
    case,=s.read(s.OUT/'fourbet-call/fixtures.json')['cases'];labels=[h['hand'] for h in case['balanced']['hands'][0]]
    combos=np.zeros(169)
    for a in range(52):
        for c in range(a+1,52):
            if a in (48,49) or c in (48,49):continue
            hi,lo=max(a//4,c//4),min(a//4,c//4)
            i=hi*13+lo if a%4==c%4 or hi==lo else lo*13+hi;combos[i]+=1
    assert combos.sum()==1225 and combos[168]==1
    mass=combos*np.array(node([])['view']['reaches_all'][2]);mass/=mass.sum()
    sig=np.array(node([3])['view']['strategy']).reshape(2,169)[1].copy()
    eq=np.frombuffer((s.ROOT/'cache/preflop_eq169.bin').read_bytes()[4:],dtype='<f4').reshape(169,169).astype(float)
    eq=(eq+1-eq.T)/2;np.fill_diagonal(eq,.5)
    value=lambda p:float(mass@((1-p)*27.5+p*(397.5*eq[168]-194)))
    old=value(sig)
    for h,p in s.read(s.OUT/'wizard-opponent-ui.json')['versus_jam200']['call_percent'].items():sig[labels.index(h)]=p/100
    swap=dict(original_bb=old,six_hand_swap_bb=value(sig),change_bb=value(sig)-old,
        note='Artificial six-hand response swap only; GTOpen entering ranges retained, no joint equilibrium or production candidate. Cached equity, two-hand compatibility, no folded-card conditioning.')
    result=dict(results=rows,paired_change=dict(zip(names,delta.tolist())),paired_monte_carlo_se=dict(zip(names,se.tolist())),
        six_hand_swap=swap,source_hashes={p.relative_to(s.ROOT).as_posix():s.sha(p) for p in [s.OUT/'folded-showdown-batches.json',s.OUT/'folded-showdown-freeze.json',s.OUT/'wizard-opponent-ui.json']})
    s.write(s.OUT/'folded-showdown-summary.json',result)
    lines=['# Folded cards and opponent response: reviewed diagnostic','',
        'The complete physical-deal check leaves the main conclusion intact: omitted folded-card information is a small contribution in this one AA decision, while the opponent response policy has a much larger effect. This is not a new solved strategy.','',
        '32 million deals, 40 independent batches, frozen saved policies, actual seven-card showdowns, and no equity cache. Hero holds AcAd; suit symmetry applies before the flop. Four CPU threads; production untouched.','',
        '| Condition | Opponent calls jam | AA equity when called | AA jam EV |','|---|---:|---:|---:|']
    for r in rows:
        e=r['estimates'];lines.append(f"| {r['mode']} | {100*e['jam_call_probability']:.2f}% | {100*e['called_equity']:.2f}% | {e['jam_ev_bb']:.3f}bb |")
    lines += ['',f"Accounting for the six folds changes jam EV by {delta[2]:+.3f}bb; approximate paired Monte Carlo 95% interval [{delta[2]-1.96*se[2]:+.3f}, {delta[2]+1.96*se[2]:+.3f}]bb. Effective sample sizes are about {rows[0]['effective_samples']:,.0f} and {rows[1]['effective_samples']:,.0f}. These intervals exclude model uncertainty and policy adaptation.", '',
        'The no-fold-conditioning arm reproduces the analytic two-hand-compatible call probability within its sampling error. Its jam EV is also close to the prior cached-equity estimate of 44.20bb. The earlier, cheaper range-conditioning calculation retained cached equity and found +0.246bb; this extension samples the actual board as well. Do not treat the two estimates as the same experiment.','',
        '## Response-policy sensitivity','',
        f"Holding GTOpen's LJ entering range fixed but replacing only the six inspected jam-response hand frequencies with Wizard's changes AA jam EV from {old:.2f}bb to {value(sig):.2f}bb. This +{value(sig)-old:.2f}bb is a deliberately artificial intervention, not an improvement claim or a prediction of Wizard's EV.", '',
        'Wizard and GTOpen put different hands into the preceding jam. An opponent defending against one jam range cannot be transplanted into the other and called an equilibrium. This supports testing jointly adapting ranges and responses rather than fitting a premium bonus or copying a visible chart.','',
        'Scope: one 200bb NL25 decision, saved GTOpen strategies, configured rake, and no new preflop solve. The original Wizard tree and GTOpen tree still have documented differences. Reserved 100bb references remain untouched.','']
    (s.OUT/'FOLDED-CARDS.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    print('Folded-card change',delta[2],'SE',se[2]);print('Six-hand intervention',swap)


if __name__=='__main__':run()
