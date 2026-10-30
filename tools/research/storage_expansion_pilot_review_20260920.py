"""Review resource feasibility and accounting; explicitly not an accuracy gate."""
import hashlib
import json
import math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/ssd-storage-20260920'
EVIDENCE=OUT.parent/'representative-coverage-20260919'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def finite(value):
    if isinstance(value,(int,float)):assert math.isfinite(value)
    elif isinstance(value,list):
        for v in value:finite(v)
    elif isinstance(value,dict):
        for v in value.values():finite(v)
def main():
    status=read(OUT/'expansion-pilot-v1-status.json');assert status['step']=='complete-awaiting-review'
    f=read(OUT/'expansion-pilot-v1-freeze.json')
    for p,h in f['inputs'].items():assert sha(ROOT/p)==h,p
    assert sha(Path(f['exe']))==f['exe_sha256']
    g=read(EVIDENCE/'expansion-pilot-v1-status.json');assert g['exit_code']==0 and g['error'] is None
    count=f['selected_boards'];r=read(OUT/'expansion-pilot-v1-result.json');finite(r)
    manifest=read(OUT/f'expansion-train-{count}.json');assert r['manifest']==manifest
    assert r['boards']==[b['board'] for b in manifest['boards']]
    assert len(r['boards'])==count and [x['iteration'] for x in r['records']]==[1,20]
    assert abs(sum(r['board_weights'])-1)<1e-12
    assert all(abs(w-1/count)<1e-12 for w in r['board_weights'])
    assert r['root_normalizer']>0 and r['entry_cutoff']==0.00001 and r['suit_orbits'] is True
    for rec in r['records']:
        e=rec['evaluation'];assert abs(e['terminal_probability']-1)<0.00001
        assert e['conservation_error']<0.0001 and min(e['gaps'])>-0.0001
        assert abs(sum(e['ev'])+e['expected_rake']-3.5)<0.0001
        assert abs(sum(e['root_frequencies'])-1)<0.00001
        assert abs(sum(h['root_mass'] for h in e['hands'])-1)<0.00001
        for hand in e['hands']:
            assert all(-1e-12<=p<=1+1e-12 for p in hand['strategy'])
            if hand['root_mass']>0:assert abs(sum(hand['strategy'])-1)<1e-10
        for node in e['preflop_policy']:
            if not node:continue
            assert all(len(a)==1326 for a in node)
            for column in zip(*node):
                assert all(-1e-12<=p<=1+1e-12 for p in column)
                assert abs(sum(column)-1)<1e-10
    cap=read(OUT/f'expansion-capacity-{count}.json')['totals'];entries=r['storage']['entries']
    assert len(entries)==2*count and all(not e['disk'] and e['read_bytes']==e['write_bytes']==0 for e in entries)
    assert sum(e['bytes'] for e in entries)==cap['canonical_state_bytes']
    assert r['storage']['workspace_bytes']==cap['shared_gpu_workspace_bytes']
    samples=read(EVIDENCE/'expansion-pilot-v1-resources.json');assert samples
    free_host=min(s['free_host_bytes'] for s in samples);free_gpu=min(s['free_gpu_bytes'] for s in samples)
    assert free_host>=20_000_000_000 and free_gpu>=3_000_000_000
    interval=(r['records'][1]['elapsed_seconds']-r['records'][0]['elapsed_seconds'])/19
    review=dict(passed=True,selected_boards=count,iterations=20,total_seconds=g['seconds'],seconds_per_iteration_1_to_20=interval,
        minimum_sampled_free_host_bytes=free_host,minimum_sampled_free_gpu_bytes=free_gpu,state_bytes=cap['canonical_state_bytes'],
        final_gap=r['records'][-1]['evaluation']['gap_total'],production_ready=False,accuracy_improvement_claim=False,
        scope='Resource and probability/conservation qualification only; 20 iterations are not a converged strategy.',
        timing_note='Interval includes final CPU evaluation and excludes most setup; one pilot, not a statistically controlled speed measurement.',
        result_sha256=sha(OUT/'expansion-pilot-v1-result.json'))
    with (OUT/'expansion-pilot-v1-review.json').open('x') as dest:json.dump(review,dest,indent=2)
    print(json.dumps(review,indent=2))
if __name__=='__main__':main()
