"""Review payload planning, independently reconcile old arena counts, preserve limits."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/ssd-storage-20260920'
EVIDENCE=OUT.parent/'representative-coverage-20260919'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert read(OUT/'capacity-v1-status.json')['step']=='complete-awaiting-review'
    freeze=read(OUT/'capacity-v1-runtime-freeze.json')
    for p,h in freeze['inputs'].items():assert sha(ROOT/p)==h,p
    exe=Path(freeze['exe']);assert sha(exe)==freeze['sha256']
    device=read(OUT/'capacity-v1-device.json');full=read(OUT/'capacity-v1-cpu.json')
    assert device['device_payload_validated'] is True and len(device['rows'])==6
    assert full['device_payload_validated'] is False and len(full['rows'])==328
    for mode in ['cpu','device']:
        g=read(EVIDENCE/f'storage-capacity-v1-{mode}-status.json')
        assert g['exit_code']==0 and g['error'] is None
    prior=read(EVIDENCE/'population164-memory-plan.json')
    old={(r['board'],r['pot']):r for r in prior['rows'] if r['future_card_orbits']}
    assert len(old)==328
    for r in full['rows']:
        p=old[(r['board'],r['pot'])]
        assert r['explicit_state_bytes']==p['full_arena_bytes']
        expected=p['packed_arena_bytes'] if r['iso_active'] else p['full_arena_bytes']
        assert r['canonical_state_bytes']==expected
    for result in [device,full]:
        rows=result['rows'];t=result['totals']
        for total,rowkey in [('canonical_state_bytes','canonical_state_bytes'),('host_retained_payload_bytes','host_retained_payload_bytes'),('retained_gpu_payload_bytes','retained_gpu_payload_bytes')]:
            assert t[total]==sum(r[rowkey] for r in rows)
        workspace=sum(max(r['workspace_components_bytes'][i] for r in rows) for i in range(11))
        assert workspace==t['shared_gpu_workspace_bytes']
        assert t['steady_gpu_payload_bytes']==workspace+t['retained_gpu_payload_bytes']
    review=dict(passed=True,scope='Device-validated allocation formulas for six constructor fixtures; CPU-only payload projection for 328 games.',
        device_totals=device['totals'],full_totals=full['totals'],
        limitations=full['note'],production_ready=False,full_forest_device_allocated=False,
        inputs_sha256={str(p.relative_to(ROOT)):sha(p) for p in [OUT/'capacity-v1-device.json',OUT/'capacity-v1-cpu.json',EVIDENCE/'population164-memory-plan.json']})
    with (OUT/'capacity-v1-review.json').open('x') as f:json.dump(review,f,indent=2)
    retained=ROOT/'target/qualified-paging/capacity-v1-audit.exe';assert not retained.exists()
    shutil.copyfile(exe,retained);assert sha(retained)==freeze['sha256']
    print(json.dumps(review,indent=2))

if __name__=='__main__':main()
