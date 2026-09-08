"""Fit and validate compact site/stake models from analyze.py counters.

Publication contains pooled observations only, never account identifiers.
Temporal holdout: last 14 calendar days. Selection also withholds 20% of
player identities from centroid fitting and parameter estimation.
"""
import os
os.environ.setdefault('OMP_NUM_THREADS','4')
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
import argparse, collections, json, math
from pathlib import Path
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor, export_text
import context

FEATURES = [('vpip','yes'),('pfr','yes'),('pre/open','call'),('pre/open','raise'),
            ('pre/limps','call'),('pre/raise','raise'),('pre/squeeze','raise'),
            ('pre/3bet_raiser','fold'),('post/flop/initiative','bet'),
            ('post/flop/facing','fold'),('post/turn/facing','fold')]
PREDICT = {
    **{f'pre/{k}':['fold','call','raise'] for k in ['open','limps','raise','squeeze','limped_raise','3bet_raiser']},
    **{f'post/{st}/{kind}':(['fold','call','raise'] if kind=='facing' else ['check','bet'])
       for st in ['flop','turn','river'] for kind in ['initiative','no_initiative','facing']},
}
MIN_HANDS = 100
PRIOR = 100.0

class Grouping:
    """A reusable classifier; training never receives validation-player rows."""
    def __init__(self,family,k,frozen_mapping=None):
        self.family,self.k=family,k
        self.frozen_mapping=frozen_mapping

    @staticmethod
    def bands(X):
        return np.array([0 if v<.14 else (1 if v<.24 else 3 if v<.48 else 5)+int(p>=(.5 if v>=.48 else .6)*v) for v,p in X[:,:2]])

    def fit(self,X,Y,weights):
        self.scaler=StandardScaler().fit(X)
        Z=self.scaler.transform(X)
        if self.family=='kmeans':
            self.model=KMeans(n_clusters=self.k,n_init=20,random_state=20260908).fit(Z)
            self.labels_=self.model.labels_
        elif self.family=='tree':
            self.model=DecisionTreeRegressor(max_leaf_nodes=self.k,min_samples_leaf=30,random_state=20260908).fit(X,Y,sample_weight=weights)
            self.leaves=sorted(set(self.model.apply(X)))
            self.labels_=np.searchsorted(self.leaves,self.model.apply(X))
        else:
            original=self.bands(X)
            mapping=np.array(self.frozen_mapping) if self.frozen_mapping is not None else np.arange(7)
            labels=mapping[original]
            # Rare historical bins are merged, not sold as well-measured types.
            while self.frozen_mapping is None:
                ids,counts=np.unique(labels,return_counts=True)
                small=[j for j,nj in zip(ids,counts) if nj<30]
                if not small: break
                j=small[0]
                others=[i for i in ids if i!=j]
                target=min(others,key=lambda i:float(np.square(Z[labels==j].mean(0)-Z[labels==i].mean(0)).sum()))
                labels[labels==j]=target; mapping[mapping==j]=target
            if self.frozen_mapping is None:
                prototypes=[(.10,.07),(.19,.06),(.19,.15),(.35,.12),(.35,.27),(.65,.12),(.65,.42)]
                for j in range(7):
                    if mapping[j] not in set(labels):
                        target=min(set(labels),key=lambda i:float(np.square(X[labels==i,:2].mean(0)-prototypes[j]).sum()))
                        mapping[j]=target
            self.band_ids=sorted(set(labels)); self.mapping=mapping
            self.labels_=np.searchsorted(self.band_ids,labels)
        self.count=len(set(self.labels_))
        return self

    def predict(self,X):
        X=np.asarray(X)
        if self.family=='kmeans': return self.model.predict(self.scaler.transform(X))
        if self.family=='tree': return np.searchsorted(self.leaves,self.model.apply(X))
        return np.searchsorted(self.band_ids,self.mapping[self.bands(X)])

def targets(c,prior):
    # Squared-error tree proxy emphasizes common decision situations while
    # selection still uses proper held-out multinomial log loss.
    probs=distributions(c,prior)
    total=sum(n(prior,key) for key in PREDICT)
    return np.concatenate([probs[key]*math.sqrt(n(prior,key)/max(1,total)) for key in PREDICT])

def observations(c,key):
    prefix=key+'|'
    return {k[len(prefix):]:v for k,v in c.items() if k.startswith(prefix)}

def n(c,key): return sum(observations(c,key).values())

def fraction(c,key,out,prior=None,strength=0):
    outs=[out] if isinstance(out,str) else out
    count=sum(c.get(key+'|'+o,0) for o in outs)
    den=n(c,key)
    base=sum(prior.get(key+'|'+o,0) for o in outs)/max(1,n(prior,key)) if prior else 0
    return (count+strength*base)/(den+strength) if den+strength else 0

def merge(cs):
    out=collections.Counter()
    for c in cs: out.update(c)
    return out

def features(c,prior):
    return [fraction(c,key,out,prior,50 if key in ('vpip','pfr') else 25) for key,out in FEATURES]

def distributions(c,prior):
    result={}
    for key,outs in PREDICT.items():
        # Jeffreys smoothing gives even unseen pool outcomes finite probability.
        p=np.array([prior.get(key+'|'+o,0)+.5 for o in outs],float)
        p/=p.sum()
        values=np.array([c.get(key+'|'+o,0) for o in outs],float)+PRIOR*p
        result[key]=values/values.sum()
    return result

def loss(c,probs):
    value,den=0.0,0
    for key,outs in PREDICT.items():
        values=np.array([c.get(key+'|'+o,0) for o in outs])
        value-=float(values@np.log(np.maximum(probs[key],1e-9)))
        den+=int(values.sum())
    return value,den

def bootstrap_player_delta(rows):
    # Cluster bootstrap: observations from the same player are not independent.
    a=np.array(rows,float)
    if len(a)<30: return None
    rng=np.random.default_rng(20260908)
    vals=[]
    for _ in range(500):
        b=a[rng.integers(0,len(a),len(a))]
        vals.append(b[:,0].sum()/max(1,b[:,1].sum()))
    return [float(x) for x in np.quantile(vals,[.025,.975])]

def choose_k(players):
    ids=[p for p,c in sorted(players.items()) if n(c[0],'vpip')>=MIN_HANDS]
    fitids=[p for p in ids if int(p[:8],16)%5!=0]
    valids=[p for p in ids if int(p[:8],16)%5==0 and n(players[p][1],'vpip')>=30]
    if len(fitids)<200 or len(valids)<30: raise ValueError('Not enough independent players for model selection')
    prior=merge(players[p][0] for p in fitids)
    X=np.array([features(players[p][0],prior) for p in fitids])
    V=np.array([features(players[p][0],prior) for p in valids])
    Y=np.array([targets(players[p][0],prior) for p in fitids])
    weights=np.array([min(3000,n(players[p][0],'vpip')) for p in fitids])
    poolprob=distributions(prior,prior)
    base={p:loss(players[p][1],poolprob) for p in valids}
    baseline=sum(v[0] for v in base.values())/sum(v[1] for v in base.values())
    def old_type(c):
        v=100*fraction(c,'vpip','yes',prior,50); p=100*fraction(c,'pfr','yes',prior,50)
        if v<14: return 0
        return (1 if v<24 else 3 if v<48 else 5)+int(p>=(.5 if v>=48 else .6)*v)
    oldgroups=[merge(players[p][0] for p in fitids if old_type(players[p][0])==j) for j in range(7)]
    oldprobs=[distributions(c,prior) for c in oldgroups]
    oldloss=sum(loss(players[p][1],oldprobs[old_type(players[p][0])])[0] for p in valids)/sum(v[1] for v in base.values())
    candidates=[]
    specs=[('kmeans',k) for k in range(2,9)]+[('tree',k) for k in range(2,9)]+[('behavior_bands',7)]
    for family,requested in specs:
        km=Grouping(family,requested).fit(X,Y,weights)
        k=km.count
        members=np.bincount(km.labels_,minlength=k)
        if min(members)<30: continue
        cs=[merge(players[p][0] for p,l in zip(fitids,km.labels_) if l==j) for j in range(k)]
        probs=[distributions(c,prior) for c in cs]
        predicted=km.predict(V)
        rows=[]
        total=0.0; denom=0
        for p,l in zip(valids,predicted):
            value,den=loss(players[p][1],probs[l])
            total+=value; denom+=den
            rows.append((base[p][0]-value,den))
        ci=bootstrap_player_delta(rows)
        row=dict(family=family,k=k,requested_groups=requested,log_loss=total/denom,improvement_pct=100*(baseline-total/denom)/baseline,
                 player_bootstrap_gain_ci=ci,fit_members=[int(x) for x in members])
        if family=='behavior_bands': row['band_mapping']=[int(x) for x in km.mapping]
        candidates.append(row)
    supported=[r for r in candidates if r['player_bootstrap_gain_ci'] and r['player_bootstrap_gain_ci'][0]>0]
    if not supported: return 1,dict(baseline=baseline,fit_players=len(fitids),validation_players=len(valids),candidates=candidates,reason='No reliably positive holdout gain; publish pool only')
    best=min(r['log_loss'] for r in supported)
    # Prefer simpler groupings within 0.1% of pool log loss of the best score.
    chosen=min((r for r in supported if r['log_loss']<=best+.001*baseline),key=lambda r:(r['k'],r['log_loss']))
    return chosen['k'],dict(baseline=baseline,legacy_seven_bins_refit_log_loss=oldloss,fit_players=len(fitids),validation_players=len(valids),validation_opportunities=sum(v[1] for v in base.values()),candidates=candidates,selected_k=chosen['k'],selected_family=chosen['family'],requested_groups=chosen['requested_groups'],band_mapping=chosen.get('band_mapping'))

def make_model(stake,label,c,pool,source):
    adjustments=[]
    def rate(key,out): return round(100*fraction(c,key,out,pool,PRIOR),2)
    stats=dict(vpip=rate('vpip','yes'),pfr=rate('pfr','yes'),
               threebet=rate('pre/raise','raise'),squeeze=rate('pre/squeeze','raise'),
               fold_to_3bet=rate('pre/3bet_raiser','fold'),fourbet=rate('pre/3bet_raiser','raise'),
               open_raise=rate('pre/open','raise'),open_limp=rate('pre/open','call'),
               iso_raise=rate('pre/limps','raise'),limp_behind=rate('pre/limps','call'),
               cont_vs_raise=rate('pre/raise',['call','raise']),cont_squeeze=rate('pre/squeeze',['call','raise']),
               cont_vs_raise_limped=rate('pre/limped_raise',['call','raise']),
               flatten=0.0,raise_size='min')
    # Input percentages sometimes round to 100.01; preserve disjoint action sums.
    for a,b in [('open_raise','open_limp'),('iso_raise','limp_behind'),('fold_to_3bet','fourbet')]:
        if stats[a]+stats[b]>100: stats[b]=round(100-stats[a],2)
    bands=[]
    for bound in ['2.5','3.5','5','999']:
        key='size/raise/'+bound
        value=rate(key,['call','raise'])
        if value<stats['threebet']:
            adjustments.append(f'{bound}bb defense floored at overall 3-bet rate by current engine schema')
            value=stats['threebet']
        bands.append([float(bound),value])
    stats['cont_vs_raise_bands']=bands
    # GTOpen offers min/max menu choices, not an arbitrary measured size curve.
    # Use the empirical majority small/large band; disclose this approximation.
    opens=observations(c,'open_size')
    if sum(v for k,v in opens.items() if k in ['3.5','5','999'])>opens.get('2.5',0): stats['raise_size']='max'
    post=dict(cbet=[rate('post/'+s+'/initiative','bet') for s in ['flop','turn','river']],
              fold_to_bet=[rate('post/'+s+'/facing','fold') for s in ['flop','turn','river']],
              raise_bet=rate('post/all/facing','raise'),donk=rate('post/all/no_initiative','bet'),
              bet_size='max' if c.get('bet_size|large',0)>c.get('bet_size|small',0) else 'min')
    source={**source,'player_hands':n(c,'vpip'),'prior_opportunities':PRIOR,'engine_adjustments':adjustments,
            'assumptions':['Reference-ordered hand ranges; flatten=0 is a modeling assumption, not measured skill.',
                           'Position/stack details are retained in the study; current archetype inputs pool positions and stacks.',
                           'Raise/bet min/max choices approximate observed size bands and depend on the configured menu.',
                           'Ante-game measurements are not a validated no-ante or live-casino population.'],
            'opportunities':{key:n(c,key) for key in list(PREDICT)+['vpip','pfr']+['size/raise/'+b for b in ['2.5','3.5','5','999']]},
            'low_sample_fields':[key for key in PREDICT if n(c,key)<500]}
    note=(f"CoinPoker {stake} · {label}. HHDealer {source['date_from']}–{source['date_to']}; "
          f"7-max ante tables, 5–7 players dealt. {source['players']:,} player names / {source['player_hands']:,} player-hands. "
          f"VPIP/PFR/3-bet {stats['vpip']:.1f}/{stats['pfr']:.1f}/{stats['threebet']:.1f}%; "
          f"fold to flop bet {post['fold_to_bet'][0]:.1f}%. Opportunity-weighted, smoothed toward the stake pool. "
          "2025 sample; positions/stacks pooled. Hand-range ordering and size-menu mapping remain model assumptions. "
          + ("Sparse fields borrow pool estimates. " if source['low_sample_fields'] else '')
          + "Full sample counts and validation: docs/coinpoker_models.md.")
    return dict(name=f'Data · CoinPoker · {stake} · {label}',stats=stats,postflop=post,note=note,source=source)

def describe(c,pool):
    v=100*fraction(c,'vpip','yes'); p=100*fraction(c,'pfr','yes')
    ratio=p/max(v,.1)
    style='aggressive' if ratio>=.6 else 'passive' if ratio<.35 else 'mixed'
    if v<18: base='Tight-'+style
    elif v<30: base='TAG' if style=='aggressive' else 'Moderate-'+style
    elif v<48: base='LAG' if style=='aggressive' else 'Loose-'+style
    else: base='Very loose-'+style
    fold=100*fraction(c,'post/flop/facing','fold',pool,PRIOR)
    pf=100*fraction(pool,'post/flop/facing','fold')
    if fold<pf-7: base+=' · Sticky'
    elif fold>pf+7: base+=' · High-fold'
    return base

def fit_stake(path):
    data=json.loads(Path(path).read_text())
    if data['schema']!=2: raise ValueError('Rerun analyze.py: joint position/player-count counters (schema 2) are required')
    if data['audit'].get('duplicate_variant',0): raise ValueError('Resolve conflicting duplicate action records before fitting')
    stake=data['stake']; players=data['players']
    pool=merge(data['pool'])
    k,validation=choose_k(players)
    full={p:merge(cs) for p,cs in players.items()}
    trainids=[p for p,cs in sorted(players.items()) if n(cs[0],'vpip')>=MIN_HANDS]
    trainpool=merge(players[p][0] for p in trainids)
    source=dict(site='CoinPoker',stakes=stake,format='7-max ante / 5–7 dealt',date_from=min(data['dates']),date_to=max(data['dates']),
                unique_hands=data['audit']['accepted'],players=len(players),type='pool',version='2026-09-08-v1')
    source['version']='2026-09-08-v2'
    context_validation=context.select(players)
    models=[make_model(stake,'Pool',pool,pool,source)]
    models[0]['stats']['dataset']=context.export(pool,pool,context_validation)
    clusters=[]
    classifier=None
    if k>1:
        X=np.array([features(players[p][0],trainpool) for p in trainids])
        Y=np.array([targets(players[p][0],trainpool) for p in trainids])
        km=Grouping(validation['selected_family'],validation['requested_groups'],validation.get('band_mapping')).fit(X,Y,np.array([min(3000,n(players[p][0],'vpip')) for p in trainids]))
        k=km.count
        classifier=dict(family=km.family,features=[f'{a}:{b}' for a,b in FEATURES],smoothing_hands=50,smoothing_conditional=25,
                        training_prior_rates=features({},trainpool))
        if km.family=='tree':
            classifier['rules']=export_text(km.model,feature_names=classifier['features'],decimals=4)
            classifier['leaf_nodes']=[int(x) for x in km.leaves]
        elif km.family=='behavior_bands':
            classifier['band_mapping']=[int(x) for x in km.mapping]
            classifier['band_ids']=[int(x) for x in km.band_ids]
            classifier['bands']='0: VPIP<14; 1/2:14-24 passive/aggressive; 3/4:24-48; 5/6:48+. Aggressive=PFR/VPIP>=0.6 (>=0.5 for 48+). Rates smoothed before classification.'
        else: classifier['centroids']=km.scaler.inverse_transform(km.model.cluster_centers_).tolist()
        ids=[p for p,c in sorted(full.items()) if n(c,'vpip')>=MIN_HANDS]
        labels=km.predict(np.array([features(full[p],trainpool) for p in ids]))
        for j in range(k):
            members=[p for p,l in zip(ids,labels) if l==j]
            c=merge(full[p] for p in members)
            clusters.append(dict(label=describe(c,pool),members=len(members),counts=c,cluster=j))
        # Human names describe fitted groups; they do not determine membership.
        namecounts=collections.Counter(x['label'] for x in clusters)
        for cl in clusters:
            label=cl['label']
            if namecounts[label]>1:
                label+=f" · {100*fraction(cl['counts'],'vpip','yes'):.0f}/{100*fraction(cl['counts'],'pfr','yes'):.0f}"
            models.append(make_model(stake,label,cl['counts'],pool,{**source,'players':cl['members'],'type':validation['selected_family'],'cluster':cl['cluster']}))
            models[-1]['stats']['dataset']=context.export(cl['counts'],pool,context_validation)
        if len({m['name'] for m in models})!=len(models): raise ValueError('Ambiguous cluster labels')
    for m in models:
        m['stats']['dataset']['small_blind_bb']=.4 if stake=='NL25' else .5
        m['note']=m['note'].replace('2025 sample; positions/stacks pooled.', '2025 sample; entry frequencies fitted by position and player count, stacks pooled. Outside 5–7 players is extrapolation.')
        m['source']['assumptions'][1]='Position/player-count entry effects fitted from joint opportunities; other responses and stacks pooled. Outside 5–7 players is extrapolation.'
    # Aggregate measurements remain auditable without any individual identifiers.
    report=dict(stake=stake,audit=data['audit'],date_from=min(data['dates']),date_to=max(data['dates']),holdout_from=data['cutoff'],
                antes=data['antes'],occupancy=data['occupancy'],players=len(players),
                players_under100=sum(n(c,'vpip')<100 for c in full.values()),
                player_hands_under100=sum(n(c,'vpip') for c in full.values() if n(c,'vpip')<100),
                validation=validation,context_validation=context_validation,classifier=classifier,pool_counts=dict(pool),
                clusters=[dict(label=m['name'],counts=dict(cl['counts']),players=cl['members']) for m,cl in zip(models[1:],clusters)],
                models=models)
    return models,report

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input',required=True); ap.add_argument('--out',required=True)
    ap.add_argument('--publish',help='Explicit cache/archetypes.json to append/replace CoinPoker models only')
    args=ap.parse_args(); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    allmodels=[]
    for stake in ['NL10','NL25','NL50','NL100']:
        models,report=fit_stake(Path(args.input)/f'{stake}.json')
        (out/f'{stake}.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
        allmodels+=models
        print(f'{stake}: {len(models)} models; k={report["validation"].get("selected_k",1)}',flush=True)
    (out/'models.json').write_text(json.dumps(allmodels,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    if args.publish:
        path=Path(args.publish)
        old=json.loads(path.read_text(encoding='utf-8'))
        keep=[a for a in old if not a['name'].startswith('Data · CoinPoker · ')]
        temporary=path.with_suffix('.json.tmp')
        temporary.write_text(json.dumps(keep+allmodels,indent=1,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
        temporary.replace(path)

if __name__=='__main__': main()
