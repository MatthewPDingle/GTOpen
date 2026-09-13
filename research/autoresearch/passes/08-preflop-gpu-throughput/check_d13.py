"""Independent exact sampled-rank inventory and optimistic work screen."""
import gzip,hashlib,itertools,json,re,statistics,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw';LAB=HERE.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    rec=read(RAW/'d13-rank-export-v1-exit.json');assert rec['returncode']==0 and rec['reason'] is None and rec['seconds']<=300
    log=(RAW/'d13-rank-export-v1.log').read_text(encoding='utf-8');assert '1 passed; 0 failed; 0 ignored' in log
    for p,h in rec['inputs'].items():assert sha(Path(p).read_bytes())==h,p
    mapping={str(Path(k)):v for k,v in read(HERE/'artifacts/d13-v1-source-map.json').items()}
    for p,h in rec['solver_source_files'].items():
        if p in mapping:assert sha((HERE/mapping[p]['archive']).read_bytes())==mapping[p]['sha256']==h,p
        else:assert sha(subprocess.check_output(['git','show',rec['source_commit']+':'+Path(p).as_posix()],cwd=LAB))==h,p
    m=read(RAW/'d13-ranks-manifest.json');compressed=(RAW/'d13-fixed-ranks-v1.json.gz').read_bytes();assert sha(compressed)==m['compressed_sha256']
    data=gzip.decompress(compressed);assert sha(data)==m['table_sha256'] and len(data)==m['table_bytes']
    exe=LAB/'target/d13-rank-frozen.exe';assert sha(exe.read_bytes())==m['executable_sha256']
    t=json.loads(data);assert (t['samples'],t['classes'],t['model'])==(1024,169,'coupled_deck_v1')
    for key in ['order','lower','upper']:assert len(t[key])==1024*169
    assert len(t['rows'])==1024
    global_counts=[];warp_counts=[];sizes={}
    for s,row in enumerate(t['rows']):
        assert row['sample']==s;start=s*169;order=t['order'][start:start+169];assert sorted(order)==list(range(169))
        keys=list(zip(t['lower'][start:start+169],t['upper'][start:start+169]))
        groups={}
        for h,key in enumerate(keys):groups.setdefault(key,[]).append(h)
        spans=sorted(groups);assert spans[0][0]==0 and spans[-1][1]==169
        assert all(a[1]==b[0] for a,b in zip(spans,spans[1:]))
        for (lo,hi),hands in groups.items():
            assert 0<=lo<hi<=169 and sorted(order[lo:hi])==sorted(hands)
            sizes[str(hi-lo)]=sizes.get(str(hi-lo),0)+1
        a=len(set(keys));b=sum(len(set(keys[i:i+32])) for i in range(0,169,32))
        # Independent run-length counting after lexicographic sorting.
        aa=sum(1 for _ in itertools.groupby(sorted(keys)))
        bb=sum(sum(1 for _ in itertools.groupby(sorted(keys[i:i+32]))) for i in range(0,169,32))
        assert a==aa==row['global_groups'] and b==bb==row['warp_groups']
        global_counts.append(a);warp_counts.append(b)
    census=read(RAW/'d11-work-census.json');schedules={}
    for label,counts,threshold in [('compact_groups',global_counts,.30),('original_warps',warp_counts,.20)]:
        groups=sum(counts);full=1024*169;fixtures={}
        for fixture,f in census['fixtures'].items():
            modes={}
            for mode,v in f['modes'].items():
                hist=v['terminal_opponent_histogram'];before=0;after=0
                for o,n in enumerate(hist[2:],2):
                    q=(o+2)//2;shared=o+3*q*o;remaining=2*q
                    before+=n*full*(shared+remaining);after+=n*(groups*shared+full*remaining)
                assert before==v['logical_fp_operations']
                modes[mode]=dict(source_operations_before=before,optimistic_source_operations_after=after,source_arithmetic_reduction=1-after/before)
            fixtures[fixture]=modes
        schedules[label]=dict(groups=groups,min_groups=min(counts),median_groups=statistics.median(counts),max_groups=max(counts),
            logical_gather_reduction=1-groups/full,gate=threshold,fixtures=fixtures,
            admitted=all(v['source_arithmetic_reduction']>=threshold for v in fixtures['large'].values()))
    admitted=[k for k,v in schedules.items() if v['admitted']]
    result=dict(verified=True,admitted=bool(admitted),admitted_schedules=admitted,schedules=schedules,rank_group_size_histogram=sizes,
        independent_counts_match=True,source_input_executable_hashes_verified=True,manifest_sha256=sha((RAW/'d13-ranks-manifest.json').read_bytes()),
        census_sha256=sha((RAW/'d11-work-census.json').read_bytes()),
        status='Static rank reuse admits separate prototype' if admitted else 'Rejected by registered arithmetic-reduction gates',
        scope='Optimistic static source work, not executed warp instructions, runtime, DRAM traffic or convergence. CDF production unchanged; coordination costs excluded.')
    dest=RAW/'d13-verified.json'
    if dest.exists():assert read(dest)==result
    else:dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
