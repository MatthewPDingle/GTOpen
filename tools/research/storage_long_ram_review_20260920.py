"""Require exact complete scientific checkpoints over the 500-iteration trajectory."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/ssd-storage-20260920'
EVIDENCE=OUT.parent/'representative-coverage-20260919'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def science(r):return {k:r[k] for k in ['boards','board_weights','suit_orbits','root_normalizer','entry_cutoff']}|{'records':[(x['iteration'],x['evaluation']) for x in r['records']]}
def main():
    status=read(OUT/'long-ram-v1-status.json');assert status['step']=='complete-awaiting-review'
    assert set(status['completed'])=={'resident','ram'}
    freeze=read(OUT/'long-ram-v1-freeze.json')
    for p,h in freeze['inputs'].items():assert sha(ROOT/p)==h,p
    for p,h in freeze['binaries'].items():assert sha(Path(p))==h,p
    results={n:read(OUT/f'long-ram-v1-{n}-result.json') for n in ['resident','ram']}
    for name,r in results.items():
        assert [x['iteration'] for x in r['records']]==[1,20,100,500]
        assert science(r)==science(results['resident'])
        old=read(OUT/f'v2-{name}-result.json')
        short=r|{'records':r['records'][:2]};assert science(short)==science(old)
        guard=read(EVIDENCE/f'long-ram-v1-{name}-status.json');assert guard['exit_code']==0 and guard['error'] is None
    assert all(not e['disk'] and e['write_bytes']==0 for e in results['ram']['storage']['entries'])
    timings={n:dict(total_seconds=r['records'][-1]['elapsed_seconds'],
        seconds_per_iteration_100_to_500=(r['records'][-1]['elapsed_seconds']-r['records'][-2]['elapsed_seconds'])/400)
        for n,r in results.items()}
    report=dict(passed=True,checkpoints=[1,20,100,500],all_scientific_values_exact=True,ssd_payload_writes=0,
        timings=timings,final_gap=results['resident']['records'][-1]['evaluation']['gap_total'],
        scope='Same three development boards and restricted two-player branch, longer changing-range trajectory. Not broad accuracy qualification.',
        timing_limit='Sequential diagnostic with checkpoint evaluation included; no statistical speedup claim.',production_ready=False,
        result_sha256={n:sha(OUT/f'long-ram-v1-{n}-result.json') for n in results})
    with (OUT/'long-ram-v1-review.json').open('x') as f:json.dump(report,f,indent=2)
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
