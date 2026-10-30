"""Independent CPU inference and gate reconstruction after the frozen final test."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
from concurrent.futures import ThreadPoolExecutor
import hashlib,json
from pathlib import Path
import threading,time,traceback,uuid
import numpy as np
import psutil
from board_prefix_publication_v1 import atomic_json
from stack_price_learning_data_v2 import public_factors
from bounded_parallel_evaluation_archive_v2 import production_available
from weighted_learning_cuda_control_20260927 import LOCK,OTHER

OUT=Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
STORE=Path('S:/GTOpen-research/stack-board-relative-learning-v1')
GEOMETRY=Path('S:/GTOpen-research/stack-geometry-control-v1')
DEST=OUT/'stack-board-relative-learning-v1-readback-v1.json'
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
_mutex=threading.Lock();_last=0.;_start=time.monotonic()

def dense_scores(weights,x,actor,width):
    """Independent NumPy implementation, including the split first layer."""
    assert width in (362,387) and x.ndim==2 and x.shape[1]==width and actor in (0,1)
    prefix=f'p{actor}.'
    assert weights[prefix+'0.weight'].shape==(64,width)
    values=x[:,:362]@weights[prefix+'0.weight'][:,:362].T+weights[prefix+'0.bias']
    if width==387:values+=x[:,362:]@weights[prefix+'0.weight'][:,362:].T
    values=np.maximum(values,0)
    for layer in (2,4):
        values=values@weights[prefix+f'{layer}.weight'].T+weights[prefix+f'{layer}.bias']
        if layer!=4:values=np.maximum(values,0)
    assert np.isfinite(values).all()
    return values

def call_probability(raw):
    logits=raw[:,:2].astype(float)
    assert np.isfinite(logits).all()
    positive=np.maximum(logits,0);den=positive.sum(1)
    call=np.divide(positive[:,1],den,out=np.zeros(len(raw)),where=den>0)
    absent=den<=0;call[absent]=(logits[absent,1]>logits[absent,0]).astype(float)
    return call
def guard():
    global _last
    with _mutex:
        now=time.monotonic();assert now-_start<1800
        if now-_last<2:return
        assert production_available() and not OTHER.exists()
        assert psutil.virtual_memory().available>24_000_000_000
        assert psutil.cpu_percent(interval=None)<75,'Heavy CPU work takes priority'
        _last=now

def run():
    guard();assert not DEST.exists()
    rp=OUT/'stack-board-relative-learning-v1-registration.json'
    pp=OUT/'stack-board-relative-learning-v1-prepared.json'
    resultpath=OUT/'stack-board-relative-learning-v1-result.json'
    reg=read(rp);prepared=read(pp);r=read(resultpath)
    assert r['passed'] and r['complete'] and r['registration_sha256']==sha(rp) and r['preparation_sha256']==sha(pp)
    assert prepared['complete'] and prepared['registration_sha256']==sha(rp) and not prepared['test_labels_prepared']
    checked={}
    def check(p,h):
        assert sha(p)==h,p
        checked[str(p)]=h
    for p in (rp,pp,resultpath):check(p,sha(p))
    for mapping in (reg['inputs'],prepared['artifacts'],r['artifacts']):
        for p,h in mapping.items():check(p,h)
    chosen=read(r['selection']['file']);check(r['selection']['file'],r['selection']['sha256'])
    assert chosen['registration_sha256']==sha(rp) and chosen['preparation_sha256']==sha(pp)
    assert not chosen['test_labels_prepared'] and not chosen['heldout_labels_prepared']
    assert chosen['paired_initial_outputs_exact'] and chosen['paired_batch_generators_exact']
    paired=read(STORE/'gpu-pair-control.json')
    assert paired['passed'] and {c['seed'] for c in paired['records']}==set(reg['seeds'])
    assert len(paired['records'])==2
    for c in paired['records']:
        assert c['rows']==3072 and c['common_inputs_actors_targets_exact'] and c['initial_scores_exact']
    assert len(r['fits'])==len(chosen['candidates'])==4
    assert {(f['seed'],f['width']) for f in r['fits']}=={(s,w) for s in reg['seeds'] for w in (362,387)}
    for f in r['fits']:
        assert f['steps']==8192 and [c['step'] for c in f['checkpoints']]==reg['validation_steps']
        best=min(f['checkpoints'],key=lambda c:(c['validation']['context_balanced_mean_regret_stack_fraction'],c['step']))
        assert f['selected']==best
        assert next(c for c in chosen['candidates'] if (c['seed'],c['width'])==(f['seed'],f['width']))['selected']==best
    for seed in reg['seeds']:
        pair=[next(f for f in r['fits'] if f['seed']==seed and f['width']==w) for w in (362,387)]
        assert pair[0]['first_batch_common_columns_sha256']==pair[1]['first_batch_common_columns_sha256']
        assert [c['batch_rng_sha256'] for c in pair[0]['checkpoints']]==[c['batch_rng_sha256'] for c in pair[1]['checkpoints']]
        assert pair[0]['checkpoints'][0]['validation']==pair[1]['checkpoints'][0]['validation']
        with np.load(pair[0]['checkpoints'][0]['weights']['file'],allow_pickle=False) as a,np.load(pair[1]['checkpoints'][0]['weights']['file'],allow_pickle=False) as b:
            assert a.files==b.files
            for name in a.files:
                if name.endswith('0.weight'):
                    assert np.array_equal(a[name],b[name][:,:362]) and not np.any(b[name][:,362:])
                else:assert np.array_equal(a[name],b[name])
    expected={(b['split'],b['index']):b for b in reg['reused_training_boards']+reg['boards']}
    assert len(expected)==len(r['board_records'])==608
    assert len({(b['split'],b['index']) for b in r['board_records']})==608
    for b in r['board_records']:
        e=expected[(b['split'],b['index'])]
        assert b['board']==e['board'] and b['canonical_group']==e['canonical_group']
    new=[b for b in r['board_records'] if b['split']!='fit']
    groups={tuple(b['canonical_group']) for b in new}
    assert len(groups)==96 and not groups&set(map(tuple,reg['excluded_probe_groups']))
    assert len({tuple(b['canonical_group']) for b in r['board_records']})==608
    cards=[];counts=[]
    for b in r['board_records']:
        if b['split']=='test':
            with np.load(b['file'],allow_pickle=False) as z:base=z['features'].copy();counts.append(z['counts'].copy())
            with np.load(b['extra_file'],allow_pickle=False) as z:extra=z['features'].copy()
            assert base.shape==(1081,362) and extra.shape==(1081,25)
            cards.append(np.concatenate((base,extra),axis=1))
    assert len(cards)==64;cards=np.concatenate(cards);counts=np.concatenate(counts)
    assert np.all(counts.sum(1)==990);equity=(counts[:,0]+.5*counts[:,1])/990
    contexts=[public_factors(read(GEOMETRY/f'stack-{d}-public.json')) for d in (*reg['fitting_depths'],*reg['heldout_depths'])]
    def one(candidate):
        width=candidate['width']
        with np.load(candidate['selected']['weights']['file'],allow_pickle=False) as z:weights={k:z[k].copy() for k in z.files}
        expected=next(t for t in r['tests'] if (t['seed'],t['width'])==(candidate['seed'],width))
        assert len(contexts)==len(expected['score']['contexts'])
        results=[]
        for context,original in zip(contexts,expected['score']['contexts']):
            assert context['stack']==original['stack']
            total=0.;count=0
            for state,public in zip(context['economics'],context['features']):
                guard();stack,net,cost,actor,_=state;actor=int(actor)
                x=cards[:,:362]+public
                if width==387:x=np.concatenate((x,cards[:,362:]),axis=1)
                call=call_probability(dense_scores(weights,x,actor,width))
                delta=equity*net-cost;loss=np.where(delta>0,(1-call)*delta,call*(-delta))
                total+=float(loss.sum());count+=len(loss)
            mean=total/count;error=abs(mean-original['mean_regret_bb'])
            assert count==original['rows'] and error<1e-4,(candidate['seed'],width,context['stack'],error)
            for partition in ('seats','price_bands','hand_groups'):assert sum(v['rows'] for v in original[partition])==count
            results.append(dict(stack=context['stack'],rows=count,mean_regret_bb=mean,
                mean_regret_stack_fraction=mean/context['stack'],cpu_cuda_mean_error_bb=error))
        return dict(seed=candidate['seed'],width=width,contexts=results)
    with ThreadPoolExecutor(max_workers=4) as pool:replayed=list(pool.map(one,chosen['candidates']))
    gates=[]
    for seed in reg['seeds']:
        values=[[c for c in next(t for t in replayed if t['seed']==seed and t['width']==w)['contexts'] if c['stack'] in reg['heldout_depths']] for w in (362,387)]
        old,new=(float(np.mean([c['mean_regret_stack_fraction'] for c in v])) for v in values)
        selected=next(c for c in chosen['candidates'] if c['seed']==seed and c['width']==387)
        passed=selected['selected']['step']>0 and old>0 and new<=.8*old and all(c['mean_regret_stack_fraction']<=.001 for c in values[1])
        assert bool(passed)==next(g for g in r['diagnostic_gates'] if g['seed']==seed)['passed']
        gates.append(dict(seed=seed,passed=bool(passed),baseline=old,candidate=new))
    result=dict(passed=True,source_sha256=sha(__file__),inputs=checked,verified_files=len(checked),
        cpu_replayed=replayed,diagnostic_gates=gates,rows_replayed=sum(c['rows'] for v in replayed for c in v['contexts']),
        maximum_cpu_cuda_mean_regret_error_bb=max(c['cpu_cuda_mean_error_bb'] for v in replayed for c in v['contexts']),
        seconds=time.monotonic()-_start,
        gpu_used=False,new_training=False,new_test_data=False,full_preflop_accuracy_qualified=False,production_modified=False)
    atomic_json(DEST,result);print(json.dumps({k:v for k,v in result.items() if k not in ('inputs','cpu_replayed')}),flush=True)

def main():
    assert not LOCK.exists() and not OTHER.exists()
    assert production_available() and psutil.cpu_percent(interval=1)<50
    assert psutil.virtual_memory().available>28_000_000_000
    with LOCK.open('x') as stream:stream.write(str(os.getpid()))
    try:run()
    except BaseException as e:
        atomic_json(OUT/('stack-board-relative-readback-interruption-'+uuid.uuid4().hex[:8]+'.json'),dict(error=repr(e),traceback=traceback.format_exc()))
        raise
    finally:
        assert LOCK.read_text()==str(os.getpid());LOCK.unlink()

if __name__=='__main__':main()
