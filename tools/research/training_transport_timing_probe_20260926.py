"""Read-only CPU timing of three fixed, completed training batch archives.

No native poker, neural inference, fresh chance samples, or source-file changes.
Only compact metadata is written; original bytes and recompression stay in RAM.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import hashlib
import json
import lzma
from pathlib import Path
import struct
import time
import psutil
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read
from reboot_research_idle_v1 import idle
from owned_research_archive_v1 import unpack, encoded, MAGIC


def main():
    start=time.monotonic()
    def guard():
        assert idle() and time.monotonic()-start<180
        assert psutil.virtual_memory().available>=20_000_000_000
    guard()
    prefix='training-transport-timing-probe-v1'
    rp,dest=[OUT/f'{prefix}-{s}.json' for s in ('registration','result')]
    assert not rp.exists() and not dest.exists()
    case=Path('S:/GTOpen-research/showdown-matched-training-v1/9266201-baseline')
    selection=[8,24,48]
    inputs={str(Path(__file__).resolve()):sha(Path(__file__)),
        str(ROOT/'tools/research/owned_research_archive_v1.py'):sha(ROOT/'tools/research/owned_research_archive_v1.py')}
    for i in selection:
        marker=case/f'retention-{i:04d}.json';r=read(marker)
        metric=case/f'iteration-{i:04d}/metrics.json'
        assert sha(metric)==r['metrics_sha256']
        archive=case/f'iteration-{i:04d}-batch-00.xz';manifest=archive.with_suffix('.xz.json')
        assert sha(manifest)==r['archives'][0]['manifest_sha256']
        assert sha(archive)==read(manifest)['packed_sha256']
        for p in [marker,metric,archive,manifest]:inputs[str(p)]=sha(p)
    save(rp,dict(inputs=inputs,iterations=selection,chunk=0,maximum_seconds=180,
        gpu_used=False,fresh_deals_sampled=0,
        scope='Observational archive decode, JSON parse/encode, and byte-identical XZ6 recompression in memory. Not a throughput intervention or poker evaluation.'))
    try:
        results=[]
        for i in selection:
            guard();archive=case/f'iteration-{i:04d}-batch-00.xz';manifest=read(archive.with_suffix('.xz.json'))
            before=time.perf_counter();members=unpack(archive,manifest,guard=guard)
            decode=time.perf_counter()-before
            before=time.perf_counter();documents={n:json.loads(b) for n,b in members.items()}
            parse=time.perf_counter()-before
            # This encoding mirrors the Python transport writer, but native
            # JSON formatting differs. Check semantics, never claim all these
            # bytes were the actual Python-produced transport.
            before=time.perf_counter()
            transport={n:(json.dumps(d,separators=(',',':'),allow_nan=False)+'\n').encode()
                       for n,d in documents.items()}
            encode=time.perf_counter()-before
            assert all(json.loads(transport[n])==d for n,d in documents.items())
            before=time.perf_counter()
            header=encoded(manifest['members'])
            original_bundle=MAGIC+struct.pack('<Q',len(header))+header+b''.join(members[m['name']] for m in manifest['members'])
            bundle=time.perf_counter()-before
            before=time.perf_counter();packed=lzma.compress(original_bundle,preset=6)
            compress=time.perf_counter()-before
            assert packed==archive.read_bytes()
            results.append(dict(iteration=i,raw_bytes=sum(map(len,members.values())),packed_bytes=len(packed),
                archive_decode_verify_seconds=decode,json_parse_seconds=parse,
                all_document_python_encode_seconds=encode,bundle_assembly_seconds=bundle,
                xz6_compress_seconds=compress,original_archive_reproduced_exactly=True))
            print(json.dumps(results[-1]),flush=True)
            del members,documents,transport,original_bundle,packed
        for p,h in inputs.items():guard();assert sha(p)==h,p
        keys=[k for k in results[0] if k.endswith('_seconds')]
        means={k:sum(r[k] for r in results)/len(results) for k in keys}
        result=dict(passed=True,registration_sha256=sha(rp),batches=results,mean_batch_seconds=means,
            eight_batch_xz6_seconds_at_probe_rate=8*means['xz6_compress_seconds'],
            seconds=time.monotonic()-start,gpu_used=False,fresh_deals_sampled=0,
            source_files_modified=False,production_modified=False,
            limitations=['Three archived batches, measured during another workload; not a full performance benchmark.',
                'Archive timing excludes disk writes and the separate retirement readback.',
                'JSON encoding of all documents is diagnostic only; native writers handle some in the real pipeline.',
                'Training remains unchanged; these timings do not establish poker strength or an optimized runtime.'])
        save(dest,result);print(json.dumps({k:v for k,v in result.items() if k!='batches'}))
    except BaseException as exc:
        save(dest,dict(passed=False,error=repr(exc),registration_sha256=sha(rp)))
        raise


if __name__=='__main__':main()
