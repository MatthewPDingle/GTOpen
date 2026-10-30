"""Read-only full-schedule check of the completed cache through the v3 loader."""
import json
from pathlib import Path
import time
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from sampled_allin_protocol_v3 import AllinCache

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'


def main():
    started=time.monotonic();assert idle()
    reviewpath=OUT/'sampled-physical-allin-training-cache-v1-independent-review.json'
    cache=AllinCache.from_review(reviewpath)
    regpath=OUT/'sampled-physical-allin-training-cache-v1-registration.json'
    reg=json.loads(regpath.read_text());rows=0;source_hashes={};batches=0
    for p,h in reg['source_batches'].items():
        if batches%64==0:assert idle() and time.monotonic()-started<120
        assert sha(p)==h,p;source_hashes[p]=h
        batch=json.loads(Path(p).read_text());converted=cache.batch(batch);cache.check_batch(converted)
        assert converted['deals']==batch['deals'] and converted['seed']==batch['seed']
        assert converted['batch_id']==batch['batch_id'] and converted['query_limit']==batch['query_limit']
        for deal,label in zip(batch['deals'],converted['allin_counts']):
            assert label['private_cards']==deal[:4]
            equity=(label['wins']+.5*label['ties'])/label['boards'];assert 0<=equity<=1
        rows+=len(converted['allin_counts']);batches+=1
    assert rows==39936 and batches==624 and len(cache.rows)==23891
    paths=[Path(__file__),ROOT/'tools/research/sampled_allin_protocol_v3.py',reviewpath,regpath]
    report=dict(passed=True,inputs={str(p):sha(p) for p in paths},source_batches=source_hashes,
        cache_sha256=cache.sha256,physical_training_deals=rows,training_batches=batches,
        canonical_private_pairs=len(cache.rows),missing_keys=0,seconds=time.monotonic()-started,
        production_modified=False,accuracy_qualified=False,
        scope='Read the complete independently audited cache through the actual training loader and mapped every fixed-schedule batch to explicit format 3 without changing deals, seeds or query limits. No native re-enumeration, training or strength evaluation.')
    save(OUT/'sampled-physical-allin-cache-adapter-v1-review.json',report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('inputs','source_batches')}))


if __name__=='__main__':main()
