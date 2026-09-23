"""Small native-observation catalog for exact root/jam policy lookups.

Checks the completed four-model control only. No active candidate inspection.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='2'
os.environ['OMP_NUM_THREADS']='2'
import itertools
import json
import time
from pathlib import Path
import numpy as np
from reboot_research_idle_v1 import idle
from sampled_physical_root_evaluation_v1 import ROOT,sha,save,hand_class
from sampled_visible_hybrid_checkpoint_v1 import read_object,model_document
from sampled_visible_hybrid_cpu64_v1 import VisibleHybridCpuBank64
from storage_strategic_common_prior_20260920 import PAIRS

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='preflop-catalog-control-v1'
STORE=Path('S:/GTOpen-research')/PREFIX


def main():
    started=time.monotonic()
    def guard():assert time.monotonic()-started<180 and idle()
    guard();assert not STORE.exists()
    context_path=OUT/'bb-context-candidate.json';source=context_path.read_text();context=json.loads(source)
    root=context['nodes'][0];jam_index=root['children'][3];jam=context['nodes'][jam_index]
    assert root['actor']==0 and [a['kind'] for a in root['actions']]==['fold','call','raise','jam']
    assert jam['actor']==1 and [a['kind'] for a in jam['actions']]==['fold','call']
    definitions=[('stratified-conditional-integration-v1',22),('btn-stratified-conditional-control-v1',12)]
    inputs={str(p):sha(p) for p in [Path(__file__),context_path,*[ROOT/'tools/research'/n for n in (
        'sampled_visible_hybrid_cpu64_v1.py','sampled_visible_hybrid_checkpoint_v1.py','reboot_research_idle_v1.py')],
        ROOT/'crates/solver/examples/research_sampled/observation_v1.rs',
        ROOT/'crates/solver/examples/research_sampled/poker_reference_v1.rs']}
    folders=[]
    for prefix,count in definitions:
        rp=OUT/f'{prefix}-registration.json';result_path=OUT/f'{prefix}-result.json'
        result=json.loads(result_path.read_text());registration=json.loads(rp.read_text())
        assert result['passed'] and result['registration_sha256']==sha(rp)
        for p,h in registration['inputs'].items():assert sha(p)==h,p
        inputs.update({str(rp):sha(rp),str(result_path):sha(result_path)})
        for index in range(count):
            folder=Path('S:/GTOpen-research')/prefix/f'batch-{16*index:04d}'
            summary=folder/'summary.json'
            if 'artifacts' in result:assert result['artifacts'][str(summary)]==sha(summary)
            else:assert any(r['path']==str(summary) and r['sha256']==sha(summary) for r in result['summaries'])
            saved=json.loads(summary.read_text())
            for name in ('queries.json','profiles.json'):
                p=folder/name;assert saved['artifacts'][name]==sha(p);inputs[str(p)]=sha(p)
            inputs[str(summary)]=sha(summary);folders.append(folder)
    review_path=OUT/'sampled-visible-hybrid-allin-control-v1-independent-review.json'
    review=json.loads(review_path.read_text());assert review['passed'] and review['completed_iterations']==4
    objects=Path('S:/GTOpen-research/sampled-visible-hybrid-allin-control-v1/checkpoint-objects')
    checkpoint=json.loads(read_object(objects,review['checkpoint']))
    inputs[str(review_path)]=sha(review_path);inputs[str(objects/review['checkpoint']['file'])]=sha(objects/review['checkpoint']['file'])
    for r in checkpoint['played_bank']:inputs[str(objects/r['file'])]=sha(objects/r['file'])
    rp=OUT/f'{PREFIX}-registration.json';save(rp,dict(inputs=inputs,maximum_seconds=180,played_models=4,
        scope='Native preflop-observation catalog and full-batch equivalence control; no model change or strength evaluation.'))
    STORE.mkdir();catalog={};reference={};checks=0
    for folder in folders:
        guard();query=json.loads((folder/'queries.json').read_text());profiles=json.loads((folder/'profiles.json').read_text())
        assert query['context_source']==profiles['context_source']==source
        policies=profiles['profiles'][0]['policies'];assert profiles['profiles'][0]['name']=='baseline'
        assert len(policies)==len(query['observations'])
        for o,p in zip(query['observations'],policies):
            if o['phase']!=0 or int(o['hi']) not in (1,jam_index+1):continue
            assert o['own_history']==[]
            actor=0 if int(o['hi'])==1 else 1;assert o['actor']==actor
            lo=int(o['lo']);c=hand_class([lo&63,(lo>>6)&63]);key=(actor,c)
            if key in catalog:
                assert o==catalog[key]
                assert np.max(abs(np.asarray(reference[key])-p['probabilities']))<1e-12
            else:catalog[key]=o;reference[key]=p['probabilities']
            checks+=1
    assert sum(k[0]==0 for k in catalog)==169 and sum(k[0]==1 for k in catalog)==96
    # Independently enumerate every physical hole combo and all suit mappings.
    # Match the native little-endian observation key, which is distinct from
    # the two-player cache's lexicographic four-card canonical key.
    by_class={};perms=list(itertools.permutations(range(4)))
    for pair in PAIRS:
        physical=list(map(int,pair));c=hand_class(physical);best=None
        for permutation in perms:
            transformed=sorted(4*(v//4)+permutation[v%4] for v in physical)
            packed=transformed[0]+(transformed[1]<<6)
            best=packed if best is None else min(best,packed)
        if c in by_class:assert by_class[c]==best
        else:by_class[c]=best
    for (actor,c),o in catalog.items():
        expected=by_class[c]+sum(63<<(6*i) for i in range(2,7))+(actor<<42)
        assert int(o['lo'])==expected
    ordered=sorted(catalog);observations=[catalog[k] for k in ordered]
    bank=VisibleHybridCpuBank64([model_document(objects,r,context_source=source) for r in checkpoint['played_bank']],context_source=source)
    began=time.monotonic();p,support=bank.average(dict(context_source=source,observations=observations),guard=guard)
    inference_seconds=time.monotonic()-began
    maximum_error=float(np.max(abs(p-np.asarray([reference[k] for k in ordered]))))
    assert maximum_error<1e-12 and np.array_equal(support,np.full(len(ordered),4.))
    catalog_path=STORE/'native-preflop-catalog.json'
    save(catalog_path,dict(format=1,context_source=source,purpose='first BB decision and BTN response to BB jam; no prior own actions',
        native_observations=[dict(player=a,hand_class=c,observation=catalog[(a,c)]) for a,c in ordered]))
    for path,h in inputs.items():assert sha(path)==h,path
    result=dict(passed=True,registration_sha256=sha(rp),catalog_artifact=str(catalog_path),catalog_sha256=sha(catalog_path),
        catalog_observations=len(ordered),native_reference_rows=checks,physical_hole_combos=1326,suit_permutations=24,
        complete_played_models=4,all_own_histories_empty=True,maximum_policy_error=maximum_error,
        catalog_inference_seconds=inference_seconds,seconds=time.monotonic()-started,gpu_used=False,production_modified=False,
        accuracy_qualified=False,scope='Exact visible-key class equivalence and sparse-catalog/full-batch policy equivalence for the completed four-model control. Does not supply showdown equities or qualify a new candidate.')
    save(OUT/f'{PREFIX}-result.json',result);print(json.dumps(result))


if __name__=='__main__':main()
