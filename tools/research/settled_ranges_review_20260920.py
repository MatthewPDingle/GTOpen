"""Review the registered stationary-tail diagnostic, not the old qualification."""
import hashlib
import itertools
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/representative-coverage-20260919'
SYM=OUT.parent/'symmetric-bridge-20260919'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())

def main():
    freeze=read(SYM/'settled-ranges-runtime-freeze.json')
    for p,h in freeze['inputs'].items():assert sha(ROOT/p)==h,p
    assert sha(Path(freeze['executable']))==freeze['executable_sha256']
    assert sha(SYM/'settled-ranges-build.log')==freeze['build_log_sha256']
    status=read(OUT/'settled-ranges-diagnostic-status.json')
    assert status['exit_code']==0 and status['error'] is None
    log=OUT/'settled-ranges-diagnostic.log'
    rows=[json.loads(l.split('SETTLED ',1)[1]) for l in log.read_text().splitlines() if 'SETTLED ' in l]
    expected=set(itertools.product(['abrupt_pair','smooth_pair'],['KsQs2d','KsQs2s','KsQh2d'],[100,500,1000,2000]))
    assert len(rows)==24 and {(r['mode'],r['board'],r['iteration']) for r in rows}==expected
    final=[r for r in rows if r['iteration']==2000]
    for r in final:
        assert r['settled_diagnostic_passed'] and r['normalizer']>0
        assert all(-1e-6<=x<.01 for x in r['combined_gap'])
        assert all(x>=-1e-6 for p in r['gaps'] for x in p)
        assert r['max_ev_difference_bb']<.002 and r['root_difference']<.01
        assert r['current_range_avg_br_difference_per_mass']<.002
    # Root strategies reproduce exactly. The old evaluator used compact
    # chance for one state; this diagnostic uses full chance for both. Its
    # already-measured same-policy evaluator difference bounds that change.
    original_log=OUT/'coherent-range-diagnostic.log'
    old=[json.loads(l.split('COHERENT ',1)[1]) for l in original_log.read_text().splitlines() if 'COHERENT ' in l]
    initial={(r['mode'],r['board']):r for r in rows if r['iteration']==100}
    assert len(old)==6
    for r in old:
        now=initial[(r['mode'],r['board'])]
        assert abs(now['old_probe_avg_br_difference_per_mass']-r['avg_br_difference']) <= r['same_policy_quotient_difference']+1e-8
        assert abs(now['root_difference']-r['root_drift'])<1e-12
    result=dict(stationary_diagnostic_passed=True,compact_qualified=False,first_100_root_drift_reproduced=True,
                first_100_probe_within_recorded_evaluator_difference=True,
                reviewer_note='An initial review assertion incorrectly expected the old compact/full probe and the new full/full probe to agree within 1e-8. The abrupt two-tone difference was 1.009123e-6, below the independently recorded 2.567129e-6 same-policy evaluator difference. Corrected this cross-evaluator comparison only; native diagnostic gates and outputs are unchanged.',
                largest_final_combined_gap=max(max(r['combined_gap']) for r in final),
                largest_final_ev_difference=max(r['max_ev_difference_bb'] for r in final),
                largest_final_current_range_hand_difference=max(r['current_range_avg_br_difference_per_mass'] for r in final),
                largest_final_old_probe_difference=max(r['old_probe_avg_br_difference_per_mass'] for r in final),
                rows=rows,evidence_sha256={str(p):sha(p) for p in [log,original_log,SYM/'settled-ranges-runtime-freeze.json',OUT/'settled-ranges-diagnostic-status.json']},
                limitation='Converged fixed distributions only. Different-range value disagreement persists; no rapid-range guarantee, no threshold replacement, no production deployment.')
    with (SYM/'settled-ranges-review.json').open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps({k:v for k,v in result.items() if k.startswith('largest_')}))

if __name__=='__main__':main()
