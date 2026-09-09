"""Frozen saved-game continuation validation. No fitting or live app mutations."""
from pathlib import Path
import argparse, hashlib, json, os, re, subprocess, time
from datetime import datetime, timezone
import numpy as np
import continuation_joint as base
ROOT=base.ROOT
OUT=ROOT/'research/preflop-evolution/continuation/pass3'
CANDIDATE=ROOT/'research/preflop-evolution/continuation/pass2/joint-v1.json'
SEED='gtopen-saved-continuation-v3-20260909'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(c,m):
    if not c: raise ValueError(m)
def texture(cards):
    return ('paired' if len({c//4 for c in cards})<3 else 'unpaired')+'/'+{1:'mono',2:'two-tone',3:'rainbow'}[len({c%4 for c in cards})]
def validate_suit_symmetric_ranges(ranges):
    for pair in ranges.values():
        for seat in ['oop','ip']:
            require(all(re.fullmatch(r'[2-9TJQKA]{2}[so]?(?::(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+))?', t.strip()) for t in pair[seat].split(',')), 'Canonical board sampling requires suit-symmetric class ranges')

def manifest():
    m=json.loads((OUT/'manifest.json').read_text())
    unsigned={k:v for k,v in m.items() if k!='id'}
    require(hashlib.sha256(json.dumps(unsigned,sort_keys=True).encode()).hexdigest()==m['id'],'manifest altered')
    require(sha(CANDIDATE)==m['candidate_sha256'],'frozen candidate altered')
    validate_suit_symmetric_ranges(m['ranges'])
    return m

def prepare():
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'manifest.json').exists(): manifest(); return
    scenarios={}
    for key,stack in [('2-2',150),('2-5',200)]:
        ps=[p for p in (ROOT/'saves/scenarios').glob('*.json') if json.loads(p.read_text()).get('stack')==stack and f'${key.replace("-","/")}' in json.loads(p.read_text()).get('name','')]
        require(len(ps)==1,f'Expected unique saved scenario {key}')
        p=ps[0]; scenarios[key]=dict(fields=json.loads(p.read_text()),sha256=sha(p))
    reports=list((ROOT/'saves/reports').glob('*.json'))
    iso_reports=[p for p in reports if p.name.startswith('overnight') and ' A BTN iso-' in p.name and 'GTO postflop' in p.name]
    require(len(iso_reports)==1,'Expected unique saved overnight iso-call GTO report')
    ipath=iso_reports[0]
    tpath=ROOT/'saves/reports/BB 3-bets BTN 4x - 2-2 150bb 10pct rake.json'
    ranges={}
    for key,p in [('iso_call',ipath),('threebet_call',tpath)]:
        s=json.loads(p.read_text())['spot']
        ranges[key]=dict(oop=s['range_oop'],ip=s['range_ip'],source_sha256=sha(p),source_description='Saved $2/2 report: '+('MP limp-calls BTN isolation' if key=='iso_call' else 'BB 3-bets and BTN calls'),source_pot=s['starting_pot'],source_stack=s['effective_stack'])
    validate_suit_symmetric_ranges(ranges)
    prior=json.loads((base.OUT/'manifest.json').read_text())
    excluded={b['board'] for b in prior['boards']}|set(prior['excluded_old_boards'])
    groups={}
    for cards,mult in base.canonical_inventory().items():
        if base.label(cards) not in excluded: groups.setdefault(texture(cards),[]).append((cards,mult))
    boards=[]
    for group,rows in sorted(groups.items()):
        rows.sort(key=lambda x:hashlib.sha256((SEED+base.label(x[0])).encode()).digest())
        for cards,mult in rows[:3]: boards.append(dict(board=base.label(cards),iso_weight=mult,stratum=group,population_in_stratum=len(rows),inclusion_probability=3/len(rows)))
    require(len(boards)==15 and len(groups)==5,'texture sample incorrect')
    cases=[]
    for game,item in scenarios.items():
        s=item['fields']; opening=min(float(x) for x in s['opens'].split(',')); sb=s['smallBlind']/s['bigBlind']
        for line,r in ranges.items():
            to=opening if line=='iso_call' else opening*min(float(x) for x in s['mult'].split(','))
            pot=2*to+(sb+1 if line=='iso_call' else sb)
            for menu,bet in [('half_pot',50),('large_bet',75)]:
                cases.append(dict(id=f'{game}-{line}-{menu}',game=game,line=line,menu=menu,bet_pct=bet,pot=pot,stack=s['stack']-to,rake_pct=s['rakePct'],rake_cap=s['rakeCap'],range_oop=r['oop'],range_ip=r['ip']))
        c=next(c for c in cases if c['game']==game and c['line']=='iso_call' and c['menu']=='half_pot').copy()
        c.update(id=f'{game}-iso_call-zero_rake',rake_pct=0,menu='zero_rake_control'); cases.append(c)
    jobs=[]
    for b in boards:
        for c in cases:
            size={'bet':[{'PotPct':c['bet_pct']}],'raise':[{'PotPct':100}],'donk':[]}
            config=dict(board=b['board'],range_oop=c['range_oop'],range_ip=c['range_ip'],tree=dict(starting_pot=c['pot'],effective_stack=c['stack'],rake_pct=c['rake_pct']/100,rake_cap=c['rake_cap'],oop=[size]*3,ip=[size]*3,max_raises=1,add_allin=False,allin_threshold=.85))
            jobs.append(dict(**b,id=c['id']+'-'+b['board'],case=c['id'],partition='validation',config=config))
    m=dict(schema=1,created_utc=datetime.now(timezone.utc).isoformat(),seed=SEED,candidate_sha256=sha(CANDIDATE),candidate_version='continuation-joint-research-v1',scenarios=scenarios,ranges=ranges,cases=cases,boards=boards,jobs=jobs,excluded_boards=sorted(excluded),population_size=1720,reference_target_gap_pct=.3,reference_max_iterations=750,threads_per_worker=4,workers=2,bootstrap_replicates=2000,bootstrap_seed=9300926,protocol='All jobs are validation; joint-v1 remains frozen. 3 uniformly sampled unseen canonical boards per pairedness/suit stratum. Weight by suit multiplicity * compatible pair mass / inclusion probability; ratio estimate. Resample boards within strata jointly across configurations. No outcome-based exclusions. Primary eight raked configurations equally weighted in percent-pot MAE; two matched zero-rake controls are separate. Exact saved game stack/blind/rake/open settings; transported old $2/2 reaching ranges, not freshly solved $2/5 ranges. Fixed one-raise 50%/75%-pot menus are abstractions, not full games.')
    require(sum(len(x) for x in groups.values())==1720,'unexpected unseen universe')
    m['id']=hashlib.sha256(json.dumps(m,sort_keys=True).encode()).hexdigest()
    (OUT/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    (OUT/'.gitignore').write_text('worker-*.log\n*.partial\n')
    (OUT/'.gitattributes').write_text('*.json -text\nrecorded-example.rs -text\n')
    print(json.dumps({k:m[k] for k in ['id','candidate_sha256','created_utc']},indent=2)); print('Frozen',len(jobs),'jobs')

def load(complete=False):
    m=manifest(); rows=[]; sig=set()
    for j in m['jobs']:
        p=OUT/'jobs'/(j['id']+'.json')
        if not p.exists(): continue
        r=json.loads(p.read_text())
        # serde_json may round the sampling fraction by one binary64 ULP.
        # Every solve-setting field must still match exactly.
        recorded=dict(r['job']); fraction=recorded.pop('inclusion_probability'); frozen=dict(j); expected=frozen.pop('inclusion_probability')
        require(recorded==frozen and abs(fraction-expected)<=1e-15 and r['manifest_id']==m['id'],'checkpoint mismatch')
        r['job']=j
        require(r['target_met'] and 0<=r['gap_pct_pot']<=m['reference_target_gap_pct'],'reference target not met')
        require(len(r['reference_ev_bb'])==2 and np.isfinite(r['reference_ev_bb']).all() and np.isfinite(r['compatible_pair_mass']) and r['compatible_pair_mass']>0,'invalid reference')
        tree=j['config']['tree']; drain=r['reference_expected_rake_bb']
        maximum=min(tree['rake_cap'] if tree['rake_cap']>0 else float('inf'),(tree['starting_pot']+2*tree['effective_stack'])*tree['rake_pct'])
        require(np.isfinite(drain) and -.001<=drain<=maximum+.001,'invalid expected rake')
        require(abs(sum(r['reference_ev_bb'])+drain-tree['starting_pot'])<.001,'reference accounting mismatch')
        require(bool(r.get('provenance',{}).get('binary_sha256')),'missing executable provenance')
        r['weight']=j['iso_weight']*r['compatible_pair_mass']/j['inclusion_probability']; rows.append(r)
        sig.add(base.provenance_signature(r['provenance']))
    require(len(sig)<=1,'mixed binaries/caches')
    if complete: require(len(rows)==len(m['jobs']),'incomplete corpus')
    return m,rows

def aggregate(m,rows,counts=None):
    model=json.loads(CANDIDATE.read_text())['parameters']; result=[]
    for c in m['cases']:
        rs=[r for r in rows if r['job']['case']==c['id']]
        require(bool(rs),'missing configuration')
        for key in ['equity','raw_bb','static_bb','calibrated_bb']:
            values=np.asarray([r['preflop_leaf'][key] for r in rs],dtype=float)
            require(values.shape==(len(rs),2) and np.isfinite(values).all() and np.max(np.abs(values-values[0]))<=1e-12,'preflop input changed across boards')
        w=np.array([r['weight']*(1 if counts is None else counts.get(r['job']['board'],0)) for r in rs],dtype=float);w/=w.sum()
        ref=np.average([r['reference_ev_bb'] for r in rs],axis=0,weights=w)
        pred={k:np.average([r['preflop_leaf'][k+'_bb'] for r in rs],axis=0,weights=w) for k in ['raw','static','calibrated']}
        joint,rake=base.predict(rs[0],model);pred['joint']=joint
        result.append(dict(case=c['id'],game=c['game'],line=c['line'],menu=c['menu'],pot=c['pot'],stack=c['stack'],spr=c['stack']/c['pot'],reference_ev_bb=ref.tolist(),reference_rake_bb=float(np.average([r['reference_expected_rake_bb'] for r in rs],weights=w)),joint_rake_bb=rake,predicted_ev_bb={k:v.tolist() for k,v in pred.items()},mae_bb={k:float(np.abs(v-ref).mean()) for k,v in pred.items()},mae_pct_pot={k:float(np.abs(v-ref).mean()/c['pot']*100) for k,v in pred.items()}))
    return result

def progress():
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    m,rs=load(); p=dict(completed=len(rs),total=len(m['jobs']),target_met=len(rs),updated_utc=datetime.now(timezone.utc).isoformat())
    (OUT/'progress.json').write_text(json.dumps(p,indent=2)+'\n')
    if not rs:return
    fig,ax=plt.subplots(figsize=(9,3));ax.plot(range(1,len(rs)+1),[r['gap_pct_pot'] for r in rs],'.',color='#479eaa');ax.axhline(.3,color='#d75e65',ls='--');ax.set(xlabel='Completed reference (manifest order)',ylabel='Gap (% pot)',title=f'Saved-game validation: {len(rs)} / {len(m["jobs"])} references');fig.tight_layout();fig.savefig(OUT/'progress.png',dpi=150);plt.close(fig)

def report():
    m,rs=load(True)
    corpus=dict(manifest_id=m['id'],candidate_sha256=m['candidate_sha256'],checkpoint_sha256={r['job']['id']:sha(OUT/'jobs'/(r['job']['id']+'.json')) for r in rs})
    accepted=OUT/'accepted-corpus.json'
    if accepted.exists():require(json.loads(accepted.read_text())==corpus,'accepted corpus bytes changed')
    else:accepted.write_text(json.dumps(corpus,indent=2)+'\n')
    groups=aggregate(m,rs); primary=[g for g in groups if g['menu']!='zero_rake_control']; keys=['raw','static','calibrated','joint'];mean={k:float(np.mean([g['mae_pct_pot'][k] for g in primary])) for k in keys}
    rng=np.random.default_rng(m['bootstrap_seed']); draws=[]
    for _ in range(m['bootstrap_replicates']):
        counts={}
        for st in sorted({b['stratum'] for b in m['boards']}):
            choices=[b['board'] for b in m['boards'] if b['stratum']==st]
            for b in rng.choice(choices,len(choices),replace=True):counts[b]=counts.get(b,0)+1
        gs=[g for g in aggregate(m,rs,counts) if g['menu']!='zero_rake_control']
        draws.append({k:float(np.mean([g['mae_pct_pot'][k]-g['mae_pct_pot']['joint'] for g in gs])) for k in keys[:-1]})
    intervals={k:[float(x) for x in np.quantile([d[k] for d in draws],[.025,.975])] for k in keys[:-1]}
    e=dict(schema=1,status='complete',manifest_id=m['id'],candidate_sha256=m['candidate_sha256'],groups=groups,primary_mae_pct_pot=mean,joint_gain_pct_pot_ci95=intervals,completed=len(rs),all_targets_met=True,max_gap_pct_pot=max(r['gap_pct_pot'] for r in rs),max_arena_mib=max(r['arena_bytes'] for r in rs)/2**20,summed_job_seconds=sum(r['build_seconds']+r['solve_seconds']+r['query_seconds'] for r in rs),promotion=False,limitation='15 unseen boards, 3 per stratum; uncertainty conditional on transported fixed ranges and restricted menus. No production promotion; intervals do not include model fit uncertainty.',source_hashes={'tool':sha(__file__),'candidate':sha(CANDIDATE),'accepted_corpus':sha(accepted)})
    e['texture_expectations']={st:aggregate(m,[r for r in rs if r['job']['stratum']==st]) for st in sorted({b['stratum'] for b in m['boards']})}
    e['texture_note']='Conditional texture diagnostics, not the primary preflop-error score. A preflop value estimate does not know the future texture.'
    e['rake_controls']=[]
    for game in ['2-2','2-5']:
        a=next(g for g in groups if g['case']==game+'-iso_call-half_pot');b=next(g for g in groups if g['case']==game+'-iso_call-zero_rake')
        e['rake_controls'].append(dict(game=game,reference_ev_change_bb=(np.array(a['reference_ev_bb'])-b['reference_ev_bb']).tolist(),joint_ev_change_bb=(np.array(a['predicted_ev_bb']['joint'])-b['predicted_ev_bb']['joint']).tolist(),calibrated_ev_change_bb=(np.array(a['predicted_ev_bb']['calibrated'])-b['predicted_ev_bb']['calibrated']).tolist(),zero_rake_calibrated_unallocated_bb=b['pot']-sum(b['predicted_ev_bb']['calibrated'])))
    e['menu_changes']=[]
    for game in ['2-2','2-5']:
        for line in ['iso_call','threebet_call']:
            a=next(g for g in groups if g['case']==game+'-'+line+'-half_pot');b=next(g for g in groups if g['case']==game+'-'+line+'-large_bet')
            require(np.max(np.abs(np.array(a['predicted_ev_bb']['joint'])-b['predicted_ev_bb']['joint']))<1e-12,'candidate unexpectedly depends on menu')
            e['menu_changes'].append(dict(game=game,line=line,reference_ev_change_bb=(np.array(b['reference_ev_bb'])-a['reference_ev_bb']).tolist(),joint_ev_change_bb=[0,0],reference_rake_change_bb=b['reference_rake_bb']-a['reference_rake_bb']))
    (OUT/'evaluation.json').write_text(json.dumps(e,indent=2)+'\n');charts(e);write_results(e);progress();print(json.dumps({k:e[k] for k in ['completed','primary_mae_pct_pot','joint_gain_pct_pot_ci95']},indent=2))

def write_results(e):
    keys=['raw','static','calibrated','joint']
    lines=['# Saved-game validation results','', '**Completed: 150 / 150 references. The joint-v1 candidate remains research-only.**','', 'The primary metric is absolute error of the weighted preflop expectation, averaged across both players and the eight raked configurations. Percent-pot scores give each configuration equal weight. These are restricted heads-up postflop references using transported saved ranges, not freshly solved full preflop games.','', '| Model | Mean error, % starting pot |','|---|---:|']
    lines += [f"| {k.title()} | {e['primary_mae_pct_pot'][k]:.3f} |" for k in keys]
    lines += ['', 'Positive gain favors joint. Conditional paired 95% board-bootstrap intervals:', '', '| Comparator | Joint gain, percentage points of pot | 95% interval |','|---|---:|---:|']
    for k in keys[:-1]:
        lo,hi=e['joint_gain_pct_pot_ci95'][k];gain=e['primary_mae_pct_pot'][k]-e['primary_mae_pct_pot']['joint'];lines.append(f'| {k.title()} | {gain:.3f} | {lo:.3f} to {hi:.3f} |')
    lines += ['', '**The average improvement is not universal.** Current calibrated realization is better in both $2/5 3-bet/call fixtures: its MAE is 0.009 / 0.019 bb, versus joint 0.186 / 0.170 bb for the 50% / 75% bet menus. The joint candidate improves the aggregate by 37.3% versus static and 39.1% versus calibrated in this limited sample, but these exceptions and transported-range limitations rule out a blanket replacement.', '', '![Value errors by saved-game fixture](value-errors.png)', '', '![Paired gain intervals](gain-intervals.png)', '', '## Individual configurations', '', '| Configuration | SPR | Raw MAE, bb | Static MAE, bb | Calibrated MAE, bb | Joint MAE, bb |','|---|---:|---:|---:|---:|---:|']
    for g in e['groups']:
        cells=' | '.join(f"{g['mae_bb'][k]:.3f}" for k in keys);lines.append(f"| {g['case']} | {g['spr']:.2f} | {cells} |")
    lines += ['', '## Rake and bet-menu controls', '', 'The zero-rake controls are excluded from the primary score. The current calibrated model does not respond to the requested rake: its OOP/IP predictions are unchanged between each matched pair. Its combined-value deficit at zero rake is therefore not expected rake.', '', '| Game | Calibrated unallocated value at zero rake, bb | Reference OOP change with rake, bb | Reference IP change with rake, bb |', '|---|---:|---:|---:|']
    for c in e['rake_controls']:lines.append(f"| ${c['game'].replace('-', '/')} | {c['zero_rake_calibrated_unallocated_bb']:.3f} | {c['reference_ev_change_bb'][0]:+.3f} | {c['reference_ev_change_bb'][1]:+.3f} |")
    lines += ['', '![Expected rake comparison](rake.png)', '', 'The frozen joint model has no bet-menu input. The following observed shifts therefore cannot be represented by it:', '', '| Game / line | OOP value change, 75% minus 50% bet, bb | IP value change, bb |','|---|---:|---:|']
    for c in e['menu_changes']:lines.append(f"| {c['game']} / {c['line']} | {c['reference_ev_change_bb'][0]:+.3f} | {c['reference_ev_change_bb'][1]:+.3f} |")
    lines += ['', 'Per-texture conditional expectations, all baseline prices and raw checkpoint provenance are retained in `evaluation.json`. They are diagnostics, not a demand that a preflop estimate anticipate the future texture.', '', '## Precision and limitations', '', f"All references reached the frozen 0.3%-pot target; maximum observed gap {e['max_gap_pct_pot']:.6f}% pot. Maximum solver arena {e['max_arena_mib']:.1f} MiB. Summed build/solve/query time {e['summed_job_seconds']/60:.1f} minutes overlaps across two four-thread workers; it is not end-to-end latency.", '', 'Only 15 independent boards (three per texture stratum) are sampled. The intervals condition on the frozen fit and these two transported reaching ranges. They exclude uncertainty about range construction, residual reference-solve error, opponent adaptation, folded-card removal and a richer postflop betting tree. The small sample does not validate all $2/2 or $2/5 situations. No model is promoted or installed from this test.', '', 'See [the frozen protocol](README.md) for the exact source settings, board population, weighting and reproduction commands.', '']
    (OUT/'RESULTS.md').write_text('\n'.join(lines))


def charts(e):
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    keys=['raw','static','calibrated','joint'];colors=['#929baa','#629fbe','#ba835d','#63ad84']
    gs=[g for g in e['groups'] if g['menu']!='zero_rake_control']
    fig,ax=plt.subplots(figsize=(11,5));x=np.arange(len(gs))
    for i,k in enumerate(keys):ax.bar(x+(i-1.5)*.19,[g['mae_pct_pot'][k] for g in gs],width=.19,label=k,color=colors[i])
    ax.set_xticks(x,[g['case'].replace('-iso_call','\niso call').replace('-threebet_call','\n3-bet call').replace('-half_pot','\n50% bet').replace('-large_bet','\n75% bet') for g in gs],fontsize=8);ax.set(ylabel='Weighted expectation MAE (% starting pot)',title='Frozen continuation models on saved-game settings');ax.legend(ncol=4);fig.tight_layout();fig.savefig(OUT/'value-errors.png',dpi=150);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,3.5))
    for i,k in enumerate(keys[:-1]):
        point=e['primary_mae_pct_pot'][k]-e['primary_mae_pct_pot']['joint'];lo,hi=e['joint_gain_pct_pot_ci95'][k];ax.plot([lo,hi],[i,i],color=colors[i],lw=4);ax.plot(point,i,'o',color='black')
    ax.axvline(0,color='gray',ls='--');ax.set_yticks(range(3),['vs raw','vs static','vs calibrated']);ax.set(xlabel='MAE reduction (% pot); positive favors joint',title='Paired 95% board-bootstrap intervals');fig.tight_layout();fig.savefig(OUT/'gain-intervals.png',dpi=150);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,4));x=np.arange(len(gs));ax.bar(x-.17,[g['reference_rake_bb'] for g in gs],width=.34,label='Reference',color='#629fbe');ax.bar(x+.17,[g['joint_rake_bb'] for g in gs],width=.34,label='Frozen joint',color='#63ad84');ax.set_xticks(x,[g['case'].replace('-iso_call','\niso call').replace('-threebet_call','\n3-bet call').replace('-half_pot','\n50% bet').replace('-large_bet','\n75% bet') for g in gs],fontsize=8);ax.set(ylabel='Expected rake (bb)',title='Rake across saved games and bet menus');ax.legend();fig.tight_layout();fig.savefig(OUT/'rake.png',dpi=150);plt.close(fig)

def run():
    m,rs=load()
    if len(rs)==len(m['jobs']):report();return
    binary=ROOT/'target/release/examples/continuation_saved.exe'; require(binary.exists(),'Build continuation_saved')
    prov=dict(started_utc=datetime.now(timezone.utc).isoformat(),binary_sha256=sha(binary),source_sha256={p:sha(ROOT/p) for p in ['crates/solver/examples/continuation_saved.rs','cache/realization_fit.json','cache/preflop_eq169.bin']})
    if rs:require(base.provenance_signature(prov)==base.provenance_signature(rs[0]['provenance']),'resume provenance changed')
    (OUT/'run.json').write_text(json.dumps(prov,indent=2)+'\n');(OUT/'recorded-example.rs').write_bytes((ROOT/'crates/solver/examples/continuation_saved.rs').read_bytes())
    active=[]
    try:
        for shard in range(2):
            log=(OUT/f'worker-{shard}.log').open('a');env=dict(os.environ,CONTINUATION_SHARD=str(shard),CONTINUATION_SHARDS='2',CONTINUATION_PROVENANCE=json.dumps(prov));env.pop('CONTINUATION_PARTITION',None);env.pop('CONTINUATION_JOB_LIMIT',None)
            p=subprocess.Popen([str(binary)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0);active.append((p,log));print('Started',p.pid,flush=True)
        last=-1
        while active:
            for p,log in list(active):
                code=p.poll()
                if code is not None:log.close();active.remove((p,log));require(code==0,f'worker failed {code}')
            count=len(list((OUT/'jobs').glob('*.json')))
            if count!=last:progress();print('Completed',count,'/',len(m['jobs']),flush=True);last=count
            if active:time.sleep(5)
    finally:
        for p,log in active:p.terminate();p.wait();log.close()
    report()
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['prepare','run','report','progress']);args=ap.parse_args();globals()[args.command]()
