"""Retain a failed runtime gate; permit separate small exactness experiments, not promotion."""
import hashlib
import json
from pathlib import Path
import psutil
from storage_expansion_pilot_review_20260920 import finite
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/ssd-storage-20260920'
EVIDENCE=OUT.parent/'representative-coverage-20260919'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    status=read(OUT/'expansion-pilot-v1-status.json')
    assert status['step']=='stopped-for-review'
    try:assert psutil.Process(status['pid']).create_time()!=status['created'],'Pilot still live'
    except psutil.NoSuchProcess:pass
    assert not (OUT/'running.lock').exists() and not (EVIDENCE/'running.lock').exists()
    freeze=read(OUT/'expansion-pilot-v1-freeze.json')
    for p,h in freeze['inputs'].items():assert sha(ROOT/p)==h,p
    assert sha(Path(freeze['exe']))==freeze['exe_sha256']
    guard=read(EVIDENCE/'expansion-pilot-v1-status.json')
    assert guard['exit_code']!=0 and guard['error']=='Registered research deadline reached; retained checkpoints.'
    assert 1800<=guard['seconds']<1830
    r=read(OUT/'expansion-pilot-v1-result.json');finite(r)
    assert r['manifest']==read(OUT/'expansion-train-112.json')
    assert len(r['boards'])==112 and [x['iteration'] for x in r['records']]==[1]
    e=r['records'][0]['evaluation']
    assert abs(e['terminal_probability']-1)<1e-5 and e['conservation_error']<1e-4
    assert min(e['gaps'])>-1e-4 and abs(sum(e['root_frequencies'])-1)<1e-5
    cap=read(OUT/'expansion-capacity-112.json')['totals'];entries=r['storage']['entries']
    assert len(entries)==224 and all(not e['disk'] and e['read_bytes']==e['write_bytes']==0 for e in entries)
    assert sum(e['bytes'] for e in entries)==cap['canonical_state_bytes']
    assert r['storage']['workspace_bytes']==cap['shared_gpu_workspace_bytes']
    samples=read(EVIDENCE/'expansion-pilot-v1-resources.json');assert samples[-1]['seconds']>=1780
    host=min(s['free_host_bytes'] for s in samples);gpu=min(s['free_gpu_bytes'] for s in samples)
    assert host>=20_000_000_000 and gpu>=3_000_000_000
    log=(EVIDENCE/'expansion-pilot-v1.log').read_text()
    assert sum(l.startswith('stored ') for l in log.splitlines())==224
    inputs=[OUT/'expansion-pilot-v1-freeze.json',OUT/'expansion-pilot-v1-status.json',OUT/'expansion-pilot-v1-result.json',
        EVIDENCE/'expansion-pilot-v1-status.json',EVIDENCE/'expansion-pilot-v1.log',EVIDENCE/'expansion-pilot-v1-resources.json',Path(__file__)]
    review=dict(runtime_gate_passed=False,capacity_observed=True,all_224_continuations_constructed=True,
        seconds=guard['seconds'],completed_saved_checkpoints=[1],target_iterations=20,
        minimum_sampled_free_host_bytes=host,minimum_sampled_free_gpu_bytes=gpu,
        canonical_state_bytes=cap['canonical_state_bytes'],planned_ssd_state_writes=0,
        allow_small_transfer_experiment=True,production_ready=False,accuracy_improvement_claim=False,
        conclusion='Capacity worked; the 20-iteration runtime gate did not. Do not extend or repeat this unmodified large run.',
        limitation='No per-iteration progress or phase timings between checkpoints. Cannot infer how many updates finished or separate final evaluation from training time.',
        next_action='Separate owner-only transfer and allocation experiments retain their unchanged exactness gates. No broad training or promotion is approved by this failure review.',
        inputs_sha256={str(p.relative_to(ROOT)):sha(p) for p in inputs})
    with (OUT/'expansion-pilot-v1-failure-review.json').open('x') as f:json.dump(review,f,indent=2)
    print(json.dumps(review,indent=2))

if __name__=='__main__':main()
