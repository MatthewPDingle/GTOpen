"""Readback controls for reusable conditional cache assembly; old fixtures only."""
import itertools
import json
from pathlib import Path
import time
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from sampled_allin_protocol_v3 import AllinCache,canonical
from sampled_conditional_cache_builder_v1 import build

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-conditional-cache-builder-control-v1'
STORE=Path('S:/GTOpen-research')/PREFIX


def main():
    started=time.monotonic();last=0.
    def guard():
        nonlocal last
        now=time.monotonic()
        if now-last>=2:
            assert now-started<600 and idle()
            assert psutil.virtual_memory().available>=20_000_000_000
            assert psutil.disk_usage(str(STORE.parent)).free>=40_000_000_000
            last=now
    guard();assert not STORE.exists()
    br=OUT/'sampled-physical-allin-training-cache-v1-independent-review.json'
    base=AllinCache.from_review(br)
    gr=OUT/'sampled-physical-allin-population-diagnostic-v1-result.json'
    ga=OUT/'sampled-physical-allin-population-diagnostic-v1-independent-review.json'
    golden=json.loads(gr.read_text());audit=json.loads(ga.read_text())
    assert audit['passed'] and audit['result_sha256']==sha(gr)
    gold=AllinCache(golden['cache_artifact'],golden['cache_sha256'])
    ep=OUT/'sampled-physical-hybrid-evaluation-v2-result.json'
    evaluation=json.loads(ep.read_text());sources={};deals=[]
    for offset in range(0,256,16):
        folder=Path('S:/GTOpen-research/sampled-physical-hybrid-evaluation-v2')/f'sampled-physical-hybrid-evaluation-v2-test-{offset}'
        sp=folder/'summary.json';bp=folder/'batch.json'
        assert sha(sp)==evaluation['batch_summary_hashes'][folder.name]
        assert sha(bp)==json.loads(sp.read_text())['artifacts']['batch.json']
        sources.update({str(p):sha(p) for p in (sp,bp)})
        deals+=json.loads(bp.read_text())['deals']
    original=list(deals)
    # Reverse player roles explicitly. The correct result must reverse wins/losses.
    deals += [d[2:4]+d[:2]+d[4:] for d in original[:8]]
    inputs={str(p):sha(p) for p in (Path(__file__),br,gr,ga,ep,
        ROOT/'tools/research/sampled_conditional_cache_builder_v1.py')}
    reg=dict(inputs=inputs,sources=sources,original_deals=256,role_reversals=8,
        maximum_new_keys=264,scope='Integration, cache reuse and role/suit controls on previously inspected fixtures only. No fresh evaluation or GPU work.',production_modified=False)
    rp=OUT/f'{PREFIX}-registration.json';save(rp,reg);STORE.mkdir()
    cache,result=build(deals,base,STORE/'built',maximum_new_keys=264,guard=guard)
    assert result['new_keys']>0 and result['reused_keys']>0
    independent_keys=set()
    for deal in deals:
        candidates=[]
        for perm in itertools.permutations(range(4)):
            remapped=[4*(c//4)+perm[c%4] for c in deal[:4]]
            candidates.append(tuple(sorted(remapped[:2])+sorted(remapped[2:])))
        independent_keys.add(min(candidates))
    assert set(cache.rows)==independent_keys
    for deal in original:
        key=canonical(deal[:4]);assert cache.rows[key]==gold.rows[key]
    for deal in original[:8]:
        old=gold.rows[canonical(deal[:4])];new=cache.rows[canonical(deal[2:4]+deal[:2])]
        assert (new['wins'],new['ties'],new['losses'])==(old['losses'],old['ties'],old['wins'])
    symmetry_checks=0
    for deal in deals[:8]:
        expected=cache.rows[canonical(deal[:4])]
        for perm in itertools.permutations(range(4)):
            remapped=[4*(c//4)+perm[c%4] for c in deal]
            label=cache.labels([remapped])[0]
            assert all(label[k]==expected[k] for k in ('wins','ties','losses','boards'))
            symmetry_checks+=1
    reuse,reused=build(deals,cache,STORE/'reuse-only',maximum_new_keys=0,guard=guard)
    assert reuse.rows==cache.rows and reused['new_keys']==0 and reused['artifacts']=={}
    invalid=[([],base,264),([original[0][:-1]],base,264),
        ([[*original[0][:8],original[0][0]]],base,264),
        ([[52,*original[0][1:]]],base,264),([[True,*original[0][1:]]],base,264),
        (deals,base,-1),(deals,base,0),(deals,None,264)]
    for i,(bad,bc,budget) in enumerate(invalid):
        destination=STORE/f'invalid-{i}'
        try:build(bad,bc,destination,maximum_new_keys=budget,guard=guard)
        except (ValueError,TypeError):pass
        else:raise AssertionError(f'Invalid case {i} accepted')
        assert not destination.exists()
    for p,h in {**inputs,**sources}.items():assert sha(p)==h,p
    for p,h in result['artifacts'].items():assert sha(p)==h,p
    guard()
    output=dict(passed=True,registration_sha256=sha(rp),complete_deals=264,
        original_rows_match_previous_exact_counts=True,independent_keys_match=True,
        reversed_player_roles_checked=8,suit_symmetry_checks=symmetry_checks,
        invalid_cases_rejected=len(invalid),reuse_only_exact=True,
        new_keys=result['new_keys'],reused_keys=result['reused_keys'],
        native_seconds=result['native_seconds'],seconds=time.monotonic()-started,
        artifacts={str(p):sha(p) for p in STORE.rglob('*.json')},
        production_modified=False,accuracy_qualified=False)
    save(OUT/f'{PREFIX}-result.json',output)
    print(json.dumps({k:v for k,v in output.items() if k!='artifacts'}))


if __name__=='__main__':main()
