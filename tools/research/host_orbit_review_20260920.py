"""Review complete registered exact-storage fixture runs, never partial passes."""
import hashlib
import itertools
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/representative-coverage-20260919'
SYM=OUT.parent/'symmetric-bridge-20260919'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())

def main():
    assert len(sys.argv)==2 and sys.argv[1] in ['v2','large']
    version=sys.argv[1];prefix='host-orbit-'+version
    runtime=SYM/(prefix+'-runtime-freeze.json');freeze=read(runtime)
    for p,h in freeze['inputs'].items():assert sha(ROOT/p)==h,p
    assert sha(Path(freeze['executable']))==freeze['executable_sha256']
    assert sha(SYM/(prefix+'-build.log'))==freeze['build_log_sha256']
    status=read(OUT/(prefix+'-diagnostic-status.json'))
    assert status['exit_code']==0 and status['error'] is None
    log=OUT/(prefix+'-diagnostic.log')
    rows=[json.loads(l.split('HOST_ORBIT ',1)[1]) for l in log.read_text().splitlines() if 'HOST_ORBIT ' in l]
    if version=='v2':
        expected=set(itertools.product(['abrupt_pair','smooth_pair'],['KsQs2d','KsQs2s','KsQh2d'],[1,17,100,300]))
        keys=[(r['mode'],r['board'],r['iteration']) for r in rows]
    else:
        expected=set(itertools.product(['5c2h2d','AcQd9d'],[39.5,93.5],['50','50,75'],[1,17,50]))
        keys=[(r['board'],r['pot'],r['menu'],r['iteration']) for r in rows]
        assert all(r['mode']=='abrupt_pair' and r['stack']=={39.5:182.,93.5:155.}[r['pot']] for r in rows)
    assert len(rows)==24 and set(keys)==expected and '1 passed; 0 failed' in log.read_text()
    for r in rows:
        assert r['passed'] and r['restore_differing_values']==0 and r['restore_max_absolute_error']==0
        assert r['resumed_values_bitwise_equal'] and r['resumed_arrays_bitwise_equal']
        assert 0<r['stored_array_bytes']<=r['raw_array_bytes']
        assert r['encode_seconds']>=0 and r['restore_seconds']>=0
    resources=read(OUT/(prefix+'-diagnostic-resources.json'))
    resource_summary=dict(samples=len(resources),minimum_free_host_bytes=min(r['free_host_bytes'] for r in resources),
                          minimum_free_gpu_bytes=min(r['free_gpu_bytes'] for r in resources))
    assert resource_summary['minimum_free_host_bytes']>=20_000_000_000
    result=dict(passed=True,observations=24,rows=rows,resources=resource_summary,
                compact_traversal_qualified=False,integrated_forest_qualified=False,production_deployed=False,
                limitation='Exact restoration and two-pass resumption for these explicitly symmetry-tied fixtures. No whole-forest memory or throughput claim; metadata and full restoration buffers are additional. Does not compress arbitrary asymmetric or unprojected policies losslessly.',
                evidence_sha256={str(p):sha(p) for p in [runtime,log,OUT/(prefix+'-diagnostic-status.json'),OUT/(prefix+'-diagnostic-resources.json')]})
    with (SYM/(prefix+'-review.json')).open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps(dict(version=version,passed=True,resources=resource_summary)))

if __name__=='__main__':main()
