"""Full completed reservoirs and malformed small fixtures; no live state edits."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import copy
import json
from pathlib import Path
import time
import numpy as np
import psutil
from weighted_physical_reservoir_v1 import ARRAYS,WeightedPhysicalReservoir
from weighted_reservoir_bulk_load_v1 import load
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import sha,save
from sampled_visible_hybrid_checkpoint_v1 import read_object


def same(a,b):
    assert a.summary()==b.summary() and a.rng.bit_generator.state==b.rng.bit_generator.state
    assert all(np.array_equal(getattr(a,k),getattr(b,k)) for k in ARRAYS)


def main():
    start=time.monotonic()
    assert psutil.virtual_memory().available>48_000_000_000 and psutil.cpu_percent(interval=1)<60
    def guard():assert time.monotonic()-start<180 and psutil.virtual_memory().available>24_000_000_000
    regpath=OUT/'weighted-stratified-study-v1-registration.json';reg=read(regpath)
    folder=Path(reg['store'])/reg['arms'][0]['name'];progress=read(folder/'progress.json');assert progress['completed']==78
    objects=folder/'objects';cp=json.loads(read_object(objects,progress['checkpoint']))
    context=(OUT/'bb-context-candidate.json').read_text()
    control=Path('T:/GTOpen-research/weighted-reservoir-bulk-load-control-v1');control.mkdir()
    timings=[];inputs={str(regpath):sha(regpath)};fixture=None
    for reference in cp['reservoirs']:
        guard();path=objects/reference['file'];read_object(objects,reference);inputs[str(path)]=sha(path)
        before=time.monotonic();old=WeightedPhysicalReservoir.load(path,context);old_seconds=time.monotonic()-before
        before=time.monotonic();new=load(path,context,guard=guard);new_seconds=time.monotonic()-before
        same(old,new)
        # Verify resumed Algorithm R behavior as well as static arrays/RNG.
        row=(new.keys[0].copy(),new.active[0].copy(),int(new.arity[0]),new.values[0].copy())
        for _ in range(32):
            old._insert(row,79,deal_weight=1.);new._insert(row,79,deal_weight=1.)
        same(old,new)
        timings.append(dict(player=new.player,retained=new.size,old_seconds=old_seconds,new_seconds=new_seconds))
        if fixture is None:
            with np.load(path,allow_pickle=False) as data:
                metadata=json.loads(str(data['metadata']));metadata.update(capacity=2,seen=2)
                fixture=dict(metadata=metadata,arrays={k:data[k][:2].copy() for k in ARRAYS})
        del old,new
    cases=[]
    def check(name,change,accepted=False):
        guard();f=copy.deepcopy(fixture);change(f);path=control/(name+'.npz')
        with path.open('xb') as handle:np.savez(handle,metadata=np.array(json.dumps(f['metadata'])),**f['arrays'])
        answers=[];loaded=[]
        for fn in (WeightedPhysicalReservoir.load,load):
            try:loaded.append(fn(path,context));answers.append(True)
            except (ValueError,KeyError,TypeError):answers.append(False)
        assert answers==[accepted,accepted],(name,answers)
        if accepted:same(*loaded)
        cases.append(dict(name=name,accepted=accepted,sha256=sha(path)))
    check('valid',lambda f:None,True)
    check('unsorted-valid',lambda f:f['arrays']['active'].__setitem__(slice(None),f['arrays']['active'][:,::-1]),True)
    def empty(f):
        f['metadata']['seen']=0;f['arrays']={k:v[:0] for k,v in f['arrays'].items()}
    check('empty',empty,True)
    check('duplicate-feature',lambda f:f['arrays']['active'].__setitem__((0,1),f['arrays']['active'][0,0]))
    check('feature-out-of-range',lambda f:f['arrays']['active'].__setitem__((0,0),269))
    check('invalid-arity',lambda f:f['arrays']['arity'].__setitem__(0,1))
    check('nonfinite-target',lambda f:f['arrays']['values'].__setitem__((0,0),float('nan')))
    def illegal(f):f['arrays']['arity'][0]=2;f['arrays']['values'][0,3]=1
    check('illegal-target',illegal)
    for name,value in [('zero',0.),('negative',-1.),('infinite',float('inf')),('excessive',65537.)]:
        check(name+'-weight',lambda f,v=value:f['arrays']['deal_weights'].__setitem__(0,v))
    check('zero-iteration',lambda f:f['arrays']['iterations'].__setitem__(0,0))
    check('wrong-dtype',lambda f:f['arrays'].__setitem__('keys',f['arrays']['keys'].astype(np.int64)))
    check('wrong-width',lambda f:f['arrays'].__setitem__('active',f['arrays']['active'][:,:35]))
    check('boolean-seen',lambda f:f['metadata'].__setitem__('seen',True))
    check('wrong-context',lambda f:f['metadata'].__setitem__('context_sha256','0'*64))
    check('missing-array',lambda f:f['arrays'].pop('deal_weights'))
    for p in (Path(__file__),Path(__file__).with_name('weighted_reservoir_bulk_load_v1.py'),Path(__file__).with_name('weighted_physical_reservoir_v1.py')):inputs[str(p)]=sha(p)
    for p,h in inputs.items():guard();assert sha(p)==h,p
    result=dict(passed=True,inputs=inputs,checkpoint=progress['checkpoint'],timings=timings,cases=cases,
        control_directory=str(control),resumed_insertions_per_player=32,seconds=time.monotonic()-start,
        gpu_used=False,production_modified=False,live_trainer_unchanged=True,
        scope='Exact full-reservoir arrays, summaries and RNG match; identical continued insertion. Small valid/malformed fixture parity. Separate-process timing during concurrent research, not an end-to-end training speedup.')
    save(OUT/'weighted-reservoir-bulk-load-control-v1-result.json',result)
    print(json.dumps(dict(passed=True,timings=timings,cases=len(cases),seconds=result['seconds'])),flush=True)


if __name__=='__main__':main()
