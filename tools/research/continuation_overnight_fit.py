"""Training-only model selection, then independent overnight evaluation."""
import collections
import json
import time

import numpy as np
import continuation_overnight as night
import range_value_pilot as pilot
from continuation_checkpoint import same_job


def load_cases(partition):
    m=night.checked_manifest();counts,eq=pilot.matrices()
    fixtures=json.loads((night.OUT/'fixtures.json').read_text())
    result=[]
    for case in fixtures['cases']:
        if case['partition']!=partition:continue
        rows=[]
        for j in m['jobs']:
            if j['case']!=case['id']:continue
            r=json.loads((night.OUT/'jobs'/f"{j['id']}.json").read_text())
            assert r['manifest_id']==m['id'] and same_job(r['job'],j) and r['target_met']
            rows.append(r)
        assert len(rows)==100
        c=pilot.context(case,counts,eq)
        residual,observed,unadjusted=pilot.aggregate(case,rows)
        c.update(case=case,residual=residual,observed=observed,unadjusted=unadjusted,rows=rows,base_x=c['x'].copy(),base_names=list(c['names']))
        result.append(c)
    return result


def distribution(c):
    d=np.array(c['case']['weights'])*pilot.COMBOS
    return d/d.sum(axis=1,keepdims=True)


def encoder(cases,kind):
    if kind=='shape':return dict(kind=kind)
    assert kind=='pca8'
    d=np.concatenate([distribution(c) for c in cases]);mean=d.mean(axis=0)
    _,_,basis=np.linalg.svd(d-mean,full_matrices=False)
    return dict(kind=kind,mean=mean.tolist(),basis=basis[:8].tolist())


def features(c,enc):
    d=distribution(c);x=c['base_x'];names=list(c['base_names'])
    columns=[]
    def add(name,v):
        columns.append(np.broadcast_to(v,(2,169)));names.append(name)
    summaries=[]
    for row in d:
        nz=row[row>0]
        summaries.append([
            float(-(nz*np.log(nz)).sum()/np.log(169)),float(1/(row@row)/169),float(row.max()),
            float(np.sort(row)[-3:].sum()),float(row[[a==b and a>=8 for a,b,_ in pilot.PARTS]].sum()),
            float(row[[a==b and a<8 for a,b,_ in pilot.PARTS]].sum()),
            float(row[[not s and a!=b and b>=8 for a,b,s in pilot.PARTS]].sum()),
            float(row[[s and a-b<=2 for a,b,s in pilot.PARTS]].sum())])
    summaries=np.array(summaries)
    pair=np.array([a==b for a,b,_ in pilot.PARTS]);suited=np.array([s for _,_,s in pilot.PARTS])
    for side,rows in [('own',summaries),('opp',summaries[::-1])]:
        for i,label in enumerate(['entropy','effective','maximum','top3','high_pairs','low_pairs','offsuit_broadway','suited_connected']):
            value=rows[:,i,None]
            add(side+'_'+label,value)
            add(side+'_'+label+'*equity',value*c['raw'])
            add(side+'_'+label+'*pair',value*pair)
    add('own_hand_mass',d)
    add('opponent_same_class_mass',d[::-1])
    for p in range(2):
        assert abs(d[p].sum()-1)<1e-12
    if enc['kind']=='pca8':
        pc=(d-np.array(enc['mean']))@np.array(enc['basis']).T
        for side,rows in [('own',pc),('opp',pc[::-1])]:
            for k in range(rows.shape[1]):
                v=rows[:,k,None]
                add(f'{side}_pc{k}',v)
                add(f'{side}_pc{k}*equity',v*c['raw'])
                add(f'{side}_pc{k}*pair',v*pair)
                add(f'{side}_pc{k}*suited',v*suited)
    return dict(c,x=np.concatenate([x,np.stack(columns,axis=-1)],axis=-1),names=names)


def fit(cases,kind,alpha):
    enc=encoder(cases,kind)
    encoded=[features(c,enc) for c in cases]
    model=pilot.fit_ridge(encoded,alpha)
    model.update(encoder=enc,feature_names=encoded[0]['names'])
    return model


def predict(c,model):
    encoded=features(c,model['encoder'])
    assert encoded['names']==model['feature_names']
    return pilot.predict(encoded,model)


def train():
    m=night.checked_manifest();cases=load_cases('train')
    assert len(cases)==24
    groups=sorted({c['case']['family'] for c in cases})
    scores=[]
    for kind in m['protocol']['candidates']:
        for alpha in m['protocol']['ridge']:
            details=[]
            for group in groups:
                fitted=fit([c for c in cases if c['case']['family']!=group],kind,alpha)
                for c in cases:
                    if c['case']['family']==group:
                        details.append(dict(case=c['case']['id'],family=group,**pilot.metrics(c,predict(c,fitted))))
            scores.append(dict(kind=kind,alpha=alpha,mae_pct_pot=float(np.mean([d['candidate'] for d in details])),cases=details))
            print('CV',kind,alpha,scores[-1]['mae_pct_pot'],flush=True)
    best=min(scores,key=lambda x:x['mae_pct_pot'])
    model=fit(cases,best['kind'],best['alpha'])
    model.update(schema=2,manifest_id=m['id'],production_enabled=False,training_case_ids=[c['case']['id'] for c in cases],
                 training_families=groups,label='Compatible-pair-weighted policy EV with preflop equity control variate; best-response values are quality diagnostics, not fitted labels.')
    night.dump(night.OUT/'candidate.json',model)
    night.dump(night.OUT/'cross-validation.json',dict(scores=scores,selected_kind=best['kind'],selected_alpha=best['alpha']))


def bootstrap(c,pred):
    rows=c['rows'];num=np.zeros((len(rows),2,169));den=np.zeros_like(num)
    groups=collections.defaultdict(list)
    for i,r in enumerate(rows):
        j=r['job'];groups[j['stratum']].append(i)
        for p in range(2):
            for h in r['hands'][p]:
                k=pilot.INDEX[h['hand']];w=j['iso_weight']/j['inclusion_probability']*h['pair_mass']
                den[i,p,k]=w;num[i,p,k]=w*(h['ev_bb']/c['case']['pot']-h['equity'])
    rng=np.random.default_rng(20260916);draws=np.zeros((500,len(rows)))
    for b in range(len(draws)):
        for ids in groups.values():
            for i in rng.choice(ids,len(ids)):draws[b,i]+=1
    bn=np.einsum('bi,iph->bph',draws,num);bd=np.einsum('bi,iph->bph',draws,den)
    target=c['raw']+np.divide(bn,bd,out=np.zeros_like(bn),where=bd>0)
    w=c['mass']*(bd>0);w/=w.sum(axis=(1,2),keepdims=True)
    errors={name:(w*np.abs(v-target)).sum(axis=(1,2))*100 for name,v in
            [('candidate',pred),('balanced',c['balanced']),('raw',c['raw'])]}
    return errors


def quality(c):
    den=np.zeros((2,169));num=np.zeros_like(den)
    for r in c['rows']:
        j=r['job']
        for p in range(2):
            for h in r['hands'][p]:
                if h['br_ev_bb'] is None:continue
                k=pilot.INDEX[h['hand']];w=j['iso_weight']/j['inclusion_probability']*h['pair_mass']
                den[p,k]+=w;num[p,k]+=w*max(0,h['br_ev_bb']-h['ev_bb'])/c['case']['pot']*100
    return np.divide(num,den,out=np.zeros_like(num),where=den>0)


def evaluate():
    m=night.checked_manifest();model=json.loads((night.OUT/'candidate.json').read_text())
    assert model['manifest_id']==m['id']
    cases=load_cases('test');assert len(cases)==8
    results=[];boot=[]
    for c in cases:
        pred=predict(c,model);err=bootstrap(c,pred);q=quality(c)
        target=c['raw']+c['residual'];probes=[]
        for p in range(2):
            for hand in night.PROBES:
                k=pilot.INDEX[hand]
                if c['observed'][p,k]<=0:continue
                probes.append(dict(player=p,hand=hand,candidate=float(pred[p,k]*20),balanced=float(c['balanced'][p,k]*20),
                    reference_cv=float(target[p,k]*20),reference_unadjusted=float(c['unadjusted'][p,k]*20),br_gain_pct_pot=float(q[p,k])))
        result=dict(case=c['case']['id'],family=c['case']['family'],spr=c['case']['stack']/20,
            mae_pct_pot=pilot.metrics(c,pred),paired_improvement_ci95_pct_pot={n:np.quantile(err[n]-err['candidate'],[.025,.975]).tolist() for n in ['balanced','raw']},
            probes=probes,mean_br_gain_pct_pot=float((q*c['mass']).sum()/2),max_probe_br_gain_pct_pot=max(p['br_gain_pct_pot'] for p in probes),
            reference_cv_pot_sum_pct=float((target*c['mass']).sum()*100),candidate_pot_sum_pct=float((pred*c['mass']).sum()*100))
        results.append(result);boot.append(err)
    families=[]
    for family in sorted({r['family'] for r in results}):
        ids=[i for i,r in enumerate(results) if r['family']==family]
        means={n:float(np.mean([results[i]['mae_pct_pot'][n] for i in ids])) for n in ['candidate','balanced','raw']}
        # Shared bootstrap board indices retain dependence across cases.
        errors={n:np.mean([boot[i][n] for i in ids],axis=0) for n in means}
        intervals={n:np.quantile(errors[n]-errors['candidate'],[.025,.975]).tolist() for n in ['balanced','raw']}
        families.append(dict(family=family,mae_pct_pot=means,paired_improvement_ci95_pct_pot=intervals,
            point_gate_passed=means['candidate']<=.85*min(means['balanced'],means['raw'])))
    passed=all(f['point_gate_passed'] for f in families)
    outcome=dict(manifest_id=m['id'],candidate_sha256=night.file_hash(night.OUT/'candidate.json'),families=families,cases=results,
        accuracy_screen_passed=passed,production_enabled=False,training_jobs=2400,test_jobs=800,
        note='Zero-rake HU continuation screen only. Confidence intervals condition on the fitted model and cached equity; training uncertainty is not included. Passing does not authorize deployment.')
    night.dump(night.OUT/'evaluation.json',outcome)
    plot(outcome)
    lines=['# Overnight continuation research results','',
        '**Accuracy screen: '+('passed; further validation required.' if passed else 'failed; do not deploy.')+'**','',
        'Completed 3,200 GPU postflop references: 24 training configurations on 100 training flops, '
        'and eight independent configurations on 100 separate test flops. Port 56708 was not modified.','',
        '| Independent source family | Balanced MAE | Raw-equity MAE | Candidate MAE |',
        '|---|---:|---:|---:|']
    for f in families:
        e=f['mae_pct_pot'];lines.append(f"| {f['family']} | {e['balanced']:.2f} | {e['raw']:.2f} | {e['candidate']:.2f} |")
    lines+=['','MAE is per-hand continuation-value error as a percentage of the starting pot, '
        'weighted by compatible range mass and averaged equally across cases. These are not action frequencies or full-game exploitability.',
        '', '![Independent source-family errors](comparison.png)','',
        'Model selection used training families only. The held-out source games and boards were evaluated after the candidate was frozen. '
        'Cases derived from the same save, including perturbations, stayed in the same partition.',
        '', 'The reference labels are policy EVs with an equity control variate. Both-player per-hand best-response checks '
        'are included in evaluation.json; rare-hand labels with large BR gains need additional solving. '
        'Sampled flops, cached preflop equity, fixed postflop sizing and approximate source ranges remain limitations.',
        '', 'This run did not deploy a model or demonstrate faster preflop solving. A successful value screen must be followed '
        'by fresh-game decision checks and GPU time-to-target/memory measurements.',
        '', 'Details: [evaluation](evaluation.json), [cross-validation](cross-validation.json), '
        '[candidate](candidate.json), [protocol and jobs](manifest.json), [live run status](status.json).','']
    (night.OUT/'RESULTS.md').write_text('\n'.join(lines),encoding='utf-8')


def plot(outcome):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    families=outcome['families'];x=np.arange(len(families))
    fig,ax=plt.subplots(figsize=(9,5),layout='constrained')
    for offset,name,label,color in [(-.24,'balanced','Balanced','#888888'),(0,'raw','Raw equity','#357ca5'),(.24,'candidate','Learned candidate','#bd6735')]:
        values=[f['mae_pct_pot'][name] for f in families]
        bars=ax.bar(x+offset,values,.22,label=label,color=color)
        ax.bar_label(bars,fmt='%.2f',padding=3,fontsize=9)
    ax.set_xticks(x,[f['family'].replace('test-','').replace('-',' ') for f in families])
    ax.set_ylabel('Range-weighted hand MAE (% of starting pot)');ax.set_title('Independent source games and unseen flops')
    ax.legend();ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
    fig.supxlabel('Lower is better. Fixed 50% postflop bet menu, zero-rake heads-up.\nA continuation-value test, not a preflop strategy or speed benchmark.',fontsize=9)
    fig.savefig(night.OUT/'comparison.png',dpi=160);plt.close(fig)


if __name__=='__main__':
    import sys
    {'train':train,'evaluate':evaluate}[sys.argv[1]]()
