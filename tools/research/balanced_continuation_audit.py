"""Freeze, run and summarize the SB=0.5 fixed-range continuation audit."""
from pathlib import Path
import collections, hashlib, json, os, subprocess, sys
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/continuation/balanced-sb05-20260915'
SEED='balanced-sb05-20260915-v1'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x): Path(p).write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')

def extend():
    """Second predeclared batch: next four hash-ranked boards per stratum."""
    m=json.loads((OUT/'manifest.json').read_text());f=json.loads((OUT/'fixtures.json').read_text())
    groups=collections.defaultdict(list)
    for board,iso in f['canonical_flops']:
        cards=[board[i:i+2] for i in range(0,6,2)]
        key=('paired' if len({c[0] for c in cards})<3 else 'unpaired')+'/'+str(len({c[1] for c in cards}))+'suits'
        groups[key].append((board,iso))
    boards=[]
    for key,items in sorted(groups.items()):
        items.sort(key=lambda x:hashlib.sha256((SEED+x[0]).encode()).digest())
        for board,iso in items[4:8]:
            boards.append(dict(board=board,iso_weight=iso,stratum=key,inclusion_probability=4/len(items)))
    jobs=[]
    for menu in ['half','large']:
        for b in boards:
            for case in ['call','threebet']:
                j=next(j for j in m['jobs'] if j['case']==case and j['menu']==menu)
                j=json.loads(json.dumps(j));j.update(**b,id=f"{case}-{menu}-{b['board']}");j['config']['board']=b['board'];jobs.append(j)
    e={**m,'boards':boards,'jobs':jobs,'parent_manifest_id':m['id'],
       'reason':'Add 20 boards to reduce large pocket-pair sampling uncertainty; no board chosen by outcome. Combined first eight hash-ranked boards per stratum form a 40-board sample.'}
    e.pop('id');e['id']=hashlib.sha256(json.dumps(e,sort_keys=True).encode()).hexdigest()
    d=OUT/'extension';d.mkdir(exist_ok=True)
    if (d/'manifest.json').exists():assert json.loads((d/'manifest.json').read_text())==e
    else:dump(d/'manifest.json',e)
    print('Frozen extension',len(jobs),'jobs',e['id'])

def compatible_raw(case):
    pairs=[(a,b) for a in range(52) for b in range(a+1,52)]
    masks=np.array([(1<<a)|(1<<b) for a,b in pairs],dtype=np.uint64)
    classes=[]
    for a,b in pairs:
        hi,lo=max(a//4,b//4),min(a//4,b//4)
        classes.append(hi*13+lo if a%4==b%4 or hi==lo else lo*13+hi)
    classes=np.array(classes)
    counts=np.zeros((169,169))
    left,right=np.where((masks[:,None]&masks[None,:])==0)
    np.add.at(counts,(classes[left],classes[right]),1)
    assert np.array_equal(counts,counts.T)
    assert counts.sum()==1326*1225
    assert np.array_equal(counts.sum(axis=1),np.bincount(classes,minlength=169)*1225)
    eq=np.frombuffer((ROOT/'cache/preflop_eq169.bin').read_bytes()[4:],dtype='<f4').reshape(169,169).astype(float)
    eq=(eq+1-eq.T)/2
    np.fill_diagonal(eq,.5)
    opponent=np.array(case['weights'][0]);mass=counts*opponent[None,:]
    return case['pot']*(mass*eq).sum(axis=1)/mass.sum(axis=1)

def run():
    binary=ROOT/'target/balanced-continuation-audit-gpu.exe'
    if not binary.exists():binary=ROOT/'target/release/examples/balanced_continuation_audit.exe'
    env=dict(os.environ);env['PATH']=str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env.get('PATH','')
    for path in [OUT/'manifest.json',OUT/'extension/manifest.json']:
        if not path.exists():continue
        m=json.loads(path.read_text())
        assert sha(binary)==m['binary_sha256'],'Different executable: create a separate audit, never mix checkpoints.'
        assert sha(ROOT/'cache/preflop_eq169.bin')==m['equity_sha256']
        assert sha(OUT/'fixtures.json')==m['fixtures_sha256']
        subprocess.run([str(binary),'run',str(path)],cwd=ROOT,env=env,check=True)

def plot():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    s=json.loads((OUT/'summary.json').read_text())
    assert s['completed']==160 and s['all_target_met']
    fig,axes=plt.subplots(1,2,figsize=(12,5),layout='constrained',sharey=True)
    for ax,case,title in zip(axes,['call','threebet'],['After calling the 6bb open','After 3-betting to 18bb and getting called']):
        for menu,dy,color,label in [('half',-.12,'#3877b8','50% pot bets'),('large',.12,'#288455','75% pot bets')]:
            r=next(r for r in s['results'] if r['case']==case and r['menu']==menu)
            v=np.array([h['cv_postflop_bb']-h['balanced_bb'] for h in r['hands']])
            lo=np.array([h['cv_ci95_bb'][0]-h['balanced_bb'] for h in r['hands']])
            hi=np.array([h['cv_ci95_bb'][1]-h['balanced_bb'] for h in r['hands']])
            ax.errorbar(v,np.arange(len(v))+dy,xerr=[v-lo,hi-v],fmt='o',color=color,capsize=3,label=label)
        ax.set_yticks(np.arange(6),[h['hand'] for h in r['hands']]);ax.tick_params(labelleft=True)
        ax.axvline(0,color='#333',lw=1);ax.grid(axis='x',alpha=.2);ax.set_title(title,fontsize=11)
        ax.set_xlabel('Postflop estimate minus Balanced (original bb)');ax.legend(fontsize=9)
    axes[0].invert_yaxis()
    fig.suptitle('Continuation pricing depends on both the hand and the situation',fontsize=14)
    fig.supxlabel('40 sampled flops · equity-adjusted estimates · conditional 95% board-bootstrap intervals\nPositive = Balanced undervalues the hand. These are heads-up continuation values, not full preflop action EVs.',fontsize=9)
    fig.savefig(OUT/'value-errors.png',dpi=160);plt.close(fig)
def prepare():
    fixtures=json.loads((OUT/'fixtures.json').read_text())
    groups=collections.defaultdict(list)
    for board,iso in fixtures['canonical_flops']:
        cards=[board[i:i+2] for i in range(0,6,2)]
        key=('paired' if len({c[0] for c in cards})<3 else 'unpaired')+'/'+str(len({c[1] for c in cards}))+'suits'
        groups[key].append((board,iso))
    assert len(groups)==5
    boards=[]
    for key,items in sorted(groups.items()):
        items.sort(key=lambda x:hashlib.sha256((SEED+x[0]).encode()).digest())
        for board,iso in items[:4]:
            boards.append(dict(board=board,iso_weight=iso,stratum=key,inclusion_probability=4/len(items)))
    jobs=[]
    for menu,bet in [('half',50),('large',75)]:
        for b in boards:
            for case in fixtures['cases']:
                size={'bet':[{'PotPct':bet}],'raise':[{'PotPct':100}],'donk':[{'PotPct':bet}]}
                cfg=dict(board=b['board'],range_oop=case['range_oop'],range_ip=case['range_ip'],tree=dict(
                    starting_pot=case['pot'],effective_stack=case['stack'],rake_pct=0,rake_cap=0,
                    oop=[size]*3,ip=[size]*3,max_raises=1,add_allin=False,allin_threshold=.85))
                jobs.append(dict(**b,case=case['id'],menu=menu,id=f"{case['id']}-{menu}-{b['board']}",config=cfg))
    m=dict(seed=SEED,fixtures_sha256=sha(OUT/'fixtures.json'),save_sha256=sha(ROOT/fixtures['save']),
           binary_sha256=sha(ROOT/'target/release/examples/balanced_continuation_audit.exe'),
           equity_sha256=sha(ROOT/'cache/preflop_eq169.bin'),boards=boards,jobs=jobs,
           target_gap_pct=.1,max_iterations=1000,
           protocol='20 stratified canonical boards, four per pairedness/suit stratum, frozen before outcomes. Weight by suit multiplicity times compatible pair mass / inclusion probability. Same boards for both branches and 50%/75% menus. Turn/river runouts enumerated, one raise per street, no extra jam option. IP tiny-mass probes explicitly reported; IP per-hand best responses measure rare-hand convergence. No full-preflop or multiway replacement.')
    m['id']=hashlib.sha256(json.dumps(m,sort_keys=True).encode()).hexdigest()
    if (OUT/'manifest.json').exists(): assert json.loads((OUT/'manifest.json').read_text())==m
    else: dump(OUT/'manifest.json',m)
    print(f'Frozen {len(jobs)} jobs, manifest {m["id"]}')

def summarize():
    f=json.loads((OUT/'fixtures.json').read_text());m=json.loads((OUT/'manifest.json').read_text())
    assert sha(OUT/'fixtures.json')==m['fixtures_sha256']
    rows=[];batches=[(OUT,m)]
    if (OUT/'extension/manifest.json').exists():
        e=json.loads((OUT/'extension/manifest.json').read_text());assert e['parent_manifest_id']==m['id']
        batches.append((OUT/'extension',e))
    for directory,batch in batches:
        for j in batch['jobs']:
            p=directory/'jobs'/f"{j['id']}.json"
            if not p.exists(): continue
            r=json.loads(p.read_text());assert r['manifest_id']==batch['id'] and r['job']==j
            rows.append(r)
    m={**m,'jobs':[j for _,batch in batches for j in batch['jobs']],'boards':[b for _,batch in batches for b in batch['boards']]}
    out=dict(completed=len(rows),total=len(m['jobs']),all_target_met=all(r['target_met'] for r in rows),results=[])
    rng=np.random.default_rng(15092026)
    board_counts=[]
    for _ in range(2000):
        counts=collections.Counter()
        for group in sorted({b['stratum'] for b in m['boards']}):
            bs=[b['board'] for b in m['boards'] if b['stratum']==group]
            counts.update(rng.choice(bs,len(bs)))
        board_counts.append(counts)
    for case in f['cases']:
        exact_raw=compatible_raw(case)
        for menu in ['half','large']:
            rs=[r for r in rows if r['job']['case']==case['id'] and r['job']['menu']==menu]
            if not rs: continue
            result=dict(case=case['id'],menu=menu,boards=len(rs),pot=case['pot'],hands=[])
            for hand in f['probes']:
                values=[]
                for r in rs:
                    hs=[h for h in r['hands'][1] if h['hand']==hand]
                    if not hs: continue
                    h=hs[0];j=r['job'];weight=j['iso_weight']/j['inclusion_probability']*h['pair_mass']
                    values.append((j['board'],weight,h['ev_bb'],h['br_ev_bb'],h['equity']))
                if not values: continue
                raw_target=exact_raw[next(i for i,h in enumerate(case['balanced']['hands'][1]) if h['hand']==hand)]
                def mean(counts=None,br=False,cv=False):
                    den=sum(w*(1 if counts is None else counts[b]) for b,w,ev,bv,eq in values)
                    if den==0:return None
                    return sum(w*(1 if counts is None else counts[b])*((bv if br else ev)-(case['pot']*eq if cv else 0)) for b,w,ev,bv,eq in values)/den+(raw_target if cv else 0)
                boot=[v for c in board_counts if (v:=mean(c)) is not None]
                balanced=next(h['value_bb'] for h in case['balanced']['hands'][1] if h['hand']==hand)
                raw=next(h['raw_bb'] for h in case['balanced']['hands'][1] if h['hand']==hand)
                lo,hi=np.percentile(boot,[2.5,97.5])
                cv_boot=[v for c in board_counts if (v:=mean(c,cv=True)) is not None]
                result['hands'].append(dict(hand=hand,balanced_bb=balanced,raw_bb=raw,postflop_bb=mean(),
                    postflop_br_bb=mean(br=True),delta_bb=mean()-balanced,ci95_bb=[lo,hi],
                    delta_ci95_bb=[lo-balanced,hi-balanced],mean_br_gain_bb=mean(br=True)-mean()))
                result['hands'][-1].update(compatible_raw_bb=raw_target,cv_postflop_bb=mean(cv=True),cv_ci95_bb=list(np.percentile(cv_boot,[2.5,97.5])))
            weights=[r['job']['iso_weight']/r['job']['inclusion_probability']*r['pair_mass'] for r in rs]
            result['mean_ip_bb']=sum(w*r['means_bb'][1] for w,r in zip(weights,rs))/sum(weights)
            result['balanced_mean_ip_bb']=case['balanced']['mean_bb'][1]
            out['results'].append(result)
    dump(OUT/'summary.json',out)
    print(json.dumps(out,indent=2))

def sensitivity():
    f=json.loads((OUT/'fixtures.json').read_text());s=json.loads((OUT/'summary.json').read_text())
    d=json.loads((OUT/'decision-node.json').read_text(encoding='utf-8-sig'))
    a=json.loads((OUT/'action-evs.json').read_text())
    assert d['config']==f['config']==a['config'] and d['iteration']==f['iteration']==a['iteration']
    assert s['completed']==s['total'] and s['all_target_met']
    rows=[]
    for c in f['cases']:
        index=1 if c['id']=='call' else 2
        probability=c['branch_probability']/(d['branch_probability']*d['actions'][index]['freq'])
        assert 0<probability<1
        for r in s['results']:
            if r['case']!=c['id']:continue
            for h in r['hands']:
                original=next(x['value_bb'] for x in c['original_balanced']['hands'][1] if x['hand']==h['hand'])
                ev=next(x['actions'][index]['ev_bb'] for x in a['hands'] if x['hand']==h['hand'])
                rows.append(dict(case=c['id'],menu=r['menu'],hand=h['hand'],terminal_probability=probability,
                    original_action_ev_bb=ev,
                    substituted_action_ev_bb=ev+probability*(h['postflop_bb']-original),
                    cv_substituted_action_ev_bb=ev+probability*(h['cv_postflop_bb']-original),
                    cv_ci95_bb=[ev+probability*(x-original) for x in h['cv_ci95_bb']]))
    dump(OUT/'sensitivity.json',dict(scope='Arithmetic one-terminal replacement against frozen opponents. Other HU, multiway, folds and re-raises retain old prices. No new equilibrium, no production changes. Compatible-card reference versus original marginal model; tiny probe/truncation changes retained.',rows=rows))
    for r in rows:
        if r['menu']=='half':print(r['case'],r['hand'],round(r['terminal_probability'],4),round(r['original_action_ev_bb'],3),round(r['cv_substituted_action_ev_bb'],3))

if __name__=='__main__':
    {'prepare':prepare,'extend':extend,'summarize':summarize,'sensitivity':sensitivity,'run':run,'plot':plot}[sys.argv[1]]()
