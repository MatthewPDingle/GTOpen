"""Independent reporting for the frozen coverage and folded-card experiments."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import json
import hashlib
import pathlib
import numpy as np
from scipy.stats import t
import integrated_coverage as c

OUT=c.OUT
def read(p):return json.loads(p.read_text())
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf8')
def interval(numer,denom):
    """Two paired ratio estimates from independent equal-sized batches."""
    numer=np.asarray(numer);denom=np.asarray(denom)
    mean=numer.sum(0)/denom.sum(0)
    influence=(numer-mean*denom)/denom.mean(0)
    delta=float(mean[1]-mean[0]);diff=influence[:,1]-influence[:,0]
    se=float(diff.std(ddof=1)/len(diff)**.5);half=float(t.ppf(.975,len(diff)-1)*se)
    return dict(control=float(mean[0]),folds=float(mean[1]),difference=delta,se=se,ci95=[delta-half,delta+half])

def folds():
    for p,h in read(OUT/'fold-freeze.json')['inputs'].items():
        assert hashlib.sha256((c.s.ROOT/p).read_bytes()).hexdigest()==h,p
    result=read(OUT/'fold-result.json');conf=read(OUT/'fold-config.json');assert result['config']==conf
    control=read(OUT/'fold-control-result.json')
    for b in control['batches']:
        assert b['sums'][0]==b['sums'][1]
        if b['class_mass'] is not None:assert b['class_mass'][0]==b['class_mass'][1] and b['board_mass'][0]==b['board_mass'][1]
    root=[b for b in result['batches'] if b['kind']==0]
    assert len(root)==conf['batches']
    denom=np.array([b['sums'] for b in root])[:,:,0]
    counts=np.array([b['class_mass'] for b in root])
    boards=np.array([b['board_mass'] for b in root])
    assert np.allclose(counts.sum(3),denom[:,:,None])
    assert np.allclose(boards[:,:,:13].sum(2),denom) and np.allclose(boards[:,:,13:].sum(2),denom)
    # Enumerate the exact collision-conditioned independent entry proposal.
    hist=read(c.s.OUT/'fold-history.json');policies={a['actor']:np.array(a['probabilities']) for a in hist['actions']}
    w=np.array([policies[p][c.CLASSES] for p in [1,2]])
    pair=w[0,:,None]*w[1,None,:]*((c.MASKS[:,None]&c.MASKS[None,:])==0);pair/=pair.sum()
    exact=np.array([np.bincount(c.CLASSES,weights=pair.sum(1-p),minlength=169) for p in [0,1]])
    estimates=counts[:,0].sum(0)/denom[:,0].sum()
    stderr=counts[:,0].std(0,ddof=1)/len(root)**.5/conf['root_draws_per_batch']
    # A simultaneous diagnostic with a conservative six-standard-error guard.
    z=np.abs(estimates-exact)/np.maximum(stderr,1e-8)
    supported=exact>1e-4
    assert z[supported].max()<6,('entry proposal mismatch',z.max())
    labels=[]
    for i in range(169):
        a,b=divmod(i,13);hi,lo=max(a,b),min(a,b)
        labels.append('23456789TJQKA'[hi]+'23456789TJQKA'[lo]+('' if a==b else 's' if a>b else 'o'))
    rows=[]
    for p in [0,1]:
        for cl in range(169):
            rows.append(dict(player=['UTG','LJ'][p],hand=labels[cl],**interval(counts[:,:,p,cl],denom)))
    board_rows=[dict(category=name,**interval(boards[:,:,i],denom)) for i,name in enumerate(list('23456789TJQKA')+['paired/two-tone','paired/rainbow','unpaired/monotone','unpaired/two-tone','unpaired/rainbow'])]
    probes=[]
    for k,p in enumerate(conf['probes'],1):
        bs=[b for b in result['batches'] if b['kind']==k];assert len(bs)==conf['batches']
        sums=np.array([b['sums'] for b in bs]);row=interval(sums[:,:,2],sums[:,:,0])
        ess=sums[:,:,0].sum(0)**2/sums[:,:,1].sum(0)
        probes.append(dict(hand=p['hand'],**row,effective_sample_sizes=ess.tolist()))
    sums=np.array([b['sums'] for b in root]);ess=sums[:,:,0].sum(0)**2/sums[:,:,1].sum(0)
    out=dict(probes=probes,class_shifts=rows,board_shifts=board_rows,root_effective_sample_sizes=ess.tolist(),
        entry_proposal_max_z=float(z[supported].max()),unit_control_passed=True,
        draws=conf['batches']*(conf['root_draws_per_batch']+len(conf['probes'])*conf['probe_draws_per_batch']),
        intervals='Pointwise paired batch-ratio 95% t intervals, not simultaneous coverage or strategic EV bounds')
    write(OUT/'fold-review.json',out)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,4))
    means=np.array([p['difference']*100 for p in probes]);ci=np.array([p['ci95'] for p in probes])*100
    ax.errorbar(means,np.arange(len(probes)),xerr=np.stack([means-ci[:,0],ci[:,1]-means]),fmt='o',color='#386b58',capsize=4)
    ax.set(yticks=np.arange(len(probes)),yticklabels=[p['hand'] for p in probes],xlabel='Equity change from six earlier folds (percentage points)',title='Physical folded-card effect vs the entering LJ range')
    ax.axvline(0,color='gray',linewidth=1);ax.grid(axis='x',alpha=.2);ax.invert_yaxis()
    fig.text(.12,.01,'34 million physical deals. Pointwise paired 95% intervals; not action EVs.',fontsize=9)
    fig.tight_layout(rect=(0,.045,1,1));fig.savefig(OUT/'fold-equity.png',dpi=160);plt.close(fig)
    print(json.dumps({k:v for k,v in out.items() if k not in ['class_shifts','board_shifts']},indent=2))

def report():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    panels=[]
    for name in ['old-two-orbits','panel-a','panel-b','panel-ab']:
        p=OUT/(name+'-result.json')
        if not p.exists() and name=='panel-a':p=OUT/'panel-a-interrupted-500.json'
        if not p.exists():continue
        r=read(p);e=r['records'][-1]['evaluation']
        panels.append(dict(panel=name,iteration=r['records'][-1]['iteration'],gap=e['gap_total'],
            frequencies=e['root_frequencies'],ev=e['ev'],hands={h['hand']:h['strategy'] for h in e['hands']},
            seconds=r['records'][-1].get('elapsed_seconds'),records=r['records']))
    print(json.dumps([{k:v for k,v in p.items() if k not in ['records','hands']}|{'AA':p['hands']['AA']} for p in panels],indent=2))
    fig,ax=plt.subplots(1,2,figsize=(11,4.4))
    for p in panels:
        ax[0].loglog([r['iteration'] for r in p['records']],[r['evaluation']['gap_total'] for r in p['records']],marker='o',label=p['panel'])
    ax[0].set(xlabel='Iterations',ylabel='Combined best-response gain (bb)',title='Convergence within each sampled game')
    ax[0].legend(fontsize=8);ax[0].grid(alpha=.2)
    x=np.arange(len(panels));bottom=np.zeros(len(panels))
    for i,(label,color) in enumerate(zip(['Fold','Call','4-bet','Jam'],['#597ab9','#75a66a','#d04f54','#824c9e'])):
        vals=np.array([p['frequencies'][i]*100 for p in panels]);ax[1].bar(x,vals,bottom=bottom,label=label,color=color);bottom+=vals
    ax[1].set(xticks=x,xticklabels=[p['panel']+'\n'+str(p['iteration'])+' iterations' for p in panels],ylim=(0,100),ylabel='Action frequency (%)',title='Root action mix at the shown checkpoint')
    ax[1].legend(fontsize=8);fig.tight_layout();fig.savefig(OUT/'coverage.png',dpi=160);plt.close(fig)
    write(OUT/'panel-summary.json',[{k:v for k,v in p.items() if k!='records'} for p in panels])

def controls():
    for p,h in read(OUT/'control-freeze.json')['inputs'].items():
        assert hashlib.sha256((c.s.ROOT/p).read_bytes()).hexdigest()==h,p
    rows=[];checks={}
    inputs=[('literal','50,75',OUT.parent/'integrated-continuation-20260919/flop-two-2000.json'),
        ('literal','50',OUT/'old-two-literal-half-result.json'),
        ('all suits','50',OUT/'old-two-orbits-result.json'),
        ('all suits','50,75',OUT/'old-two-orbits-two-sizes-result.json')]
    for suits,menu,path in inputs:
        d=read(path);last=d['records'][-1];assert last['iteration']==2000
        checks[path.name]=audit_result(d)
        e=last['evaluation'];assert e['conservation_error']<1e-4 and abs(e['terminal_probability']-1)<1e-5
        rows.append(dict(suits=suits,bet_menu=menu,gap=e['gap_total'],frequencies=e['root_frequencies'],
            AA=next(x['strategy'] for x in e['hands'] if x['hand']=='AA'),seconds=last['elapsed_seconds']))
    write(OUT/'control-summary.json',rows);write(OUT/'control-accounting.json',checks);print(json.dumps(rows,indent=2))

def audit_result(result):
    """Independent physical pair enumeration, including literal-board controls."""
    d=read(c.s.OUT.parent/'conditional-hu-20260919/subtree.json')
    w=np.array(d['incoming_class_mass'])[:,c.CLASSES]/c.COUNTS[c.CLASSES]
    w/=w.max(1)[:,None];w[w<1e-5]=0
    compatible=(c.MASKS[:,None]&c.MASKS[None,:])==0
    manifest=result.get('manifest',dict(suit_orbits=False,boards=[dict(board=b,weight=1) for b in result['boards']]))
    boards=manifest['boards'];perms=c.PERMS if manifest['suit_orbits'] else [(0,1,2,3)]
    denom=sum(b['weight'] for b in boards)*len(perms);chance=np.zeros_like(compatible,dtype=float)
    for b in boards:
        for perm in perms:
            cs=c.cards(c.relabel(b['board'],perm));legal=(c.MASKS&np.uint64(sum(1<<v for v in cs)))==0
            chance+=legal[:,None]*legal[None,:]*b['weight']/denom
    chance*=compatible*w[0,:,None]*w[1,None,:];z=chance.sum();marginal=chance.sum(1)/z
    normalizer_error=abs(result['root_normalizer']/z-1);assert normalizer_error<1e-7
    frequency_error=0.;class_error=0.;prob_error=0.;cash_error=0.
    for r in result['records']:
        e=r['evaluation'];sigma=np.array(e['preflop_policy'][0]);freq=sigma@marginal
        frequency_error=max(frequency_error,float(abs(freq-e['root_frequencies']).max()))
        prob_error=max(prob_error,abs(e['terminal_probability']-1))
        cash_error=max(cash_error,abs(sum(e['ev'])+e['expected_rake']-3.5))
        for cl,h in enumerate(e['hands']):
            sel=c.CLASSES==cl;den=marginal[sel].sum()
            class_error=max(class_error,abs(den-h['root_mass']))
            if den>0:class_error=max(class_error,float(abs(sigma[:,sel]@marginal[sel]/den-h['strategy']).max()))
        assert min(e['gaps'])>-1e-6
    assert frequency_error<1e-7 and class_error<1e-7 and prob_error<1e-5 and cash_error<1e-4
    return dict(normalizer_relative_error=float(normalizer_error),frequency_max_error=frequency_error,
        hand_summary_max_error=class_error,terminal_probability_max_error=prob_error,cash_conservation_max_error=cash_error)

def stability():
    """Compare policies using one common full-deck entry prior."""
    d=read(c.s.OUT.parent/'conditional-hu-20260919/subtree.json')
    w=np.array(d['incoming_class_mass'])[:,c.CLASSES]/c.COUNTS[c.CLASSES]
    w/=w.max(1)[:,None];w[w<1e-5]=0
    joint=w[0,:,None]*w[1,None,:]*((c.MASKS[:,None]&c.MASKS[None,:])==0)
    marginal=joint.sum(1)/joint.sum();prior=np.bincount(c.CLASSES,weights=marginal,minlength=169)
    policies={};rows=[]
    inputs=[(n,OUT/(n+'-result.json')) for n in ['old-two-orbits','panel-a','panel-b','panel-ab','old-two-literal-half','old-two-orbits-two-sizes']]
    inputs.append(('old-two-literal-two-sizes',OUT.parent/'integrated-continuation-20260919/flop-two-2000.json'))
    for name,path in inputs:
        r=read(path);last=r['records'][-1];assert last['iteration']==2000
        e=last['evaluation'];s=np.array(e['preflop_policy'][0]);policies[name]=s
        aa_indices=np.flatnonzero(c.CLASSES==168)
        aa={''.join('23456789TJQKA'[v//4]+'cdhs'[v%4] for v in c.PAIRS[i]):s[:,i].tolist() for i in aa_indices}
        rows.append(dict(panel=name,standardized_frequencies=(s@marginal).tolist(),original_frequencies=e['root_frequencies'],
            gap=e['gap_total'],AA_combos=aa,AA_call_spread=float(np.ptp(s[1,aa_indices]))))
    comparisons=[]
    for a,b in [('panel-a','panel-b'),('panel-a','panel-ab'),('panel-b','panel-ab'),
        ('old-two-literal-two-sizes','old-two-literal-half'),('old-two-literal-two-sizes','old-two-orbits-two-sizes'),
        ('old-two-literal-half','old-two-orbits'),('old-two-orbits','old-two-orbits-two-sizes')]:
        diff=np.abs(policies[a]-policies[b]).sum(0)/2
        by_class=np.bincount(c.CLASSES,weights=diff*marginal,minlength=169)
        active=np.flatnonzero(prior>1e-4)
        top=sorted(active,key=lambda cl:by_class[cl],reverse=True)[:12]
        def label(cl):
            a,b=divmod(int(cl),13);return '23456789TJQKA'[max(a,b)]+'23456789TJQKA'[min(a,b)]+('' if a==b else 's' if a>b else 'o')
        comparisons.append(dict(a=a,b=b,prior_weighted_policy_tv=float(diff@marginal),
            standardized_frequency_delta=((policies[b]-policies[a])@marginal).tolist(),
            largest_contributions=[dict(hand=label(cl),prior=float(prior[cl]),policy_tv=float(by_class[cl]/prior[cl]),weighted_contribution=float(by_class[cl])) for cl in top]))
    # Re-running after interruption must reproduce completed evaluations, apart
    # from wall-clock timing and the later checkpoints that did not exist yet.
    original=read(OUT/'panel-a-interrupted-500.json')['records'];repeat=read(OUT/'panel-a-result.json')['records']
    assert all(x['evaluation']==y['evaluation'] for x,y in zip(original,repeat))
    result=dict(common_prior='Exact full-deck two-player entry prior, same 1e-5 support cutoff; earlier folds omitted.',
        rows=rows,comparisons=comparisons,restart_reproduced=True,
        note='Policy sensitivity, not error versus poker ground truth. Different small games may legitimately have different equilibria.')
    write(OUT/'policy-stability.json',result)
    print(json.dumps([{k:v for k,v in row.items() if k!='largest_contributions'} for row in comparisons],indent=2))

def summary():
    panels=read(OUT/'panel-summary.json');controls_data=read(OUT/'control-summary.json');st=read(OUT/'policy-stability.json')
    assert len(panels)==4 and all(p['iteration']==2000 for p in panels)
    text=['# Completed board-coverage comparison','',
        'All prescribed development solves and both additional controls reached 2,000 iterations. '
        'The numerical accounting checks pass, but these small board panels produce materially different ranges. '
        'They are research games, not a deployment candidate or a validated match to GTO Wizard.','',
        '## Connected-game results','',
        'Same fixed UTG/LJ entry policies, original investments, 4% rake capped at 6 bb, and both called postflop branches. '
        'The four rows below use 50% bets and pot raises. All legal turn and river cards are included. '
        'Earlier folded-card information is still omitted from these solves.','',
        '| Board panel | Fold | Call | 4-bet | Jam | Combined deviation gain (bb) | Time (s) |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for p in panels:
        f=p['frequencies'];text.append(f"| {p['panel']} | {f[0]*100:.2f}% | {f[1]*100:.2f}% | {f[2]*100:.2f}% | {f[3]*100:.3f}% | {p['gap']:.6f} | {p['seconds']:.1f} |")
    comparison=next(x for x in st['comparisons'] if x['a']=='panel-a' and x['b']=='panel-b')
    text+=['','Times are observed research-run wall times, not an isolated performance benchmark.',
        '',f"Using one common full-deck entry prior, A versus B has {comparison['prior_weighted_policy_tv']*100:.2f}% prior-weighted policy total variation. "
        'This measures action-probability redistribution across hands, not the percentage of hands with any difference. '
        '66 is almost all fold in A and all call in B; 88 moves the other way. The restarted A run reproduced every saved checkpoint exactly.',
        '', '![Convergence and root frequencies](coverage.png)','', '## Why the board sample is not adequate','',
        'The ten-board game has no seven on any flop, so 77 cannot flop a set. '
        '99 gets a matching flop card about 43% of the time, versus roughly 12% with the full deck and this entering opposing range. '
        'The full-deck enumeration agrees with an independent remaining-card combinatorial calculation to below 7e-16. '
        'A small private-prior distance therefore cannot substitute for checking actual hand-making opportunities.',
        '', '![Pocket-pair opportunities](flop-structure.png)','',
        'The existing 47/95/184 report subsets reduce the worst pocket-pair opportunity error to 4.28/2.90/3.24 percentage points, '
        'respectively, versus 31.40 points for the ten-board development panel. Those are chance-only checks; no connected strategies '
        'for the report subsets were solved in this batch. Bigger samples do not guarantee monotonic improvement for every feature.',
        '', '## AA controls: separate suit coverage from bet sizes','',
        '| Suit treatment | Postflop bet menu | AA call | AA 4-bet | AA jam | Combined gain (bb) |',
        '|---|---|---:|---:|---:|---:|']
    for row in controls_data:
        menu=' / '.join(x+'%' for x in row['bet_menu'].split(','))
        a=row['AA'];text.append(f"| {row['suits']} | {menu} | {a[1]*100:.3f}% | {a[2]*100:.3f}% | {a[3]*100:.5f}% | {row['gap']:.6f} |")
    text+=['','These controls keep the two board ranks fixed. Literal-board games contain only the announced suit arrangements; '
        'the orbit games include every suit relabeling. Neither has comprehensive rank coverage. '
        'The comparison explains sensitivity inside these small games; it does not establish how AA should be played in the full game.',
        '', '## Validation and next gate','',
        '- Physical private-card enumeration reproduces root normalizers, action frequencies and hand summaries. '
        'A separate terminal traversal verifies total probability and player EVs plus rake.',
        '- The suit-orbit river comparison matches 24 explicit copies through 100 iterations within 4.4e-7 bb.',
        '- The independent folded-card audit remains unchanged; its simulation policies came from the frozen saved game, not new observed player hands.',
        '- No production code was changed or deployed. The user session on 56708 was preserved. Reserved boards and Wizard validation outcomes were not solved or used to tune strategies.',
        '', 'Next: validate the existing future-card symmetry compression for the restricted external-reach interface, '
        'then test processing a more representative board set in groups. The allocation estimate drops from 17.558 to 12.209 GB '
        'for this ten-board game, excluding overhead, but correctness and runtime still need to be tested. '
        'See [the scaling plan](SCALING.md) for the guard conditions and larger-board feasibility gate.',
        '', 'Detailed measurements: [accounting](coverage-audit.json), [control accounting](control-accounting.json), '
        '[policy sensitivity](policy-stability.json), [sampling audit](sampling-audit.json), '
        '[flop structure](flop-structure.json), and [memory plan](future-card-memory.json).','']
    (OUT/'RESULTS.md').write_text('\n'.join(text),encoding='utf8')

if __name__=='__main__':
    import sys
    if sys.argv[1]=='folds':folds()
    elif sys.argv[1]=='report':report()
    elif sys.argv[1]=='controls':controls()
    elif sys.argv[1]=='stability':stability()
    elif sys.argv[1]=='summary':summary()
    else:raise ValueError(sys.argv[1])
