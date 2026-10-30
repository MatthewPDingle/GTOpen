"""In-memory compression throughput probe on the same fixed completed batches.

All three source bundles and compression settings stay identical. Thread counts
change only concurrent compression, never poker data or model arithmetic.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import concurrent.futures
import json
import lzma
from pathlib import Path
import struct
import time
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read
from reboot_research_idle_v1 import idle
from owned_research_archive_v1 import unpack,encoded,MAGIC


def main():
    start=time.monotonic()
    def guard():
        assert idle() and time.monotonic()-start<300
        assert psutil.virtual_memory().available>=20_000_000_000
    guard();prefix='training-parallel-xz-probe-v1'
    rp,dest=[OUT/f'{prefix}-{s}.json' for s in ('registration','result')]
    assert not rp.exists() and not dest.exists()
    source_path=OUT/'training-transport-timing-probe-v1-registration.json'
    source_result=OUT/'training-transport-timing-probe-v1-result.json'
    source=read(source_path)
    assert read(source_result)['passed'] and read(source_result)['registration_sha256']==sha(source_path)
    inputs=dict(source['inputs'])
    for p in [source_path,source_result,Path(__file__).resolve()]:inputs[str(p)]=sha(p)
    for p,h in inputs.items():assert sha(p)==h,p
    # Fixed order contains two sequential and two parallel passes to expose
    # simple warm-cache/order effects; no selection of the fastest pass.
    order=[1,3,3,1]
    save(rp,dict(inputs=inputs,worker_counts=order,iterations=[8,24,48],preset=6,
        maximum_seconds=300,gpu_used=False,scope='All passes use identical three bundles; report every timing and exact original-archive equality.'))
    try:
        case=Path('S:/GTOpen-research/showdown-matched-training-v1/9266201-baseline')
        bundles=[];expected=[]
        for i in [8,24,48]:
            path=case/f'iteration-{i:04d}-batch-00.xz';m=read(path.with_suffix('.xz.json'))
            parts=unpack(path,m,guard=guard);h=encoded(m['members'])
            bundles.append(MAGIC+struct.pack('<Q',len(h))+h+b''.join(parts[x['name']] for x in m['members']))
            expected.append(path.read_bytes())
        del parts
        def compress(raw):return lzma.compress(raw,preset=6)
        rows=[]
        for workers in order:
            guard();before=time.perf_counter()
            if workers==1:actual=[compress(b) for b in bundles]
            else:
                with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
                    actual=list(pool.map(compress,bundles))
            seconds=time.perf_counter()-before
            assert actual==expected
            rows.append(dict(workers=workers,seconds=seconds,all_original_archives_byte_identical=True))
            print(json.dumps(rows[-1]),flush=True)
            del actual
        means={str(k):sum(r['seconds'] for r in rows if r['workers']==k)/2 for k in (1,3)}
        for p,h in inputs.items():guard();assert sha(p)==h,p
        result=dict(passed=True,registration_sha256=sha(rp),passes=rows,mean_seconds=means,
            measured_speedup=means['1']/means['3'],seconds=time.monotonic()-start,
            gpu_used=False,fresh_deals_sampled=0,source_files_modified=False,production_modified=False,
            limitations=['Small in-memory compression probe with live training and audit competing for host resources.',
                'Not an end-to-end training benchmark; disk I/O, manifests, guards and retirement are excluded.',
                'No change to current fixed experiment; parallel archive integration needs separate qualification.'])
        save(dest,result);print(json.dumps(result))
    except BaseException as exc:
        save(dest,dict(passed=False,error=repr(exc),registration_sha256=sha(rp)))
        raise


if __name__=='__main__':main()
