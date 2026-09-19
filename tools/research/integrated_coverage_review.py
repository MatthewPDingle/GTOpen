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
    rows=[]
    inputs=[('literal','50,75',OUT.parent/'integrated-continuation-20260919/flop-two-2000.json'),
        ('literal','50',OUT/'old-two-literal-half-result.json'),
        ('all suits','50',OUT/'old-two-orbits-result.json'),
        ('all suits','50,75',OUT/'old-two-orbits-two-sizes-result.json')]
    for suits,menu,path in inputs:
        d=read(path);last=d['records'][-1];assert last['iteration']==2000
        e=last['evaluation'];assert e['conservation_error']<1e-4 and abs(e['terminal_probability']-1)<1e-5
        rows.append(dict(suits=suits,bet_menu=menu,gap=e['gap_total'],frequencies=e['root_frequencies'],
            AA=next(x['strategy'] for x in e['hands'] if x['hand']=='AA'),seconds=last['elapsed_seconds']))
    write(OUT/'control-summary.json',rows);print(json.dumps(rows,indent=2))

if __name__=='__main__':
    import sys
    if sys.argv[1]=='folds':folds()
    elif sys.argv[1]=='report':report()
    elif sys.argv[1]=='controls':controls()
    else:raise ValueError(sys.argv[1])
