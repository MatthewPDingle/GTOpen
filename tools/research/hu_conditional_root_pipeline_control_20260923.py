"""CPU integration control against the independently reviewed learned fixtures."""
import os
os.environ['OPENBLAS_NUM_THREADS']='2'
os.environ['OMP_NUM_THREADS']='2'
import json
from pathlib import Path
import time

import numpy as np
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from sampled_conditional_root_evaluation_v1 import batch_values
from sampled_physical_hybrid_checkpoint_v1 import read_object,model_document,verify_bank
from sampled_physical_hybrid_cpu64_v1 import HybridCpuBank64
from sampled_allin_protocol_v3 import AllinCache

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-conditional-root-pipeline-control-v1'
STORE=Path('S:/GTOpen-research')/PREFIX
PRIOR='sampled-physical-allin-learned-evaluation-control-v1'


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
    prior_result=OUT/f'{PRIOR}-result.json';prior_review=OUT/f'{PRIOR}-independent-review.json'
    review=json.loads(prior_review.read_text());assert review['passed'] and review['source_result_sha256']==sha(prior_result)
    prior=json.loads(prior_result.read_text())
    for p,h in prior['artifacts'].items():guard();assert sha(p)==h,p
    source_reg_path=OUT/'sampled-physical-hybrid-evaluation-v1-registration.json'
    source=json.loads(source_reg_path.read_text());objects=Path(source['objects']);context=Path(source['context'])
    checkpoint=json.loads(read_object(objects,source['checkpoint']))
    verify_bank(objects,78,checkpoint['played_bank'],checkpoint['next_model'],context_source=context.read_text())
    models=[model_document(objects,r,context_source=context.read_text()) for r in checkpoint['played_bank']]
    cache_review=OUT/'sampled-physical-allin-training-cache-v1-independent-review.json'
    cache=AllinCache.from_review(cache_review)
    paths=[Path(__file__),prior_result,prior_review,source_reg_path,cache_review,
        ROOT/'tools/research/sampled_conditional_root_evaluation_v1.py',
        ROOT/'tools/research/sampled_physical_hybrid_cpu64_v1.py',
        ROOT/'tools/research/sampled_allin_protocol_v3.py',
        ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe',
        ROOT/'target/release/examples/hu_sampled_bank_bridge.exe']
    reg=dict(inputs={str(p):sha(p) for p in paths},reference_artifacts=prior['artifacts'],
        checkpoint=source['checkpoint'],generations=list(range(78)),complete_deals=256,
        scope='CPU-only direct conditional batch integration against 256 previously reviewed diagnostic deals and all 78 played hybrid models. Exact policy/native-value comparison. No new chance data, response fitting, held-out confirmation, GPU job or deployment.',production_modified=False)
    regpath=OUT/f'{PREFIX}-registration.json';save(regpath,reg);STORE.mkdir()
    bank=HybridCpuBank64(models,context_source=context.read_text())
    # This wrapper enforces the no-label policy boundary at the actual bank call.
    class VisibleOnlyBank:
        calls=0
        def average(self,q,*,guard):
            b=json.loads(q['batch_source'])
            assert b['format']==2 and not any(k.startswith('allin_') or k=='terminal_estimator' for k in b)
            assert all('opponent_cards' not in o and 'allin_equity' not in o for o in q['observations'])
            self.calls+=1;return bank.average(q,guard=guard)
    visible=VisibleOnlyBank();records=[];error=None;max_policy=max_payoff=0.
    try:
        for rep in range(16):
            guard();old=Path('S:/GTOpen-research')/PRIOR/f'runout-{rep:02d}'
            batch=json.loads((old/'batch.json').read_text());folder=STORE/f'runout-{rep:02d}'
            summary=batch_values(context,batch,folder,guard,visible,cache)
            assert summary['format']==2 and len(summary['artifacts'])==5
            assert json.loads((folder/'queries.json').read_text())==json.loads((old/'queries.json').read_text())
            a=json.loads((folder/'profiles.json').read_text());b=json.loads((old/'conditional-profiles.json').read_text())
            assert a==b
            new=json.loads((folder/'native.json').read_text());reference=json.loads((old/'conditional-native.json').read_text())
            assert new==reference
            for p in new['profiles']:
                values=[d['values'][0] for d in p['deals']]
                s=summary['baseline_values'] if p['name']=='baseline' else [r[int(p['name'][-1])] for r in summary['action_values']]
                max_payoff=max(max_payoff,float(np.max(np.abs(np.array(s)-values))))
            records.append(dict(replicate=rep,summary_path=str(folder/'summary.json'),summary_sha256=sha(folder/'summary.json')))
            print(json.dumps(dict(replicate=rep,seconds=time.monotonic()-started)),flush=True)
        assert visible.calls==16 and max_payoff==0
        for p,h in reg['inputs'].items():assert sha(p)==h,p
        save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(regpath),
            records=records,complete_deals=256,played_models=78,policy_and_native_documents_exact=True,
            unlabelled_policy_calls=visible.calls,maximum_summary_payoff_error_bb=max_payoff,
            seconds=time.monotonic()-started,scope=reg['scope'],production_modified=False))
    except Exception as exc:error=str(exc);raise
    finally:save(OUT/f'{PREFIX}-status.json',dict(state='complete' if error is None else 'stopped',error=error,
        seconds=time.monotonic()-started,production_modified=False))


if __name__=='__main__':main()
