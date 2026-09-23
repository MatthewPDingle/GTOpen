"""CPU-only BTN-conditioned stream through exact-all-in response plumbing."""
import os
os.environ['OPENBLAS_NUM_THREADS']='2'
os.environ['OMP_NUM_THREADS']='2'
import json
import time
from pathlib import Path
import numpy as np
import psutil
from reboot_research_idle_v1 import idle
from sampled_physical_root_evaluation_v1 import ROOT,sha,save,hand_class
from sampled_player_stratified_response_deals_v2 import sample,private_law
from storage_strategic_common_prior_20260920 import CLASSES
from sampled_conditional_cache_builder_v1 import build
from sampled_conditional_root_evaluation_v1 import batch_values
from sampled_conditional_btn_response_v1 import rows,learn,differences
from sampled_visible_hybrid_checkpoint_v1 import read_object,model_document,verify_bank
from sampled_visible_hybrid_cpu64_v1 import VisibleHybridCpuBank64
from sampled_allin_protocol_v3 import AllinCache

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='btn-stratified-conditional-control-v1'
STORE=Path('S:/GTOpen-research')/PREFIX


def main():
    started=time.monotonic();last=0.
    def guard():
        nonlocal last
        now=time.monotonic()
        if now-last>=2:
            assert now-started<900 and idle()
            assert psutil.virtual_memory().available>=20_000_000_000
            assert psutil.disk_usage(str(STORE.parent)).free>=40_000_000_000
            last=now
    guard();assert not STORE.exists()
    context_path=OUT/'bb-context-candidate.json';source=context_path.read_text();context=json.loads(source)
    rp=OUT/'sampled-visible-hybrid-allin-control-v1-independent-review.json';review=json.loads(rp.read_text())
    assert review['passed'] and review['terminal_complete'] and review['completed_iterations']==4
    objects=Path('S:/GTOpen-research/sampled-visible-hybrid-allin-control-v1/checkpoint-objects')
    checkpoint=json.loads(read_object(objects,review['checkpoint']))
    verify_bank(objects,4,checkpoint['played_bank'],checkpoint['next_model'],context_source=source)
    cache_review=OUT/'sampled-physical-allin-training-cache-v1-independent-review.json'
    base=AllinCache.from_review(cache_review)
    _,marginal,_=private_law(source,player=1,seed=0)
    classes=[c for c in range(169) if marginal[CLASSES==c].sum()>0]
    assert len(classes)==96
    paths=[Path(__file__),context_path,rp,cache_review,objects/review['checkpoint']['file'],
        *[objects/r['file'] for r in checkpoint['played_bank']],
        *[ROOT/'tools/research'/n for n in ('sampled_player_stratified_response_deals_v2.py',
            'sampled_conditional_cache_builder_v1.py','sampled_conditional_root_evaluation_v1.py',
            'sampled_conditional_btn_response_v1.py','sampled_visible_hybrid_cpu64_v1.py',
            'reboot_research_idle_v1.py')],
        *[ROOT/'target/release/examples'/n for n in ('hu_sampled_bank_bridge.exe',
            'hu_sampled_profile_allin_evaluation_v1.exe','hu_allin_board_reference.exe')]]
    reg=dict(inputs={str(p):sha(p) for p in paths},seed=193934,conditioned_player=1,
        classes=classes,per_class=2,deals=192,maximum_seconds=900,
        checkpoint=review['checkpoint'],played_generations=list(range(4)),
        scope='BTN-conditioned physical training fixtures with the completed four-model control bank. No active-trial inspection, GPU work or statistical strength test.',production_modified=False)
    registration=OUT/f'{PREFIX}-registration.json';save(registration,reg);STORE.mkdir()
    error=None
    try:
        sampled=sample(source,player=1,seed=reg['seed'],per_class=2,classes=classes,guard=guard)
        save(STORE/'deals.json',sampled)
        cache,cache_result=build(sampled['deals'],base,STORE/'cache',maximum_new_keys=192,guard=guard)
        bank=VisibleHybridCpuBank64([model_document(objects,r,context_source=source) for r in checkpoint['played_bank']],context_source=source)
        class VisibleOnly:
            calls=0
            def average(self,queries,*,guard):
                batch=json.loads(queries['batch_source'])
                assert batch['format']==2 and not any(k.startswith('allin_') or k=='terminal_estimator' for k in batch)
                self.calls+=1
                return bank.average(queries,guard=guard)
        visible=VisibleOnly();response_rows=[];artifacts={};maximum_error=0.
        for offset in range(0,192,16):
            guard();folder=STORE/f'batch-{offset:04d}'
            batch=dict(format=2,batch_id=f'{PREFIX}-{offset}',seed=0,query_limit=100000,deals=sampled['deals'][offset:offset+16])
            summary=batch_values(context_path,batch,folder,guard,visible,cache)
            profiles=json.loads((folder/'profiles.json').read_text());native=json.loads((folder/'native.json').read_text())
            selected,err=rows(context,batch,profiles,native,summary,cache)
            assert [r['hand_class'] for r in selected]==sampled['hand_classes'][offset:offset+16]
            assert [hand_class(d[2:4]) for d in batch['deals']]==[r['hand_class'] for r in selected]
            response_rows.extend(selected);maximum_error=max(maximum_error,err)
            for n in ('query-batch.json','conditional-batch.json','queries.json','profiles.json','native.json','summary.json'):
                artifacts[str(folder/n)]=sha(folder/n)
        assert visible.calls==12 and len(response_rows)==192
        # One observation/class is a transport test only, not the future
        # statistical response-training threshold or a claim of precision.
        response=learn(response_rows[:96],minimum_training_deals=1)
        delta=differences(response,response_rows[96:])
        expected=[]
        for r in response_rows[96:]:
            a=response['actions'][r['hand_class']]
            local=r['baseline_local_value'];chosen=local if a<0 else r['call_value'] if a else r['fold_value']
            expected.append([r['jam_reach']*(v-local) for v in (chosen,r['fold_value'],r['call_value'])])
        assert np.array_equal(delta,expected)
        assert response['counts']==[1 if c in classes else 0 for c in range(169)]
        assert all(response['actions'][c]==-1 for c in range(169) if c not in classes)
        for p,h in reg['inputs'].items():assert sha(p)==h,p
        save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(registration),
            classes=96,deals=192,conditioned_player=1,played_models=4,unlabelled_policy_calls=visible.calls,
            maximum_role_cashflow_error_bb=maximum_error,response_transport_exact=True,
            unsupported_classes_preserved_as_fallback=True,cache_result=cache_result,artifacts=artifacts,
            sample_sha256=sha(STORE/'deals.json'),seconds=time.monotonic()-started,
            scope=reg['scope'],gpu_used=False,production_modified=False,accuracy_qualified=False))
        print(json.dumps(dict(passed=True,classes=96,deals=192,maximum_role_cashflow_error_bb=maximum_error,seconds=time.monotonic()-started)))
    except Exception as exc:error=repr(exc);raise
    finally:
        save(OUT/f'{PREFIX}-status.json',dict(state='stopped' if error else 'complete',error=error,seconds=time.monotonic()-started,production_modified=False))


if __name__=='__main__':main()
