"""Independent D10 witness reconstruction with NumPy set unions."""
import gzip,hashlib,json,struct,subprocess
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw';LAB=HERE.parents[3];NONE=2**32-1
SIZES=[128,512,2048]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(b):return hashlib.sha256(b).hexdigest()
def counts(a,size):
    out=[]
    for start in range(0,a.shape[0],size):
        ids=np.unique(a[start:start+size]);out.append(int(len(ids)-(len(ids)>0 and ids[-1]==NONE)))
    return out

def main():
    build=read(RAW/'d10-invariants-v2-exit.json');assert build['returncode']==0 and build['reason'] is None
    assert '1 passed; 0 failed; 1 ignored' in (RAW/'d10-invariants-v2.log').read_text(encoding='utf-8')
    failed=read(RAW/'d10-invariants-v1-exit.json');assert failed['returncode']==101
    assert 'no rules expected' in (RAW/'d10-invariants-v1.log').read_text(encoding='utf-8')
    for v,record in [('v1',failed),('v2',build)]:
        for name,entry in read(HERE/f'artifacts/d10-{v}-source-map.json').items():
            assert sha((HERE/entry['archive']).read_bytes())==entry['sha256']==record['solver_source_files'][name.replace('/','\\')]
    result={}
    for fixture in ['small','large']:
        name=f'd10-{fixture}-v1';record=read(RAW/f'{name}-exit.json');m=read(RAW/f'{name}-witness-manifest.json')
        assert record['returncode']==0 and record['reason'] is None and record['solver_source_files']==build['solver_source_files']
        assert record['exe_sha256']==m['executable_sha256']
        for path,digest in record['inputs'].items():assert sha(Path(path).read_bytes())==digest
        assert m['save_sha256'] in record['inputs'].values()
        data=(RAW/f'{name}-witness.bin.gz').read_bytes();assert sha(data)==m['compressed_sha256']
        data=gzip.decompress(data);assert sha(data)==m['witness_sha256'] and len(data)==m['witness_bytes']
        outpath=RAW/f'{name}.json';assert sha(outpath.read_bytes())==m['output_sha256'];out=read(outpath)
        assert out['arenas_unchanged'] and out['read_only'] and out['batch']==32
        assert data[:8]==b'D10V1\0\0\0';np_,nt=struct.unpack_from('<2I',data,8);at=16
        assert out['players']==np_ and len(out['rows'])==2*np_
        layout=read(RAW/f'c14-{fixture}-layout-v1.json')
        assert (layout['input'],layout['players'],layout['nodes'],layout['iteration'])==(out['input'],np_,out['nodes'],out['iteration'])
        assert nt==read(RAW/f'd07-{fixture}-v1.json')['terminals']
        metric={size:{'current':{'baseline_rows':0,'tile_rows':0,'max_rows':0,'producer_launches':0,'consumer_launches':0},'average':{}} for size in SIZES}
        avg=[];avg_baseline=[]
        for mode in [0,1]:
            for seat in range(np_):
                m_,p_,n=struct.unpack_from('<3I',data,at);at+=12;assert (m_,p_)==(mode,seat)
                baseline=np.frombuffer(data,dtype='<u4',count=n,offset=at).copy();at+=4*n
                assert len(np.unique(baseline))==n and (n==0 or baseline[-1]<NONE)
                a=np.full((nt,np_-1),NONE,dtype=np.uint32);positive=0;weighted=0;keys=set()
                for t in range(nt):
                    k=struct.unpack_from('<I',data,at)[0];at+=4;assert k==0 or 2<=k<np_
                    if k:
                        key=struct.unpack_from('<'+'I'*k,data,at);at+=4*k
                        a[t,:k]=key;positive+=1;weighted+=k;keys.add(key)
                r=out['rows'][mode*np_+seat]
                assert (r['mode'],r['player'],r['unique_distributions'],r['positive_terminals'],r['weighted_terminals'],r['unique_equity_keys'],r['unique_weighted_terminals'])==(mode,seat,n,positive,weighted,len(keys),sum(map(len,keys)))
                allids=np.unique(a);allids=allids[allids!=NONE];assert np.isin(allids,baseline).all()
                if mode==0:assert np.array_equal(allids,baseline)
                for tile in r['tiles']:
                    size=tile['size'];c=counts(a,size);assert c==tile['counts']
                    if mode==0:
                        item=metric[size]['current'];item['baseline_rows']+=n;item['tile_rows']+=sum(c);item['max_rows']=max(item['max_rows'],max(c,default=0))
                        item['producer_launches']+=32*sum(x>0 for x in c);item['consumer_launches']+=32*sum(x>0 for x in c)
                if mode==1:avg.append(a);avg_baseline.append(baseline)
                print(json.dumps({'verified':fixture,'mode':mode,'seat':seat,'baseline_rows':n}),flush=True)
        assert at==len(data)
        groups=layout['plan']['groups'];assert sorted(sum(groups,[]))==list(range(np_))
        for size in SIZES:
            item={'baseline_rows':0,'tile_rows':0,'max_rows':0,'producer_launches':0,'consumer_launches':0}
            for group in groups:
                item['baseline_rows']+=len(np.unique(np.concatenate([avg_baseline[p] for p in group])))
                for start in range(0,nt,size):
                    ids=np.unique(np.concatenate([avg[p][start:start+size].ravel() for p in group]));n=int(len(ids)-(len(ids)>0 and ids[-1]==NONE))
                    item['tile_rows']+=n;item['max_rows']=max(item['max_rows'],n);item['producer_launches']+=32*(n>0)
                    item['consumer_launches']+=32*sum(bool(np.any(avg[p][start:start+size]!=NONE)) for p in group)
            metric[size]['average']=item
            for item in metric[size].values():
                item['construction_ratio']=item['tile_rows']/item['baseline_rows'];item['max_cdf_bytes']=item['max_rows']*32*170*4
        result[fixture]={'tiles':metric,'cohorts':groups,'terminals':nt,'iteration':out['iteration'],'independent_witness_reproduction':True}
        del avg,data
        print(json.dumps({'fixture':fixture,'metrics':metric}),flush=True)
    admitted=[]
    for size in SIZES:
        if all(result[f]['tiles'][size][mode]['construction_ratio']<=(1.25 if f=='large' else 1.30) and result[f]['tiles'][size][mode]['max_cdf_bytes']<=4*1024*1024 for f in ['small','large'] for mode in ['current','average']):admitted.append(size)
    payload={'admitted':bool(admitted),'tile_sizes_admitted':admitted,'fixtures':result,'status':'Admitted for a separately qualified GPU prototype' if admitted else 'Rejected by registered feasibility gate','scope':'Exact table-count and storage inventory only; no measured cache hits, runtime gain or convergence improvement. No learning or production mutation.'}
    dest=RAW/'d10-verified.json'
    if dest.exists():assert read(dest)==json.loads(json.dumps(payload))
    else:dest.write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'admitted':admitted,'status':payload['status']}),flush=True)
if __name__=='__main__':main()
