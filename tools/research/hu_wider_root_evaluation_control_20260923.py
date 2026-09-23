"""Small end-to-end CPU control; never reads the active training candidate."""
import os
os.environ['OPENBLAS_NUM_THREADS']='2'
os.environ['OMP_NUM_THREADS']='2'
import time
from pathlib import Path
import numpy as np
import psutil
from later_average_support_v1 import OUT,read,load_complete_cache,weights
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from sampled_visible_hybrid_checkpoint_v1 import read_object,model_document,verify_bank
from sampled_visible_hybrid_cpu64_v1 import VisibleHybridCpuBank64
from preflop_allin_matrix_v1 import AllinMatrix
from wider_root_evaluation_v1 import run
from reboot_research_idle_v1 import idle

PREFIX='wider-root-evaluation-control-v1'
STORE=Path('S:/GTOpen-research')/PREFIX


def main():
    started=time.monotonic()
    def guard():
        assert time.monotonic()-started<600 and idle() and psutil.virtual_memory().available>20_000_000_000
    guard();assert not STORE.exists()
    rp=OUT/f'{PREFIX}-registration.json';assert not rp.exists()
    review_path=OUT/'sampled-visible-hybrid-allin-control-v1-independent-review.json';review=read(review_path)
    assert review['passed'] and review['terminal_complete'] and review['completed_iterations']==4
    objects=Path('S:/GTOpen-research/sampled-visible-hybrid-allin-control-v1/checkpoint-objects')
    cp=OUT/'bb-context-candidate.json';source=cp.read_text()
    checkpoint=read(objects/review['checkpoint']['file']);assert sha(objects/review['checkpoint']['file'])==review['checkpoint']['sha256']
    verify_bank(objects,4,checkpoint['played_bank'],checkpoint['next_model'],context_source=source)
    docs=[model_document(objects,r,context_source=source) for r in checkpoint['played_bank']]
    bank=VisibleHybridCpuBank64(docs,context_source=source,weights_by_player=weights('linear',4))
    catalog_path=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    catalog=read(catalog_path)['native_observations'];prob,support=bank.average(dict(context_source=source,observations=[r['observation'] for r in catalog]),guard=guard)
    assert len(prob)==265 and np.array_equal(support,np.full(265,10.))
    root=np.zeros((169,4));call=np.zeros(169)
    for row,p in zip(catalog,prob):
        if row['player']==0:root[row['hand_class']]=p
        else:call[row['hand_class']]=p[1]
    mrp,mpp,mapath=[OUT/f'preflop-allin-matrix-control-v1-{k}.json' for k in ('registration','result','independent-review')]
    mp,ma=read(mpp),read(mapath)
    assert ma['passed'] and ma['result_sha256']==sha(mpp) and ma['registration_sha256']==sha(mrp)
    matrix_path=Path(mp['matrix_artifact']);assert sha(matrix_path)==mp['matrix_sha256']==ma['matrix_sha256']
    matrix=AllinMatrix(read(matrix_path),source);e=matrix.evaluate(root,call)
    exact=dict(context_sha256=sha(cp),baseline=root.tolist(),masses=e['bb_entries'].tolist(),
        fold_entries=e['bb_fold_entries'].tolist(),jam_entries=e['bb_jam_entries'].tolist())
    cache=load_complete_cache()
    paths=[Path(__file__),review_path,cp,catalog_path,mrp,mpp,mapath,matrix_path,
        objects/review['checkpoint']['file'],*[objects/r['file'] for r in checkpoint['played_bank']],
        *[ROOT/'tools/research'/name for name in ('wider_root_evaluation_v1.py','exact_aware_root_response_v1.py',
            'sampled_conditional_root_evaluation_v1.py','sampled_player_stratified_response_deals_v2.py',
            'sampled_evaluation_intervals_v1.py','root_residual_evaluation_v1.py','sampled_visible_hybrid_cpu64_v1.py')],
        *[ROOT/'target/release/examples'/name for name in ('hu_sampled_bank_bridge.exe','hu_sampled_profile_allin_evaluation_v1.exe')]]
    config=dict(id=PREFIX,train_seed=194231,test_seed=194232,per_class=2,test_deals=128,batch_size=16,minimum_training_deals=1,family_alpha=.025)
    reg=dict(inputs={str(p):sha(p) for p in paths},config=config,exact=exact,store=str(STORE),
        checkpoint=review['checkpoint'],cache_sha256=cache.sha256,maximum_seconds=600,
        scope='CPU execution/transport control using the completed four-model bank; not a strategic candidate evaluation.',production_modified=False,gpu_used=False)
    save(rp,reg)
    class VisibleOnly:
        def average(self,q,*,guard):
            b=__import__('json').loads(q['batch_source'])
            assert b['format']==2 and not any(k.startswith('allin_') or k=='terminal_estimator' for k in b)
            return bank.average(q,guard=guard)
    result=run(cp,VisibleOnly(),cache,exact,config,STORE,guard)
    assert result['complete'] and result['training_deals']==338 and result['test_deals']==128
    assert result['training_counts']==[2]*169 and result['stability']['eligible_classes']==169
    assert len(result['batch_summary_hashes'])==30
    for p,h in reg['inputs'].items():assert sha(p)==h,p
    guard();save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(rp),
        result_sha256=sha(STORE/'result.json'),training_deals=338,test_deals=128,batches=30,
        seconds=time.monotonic()-started,production_modified=False,gpu_used=False,accuracy_qualified=False,
        scope=reg['scope']))
    print(dict(passed=True,seconds=time.monotonic()-started,phase_timings=result['phase_timings']))


if __name__=='__main__':main()
