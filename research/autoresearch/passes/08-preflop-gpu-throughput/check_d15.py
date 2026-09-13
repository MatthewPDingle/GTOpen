"""Independent audit of support capacity and cohort-weighted upper bounds."""
import array,collections,gzip,hashlib,itertools,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw';LAB=HERE.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    rec=read(RAW/'d15-zero-bound-v1-exit.json');r=read(RAW/'d15-zero-bound.json')
    assert rec['returncode']==0 and rec['reason'] is None and rec['seconds']<=180
    assert rec['source_diff_sha256']==hashlib.sha256(b'').hexdigest()
    for p,h in rec['inputs'].items():assert sha(Path(p))==h,p
    for p,h in rec['solver_source_files'].items():assert sha(LAB/p)==h,p
    for p,h in r['sources'].items():assert sha(RAW/p)==h,p
    assert r['protocol_sha256']==sha(HERE/'D15_PROTOCOL.md') and r['script_sha256']==sha(HERE/'d15_zero_bound.py')
    capacity=[0]*170
    # Exhaustive six-tile masks, independent of the ceil expression.
    for k in range(1,170):
        capacity[k]=max(6-mask.bit_count() for mask in range(1,64)
            if sum(([32]*5+[9])[i] for i in range(6) if mask&(1<<i))>=k)
    assert capacity[1]==5 and capacity[160]==1 and capacity[161]==capacity[169]==0
    d11=read(RAW/'d11-work-census.json');summary={}
    for fixture,f in r['fixtures'].items():
        old=read(RAW/f'd10-{fixture}-v1.json');manifest=read(RAW/f'd10-{fixture}-v1-witness-manifest.json')
        z=(RAW/f'd10-{fixture}-v1-witness.bin.gz').read_bytes();assert hashlib.sha256(z).hexdigest()==manifest['compressed_sha256']
        b=gzip.decompress(z);assert hashlib.sha256(b).hexdigest()==manifest['witness_sha256']
        words=array.array('I');words.frombytes(b[8:]);assert words.itemsize==4
        if sys.byteorder!='little':words.byteswap()
        np,nt=words[:2];pos=2;avg=[]
        for mode in (0,1):
            for seat in range(np):
                m,p,n=words[pos:pos+3];pos+=3;assert (m,p)==(mode,seat)
                ids=words[pos:pos+n];pos+=n
                if mode:avg.append(set(ids))
                for _ in range(nt):pos+=1+words[pos]
        assert pos==len(words)
        membership=collections.defaultdict(int)
        for group in f['cohorts']:
            for identity in set().union(*(avg[p] for p in group)):membership[identity]+=1
        weights=collections.Counter(membership.values())
        assert {int(k):v for k,v in f['check_identity_multiplicity_histogram'].items()}==weights
        for mode,label in [(0,'learning'),(1,'check')]:
            v=f['modes'][label];hist=[sum(x['unique_support_histogram'][k] for x in old['rows'] if x['mode']==mode) for k in range(170)]
            assert hist==v['support_histogram'] and hist[0]==0
            values=collections.Counter()
            for k,count in enumerate(hist):values[capacity[k]]+=count
            if mode==0:
                upper=sum(k*n for k,n in values.items());rows=sum(hist)
            else:
                # Greedy histogram transport pairs greatest allowances/weights;
                # independent of expanded arrays and the census's layer formula.
                available=dict(values);upper=0
                for weight,count in sorted(weights.items(),reverse=True):
                    for allowance in sorted(available,reverse=True):
                        n=min(count,available[allowance]);upper+=n*weight*allowance
                        count-=n;available[allowance]-=n
                    assert count==0
                assert sum(available.values())==0
                rows=sum(k*n for k,n in weights.items())
            assert rows==v['distinct_cdf_rows']==d11['fixtures'][fixture]['modes'][label]['distinct_distribution_rows']
            assert upper*1024==v['empty_tile_upper_bound'] and rows*6144==v['all_tile_scans']
            assert v['empty_fraction_upper_bound']==upper/(rows*6)
        summary[fixture]={label:dict(rows=v['distinct_cdf_rows'],empty_fraction_upper_bound=v['empty_fraction_upper_bound'],
              positive_hand_counts={str(k):n for k,n in enumerate(v['support_histogram']) if n}) for label,v in f['modes'].items()}
    large=r['fixtures']['large']['modes'];assert large['check']['support_histogram'][:169]==[0]*169
    assert large['check']['empty_tile_upper_bound']==0 and not r['admit_actual_inventory']
    out=dict(verified=True,admitted=False,retained=False,
        status='Both-mode zero-scan proposal rejected: dense accuracy-check ranges',
        bounds={f:{m:v['empty_fraction_upper_bound'] for m,v in x['modes'].items()} for f,x in r['fixtures'].items()},
        large_check_every_observed_distribution_has_169_positive_hands=True,
        large_check_global_distinct_identities=large['check']['support_histogram'][169],
        independent_capacity_and_cohort_assignment_audit=True,
        census_sha256=sha(RAW/'d15-zero-bound.json'),protocol_sha256=r['protocol_sha256'],
        next='Learning-only dispatch remains a separate unqualified possibility; actual sampled empty-tile counts are unknown.',
        scope='Immutable distinct-row support bound. Not a speed measurement or permission to truncate tiny positive probabilities.')
    target=RAW/'d15-verified.json'
    if target.exists():assert read(target)==out
    else:target.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
