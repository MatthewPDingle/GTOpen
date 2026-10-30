"""Review all registered replay samples and preserve original failures."""
import hashlib
import itertools
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/representative-coverage-20260919'
SYM=OUT.parent/'symmetric-bridge-20260919'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())

def main():
    freeze=read(SYM/'gpu-replay-runtime-freeze.json')
    for p,h in freeze['inputs'].items(): assert sha(ROOT/p)==h,p
    assert sha(Path(freeze['executable']))==freeze['executable_sha256']
    assert sha(SYM/'gpu-replay-build.log')==freeze['build_log_sha256']
    status=read(OUT/'gpu-replay-diagnostic-status.json')
    assert status['exit_code']==0 and status['error'] is None
    log=OUT/'gpu-replay-diagnostic.log'
    rows=[json.loads(l.split('GPU_REPLAY ',1)[1]) for l in log.read_text().splitlines() if 'GPU_REPLAY ' in l]
    keys=[(r['mode'],r['board'],r['iteration'],r['player']) for r in rows]
    expected=set(itertools.product(['abrupt_pair','smooth_pair'],['KsQs2d','KsQs2s','KsQh2d'],[1,2,16,17,50,100],[0,1]))
    assert len(keys)==72 and set(keys)==expected and '1 passed; 0 failed' in log.read_text()
    columns=['same_state_cfv_per_mass','post_root_difference','post_avg_br_difference_per_mass']
    for r in rows:
        assert r['prestate_all_arrays_bitwise_equal'] and r['passed']
        assert all(0<=r[c]<.002 for c in columns)
    result=dict(passed=True,samples=72,maxima={c:max(r[c] for r in rows) for c in columns},
                rows=rows,compact_qualified=False,
                limitation='Sampled local updates only. Average sums use the pre-update policy, so matching average-policy evaluations do not imply identical updated regrets or independent future trajectories. Original smooth and abrupt trajectory failures remain failed.',
                evidence_sha256={str(p):sha(p) for p in [log,SYM/'gpu-replay-runtime-freeze.json',OUT/'gpu-replay-diagnostic-status.json']})
    with (SYM/'gpu-replay-review.json').open('x') as f: json.dump(result,f,indent=2)
    print(json.dumps(result['maxima']))

if __name__=='__main__': main()
