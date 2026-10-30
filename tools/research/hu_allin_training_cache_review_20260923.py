"""Complete-cache identity, coverage and integer-count readback; no re-enumeration."""
import itertools
import json
from pathlib import Path
import time
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT, sha, save

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-physical-allin-training-cache-v1'


def main():
    started=time.monotonic(); last=0.
    def guard():
        nonlocal last
        now=time.monotonic()
        if now-last>=2:
            assert now-started<600 and idle()
            assert psutil.virtual_memory().available>=20_000_000_000
            last=now
    guard()
    paths={s:OUT/f'{PREFIX}-{s}.json' for s in ('registration','result','status')}
    reg,result,status=[json.loads(paths[s].read_text()) for s in ('registration','result','status')]
    assert status['state']=='complete' and status['error'] is None and result['passed']
    assert result['registration_sha256']==sha(paths['registration'])
    for p,h in reg['inputs'].items(): assert sha(p)==h,p
    permutations=list(itertools.permutations(range(4))); keys=set(); total=0
    for p,h in reg['source_batches'].items():
        guard(); assert sha(p)==h,p
        batch=json.loads(Path(p).read_text()); total+=len(batch['deals'])
        for deal in batch['deals']:
            candidates=[]
            for perm in permutations:
                cards=[(c//4)*4+perm[c%4] for c in deal[:4]]
                candidates.append(tuple(sorted(cards[:2])+sorted(cards[2:])))
            keys.add(min(candidates))
    assert total==39936 and len(keys)==23891
    assert sha(result['keys_artifact'])==result['keys_sha256']
    assert sha(result['cache_artifact'])==result['cache_sha256']
    assert json.loads(Path(result['keys_artifact']).read_text())==[list(k) for k in sorted(keys)]
    cache=json.loads(Path(result['cache_artifact']).read_text()); assert cache['format']==1 and cache['player_roles_fixed']
    reconstructed=[]
    for i,batch in enumerate(result['batches']):
        guard(); assert batch['offset']==20*i
        for p,h in batch['artifacts'].items(): assert sha(p)==h,p
        files={Path(p).name:Path(p) for p in batch['artifacts']}
        inputs=json.loads(files['input.json'].read_text())['cases']; native=json.loads(files['native.json'].read_text())
        assert len(inputs)==len(native)==min(20,23891-20*i)
        for case,row in zip(inputs,native):
            assert case['private_cards']==row['private_cards']
            assert all(type(row[k]) is int and row[k]>=0 for k in ('wins','ties','losses','exact_boards'))
            assert row['wins']+row['ties']+row['losses']==row['exact_boards']==1712304
            assert row['equity']==(row['wins']+.5*row['ties'])/1712304
            reconstructed.append(dict(private_cards=row['private_cards'],wins=row['wins'],ties=row['ties'],losses=row['losses'],boards=row['exact_boards']))
    assert reconstructed==cache['rows'] and [tuple(r['private_cards']) for r in reconstructed]==sorted(keys)
    assert result['completed_keys']==len(reconstructed) and result['exact_boards']==23891*1712304
    assert result['independent_sampled_winner_checks']==23891
    for p,h in reg['inputs'].items(): assert sha(p)==h,p
    guard()
    save(OUT/f'{PREFIX}-independent-review.json',dict(passed=True,reviewer_sha256=sha(Path(__file__)),
        inputs={str(p):sha(p) for p in paths.values()},source_training_deals=total,
        unique_keys_reconstructed=len(keys),native_batches_verified=len(result['batches']),
        cache_artifact=result['cache_artifact'],cache_sha256=result['cache_sha256'],
        exact_boards_recorded=result['exact_boards'],seconds=time.monotonic()-started,
        production_modified=False,accuracy_qualified=False,
        scope='Reconstructed suit-symmetry coverage from every source training deal, verified native batch identities and counts, and rebuilt the entire cache. Exhaustive native enumeration and per-key sampled winner checks were not rerun. No solver-strength claim.'))
    print(json.dumps(dict(passed=True,keys=len(keys),training_deals=total)))


if __name__=='__main__': main()
