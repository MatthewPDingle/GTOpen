"""Review bounded physical I/O evidence and forecast traffic, not solver speed."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/ssd-storage-20260920'


def main():
    freeze=json.loads((OUT/'physical-v1-freeze.json').read_text())
    for p,digest in freeze['inputs'].items():
        assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==digest,p
    r=json.loads((OUT/'physical-v1-result.json').read_text())
    assert r['passed'] and r['error'] is None
    assert r['total_written_bytes']==r['total_read_bytes']==32*1024**3
    assert Path(r['scratch']).stat().st_size==16*1024**3
    assert [(p['repeat'],p['action']) for p in r['phases']]==[(0,'write'),(0,'read'),(1,'write'),(1,'read')]
    for p in r['phases']:
        assert p['bytes']==16*1024**3 and len(p['chunk_io_seconds'])==2048
        assert abs(sum(p['chunk_io_seconds'])-p['io_seconds'])<1e-8
        assert p['wall_seconds']>=p['io_seconds']+p['flush_seconds']
    speeds={a:sum(p['bytes'] for p in r['phases'] if p['action']==a)/
               sum(p['io_seconds']+p['flush_seconds'] for p in r['phases'] if p['action']==a)
            for a in ['read','write']}
    inclusive={a:sum(p['bytes'] for p in r['phases'] if p['action']==a)/
               sum(p['wall_seconds'] for p in r['phases'] if p['action']==a)
               for a in ['read','write']}
    projections=[]
    for cold_gb in [10,20,40,89.481280128]:
        # Current implementation commits/reads every full cold record for each player sweep.
        volume=cold_gb*1e9*2*2000
        projections.append(dict(cold_state_decimal_gb=cold_gb,iterations=2000,
            read_decimal_tb=volume/1e12,write_decimal_tb=volume/1e12,
            idealized_io_hours=(volume/speeds['read']+volume/speeds['write'])/3600))
    result=dict(passed=True,physical_io_bytes_per_second=speeds,
                inclusive_bytes_per_second=inclusive,traffic_projections=projections,
                caveat='Two 16-GiB repetitions bypass Windows file cache, but not SSD internal caching. Projection assumes these short-test speeds persist and excludes solver work, packing, checksums, evaluation and contention. Not a drive endurance or full-run speed prediction.',
                source_sha256=hashlib.sha256((OUT/'physical-v1-result.json').read_bytes()).hexdigest())
    with (OUT/'physical-v1-review.json').open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
