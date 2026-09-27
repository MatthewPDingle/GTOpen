"""CPU-only fixed-input snapshot equivalence, isolation and timing control."""
import copy
import hashlib
import json
from pathlib import Path
import statistics
import time
import numpy as np
from native_query_snapshot_v1 import snapshot
from shared_visible_query_arrays_v1 import prepare
from owned_columnar_evaluation_archive_v1 import restore
from sampled_physical_root_evaluation_v1 import sha,save
from later_average_support_v1 import OUT,read

PREFIX='native-query-snapshot-control-v1'
STORE=Path('S:/GTOpen-research/weighted-complete-evaluation-study-v1')
ARRAYS=('features','actors','legal','prior','action','valid')


def main():
    began=time.monotonic();rp=OUT/f'{PREFIX}-registration.json';assert not rp.exists()
    status=read(OUT/'weighted-complete-evaluation-study-v1-status.json')
    cp=STORE/status['checkpoint']['file'];assert sha(cp)==status['checkpoint']['sha256']
    document=read(cp); names=[f'test-{i*32:06d}' for i in range(4)]
    paths=[cp,Path(__file__).resolve(),Path(__file__).with_name('native_query_snapshot_v1.py'),
           Path(__file__).with_name('shared_visible_query_arrays_v1.py'),
           Path(__file__).with_name('sampled_visible_features_bulk_v1.py')]
    for name in names:
        route=document['routes'][name]; folder=STORE/route['attempt']
        paths.extend((folder/(name+'.manifest.json'),folder/(name+'.xz')))
    inputs={str(p):sha(p) for p in paths}
    save(rp,dict(inputs=inputs,batches=names,repeats=3,maximum_seconds=180,
        method='Alternating execution order; exact JSON bytes and every derived array versus deepcopy; caller-mutation isolation.',
        gpu_used=False,production_modified=False))
    rejected=0
    for bad in ([],{'a':float('nan')},{'a':float('inf')},{1:'changed-key'},{'a':(1,2)}, {'a':object()}):
        try:snapshot(bad)
        except (ValueError,TypeError):rejected+=1
        else:raise AssertionError('Unsupported document accepted')
    records=[]
    for name in names:
        route=document['routes'][name];folder=STORE/route['attempt']
        mp=folder/(name+'.manifest.json');assert sha(mp)==route['manifest_sha256']
        members=restore(folder/(name+'.xz'),read(mp),guard=lambda:None)
        source=members['queries.json'];q=json.loads(source)
        a=copy.deepcopy(q);b=snapshot(q)
        assert json.dumps(a,allow_nan=False)==json.dumps(b,allow_nan=False)
        aa,bb=prepare(a),prepare(b)
        assert all(np.array_equal(getattr(aa,k),getattr(bb,k)) for k in ARRAYS)
        old=[[],[]];whole=[[],[]]
        for repeat in range(3):
            for which in ([0,1] if repeat%2==0 else [1,0]):
                fn=copy.deepcopy if which==0 else snapshot
                t=time.perf_counter();clone=fn(q);cloned=time.perf_counter();arr=prepare(clone)
                whole[which].append(time.perf_counter()-t);old[which].append(cloned-t)
                assert all(np.array_equal(getattr(aa,k),getattr(arr,k)) for k in ARRAYS)
        # Independently mutate caller and snapshot deep inside nested structures.
        original_bytes=json.dumps(q)
        b['observations'][0]['active_features'][0]=-999
        assert json.dumps(q)==original_bytes
        before=json.dumps(a);q['observations'][0]['active_features'][0]=-998
        assert json.dumps(a)==before
        records.append(dict(name=name,query_sha256=hashlib.sha256(source).hexdigest(),rows=len(a['observations']),
            copy_seconds=old,copy_and_preparation_seconds=whole,
            median_copy_seconds=[statistics.median(x) for x in old],
            median_copy_and_preparation_seconds=[statistics.median(x) for x in whole]))
    for p,h in inputs.items():assert sha(p)==h,p
    assert time.monotonic()-began<180
    reference=sum(r['median_copy_and_preparation_seconds'][0] for r in records)
    candidate=sum(r['median_copy_and_preparation_seconds'][1] for r in records)
    result=dict(passed=True,registration_sha256=sha(rp),records=records,rejected_invalid_documents=rejected,
        exact_arrays=True,caller_isolation=True,aggregate_preparation_ratio=candidate/reference,
        seconds=time.monotonic()-began,gpu_used=False,production_modified=False,
        limitation='CPU snapshot/preparation only, concurrent with live evaluation. Not an end-to-end speedup; CUDA/evaluation integration remains unqualified.')
    save(OUT/f'{PREFIX}-result.json',result);print(json.dumps(result),flush=True)


if __name__=='__main__':main()
