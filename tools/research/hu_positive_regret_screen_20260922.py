"""Size-only screen of post-projection CFR+ positive-regret storage. Not yet GPU-qualified."""
import hashlib
import json
from pathlib import Path
import struct
import sys
import time
import numpy as np
import psutil

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
sys.path.insert(0,'S:/GTOpen-research/python-codecs-20260922')
import zstandard as zstd


def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    review_path=OUT/'wide-maturity-v1-review.json'
    review=json.loads(review_path.read_text());assert review['passed'] is True
    registration=OUT/'wide-positive-regret-screen-v1-registration.json'
    result_path=OUT/'wide-positive-regret-screen-v1-result.json'
    assert not registration.exists() and not result_path.exists()
    assert psutil.virtual_memory().available>20*2**30
    record={'input_review_sha256':sha(review_path),'sources':review['snapshots'],'script_sha256':sha(Path(__file__)),
        'created_at_unix':time.time(),'zstandard_version':zstd.__version__,'codec_levels':[3],
        'chunk_bytes':1024*1024,'framing_allowance_per_chunk_bytes':64,'source_header_bytes':72,
        'selection':'All four registered snapshots, all arrays, all payload bytes; no ratio-based selection',
        'transform':'After complete symmetry projection, replace only negative regrets in arrays 0 and 1 with positive zero. Other bytes unchanged. Measure all four milestones. No modified checkpoint written or imported.',
        'base_script_sha256':sha(ROOT/'tools/research/hu_wide_maturity_compression_20260922.py'),
        'cfr_source_sha256':sha(ROOT/'crates/solver/src/cfr.rs'),
        'kernel_source_sha256':sha(ROOT/'crates/solver/src/gpu/kernels.cu'),
        'projection_source_sha256':sha(ROOT/'crates/solver/src/gpu/continuation_projection.cu'),
        'compression_of_transformed_bytes_is_lossless':True,'original_state_is_byte_exact':False,'semantic_equivalence_gpu_validated':False,'compressed_files_written':False,
        'limits':'Size screen only. Original signed state cannot be recovered. Candidate applies only to CFR+ between completed projected sweeps. Does not qualify DCFR, predictive CFR, clipping before projection, cold recovery or whole-forest capacity.'}
    with registration.open('x') as f:json.dump(record,f,indent=2)
    # Narrow algebra controls, not a substitute for resumed GPU trajectory checks.
    rng=np.random.default_rng(20260922)
    regrets=rng.uniform(-1e5,1e5,size=100000).astype('f4')
    delta=rng.uniform(-1e4,1e4,size=100000).astype('f4')
    clipped=regrets.copy();clipped[clipped<0]=0.
    left=regrets*np.where(regrets>0,np.float32(1),np.float32(0))+delta
    right=clipped+delta
    assert np.array_equal(left,right)
    assert np.array_equal(np.maximum(regrets,0),np.maximum(clipped,0))
    assert (-2*.5+2)!=(0*.5+2), 'DCFR must be excluded'
    assert max(np.mean([.2,-.4]),0)!=np.mean([.2,0]), 'pre-projection clipping must be excluded'
    encoders={level:zstd.ZstdCompressor(level=level,write_checksum=True) for level in [3]}
    decoder=zstd.ZstdDecompressor()
    rows=[];began=time.monotonic()
    for name,expected in record['sources'].items():
        path=Path(name);assert sha(path)==expected
        metrics={level:{'raw_bytes':0,'encoded_bytes':0,'chunks':0,'encode_seconds':0.,'decode_seconds':0.} for level in encoders}
        array_stats=[];digest=hashlib.sha256(); transformed_digest=hashlib.sha256()
        with path.open('rb') as f:
            header=f.read(72);digest.update(header);h=struct.unpack('<9Q',header)
            assert h[0]==0x47544f5353440001
            assert path.stat().st_size==72+4*sum(h[4:8])
            for k,length in enumerate(h[4:8]):
                remaining=length*4;zeros=0;negatives=0;lowest=float('inf');largest=-float('inf');smallest=float('inf')
                while remaining:
                    data=f.read(min(1024*1024,remaining));assert data and len(data)%4==0
                    remaining-=len(data);digest.update(data)
                    values=np.frombuffer(data,dtype='<f4')
                    assert np.isfinite(values).all()
                    if k>=2:assert (values>=0).all()
                    negatives+=int(np.count_nonzero(values<0))
                    lowest=min(lowest,float(values.min()))
                    zeros+=int(np.count_nonzero(values==0))
                    largest=max(largest,float(values.max()))
                    positive=values[values>0]
                    if positive.size:smallest=min(smallest,float(positive.min()))
                    if k<2:
                        changed=values.copy();changed[changed<0]=0.
                        assert np.array_equal(changed[values>=0].view('u4'),values[values>=0].view('u4'))
                        data=changed.tobytes()
                    transformed_digest.update(data)
                    for level,encoder in encoders.items():
                        m=metrics[level];start=time.perf_counter();encoded=encoder.compress(data)
                        m['encode_seconds']+=time.perf_counter()-start
                        start=time.perf_counter();decoded=decoder.decompress(encoded)
                        m['decode_seconds']+=time.perf_counter()-start
                        assert decoded==data
                        m['raw_bytes']+=len(data);m['encoded_bytes']+=len(encoded);m['chunks']+=1
                array_stats.append({'array':k,'float_count':length,'zeros':zeros,'negative':negatives,'minimum':lowest,'maximum':largest,
                    'minimum_positive':None if smallest==float('inf') else smallest})
            assert not f.read(1)
        assert digest.hexdigest()==expected and sha(path)==expected
        for m in metrics.values():
            m['framed_bytes']=m['encoded_bytes']+64*m['chunks']+72
            m['ratio']=m['raw_bytes']/m['framed_bytes']
        row={'path':name,'sha256':expected,'iteration':h[3],'arrays':array_stats,'transformed_payload_sha256':transformed_digest.hexdigest(),'codecs':metrics}
        rows.append(row)
        print('POSITIVE_REGRET_SCREEN',json.dumps({'iteration':h[3],'codecs':metrics}),flush=True)
    assert sha(review_path)==record['input_review_sha256']
    assert sha(Path(__file__))==record['script_sha256']
    for key,name in [('cfr_source_sha256','crates/solver/src/cfr.rs'),
                     ('kernel_source_sha256','crates/solver/src/gpu/kernels.cu'),
                     ('projection_source_sha256','crates/solver/src/gpu/continuation_projection.cu'),
                     ('base_script_sha256','tools/research/hu_wide_maturity_compression_20260922.py')]:
        assert sha(ROOT/name)==record[key]
    result={'scalar_control_samples':100000,'dcfr_and_pre_projection_negative_controls_passed':True,'passed':True,'rows':rows,'registration_sha256':sha(registration),
        'elapsed_seconds':time.monotonic()-began,'production_modified':False,
        'full_forest_admitted':False,'strategic_accuracy_claim':False,'transformed_bytes_roundtrip_exact':True,'original_state_is_byte_exact':False,'semantic_equivalence_gpu_validated':False}
    with result_path.open('x') as f:json.dump(result,f,indent=2)
    print('POSITIVE_REGRET_SCREEN_DONE',json.dumps({'passed':True,'elapsed_seconds':result['elapsed_seconds']}),flush=True)


if __name__=='__main__':main()
