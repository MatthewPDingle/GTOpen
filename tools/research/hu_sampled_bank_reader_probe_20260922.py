"""Read-only, frozen-copy comparison of repeated versus cached NPZ reads."""
import hashlib
import json
from pathlib import Path
import shutil
import time
import numpy as np
from loopback_research_validation import idle

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-bank-reader-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
    assert idle()
    source=ROOT/'target/research-sampled/sampled-neural-bank-v1-case0-seed17.npz'
    snapshot=ROOT/'target/research-sampled/sampled-bank-reader-v1-snapshot.npz'
    assert not snapshot.exists()
    before=sha(source);shutil.copyfile(source,snapshot)
    assert sha(snapshot)==before==sha(source),'Live checkpoint changed while copying; do not benchmark a mixed artifact.'
    reg=OUT/(PREFIX+'-registration.json');assert not reg.exists()
    with np.load(snapshot) as stored:
        iterations=int(stored['iterations']);keys=[k for k in stored.files if k.startswith('p')]
    indices=np.linspace(0,iterations-2,12,dtype=int).tolist()
    record=dict(inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__)),str(snapshot.relative_to(ROOT)):sha(snapshot)},
        source_snapshot_iteration=iterations,indices=indices,keys=keys,maximum_seconds=60,
        purpose='Read-only checkpoint verification overhead; identical arrays, no training or GPU activity',production_modified=False)
    save(reg,record);started=time.perf_counter();observations=[]
    with np.load(snapshot) as stored:
        t=time.perf_counter()
        for i in indices:
            observations.append({k:stored[k][i].copy() for k in keys})
            assert time.perf_counter()-started<60 and idle()
        repeated=time.perf_counter()-t
    with np.load(snapshot) as stored:
        t=time.perf_counter();cache={k:stored[k] for k in keys}
        for i,row in zip(indices,observations):
            for k in keys:assert np.array_equal(cache[k][i],row[k])
        cached=time.perf_counter()-t
    assert sha(snapshot)==before
    result=dict(passed=True,registration_sha256=sha(reg),source_snapshot_iteration=iterations,
        repeated_decompression_seconds=repeated,cached_decompression_seconds=cached,
        ratio=repeated/cached,array_slice_comparisons=len(keys)*len(indices),
        cached_payload_bytes=sum(v.nbytes for v in cache.values()),
        scope='Small read-only timing probe; includes idle checks in repeated path, not a model-training speedup claim.',
        production_modified=False)
    save(OUT/(PREFIX+'-result.json'),result);print(json.dumps(result,indent=2))


if __name__=='__main__':main()
