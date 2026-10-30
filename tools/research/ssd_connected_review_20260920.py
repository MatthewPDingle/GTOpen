"""Exact scientific checkpoint comparison across four registered storage modes."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/ssd-storage-20260920'
EVIDENCE=OUT.parent/'representative-coverage-20260919'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    status=json.loads((OUT/'connected-v1-status.json').read_text())
    assert status['step']=='complete-awaiting-review'
    assert status['completed']==['resident','ram','ssd','mixed']
    freeze=json.loads((OUT/'connected-v1-runtime-freeze.json').read_text())
    for path,digest in freeze['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in freeze['executables'].items():assert sha(Path(path))==digest,path
    results={name:json.loads((OUT/(name+'-result.json')).read_text()) for name in status['completed']}
    base=results['resident']
    def science(r):
        return {k:r[k] for k in ['boards','board_weights','suit_orbits','root_normalizer','entry_cutoff']} | {
            'records':[(x['iteration'],x['evaluation']) for x in r['records']]}
    assert [r['iteration'] for r in base['records']]==[1,20]
    for name,r in results.items():
        assert science(r)==science(base),f'{name}: scientific output mismatch'
        guard=json.loads((EVIDENCE/f'ssd-connected-v1-{name}-status.json').read_text())
        assert guard['exit_code']==0 and guard['error'] is None
    assert all(not e['disk'] for e in results['ram']['storage']['entries'])
    assert all(e['disk'] for e in results['ssd']['storage']['entries'])
    assert {e['disk'] for e in results['mixed']['storage']['entries']}=={False,True}
    assert sum(e['bytes'] for e in results['mixed']['storage']['entries'] if not e['disk'])<=800_000_000
    writes=sum(e['write_bytes'] for n in ['ssd','mixed'] for e in results[n]['storage']['entries'])
    assert writes<=128*1024**3
    summary={name:dict(checkpoints_exact=True,seconds=r['records'][-1]['elapsed_seconds'],
        storage=r.get('storage')) for name,r in results.items()}
    result=dict(passed=True,scope='Three development boards, both called pots, 20 evolving-range iterations; storage equivalence only',
        summary=summary,strategy_write_bytes=writes,production_ready=False,
        limitation='First integration repeatedly reconstructs full host states, including unnecessary strategy reconstruction for all-in equity. Reported read_bytes counts sweep loads only, excluding evaluation and all-in materialization reads. Correctness passing does not make its runtime acceptable. No large training run qualified.',
        result_sha256={name:sha(OUT/(name+'-result.json')) for name in results})
    with (OUT/'connected-v1-review.json').open('x') as f:json.dump(result,f,indent=2)
    for path,digest in freeze['executables'].items():
        retained=ROOT/'target/qualified-paging'/('ssd-connected-v1-'+Path(path).name)
        assert not retained.exists();shutil.copyfile(path,retained);assert sha(retained)==digest
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
