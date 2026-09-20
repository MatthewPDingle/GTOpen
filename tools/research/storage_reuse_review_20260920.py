"""Exact trajectory and unchanged traffic accounting after reusing parked RAM destinations."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/ssd-storage-20260920'
EVIDENCE=OUT.parent/'representative-coverage-20260919'
LABEL='reuse-download-v1'

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def science(r):
    return {k:r[k] for k in ['boards','board_weights','suit_orbits','root_normalizer','entry_cutoff']}|{
        'records':[(x['iteration'],x['evaluation']) for x in r['records']]}

def main():
    status=read(OUT/f'{LABEL}-status.json')
    assert status['step']=='complete-awaiting-review' and status['completed']==['diagnostic','ram','ssd']
    freeze=read(OUT/f'{LABEL}-runtime-freeze.json')
    for p,h in freeze['inputs'].items():assert sha(ROOT/p)==h,p
    for r in freeze['executables'].values():assert sha(Path(r['path']))==r['sha256']
    guards={}
    for name in status['completed']:
        g=read(EVIDENCE/f'{LABEL}-{name}-status.json');assert g['exit_code']==0 and g['error'] is None
        samples=read(EVIDENCE/f'{LABEL}-{name}-resources.json');assert samples
        assert min(s['free_host_bytes'] for s in samples)>=20_000_000_000
        assert min(s['free_gpu_bytes'] for s in samples)>=3_000_000_000
        guards[name]=g
    log=(EVIDENCE/f'{LABEL}-diagnostic.log').read_text()
    assert 'test result: ok. 1 passed; 0 failed;' in log
    rows=[json.loads(l.split('GPU_STORED_PASS ',1)[1]) for l in log.splitlines() if 'GPU_STORED_PASS {' in l]
    assert len(rows)==720 and all(r['passed'] for r in rows)
    assert {(r['entry'],r['iteration'],r['player']) for r in rows}=={(e,t,p) for e in range(6) for t in range(1,61) for p in range(2)}
    summaries=[json.loads(l.split('GPU_STORED_SUMMARY ',1)[1]) for l in log.splitlines() if 'GPU_STORED_SUMMARY {' in l]
    assert len(summaries)==1
    assert all(summaries[0][k] is True for k in ['values_bitwise_equal','restored_arrays_bitwise_equal','full_device_arrays_bitwise_equal'])
    base=read(OUT/'v2-resident-result.json');assert science(base)==science(read(OUT/'resident-result.json'))
    results={name:read(OUT/f'{LABEL}-{name}-result.json') for name in ['ram','ssd']}
    summary={}
    for name,r in results.items():
        assert science(r)==science(base),name+' numerical mismatch'
        assert r['manifest']==read(OUT/'connected-three.json')
        assert [x['iteration'] for x in r['records']]==[1,20]
        prior=read(OUT/f'owner-download-v1-{name}-result.json');assert len(r['storage']['entries'])==6
        new_bytes=old_bytes=0
        for e,old in zip(r['storage']['entries'],prior['storage']['entries']):
            assert e['bytes']==old['bytes'] and e['disk']==old['disk']==(name=='ssd')
            assert e['read_bytes']==old['read_bytes'] and e['write_bytes']==old['write_bytes']
            # Two player sweeps: two full uploads plus one full state of changed downloads.
            assert e['gpu_transfer_bytes']==3*20*e['bytes']
            assert e['gpu_transfer_bytes']==old['gpu_transfer_bytes']
            new_bytes+=e['gpu_transfer_bytes'];old_bytes+=old['gpu_transfer_bytes']
        assert r['storage']['workspace_bytes']==prior['storage']['workspace_bytes']
        assert sum(e['write_bytes'] for e in r['storage']['entries'])<=64*1024**3
        summary[name]=dict(checkpoints_exact=True,seconds=r['records'][-1]['elapsed_seconds'],
            strategy_transfer_bytes=new_bytes,old_strategy_transfer_bytes=old_bytes,transfer_fraction=new_bytes/old_bytes)
    review=dict(passed=True,diagnostic_passes=720,summary=summary,production_ready=False,
        longer_trajectory_qualified=False,timing_claim=False,
        scope='RAM allocation reuse preserves full device state and 20-iteration changing-range outputs. Both RAM and complete-generation SSD modes checked. Three development boards only.',
        result_sha256={name:sha(OUT/f'{LABEL}-{name}-result.json') for name in results},
        log_sha256=sha(EVIDENCE/f'{LABEL}-diagnostic.log'))
    with (OUT/f'{LABEL}-review.json').open('x') as f:json.dump(review,f,indent=2)
    print(json.dumps(review,indent=2))

if __name__=='__main__':main()
