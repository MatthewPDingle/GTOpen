"""Score TRAINING rows by street at existing checkpoints; no new fit or test peek."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
import gc
import json
from pathlib import Path
import time
import numpy as np
from board_later_fit_holdout_run_v1 import ROOT,OUT,LOCK,OTHER,Guard,read,sha,verify
from board_later_fit_holdout_train_v1 import configure,Evaluation
from board_later_fit_holdout_data_v1 import prepare
from weighted_reservoir_bulk_load_v1 import load
from sampled_visible_initialization_v1 import fresh_visible_network
from board_prefix_publication_v1 import atomic_json


def main():
    prefix='board-later-fit-training-phases-v1';destination=OUT/(prefix+'-result.json')
    registration=OUT/'board-later-fit-holdout-v1-registration.json'
    source=OUT/'board-later-fit-holdout-v1-result.json'
    reg,result=read(registration),read(source)
    assert result['complete'] and result['passed'] and result['registration_sha256']==sha(registration)
    assert not destination.exists() and not LOCK.exists() and not OTHER.exists()
    verify(reg['inputs']);guard=Guard();acquired=False
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;guard();configure()
        import torch
        assert torch.cuda.is_available()
        rows=[];maximum=0.
        for item,prior in zip(reg['datasets'],result['datasets']):
            assert item['name']==prior['dataset'];verify(item['inputs'])
            r=load(item['reservoir'],Path(item['context']).read_text(),guard=guard)
            parts,proof,split=prepare(r.active[:r.size],r.arity[:r.size],r.values[:r.size],r.deal_weights[:r.size])
            assert proof==prior['split'];mask=split==0
            raw=dict(active=r.active[:r.size][mask],arity=r.arity[:r.size][mask],
                values=r.values[:r.size][mask],weights=r.deal_weights[:r.size][mask])
            evaluation=Evaluation(raw,parts['train']['scale'],guard);points=[]
            for saved in prior['checkpoints']:
                assert sha(saved['weights'])==saved['weights_sha256']
                model=fresh_visible_network(item['fit_seed']).cuda()
                model.load_state_dict(torch.load(saved['weights'],weights_only=True,map_location='cuda'))
                metrics=evaluation(model,guard)
                difference=abs(metrics['all']['normalized_loss']-saved['normalized_training_loss'])
                assert difference<1e-6,difference;maximum=max(maximum,difference)
                points.append(dict(steps=saved['step'],training=metrics,validation=saved['validation']))
                del model
            rows.append(dict(dataset=item['name'],checkpoints=points))
            print(json.dumps(dict(dataset=item['name'],postflop_training_losses=[p['training']['postflop']['normalized_loss'] for p in points])),flush=True)
            del r,parts,raw,evaluation;gc.collect();torch.cuda.empty_cache()
        verify(reg['inputs'])
        atomic_json(destination,dict(passed=True,inputs={str(p):sha(p) for p in (registration,source,Path(__file__))},
            parent_inputs=reg['inputs'],datasets=rows,maximum_direct_grouped_training_difference=maximum,
            new_training=False,final_test_evaluated=False,seconds=time.monotonic()-guard.started))
        print(json.dumps(dict(passed=True,result=str(destination),maximum_training_difference=maximum)),flush=True)
    finally:
        if acquired and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':main()
