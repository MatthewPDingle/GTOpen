"""One preregistered source/scale, with exclusive artifacts and pinned inputs."""
import argparse
import datetime as dt
import hashlib
import json
import shutil
from run_small128_queue import run, LAB, HERE, CACHE, EXES

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()

if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=int,choices=(50,1000),required=True)
    p.add_argument('--scale',choices=('0.01','0.1','1'),required=True)
    p.add_argument('--execute',action='store_true')
    a=p.parse_args()
    if not a.execute:
        raise SystemExit('Explicit --execute required')
    source=LAB/f'target/research-preview/preview64-eight-{a.source:03d}-a.gtop'
    expected={50:'54d354a65929de2427e7a6c83e2ce9d60711c28fd3c4288d087674d748771290',
              1000:'263c608c23f856d0c45efde4f5659dcff98d8b9312a827a18b887fc64574d705'}
    if sha(source)!=expected[a.source]:
        raise SystemExit('Frozen preview source changed')
    deadline=dt.datetime(2026,9,11,3,3,27,tzinfo=dt.timezone.utc)
    if (deadline-dt.datetime.now(dt.timezone.utc)).total_seconds()<1900:
        raise SystemExit('Insufficient window for bounded1800s warmstart and cleanup')
    if shutil.disk_usage(LAB).free<source.stat().st_size*7:
        raise SystemExit('Insufficient checkpoint and staging reserve')
    name=f'warmstart-large64-{a.source}-scale-{a.scale.replace(".","p")}-a'
    out=LAB/'target/research-preview'/name
    if out.exists():
        raise SystemExit('Output already exists')
    protocol={'source':str(source),'source_sha256':expected[a.source],
              'source_iterations':a.source,'scale':a.scale,'output':str(out),
              'binary':EXES['preflop_preview_warmstart_gpu'],
              'binary_build_source':'479c065d3f35043107cd925ba918cec1b51c8f99',
              'binary_build_log':'raw/solver-tests-build-h.log',
              'cache_sha256':sha(CACHE),'full_checkpoints':[2,10,30,50,100],
              'scope':'Development; original source solve time excluded from new-stage timing; local quality not inferred from gap'}
    with (HERE/'proposals/continuation-ensemble'/f'{name}-inputs.json').open('x') as f:
        json.dump(protocol,f,indent=2)
    run(name,'preflop_preview_warmstart_gpu',[source,CACHE,out,23000,a.scale],1800)
