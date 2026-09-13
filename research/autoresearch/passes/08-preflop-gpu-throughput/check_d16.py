"""Independent capacity-mask proof and preserved per-seat support audit."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw';LAB=HERE.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    run=read(RAW/'d16-learning-bound-v1-exit.json');r=read(RAW/'d16-learning-bound.json')
    assert run['returncode']==0 and run['reason'] is None and run['seconds']<=180
    assert run['source_diff_sha256']==hashlib.sha256(b'').hexdigest()
    for p,h in run['inputs'].items():assert sha(Path(p))==h
    for p,h in run['solver_source_files'].items():assert sha(LAB/p)==h
    for p,h in r['sources'].items():assert sha(RAW/p)==h
    assert r['protocol_sha256']==sha(HERE/'D16_PROTOCOL.md')
    assert r['script_sha256']==sha(HERE/'d16_learning_bound.py')
    sizes=[32]*5+[9];minimum={};maximum={}
    for k in range(1,170):
        feasible=[6-mask.bit_count() for mask in range(64)
            if mask.bit_count()<=k<=sum(sizes[i] for i in range(6) if mask&(1<<i))]
        minimum[k]=min(feasible);maximum[k]=max(feasible)
    assert minimum[1]==5 and minimum[6]==0 and maximum[169]==0
    bounds={}
    for name,f in r['fixtures'].items():
        old=read(RAW/f'd10-{name}-v1.json');total=lo=hi=0;hist=[0]*170
        for row,seat in zip([x for x in old['rows'] if x['mode']==0],f['seats']):
            h=row['unique_support_histogram'];assert not h[0]
            n=sum(h);lower=sum(minimum[k]*h[k] for k in range(1,170))
            upper=sum(maximum[k]*h[k] for k in range(1,170))
            assert seat==dict(seat=row['player'],distinct_rows=n,
                guaranteed_empty_tiles_per_sample=lower,guaranteed_empty_fraction=lower/(6*n))
            assert n==row['unique_distributions'];total+=n;lo+=lower;hi+=upper
            hist=[x+y for x,y in zip(hist,h)]
        assert len(f['seats'])==old['players'] and hist==f['support_histogram']
        assert total==f['distinct_rows'] and f['total_tile_scans']==total*6144
        assert lo*1024==f['guaranteed_empty_tile_scans'] and hi*1024==f['optimistic_empty_tile_scans']
        assert f['guaranteed_empty_fraction']==lo/(6*total)
        assert f['optimistic_empty_fraction']==hi/(6*total)
        bounds[name]=dict(lower=lo/(6*total),upper=hi/(6*total))
    admitted=bounds['large']['lower']>=.20
    assert admitted==r['admit_gpu_prototype']
    out=dict(verified=True,admitted=admitted,retained=False,
        status='Learning-only empty scan prototype admitted' if admitted else 'Learning-only lower bound gate failed',
        bounds=bounds,capacity_cases=169,census_sha256=sha(RAW/'d16-learning-bound.json'),
        protocol_sha256=r['protocol_sha256'],
        scope='Learning-only structural lower bound. Loads, votes, carry and stores remain; no measured speedup.')
    target=RAW/'d16-verified.json'
    if target.exists():assert read(target)==out
    else:target.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
