"""Read-only large-dictionary compression probe on fixed completed training data."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import hashlib
import json
import lzma
from pathlib import Path
import struct
import time
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read
from reboot_research_idle_v1 import idle
from owned_research_archive_v1 import unpack,encoded,MAGIC,MAX_RAW,MAX_HEADER


def main():
    start=time.monotonic()
    def guard():
        assert idle() and time.monotonic()-start<240
        assert psutil.virtual_memory().available>=20_000_000_000
    guard();prefix='training-dictionary-probe-v1'
    rp,dest=[OUT/f'{prefix}-{s}.json' for s in ('registration','result')]
    assert not rp.exists() and not dest.exists()
    sp=OUT/'training-transport-timing-probe-v1-registration.json'
    sr=OUT/'training-transport-timing-probe-v1-result.json'
    assert read(sr)['passed'] and read(sr)['registration_sha256']==sha(sp)
    inputs=dict(read(sp)['inputs'])
    for p in [sp,sr,Path(__file__).resolve()]:inputs[str(p)]=sha(p)
    for p,h in inputs.items():assert sha(p)==h,p
    save(rp,dict(inputs=inputs,iterations=[8,24,48],chunk=0,presets=[6,9],
        maximum_seconds=240,decoder_memory_limit=128*1024**2,gpu_used=False,
        scope='In-memory only. Do not replace original archives or completion markers. Exact original raw bundle reconstruction required.'))
    try:
        case=Path('S:/GTOpen-research/showdown-matched-training-v1/9266201-baseline')
        rows=[]
        for i in [8,24,48]:
            guard();path=case/f'iteration-{i:04d}-batch-00.xz';manifest=read(path.with_suffix('.xz.json'))
            members=unpack(path,manifest,guard=guard);header=encoded(manifest['members'])
            raw=MAGIC+struct.pack('<Q',len(header))+header+b''.join(members[m['name']] for m in manifest['members'])
            for preset in [6,9]:
                before=time.perf_counter();packed=lzma.compress(raw,preset=preset);seconds=time.perf_counter()-before
                decoder=lzma.LZMADecompressor(format=lzma.FORMAT_XZ,memlimit=128*1024**2)
                restored=decoder.decompress(packed,max_length=MAX_RAW+MAX_HEADER+17)
                assert decoder.eof and not decoder.unused_data and restored==raw
                if preset==6:assert packed==path.read_bytes()
                row=dict(iteration=i,preset=preset,packed_bytes=len(packed),compress_seconds=seconds,
                    raw_bundle_sha256=hashlib.sha256(raw).hexdigest(),packed_sha256=hashlib.sha256(packed).hexdigest(),
                    exact_raw_bundle_restored=True,decoder_within_existing_memory_bound=True)
                rows.append(row);print(json.dumps(row),flush=True)
            del raw,members,packed,restored
        totals={str(k):sum(r['packed_bytes'] for r in rows if r['preset']==k) for k in [6,9]}
        for p,h in inputs.items():guard();assert sha(p)==h,p
        result=dict(passed=True,registration_sha256=sha(rp),rows=rows,packed_byte_totals=totals,
            size_ratio=totals['9']/totals['6'],seconds=time.monotonic()-start,gpu_used=False,
            source_files_modified=False,production_modified=False,fresh_deals_sampled=0,
            limitations=['Three fixed baseline batches; not a guaranteed full-study ratio.',
                'New compressed container bytes differ. Existing archive hashes and readers must not be silently changed.',
                'This probe does not qualify retirement, a new archive reader, or any poker improvement.'])
        save(dest,result);print(json.dumps({k:v for k,v in result.items() if k!='rows'}))
    except BaseException as exc:
        save(dest,dict(passed=False,error=repr(exc),registration_sha256=sha(rp)))
        raise


if __name__=='__main__':main()
