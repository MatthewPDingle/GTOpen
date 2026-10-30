"""Timing-only inspection of the first 16 committed evaluation batches.

No policy values, payoff contrasts or partial significance results are emitted.
No GPU work or modifications to the running evaluation.
"""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import lzma
from pathlib import Path
import statistics
import struct
import time
import psutil
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import sha,save
from owned_columnar_evaluation_archive_v1 import MAX_PACKED,MAX_RAW,MAX_HEADER,MAGIC

PREFIX='weighted-evaluation-stage-timing-v1'
STORE=Path('S:/GTOpen-research/weighted-complete-evaluation-study-v1')


def inspect(item):
    name,route=item; folder=STORE/route['attempt']
    manifest_path=folder/(name+'.manifest.json'); packed_path=folder/(name+'.xz')
    assert sha(manifest_path)==route['manifest_sha256']; manifest=read(manifest_path)
    assert manifest['codec']=='xz-columnar-crossed-v1'
    assert packed_path.stat().st_size==manifest['packed_bytes']<=MAX_PACKED
    packed=packed_path.read_bytes(); assert hashlib.sha256(packed).hexdigest()==manifest['packed_sha256']
    decoder=lzma.LZMADecompressor(format=lzma.FORMAT_XZ,memlimit=128*1024**2)
    raw=decoder.decompress(packed,max_length=MAX_RAW+MAX_HEADER+17)
    assert decoder.eof and not decoder.unused_data and raw[:8]==MAGIC
    n=struct.unpack('<Q',raw[8:16])[0]; assert 0<n<=MAX_HEADER
    members=json.loads(raw[16:16+n]); assert members==manifest['members']
    offset=16+n; summary=None
    for member in members:
        if member['name']=='summary.json':
            assert member['codec']=='raw'
            data=raw[offset:offset+member['bytes']]
            assert len(data)==member['raw_bytes']
            assert hashlib.sha256(data).hexdigest()==member['raw_sha256']==route['summary_sha256']
            summary=json.loads(data)
        offset+=member['bytes']
    assert offset==len(raw) and summary is not None
    assert summary['deals']==32 and len(summary['averaging_seconds'])==4
    return dict(name=name,deals=summary['deals'],query_seconds=summary['query_seconds'],
        bank_seconds=sum(summary['averaging_seconds']),bank_seconds_individual=summary['averaging_seconds'],
        native_seconds=summary['native_seconds'],manifest_sha256=route['manifest_sha256'],
        archive_sha256=manifest['packed_sha256'],summary_sha256=route['summary_sha256'])


def main():
    began=time.monotonic(); path=OUT/f'{PREFIX}-result.json'; assert not path.exists()
    assert psutil.virtual_memory().available>24_000_000_000
    status=read(OUT/'weighted-complete-evaluation-study-v1-status.json')
    checkpoint=STORE/status['checkpoint']['file']; assert sha(checkpoint)==status['checkpoint']['sha256']
    document=read(checkpoint); assert document['completed_deals']>=512
    names=[f'test-{i*32:06d}' for i in range(16)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        records=list(pool.map(inspect,[(n,document['routes'][n]) for n in names]))
    means={k:statistics.mean(r[k] for r in records) for k in ('query_seconds','bank_seconds','native_seconds')}
    total=sum(means.values())
    result=dict(scope='First 16 committed 32-deal batches; recorded stage wall times only.',
        checkpoint_path=str(checkpoint),checkpoint_sha256=sha(checkpoint),batches=16,deals=512,
        records=records,mean_seconds_per_batch=means,
        shares_of_instrumented_time={k:v/total for k,v in means.items()},
        seconds=time.monotonic()-began,gpu_used=False,production_modified=False,
        limitation='Bank time includes CPU preparation, transfers and CUDA work. JSON serialization, archive work and coordinator overhead are not fully instrumented. Not a GPU profile or end-to-end speedup claim.')
    assert time.monotonic()-began<120
    save(path,result);print(json.dumps({k:v for k,v in result.items() if k!='records'}),flush=True)


if __name__=='__main__':main()
