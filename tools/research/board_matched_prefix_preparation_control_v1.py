"""Replay historical chance inputs to qualify the matched-prefix specification.

No CUDA initialization, optimizer work or new outcome measurements. This does
not qualify the future runner's execution or its trained state.
"""
import json
from pathlib import Path
import time
from unittest.mock import patch
import numpy as np
from board_matched_prefix_v1 import specification, qualifications, main as prefix_main, STORE
from class_stratified_physical_deals_v1 import ClassStratifiedDeals
from sampled_physical_root_evaluation_v1 import sha,save
from later_average_support_v1 import OUT,read


def main():
    began=time.monotonic(); prefix='board-matched-prefix-preparation-control-v1'
    rp=OUT/f'{prefix}-registration.json'; assert not rp.exists() and not STORE.exists()
    arms,paths,args,_=specification(); old=read(OUT/'weighted-stratified-study-v1-registration.json')
    folders=[]
    for arm in arms:
        root=Path(old['store'])/arm['control']
        for iteration in (1,2):
            matches=[p for p in root.glob(f'iteration-{iteration:04d}-*') if (p/'metrics.json').exists()]
            assert len(matches)==1
            folder=matches[0]; folders.append(folder)
            paths.extend((folder/'source-generation.json',folder/'metrics.json'))
            paths.extend(folder.glob('batch-*/batch.json'))
    paths.extend((Path(__file__).resolve(),Path(__file__).with_name('board_matched_prefix_v1.py'),
                  Path(__file__).with_name('class_stratified_physical_deals_v1.py')))
    inputs={str(p):sha(p) for p in paths}
    save(rp,dict(inputs=inputs,scope='Exact first-two-generation physical deals and action seeds versus historical control artifacts; no fits.',
                 maximum_seconds=120,gpu_used=False,production_modified=False))
    records=[]; k=0
    for arm in arms:
        cfg=arm['config']; sampler=ClassStratifiedDeals(args['context_source'],seed=cfg['sampler_seed'])
        rng=np.random.Generator(np.random.PCG64(cfg['action_seed']))
        for iteration in (1,2):
            folder=folders[k]; k+=1
            drawn=sampler.sample(cfg['deals_per_generation'])
            assert drawn==read(folder/'source-generation.json')
            for chunk in range(8):
                batch=read(folder/f'batch-{chunk:02d}/batch.json')
                assert batch['seed']==int(rng.integers(0,2**63))
                assert batch['deals']==drawn['deals'][chunk*64:(chunk+1)*64]
            restored=ClassStratifiedDeals.restore(sampler.checkpoint(),args['context_source'])
            assert restored.checkpoint()==sampler.checkpoint()
            records.append(dict(arm=arm['name'],iteration=iteration,deals=512,action_batches=8,
                                source_generation_sha256=sha(folder/'source-generation.json')))
    # The pending-qualification branch must fail before CUDA/resource admission.
    with patch('board_matched_prefix_v1.qualifications',return_value=([],['deliberately-missing-control'])):
        try: prefix_main(run=True)
        except AssertionError as error: assert 'readback must finish first' in str(error)
        else: raise AssertionError('Pending control admitted execution')
    assert not STORE.exists()
    _,pending=qualifications()
    for p,h in inputs.items(): assert sha(p)==h,p
    assert time.monotonic()-began<120
    result=dict(passed=True,registration_sha256=sha(rp),records=records,physical_deals_reproduced=2048,
        action_batch_seeds_reproduced=32,pending_gate_rejected=True,still_pending=pending,
        seconds=time.monotonic()-began,gpu_used=False,training_started=False,production_modified=False,
        limitation='Prepares configuration and launch gating only. Full-budget trained prefix and independent audit still required.')
    save(OUT/f'{prefix}-result.json',result); print(json.dumps(result),flush=True)


if __name__=='__main__':main()
