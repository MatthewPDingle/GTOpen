"""Require exact parity on every registered shared-workspace pass."""
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
    assert len(sys.argv)==2 and sys.argv[1] in ['v1','v2']
    version=sys.argv[1];prefix='host-paging' if version=='v1' else 'host-paging-v2'
    runtime=SYM/(prefix+'-runtime-freeze.json');freeze=read(runtime)
    for p,h in freeze['inputs'].items():assert sha(ROOT/p)==h,p
    exe=Path(freeze['executable']);assert sha(exe)==freeze['executable_sha256']
    assert sha(SYM/(prefix+'-build.log'))==freeze['build_log_sha256']
    status=read(OUT/(prefix+'-diagnostic-status.json'))
    assert status['exit_code']==0 and status['error'] is None
    log=OUT/(prefix+'-diagnostic.log');lines=log.read_text().splitlines()
    rows=[json.loads(l.split('HOST_PAGING ',1)[1]) for l in lines if 'HOST_PAGING ' in l]
    summaries=[json.loads(l.split('HOST_PAGING_SUMMARY ',1)[1]) for l in lines if 'HOST_PAGING_SUMMARY ' in l]
    assert len(rows)==720 and len(summaries)==1
    expected=set(itertools.product(range(6),range(1,61),range(2)))
    assert {(r['entry'],r['iteration'],r['player']) for r in rows}==expected
    assert all(all(r[k] for k in ['values_bitwise_equal','arrays_bitwise_equal','park_restore_bitwise_equal','passed']) for r in rows)
    summary=summaries[0];assert summary['entries']==6 and summary['passes']==720 and summary['failures']==0
    if version=='v2':assert summary['candidate_pinned_staging_bytes']==24
    assert '1 passed; 0 failed' in log.read_text()
    resources=read(OUT/(prefix+'-diagnostic-resources.json'))
    sampled=dict(samples=len(resources),minimum_free_host_bytes=min(r['free_host_bytes'] for r in resources),
                 minimum_free_gpu_bytes=min(r['free_gpu_bytes'] for r in resources))
    # Unit-test executable names can be reused by later builds. Keep an exact
    # local copy before compiling the next diagnostic; hashes remain in Git.
    retained=ROOT/'target/qualified-paging'/(prefix+'-diagnostic.exe')
    retained.parent.mkdir(parents=True,exist_ok=True)
    if retained.exists():assert sha(retained)==sha(exe)
    else:retained.write_bytes(exe.read_bytes())
    result=dict(passed=True,version=version,summary=summary,resources=sampled,
                retained_executable=str(retained),retained_executable_sha256=sha(retained),
                integrated_forest_qualified=False,production_deployed=False,
                limitation='Test-only explicit tied traversal, six small trees. All four arrays transfer each pass. Static metadata, full restoration buffers and reference-test solvers are additional. No production throughput or full-forest capacity claim.',
                evidence_sha256={str(p):sha(p) for p in [runtime,log,OUT/(prefix+'-diagnostic-status.json')]})
    with (SYM/(prefix+'-review.json')).open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps(result))

if __name__=='__main__':main()
