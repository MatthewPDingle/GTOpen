"""Measured non-jam iso/re-raise sizes; a separate frozen retrospective study.

Never changes old collectors or installed models. Conditional hand action
probabilities and existing opening sizes are preserved exactly during export.
"""
import argparse,collections,copy,datetime,hashlib,importlib.util,json,math,re,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'research/ignition-action-sizes';PRIVATE=ROOT/'output/action-sizing'
SOURCE=Path('T:/Dev/Poker Data/Ignition');LIBRARY=ROOT/'cache/archetypes.json'
SPLIT={'tune_from':'2025-10-05','test_from':'2025-11-03'}
GROUPS=['iso_paid_1','iso_paid_2','iso_paid_3','iso_free_1','iso_free_2','iso_free_3','threebet','squeeze','limp_reraise','reraise','cold_reraise']
EXTRA=['iso_1','iso_2','iso_3','iso_paid_all','iso_free_all','iso_all']
MENUS={'bb':[2.,3.,4.,5.,7.5,10.,15.],'previous':[2.,2.5,3.,4.,5.,7.]}
DEPENDENCIES=['tools/ignition/analyze.py','tools/coinpoker/analyze.py']
def require(c,m):
    if not c:raise ValueError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def basis(group):return 'bb' if group.startswith('iso_') else 'previous'
def protocol():
    value=dict(schema=1,retrospective=True,source='Ignition NL10 regular, all fully validated opponent preflop raises; hero excluded.',split=SPLIT,groups=GROUPS,pooling_groups=EXTRA,
        amount_definition='Iso: total raise-to in bb. Re-raises: total raise-to divided by previous faced raise-to. True all-ins identified by chips added equaling remaining actor stack and kept separate.',
        exclusion='Use unchanged validated source selection, deduplication, full replay exclusions. No further outcome-based exclusions. Forced posts and calls are not raise opportunities.',
        sizing_conditional='Distribution of size given an ordinary non-jam raise; independent of hand. Existing fold/call/raise/jam probabilities and opening sizes are unchanged.',
        candidates=['pooled',30.,100.,300.,1000.],candidate_definition='Exact observed empirical size mass; per table-size/position Dirichlet shrinkage toward same-situation pool at fixed strengths. Unobserved exact contexts use the pool, never pretend to have positional measurements.',
        scoring_menus=MENUS,score='Categorical log loss after nearest log-distance projection onto fixed menu (tie smaller); support-independent 1e-12 numerical log clamp, never a production minimum size frequency.',
        selection='Select pooled/context strength by earlier tuning mean log loss; freeze before later scoring. Context release gate predefined: later gain lower 95% paired session bootstrap bound >0 and at least30 later raises/10 later sessions. Gate failures retain pooled sizing with explicit unsupported contextual-detail note; not a model chosen to minimize later loss.',
        minimum_pool='At least50 full-source non-jam raises across10 sessions before exporting a direct pool. Sparse iso free/paid groups borrow the matching limper-count pool, then all-iso pool if supported; sparse later-raise groups retain legacy size rules. These are support heuristics, not calibrated confidence.',
        uncertainty='2000 paired source-session bootstrap replicates seed20260911. Marginal exploratory intervals, not simultaneous guarantees; none below2 sessions.',
        source_exposure='All existing NL10 regular periods already inspected. Reused historical split, not fresh independent validation. No automatic support expansion to other stakes/blinds/table sizes.',
        export='Only a candidate library under output/action-sizing. Shared policies cloned/deduplicated for differing size contexts, all hand probabilities and all opening policies exactly preserved.')
    p=OUT/'protocol.json'
    if p.exists():require(json.loads(p.read_text())==value,'Protocol changed after freeze')
    else:write(p,value)
    return value

def replay_sizes(text,cp):
    """Additional extraction after unchanged full cp.replay validates the hand."""
    header=cp.HEADER.match(text);bb=cp.cents(header[3]);pre,rest=text.split('*** HOLE CARDS ***',1)
    seats=[m for l in pre.splitlines() if (m:=cp.SEAT.match(l))];names=[m[2] for m in seats];stack={m[2]:cp.cents(m[3]) for m in seats};put=dict.fromkeys(names,0)
    btn=int(re.search(r'Seat #(\d+) is the button',pre)[1]);bi=[int(s[1]) for s in seats].index(btn);roles={p:(bi-i)%len(names) for i,p in enumerate(names)}
    for l in pre.splitlines():
        if m:=cp.POST.match(l):put[m[1]]+=cp.cents(m[3]);roles[m[1]]=-1 if m[2]=='small blind' else -2
    raises=limpers=callers=0;voluntary=set();cur=bb;events=[];counts=collections.Counter();opens=collections.Counter()
    for l in rest.splitlines():
        if l.startswith('*** '):break
        if m:=cp.RETURN.match(l):put[m[2]]-=cp.cents(m[1]);continue
        m=cp.ACTION.match(l)
        if not m:continue
        p,act,amt,to,tail=m.groups();facing=cur-put[p]
        policy=('limps' if facing==0 or limpers else 'open') if raises==0 else ('limp_defense' if p in voluntary else 'squeeze' if callers else 'raise') if raises==1 else ('reraise' if p in voluntary else 'cold_reraise')
        action={'folds':'fold','checks':'call','calls':'call','raises':'raise'}[act]
        if '[ME]' not in p:counts[(len(names),roles[p],policy,action)]+=1
        if act=='raises':
            target=cp.cents(to);jam=target-put[p]>=stack[p]-put[p]
            if '[ME]' not in p:
                if raises==0 and not limpers:
                    if facing>0:opens[(len(names),roles[p],'jam' if jam else f'{target/bb:.4f}')]+=1
                else:
                    group=f'iso_{"free" if facing==0 else "paid"}_{min(limpers,3)}' if raises==0 else {'raise':'threebet','limp_defense':'limp_reraise'}.get(policy,policy)
                    require(group in GROUPS,'Unexpected sizing group')
                    events.append(dict(group=group,players=len(names),role=roles[p],amount=target/bb if raises==0 else target/cur,basis='bb' if raises==0 else 'previous',jam=jam,raise_to_bb=target/bb,previous_to_bb=cur/bb,invested_bb=put[p]/bb,remaining_bb=(stack[p]-put[p])/bb))
            voluntary.add(p);put[p]=target;cur=target;raises+=1;callers=0
        elif act=='calls':
            put[p]+=cp.cents(amt);voluntary.add(p)
            if raises==0:limpers+=1
            else:callers+=1
    return events,counts,opens

def collect():
    protocol();a=module('action_size_ignition',ROOT/'tools/ignition/analyze.py');dependencies={p:sha(ROOT/p) for p in DEPENDENCIES};script=sha(__file__)
    prior_path=ROOT/'output/ignition-contextual-reraise/analysis.json';prior=json.loads(prior_path.read_text());priorby={s['id']:s for s in prior['sessions']};old_snapshot_path=ROOT/'output/ignition-transfer-v1/collection_manifest.json';old_snapshot=json.loads(old_snapshot_path.read_text())['training']
    files=[];seen={};sessions=[];audit=collections.Counter();roles={'BB':-2,'SB':-1,'BTN':0,'CO':1,'HJ':2,'LJ':3,'UTG':4}
    for path in a.source_paths(SOURCE):
        raw=path.read_bytes();files.append(dict(path=str(path.relative_to(SOURCE)),sha256=hashlib.sha256(raw).hexdigest()));dates=[];events=[];allcounts=collections.Counter();allopens=collections.Counter()
        for block in re.split(r'(?=^Ignition Hand #)',raw.decode('utf-8-sig',errors='replace'),flags=re.M):
            hid=re.match(r'Ignition Hand #(\d+)',block)
            if not hid:continue
            audit['raw']+=1
            if hid[1] in seen:audit['duplicates']+=1;continue
            seen[hid[1]]=hashlib.sha256(block.strip().encode()).hexdigest()
            try:canonical,cards=a.convert(block);meta,counters=a.cp.replay(canonical,10,variant='ignition')
            except (a.cp.Invalid,ValueError,KeyError,TypeError) as e:audit['excluded/'+str(e)]+=1;continue
            extra,counts,opens=replay_sizes(canonical,a.cp);expected=collections.Counter()
            for player,c in counters.items():
                if '[ME]' in player:continue
                for key,n in c.items():
                    if key.startswith('policy/'):
                        prefix,action=key.split('|');_,players,pos,bucket=prefix.split('/')
                        if bucket.startswith('raise_'):continue
                        expected[(int(players),roles[pos],bucket,action)]+=n
            require(counts==expected,'Independent collector changed existing action denominators')
            audit['accepted']+=1;dates.append(meta['date']);events.extend(extra);allcounts.update(counts);allopens.update(opens)
        if dates:
            sid=hashlib.sha256(path.name.encode()).hexdigest()[:16];require(sid in priorby,'New source session requires new protocol')
            old=priorby[sid];expected=collections.Counter();expectedopens=collections.Counter()
            for key,n in old['policy_cells'].items():
                pref,action=key.split('|');bucket,players,pos,hand=pref.split('/')
                if bucket.startswith('raise_'):continue
                expected[(int(players),roles[pos],bucket,action)]+=n
            for key,n in old['counts'].items():
                if key.startswith('opening_size/'):
                    prefix,size=key.split('|');_,players,pos=prefix.split('/');expectedopens[(int(players),roles[pos],size)]+=n
            require(allcounts==expected and allopens==expectedopens,'Existing validated session/action/open-size denominator differs')
            sessions.append(dict(id=sid,first=min(dates),last=max(dates),events=events))
    require(files==old_snapshot['files'] and sorted(seen)==old_snapshot['hand_ids'],'Source changed since previous audit; reserve new data')
    require(files==[dict(path=str(p.relative_to(SOURCE)),sha256=sha(p)) for p in a.source_paths(SOURCE)],'Source changed during collection')
    require(dependencies=={p:sha(ROOT/p) for p in DEPENDENCIES} and script==sha(__file__),'Collector changed mid-run')
    require(len(sessions)==len(prior['sessions']),'Validated session count mismatch')
    write(PRIVATE/'observations.json',dict(audit=dict(audit),sessions=sessions))
    write(PRIVATE/'manifest.json',dict(schema=1,files=files,hand_ids=sorted(seen),observations_sha256=sha(PRIVATE/'observations.json'),prior_analysis_sha256=sha(prior_path),old_snapshot_sha256=sha(old_snapshot_path),collector_sha256=script,dependencies_sha256=dependencies,protocol_sha256=sha(OUT/'protocol.json'),source_library_sha256=sha(LIBRARY)))
    print(json.dumps(dict(audit=audit,sessions=len(sessions),sizing_events=sum(len(s['events']) for s in sessions))))

def in_group(e,group):
    g=e['group']
    if group in GROUPS:return g==group
    if group=='iso_all':return g.startswith('iso_')
    if group in ['iso_paid_all','iso_free_all']:return g.startswith(group[:-3])
    return g.startswith('iso_') and g.endswith('_'+group[-1])
def records(sessions,group):return [(i,e) for i,s in enumerate(sessions) for e in s['events'] if in_group(e,group) and not e['jam']]
def fit(sessions,group,strength=None):
    rs=records(sessions,group);pool=collections.Counter();contexts=collections.defaultdict(collections.Counter)
    for _,e in rs:pool[e['amount']]+=1;contexts[e['players'],e['role']][e['amount']]+=1
    if not pool:return {},{}
    total=sum(pool.values());prior={size:n/total for size,n in pool.items()};policies={}
    if strength is not None:
        for key,c in contexts.items():policies[key]={size:(c[size]+strength*p)/(sum(c.values())+strength) for size,p in prior.items()}
    return policies,prior
def project(distribution,menu):
    out=np.zeros(len(menu))
    for size,weight in distribution.items():
        require(size>0 and math.isfinite(size) and weight>=0 and math.isfinite(weight),'Invalid sizing distribution')
        i=min(range(len(menu)),key=lambda i:(abs(math.log(menu[i]/size)),menu[i]));out[i]+=weight
    return out
def predict(model,record,menu):
    policies,prior=model;return project(policies.get((record['players'],record['role']),prior),menu)
def comparison(sessions,group,models):
    rs=records(sessions,group);menu=MENUS[basis(group)]
    if not rs or any(not m[1] for m in models):return None
    losses=[[] for m in models];ids=[]
    for sid,e in rs:
        actual=int(np.argmax(project({e['amount']:1.},menu)));ids.append(sid)
        for j,m in enumerate(models):losses[j].append(-math.log(max(predict(m,e,menu)[actual],1e-12)))
    loss=np.array(losses);ids=np.array(ids);units=np.array([[int((ids==s).sum()),float((loss[0]-loss[1])[ids==s].sum())] for s in np.unique(ids)]) if len(models)>1 else None
    ci=None
    if units is not None and len(units)>=2:
        rng=np.random.default_rng(20260911);draw=[]
        for _ in range(2000):z=units[rng.integers(len(units),size=len(units))].sum(0);draw.append(z[1]/z[0])
        ci=np.quantile(draw,[.025,.975]).tolist()
    return dict(decisions=len(rs),sessions=len(np.unique(ids)),log_loss=[float(x.mean()) for x in loss],gain_95_interval=ci)
def verify():
    protocol();m=json.loads((PRIVATE/'manifest.json').read_text());require(m['observations_sha256']==sha(PRIVATE/'observations.json'),'Observations changed');require(m['collector_sha256']==sha(__file__),'Collector/evaluator source changed; recollect')
    require(m['protocol_sha256']==sha(OUT/'protocol.json'),'Protocol changed');require(m['dependencies_sha256']=={p:sha(ROOT/p) for p in DEPENDENCIES},'Parser changed');require(m['source_library_sha256']==sha(LIBRARY),'Source library changed');return m

def evaluate():
    manifest=verify();data=json.loads((PRIVATE/'observations.json').read_text());ss=data['sessions'];tr=[s for s in ss if s['last']<SPLIT['tune_from']];tu=[s for s in ss if s['first']>=SPLIT['tune_from'] and s['last']<SPLIT['test_from']];te=[s for s in ss if s['first']>=SPLIT['test_from']];selections={}
    for group in GROUPS+EXTRA:
        candidates=[]
        for strength in [None,30.,100.,300.,1000.]:
            model=fit(tr,group,strength);score=comparison(tu,group,[model]);candidates.append(dict(strength=strength,tuning_log_loss=None if score is None else score['log_loss'][0]))
        available=[c for c in candidates if c['tuning_log_loss'] is not None]
        selections[group]=dict(candidates=candidates,selected=min(available,key=lambda c:c['tuning_log_loss']) if available else None)
    write(OUT/'selection.json',dict(groups=selections,protocol_sha256=sha(OUT/'protocol.json'),frozen_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),later_scored=False))
    groups={};distributions={}
    for group in GROUPS+EXTRA:
        selection=selections[group]['selected'];strength=selection['strength'] if selection else None
        pooled=fit(tr+tu,group);selected=fit(tr+tu,group,strength);later=comparison(te,group,[pooled,selected]);ctx=bool(strength is not None and later and later['decisions']>=30 and later['sessions']>=10 and later['gain_95_interval'] and later['gain_95_interval'][0]>0)
        rs=records(ss,group);session_count=len({sid for sid,_ in rs});supported=len(rs)>=50 and session_count>=10;final=fit(ss,group,strength if ctx else None)
        groups[group]=dict(basis=basis(group),nonjam=len(rs),sessions=session_count,jams=sum(e['jam'] for s in ss for e in s['events'] if in_group(e,group)),selected=selection,later=later,contextual_released=ctx,pool_supported=supported,release='contextual' if ctx and supported else 'pooled' if supported else 'legacy/same-limper-count fallback',context_support=[dict(players=n,role=r,nonjam=sum(e['players']==n and e['role']==r for _,e in rs)) for n,r in sorted({(e['players'],e['role']) for _,e in rs})])
        distributions[group]=dict(basis=basis(group),pool=[[size,p] for size,p in sorted(final[1].items())],contexts=[dict(players=n,role=r,sizes=[[size,p] for size,p in sorted(v.items())]) for (n,r),v in sorted(final[0].items())])
    result=dict(schema=1,retrospective=True,production_changed=False,protocol_sha256=sha(OUT/'protocol.json'),selection_sha256=sha(OUT/'selection.json'),private_manifest_sha256=sha(PRIVATE/'manifest.json'),collector_sha256=sha(__file__),audit=data['audit'],split_sessions=dict(train=len(tr),tune=len(tu),later=len(te),excluded=len(ss)-len(tr)-len(tu)-len(te)),groups=groups,distributions=distributions,unique_sizing_events=sum(len(s['events']) for s in ss),unique_nonjam_events=sum(not e['jam'] for s in ss for e in s['events']))
    write(OUT/'evaluation.json',result);print(json.dumps({k:{x:v[x] for x in ['nonjam','jams','selected','later','release']} for k,v in groups.items()},indent=2));export(result);render(result)

def choose(group,players,role,result):
    options=[group]
    if group.startswith('iso_') and group in GROUPS:options += ['iso_'+group[-1],'iso_all']
    elif group in ['iso_paid_all','iso_free_all']:options+=['iso_all']
    for source in options:
        g=result['groups'][source]
        if g['pool_supported']:
            d=result['distributions'][source];row=next((r for r in d['contexts'] if r['players']==players and r['role']==role),None)
            return source,d['basis'],row['sizes'] if row else d['pool'],bool(row)
    return None

def export(result):
    before=json.loads(LIBRARY.read_text(encoding='utf-8'));after=copy.deepcopy(before);changed=[]
    for model in after:
        if model['stats'].get('dataset',{}).get('site','').startswith('Ignition')==False:continue
        d=model['stats']['dataset'];original=copy.deepcopy(d);policies=copy.deepcopy(d['response_policies']);intern={json.dumps(p,sort_keys=True,separators=(',',':')):i for i,p in enumerate(policies)};coverage=[]
        for row in d['rows']:
            for key,index in list(row['responses'].items()):
                group='threebet' if key=='raise' or key.startswith('raise_') else 'squeeze' if key=='squeeze' else 'limp_reraise' if key=='limp_defense' else key if key in ['reraise','cold_reraise'] else 'iso_'+key[6:] if key.startswith(('limps_paid_','limps_free_')) else ('iso_free_all' if row['role']==-2 else 'iso_paid_all') if key=='limps' else None
                if not group:continue
                value=choose(group,row['players'],row['role'],result)
                if value is None:coverage.append(dict(players=row['players'],role=row['role'],policy=key,requested=group,source=None));continue
                source,unit,sizes,context=value;policy=copy.deepcopy(original['response_policies'][index]);policy.pop('raise_sizes',None);policy.pop('raise_multiples',None);policy['raise_sizes' if unit=='bb' else 'raise_multiples']=[[a,round(b,12)] for a,b in sizes if b>0]
                signature=json.dumps(policy,sort_keys=True,separators=(',',':'))
                if signature not in intern:intern[signature]=len(policies);policies.append(policy)
                row['responses'][key]=intern[signature];coverage.append(dict(players=row['players'],role=row['role'],policy=key,requested=group,source=source,contextual=context,nonjam=result['groups'][source]['nonjam']))
        d['response_policies']=policies
        require(len(policies)<=512,'Sizing clones exceed current backend policy limit')
        for old,row in zip(original['rows'],d['rows']):
            require(old['opening']==row['opening'],'Opening policy changed')
            for key,index in old['responses'].items():
                oldp=original['response_policies'][index];newp=policies[row['responses'][key]]
                require(all(oldp[k]==newp[k] for k in ['call','raise','jam','raise_size']),'Hand-action policy changed')
        d['response_notes']['action_sizes']='Non-jam sizes learned from Ignition NL10 regular: iso raise-to bb by free/paid and limper count; re-raise multiples of the previous faced total. Distributions are conditional on raising and pool hands/stacks. Sparse iso groups borrow same-limper-count/all-iso evidence; sparse later groups keep legacy rules. Historical retrospective validation, not new source-format support. Opening/hand/jam probabilities unchanged.'
        for key in sorted({c['policy'] for c in coverage}):
            used=[c for c in coverage if c['policy']==key];sources=sorted({c['source'] for c in used if c['source']})
            pieces=[]
            for src in sources:
                evidence=result['groups'][src]
                pieces.append(f"{src.replace('_',' ')}: {evidence['nonjam']} non-jam raises from {evidence['sessions']} sessions, {evidence['release']}")
            unit='raise-to bb' if key.startswith('limps') else 'multiple of previous faced raise-to'
            d['response_notes']['sizing_'+key]='Sizing ('+unit+'): '+('; '.join(pieces) if pieces else 'insufficient evidence; legacy size rule retained')+'. Counts describe source pools, not certainty at this seat. Conditional on ordinary raising; hands and stacks pooled; nearest legal non-jam menu projection. Unsupported positions use a pool, not invented positional observations. Retrospective evidence only.'
            if key.startswith('raise_'):d['response_notes']['sizing_'+key]+=' Opening-size response bands share the ordinary 3-bet sizing model.'
            if any(c['requested']!=c['source'] and c['source'] for c in used):d['response_notes']['sizing_'+key]+=' Sparse payment/limper contexts borrow the stated broader source.'
        if 'opening_sizes' in d['response_notes']:
            d['response_notes']['opening_sizes']=d['response_notes']['opening_sizes'].replace('Iso-raises, re-raises and jams retain their existing size rules.','Existing opening mixtures and jam policies are preserved. Other non-jam action sizes now have separate measured distributions.')
            d['response_notes']['sizing_unopened']=d['response_notes']['opening_sizes']
        model['source']['assumptions']=[x.replace('Raise/jam sizing uses the configured menu, not a learned sizing distribution.','Measured non-jam sizing is projected onto the configured menu; jam action probabilities are unchanged.').replace('Jam/iso/re-raise rules unchanged.','Opening size mixture unchanged; see separate non-opening sizing evidence.') for x in model['source']['assumptions']]
        model['source']['version']='2026-09-09-action-sizes-v1';model['source']['assumptions'].append(d['response_notes']['action_sizes']);changed.append(dict(name=model['name'],policies_before=len(original['response_policies']),policies_after=len(policies),coverage=coverage))
    require(len(changed)==1,'Expected one Ignition library model')
    for a,b in zip(before,after):
        if a['stats'].get('dataset',{}).get('site','').startswith('Ignition')==False:require(a==b,'Unrelated model changed')
    write(PRIVATE/'archetypes-candidate.json',after);write(OUT/'export-verification.json',dict(source_library_sha256=sha(LIBRARY),candidate_library_sha256=sha(PRIVATE/'archetypes-candidate.json'),all_opening_policies_preserved=True,all_hand_action_probabilities_preserved=True,other_models_unchanged=True,changed=changed));print('Candidate only:',PRIVATE/'archetypes-candidate.json')

def render(result=None):
    import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
    if result is None:result=json.loads((OUT/'evaluation.json').read_text())
    primary=[g for g in GROUPS if result['groups'][g]['nonjam']];fig,axs=plt.subplots(1,2,figsize=(13,5.7),layout='constrained');pos=np.arange(len(primary));gs=result['groups'];axs[0].barh(pos,[gs[g]['nonjam'] for g in primary],color='#559577',label='Non-jam');axs[0].barh(pos,[gs[g]['jams'] for g in primary],left=[gs[g]['nonjam'] for g in primary],color='#ac6260',label='Jam (excluded from size fit)');axs[0].set_yticks(pos,[g.replace('_',' ') for g in primary]);axs[0].invert_yaxis();axs[0].set_xlabel('Validated opponent raises');axs[0].legend(fontsize=8)
    for i,g in enumerate(primary):
        later=gs[g]['later']
        if not later:continue
        gain=later['log_loss'][0]-later['log_loss'][1];axs[1].plot(gain,i,'o',color='#559577');ci=later['gain_95_interval']
        if ci:axs[1].plot(ci,[i,i],color='#559577')
    axs[1].axvline(0,color='#666');axs[1].set_yticks(pos,[g.replace('_',' ') for g in primary]);axs[1].invert_yaxis();axs[1].set_xlabel('Context sizing log-loss gain vs same-situation pool\nExploratory paired 95% session intervals');fig.suptitle('Action sizing evidence — reused historical evaluation');fig.savefig(OUT/'coverage-and-validation.png',dpi=150);plt.close(fig)
    groups=['iso_1','iso_2','iso_3','threebet','squeeze','reraise'];fig,axs=plt.subplots(2,3,figsize=(12,6.7),layout='constrained')
    for ax,g in zip(axs.ravel(),groups):
        dist=result['distributions'][g];menu=MENUS[dist['basis']];weights=project(dict(dist['pool']),menu);ax.bar(range(len(menu)),100*weights,color='#559577');ax.set_xticks(range(len(menu)),[str(v).removesuffix('.0') for v in menu]);ax.set_title(g.replace('_',' ')+f' (n={gs[g]["nonjam"]})');ax.set_xlabel('Raise-to bb' if dist['basis']=='bb' else 'Multiple of previous raise-to');ax.set_ylabel('% of non-jam raises')
    fig.suptitle('Observed pooled sizes projected onto fixed diagnostic menus');fig.savefig(OUT/'size-distributions.png',dpi=150);plt.close(fig)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['prepare','collect','evaluate','render']);args=ap.parse_args()
    {'prepare':protocol,'collect':collect,'evaluate':evaluate,'render':render}[args.mode]()
