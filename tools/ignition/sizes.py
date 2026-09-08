"""Observed first-in non-all-in sizes, with chronological context-pooling checks.

Amounts remain in bb. Runtime projects this discrete distribution onto the
scenario's non-jam menu by nearest log distance. No probability is invented for
an unsupported menu size. Size is independent of hand conditional on raising.
"""
import collections, json, math
from pathlib import Path
import numpy as np
import importlib.util
spec=importlib.util.spec_from_file_location("opening_sizes_fit",Path(__file__).with_name("fit.py"))
opening=importlib.util.module_from_spec(spec);spec.loader.exec_module(opening)
closest=opening.closest
from context import ROLES


def counts(sessions):
    rows=collections.defaultdict(collections.Counter); jams=0
    for session in sessions:
        for key,value in session['counts'].items():
            if not key.startswith('opening_size/'):continue
            prefix,size=key.split('|');_,n,role=prefix.split('/')
            if size=='jam':jams+=value;continue
            rows[int(n),ROLES[role]][float(size)]+=value
    return dict(rows),jams


def fit(sessions,strength):
    rows,_=counts(sessions);pool=sum(rows.values(),collections.Counter());total=sum(pool.values())
    if not total:raise ValueError('No validated opening sizes')
    prior={size:v/total for size,v in pool.items()};result={}
    for key,row in rows.items():
        n=sum(row.values());result[key]={size:(row[size]+strength*p)/(n+strength) for size,p in prior.items()}
    return result,prior


def project(probabilities,menu):
    out=np.zeros(len(menu))
    for size,p in probabilities.items():
        i=min(range(len(menu)),key=lambda i:(abs(math.log(menu[i]/size)),menu[i]))
        out[i]+=p
    return out


def loss(sessions,model):
    policies,prior=model;total=loss=0
    # Fixed menu for diagnostics only. Production keeps exact observed sizes.
    menu=[2,2.5,3,5]
    for key,row in counts(sessions)[0].items():
        pred=project(policies[closest(policies,*key)] if policies else prior,menu)
        actual=project(row,menu);total+=actual.sum();loss-=float((actual*np.log(np.maximum(pred,1e-12))).sum())
    return float(loss/total),int(total)


def run(source,out,publish=False):
    data=json.loads(Path(source).read_text(encoding='utf-8'));ss=data['sessions']
    report=json.loads((Path(out)/'NL10.json').read_text(encoding='utf-8'));assert data['audit']==report['audit']
    train=[s for s in ss if s['last']<'2025-10-05']
    tune=[s for s in ss if s['first']>='2025-10-05' and s['last']<'2025-11-03']
    test=[s for s in ss if s['first']>='2025-11-03']
    candidates=[dict(strength=a,tuning_loss=loss(tune,fit(train,a))[0]) for a in [10,30,100,300,1000]]
    best=min(candidates,key=lambda x:x['tuning_loss']);trained=fit(train+tune,best['strength'])
    contextual,n=loss(test,trained);pooled,_=loss(test,({},trained[1]));legacy,_=loss(test,({}, {5.:1.}))
    # If positional sizing doesn't outperform pooling, publish pooled evidence.
    use_context=bool(contextual<pooled)
    final,prior=fit(ss,best['strength']);rows,jams=counts(ss)
    evidence=dict(retrospective=True,selection=candidates,selected=best,contextual_published=use_context,
        later_sessions=dict(openings=n,contextual_log_loss=contextual,pooled_log_loss=pooled,legacy_max_log_loss=legacy),
        nonjam_openings=sum(sum(r.values()) for r in rows.values()),excluded_open_jams=jams,
        assumptions=['Non-jam first-in opens only; iso-raises and re-raises retain existing rules.',
          'Size independent of hand conditional on ordinary raise; stacks pooled. Jam policy unchanged.',
          'Exact observed bb sizes projected to nearest non-jam scenario size by log distance; ties smaller.',
          'Sparse positions shrink toward observed pool; out-of-coverage positions borrow nearest observed position.',
          'Historical evaluation dates have been inspected in previous development; this is not fresh untouched validation.',
          'A scenario outside historical sizing/stack/stakes coverage is an unvalidated transfer. No arbitrary menu floor.'])
    model=report['model'];dataset=model['stats']['dataset'];coverage=[]
    for row in dataset['rows']:
        if row['role']==-2:continue
        key=closest(final,row['players'],row['role']);policy=final[key] if use_context else prior
        row['opening']['raise_sizes']=[[size,round(p,12)] for size,p in sorted(policy.items()) if p>0]
        coverage.append(dict(players=row['players'],role=row['role'],source_players=key[0],source_role=key[1],
            direct_openings=sum(rows.get((row['players'],row['role']),{}).values()),source_openings=sum(rows[key].values()),
            menu_2_2_5_3_5=project(policy,[2,2.5,3,5]).tolist()))
    evidence['coverage']=coverage
    dataset['response_notes']['opening_sizes']='Opening sizes: observed non-jam first-in amounts, pooled across hands and stacks; '+('sparse positions shrink toward the observed pool.' if use_context else 'pooled across positions; positional candidate did not improve the historical check.')+' Mapped to the nearest available non-jam size; no invented minimum frequency. Unsupported positions borrow measured neighbors. Iso-raises, re-raises and jams retain their existing size rules.'
    model['source']['version']='2026-09-09-v6'
    model['source']['assumptions']=[x for x in model['source']['assumptions'] if x!='Configured smallest/largest sizes approximate the observed distribution.']
    model['source']['assumptions']=[x for x in model['source']['assumptions'] if not x.startswith('Opening sizes:')]
    model['source']['assumptions'].append('Opening sizes: empirical non-jam amounts; hand-independent size mix with contextual shrinkage and nearest-menu projection. Jam/iso/re-raise rules unchanged.')
    report['opening_size_validation']=evidence
    Path('output/opening-size-evidence.json').write_text(json.dumps(evidence,indent=1,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    if publish:
        for name,value in [('NL10.json',report),('models.json',[model])]:
            (Path(out)/name).write_text(json.dumps(value,indent=1,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in evidence.items() if k!='coverage'},indent=2))

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--out',required=True);p.add_argument('--publish',action='store_true');a=p.parse_args();run(a.input,a.out,a.publish)
