"""Read-only replay of the complete-sample conditional evaluation diagnosis."""
import json
from pathlib import Path
import statistics
import time

from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from sampled_physical_deals_v1 import PhysicalDeals
from sampled_allin_protocol_v3 import AllinCache,canonical

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-physical-allin-population-diagnostic-v1'
SOURCE='sampled-physical-hybrid-evaluation-v2'


def read(p):return json.loads(Path(p).read_text())


def main():
    began=time.monotonic();last=0.
    def guard():
        nonlocal last
        now=time.monotonic()
        if now-last>2:
            assert idle() and now-began<1200;last=now
    guard();regpath=OUT/f'{PREFIX}-registration.json';rp=OUT/f'{PREFIX}-result.json'
    reg,result=read(regpath),read(rp);status=read(OUT/f'{PREFIX}-status.json')
    assert status['state']=='complete' and status['error'] is None
    assert result['passed'] and result['registration_sha256']==sha(regpath)
    assert result['source_test_deals']==16384 and result['seconds']<reg['maximum_seconds']
    checked=0
    for group in (reg['inputs'],reg['source_batches'],result['cache_artifacts'],result['evaluation_artifacts']):
        for path,h in group.items():guard();assert sha(path)==h,path;checked+=1
    cache=AllinCache(result['cache_artifact'],result['cache_sha256'])
    original_cache=AllinCache.from_review(OUT/'sampled-physical-allin-training-cache-v1-independent-review.json')
    store=Path(result['cache_artifact']).parent
    keys=[tuple(h) for h in read(store/'keys.json')];missing=[tuple(h) for h in read(store/'missing-keys.json')]
    assert sorted(cache.rows)==keys and len(keys)==reg['unique_keys']
    assert missing==[k for k in keys if k not in original_cache.rows]
    assert len(missing)==result['new_equity_keys']==reg['missing_keys']
    for k in keys:
        if k not in missing:assert cache.rows[k]==original_cache.rows[k]
    reconstructed=[]
    for offset in range(0,len(missing),20):
        folder=store/f'equity-{offset:05d}';inp=read(folder/'input.json');native=read(folder/'native.json')
        assert len(inp['cases'])==len(native)==len(missing[offset:offset+20])
        for h,case,n in zip(missing[offset:offset+20],inp['cases'],native):
            assert list(h)==case['private_cards']==n['private_cards']
            assert n['wins']+n['ties']+n['losses']==n['exact_boards']==1712304
            expected=dict(private_cards=list(h),wins=n['wins'],ties=n['ties'],losses=n['losses'],boards=n['exact_boards'])
            assert cache.rows[h]==expected;reconstructed.append(h)
    assert reconstructed==missing
    sr=read(OUT/f'{SOURCE}-registration.json');source_result=read(OUT/f'{SOURCE}-result.json')
    context_source=Path(sr['context']).read_text();source_store=Path(sr['store'])
    response_path=source_store/'response.json';response=read(response_path)
    assert sha(response_path)==source_result['response_sha256']
    sampler=PhysicalDeals(context_source,mode='full_deck',seed=sr['config']['test_seed'])
    assert sha(result['paired_rows'])==result['paired_rows_sha256'];rows=read(result['paired_rows'])
    assert len(rows)==16384;seen_keys=set();max_error=0.;fallback=0
    names=['baseline']+[f'action-{a}' for a in range(4)]
    for offset in range(0,16384,16):
        guard();folder=store/f'test-{offset}';source=source_store/f'{SOURCE}-test-{offset}'
        original_batch=read(source/'batch.json');batch=read(folder/'batch.json')
        assert batch['deals']==original_batch['deals']==sampler.sample(16)['deals']
        cache.check_batch(batch);seen_keys.update(canonical(d[:4]) for d in batch['deals'])
        profile=read(folder/'profiles.json');original_profile=read(source/'profiles.json')
        assert profile['profiles']==original_profile['profiles']
        assert profile['context_source']==context_source
        assert profile['batch_source']==(folder/'batch.json').read_text()
        native=read(folder/'native.json');old_native=read(source/'native.json')
        assert [p['name'] for p in native['profiles']]==names
        assert native['maximum_forward_cashflow_error']<1e-10 and native['maximum_conservation_error']<1e-10
        assert all(len(p['deals'])==16 for p in native['profiles'])
        summary=read(source/'summary.json');oldpaired=read(source/'paired.json')
        assert sha(source/'summary.json')==source_result['batch_summary_hashes'][source.name]
        for old,new in zip(old_native['profiles'],native['profiles']):
            for a,b in zip(old['deals'],new['deals']):
                assert a['expected_rake']==b['expected_rake'] and a['terminal_mass']==b['terminal_mass']
            if old['name'] in ('action-0','action-1'):assert old['deals']==new['deals']
        for i in range(16):
            row=rows[offset+i];assert row['index']==offset+i and row['hand_class']==summary['classes'][i]
            assert row['original']==oldpaired['differences'][i]
            baseline=native['profiles'][0]['deals'][i]['values'][0]
            actions=[p['deals'][i]['values'][0] for p in native['profiles'][1:]]
            a=response['actions'][row['hand_class']]
            expected=[actions[a]-baseline if a>=0 else 0.]+[v-baseline for v in actions]
            if a<0:fallback+=1
            assert row['conditional']==expected
            error=abs(sum(p*v for p,v in zip(summary['root_probabilities'][i],actions))-baseline)
            max_error=max(max_error,error)
    assert sampler.draws==16384 and sorted(seen_keys)==keys and max_error<1e-9
    diagnostics=[]
    for i,item in enumerate(result['diagnostics']):
        assert item['comparison']==reg['comparisons'][i]
        variance=[]
        for kind in ('original','conditional'):
            values=[r[kind][i] for r in rows];m=statistics.mean(values);v=statistics.variance(values)
            assert abs(m-item[f'{kind}_mean'])<1e-9
            assert abs(v-item[f'{kind}_variance'])<1e-7
            variance.append(v)
        ratio=variance[1]/variance[0];assert abs(ratio-item['variance_ratio'])<1e-11
        diagnostics.append(dict(comparison=item['comparison'],variance_ratio=ratio))
    review=dict(passed=True,registration_sha256=sha(regpath),result_sha256=sha(rp),reviewer_sha256=sha(Path(__file__)),
        checked_hashes=checked,completed_deals=16384,all_classes_retained=len(set(r['hand_class'] for r in rows)),
        fallback_deals=fallback,new_exact_keys=len(missing),maximum_root_mixture_error_bb=max_error,
        diagnostics=diagnostics,seconds=time.monotonic()-began,production_modified=False,
        scope='Full saved-artifact audit, exact cache assembly, original chance-stream replay, unchanged policy/response verification and independent descriptive-statistic recomputation. Does not re-enumerate all boards or rerun neural/native evaluations. No new confidence or policy-strength conclusion.')
    save(OUT/f'{PREFIX}-independent-review.json',review);print(json.dumps(review,indent=2))


if __name__=='__main__':main()
