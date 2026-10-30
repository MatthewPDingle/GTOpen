"""Independent statistical readback of the exact/Monte Carlo board control."""
import json
import math
from pathlib import Path
from sampled_physical_root_evaluation_v1 import ROOT, sha, save

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-allin-board-control-v1'


def main():
    paths = {s:OUT/f'{PREFIX}-{s}.json' for s in ('registration','result','status')}
    reg,result,status = [json.loads(paths[s].read_text()) for s in ('registration','result','status')]
    assert result['passed'] and status['state']=='complete' and status['error'] is None
    assert result['registration_sha256']==sha(paths['registration'])
    for p,h in reg['inputs'].items(): assert sha(p)==h,p
    for p,h in result['artifacts'].items(): assert sha(p)==h,p
    files = {Path(p).name:Path(p) for p in result['artifacts']}
    cases = json.loads(files['input.json'].read_text())['cases']
    native = json.loads(files['native.json'].read_text())
    assert len(cases)==len(native)==19
    variance=[]
    for case,row in zip(cases,native):
        assert case['private_cards']==row['private_cards']
        assert row['wins']+row['ties']+row['losses']==row['exact_boards']==math.comb(48,5)
        p = (row['wins']+.5*row['ties'])/row['exact_boards']; assert p==row['equity']
        variance.append((row['wins']+.25*row['ties'])/row['exact_boards']-p*p)
        assert len(case['sampled_boards'])==len(row['sampled_scores'])==32*1024
        for board in case['sampled_boards']:
            assert len(set(case['private_cards']+board))==9 and all(0<=c<52 for c in board)
    rebuilt=[]
    for count,actual in zip(reg['prefixes'],result['prefix_results']):
        errors=[]
        for row in native[:16]:
            for repetition in range(32):
                samples=row['sampled_scores'][repetition*1024:repetition*1024+count]
                errors.append(math.fsum(samples)/(2*count)-row['equity'])
        rms=math.sqrt(math.fsum(e*e for e in errors)/512)
        expected=dict(boards_per_label=count,replicate_labels=512,rms_equity_error=rms,
            mean_equity_error=math.fsum(errors)/512,rms_200bb_call_value_error=398.5*rms,
            theoretical_fixture_rms_equity_error=math.sqrt(math.fsum(variance[:16])/16/count))
        assert expected.keys()==actual.keys()
        for k,v in expected.items(): assert math.isclose(v,actual[k],abs_tol=1e-12),k
        rebuilt.append(expected)
    assert result['exact_boards_enumerated']==19*math.comb(48,5)
    assert result['sampled_boards_evaluated']==19*32*1024
    save(OUT/f'{PREFIX}-independent-review.json',dict(passed=True,reviewer_sha256=sha(Path(__file__)),
        inputs={str(p):sha(p) for p in paths.values()},prefix_results=rebuilt,
        scope='Artifact, legal-card and independent scalar statistical readback. Exhaustive native enumeration and independent seven-card winner checks were not rerun. Fixture calculation only; no trained-policy accuracy claim.',
        accuracy_qualified=False,production_modified=False))
    print(json.dumps(dict(passed=True,exact_boards=result['exact_boards_enumerated'])))


if __name__=='__main__': main()
