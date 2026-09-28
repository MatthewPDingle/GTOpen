"""Read-only retained-native comparisons; no model fitting or fresh poker deals."""
import copy
import hashlib
import json
from pathlib import Path
import time
from board_prefix_publication_v1 import atomic_json
from complete_preflop_query_catalog_v1 import build

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='complete-preflop-query-catalog-control-v1'
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json')
CATALOG=OUT/(NAME+'-catalog.json')


def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not any(p.exists() for p in (REG,RESULT,CATALOG)),'Preserve earlier evidence'
    start=time.monotonic();context=OUT/'bb-context-candidate.json'
    matrix=OUT/'preflop-allin-matrix-control-v1-matrix.json'
    native=Path('S:/GTOpen-research/board-root-components-control-v1/preflop-catalog.json')
    reference=OUT/'board-root-components-control-v1-result.json';proof=read(reference);assert proof['passed']
    for p in (native,context,ROOT/'crates/solver/examples/hu_preflop_visible_catalog_v1.rs'):
        assert sha(p)==proof['inputs'][str(p)]
    paths=[Path(__file__),Path(__file__).with_name('complete_preflop_query_catalog_v1.py'),
           context,matrix,native,reference]
    fixtures=[];store=Path('S:/GTOpen-research/weighted-complete-river-training-pilot-v1')
    for arm,index in (('A-river',0),('B-river',1)):
        progress=store/arm/'progress.json';p=read(progress);assert p['completed']==80
        row=p['updates'][index];metric=store/arm/row['metrics'];assert sha(metric)==row['sha256']
        m=read(metric);assert m['iteration']==79+index
        q=metric.parent/'batch-00/queries.json';assert sha(q)==m['subbatches'][0]['artifacts']['queries.json']
        paths.extend([progress,metric,q]);fixtures.append(q)
    inputs={str(p):sha(p) for p in paths}
    atomic_json(REG,dict(inputs=inputs,maximum_seconds=60,gpu_used=False,new_poker_deals=0,
        purpose='Complete supported query construction and native own-history readback only.'))
    n=read(native);source=context.read_text();mat=read(matrix);built=build(n,source,mat)
    observations=built['query']['observations'];lookup={(o['hi'],o['lo']):o for o in observations}
    comparisons=links=0
    def expanded(obs,rows):
        return [(rows[i]['hi'],rows[i]['lo'],a,count) for i,a,count in obs['own_history']]
    for fixture in fixtures:
        q=read(fixture);assert q['context_source']==source
        for o in q['observations']:
            if o['phase']!=0:continue
            expected=lookup[(o['hi'],o['lo'])]
            assert {k:v for k,v in o.items() if k!='own_history'}=={k:v for k,v in expected.items() if k!='own_history'}
            assert expanded(o,q['observations'])==expanded(expected,observations)
            comparisons+=1;links+=len(o['own_history'])
    assert comparisons>0 and links>0
    rejected=0
    for kind in ('duplicate','missing','wrong_class','wrong_key','noninvariant'):
        bad=copy.deepcopy(n)
        if kind=='duplicate':bad['rows'].append(copy.deepcopy(bad['rows'][0]))
        elif kind=='missing':bad['rows'].pop()
        elif kind=='wrong_class':bad['rows'][0]['hand']=[0,4]
        elif kind=='wrong_key':bad['rows'][0]['observation']['hi']='4'
        else:bad['rows'][1]['observation']['active_features'][0]=1
        try:build(bad,source,mat)
        except ValueError:rejected+=1
        else:raise AssertionError('Malformed native catalog accepted')
    try:build(n,source+' ',mat)
    except ValueError:rejected+=1
    else:raise AssertionError('Mismatched context accepted')
    for p,h in inputs.items():assert sha(p)==h
    assert time.monotonic()-start<60
    atomic_json(CATALOG,built)
    result=dict(passed=True,registration_sha256=sha(REG),catalog_sha256=sha(CATALOG),
        physical_rows=built['physical_rows_checked'],canonical_rows=built['canonical_rows_checked'],
        query_rows=len(observations),supported_classes=built['supported_classes'],
        native_preflop_rows_compared=comparisons,native_own_history_links_compared=links,
        invalid_rejections=rejected,seconds=time.monotonic()-start,gpu_used=False,new_poker_deals=0,
        policy_bank_inference_qualified=False,payoff_estimator_qualified=False,accuracy_claim=False)
    atomic_json(RESULT,result);print(json.dumps(result),flush=True)


if __name__=='__main__':main()
