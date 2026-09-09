"""Offline re-raise experiment. Never modifies the installed player library.

Regularized multinomial log-odds adjustments to the existing hand-aware model:
entry history, raise depth, continuous call price, commitment and seat. The
larger candidate also shares smooth hand/price effects instead of fitting 169
independent policies for every combination. Earlier tuning sessions select
strength/feature family; later sessions give RETROSPECTIVE diagnostics.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp, softmax

spec=importlib.util.spec_from_file_location('rer_sm',Path(__file__).with_name('smoothing.py'))
sm=importlib.util.module_from_spec(spec);spec.loader.exec_module(sm)
ROLES={'BB':-2,'SB':-1,'BTN':0,'CO':1,'HJ':2,'LJ':3,'UTG':4}
ENTRIES=['cold','called','raised']


def observations(sessions):
    rows=[];y=[];session=[]
    for i,s in enumerate(sessions):
        grouped={}
        for key,value in s['reraise_cells'].items():
            key,a=key.split('|')
            if key not in grouped:grouped[key]=np.zeros(3)
            grouped[key][['fold','call','raise'].index(a)]+=value
        for key,c in sorted(grouped.items()):
            n,pos,entry,depth,price,invested,remaining,h=key.split('/')
            rows.append([int(n),ROLES[pos],ENTRIES.index(entry),int(depth=='4betplus'),float(price),float(invested),float(remaining),int(h)])
            y.append(c);session.append(i)
    return np.array(rows),np.array(y),np.array(session)


def features(rows,family):
    n,r,e,d,p,invested,remaining,h=rows.T
    h=h.astype(int);e=e.astype(int)
    entry=np.eye(3)[e];seat=np.eye(7)[(r+2).astype(int)]
    price=(p-.3)/.15
    commit=invested/np.maximum(invested+remaining,1e-8)
    stack=(np.log1p(remaining)-np.log(101))/2
    base=[entry,entry*d[:,None],entry*price[:,None],entry*(price**2)[:,None],
          entry*commit[:,None],entry*stack[:,None],seat,(n-6)[:,None]/3]
    names=[f'{prefix}/{v}' for prefix in ['entry','depth','price','price2','commit','stack'] for v in ENTRIES]
    names += [f'seat/{v}' for v in range(-2,5)]+['players']
    if family=='hand_price':
        hi=sm.HI[h]/12;lo=sm.LO[h]/12;pair=(sm.TYPE[h]==0).astype(float);suited=(sm.TYPE[h]==1).astype(float)
        hand=np.column_stack([hi-.5,lo-.5,pair,suited,pair*(hi-.5),suited*(lo-.5)])
        hnames=['high','low','pair','suited','pair_rank','suited_low']
        for j,name in enumerate(ENTRIES):
            for modifier,tag in [(np.ones(len(rows)),'hand'),(price,'hand_price'),(d,'hand_depth')]:
                base.append(hand*(entry[:,j]*modifier)[:,None]);names += [f'{name}/{tag}/{v}' for v in hnames]
    return np.column_stack(base),names


def baseline(sessions,report):
    models={}
    for b in ['reraise','cold_reraise']:
        evidence=report['smoothing_validation']['buckets'][b];assert evidence['published']
        v=evidence['selected']
        models[b]=sm.fit(sm.merge(sm.collect(sessions,b)),v['alpha'],v['beta'],v['width'])
    return models


def base_probs(models,rows):
    return np.array([models[b][sm.closest(models[b],(int(n),int(r)))][int(h)]
        for n,r,e,d,p,i,s,h in rows for b in ['cold_reraise' if e==0 else 'reraise']])


def objective(v,x,y,offset,ridge):
    w=v.reshape(x.shape[1],2)
    logits=offset+np.column_stack([np.zeros(len(x)),x@w])
    logp=logits-logsumexp(logits,axis=1)[:,None]
    err=np.exp(logp)*y.sum(1)[:,None]-y
    return float(-(y*logp).sum()+.5*ridge*(w*w).sum()),(x.T@err[:,1:]+ridge*w).ravel()


def fit(x,y,p,ridge):
    offset=np.log(np.maximum(p,1e-12))
    opt=minimize(objective,np.zeros(x.shape[1]*2),args=(x,y,offset,ridge),jac=True,method='L-BFGS-B',
        options={'maxiter':1500,'ftol':1e-10,'gtol':1e-6})
    if not opt.success:raise RuntimeError(opt.message)
    return opt.x.reshape(x.shape[1],2)


def predict(x,p,w):
    return softmax(np.log(np.maximum(p,1e-12))+np.column_stack([np.zeros(len(x)),x@w]),axis=1)


def loss(y,p):return float(-(y*np.log(np.maximum(p,1e-12))).sum()/y.sum())


def metrics(y,old,new,sessions):
    oldll=-(y*np.log(np.maximum(old,1e-12))).sum(1);newll=-(y*np.log(np.maximum(new,1e-12))).sum(1)
    totals=np.array([[y[sessions==s].sum(),(oldll-newll)[sessions==s].sum()] for s in np.unique(sessions)])
    rng=np.random.default_rng(20260909);samples=[]
    for _ in range(2000):
        z=totals[rng.integers(len(totals),size=len(totals))].sum(0);samples.append(z[1]/z[0])
    return dict(decisions=int(y.sum()),sessions=len(totals),baseline_loss=loss(y,old),candidate_loss=loss(y,new),
        gain_interval=np.quantile(samples,[.025,.975]).tolist(),
        observed_call=float(y[:,1].sum()/y.sum()),baseline_call=float((old[:,1]*y.sum(1)).sum()/y.sum()),
        candidate_call=float((new[:,1]*y.sum(1)).sum()/y.sum()))


def run(source,out):
    data=json.loads(Path(source).read_text(encoding='utf-8'));out=Path(out);out.mkdir(parents=True,exist_ok=True)
    report=json.loads(Path('docs/ignition/NL10.json').read_text(encoding='utf-8'));assert data['audit']==report['audit']
    for session in data['sessions']:
        for entry,bucket in [(True,'cold_reraise'),(False,'reraise')]:
            rows,counts,_=observations([session])
            actual=counts[(rows[:,2]==0)==entry].sum() if len(rows) else 0
            expected=sum(v for k,v in session['policy_cells'].items() if k.startswith(bucket+'/'))
            assert actual==expected,'Detailed collection changed the decision denominator'
    s=report['splits'];sessions=data['sessions']
    tr=[x for x in sessions if x['last']<s['tune_from']]
    tu=[x for x in sessions if x['first']>=s['tune_from'] and x['last']<s['test_from']]
    te=[x for x in sessions if x['first']>=s['test_from']]
    rows,y,_=observations(tr);trows,ty,_=observations(tu);erows,ey,es=observations(te)
    model=baseline(tr,report);p=base_probs(model,rows);tp=base_probs(model,trows)
    candidates=[]
    # Fixed family/grid: do not expand after reading the later diagnostics.
    for family in ['context','hand_price']:
        x,names=features(rows,family);tx,_=features(trows,family)
        for ridge in [1.,10.,100.,1000.]:
            w=fit(x,y,p,ridge);z=dict(family=family,ridge=ridge,tuning_loss=loss(ty,predict(tx,tp,w)))
            candidates.append(z);print(json.dumps(z),flush=True)
    best=min(candidates,key=lambda z:z['tuning_loss'])
    rows,y,_=observations(tr+tu);model=baseline(tr+tu,report);p=base_probs(model,rows);old=base_probs(model,erows)
    x,names=features(rows,best['family']);ex,_=features(erows,best['family']);w=fit(x,y,p,best['ridge']);new=predict(ex,old,w)
    masks={'all':np.ones(len(erows),bool),'after_entry':erows[:,2]!=0,'cold':erows[:,2]==0}
    for i,entry in enumerate(ENTRIES):
        for depth in [0,1]:masks[f'{entry}/{"3bet" if not depth else "4betplus"}']=(erows[:,2]==i)&(erows[:,3]==depth)
    for role in range(-2,5):masks[f'role/{role}']=erows[:,1]==role
    for group,mask in sm.GROUPS.items():masks['hand/'+group]=mask[erows[:,7].astype(int)]
    masks['weak_offsuit']=(sm.TYPE[erows[:,7].astype(int)]==2)&(sm.HI[erows[:,7].astype(int)]<9)
    for name,mask in list(masks.items()):
        if name.startswith(('hand/','role/')) or name=='weak_offsuit':masks['entered/'+name]=mask&(erows[:,2]!=0)
    gate_names=list(masks)
    # Exploratory diagnostics requested after the first result; never used to
    # expand the candidate grid or choose its regularization.
    for name,mask in [('low',erows[:,4]<=.15),('middle',(erows[:,4]>.15)&(erows[:,4]<=.3)),('high',erows[:,4]>.3)]:
        masks['price/'+name]=mask;masks['entered/price/'+name]=mask&(erows[:,2]!=0)
    direct={b:sm.merge(sm.collect(tr+tu,b)) for b in ['reraise','cold_reraise']}
    support=np.array([direct[b].get((int(n),int(r)),np.zeros((169,3)))[int(h)].sum()
        for n,r,e,d,p,i,s,h in erows for b in ['cold_reraise' if e==0 else 'reraise']])
    for name,mask in [('none',support==0),('1-4',(support>0)&(support<5)),('5+',support>=5)]:
        masks['direct_support/'+name]=mask
    summary={name:metrics(ey[mask],old[mask],new[mask],es[mask]) for name,mask in masks.items() if mask.any()}
    promising=summary['all']['gain_interval'][0]>0 and summary['after_entry']['candidate_loss']<summary['after_entry']['baseline_loss'] and all(v['gain_interval'][1]>=0 for k,v in summary.items() if k in gate_names and v['decisions']>=30)
    evidence=dict(retrospective=True,installed=False,audit=data['audit'],splits=s,
        split_sessions=dict(train=len(tr),tune=len(tu),later=len(te),excluded_boundary=len(sessions)-len(tr)-len(tu)-len(te)),
        split_decisions=dict(train=int(observations(tr)[1].sum()),tune=int(ty.sum()),later=int(ey.sum())),
        candidate_grid=candidates,selected=best,metrics=summary,promising=promising,exploratory_groups=[k for k in masks if k not in gate_names],
        gate='Positive overall 95% session-bootstrap gain, lower after-entry mean loss, no clearly negative interval in reported subgroups with >=30 decisions. Not proof of noninferiority.',
        limitations=['Previously inspected periods: retrospective development, not fresh validation.',
            'Entry history means ever raised / called only / cold; prices are capped nominal call shares, not side-pot-adjusted pot odds.',
            'Positions/stacks/opponents remain sparse; no extrapolation validation beyond source conditions.',
            'Frozen baseline strengths were chosen in earlier retrospective work. Baseline hand counts are refitted only on training sessions.',
            'No solver/UI integration: prototype requires contextual runtime inputs. Production policies are unchanged.'])
    (out/'experiment.json').write_text(json.dumps(evidence,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    final=baseline(sessions,report);frows,fy,_=observations(sessions);fx,_=features(frows,best['family']);fw=fit(fx,fy,base_probs(final,frows),best['ridge'])
    artifact=dict(prototype=True,selected=best,features=names,weights=fw.tolist(),
        baseline={b:[dict(players=k[0],role=k[1],probabilities=v.tolist()) for k,v in m.items()] for b,m in final.items()})
    (out/'candidate.json').write_text(json.dumps(artifact,separators=(',',':'),allow_nan=False)+'\n',encoding='utf-8')
    # Concrete diagnostic: same HJ hand/entry/depth/stack at three nominal prices.
    examples=[]
    for label,h in [('AA',168),('QQ',140),('AKs',167),('72o',5),('32o',1),('J4o',35)]:
        for price in [.15,.3,.45]:
            row=np.array([[6,2,2,0,price,2.5,97.5,h]]);p=base_probs(final,row)
            q=predict(features(row,best['family'])[0],p,fw)
            examples.append(dict(hand=label,price=price,baseline_call=float(p[0,1]),candidate_call=float(q[0,1]),candidate_raise=float(q[0,2])))
    (out/'examples.json').write_text(json.dumps(examples,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(selected=best,promising=promising,metrics=summary),indent=2),flush=True)
    write_report(out,evidence,examples)


def write_report(out,evidence,examples):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    groups=[('all','All re-raises'),('after_entry','After prior entry'),('cold','Cold defense'),('entered/weak_offsuit','Entered weak offsuit')]
    m=evidence['metrics'];fig,(ax,bx)=plt.subplots(1,2,figsize=(12,4.6),layout='constrained')
    y=np.arange(len(groups));ax.barh(y-.18,[m[k]['baseline_loss'] for k,_ in groups],.34,color='#818c9b',label='Current model')
    ax.barh(y+.18,[m[k]['candidate_loss'] for k,_ in groups],.34,color='#4c916b',label='Contextual candidate')
    ax.set_yticks(y,[f'{label} (n={m[k]["decisions"]:,})' for k,label in groups]);ax.invert_yaxis()
    ax.set_xlabel('Later-session log loss (lower is better)');ax.set_title('Retrospective prediction comparison');ax.legend(frameon=False)
    for hand,color in [('72o','#be604b'),('32o','#557bb0')]:
        rows=[x for x in examples if x['hand']==hand];x=[r['price']*100 for r in rows]
        bx.plot(x,[r['candidate_call']*100 for r in rows],marker='o',color=color,label=f'{hand} candidate')
        bx.plot(x,[r['baseline_call']*100 for r in rows],linestyle='--',color=color,alpha=.65,label=f'{hand} current')
    bx.set_xlabel('Nominal call price (%)');bx.set_ylabel('Conditional call frequency (%)');bx.set_ylim(0,100)
    bx.set_title('Illustrative HJ response after raising\nSparse weak-hand estimates, not observations',fontsize=10);bx.legend(frameon=False,fontsize=8)
    for a in [ax,bx]:a.spines[['top','right']].set_visible(False)
    fig.savefig(out/'comparison.png',dpi=160);plt.close(fig)
    rows='\n'.join(f"| {label} | {m[k]['decisions']:,} | {m[k]['baseline_loss']:.4f} | {m[k]['candidate_loss']:.4f} | {100*(1-m[k]['candidate_loss']/m[k]['baseline_loss']):.1f}% |" for k,label in groups)
    text='''# Contextual re-raise experiment — 9 September 2026

**Frozen offline experiment; now available separately as Contextual v1.** See
[runtime integration and coverage](../../docs/contextual_preflop.md). This page
and `experiment.json` record the retrospective experiment before integration;
existing profiles and saved games are not converted. Lower log loss means
better probability predictions, not an equivalent increase in win rate or
classification accuracy.

| Comparison | Later decisions | Current log loss | Candidate log loss | Reduction |
|---|---:|---:|---:|---:|
'''+rows+'''

![Prediction comparison and illustrative price response](comparison.png)

## Model and evaluation

The candidate adds regularized multinomial log-odds adjustments to the current
hand-aware model. Inputs are cold/called-only/previously-raised entry, 3-bet
versus 4-bet+, continuous nominal call price, investment fraction, remaining
stack, position and table size. Shared hand-rank/family interactions allow
price and depth effects to differ between hands without separately estimating
every hand/position/price cell. There is no forced weak-hand fold rule.

The nominal price is the incremental call capped at the actor's remaining
stack, divided by the pot before acting plus that call. It is **not side-pot
adjusted pot odds**. Entry means whether the player has ever raised in the
hand; it does not encode every earlier action or opponent position.

The fixed search compared context-only and hand-interaction families at four
regularization strengths (1, 10, 100, 1000), selected on earlier tuning
sessions. The hand-interaction candidate at strength 1 won. Baseline hand
counts were also refitted only on training data. The chronology is 331 training,
137 tuning and 83 later sessions; four boundary-crossing sessions are excluded.
There are 6,981 / 2,979 / 2,351 re-raise decisions in those splits; 80 later
sessions contain relevant decisions. The final prototype is refitted on the
full source only after evaluation.

This reuses periods already inspected in earlier development. The baseline's
smoothing strengths also come from that earlier work. It is a **retrospective
comparison, not fresh independent validation**. The JSON records the entire
candidate grid and 2,000-resample session-bootstrap intervals. Price/support
subgroups were added as exploratory diagnostics after the first result; they
did not change candidate selection.

## Findings and limits

- Overall mean log-loss gain: 0.0496, with a 95% session-bootstrap interval
  of 0.0382–0.0606. After-entry gain: 0.0852 (0.0635–0.1059).
- All four after-entry groups (prior call/raise × 3-bet/4-bet+) improved on
  these sessions. All reported subgroups with at least 30 decisions passed
  the screen against clearly negative improvement intervals; that does not
  establish noninferiority everywhere or account for multiple comparisons.
- The HJ after-entry subgroup has 290 later observations and its improvement
  interval includes zero. Cold 4-bet+ has only 18 later observations. These
  remain uncertain rather than independently validated position policies.
- Low/middle/high price groups and hands with zero direct position-specific
  training observations improved in exploratory checks. The low-price group
  has just 36 later decisions.
- At an illustrative six-handed HJ state (previously raised to 2.5bb, 97.5bb
  remaining, facing a 3-bet), 72o's old 40.8% call becomes 37.9% at price 30%
  and 8.4% at price 45%. These individual hand estimates are not validated
  observations. At price 15% it still predicts 91.7% calls: rare loose entries
  and cheap calls are not made realistic simply by forcing all weak hands out.

## Artifacts and next integration step

- `experiment.json`: selection, metrics, bootstrap intervals and limitations.
- `candidate.json`: frozen feature order, coefficients and baseline matrices.
- `examples.json`: the illustrative hand predictions plotted above.

The candidate requires contextual inputs at each decision; it cannot correctly
replace a static Vs 3-bet+ grid. The separate versioned integration supplies
runtime entry/depth/price, supported-format checks, legal-action mapping and
context controls in the preview. Integration checks and runtime costs are
tracked in the [development record](../preflop-evolution/README.md), separately
from the predictive results here.

Reproduce from the private validated source:

```powershell
python tools/ignition/analyze.py --source 'T:\\Dev\\Poker Data\\Ignition' --out output/ignition-contextual-reraise
python tools/ignition/contextual_reraise.py --input output/ignition-contextual-reraise/analysis.json --out research/ignition-reraise
python -m unittest discover -s tools/ignition -p test_models.py
```

Only aggregate parameters and diagnostics are published; raw histories and
session-level observations stay local.
'''
    (out/'README.md').write_text(text,encoding='utf-8',newline='\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--out',required=True);a=p.parse_args();run(a.input,a.out)
