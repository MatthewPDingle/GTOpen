"""Separate root-policy and later-policy changes using paired saved outcomes."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import concurrent.futures
import json
import multiprocessing
from pathlib import Path
import time
import numpy as np
import psutil
from board_root_action_effects_v1 import initialize,load_chunk,summarize
from board_root_action_replay_store_v1 import sha
from board_prefix_publication_v1 import atomic_json
from weighted_evaluation_readback_v1 import worker_guard

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='board-root-policy-effects-v1'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
PAIRS=((0,1),(0,2),(0,3),(1,2),(1,3),(2,3))


def read(p):return json.loads(Path(p).read_bytes())


def transform(q,classes,root_probabilities):
    n=len(q);roots=np.asarray(root_probabilities).reshape(2,2,169,4)
    p=roots[:,:,classes,:].transpose(2,0,1,3)
    cells=np.einsum('dsra,dsloa->dsrlo',p,q.reshape(n,2,2,2,4))
    old=cells[:,:,0,0];new=cells[:,:,1,1]
    effects=np.stack([cells[:,:,1,0]-old,new-cells[:,:,0,1],
        cells[:,:,0,1]-old,new-cells[:,:,1,0],
        new-cells[:,:,1,0]-cells[:,:,0,1]+old,new-old],axis=2)
    assert np.max(abs(effects[:,:,0]+effects[:,:,3]-effects[:,:,5]))<1e-10
    assert np.max(abs(effects[:,:,1]+effects[:,:,2]-effects[:,:,5]))<1e-10
    cross=q[:,7]-q[:,3]
    cross_pairs=np.stack([cross[:,a]-cross[:,b] for a,b in PAIRS],axis=1)
    return cells,effects,cross,cross_pairs


def main():
    worker_guard();assert psutil.cpu_percent(interval=1)<30 and not LOCK.exists() and not OTHER.exists()
    rp=OUT/'board-root-action-replay-v1-registration.json';ap=OUT/'board-root-action-replay-readback-v1-result.json'
    ar=OUT/'board-root-action-replay-readback-v1-registration.json';reg=read(rp);audit=read(ap)
    assert audit['passed'] and audit['readback_registration_sha256']==sha(ar) and audit['source_registration_sha256']==sha(rp)
    for p,h in read(ar)['inputs'].items():assert sha(p)==h,p
    summary_path=Path(reg['store'])/'summary.json';root_path=Path(reg['root_stability_path'])
    assert sha(root_path)==reg['inputs'][str(root_path)]
    registration=OUT/(PREFIX+'-registration.json');output=OUT/(PREFIX+'-result.json')
    assert not registration.exists() and not output.exists()
    source=ROOT/'tools/research/board_root_action_effects_v1.py'
    evidence=dict(format=1,inputs={str(p):sha(p) for p in (rp,ap,ar,summary_path,root_path,source,Path(__file__))},
        replay_registration=str(rp),replay_registration_sha256=sha(rp),readback_registration=str(ar),
        workers=8,maximum_seconds=600,new_deals=0,gpu_used=False,exploratory=True,accuracy_qualified=False,
        scope='Paired hybrid root/later policies. Roots are fixed saved averages; no sample-maximized action selection.')
    pool=None;acquired=False;started=time.monotonic()
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;assert not OTHER.exists();atomic_json(registration,evidence)
        pool=concurrent.futures.ProcessPoolExecutor(max_workers=8,mp_context=multiprocessing.get_context('spawn'),
            initializer=initialize,initargs=(str(registration),))
        groups=[reg['batches'][i:i+32] for i in range(0,len(reg['batches']),32)]
        futures=[pool.submit(load_chunk,g) for g in groups];all_classes=[];all_q=[]
        for group,future in zip(groups,futures):
            while True:
                worker_guard();assert time.monotonic()-started<600
                try:names,c,q=future.result(timeout=2);break
                except concurrent.futures.TimeoutError:pass
            assert names==group;all_classes.append(c);all_q.append(q)
        pool.shutdown(wait=True);pool=None
        classes=np.concatenate(all_classes);q=np.concatenate(all_q)
        assert q.shape==(65536,8,4) and np.bincount(classes,minlength=169).tolist()==audit['class_evaluation_counts']
        cells,effects,cross,cross_pairs=transform(q,classes,read(root_path)['root_probabilities'])
        summaries=read(summary_path)['profiles'];maximum=0.
        for seed in range(2):
            for later in range(2):
                for opponent in range(2):
                    actual=cells[:,seed,later,later,opponent].mean()
                    expected=summaries[seed*4+later*2+opponent]['overall']['original_mixture_means'][0]
                    maximum=max(maximum,abs(actual-expected));assert abs(actual-expected)<1e-10
        output_data=dict(format=1,passed=True,registration_sha256=sha(registration),deals=65536,
            cell_dimensions=['seed','BB_root_old_new','BB_later_old_new','BTN_old_new'],
            effect_dimensions=['seed','effect','BTN_old_new'],
            effect_order=['root_change_old_later','root_change_new_later','later_change_old_root',
                'later_change_new_root','root_later_interaction','total_BB_change'],
            cells=summarize(cells),effects=summarize(effects),
            cross_seed_candidate_action_difference=summarize(cross),
            cross_seed_candidate_action_pair_difference=summarize(cross_pairs),
            action_order=['fold','call','raise','jam'],action_pair_order=PAIRS,
            classes=[dict(native_class_index=c,cells=summarize(cells[classes==c]),effects=summarize(effects[classes==c]),
                cross_seed_candidate_action_difference=summarize(cross[classes==c]),
                cross_seed_candidate_action_pair_difference=summarize(cross_pairs[classes==c])) for c in range(169)],
            maximum_original_mixture_difference=maximum,exact_decomposition_identities=True,
            source_hashes_unchanged=True,seconds=time.monotonic()-started,
            new_deals=0,gpu_used=False,exploratory=True,accuracy_qualified=False,
            limitations='Paired descriptive SEs on reused data. Cross-seed values change both players, so their difference is not isolated causal attribution.')
        for p,h in evidence['inputs'].items():assert sha(p)==h,p
        atomic_json(output,output_data)
        print(json.dumps({k:v for k,v in output_data.items() if k!='classes'}),flush=True)
    finally:
        if pool is not None:
            for p in list(pool._processes.values()):
                if p.is_alive():p.terminate()
            pool.shutdown(wait=True,cancel_futures=True)
        if acquired:
            assert LOCK.read_text()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':main()
