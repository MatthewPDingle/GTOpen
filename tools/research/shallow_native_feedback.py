"""Frozen-policy feedback references for the opt-in shallow native study."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import time
import numpy as np
import shallow_native_study as native
import evaluate_holdem_raise_audit as action

OUT,ROOT=native.OUT,native.ROOT
read,write,now=native.read,native.write,native.now
pilot=native.previous.pilot


def stability():
    native.checked();result={}
    for arm in ['baseline','shallow']:
        snapshots=[read(OUT/arm/str(n)/f'iteration-{n}.json') for n in [500,1500,3000]]
        rows=[]
        for path in [[],[2]]:
            a,b=[next(r['view'] for r in s['views'] if r['path']==path) for s in snapshots[1:]]
            freq=[np.array([x['freq'] for x in v['actions']]) for v in [a,b]]
            delta=float(abs(freq[1]-freq[0]).max())
            sa,sb=[np.array(v['strategy']).reshape(-1,169) for v in [a,b]]
            variation=float(np.mean(abs(sa-sb).sum(axis=0)/2))
            rows.append(dict(path=path,actions=[x['label'] for x in b['actions']],frequencies_1500=freq[0].tolist(),
                frequencies_3000=freq[1].tolist(),max_aggregate_movement_pp=100*delta,
                mean_hand_total_variation=variation,passed=delta<=.005 and variation<=.01))
        result[arm]=dict(rows=rows,passed=all(r['passed'] for r in rows),
            checkpoints=[{k:s[k] for k in ['iteration','gaps','evs','learning_seconds','setup_seconds']} for s in snapshots])
    write(OUT/'stability.json',result);print(json.dumps(result,indent=2),flush=True)


def benchmark():
    native.checked();rows=[]
    for repeat in range(3):
        for arm in (['baseline','shallow'] if repeat%2==0 else ['shallow','baseline']):
            folder=OUT/'timing'/f'{repeat}-{arm}';folder.mkdir(parents=True,exist_ok=True)
            kernel=native.BASE_KERNEL if arm=='baseline' else OUT/'interface.cu'
            native.command([native.BIN,'solve',native.previous.prior.SAVE,folder,'candidate',1000,kernel],
                           folder/'solve.log',{'GTOPEN_INTERFACE_WARMUP':'100'})
            s=read(folder/'iteration-1100.json')
            rows.append(dict(repeat=repeat,arm=arm,learning_seconds=s['learning_seconds'],setup_seconds=s['setup_seconds']))
    medians={arm:float(np.median([r['learning_seconds'] for r in rows if r['arm']==arm])) for arm in ['baseline','shallow']}
    write(OUT/'timing.json',dict(rows=rows,medians=medians,shallow_over_baseline=medians['shallow']/medians['baseline'],
          scope='40-node fixture only; not a large-tree speed claim',production_enabled=False))
    print('Timing',medians,flush=True)


def prepare():
    implementation=native.checked()
    assert not (OUT/'manifest.json').exists(),'Preserve registered feedback labels'
    assert read(OUT/'shallow/audit/parity.json')['passed']
    tree=read(OUT/'shallow/tree.json');boards=native.previous.panel('shallow-native-feedback-v1',10)
    template=read(native.previous.OUT/'manifest.json')['jobs'][0]['config']['tree']
    cases=[];jobs=[]
    for path,ident in zip(native.previous.old.PATHS,native.previous.old.CASE_IDS):
        node=next(n for n in tree['nodes'] if n['path']==path)
        p=(pilot.COMBOS/1326).astype(np.float32)
        weights=np.minimum(np.array(node['reaches'],dtype=np.float32)/p,1.)[[1,0]].astype(float)
        texts=[','.join(f'{pilot.LABELS[k]}:{v:.9g}' for k,v in enumerate(row) if v>0) for row in weights]
        case=dict(id=ident,node=node['id'],path=path,pot=node['pot'],stack=min(tree['config']['stack']-v for v in node['invested']),
                  weights=[pilot.weights(t) for t in texts],range_oop=texts[0],range_ip=texts[1],positions=['BB','SB'])
        cases.append(case)
        cfg=dict(template,starting_pot=case['pot'],effective_stack=case['stack'])
        for b in boards:
            jobs.append(dict(**b,id=ident+'-'+b['board'],case=ident,
                config=dict(board=b['board'],range_oop=texts[0],range_ip=texts[1],tree=cfg)))
    sources=[Path(__file__),OUT/'shallow/tree.json',OUT/'shallow/3000/policy.gtop',OUT/'implementation-freeze.json',
             ROOT/'tools/research/evaluate_shallow_native_feedback.py',native.previous.prior.REFERENCE]
    m=dict(registered_at=now(),implementation_id=implementation['id'],cases=cases,jobs=jobs,boards=boards,
           inputs={p.relative_to(ROOT).as_posix():pilot.sha(p) for p in sources},target_gap_pct=.1,max_iterations=2000,
           bootstrap_seed=2026091704,bootstrap_replicates=5000,production_enabled=False)
    m['id']=hashlib.sha256(json.dumps(m,sort_keys=True).encode()).hexdigest()
    write(OUT/'reference-preflight.json',dict(live=native.previous.prior.idle(),references=len(jobs),registered_at=now()))
    write(OUT/'manifest.json',m);print('Registered',len(jobs),'fresh-range references',flush=True)


def checked():
    native.checked();m=read(OUT/'manifest.json')
    assert hashlib.sha256(json.dumps({k:v for k,v in m.items() if k!='id'},sort_keys=True).encode()).hexdigest()==m['id']
    for p,h in m['inputs'].items():assert pilot.sha(ROOT/p)==h,p
    return m


def run():
    m=checked();start=time.perf_counter()
    for i,j in enumerate(m['jobs']):
        path=OUT/'jobs'/(j['id']+'.json')
        if not path.exists():
            write(OUT/'status.json',dict(stage='references',completed=i,total=len(m['jobs']),active=j['id'],updated=now()))
            native.command([native.previous.prior.REFERENCE,OUT/'manifest.json',1],OUT/(j['id']+'.log'))
        native.previous.old.validate(read(path),j,m)
        print('reference',i+1,'/',len(m['jobs']),j['id'],'elapsed',round(time.perf_counter()-start),flush=True)
    checked();write(OUT/'status.json',dict(stage='references_complete',completed=len(m['jobs']),total=len(m['jobs']),updated=now()))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['stability','benchmark','prepare','run'])
    globals()[p.parse_args().command]()
