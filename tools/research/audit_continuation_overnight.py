"""Independent reference accounting and final-artifact audit.

Run with --partial during collection; without it every job/artifact is required.
This does not train, modify manifests, replace checkpoints or contact the app.
"""
import functools
import json
import math
import sys

import numpy as np
import continuation_overnight as night
import range_value_pilot as pilot
from continuation_checkpoint import same_job


@functools.lru_cache(maxsize=210)
def compatible_counts(board):
    """Exact class-pair deal counts after excluding the flop's three cards.

    Start with the Cartesian product of class combos. Subtract products
    sharing each card, then add identical combos back once (counted twice).
    No equity cache or solver reach code is used here.
    """
    excluded=set()
    for i in range(0,len(board),2):
        excluded.add(pilot.RANKS.index(board[i])*4+'cdhs'.index(board[i+1]))
    assert not board or len(excluded)==3
    counts=np.zeros(169,dtype=np.int64)
    incidence=np.zeros((169,52),dtype=np.int64)
    for a in range(52):
        if a in excluded:continue
        for b in range(a+1,52):
            if b in excluded:continue
            hi,lo=max(a//4,b//4),min(a//4,b//4)
            k=hi*13+lo if hi==lo or a%4==b%4 else lo*13+hi
            counts[k]+=1;incidence[k,a]+=1;incidence[k,b]+=1
    result=np.outer(counts,counts)-incidence@incidence.T+np.diag(counts)
    assert (result>=0).all() and np.array_equal(result,result.T)
    cards=52-len(excluded)
    assert result.sum()==math.comb(cards,2)*math.comb(cards-2,2)
    return result


def check_reference(result,job,manifest,case):
    assert result['manifest_id']==manifest['id'] and same_job(result['job'],job)
    gap=result['gap_pct'];assert isinstance(gap,(int,float)) and math.isfinite(gap)
    assert result['target_met'] is True and 0<=gap<=manifest['target_gap_pct']
    if manifest.get('query_mode')=='materialized_full_enumeration':
        assert result['query_mode']==manifest['query_mode']
        assert 0<=result['gpu_gap_pct']<=manifest['target_gap_pct']
        assert result['trace'][-1]['cpu_gap_pct']==gap
        br_means=[sum(h['pair_mass']*h['br_ev_bb'] for h in row)/sum(h['pair_mass'] for h in row) for row in result['hands']]
        reconstructed=(sum(br_means)-job['config']['tree']['starting_pot'])/2/job['config']['tree']['starting_pot']*100
        assert abs(reconstructed-gap)<1e-4
    assert 0<result['iterations']<=manifest['max_iterations']
    assert result['trace'][-1]['iteration']==result['iterations']
    assert abs(result['trace'][-1]['gap_pct']-gap)<1e-12
    assert math.isfinite(result['seconds']) and result['seconds']>0
    pot=job['config']['tree']['starting_pot']
    assert job['config']['tree']['rake_pct']==0
    assert abs(sum(result['means_bb'])-pot)<.002
    # Round through f32, matching the range parser's storage precision.
    w=np.array(case['weights'],dtype=np.float32).astype(float)
    joint=compatible_counts(job['board'])*w[0,:,None]*w[1,None,:]
    expected=np.array([joint.sum(axis=1),joint.sum(axis=0)])
    assert joint.sum()>0
    np.testing.assert_allclose(result['pair_mass'],joint.sum(),rtol=3e-5,atol=1e-5)
    max_relative=0.
    for p in range(2):
        by_hand={h['hand']:h for h in result['hands'][p]}
        assert len(by_hand)==len(result['hands'][p])
        actual=np.zeros(169);value=0.
        for label,h in by_hand.items():
            k=pilot.INDEX[label];actual[k]=h['pair_mass']
            assert actual[k]>0 and all(math.isfinite(h[field]) for field in ['pair_mass','ev_bb','equity','br_ev_bb'])
            assert -1e-5<=h['equity']<=1+1e-5
            value+=actual[k]*h['ev_bb']
        np.testing.assert_allclose(actual,expected[p],rtol=3e-5,atol=1e-6)
        assert abs(value/actual.sum()-result['means_bb'][p])<2e-5
        nz=expected[p]>0
        max_relative=max(max_relative,float(np.max(np.abs(actual[nz]-expected[p,nz])/expected[p,nz])))
    return max_relative


def check_artifacts(m,cases):
    root=night.OUT
    required=['candidate.json','cross-validation.json','evaluation.json','RESULTS.md','comparison.png']
    if any(not (root/p).exists() for p in required):return False
    model=json.loads((root/'candidate.json').read_text())
    cv=json.loads((root/'cross-validation.json').read_text())
    evaluation=json.loads((root/'evaluation.json').read_text())
    train=[c for c in cases.values() if c['partition']=='train'];test=[c for c in cases.values() if c['partition']=='test']
    assert model['manifest_id']==m['id'] and model['production_enabled'] is False
    assert set(model['training_case_ids'])=={c['id'] for c in train} and len(model['training_case_ids'])==len(train)
    assert set(model['training_families'])=={c['family'] for c in train}
    expected_options={(k,a) for k in m['protocol']['candidates'] for a in m['protocol']['ridge']}
    assert {(r['kind'],r['alpha']) for r in cv['scores']}==expected_options and len(cv['scores'])==len(expected_options)
    for row in cv['scores']:
        assert {r['case'] for r in row['cases']}=={c['id'] for c in train} and len(row['cases'])==len(train)
        assert abs(np.mean([r['candidate'] for r in row['cases']])-row['mae_pct_pot'])<1e-9
    chosen=min(cv['scores'],key=lambda r:r['mae_pct_pot'])
    assert chosen['kind']==cv['selected_kind']==model['encoder']['kind']
    assert chosen['alpha']==cv['selected_alpha']==model['alpha']
    assert evaluation['manifest_id']==m['id'] and evaluation['production_enabled'] is False
    assert evaluation['candidate_sha256']==night.file_hash(root/'candidate.json')
    assert {r['case'] for r in evaluation['cases']}=={c['id'] for c in test} and len(evaluation['cases'])==len(test)
    assert {f['family'] for f in evaluation['families']}=={c['family'] for c in test}
    for family in evaluation['families']:
        rows=[r for r in evaluation['cases'] if r['family']==family['family']]
        for key in ['candidate','balanced','raw']:
            expected=np.mean([r['mae_pct_pot'][key] for r in rows])
            assert abs(expected-family['mae_pct_pot'][key])<1e-9
        e=family['mae_pct_pot']
        assert family['point_gate_passed']==bool(e['candidate']<=.85*min(e['balanced'],e['raw']))
    assert evaluation['accuracy_screen_passed']==all(f['point_gate_passed'] for f in evaluation['families'])
    expected_text='passed; further validation required.' if evaluation['accuracy_screen_passed'] else 'failed; do not deploy.'
    assert expected_text in (root/'RESULTS.md').read_text()
    assert (root/'comparison.png').read_bytes()[:8]==b'\x89PNG\r\n\x1a\n'
    return True


def main():
    partial='--partial' in sys.argv
    m=night.checked_manifest();fixtures=json.loads((night.OUT/'fixtures.json').read_text())
    cases={c['id']:c for c in fixtures['cases']};jobs={j['id']:j for j in m['jobs']}
    assert len(cases)==32 and len(jobs)==len(m['jobs'])==3200
    assert night.file_hash(night.ROOT/m.get('binary_path','target/range-value-reference-night1.exe'))==m['binary_sha256']
    partitions={p:{c['source_sha256'] for c in cases.values() if c['partition']==p} for p in ['train','test']}
    assert not partitions['train']&partitions['test']
    boards={p:{b['board'] for b in m['boards'] if b['partition']==p} for p in ['train','test']}
    assert not boards['train']&boards['test'] and all(len(bs)==100 for bs in boards.values())
    paths=sorted((night.OUT/'jobs').glob('*.json'))
    assert {p.stem for p in paths}<=set(jobs)
    largest=0.
    for path in paths:
        job=jobs[path.stem]
        r=json.loads(path.read_text())
        largest=max(largest,check_reference(r,job,m,cases[job['case']]))
    artifacts=check_artifacts(m,cases)
    complete=len(paths)==len(jobs) and artifacts
    out=dict(manifest_id=m['id'],audited_utc=night.now(),complete=complete,
        checked_jobs=len(paths),required_jobs=len(jobs),artifacts_checked=artifacts,
        max_relative_class_pair_mass_error=largest,
        note='Exact combinatorial card-removal accounting independently checked for every available reference. Full completion also requires rendered-graph inspection, final measured-result review, tests and GitHub push.')
    night.dump(night.OUT/('partial-audit.json' if partial else 'completion-audit.json'),out)
    print(json.dumps(out,indent=2))
    if not partial and not complete:raise SystemExit(2)


if __name__=='__main__':main()
