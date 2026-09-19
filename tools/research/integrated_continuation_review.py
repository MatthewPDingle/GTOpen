"""Independent physical root-chance audit and engineering-pilot report."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import wizard_continuation_study as s

OUT=s.OUT.parent/'integrated-continuation-20260919'
freeze=json.loads((OUT/'freeze.json').read_text(encoding='utf-8-sig'))
for path,digest in freeze['inputs'].items():assert s.sha(s.ROOT/path)==digest,path
support_freeze=json.loads((OUT/'supported-freeze.json').read_text(encoding='utf-8-sig'))
for path,digest in support_freeze['inputs'].items():assert s.sha(s.ROOT/path)==digest,path
pairs=[(a,b) for a in range(52) for b in range(a+1,52)]
masks=np.array([(1<<a)|(1<<b) for a,b in pairs],dtype=np.uint64)
classes=np.array([max(a//4,b//4)*13+min(a//4,b//4) if a%4==b%4 or a//4==b//4 else min(a//4,b//4)*13+max(a//4,b//4) for a,b in pairs])
multiplicity=np.bincount(classes,minlength=169)
data=s.read(s.OUT.parent/'conditional-hu-20260919/subtree.json')
w=np.array(data['incoming_class_mass'])[:,classes]/multiplicity[classes]
w/=w.max(1)[:,None]
compatible=(masks[:,None]&masks[None,:])==0
reviews=[]
fig,ax=plt.subplots(figsize=(8,4.5))
names=['river-pilot','turn-pilot','river-2000','turn-2000','supported-river-500','flop-smoke-20','flop-two-500','flop-two-2000']
for name in names:
    if not (OUT/(name+'.json')).exists():continue
    result=s.read(OUT/(name+'.json'));chance=np.zeros((1326,1326))
    for board in result['boards']:
        cards=['23456789TJQKA'.index(board[i])*4+'cdhs'.index(board[i+1]) for i in range(0,len(board),2)]
        assert len(set(cards))==len(cards)
        legal=(masks&np.uint64(sum(1<<c for c in cards)))==0
        chance+=compatible*legal[:,None]*legal[None,:]/len(result['boards'])
    untrimmed=chance*w[0,:,None]*w[1,None,:];untrimmed/=untrimmed.sum()
    weights=w.copy()
    if result.get('entry_cutoff'):
        weights[weights<result['entry_cutoff']]=0
    chance*=weights[0,:,None]*weights[1,None,:];z=chance.sum();chance/=z
    tv=float(abs(chance-untrimmed).sum()/2)
    full_deck=compatible*weights[0,:,None]*weights[1,None,:];full_deck/=full_deck.sum()
    panel_tv=float(abs(chance-full_deck).sum()/2)
    normalizer_error=abs(z-result['root_normalizer'])/z;assert normalizer_error<1e-7
    marginal=chance.sum(1);error=0.
    for row in result['records']:
        e=row['evaluation'];sigma=np.array(e['preflop_policy'][0]);assert abs(sigma.sum(0)-1).max()<1e-12
        error=max(error,float(abs(sigma@marginal-np.array(e['root_frequencies'])).max()))
        expected_class=np.bincount(classes,weights=marginal,minlength=169)
        error=max(error,float(abs(expected_class-np.array([h['root_mass'] for h in e['hands']])).max()))
        assert min(e['gaps'])>=-1e-6 and abs(e['terminal_probability']-1)<1e-5 and e['conservation_error']<1e-4
    assert error<1e-7
    last=result['records'][-1];reviews.append(dict(name=name,root_normalizer_relative_error=normalizer_error,
        physical_root_frequency_max_error=error,final_iteration=last['iteration'],final_gap_bb=last['evaluation']['gap_total'],
        maximum_conservation_error=max(r['evaluation']['conservation_error'] for r in result['records']),elapsed_seconds=last['elapsed_seconds'],
        entry_trimming_joint_total_variation=tv,fixed_policy_ev_change_bound_bb=403.5*tv,
        finite_panel_prior_tv_vs_full_deck=panel_tv))
    if name.endswith('2000'):
        previous=s.read(OUT/(name.replace('2000','500' if name.startswith('flop') else 'pilot')+'.json'))
        for a,b in zip(result['records'],previous['records']):assert a['evaluation']==b['evaluation'],'restart not reproducible'
        ax.loglog([r['iteration'] for r in result['records']],[r['evaluation']['gap_total'] for r in result['records']],marker='o',label=name.split('-')[0].title()+' panel')
ax.set(xlabel='Integrated CFR iterations',ylabel='Combined best-response gain (bb)',title='Connected-game engineering checks — limited board panels')
ax.grid(True,which='both',alpha=.2);ax.legend();fig.tight_layout();fig.savefig(OUT/'convergence.png',dpi=150);plt.close(fig)
s.write(OUT/'verification.json',dict(checks=reviews,note='Physical two-player combo enumeration. Not validation of full-deck preflop accuracy.',
    inputs={str(p.relative_to(s.ROOT)).replace('\\','/'):s.sha(p) for p in [OUT/(n+'.json') for n in names] if p.exists()}))
print(json.dumps(reviews,indent=2))
