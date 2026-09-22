"""Independent arithmetic readback of the post-hoc BTN response diagnosis."""
import json
import math
from pathlib import Path
import time
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT, sha, save

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-dense-btn-jam-diagnosis-v1'


def main():
    started = time.monotonic()
    def guard():
        assert idle() and time.monotonic()-started < 600
        assert psutil.virtual_memory().available >= 20_000_000_000
    guard()
    paths = {n:OUT/f'{PREFIX}-{n}.json' for n in ('registration','result','status')}
    reg,result,status = [json.loads(paths[n].read_text()) for n in ('registration','result','status')]
    assert status['state']=='complete' and status['error'] is None and result['passed']
    assert result['registration_sha256']==sha(paths['registration'])
    for p,h in reg['inputs'].items(): assert sha(p)==h,p
    assert sha(result['row_artifact'])==result['rows_sha256']
    assert sha(result['response_artifact'])==result['response_sha256']
    for i,(p,h) in enumerate(result['source_artifacts'].items()):
        if i%128==0: guard()
        assert sha(p)==h,p
    rows = json.loads(Path(result['row_artifact']).read_text())
    response = json.loads(Path(result['response_artifact']).read_text())
    assert len(rows['train'])==8192 and len(rows['test'])==16384
    counts = [0]*169; sums = [[] for _ in range(169)]
    for r in rows['train']:
        c = r['hand_class']; counts[c]+=1
        sums[c].append(r['jam_reach']*(r['call_value']-r['fold_value']))
    advantages = [math.fsum(v) for v in sums]
    choices = [int(advantages[c]>0) if counts[c]>=16 else -1 for c in range(169)]
    assert choices==response['actions'] and counts==response['counts']
    for x,y in zip(advantages,response['weighted_call_advantage']): assert math.isclose(x,y,abs_tol=1e-8,rel_tol=1e-12)
    test = rows['test']; deltas = []; fallback = 0
    for r in rows['train']+test:
        assert r['call_value'] in (-200.,-.75,198.5) and r['fold_value']==-2.
        assert 0<=r['jam_reach']<=1 and 0<=r['baseline_call_probability']<=1
        expected = -2+(r['call_value']+2)*r['baseline_call_probability']
        assert math.isclose(expected,r['baseline_local_value'],abs_tol=1e-12)
    for r in test:
        a = choices[r['hand_class']]; fallback+=int(a<0)
        alternative = r['baseline_local_value'] if a<0 else r['call_value'] if a else -2.
        deltas.append(r['jam_reach']*(alternative-r['baseline_local_value']))
    reach = math.fsum(r['jam_reach'] for r in test)
    rebuilt = dict(mean_bb_jam_reach=reach/16384,
        conditional_btn_call_frequency=math.fsum(r['jam_reach']*r['baseline_call_probability'] for r in test)/reach,
        trained_response_gain_per_spot_entry_bb=math.fsum(deltas)/16384,
        trained_response_gain_per_jam_reached_bb=math.fsum(deltas)/reach,
        always_call_gain_per_spot_entry_bb=math.fsum(r['jam_reach']*(r['call_value']-r['baseline_local_value']) for r in test)/16384,
        always_fold_gain_per_spot_entry_bb=math.fsum(r['jam_reach']*(-2-r['baseline_local_value']) for r in test)/16384,
        mean_baseline_btn_value_per_spot_entry_bb=math.fsum(r['baseline_full_value'] for r in test)/16384)
    for k,v in rebuilt.items(): assert math.isclose(v,result[k],abs_tol=1e-12),k
    assert fallback==result['fallback_test_deals']
    classes = {r['hand_class']:r for r in result['classes']}
    assert set(classes)=={r['hand_class'] for r in test}
    for c,row in classes.items():
        subset = [r for r in test if r['hand_class']==c]; weights = [r['jam_reach'] for r in subset]
        total = math.fsum(weights)
        assert row['test_deals']==len(subset) and row['training_deals']==counts[c]
        assert row['train_selected_action']==choices[c]
        assert all(abs(row['baseline_call_probability']-r['baseline_call_probability'])<1e-12 for r in subset)
        assert math.isclose(row['summed_jam_reach'],total,abs_tol=1e-12)
        assert math.isclose(row['effective_weighted_test_deals'],total**2/math.fsum(w*w for w in weights),abs_tol=1e-12)
        ev = math.fsum(r['jam_reach']*(r['call_value']+2) for r in subset)/total
        assert math.isclose(row['conditional_call_minus_fold'],ev,abs_tol=1e-12)
    guard()
    save(OUT/f'{PREFIX}-independent-review.json',dict(passed=True,reviewer_sha256=sha(Path(__file__)),
        inputs={str(p):sha(p) for p in paths.values()},source_artifacts_verified=len(result['source_artifacts']),
        training_response_reconstructed=True,paired_differences_reconstructed=len(deltas),
        classes_reconstructed=len(classes),means_reconstructed=rebuilt,seconds=time.monotonic()-started,
        production_modified=False,fresh_confirmation=False,
        scope='Artifact and independent arithmetic readback; original rank enumeration/native traversal not rerun. Post-hoc diagnosis only, with no fresh confidence claim or policy promotion.'))
    print(json.dumps(dict(passed=True,source_artifacts=len(result['source_artifacts']),classes=len(classes),means=rebuilt)))


if __name__=='__main__': main()
