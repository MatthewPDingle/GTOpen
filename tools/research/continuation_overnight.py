"""Checkpointed overnight continuation research. Never mutates the live app.

inventory -> prepare -> run. Training/test source families and boards are frozen
before reference outcomes; every completed reference is independently resumable.
"""
from pathlib import Path
import collections
import ctypes
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request

import numpy as np
import range_value_pilot as pilot

ROOT = pilot.ROOT
OUT = ROOT/'research/preflop-evolution/continuation/range-value-overnight-20260915'
SOURCES = [
    ('train-six-modeled','train','Before position models 20260908.gtop'),
    ('train-seven-open','train','7-max 200bb 25 35330541limpall-in.gtop'),
    ('train-eight-equal','train','2-2 equal blinds corrected 20260907-2118.gtop'),
    ('train-eight-straddle','train','balanced-sb05-continuation-20260915.gtop'),
    ('test-seven-straddle','test','7-max 200bb Adelaide 25 str 68o 3r 3mr 0a 5r 41rc l ai.gtop'),
    ('test-eight-open','test','8-max 200bb 25 Adelaide.gtop'),
]
PROBES = ['AA','KK','QQ','JJ','TT','99','88','55','A5s','AJo','KQo','QJs','JTs','T9s','76s','54s']


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def dump(path,value):
    path = Path(path);temp = path.with_suffix(path.suffix+'.partial')
    temp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    os.replace(temp,path)


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):
            digest.update(block)
    return digest.hexdigest()


def checked_manifest():
    m = json.loads((OUT/'manifest.json').read_text())
    assert hashlib.sha256(json.dumps({k:v for k,v in m.items() if k != 'id'},sort_keys=True).encode()).hexdigest() == m['id']
    assert file_hash(OUT/'fixtures.json') == m['fixtures_sha256']
    assert file_hash(ROOT/'cache/preflop_eq169.bin') == m['equity_sha256']
    assert file_hash(ROOT/'cache/realization_fit.json') == m['fit_sha256']
    return m


def inventory():
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'inventory').mkdir(exist_ok=True)
    exe = ROOT/'target/release/examples/continuation_range_inventory.exe'
    for family,partition,name in SOURCES:
        save = ROOT/'saves/preflop'/name;digest = file_hash(save)
        output = OUT/'inventory'/f'{family}.json'
        if output.exists():
            r = json.loads(output.read_text())
            assert r['source_sha256'] == digest
            continue
        with (OUT/'inventory'/f'{family}.log').open('w') as log:
            subprocess.run([str(exe),str(save),str(output)],cwd=ROOT,stdout=log,stderr=log,check=True)
        r = json.loads(output.read_text());assert file_hash(save) == digest
        r.update(source_sha256=digest,family=family,partition=partition,extractor_sha256=file_hash(exe))
        dump(output,r)
        print(f"Inventoried {family}: {len(r['candidates'])} branches",flush=True)


def clean_weights(original):
    w = np.array(original,dtype=float)
    assert w.shape == (2,169) and np.isfinite(w).all() and (w>=0).all()
    w /= w.max(axis=1,keepdims=True)
    removed=[];added=[]
    for p in range(2):
        total = float(w[p]@pilot.COMBOS);dropped=0.
        for h in np.argsort(w[p]):
            if w[p,h] >= .005 or dropped+w[p,h]*pilot.COMBOS[h] > total*.001:
                break
            dropped += w[p,h]*pilot.COMBOS[h];w[p,h]=0
        extra = 0.
        for hand in PROBES:
            h = pilot.INDEX[hand]
            if w[p,h] < .0001:
                extra += (.0001-w[p,h])*pilot.COMBOS[h];w[p,h]=.0001
        removed.append(dropped/total);added.append(extra/total)
    # The serialized range parser receives these same rounded weights.
    w = np.round(w,9)
    return w,removed,added


def signature(c):
    w = np.array(c['weights'])*pilot.COMBOS
    w /= w.sum(axis=1,keepdims=True)
    return np.r_[w.ravel(),np.log1p(c['stack']/c['pot'])/5,c['raises']/4]


def choose(candidates,n):
    # Outcome-independent coverage: depth first, then farthest range/SPR shape.
    usable = [c for c in candidates if c['branch_probability']>=1e-7]
    assert len(usable)>=n
    selected=[]
    for depth in [1,2,3,0]:
        rows = [c for c in usable if min(c['raises'],3)==depth]
        if rows:
            selected.append(max(rows,key=lambda c:c['branch_probability']))
    selected=selected[:n]
    while len(selected)<n:
        rest=[c for c in usable if c not in selected]
        selected.append(max(rest,key=lambda c:min(np.linalg.norm(signature(c)-signature(s)) for s in selected)))
    return selected


def prepare():
    cases=[]
    rng=np.random.default_rng(20260915)
    for family,partition,_ in SOURCES:
        inv=json.loads((OUT/'inventory'/f'{family}.json').read_text())
        rows=choose(inv['candidates'],5 if partition=='train' else 4)
        if partition=='train':
            # Keep a controlled perturbation beside its parent source family.
            variant=json.loads(json.dumps(rows[0]))
            w=np.array(variant['weights']);w*=np.exp(rng.normal(0,.6,w.shape))
            variant.update(weights=w.tolist(),perturbation='Nonzero weights multiplied by exp(N(0,0.6)); seed 20260915.')
            rows.append(variant)
        for i,r in enumerate(rows):
            w,removed,added=clean_weights(r['weights'])
            range_text=lambda p:','.join(f'{pilot.LABELS[h]}:{v:.9f}' for h,v in enumerate(w[p]) if v>0)
            cases.append(dict(id=f'{family}-{i:02}',family=family,partition=partition,
                # Normalize monetary scale only; retain the original SPR.
                pot=20.,stack=20*r['stack']/r['pot'],original_pot=r['pot'],original_stack=r['stack'],
                weights=w.tolist(),range_oop=range_text(0),range_ip=range_text(1),
                source_path=r['path'],source_sha256=inv['source_sha256'],source_config=inv['config'],
                source_iteration=inv['iteration'],source_branch_probability=r['branch_probability'],
                raises=r['raises'],oop_position=r['oop_position'],ip_position=r['ip_position'],
                removed_mass_fraction=removed,probe_added_mass_fraction=added,perturbation=r.get('perturbation')))
    assert len(cases)==32 and sum(c['partition']=='train' for c in cases)==24
    fixtures=dict(cases=cases,probes=PROBES,sources=[dict(family=f,partition=p,file=n) for f,p,n in SOURCES])
    fp=OUT/'fixtures.json'
    if fp.exists(): assert json.loads(fp.read_text())==fixtures
    else: dump(fp,fixtures)
    old_boards={b['board'] for b in json.loads((pilot.OUT/'manifest.json').read_text())['boards']}
    for directory in [pilot.AUDIT,pilot.AUDIT/'extension']:
        old_boards.update(b['board'] for b in json.loads((directory/'manifest.json').read_text())['boards'])
    groups=collections.defaultdict(list)
    for board,iso in json.loads((pilot.AUDIT/'fixtures.json').read_text())['canonical_flops']:
        if board in old_boards: continue
        cards=[board[i:i+2] for i in range(0,6,2)]
        key=('paired' if len({c[0] for c in cards})<3 else 'unpaired')+'/'+str(len({c[1] for c in cards}))+'suits'
        groups[key].append((board,iso))
    boards=[]
    for key,rows in sorted(groups.items()):
        rows.sort(key=lambda x:hashlib.sha256(('overnight-range-v2'+x[0]).encode()).digest())
        for partition,items in [('train',rows[:20]),('test',rows[20:40])]:
            for board,iso in items:
                boards.append(dict(board=board,iso_weight=iso,stratum=key,partition=partition,inclusion_probability=20/len(rows)))
    assert len(boards)==200 and len({b['board'] for b in boards})==200
    jobs=[]
    for b in boards:
        for c in cases:
            if c['partition']!=b['partition']: continue
            size={'bet':[{'PotPct':50}],'raise':[{'PotPct':100}],'donk':[{'PotPct':50}]}
            cfg=dict(board=b['board'],range_oop=c['range_oop'],range_ip=c['range_ip'],tree=dict(
                starting_pot=c['pot'],effective_stack=c['stack'],rake_pct=0,rake_cap=0,
                oop=[size]*3,ip=[size]*3,max_raises=1,add_allin=False,allin_threshold=.85))
            jobs.append(dict(**b,case=c['id'],family=c['family'],menu='half',id=c['id']+'-'+b['board'],config=cfg))
    assert len(jobs)==3200
    # Interleave source cases/boards to make progress balanced across the batch.
    binary=ROOT/'target/range-value-reference-night1.exe'
    if not binary.exists(): shutil.copy2(ROOT/'target/release/examples/range_value_reference.exe',binary)
    m=dict(schema=2,jobs=jobs,boards=boards,fixtures_sha256=file_hash(fp),binary_sha256=file_hash(binary),
        equity_sha256=file_hash(ROOT/'cache/preflop_eq169.bin'),fit_sha256=file_hash(ROOT/'cache/realization_fit.json'),
        target_gap_pct=.1,max_iterations=2000,
        protocol=dict(training='24 configurations from four source families, including four controlled perturbations; 100 distinct training flops.',
            independent_test='Eight configurations from two other source games; 100 entirely separate test flops. All siblings stay together. Previous pilot/audit boards excluded.',
            caveats='Source ranges are generated by approximate legacy/model-based preflop games, not treated as payoff truth. Postflop labels recomputed with zero rake. Fixed 50% menu, HU only; no deployment.',
            candidates=['shape','pca8'],ridge=[.01,.1,1.,10.],
            selection='Leave-one-training-source-family-out MAE. PCA fit on training families only within each fold; never use test labels for fitting or selection.',
            gate='At least 15% lower mean range-weighted hand MAE than both Balanced and raw equity on each held-out source family; report paired board-bootstrap uncertainty and rare-hand BR checks.',
            outcome='Complete report even if no candidate passes. No GPU integration or automatic deployment. Fresh preflop decision and GPU overhead validation remains a later gate.'))
    m['id']=hashlib.sha256(json.dumps(m,sort_keys=True).encode()).hexdigest()
    if (OUT/'manifest.json').exists(): assert json.loads((OUT/'manifest.json').read_text())==m
    else: dump(OUT/'manifest.json',m)
    print('Frozen',len(jobs),'jobs, manifest',m['id'])


def process_alive(pid):
    if not pid:return False
    kernel=ctypes.windll.kernel32
    kernel.OpenProcess.restype=ctypes.c_void_p
    handle=kernel.OpenProcess(0x1000,False,int(pid))
    if not handle:return False
    code=ctypes.c_ulong()
    try:
        return bool(kernel.GetExitCodeProcess(ctypes.c_void_p(handle),ctypes.byref(code))) and code.value==259
    finally:kernel.CloseHandle(ctypes.c_void_p(handle))


def live_busy():
    states=[]
    for endpoint in ['/api/preflop/status','/api/status']:
        try:
            with urllib.request.urlopen('http://localhost:56708'+endpoint,timeout=3) as r:
                states.append(json.load(r).get('state'))
        except (OSError,ValueError):
            # Server being unavailable does not authorize restarting it.
            pass
    return any(s in ['running','solving','building'] for s in states)


def run():
    import msvcrt
    m=checked_manifest();binary=ROOT/'target/range-value-reference-night1.exe'
    assert file_hash(binary)==m['binary_sha256']
    lock=(OUT/'.run.lock').open('a+b');lock.seek(0)
    if lock.read(1)==b'':lock.write(b'0');lock.flush()
    lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    old=json.loads((OUT/'status.json').read_text()) if (OUT/'status.json').exists() else {}
    if process_alive(old.get('active_child_pid')):
        raise RuntimeError('A prior reference child is still alive; inspect it before resuming.')
    started=now();deadline=time.monotonic()+10*3600;child=None;completed={}
    def refresh():
        for path in (OUT/'jobs').glob('*.json'):
            if path.stem in completed:continue
            r=json.loads(path.read_text())
            assert r['manifest_id']==m['id'] and r['job']['id']==path.stem
            if not r['target_met']:raise RuntimeError('Accuracy target not met: '+path.stem)
            completed[path.stem]=r['seconds']
    def status(phase,**extra):
        dump(OUT/'status.json',dict(phase=phase,pid=os.getpid(),active_child_pid=child.pid if child and child.poll() is None else None,
            started_utc=started,updated_utc=now(),completed=len(completed),total=len(m['jobs']),
            summed_reference_seconds=sum(completed.values()),manifest_id=m['id'],**extra))
    env=dict(os.environ);env['PATH']=str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env.get('PATH','')
    try:
        refresh();status('references')
        while len(completed)<len(m['jobs']):
            if time.monotonic()>deadline:
                status('paused_time_budget',note='Checkpointed; incomplete, resume required.');return
            if live_busy():
                status('waiting_for_live_solve');time.sleep(20);continue
            with (OUT/'references.log').open('a',encoding='utf-8') as log:
                child=subprocess.Popen([str(binary),str(OUT/'manifest.json'),'4'],cwd=ROOT,env=env,stdout=log,stderr=log)
                while child.poll() is None:
                    refresh();status('references');time.sleep(3)
                if child.returncode:raise RuntimeError(f'Reference process exited {child.returncode}; see references.log')
                child=None
            refresh();status('references')
        status('training')
        import continuation_overnight_fit as trainer
        trainer.train()
        status('independent_evaluation')
        trainer.evaluate()
        status('complete',report='RESULTS.md',production_changed=False)
    except BaseException as error:
        status('attention_required',error=str(error))
        raise
    finally:
        lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1);lock.close()


if __name__=='__main__':
    {'inventory':inventory,'prepare':prepare,'run':run}[sys.argv[1]]()
