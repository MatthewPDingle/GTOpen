"""Independent CPU dense-network replay of the frozen diagnostic's primary means."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import threading
import time
import numpy as np
import psutil
from board_prefix_publication_v1 import atomic_json
from stack_price_learning_data_v2 import public_factors
from bounded_parallel_evaluation_archive_v2 import production_available
from weighted_learning_cuda_control_20260927 import LOCK,OTHER

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
STORE=Path('S:/GTOpen-research/stack-board-training-budget-v1')
GEOMETRY=Path('S:/GTOpen-research/stack-geometry-control-v1')
RESULT=OUT/'stack-board-training-budget-v1-readback-v1.json'
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
_probe_lock=threading.Lock()
_last_probe=0.
_began=time.monotonic()
def guard():
    global _last_probe
    with _probe_lock:
        now=time.monotonic()
        assert now-_began<1800, 'Bounded CPU readback time limit'
        if now-_last_probe<2:return
        assert production_available() and not OTHER.exists(), 'Other work takes priority'
        assert psutil.virtual_memory().available>24_000_000_000
        _last_probe=now

def run():
    guard()
    assert not RESULT.exists()
    rp=OUT/'stack-board-training-budget-v1-registration.json';path=OUT/'stack-board-training-budget-v1-result.json'
    r=read(path);reg=read(rp)
    assert r['passed'] and r['complete'] and r['registration_sha256']==sha(rp)
    checked={}
    def check(p,h):
        assert sha(p)==h,p
        checked[str(p)]=h
    check(rp,sha(rp));check(path,sha(path))
    for p,h in reg['inputs'].items():check(p,h)
    for p,h in r['artifacts'].items():check(p,h)
    chosen=read(r['selection']['file']);check(r['selection']['file'],r['selection']['sha256'])
    assert chosen['test_labels_prepared'] is False and chosen['heldout_labels_prepared'] is False
    assert len(r['fits'])==4 and len(r['chains'])==2
    assert {(f['seed'],f['arm']) for f in r['fits']}=={(seed,arm) for seed in reg['seeds'] for arm in ('short','long')}
    assert chosen['paired_shared_prefix'] and reg['paired_shared_prefix']
    assert len(reg['reused_training_boards'])==512 and all(b['split']=='fit' for b in reg['reused_training_boards'])
    assert [b['index'] for b in reg['reused_training_boards']]==list(range(512))
    for fit in r['fits']:
        limit=reg['arms'][fit['arm']]
        assert fit['steps']==limit
        assert [c['step'] for c in fit['checkpoints']]==[s for s in reg['validation_steps'] if s<=limit]
        chain=next(c for c in r['chains'] if c['seed']==fit['seed'])
        assert chain['steps']==32768
        assert fit['checkpoints']==[c for c in chain['checkpoints'] if c['step']<=limit]
        best=min(fit['checkpoints'],key=lambda c:(c['validation']['context_balanced_mean_regret_stack_fraction'],c['step']))
        assert fit['selected']==best
        candidate=next(c for c in chosen['candidates'] if (c['seed'],c['arm'])==(fit['seed'],fit['arm']))
        assert candidate['selected']==best
    assert chosen['paired_initial_weights_identical']
    for seed in reg['seeds']:
        pair=[next(f for f in r['fits'] if f['seed']==seed and f['arm']==arm) for arm in ('short','long')]
        with np.load(pair[0]['checkpoints'][0]['weights']['file'],allow_pickle=False) as a,np.load(pair[1]['checkpoints'][0]['weights']['file'],allow_pickle=False) as b:
            assert a.files==b.files and all(np.array_equal(a[k],b[k]) for k in a.files)
    expected_boards={b['index']:b for b in reg['boards']}
    assert len(r['board_records'])==len(expected_boards)
    assert len({b['index'] for b in r['board_records']})==len(expected_boards)
    for b in r['board_records']:
        expected=expected_boards[b['index']]
        assert all(b[k]==expected[k] for k in ('board','split','canonical_group'))
    groups=[tuple(b['canonical_group']) for b in r['board_records']]
    assert len(groups)==96 and len(set(groups))==96 and not set(groups)&set(map(tuple,reg['excluded_probe_groups']))
    cards=[];counts=[]
    for b in r['board_records']:
        if b['split']=='test':
            with np.load(b['file'],allow_pickle=False) as d:cards.append(d['features']);counts.append(d['counts'])
    assert len(cards)==64;cards=np.concatenate(cards);counts=np.concatenate(counts)
    equity=(counts[:,0]+.5*counts[:,1])/990
    contexts=[public_factors(read(GEOMETRY/f'stack-{d}-public.json')) for d in (*reg['fitting_depths'],*reg['heldout_depths'])]
    def one(candidate):
        width=candidate['width'];model=candidate['selected']['weights']
        with np.load(model['file'],allow_pickle=False) as d:weights={k:d[k].copy() for k in d.files}
        expected=next(t for t in r['tests'] if (t['seed'],t['arm'])==(candidate['seed'],candidate['arm']))
        results=[]
        for context,original in zip(contexts,expected['score']['contexts']):
            total=0.;count=0
            for state,vector in zip(context['economics'],context['features']):
                guard()
                stack,net,cost,actor,_=state;actor=int(actor)
                x=cards[:,:width]+vector[:width]
                for layer in (0,2,4):
                    x=x@weights[f'p{actor}.{layer}.weight'].T+weights[f'p{actor}.{layer}.bias']
                    if layer!=4:x=np.maximum(x,0)
                scores=x[:,:2].astype(np.float64);positive=np.maximum(scores,0);den=positive.sum(1)
                call=np.divide(positive[:,1],den,out=np.zeros(len(x)),where=den>0)
                absent=den<=0;call[absent]=(scores[absent,1]>scores[absent,0]).astype(float)
                delta=equity*net-cost
                # Independent cash loss relative to the better legal action.
                loss=np.where(delta>0,(1-call)*delta,call*(-delta))
                total+=float(loss.sum());count+=len(loss)
            mean=total/count;assert count==original['rows']
            error=abs(mean-original['mean_regret_bb'])
            assert error<1e-4, (candidate['seed'],width,context['stack'],error)
            assert sum(s['rows'] for s in original['seats'])==count
            assert sum(s['rows'] for s in original['price_bands'])==count
            assert sum(s['rows'] for s in original['hand_groups'])==count
            results.append(dict(stack=context['stack'],rows=count,mean_regret_bb=mean,
                                mean_regret_stack_fraction=mean/context['stack'],cpu_cuda_mean_error_bb=error))
        return dict(seed=candidate['seed'],width=width,arm=candidate['arm'],contexts=results)
    with ThreadPoolExecutor(max_workers=4) as pool:replayed=list(pool.map(one,chosen['candidates']))
    gates=[]
    for seed in reg['seeds']:
        records=[next(x for x in replayed if x['seed']==seed and x['arm']==arm) for arm in ('short','long')]
        values=[[c for c in a['contexts'] if c['stack'] in reg['heldout_depths']] for a in records]
        old,new=(float(np.mean([c['mean_regret_stack_fraction'] for c in group])) for group in values)
        selection=next(c for c in chosen['candidates'] if c['seed']==seed and c['arm']=='long')
        passed=selection['selected']['step']>0 and old>0 and new<=.8*old and all(c['mean_regret_stack_fraction']<=.001 for c in values[1])
        assert bool(passed)==next(g for g in r['diagnostic_gates'] if g['seed']==seed)['passed']
        gates.append(dict(seed=seed,passed=bool(passed),baseline=old,candidate=new))
    maximum=max(c['cpu_cuda_mean_error_bb'] for a in replayed for c in a['contexts'])
    atomic_json(RESULT,dict(passed=True,source_sha256=sha(__file__),inputs=checked,verified_files=len(checked),
        cpu_replayed=replayed,diagnostic_gates=gates,maximum_cpu_cuda_mean_regret_error_bb=maximum,
        rows_replayed=sum(c['rows'] for a in replayed for c in a['contexts']),gpu_used=False,
        new_training=False,new_test_data=False,full_preflop_accuracy_qualified=False,production_modified=False))
    print(json.dumps({k:v for k,v in read(RESULT).items() if k not in ('inputs','cpu_replayed')}),flush=True)

def main():
    assert not LOCK.exists() and not OTHER.exists()
    with LOCK.open('x') as f:f.write(str(os.getpid()))
    try:run()
    finally:
        assert LOCK.read_text()==str(os.getpid());LOCK.unlink()

if __name__=='__main__':main()
