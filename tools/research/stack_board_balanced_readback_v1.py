"""Independent CPU reconstruction of the frozen balanced-board comparison."""
import time
_start=time.monotonic()
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib, json, threading, time, traceback, uuid
from itertools import permutations
import numpy as np
import psutil
from board_prefix_publication_v1 import atomic_json
from stack_price_learning_data_v2 import public_factors
from stack_board_relative_readback_v1 import dense_scores
from stack_board_balanced_metrics_v1 import reference_context, compare_context, TOLERANCE_POLICY as TOLERANCES
from stack_board_balanced_sampler_v1 import board_cell, allocation
from bounded_parallel_evaluation_archive_v2 import production_available
from weighted_learning_cuda_control_20260927 import LOCK, OTHER

OUT=Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
NAME='stack-board-balanced-learning-v1'
STORE=Path('S:/GTOpen-research')/NAME
GEOMETRY=Path('S:/GTOpen-research/stack-geometry-control-v1')
DEST=OUT/(NAME+'-readback-v1.json')
STATUS=OUT/(NAME+'-readback-status.json')
ATTEMPT=OUT/(NAME+'-readback-attempt.json')
_mutex=threading.Lock()
_last=0.
_status_mutex=threading.Lock()

def read(path):return json.loads(Path(path).read_bytes())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def status(state,**values):
    record=dict(state=state,pid=os.getpid(),process_created=psutil.Process().create_time(),unix=time.time(),**values)
    with _status_mutex:atomic_json(STATUS,record,replace=True)
    print(json.dumps(record),flush=True)

def guard():
    global _last
    with _mutex:
        now=time.monotonic()
        assert now-_start<1800, 'Readback execution cap reached'
        if now-_last<2:return
        assert production_available() and not OTHER.exists()
        assert psutil.virtual_memory().available>24_000_000_000
        assert psutil.cpu_percent(interval=None)<75, 'Heavy CPU work takes priority'
        _last=now

def run():
    guard()
    assert not DEST.exists(), 'Do not duplicate readback'
    rp,pp,result_path=(OUT/(NAME+suffix+'.json') for suffix in ('-registration','-prepared','-result'))
    reg,prepared,result=read(rp),read(pp),read(result_path)
    assert result['passed'] and result['complete']
    assert result['registration_sha256']==sha(rp) and result['preparation_sha256']==sha(pp)
    assert prepared['passed'] and prepared['complete'] and prepared['registration_sha256']==sha(rp)
    assert not prepared['test_labels_prepared'] and not prepared['stress_labels_prepared']
    assert reg['readback_tolerances']==TOLERANCES
    checked={}
    def check(path,value):
        guard()
        assert sha(path)==value,path
        checked[str(path)]=value
    def check_ref(ref):
        path,value=ref['file'],ref['sha256']
        assert result['artifacts'].get(path,reg['inputs'].get(path))==value,path
        check(path,value)
    for path in (rp,pp,result_path):check(path,sha(path))
    for mapping in (reg['inputs'],prepared['artifacts'],result['artifacts']):
        for path,value in mapping.items():check(path,value)
    chosen=read(result['selection']['file'])
    check(result['selection']['file'],result['selection']['sha256'])
    assert chosen['registration_sha256']==sha(rp) and chosen['preparation_sha256']==sha(pp)
    assert not chosen['test_labels_prepared'] and not chosen['stress_labels_prepared'] and not chosen['heldout_labels_prepared']
    assert chosen['paired_initial_outputs_exact'] and chosen['paired_batch_generators_exact']
    pairs=read(STORE/'gpu-pair-control.json')
    assert pairs['passed'] and len(pairs['records'])==4
    assert {(p['seed'],p['arm']) for p in pairs['records']}=={(s,a) for s in reg['seeds'] for a in reg['arms']}
    for pair in pairs['records']:
        assert pair['rows']==3072 and pair['common_inputs_actors_targets_exact'] and pair['initial_scores_exact']
    assert len(result['fits'])==len(chosen['candidates'])==8
    assert {(f['seed'],f['arm'],f['width']) for f in result['fits']}=={(s,a,w) for s in reg['seeds'] for a in reg['arms'] for w in reg['widths']}
    for fit in result['fits']:
        assert fit['steps']==8192 and [c['step'] for c in fit['checkpoints']]==reg['validation_steps']
        best=min(fit['checkpoints'],key=lambda c:(c['validation']['context_balanced_mean_regret_stack_fraction'],c['step']))
        assert fit['selected']==best
        assert next(c for c in chosen['candidates'] if (c['seed'],c['arm'],c['width'])==(fit['seed'],fit['arm'],fit['width']))['selected']==best
        for checkpoint in fit['checkpoints']:check_ref(checkpoint['weights'])
    for seed in reg['seeds']:
        initial=[]
        for arm in reg['arms']:
            pair=[next(f for f in result['fits'] if (f['seed'],f['arm'],f['width'])==(seed,arm,width)) for width in reg['widths']]
            assert pair[0]['first_batch_common_columns_sha256']==pair[1]['first_batch_common_columns_sha256']
            assert [c['batch_rng_sha256'] for c in pair[0]['checkpoints']]==[c['batch_rng_sha256'] for c in pair[1]['checkpoints']]
            initial.extend(f['checkpoints'][0]['validation'] for f in pair)
            with np.load(pair[0]['checkpoints'][0]['weights']['file'],allow_pickle=False) as a,np.load(pair[1]['checkpoints'][0]['weights']['file'],allow_pickle=False) as b:
                assert a.files==b.files
                for name in a.files:
                    if name.endswith('0.weight'):
                        assert np.array_equal(a[name],b[name][:,:362]) and not np.any(b[name][:,362:])
                    else:assert np.array_equal(a[name],b[name])
        assert all(c==initial[0] for c in initial)
    expected={(b['split'],b['index']):b for b in reg['reused_training_boards']+reg['boards']}
    assert len(expected)==len(result['board_records'])==1856
    assert len({(b['split'],b['index']) for b in result['board_records']})==1856
    for board in result['board_records']:
        e=expected[(board['split'],board['index'])]
        assert board['board']==e['board'] and board['canonical_group']==e['canonical_group']
        cards=board['board']
        assert len(cards)==len(set(cards))==5 and all(type(c) is int and 0<=c<52 for c in cards)
        reconstructed=min(tuple(sorted((c//4)*4+p[c%4] for c in cards)) for p in permutations(range(4)))
        assert reconstructed==tuple(board['canonical_group'])
        check_ref(board)
        check_ref(dict(file=board['extra_file'],sha256=board['extra_sha256']))
        if board['split']!='fit':assert board['cell']==board_cell(board['board'])
    new=[b for b in result['board_records'] if b['split']!='fit']
    groups={tuple(b['canonical_group']) for b in new}
    assert len(groups)==1344 and not groups & set(map(tuple,reg['excluded_probe_groups']))
    assert len({tuple(b['canonical_group']) for b in result['board_records']})==1856
    for split,count in (('fit_structured',512),('stress',64)):
        quota={cell:sum(b['split']==split and b['cell']==cell for b in new) for cell in allocation(count)}
        assert quota==allocation(count)
    datasets={}
    for split,count in (('test',128),('stress',64)):
        records=[b for b in result['board_records'] if b['split']==split]
        cards=[]
        counts=[]
        for board in records:
            with np.load(board['file'],allow_pickle=False) as z:base=z['features'].copy();counts.append(z['counts'].copy())
            with np.load(board['extra_file'],allow_pickle=False) as z:extra=z['features'].copy()
            assert base.shape==(1081,362) and extra.shape==(1081,25)
            cards.append(np.concatenate((base,extra),axis=1))
        assert len(cards)==count
        cards,counts=np.concatenate(cards),np.concatenate(counts)
        assert np.all(counts.sum(1)==990)
        equity=(counts[:,0]+.5*counts[:,1])/990
        datasets[split]=dict(cards=cards,equity=equity,category=np.argmax(cards[:,269:278],axis=1),board_count=count,
            board_keys=[dict(index=b['index'],canonical_group=b['canonical_group']) for b in records])
    contexts=[public_factors(read(GEOMETRY/f'stack-{depth}-public.json')) for depth in (*reg['fitting_depths'],*reg['heldout_depths'])]
    assert len(result['tests'])==16
    assert {(t['seed'],t['arm'],t['width'],t['split']) for t in result['tests']}=={(s,a,w,split) for s in reg['seeds'] for a in reg['arms'] for w in reg['widths'] for split in ('test','stress')}
    def one(job):
        candidate,split=job
        seed,arm,width=(candidate[k] for k in ('seed','arm','width'))
        data=datasets[split]
        check_ref(candidate['selected']['weights'])
        with np.load(candidate['selected']['weights']['file'],allow_pickle=False) as z:weights={k:z[k].copy() for k in z.files}
        original=next(t for t in result['tests'] if (t['seed'],t['arm'],t['width'],t['split'])==(seed,arm,width,split))
        assert original['board_keys']==data['board_keys'] and len(original['score']['contexts'])==len(contexts)
        replayed=[]
        comparisons=[]
        for context,stored in zip(contexts,original['score']['contexts']):
            guard()
            assert context['stack']==stored['stack']
            def score_rows():
                for state,public in zip(context['economics'],context['features']):
                    guard()
                    x=data['cards'][:,:362]+public
                    if width==387:x=np.concatenate((x,data['cards'][:,362:]),axis=1)
                    yield dense_scores(weights,x,int(state[3]),width)
            rebuilt=reference_context(score_rows(),data['equity'],context['economics'],data['category'],context['stack'],data['board_count'],detail=True,guard=guard)
            comparison=compare_context(stored,rebuilt)
            assert comparison['passed'],(seed,arm,width,split,context['stack'],comparison)
            replayed.append(rebuilt)
            comparisons.append(comparison)
            status('context_verified',seed=seed,arm=arm,width=width,split=split,stack=context['stack'])
        normalized=float(np.mean([c['mean_regret_stack_fraction'] for c in replayed]))
        mean=float(np.mean([c['mean_regret_bb'] for c in replayed]))
        assert abs(normalized-original['score']['context_balanced_mean_regret_stack_fraction'])<1e-5
        assert abs(mean-original['score']['context_balanced_mean_regret_bb'])<1e-4
        assert sum(c['rows'] for c in replayed)==original['score']['rows']
        return dict(seed=seed,arm=arm,width=width,split=split,contexts=replayed,metric_comparisons=comparisons,
            context_balanced_mean_regret_stack_fraction=normalized,context_balanced_mean_regret_bb=mean)
    jobs=[(candidate,split) for split in ('test','stress') for candidate in chosen['candidates']]
    with ThreadPoolExecutor(max_workers=4) as pool:replayed=list(pool.map(one,jobs))
    gates=[]
    for seed in reg['seeds']:
        groups=[[c for c in next(t for t in replayed if (t['seed'],t['arm'],t['width'],t['split'])==(seed,arm,387,'test'))['contexts'] if c['stack'] in reg['heldout_depths']] for arm in reg['arms']]
        baseline,candidate=(float(np.mean([c['mean_regret_stack_fraction'] for c in group])) for group in groups)
        selected=next(c for c in chosen['candidates'] if (c['seed'],c['arm'],c['width'])==(seed,'structured',387))
        passed=baseline>0 and candidate<=.8*baseline and all(c['mean_regret_stack_fraction']<=.001 for c in groups[1])
        assert bool(passed)==next(g for g in result['diagnostic_gates'] if g['seed']==seed)['passed']
        gates.append(dict(seed=seed,passed=bool(passed),baseline=baseline,candidate=candidate))
    verified=dict(passed=True,source_sha256=sha(__file__),inputs=checked,verified_files=len(checked),cpu_replayed=replayed,
        diagnostic_gates=gates,rows_replayed=sum(c['rows'] for t in replayed for c in t['contexts']),
        tolerance_policy=TOLERANCES,all_reported_context_subgroup_board_and_tail_metrics_reconstructed=True,
        seconds=time.monotonic()-_start,gpu_used=False,new_training=False,new_test_data=False,
        full_preflop_accuracy_qualified=False,production_modified=False)
    guard()
    atomic_json(DEST,verified)
    status('complete',rows=verified['rows_replayed'],verified_files=len(checked),gates=gates,seconds=verified['seconds'])

def main():
    assert not LOCK.exists() and not OTHER.exists() and not DEST.exists() and not ATTEMPT.exists()
    assert production_available() and psutil.cpu_percent(interval=1)<50
    assert psutil.virtual_memory().available>28_000_000_000
    with LOCK.open('x') as stream:stream.write(str(os.getpid()))
    try:
        atomic_json(ATTEMPT,dict(pid=os.getpid(),process_created=psutil.Process().create_time(),source_sha256=sha(__file__)))
        run()
    except BaseException as error:
        atomic_json(OUT/(NAME+'-readback-interruption-'+uuid.uuid4().hex[:8]+'.json'),dict(error=repr(error),traceback=traceback.format_exc()))
        status('terminal_error',error=repr(error))
        raise
    finally:
        assert LOCK.read_text()==str(os.getpid())
        LOCK.unlink()

if __name__=='__main__':main()
