"""Review cached and independently dealt local call values."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import wizard_continuation_study as s


def run():
    freeze=s.read(s.OUT/'jam-response-physical-freeze.json')
    for path,digest in freeze['inputs'].items():assert s.sha(s.ROOT/path)==digest,path
    raw=s.read(s.OUT/'jam-response-physical-batches.json');analytic=s.read(s.OUT/'jam-response-audit.json')
    assert raw['draws_per_hand']==32000000 and len(raw['batches'])==400
    rows=[]
    for hand in ['AA','KK','QQ','JJ','AKs','AKo','AQs','AJs','ATs','KQs']:
        selected=[r for r in raw['batches'] if r['hand']==hand]
        assert len(selected)==40 and {r['batch'] for r in selected}==set(range(40))
        b=np.array([r['sums'] for r in selected]);t=b.sum(0);modes=[]
        assert (b[:,:,0]>0).all() and (b[:,:,2]>=0).all() and (b[:,:,2]<=b[:,:,0]).all()
        for i,mode in enumerate(raw['modes']):
            value=397.5*t[i,2]/t[i,0]-182
            jk=np.array([397.5*(t[i,2]-r[i,2])/(t[i,0]-r[i,0])-182 for r in b])
            se=np.sqrt(39/40*((jk-jk.mean())**2).sum())
            modes.append(dict(mode=mode,call_ev_bb=float(value),monte_carlo_se_bb=float(se),
                monte_carlo_ci95_bb=[float(value-1.96*se),float(value+1.96*se)],effective_samples=float(t[i,0]**2/t[i,1])))
        old=next(r for r in analytic['hand_results'] if r['hand']==hand)
        rows.append(dict(hand=hand,independent_call_ev_bb=old['independent_call_ev_bb'],
            cached_compatible_call_ev_bb=old['compatible_call_ev_bb'],saved_call_probability=old['saved_call_probability'],
            entering_weight=old['entering_weight'],physical=modes))
    result=dict(results=rows,draws_per_hand=32000000,total_draws=320000000,
        source_hashes={p.relative_to(s.ROOT).as_posix():s.sha(p) for p in [s.OUT/'jam-response-physical-batches.json',s.OUT/'jam-response-physical-freeze.json',s.OUT/'jam-response-audit.json']},
        note='Monte Carlo intervals cover independent sampling only, conditional on saved policies. Fresh physical boards do not use the class equity cache. Some tiny edges remain unresolved. No global equilibrium claim.')
    s.write(s.OUT/'jam-response-reviewed.json',result)
    chart=[r for r in rows if r['hand'] in ['KK','QQ','JJ','AKs','AKo','AQs']]
    fig,ax=plt.subplots(figsize=(9,4.5),layout='constrained');x=np.arange(len(chart))
    ax.scatter(x-.1,[r['independent_call_ev_bb'] for r in chart],marker='x',s=65,label='Current independent-class value',color='#c45646')
    means=[r['physical'][1]['call_ev_bb'] for r in chart];err=[1.96*r['physical'][1]['monte_carlo_se_bb'] for r in chart]
    ax.errorbar(x+.1,means,yerr=err,fmt='o',capsize=4,color='#337aad',label='Physical cards and six folds: 95% MC interval')
    ax.axhline(0,color='#777',linestyle='--');ax.set(xticks=x,xticklabels=[r['hand'] for r in chart],ylabel='LJ call value relative to folding (bb)',title='Same saved UTG jam policy; different card conditioning')
    ax.grid(alpha=.15);ax.legend(fontsize=8);fig.savefig(s.OUT/'jam-response-values.png',dpi=170);plt.close(fig)
    lines=['# Physical-card response audit: reviewed results','',
        '**Confirmed in this saved spot:** ignoring the caller\'s cards when constructing the opponent\'s range can reverse the value of important calls. This is a separate limitation from the postflop continuation approximation. This all-in branch has no postflop betting left.','',
        '32 million physical eight-player deals and boards per hand, ten selected hands, four CPU threads. The full conditioning includes the six observed folds. The old independent-class formula first reproduced all six exported saved action values within 0.0001bb. Both calculations therefore concern the same saved policy and pot accounting.','',
        '| LJ hand | Current call % | Independent EV | Physical EV, six folds [95% MC interval] |','|---|---:|---:|---:|']
    for r in rows:
        p=r['physical'][1];lo,hi=p['monte_carlo_ci95_bb']
        lines.append(f"| {r['hand']} | {100*r['saved_call_probability']:.1f}% | {r['independent_call_ev_bb']:+.2f} | {p['call_ev_bb']:+.2f} [{lo:+.2f}, {hi:+.2f}] |")
    lines+=['','![Local call values](jam-response-values.png)','',
        'AKs, AKo and AQs are material parts of LJ\'s entering range. They have clearly positive physical call values against the frozen UTG jam, while the current policy calls AKs only about half the time and almost always folds AKo/AQs. AJs also has positive counterfactual value, but almost never reaches this node in the saved policy. Do not equate every displayed hand\'s error with equal overall impact.','',
        'JJ remains near the boundary: its full-conditioning interval overlaps zero. QQ is slightly negative. Some class-cache estimates differ by around 1bb from the fresh physical-deal estimate; the cache cannot justify fine-grained recommendations near zero.','',
        '## Why the policies must adapt together','',
        'The exploratory analytic audit moves AA probability from UTG jam to call while preserving AA\'s total action probability and its 4-bet frequency. LJ\'s local best response changes substantially. Even before that transfer, recomputing a two-card-compatible local response changes AA\'s jam value from about 44.2bb against the saved response to about 75.1bb against that local response. This is not AA\'s equilibrium value: changing LJ\'s response creates incentives for other UTG hands to change too.','',
        'The local response calculation estimates a 2.83bb improvement for LJ conditional on this jam under its cached two-hand model. It is not a root exploitability estimate. The saved independent-class branch probability is only about 0.000381; physical branch probabilities and a full-game best response were not computed.','',
        '## Implementation consequence','',
        'Changing only the displayed equity or normalizing one terminal by compatible opponent mass is insufficient. A solver correction must use consistent card-conditioned chance weights in showdown values, fold payoffs, action aggregation and counterfactual updates. Otherwise it can create a different accounting error. A bounded two-player test game with independently enumerated compatible hand pairs is the appropriate next implementation gate, before modifying the multiway GPU solver.','',
        'This result does not establish that matching Wizard requires these exact responses: Wizard has different entering and jamming ranges. No production changes were made; reserved Wizard cases remain untouched.','']
    (s.OUT/'JAM-RESPONSES.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    print('Reviewed physical response audit',len(rows),'hands')


if __name__=='__main__':run()
