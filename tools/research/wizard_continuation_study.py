"""Isolated fixed-range Wizard-baseline audit. No live-server writes."""
import collections
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/preflop-evolution/wizard-continuation-20260919'
BASE = OUT.parent / 'wizard-baseline-20260919'
BINARY = ROOT / 'target/release/examples/wizard_continuation_audit.exe'
SAVE = ROOT / 'saves/preflop/wizard-nl25-baseline-20260919-refined.gtop'
SEED = 'wizard-fixed-ranges-20260919-v1'


def read(p): return json.loads(p.read_text(encoding='utf-8'))
def write(p, data): p.write_text(json.dumps(data, indent=2, allow_nan=False)+'\n', encoding='utf-8', newline='\n')
def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def idle():
    states = {}
    for key, endpoint in [('preflop', 'preflop/status'), ('postflop', 'status'), ('reports', 'reports/status')]:
        with urllib.request.urlopen('http://localhost:56708/api/'+endpoint, timeout=15) as response:
            states[key] = json.load(response)
    return all(s.get('state', '') not in ('running', 'building', 'solving') and not s.get('running', False) for s in states.values()), states


def prepare():
    assert not (OUT/'manifest.json').exists(), 'Do not overwrite the frozen study'
    assert sha(SAVE) == read(BASE/'save-provenance.json')['sha256']
    if not (OUT/'fixtures.json').exists():
        subprocess.run([str(BINARY), 'prepare', str(SAVE), str(OUT/'fixtures.json')], cwd=ROOT, check=True)
    f = read(OUT/'fixtures.json'); case, = f['cases']
    assert f['iteration'] == 1000 and f['config']['rake_pct'] == 4 and f['config']['rake_cap'] == 6
    assert case['path'] == [1, 2, 0, 0, 0, 0, 0, 0, 1]
    assert abs(case['pot']-39.5) < 1e-9 and case['stack'] == 182
    groups = collections.defaultdict(list)
    for board, iso in f['canonical_flops']:
        cards = [board[i:i+2] for i in range(0,6,2)]
        key = ('paired' if len({c[0] for c in cards}) < 3 else 'unpaired')+'/'+str(len({c[1] for c in cards}))
        groups[key].append((board,iso))
    assert len(groups) == 5
    boards=[]
    for group, items in sorted(groups.items()):
        items.sort(key=lambda x: hashlib.sha256((SEED+x[0]).encode()).digest())
        for i,(board,iso) in enumerate(items[:8]):
            boards.append(dict(board=board,iso_weight=iso,stratum=group,inclusion_probability=8/len(items),panel=i//4))
    jobs=[]
    for panel in (0,1):
        for b in (b for b in boards if b['panel'] == panel):
            for menu,bet in [('half',50),('large',75)]:
                sizing={'bet':[{'PotPct':bet}],'raise':[{'PotPct':100}],'donk':[{'PotPct':bet}]}
                tree=dict(starting_pot=case['pot'],effective_stack=case['stack'],rake_pct=.04,rake_cap=6,
                          oop=[sizing]*3,ip=[sizing]*3,max_raises=1,add_allin=False,allin_threshold=.85)
                jobs.append(dict(**b,id=f"{menu}-{b['board']}",menu=menu,case=case['id'],
                    config=dict(board=b['board'],range_oop=case['range_oop'],range_ip=case['range_ip'],tree=tree)))
    inputs=[BINARY, SAVE, OUT/'fixtures.json', OUT/'PROTOCOL.md', ROOT/'cache/preflop_eq169.bin', ROOT/'cache/realization_fit.json', ROOT/'crates/solver/examples/wizard_continuation_audit.rs']
    m=dict(registered_utc=dt.datetime.now(dt.timezone.utc).isoformat(),seed=SEED,boards=boards,jobs=jobs,
           target_gap_pct=.05,max_iterations=2000,probe_br_gain_limit_bb=.05,
           inputs={p.relative_to(ROOT).as_posix():sha(p) for p in inputs})
    m['id']=hashlib.sha256(json.dumps(m,sort_keys=True).encode()).hexdigest()
    write(OUT/'manifest.json',m)
    print('Frozen',len(jobs),'jobs;',case['removed_mass_fraction'],case['probe_added_mass_fraction'],flush=True)


def same_job(a,b):
    aa,bb=dict(a),dict(b)
    av,bv=aa.pop('inclusion_probability'),bb.pop('inclusion_probability')
    return aa == bb and abs(av-bv) <= 2*max(math.ulp(av),math.ulp(bv))


def validate(r,j,m):
    assert r['manifest_id'] == m['id'] and same_job(r['job'],j)
    assert r['query_mode'] == 'materialized_full_enumeration'
    assert r['target_met'] and max(r['gap_pct'],r['gpu_gap_pct']) <= m['target_gap_pct']
    pot=j['config']['tree']['starting_pot']
    rake=pot-sum(r['means_bb'])
    assert -.002 <= rake <= 6.002 and abs(rake-r['expected_rake_bb']) < 1e-6
    for hands in r['hands']:
        mass=sum(h['pair_mass'] for h in hands)
        assert abs(mass/r['pair_mass']-1) < 1e-5
        for h in hands:
            assert np.isfinite([h['pair_mass'],h['ev_bb'],h['br_ev_bb'],h['equity']]).all()


def checked():
    m=read(OUT/'manifest.json')
    assert hashlib.sha256(json.dumps({k:v for k,v in m.items() if k!='id'},sort_keys=True).encode()).hexdigest() == m['id']
    for p,digest in m['inputs'].items(): assert sha(ROOT/p) == digest,p
    return m


def run():
    import msvcrt
    lock=(OUT/'run.lock').open('a+b'); lock.seek(0); lock.write(b'0');lock.flush();lock.seek(0)
    msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    m=checked()
    env=dict(os.environ);env['PATH']=str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env.get('PATH','')
    for i,j in enumerate(m['jobs']):
        dest=OUT/'jobs'/f"{j['id']}.json"
        if dest.exists(): validate(read(dest),j,m);continue
        free,states=idle()
        while not free:
            write(OUT/'status.json',dict(stage='waiting_for_live_app',job=j['id']))
            time.sleep(30);free,states=idle()
        write(OUT/'status.json',dict(stage='solving',job=j['id'],completed=i,total=len(m['jobs'])))
        with (OUT/(j['id']+'.log')).open('w') as log:
            subprocess.run([str(BINARY),'run',str(OUT/'manifest.json'),'1'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        validate(read(dest),j,m)
        print('Completed',i+1,'/',len(m['jobs']),j['id'],flush=True)
    summarize()
    write(OUT/'status.json',dict(stage='ready_for_review',completed=len(m['jobs'])))


def compatible_equity(case):
    pairs=[(a,b) for a in range(52) for b in range(a+1,52)]
    masks=np.array([(1<<a)|(1<<b) for a,b in pairs],dtype=np.uint64)
    classes=np.array([max(a//4,b//4)*13+min(a//4,b//4) if a%4==b%4 or a//4==b//4 else min(a//4,b//4)*13+max(a//4,b//4) for a,b in pairs])
    counts=np.zeros((169,169));a,b=np.where((masks[:,None]&masks[None,:])==0)
    np.add.at(counts,(classes[a],classes[b]),1)
    assert counts.sum()==1326*1225
    eq=np.frombuffer((ROOT/'cache/preflop_eq169.bin').read_bytes()[4:],dtype='<f4').reshape(169,169).astype(float)
    eq=(eq+1-eq.T)/2;np.fill_diagonal(eq,.5)
    mass=counts*np.array(case['weights'][1])[None,:]
    return (mass*eq).sum(axis=1)/mass.sum(axis=1)


def summarize(use_precision=False):
    m=read(OUT/'manifest.json');f=read(OUT/'fixtures.json');case,=f['cases']
    rows=[]
    pm=read(OUT/'precision/manifest.json') if use_precision else None
    if pm:
        assert pm['parent_manifest_id']==m['id']
    for j in m['jobs']:
        path=OUT/'jobs'/f"{j['id']}.json"
        if path.exists():
            r=read(path);validate(r,j,m)
            if pm and any(pj['id']==j['id'] for pj in pm['jobs']):
                better=read(OUT/'precision/jobs'/f"{j['id']}.json")
                validate(better,j,pm)
                assert better['max_probe_br_gain_bb']<=pm['probe_br_gain_limit_bb']
                r=better
            rows.append(r)
    if len(rows)!=len(m['jobs']):
        write(OUT/'partial.json',dict(completed=len(rows),total=len(m['jobs']),note='No all-board estimate from incomplete panel'))
        return
    boards=m['boards']; index={b['board']:i for i,b in enumerate(boards)}
    rng=np.random.default_rng(19092026);draws=np.zeros((5000,len(boards)))
    for group in sorted({b['stratum'] for b in boards}):
        indices=[i for i,b in enumerate(boards) if b['stratum']==group]
        for row in draws:
            np.add.at(row,rng.choice(indices,len(indices)),1)
    eq=compatible_equity(case);results=[]
    for menu in ('half','large'):
        rr=[r for r in rows if r['job']['menu']==menu]
        for hand in f['probes']:
            mass=np.zeros(len(boards));ev=mass.copy();residual=mass.copy();br=mass.copy()
            class_id=next(i for i,h in enumerate(case['balanced']['hands'][0]) if h['hand']==hand)
            gains=[]
            for r in rr:
                h=next((h for h in r['hands'][0] if h['hand']==hand),None)
                if h is None:continue
                i=index[r['job']['board']]; w=r['job']['iso_weight']/r['job']['inclusion_probability']*h['pair_mass']
                mass[i]=w;ev[i]=w*h['ev_bb'];br[i]=w*h['br_ev_bb']
                residual[i]=w*(h['ev_bb']-case['pot']*h['equity'])
                gains.append(h['br_ev_bb']-h['ev_bb'])
            den=draws@mass;assert (den>0).all()
            estimates=draws@ev/den;controls=draws@residual/den+case['pot']*eq[class_id]
            base=case['balanced']['hands'][0][class_id]['value_bb']
            results.append(dict(menu=menu,hand=hand,balanced_bb=base,postflop_bb=float(ev.sum()/mass.sum()),
                ci95_bb=np.quantile(estimates,[.025,.975]).tolist(),equity_control_bb=float(residual.sum()/mass.sum()+case['pot']*eq[class_id]),
                equity_control_ci95_bb=np.quantile(controls,[.025,.975]).tolist(),max_board_br_gain_bb=max(gains),
                mean_br_gain_bb=float((br-ev).sum()/mass.sum()),probe_quality_pass=max(gains)<=m['probe_br_gain_limit_bb']))
    write(OUT/('precision-summary.json' if use_precision else 'summary.json'),dict(completed=len(rows),precision_references=len(pm['jobs']) if pm else 0,results=results,
        note='Gross continuation values, conditional on fixed perturbed ranges and restricted menus. Primary direct estimator; equity-control mean uses Monte Carlo cache. Intervals exclude model/range uncertainty.'))


if __name__=='__main__':
    try:
        {'prepare':prepare,'run':run,'summarize':summarize}[sys.argv[1]]()
    except Exception as error:
        if sys.argv[1]=='run':
            write(OUT/'status.json',dict(stage='failed',error=str(error)))
        raise
