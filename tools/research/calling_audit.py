"""Retrospective first-entry re-raise audit; does not install a model.

Public files contain aggregate diagnostics only. Raw/session observations and
source manifests stay beneath output/. Freeze the protocol before extraction.
"""
import argparse, collections, datetime, hashlib, importlib.util, json, re, sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/behavior/pass3'
PRIVATE=ROOT/'output/behavior-pass3'
KINDS=['cold','limp','cold_call','open_raise','iso_raise','reraise_entry']
SPLIT={'tune_from':'2025-10-05','test_from':'2025-11-03'}
ARTIFACT=ROOT/'cache/contextual/ignition-nl10-reraise-v1.json'
DEPENDENCIES=['tools/ignition/analyze.py','tools/coinpoker/analyze.py','tools/ignition/contextual_reraise.py','tools/ignition/smoothing.py','tools/ignition/limps.py','tools/ignition/responses.py','tools/ignition/fit.py','tools/coinpoker/fit.py','tools/coinpoker/context.py','docs/ignition/NL10.json']
def require(ok,message):
    if not ok:raise ValueError(message)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def protocol():
    value=dict(schema=1,retrospective=True,production_changed=False,split=SPLIT,
        prior_exposure='All NL10 regular periods and prior NL5/NL25 transfer groups have already been inspected. No fresh holdout claim. Future newly collected sessions are required for independent confirmation.',
        source='All validated Ignition NL10 regular opponent decisions facing two or more raises; exclude hero; deduplicate hands before replay.',
        entry_types=KINDS,entry_definition='First voluntary preflop action: limp, cold call facing an open or later raise, unopened open raise, iso-raise over limps, or direct re-raise. A later raise does not erase first-entry type; current v1 ever-raised state is retained separately.',
        baseline='Reproduce current contextual family (hand_price, ridge 1) with hand probabilities fitted only on the current training split. Never score NL10 with the full-source runtime artifact.',
        candidates={'residual_ridge':[10.,100.,1000.],'residual_features':'first-entry category x intercept, centered nominal price, actor starting stack log, raise depth; original contextual prediction remains an offset','blend':'Correction weight n/(n+30), where n is training decisions in first-entry x price band x actor stack band. No labels from tuning/evaluation enter support counts.'},
        selection='Choose residual ridge and full/support blend by earlier tuning log loss. Freeze selection, then refit on train+tune and evaluate once on later previously inspected sessions.',
        groups=['first-entry','price <=15%, 15-30%, >30%','faced total <=10, 10-25, >25 bb','actor starting stack <50, 50-150, >150 bb','3-bet vs 4-bet+','weak offsuit T-high or less','direct same-context hand support 0,1-4,5+'],
        uncertainty='2000 paired source-session bootstrap replicates, seed 20260910. Exploratory marginal intervals; no simultaneous guarantee. Suppress intervals below two sessions.',
        promotion_gate='No automatic production promotion. Consider candidate for independent confirmation only with positive overall paired lower bound and no negative point gain in first-entry groups with >=100 decisions.',
        limitation='Actor stack is not effective stack; opponent positions, full raise sequence, side pots, rake and first-entry size are not fitted. Sparse support blend is a research comparison, not a claim that the existing predictor is correct.')
    path=OUT/'protocol.json'
    if path.exists():require(json.loads(path.read_text())==value,'Frozen protocol differs')
    else:write(path,value)
    return value

def extract(canonical,cards,cp,hand_index):
    """Extract only after full replay validation; no outcome/showdown features."""
    header=cp.HEADER.match(canonical);bb=cp.cents(header[3]);pre,rest=canonical.split('*** HOLE CARDS ***',1)
    rec=[m for l in pre.splitlines() if (m:=cp.SEAT.match(l))]
    names=[m[2] for m in rec];stacks={m[2]:cp.cents(m[3]) for m in rec};contrib=dict.fromkeys(names,0)
    btn=int(re.search(r'Seat #(\d+) is the button',pre)[1]);bi=[int(m[1]) for m in rec].index(btn)
    roles={p:((bi-i)%len(names)) for i,p in enumerate(names)}
    for l in pre.splitlines():
        if m:=cp.POST.match(l):
            contrib[m[1]]+=cp.cents(m[3]);roles[m[1]]= -1 if m[2]=='small blind' else -2
    cur=bb;raises=0;pot=sum(contrib.values());first={};ever_raised=set();records=[]
    for l in rest.splitlines():
        if l.startswith('*** '):break
        if m:=cp.RETURN.match(l):
            value=cp.cents(m[1]);contrib[m[2]]-=value;pot-=value;continue
        m=cp.ACTION.match(l)
        if not m:continue
        p,act,amount,to,tail=m.groups();facing=cur-contrib[p]
        if raises>=2:
            cost=min(facing,stacks[p]-contrib[p]);entry=2 if p in ever_raised else 1 if p in first else 0
            row=[len(names),roles[p],entry,int(raises>=3),round(cost/max(1,pot+cost),6),round(contrib[p]/bb,4),round((stacks[p]-contrib[p])/bb,4),hand_index(cards[p])]
            if '[ME]' not in p:records.append(dict(row=row,kind=first.get(p,'cold'),faced_bb=cur/bb,action={'folds':0,'calls':1,'raises':2}[act]))
        if act=='calls':
            first.setdefault(p,'limp' if raises==0 else 'cold_call');v=cp.cents(amount);contrib[p]+=v;pot+=v
        elif act=='raises':
            first.setdefault(p,'open_raise' if raises==0 and not first else 'iso_raise' if raises==0 else 'reraise_entry')
            target=cp.cents(to);pot+=target-contrib[p];contrib[p]=target;cur=target;raises+=1;ever_raised.add(p)
    return records

def collect(source):
    protocol();dependencies={q:digest(ROOT/q) for q in DEPENDENCIES};script_hash=digest(__file__);a=load_module('pass3_ignition',ROOT/'tools/ignition/analyze.py');paths=a.source_paths(source);seen={};sessions=[];audit=collections.Counter();files=[]
    old=json.loads((ROOT/'output/ignition-contextual-reraise/analysis.json').read_text());oldby={s['id']:s for s in old['sessions']}
    for path in paths:
        raw=path.read_bytes();files.append(dict(path=str(path.relative_to(source)),sha256=hashlib.sha256(raw).hexdigest()));records=[];dates=[]
        for block in re.split(r'(?=^Ignition Hand #)',raw.decode('utf-8-sig',errors='replace'),flags=re.M):
            m=re.match(r'Ignition Hand #(\d+)',block)
            if not m:continue
            audit['raw']+=1
            if m[1] in seen:audit['duplicates']+=1;continue
            seen[m[1]]=hashlib.sha256(block.strip().encode()).hexdigest()
            try:canonical,cards=a.convert(block);meta,counters=a.cp.replay(canonical,10,variant='ignition')
            except (a.cp.Invalid,ValueError,KeyError,TypeError) as e:audit['excluded/'+str(e)]+=1;continue
            rows=extract(canonical,cards,a.cp,a.hand_index)
            expected=sum(v for p,c in counters.items() if '[ME]' not in p for k,v in c.items() if k.startswith('reraise_detail/'))
            require(len(rows)==expected,'Detailed replay denominator mismatch')
            audit['accepted']+=1;dates.append(meta['date']);records.extend(rows)
        if dates:
            sid=hashlib.sha256(path.name.encode()).hexdigest()[:16]
            require(sid in oldby,'New/unrecognized session: update prospective protocol before consuming it')
            original=oldby[sid]
            require(len(records)==sum(original['reraise_cells'].values()),'Existing session re-raise denominator differs')
            # Stronger preservation check: all old contextual features/actions match.
            actual=collections.Counter()
            for z in records:actual[(tuple(z['row']),z['action'])]+=1
            predictor=load_module('pass3_counter_predictor',ROOT/'tools/ignition/contextual_reraise.py') if not sessions else predictor
            rr,yy,_=predictor.observations([original]);prior=collections.Counter()
            for r,y in zip(rr,yy):
                for k,n in enumerate(y):
                    if n:prior[(tuple(r),k)]+=int(n)
            require(actual==prior,'Detailed replay changed existing context/action observations')
            sessions.append(dict(id=sid,first=min(dates),last=max(dates),records=records))
    require(len(sessions)==len(old['sessions']),'Existing validated session count differs')
    require(dependencies=={q:digest(ROOT/q) for q in DEPENDENCIES} and script_hash==digest(__file__),'Collection code changed mid-run')
    require(files==[dict(path=str(q.relative_to(source)),sha256=digest(q)) for q in a.source_paths(source)],'Sources changed during collection')
    PRIVATE.mkdir(parents=True,exist_ok=True);write(PRIVATE/'observations.json',dict(audit=dict(audit),sessions=sessions))
    manifest=dict(schema=1,dependencies_sha256=dependencies,files=files,hand_ids=sorted(seen),observations_sha256=digest(PRIVATE/'observations.json'),previous_analysis_sha256=digest(ROOT/'output/ignition-contextual-reraise/analysis.json'),protocol_sha256=digest(OUT/'protocol.json'),extractor_sha256=digest(__file__),parser_sha256={p:digest(ROOT/p) for p in ['tools/ignition/analyze.py','tools/coinpoker/analyze.py']},runtime_model_sha256=digest(ARTIFACT))
    write(PRIVATE/'manifest.json',manifest);print(json.dumps(dict(audit=audit,sessions=len(sessions),decisions=sum(len(s['records']) for s in sessions))))

def arrays(sessions):
    records=[z for s in sessions for z in s['records']]
    return (np.array([z['row'] for z in records],float),np.eye(3)[[z['action'] for z in records]],np.array([KINDS.index(z['kind']) for z in records]),np.array([z['faced_bb'] for z in records]),np.repeat(np.arange(len(sessions)),[len(s['records']) for s in sessions]))
def extra(rows,kinds):
    entry=np.eye(len(KINDS))[kinds];stack=rows[:,5]+rows[:,6]
    return np.column_stack([entry,entry*((rows[:,4]-.3)/.15)[:,None],entry*((np.log1p(stack)-np.log(101))/2)[:,None],entry*rows[:,3,None]])
def support_keys(rows,kinds):
    return [(int(k),int(np.digitize(r[4],[.150000001,.300000001])),int(np.digitize(r[5]+r[6],[50,150.00000001]))) for r,k in zip(rows,kinds)]
def blend_weights(train_rows,train_kinds,rows,kinds):
    count=collections.Counter(support_keys(train_rows,train_kinds))
    return np.array([count[k]/(count[k]+30.) for k in support_keys(rows,kinds)])
def blend(base,new,weight):
    require(np.isfinite(weight).all() and ((weight>=0)&(weight<=1)).all(),'Invalid support weight')
    return base+(new-base)*weight[:,None]
def metrics(y,base,new,ids):
    if not len(y):return None
    ll=[-(y*np.log(np.maximum(p,1e-12))).sum(1) for p in [base,new]]
    units=np.array([[int((ids==s).sum()),float((ll[0]-ll[1])[ids==s].sum())] for s in np.unique(ids)])
    rng=np.random.default_rng(20260910);boot=[]
    for _ in range(2000):
        u=units[rng.integers(len(units),size=len(units))].sum(0);boot.append(u[1]/u[0])
    return dict(decisions=len(y),sessions=len(units),contextual_log_loss=float(ll[0].mean()),candidate_log_loss=float(ll[1].mean()),gain=float((ll[0]-ll[1]).mean()),gain_95_interval=np.quantile(boot,[.025,.975]).tolist() if len(units)>=2 else None,observed_call=float(y[:,1].mean()),contextual_call=float(base[:,1].mean()),candidate_call=float(new[:,1].mean()),contextual_brier=float(((base-y)**2).sum(1).mean()),candidate_brier=float(((new-y)**2).sum(1).mean()))
def verify_inputs():
    protocol();manifest=json.loads((PRIVATE/'manifest.json').read_text())
    require(manifest['dependencies_sha256']=={q:digest(ROOT/q) for q in DEPENDENCIES},'Analysis/predictor dependency changed')
    require(manifest['observations_sha256']==digest(PRIVATE/'observations.json'),'Observation hash mismatch')
    require(manifest['protocol_sha256']==digest(OUT/'protocol.json'),'Protocol hash mismatch')
    require(manifest['extractor_sha256']==digest(__file__),'Collector/evaluator source changed: recollect')
    require(manifest['previous_analysis_sha256']==digest(ROOT/'output/ignition-contextual-reraise/analysis.json'),'Prior analysis hash mismatch')
    require(manifest['runtime_model_sha256']==digest(ARTIFACT),'Installed model changed')
    require(manifest['parser_sha256']=={p:digest(ROOT/p) for p in manifest['parser_sha256']},'Parser changed')
    return manifest

def evaluate():
    manifest=verify_inputs();data=json.loads((PRIVATE/'observations.json').read_text());p=load_module('pass3_contextual',ROOT/'tools/ignition/contextual_reraise.py');report=json.loads((ROOT/'docs/ignition/NL10.json').read_text())
    source=json.loads((ROOT/'output/ignition-contextual-reraise/analysis.json').read_text());sourceby={s['id']:s for s in source['sessions']}
    sessions=data['sessions'];tr=[s for s in sessions if s['last']<SPLIT['tune_from']];tu=[s for s in sessions if s['first']>=SPLIT['tune_from'] and s['last']<SPLIT['test_from']];te=[s for s in sessions if s['first']>=SPLIT['test_from']]
    require(not (set(s['id'] for s in tr)&set(s['id'] for s in tu)),'Split leakage')
    def original_fit(ss,target):
        rr,yy,_,_,_=arrays(ss);model=p.baseline([sourceby[s['id']] for s in ss],report);bp=p.base_probs(model,rr);xx,_=p.features(rr,'hand_price');w=p.fit(xx,yy,bp,1.)
        return p.predict(xx,bp,w),p.predict(p.features(target,'hand_price')[0],p.base_probs(model,target),w),model,w
    r,y,k,_,_=arrays(tr);vr,vy,vk,_,_=arrays(tu);base,vbase,_,_=original_fit(tr,vr);candidates=[]
    for ridge in [10.,100.,1000.]:
        w=p.fit(extra(r,k),y,base,ridge);prediction=p.predict(extra(vr,vk),vbase,w)
        for use_blend in [False,True]:
            q=blend(vbase,prediction,blend_weights(r,k,vr,vk)) if use_blend else prediction
            candidates.append(dict(ridge=ridge,support_blend=use_blend,tuning_log_loss=p.loss(vy,q)))
    best=min(candidates,key=lambda z:z['tuning_log_loss'])
    write(OUT/'selection.json',dict(schema=1,candidates=candidates,selected=best,baseline_tuning_log_loss=p.loss(vy,vbase),protocol_sha256=digest(OUT/'protocol.json'),frozen_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),later_scored=False))
    fit=tr+tu;r,y,k,_,_=arrays(fit);er,ey,ek,faced,eids=arrays(te);base,ebase,base_model,base_weights=original_fit(fit,er);w=p.fit(extra(r,k),y,base,best['ridge']);full=p.predict(extra(er,ek),ebase,w);weights=blend_weights(r,k,er,ek);new=blend(ebase,full,weights) if best['support_blend'] else full
    write(OUT/'candidate-research-only.json',dict(production=False,selected=best,weights=w.tolist(),contextual_weights=base_weights.tolist(),baseline={b:[dict(players=z[0],role=z[1],probabilities=v.tolist()) for z,v in m.items()] for b,m in base_model.items()},support_counts=[dict(kind=z[0],price_band=z[1],stack_band=z[2],decisions=n) for z,n in sorted(collections.Counter(support_keys(r,k)).items())],features='First-entry x intercept, price, log actor stack, raise depth; offset is train+tune contextual-v1 refit for this retrospective evaluation.',protocol_sha256=digest(OUT/'protocol.json'),frozen_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
    # Diagnostic feature support is counted on train+tune only.
    direct=collections.Counter((int(row[0]),int(row[1]),int(kind),int(row[7])) for row,kind in zip(r,k));support=np.array([direct[(int(row[0]),int(row[1]),int(kind),int(row[7]))] for row,kind in zip(er,ek)])
    stack=er[:,5]+er[:,6];h=er[:,7].astype(int);weak=(h//13<h%13)&(h%13<9)
    masks={'all':np.ones(len(er),bool)}
    for i,name in enumerate(KINDS):masks['entry/'+name]=ek==i
    for name,mask in [('cheap',er[:,4]<=.15),('middle',(er[:,4]>.15)&(er[:,4]<=.3)),('expensive',er[:,4]>.3),('weak_offsuit',weak),('weak_cheap',weak&(er[:,4]<=.15)),('3bet',er[:,3]==0),('4betplus',er[:,3]==1),('stack_lt50',stack<50),('stack_50_150',(stack>=50)&(stack<=150)),('stack_gt150',stack>150),('faced_le10',faced<=10),('faced_10_25',(faced>10)&(faced<=25)),('faced_gt25',faced>25),('direct_0',support==0),('direct_1_4',(support>0)&(support<5)),('direct_5plus',support>=5)]:masks[name]=mask
    for i,name in enumerate(KINDS):
        for price,mask in [('cheap',er[:,4]<=.15),('middle',(er[:,4]>.15)&(er[:,4]<=.3)),('expensive',er[:,4]>.3)]:masks[f'entry_price/{name}/{price}']=(ek==i)&mask
    results={name:metrics(ey[m],ebase[m],new[m],eids[m]) for name,m in masks.items()}
    coverage=[]
    for kind in KINDS:
        mask=ek==KINDS.index(kind);cnt=int(mask.sum())
        coverage.append(dict(entry=kind,later_decisions=cnt,later_sessions=len(np.unique(eids[mask])),same_position_table_hand_train_decisions_zero=int((mask&(support==0)).sum()),same_position_table_hand_train_decisions_under5=int((mask&(support<5)).sum())))
    gate=results['all']['gain_95_interval'][0]>0 and all(v['gain']>=0 for name,v in results.items() if name.startswith('entry/') and v and v['decisions']>=100)
    result=dict(schema=1,retrospective=True,production_changed=False,protocol_sha256=digest(OUT/'protocol.json'),selection_sha256=digest(OUT/'selection.json'),private_manifest_sha256=digest(PRIVATE/'manifest.json'),runtime_model_sha256=digest(ARTIFACT),audit=data['audit'],splits=dict(train=len(tr),tune=len(tu),later=len(te),excluded=len(sessions)-len(tr)-len(tu)-len(te)),split_decisions=dict(train=len(arrays(tr)[0]),tune=len(vr),later=len(er)),selected=best,metrics=results,coverage=coverage,research_gate_passed=gate,full_correction_all=metrics(ey,ebase,full,eids),support_blend_all=metrics(ey,ebase,blend(ebase,full,weights),eids),source_sha256={q:digest(ROOT/q) for q in ['tools/research/calling_audit.py','tools/ignition/contextual_reraise.py','tools/ignition/smoothing.py','tools/ignition/limps.py','tools/ignition/responses.py','tools/ignition/fit.py','tools/coinpoker/fit.py','tools/coinpoker/context.py']})
    result['candidate_sha256']=digest(OUT/'candidate-research-only.json');write(OUT/'evaluation.json',result)
    print(json.dumps(dict(selected=best,all=results['all'],entries={k:v for k,v in results.items() if k.startswith('entry/')},gate=gate),indent=2));render(result)

def render(result=None):
    import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
    if result is None:result=json.loads((OUT/'evaluation.json').read_text())
    groups=[('all','All'),*[(f'entry/{k}',k.replace('_',' ').title()) for k in KINDS]];groups=[(k,l) for k,l in groups if result['metrics'][k]]
    fig,axs=plt.subplots(1,2,figsize=(13,4.8),layout='constrained');pos=np.arange(len(groups));ms=[result['metrics'][k] for k,l in groups]
    for offset,key,label,color in [(-.18,'contextual_log_loss','Existing contextual family','#7a8895'),(.18,'candidate_log_loss','Entry-aware research candidate','#4c916b')]:axs[0].barh(pos+offset,[m[key] for m in ms],.34,label=label,color=color)
    axs[0].set_yticks(pos,[f'{l} (n={m["decisions"]})' for (_,l),m in zip(groups,ms)]);axs[0].invert_yaxis();axs[0].set_xlabel('Later-session log loss (lower is better)');axs[0].legend(fontsize=8)
    for key,label,marker in [('observed_call','Observed','o'),('contextual_call','Existing contextual','x'),('candidate_call','Entry-aware candidate','s')]:axs[1].plot([100*m[key] for m in ms],pos,marker=marker,linestyle='none',label=label)
    axs[1].set_yticks(pos,[l for _,l in groups]);axs[1].invert_yaxis();axs[1].set_xlabel('Conditional call frequency (%)');axs[1].legend(fontsize=8);fig.suptitle('First-entry audit — reused historical evaluation sessions');fig.savefig(OUT/'entry-comparison.png',dpi=160);plt.close(fig)
    names=[('cheap','Price ≤15%'),('middle','Price 15–30%'),('expensive','Price >30%'),('stack_lt50','Stack <50bb'),('stack_50_150','Stack 50–150bb'),('stack_gt150','Stack >150bb'),('weak_offsuit','Weak offsuit'),('weak_cheap','Weak + cheap')];names=[(k,l) for k,l in names if result['metrics'][k]]
    fig,ax=plt.subplots(figsize=(9,5.5),layout='constrained')
    for i,(key,label) in enumerate(names):
        m=result['metrics'][key];ci=m['gain_95_interval'];ax.plot(m['gain'],i,'o',color='#4c916b')
        if ci:ax.plot(ci,[i,i],color='#4c916b')
    ax.set_yticks(np.arange(len(names)),[f'{l} (n={result["metrics"][k]["decisions"]})' for k,l in names]);ax.invert_yaxis();ax.axvline(0,color='#666',linewidth=1);ax.set_xlabel('Log-loss improvement vs existing contextual family\nPaired exploratory 95% session bootstrap');ax.set_title('Price, stack and sparse-hand uncertainty');fig.savefig(OUT/'subgroup-uncertainty.png',dpi=160);plt.close(fig)
    cov=result['coverage'];fig,ax=plt.subplots(figsize=(10,4.8),layout='constrained');pos=np.arange(len(cov));total=np.array([c['later_decisions'] for c in cov]);zero=np.array([c['same_position_table_hand_train_decisions_zero'] for c in cov]);under=np.array([c['same_position_table_hand_train_decisions_under5'] for c in cov]);ax.barh(pos,zero,label='No direct training decision',color='#a15b55');ax.barh(pos,under-zero,left=zero,label='1–4 direct training decisions',color='#c99850');ax.barh(pos,total-under,left=under,label='5+ direct training decisions',color='#4c916b');ax.set_yticks(pos,[c['entry'].replace('_',' ') for c in cov]);ax.invert_yaxis();ax.set_xlabel('Later decisions, classified by same first-entry / position / table size / hand support');ax.legend(fontsize=8);ax.set_title('Hand-level evidence is much thinner than pooled sample size');fig.savefig(OUT/'evidence-coverage.png',dpi=160);plt.close(fig)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['prepare','collect','evaluate','render']);ap.add_argument('--source',type=Path,default=Path('T:/Dev/Poker Data/Ignition'));args=ap.parse_args()
    if args.mode=='prepare':protocol()
    elif args.mode=='collect':collect(args.source)
    elif args.mode=='evaluate':evaluate()
    else:render()
