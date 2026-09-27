"""Compare full completed checkpoint recovery, including every historical model."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import copy
import json
from pathlib import Path
import time
import numpy as np
import psutil
import weighted_training_checkpoint_v1 as old
import weighted_checkpoint_bulk_restore_v1 as new
from weighted_physical_reservoir_v1 import ARRAYS
from preflop_allin_matrix_v1 import AllinMatrix
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import sha,save


def same(a,b):
    for name in ('completed_iterations','played_bank','next_model'):assert a[name]==b[name]
    assert a['sampler'].checkpoint()==b['sampler'].checkpoint()
    assert a['action_rng'].bit_generator.state==b['action_rng'].bit_generator.state
    for name in ('root_regret_state','exact_btn_state'):assert a[name].document()==b[name].document()
    for x,y in zip(a['reservoirs'],b['reservoirs']):
        assert x.summary()==y.summary() and x.rng.bit_generator.state==y.rng.bit_generator.state
        assert all(np.array_equal(getattr(x,k),getattr(y,k)) for k in ARRAYS)


def main():
    started=time.monotonic();assert psutil.virtual_memory().available>48_000_000_000 and psutil.cpu_percent(interval=1)<60
    def guard():assert time.monotonic()-started<240 and psutil.virtual_memory().available>24_000_000_000
    helper=OUT/'weighted-reservoir-bulk-load-control-v1-result.json';proof=read(helper);assert proof['passed']
    for p,h in proof['inputs'].items():assert sha(p)==h,p
    rp=OUT/'weighted-stratified-study-v1-registration.json';reg=read(rp);arm=reg['arms'][0]
    folder=Path(reg['store'])/arm['name'];p=read(folder/'progress.json');assert p['completed']==78
    cp=OUT/'bb-context-candidate.json';mp=OUT/'preflop-allin-matrix-control-v1-matrix.json'
    cat=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    args=dict(context_source=cp.read_text(),catalog_source=cat.read_text(),matrix_sha256=sha(mp),entry_mass=AllinMatrix(read(mp),cp.read_text()).btn_mass)
    objects=folder/'objects';timings=[]
    before=time.monotonic();a=old.restore_checkpoint(objects,p['checkpoint'],arm['config'],**args)
    timings.append(dict(method='original-before',seconds=time.monotonic()-before))
    before=time.monotonic();b=new.restore_checkpoint(objects,p['checkpoint'],arm['config'],guard=guard,**args)
    timings.append(dict(method='batched-restore',seconds=time.monotonic()-before));same(a,b)
    before=time.monotonic();c=old.restore_checkpoint(objects,p['checkpoint'],arm['config'],**args)
    timings.append(dict(method='original-after',seconds=time.monotonic()-before));same(a,c);del c
    rejects=[]
    variants=[]
    cfg=copy.deepcopy(arm['config']);cfg['learning_rate']*=2;variants.append(('changed-config',p['checkpoint'],cfg,args))
    reference=dict(p['checkpoint'],sha256='0'*64);variants.append(('bad-object-hash',reference,arm['config'],args))
    variants.append(('changed-matrix',p['checkpoint'],arm['config'],dict(args,matrix_sha256='0'*64)))
    variants.append(('changed-context',p['checkpoint'],arm['config'],dict(args,context_source=args['context_source']+' ')))
    for name,ref,config,values in variants:
        outcomes=[]
        for reader in (old.restore_checkpoint,new.restore_checkpoint):
            try:reader(objects,ref,config,**values);outcomes.append(False)
            except (ValueError,AssertionError):outcomes.append(True)
        assert outcomes==[True,True],name;rejects.append(name)
    assert read(folder/'progress.json')==p
    inputs={str(x):sha(x) for x in [rp,helper,cp,mp,cat,Path(old.__file__),Path(new.__file__),Path(__file__)]}
    output=dict(passed=True,inputs=inputs,checkpoint=p['checkpoint'],completed=78,
        historical_models_checked=79,retained_rows=[r.size for r in a['reservoirs']],timings=timings,rejections=rejects,
        exact_full_state_equal=True,gpu_used=False,live_trainer_unchanged=True,production_modified=False,
        seconds=time.monotonic()-started,scope='Completed checkpoint restore only, during concurrent research. Original-new-original full validation; no end-to-end training or poker accuracy claim.')
    save(OUT/'weighted-checkpoint-bulk-restore-control-v1-result.json',output)
    print(json.dumps(dict(passed=True,timings=timings,retained_rows=output['retained_rows'],rejections=rejects)),flush=True)


if __name__=='__main__':main()
