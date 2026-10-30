"""Reconstruct weighted terminal values directly from retained native evidence."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import hashlib,itertools,json,math,time
from pathlib import Path
import numpy as np
import psutil
from board_prefix_publication_v1 import atomic_json
from bounded_parallel_evaluation_archive_v2 import production_available
from weighted_learning_cuda_control_20260927 import LOCK,OTHER

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='river-range-policy-binding-v1';STORE=Path('S:/GTOpen-research')/NAME
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json')
DEST=OUT/(NAME+'-readback-v1.json')
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assert not DEST.exists() and not LOCK.exists() and not OTHER.exists()
    assert production_available() and psutil.cpu_percent(interval=1)<50 and psutil.virtual_memory().available>28_000_000_000
    result=read(RESULT);reg=read(REG)
    assert result['passed'] and result['complete'] and result['registration_sha256']==sha(REG)
    assert result['job']['active_processes']==0
    started=time.monotonic();records=[];verified=0;maximum=0.;unsupported=0
    with LOCK.open('x') as f:f.write(str(os.getpid()))
    try:
        for path,h in {**reg['inputs'],**result['artifacts']}.items():assert sha(path)==h,path;verified+=1
        entry=[{tuple(map(int,k.split(','))):v for k,v in e.items()} for e in read(STORE/'entry.json')]
        for task in reg['tasks']:
            assert time.monotonic()-started<600 and production_available() and not OTHER.exists()
            assert psutil.virtual_memory().available>24_000_000_000 and psutil.cpu_percent(interval=None)<75
            folder=STORE/f"state-{task['index']}";doc=read(folder/'native-export.json');record=read(folder/'result.json')
            with np.load(folder/'retained.npz',allow_pickle=False) as z:arrays={k:z[k] for k in z.files}
            sigma=arrays['policy'];hands=arrays['hands'];ranks=arrays['ranks'];lookup={tuple(h):i for i,h in enumerate(hands)}
            rows=doc['queries']['observations'];common={};proofs={};support=0
            assert np.shape(sigma)==(len(rows),4) and np.isfinite(sigma).all() and np.all(sigma>=0)
            for i,row in enumerate(rows):assert abs(math.fsum(sigma[i,:row['n']])-1)<1e-12 and not np.any(sigma[i,row['n']:])
            native_ranks=read(folder/'native-ranks.json')
            assert np.array_equal(hands,[r['hand'] for r in native_ranks['rows']])
            assert np.array_equal(ranks,[r['rank'] for r in native_ranks['rows']])
            expected_hands=list(itertools.combinations([c for c in range(52) if c not in task['board']],2))
            assert np.array_equal(hands,expected_hands)
            for j,target in enumerate(doc['targets']):
                perm=task['permutations'][j];inverse=[perm.index(s) for s in range(4)]
                physical=lambda pair:tuple(sorted(c//4*4+inverse[c%4] for c in pair))
                hero=task['actor'];hi=lookup[tuple(task['hands'][j])]
                raw=[];paid=[];equity=[];ids=[];mine=[]
                for k,pair in enumerate(target['pairs']):
                    opp=physical(pair['cards']);oi=lookup[opp];weight=entry[1-hero][tuple(pair['cards'])]
                    likelihood=[];own=[];signature=[]
                    for qi,a,n in pair['path']:
                        assert rows[qi]['n']==n and 0<=a<n
                        if rows[qi]['actor']==hero:own.append(float(sigma[qi,a]))
                        else:
                            likelihood.append(float(sigma[qi,a]));signature.append((rows[qi]['hi'],rows[qi]['lo'],a,n))
                    weight*=math.prod(likelihood)
                    if opp in common:
                        assert abs(common[opp]-weight)<1e-10 and proofs[opp]==signature
                    elif j<3:common[opp]=weight;proofs[opp]=signature
                    else:raise AssertionError('Fourth holding supplied previously uncovered mass')
                    assert not set(opp).intersection(task['hands'][j])
                    node=target['nodes'][pair['root']];fold,call=[target['nodes'][c] for c in node['children']]
                    assert [a['kind'] for a in node['actions']]==['fold','call']
                    assert [fold['kind'],call['kind']]==['fold','showdown']
                    outcome=pair['outcome_loss_tie_win'];assert outcome==(2 if ranks[hi]>ranks[oi] else 1 if ranks[hi]==ranks[oi] else 0)
                    raw.append(weight);paid.append(call['payoff']-fold['payoff']);equity.append(outcome/2);ids.append(oi);mine.append(math.prod(own))
                assert len(raw)==990 and len(set(ids))==990 and max(mine)-min(mine)<1e-12
                total=math.fsum(raw);stored=record['records'][j]
                assert bool(total>0)==stored['supported'] and abs(total-stored['opponent_mass'])<1e-10
                assert abs(mine[0]-stored['own_history_likelihood'])<1e-12
                assert np.array_equal(ids,arrays[f'ids_{j}']) and np.max(abs(np.asarray(raw)-arrays[f'mass_{j}']))<1e-10
                assert np.array_equal(paid,arrays[f'payout_{j}'])
                if total>0:
                    eq=math.fsum(w/total*e for w,e in zip(raw,equity));cash=math.fsum(w/total*v for w,v in zip(raw,paid))
                    assert abs(eq-stored['equity'])<1e-12
                    error=abs(cash-stored['call_minus_fold_bb']);maximum=max(maximum,error);assert error<1e-9;support+=1
                else:
                    assert stored['equity'] is None and stored['call_minus_fold_bb'] is None;unsupported+=1
                if j==2:assert len(common)==1081
            assert set(common)==set(lookup) and np.max(abs(np.asarray([common[tuple(h)] for h in hands])-arrays['weights']))<1e-10
            records.append(dict(index=task['index'],supported=support,rows=4,coverage=len(common)))
        atomic_json(DEST,dict(passed=True,complete=True,source_sha256=sha(__file__),registration_sha256=sha(REG),
            result_sha256=sha(RESULT),verified_hashes=verified,states=len(records),hero_rows=64,pair_rows=64*990,
            records=records,unsupported_rows=unsupported,maximum_payoff_difference_bb=maximum,
            seconds=time.monotonic()-started,gpu_used=False,training_started=False))
        print(json.dumps(read(DEST)),flush=True)
    finally:
        assert LOCK.read_text()==str(os.getpid());LOCK.unlink()

if __name__=='__main__':main()
