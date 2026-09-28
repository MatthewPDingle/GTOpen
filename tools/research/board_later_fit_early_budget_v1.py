"""Validation-only shorter-fit diagnostic after longer fits overfit; test closed."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
import argparse
import concurrent.futures
import gc
import json
import multiprocessing
from pathlib import Path
import time
import numpy as np
import psutil
from board_later_fit_holdout_run_v1 import ROOT,OUT,LOCK,OTHER,Guard,inputs,read,sha,verify,prepared_dataset
from board_later_fit_holdout_train_v1 import configure,curve,Evaluation
from board_prefix_publication_v1 import atomic_json

PREFIX='board-later-fit-early-budget-v1';STORE=Path('S:/GTOpen-research')/PREFIX
BUDGETS=(64,128,256,512)


def training_and_validation(item):
    data=prepared_dataset(item)
    # Input splitting reconstructs the original source identity, but final-test
    # targets are never passed to inference/scoring in this follow-up.
    del data['raw']['test']
    return data


def main(run=False):
    source,prepared,hashes=inputs()
    old_path=OUT/'board-later-fit-holdout-v1-result.json';old=read(old_path)
    old_registration=OUT/'board-later-fit-holdout-v1-registration.json'
    phase_path=OUT/'board-later-fit-training-phases-v1-result.json';phase=read(phase_path)
    assert old['passed'] and old['complete'] and old['selection']['selected_steps']==512
    assert old['registration_sha256']==sha(old_registration)
    assert phase['passed'] and not phase['final_test_evaluated']
    assert phase['inputs'][str(old_path)]==sha(old_path)
    for p in (Path(__file__),old_path,old_registration,phase_path):hashes[str(p)]=sha(p)
    if not run:
        print(json.dumps(dict(ready=True,steps=BUDGETS,validation_only=True,final_test_closed=True)));return
    guard=Guard();acquired=False;pool=None
    rp=OUT/(PREFIX+'-registration.json');destination=OUT/(PREFIX+'-result.json')
    assert not rp.exists() and not destination.exists() and not STORE.exists()
    assert not LOCK.exists() and not OTHER.exists()
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;guard();assert psutil.cpu_percent(interval=1)<75
        from global_research_inventory_v2 import measure
        inventory=measure();assert sum(r['allocated_file_bytes'] for r in inventory)+100_000_000<800_000_000_000
        guard();configure()
        import torch
        assert torch.cuda.is_available()
        reg=dict(inputs=hashes,datasets=source['datasets'],budgets=BUDGETS,architecture=[302,64,64,4],
            learning_rate=.003,chunk_size=4096,cpu_preparation_workers=2,
            selection='Single common budget minimizing equal-dataset mean postflop validation MSE; ties choose shorter.',
            scope='Follow-up tuning on the SAME validation partition; not new independent confirmation.',
            final_test_evaluated=False,final_test_inaccessible_to_scoring=True,
            baseline_check='Repeated 512-step weights and validation loss must reproduce prior baseline within 1e-7.',
            maximum_seconds=1800,maximum_retained_bytes=100_000_000,maximum_device_bytes=8_000_000_000,
            storage_admission=inventory,resource_sharing='Same qualified light-desktop sharing guard as parent study.',
            new_deals=0,production_modified=False,accuracy_qualified=False,
            pid=os.getpid(),process_created=psutil.Process().create_time(),created_unix=time.time())
        atomic_json(rp,reg);STORE.mkdir();identity=sha(rp)
        atomic_json(STORE/'owner.json',dict(root=str(STORE),registration_sha256=identity))
        pool=concurrent.futures.ProcessPoolExecutor(max_workers=2,mp_context=multiprocessing.get_context('spawn'))
        futures=[pool.submit(training_and_validation,d) for d in source['datasets']]
        data_sets=[]
        for i,future in enumerate(futures):
            while True:
                guard()
                try:data=future.result(timeout=2);break
                except concurrent.futures.TimeoutError:pass
            assert data['proof']==prepared['datasets'][i]['split'] and set(data['raw'])=={'validation'}
            data_sets.append(data)
        pool.shutdown(wait=True);pool=None;records=[]
        for data,prior in zip(data_sets,old['datasets']):
            item=data['item'];assert item['name']==prior['dataset'];name=item['name']
            validation=Evaluation(data['raw']['validation'],data['train']['scale'],guard)
            points=[];baseline_error={}
            def checkpoint(model,record):
                value=validation(model,guard);path=STORE/(name+'-step-'+str(record['step'])+'.pt')
                with path.open('xb') as f:torch.save({k:v.detach().cpu() for k,v in model.state_dict().items()},f)
                if record['step']==512:
                    previous=prior['checkpoints'][0];assert previous['step']==512 and sha(previous['weights'])==previous['weights_sha256']
                    original=torch.load(previous['weights'],weights_only=True,map_location='cpu')
                    difference=max(float((model.state_dict()[k].detach().cpu()-v).abs().max()) for k,v in original.items())
                    loss_error=max(abs(value[k]['normalized_loss']-previous['validation'][k]['normalized_loss']) for k in value)
                    assert difference<1e-7 and loss_error<1e-7,(difference,loss_error)
                    baseline_error.update(maximum_parameter_difference=difference,maximum_validation_loss_difference=loss_error)
                point=dict(**record,validation=value,weights=str(path),weights_sha256=sha(path))
                points.append(point);atomic_json(STORE/(name+'-step-'+str(record['step'])+'.json'),point)
                print(json.dumps(dict(dataset=name,steps=record['step'],postflop_validation_loss=value['postflop']['normalized_loss'])),flush=True)
            timing=curve(data['train'],item['fit_seed'],BUDGETS,checkpoint,guard)
            records.append(dict(dataset=name,checkpoints=points,timing=timing,baseline_reproduction=baseline_error))
            del validation;gc.collect();torch.cuda.empty_cache()
        scores=[dict(steps=b,mean_postflop_validation_loss=float(np.mean([r['checkpoints'][i]['validation']['postflop']['normalized_loss'] for r in records])))
            for i,b in enumerate(BUDGETS)]
        selected=min(scores,key=lambda x:(x['mean_postflop_validation_loss'],x['steps']))['steps']
        verify(hashes)
        retained=sum(p.stat().st_size for p in STORE.iterdir() if p.is_file());assert retained<100_000_000
        result=dict(passed=True,complete=True,registration_sha256=identity,scores=scores,selected_steps=selected,
            datasets=records,final_test_evaluated=False,accuracy_qualified=False,production_modified=False,
            seconds=time.monotonic()-guard.started,retained_bytes=retained,resource_probes=guard.probes)
        atomic_json(destination,result)
        print(json.dumps(dict(complete=True,selected_steps=selected,scores=scores,seconds=result['seconds'])),flush=True)
    finally:
        if pool is not None:
            for p in list(pool._processes.values()):
                if p.is_alive():p.terminate()
            pool.shutdown(wait=True,cancel_futures=True)
        if acquired and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');main(parser.parse_args().run)
