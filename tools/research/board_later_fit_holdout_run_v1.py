"""Bounded, registered four-dataset holdout experiment; no production changes."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
import argparse
import concurrent.futures
import gc
import hashlib
import json
import multiprocessing
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
import psutil
from board_later_fit_holdout_data_v1 import prepare,SALT
from board_later_fit_holdout_train_v1 import configure,curve,control,Evaluation
from weighted_reservoir_bulk_load_v1 import load
from board_prefix_publication_v1 import atomic_json
from bounded_parallel_evaluation_archive_v2 import production_available

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='board-later-fit-holdout-v1'
STORE=Path('S:/GTOpen-research')/PREFIX
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
BUDGETS=(512,2048,8192)


def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify(inputs):
    for p,h in inputs.items():assert sha(p)==h,p


def gpu_snapshot():
    lines=subprocess.check_output(['nvidia-smi','--query-gpu=utilization.gpu,memory.free',
        '--format=csv,noheader,nounits'],creationflags=subprocess.CREATE_NO_WINDOW,timeout=10).decode().splitlines()
    assert len(lines)==1
    use,free=(float(x.strip()) for x in lines[0].split(','))
    return dict(utilization_percent=use,free_bytes=int(free*1024**2))


class Guard:
    def __init__(self):self.started=time.monotonic();self.last=0.;self.last_gpu=0.;self.probes=[]
    def __call__(self):
        assert time.monotonic()-self.started<1800,'Thirty-minute study limit reached'
        if time.monotonic()-self.last<2:return
        assert psutil.virtual_memory().available>24_000_000_000
        assert not OTHER.exists(),'Another study has priority'
        assert production_available(),'Production became active; preserve evidence and yield'
        assert psutil.disk_usage('S:/').free>5_000_000_000
        if 'torch' in sys.modules:
            import torch
            if torch.cuda.is_initialized():
                assert torch.cuda.memory_allocated()<8_000_000_000
                assert torch.cuda.memory_reserved()<8_000_000_000
        self.last=time.monotonic()
        if time.monotonic()-self.last_gpu>30:self.desktop_probe()
    def desktop_probe(self):
        if 'torch' in sys.modules:
            import torch
            if torch.cuda.is_initialized():torch.cuda.synchronize()
        # Stop our work before sampling utilization, so our fit is not mistaken
        # for a competing task. Browser/video spikes may coexist below 65%.
        time.sleep(1.2)
        while True:
            assert time.monotonic()-self.started<1800
            assert production_available()
            value=gpu_snapshot();self.probes.append(dict(elapsed=time.monotonic()-self.started,**value))
            if value['utilization_percent']<65 and value['free_bytes']>10_000_000_000:break
            print(json.dumps(dict(state='yielding_to_other_gpu_work',**value)),flush=True)
            time.sleep(5)
        self.last_gpu=time.monotonic()


def prepared_dataset(item):
    verify(item['inputs'])
    assert psutil.virtual_memory().available>24_000_000_000
    r=load(item['reservoir'],Path(item['context']).read_text())
    assert r.size==item['retained_examples'] and r.player==item['player']
    assert int(r.iterations[:r.size].max())==77
    assert abs(r.deal_weights[:r.size].sum()-item['retained_weight'])<1e-8
    parts,proof,split=prepare(r.active[:r.size],r.arity[:r.size],r.values[:r.size],r.deal_weights[:r.size])
    raw={}
    for i,name in ((1,'validation'),(2,'test')):
        mask=split==i
        raw[name]=dict(active=r.active[:r.size][mask],arity=r.arity[:r.size][mask],
            values=r.values[:r.size][mask],weights=r.deal_weights[:r.size][mask])
    verify(item['inputs'])
    return dict(item=item,train=parts['train'],proof=proof,raw=raw)


def inputs():
    prep_reg=OUT/'board-later-fit-holdout-preparation-v1-registration.json'
    prep_result=OUT/'board-later-fit-holdout-preparation-v1-result.json'
    reg,result=read(prep_reg),read(prep_result)
    assert result['passed'] and result['registration_sha256']==sha(prep_reg)
    verify(reg['inputs'])
    files=[Path(__file__),prep_reg,prep_result,OUT/'BOARD-LATER-FIT-HOLDOUT-PLAN.md']
    files += [ROOT/'tools/research'/n for n in ('board_later_fit_holdout_data_v1.py',
        'board_later_fit_holdout_train_v1.py','weighted_visible_objective_v1.py',
        'sampled_visible_gradient_graph_fit_v1.py','weighted_training_graph_fit_v2.py',
        'sampled_visible_initialization_v1.py','sampled_physical_fit_v1.py',
        'sampled_visible_features_bulk_v1.py','sampled_visible_poker_features_v1.py',
        'weighted_reservoir_bulk_load_v1.py','weighted_physical_reservoir_v1.py',
        'board_prefix_publication_v1.py','global_research_inventory_v2.py')]
    hashes={**reg['inputs'],**{str(p):sha(p) for p in files}}
    return reg,result,hashes


def main(mode):
    source,preparation,hashes=inputs();guard=Guard();acquired=False;pool=None
    if mode=='ready':
        print(json.dumps(dict(ready=True,datasets=4,steps=BUDGETS,maximum_seconds=1800)));return
    assert not LOCK.exists() and not OTHER.exists()
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;guard()
        assert psutil.cpu_percent(interval=1)<75
        configure()
        import torch
        assert torch.cuda.is_available() and os.environ.get('CUDA_VISIBLE_DEVICES')!='-1'
        if mode=='control':
            path=OUT/(PREFIX+'-control.json');assert not path.exists()
            data=prepared_dataset(source['datasets'][0])
            proof=control(data['train'],data['item']['fit_seed'],guard)
            verify(hashes)
            atomic_json(path,dict(**proof,inputs=hashes,resource_probes=guard.probes,seconds=time.monotonic()-guard.started))
            print(json.dumps(proof),flush=True);return
        control_path=OUT/(PREFIX+'-control.json');qualification=read(control_path)
        assert qualification['passed'] and qualification['inputs']==hashes
        hashes[str(control_path)]=sha(control_path)
        rp=OUT/(PREFIX+'-registration.json');result_path=OUT/(PREFIX+'-result.json')
        assert not rp.exists() and not result_path.exists() and not STORE.exists()
        from global_research_inventory_v2 import measure
        inventory=measure();assert sum(x['allocated_file_bytes'] for x in inventory)+500_000_000<800_000_000_000
        guard()
        registration=dict(format=1,inputs=hashes,datasets=source['datasets'],budgets=BUDGETS,salt=SALT,
            architecture=[302,64,64,4],learning_rate=.003,chunk_size=4096,tf32=False,cpu_preparation_workers=2,
            initialization='original saved fit seed; one continuous trajectory per dataset',
            selection='Single budget minimizing equal-dataset mean postflop normalized validation MSE; ties choose shorter.',
            final_test='Only baseline 512 and globally validation-selected budget, after publishing fixed selection.',
            normalization='Training-only scale; raw heldout weighted legal-action squared error.',
            maximum_seconds=1800,maximum_retained_bytes=500_000_000,maximum_device_bytes=8_000_000_000,
            gpu_sharing='Light desktop/video allowed; pause own work to probe competing load every 30 seconds; yield at 65% or <10GB free.',
            storage_admission=inventory,production_modified=False,new_deals=0,accuracy_qualified=False,
            created_unix=time.time(),pid=os.getpid(),process_created=psutil.Process().create_time())
        atomic_json(rp,registration);STORE.mkdir();identity=sha(rp)
        atomic_json(STORE/'owner.json',dict(root=str(STORE),registration_sha256=identity))
        pool=concurrent.futures.ProcessPoolExecutor(max_workers=2,mp_context=multiprocessing.get_context('spawn'))
        futures=[pool.submit(prepared_dataset,item) for item in source['datasets']]
        datasets=[]
        for i,future in enumerate(futures):
            while True:
                guard()
                try:data=future.result(timeout=2);break
                except concurrent.futures.TimeoutError:pass
            assert data['proof']==preparation['datasets'][i]['split']
            datasets.append(data)
        pool.shutdown(wait=True);pool=None
        records=[]
        for data in datasets:
            guard.desktop_probe();torch.cuda.reset_peak_memory_stats()
            item=data['item'];name=item['name'];validation=Evaluation(data['raw']['validation'],data['train']['scale'],guard)
            points=[]
            def checkpoint(model,record):
                value=validation(model,guard);path=STORE/(name+'-step-'+str(record['step'])+'.pt')
                with path.open('xb') as f:torch.save({k:v.detach().cpu() for k,v in model.state_dict().items()},f)
                point=dict(**record,validation=value,weights=str(path),weights_sha256=sha(path))
                points.append(point)
                atomic_json(STORE/(name+'-step-'+str(record['step'])+'.json'),point)
                print(json.dumps(dict(state='checkpoint',dataset=name,step=record['step'],
                    training_loss=record['normalized_training_loss'],validation_postflop_loss=value['postflop']['normalized_loss'])),flush=True)
            timing=curve(data['train'],item['fit_seed'],BUDGETS,checkpoint,guard)
            records.append(dict(dataset=name,checkpoints=points,timing=timing,split=data['proof']))
            del validation;gc.collect();torch.cuda.empty_cache()
        scores=[dict(steps=b,mean_postflop_validation_loss=float(np.mean([
            r['checkpoints'][i]['validation']['postflop']['normalized_loss'] for r in records]))) for i,b in enumerate(BUDGETS)]
        selected=min(scores,key=lambda x:(x['mean_postflop_validation_loss'],x['steps']))['steps']
        selection=dict(registration_sha256=identity,scores=scores,selected_steps=selected,test_evaluated=False)
        atomic_json(STORE/'selection.json',selection)
        tests=[]
        from sampled_visible_initialization_v1 import fresh_visible_network
        for data,record in zip(datasets,records):
            evaluation=Evaluation(data['raw']['test'],data['train']['scale'],guard);points=[]
            for step in sorted({512,selected}):
                point=next(p for p in record['checkpoints'] if p['step']==step)
                assert sha(point['weights'])==point['weights_sha256']
                model=fresh_visible_network(data['item']['fit_seed']).cuda()
                model.load_state_dict(torch.load(point['weights'],weights_only=True,map_location='cuda'))
                points.append(dict(steps=step,metrics=evaluation(model,guard)))
                del model
            tests.append(dict(dataset=data['item']['name'],checkpoints=points));del evaluation
        verify(hashes)
        retained=sum(p.stat().st_size for p in STORE.iterdir() if p.is_file());assert retained<500_000_000
        result=dict(passed=True,complete=True,registration_sha256=identity,selection=selection,
            selection_sha256=sha(STORE/'selection.json'),datasets=records,final_tests=tests,
            resource_probes=guard.probes,seconds=time.monotonic()-guard.started,retained_bytes=retained,
            interpretation='Fixed-data generalization diagnostic only; no preflop strength qualification.',
            production_modified=False,accuracy_qualified=False)
        atomic_json(result_path,result)
        print(json.dumps(dict(state='complete',selected_steps=selected,seconds=result['seconds'],result=str(result_path))),flush=True)
    finally:
        if pool is not None:
            for p in list(pool._processes.values()):
                if p.is_alive():p.terminate()
            pool.shutdown(wait=True,cancel_futures=True)
        if acquired and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=('ready','control','run'),default='ready')
    main(parser.parse_args().mode)
