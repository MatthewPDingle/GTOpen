"""Independent static-boundary map, case, source and compiler audit."""
import gzip,hashlib,json,subprocess
from pathlib import Path
from check_d09 import entries
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw';LAB=HERE.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    folder=RAW/'c23-static-v1';rec=read(RAW/'c23-static-v1-exit.json')
    assert rec['returncode']==0 and rec['reason'] is None and rec['seconds']<=300
    assert '1 passed; 0 failed; 0 ignored' in (RAW/'c23-static-v1.log').read_text(encoding='utf-8')
    for p,h in rec['inputs'].items():assert sha(p)==h,p
    mapping={str(Path(k)):v for k,v in read(HERE/'artifacts/c23-v1-source-map.json').items()}
    for p,h in rec['solver_source_files'].items():
        if p in mapping:
            v=mapping[p];assert sha(HERE/v['archive'])==h==v['sha256']
        else:assert hashlib.sha256(subprocess.check_output(['git','show',rec['source_commit']+':'+Path(p).as_posix()],cwd=LAB)).hexdigest()==h,p
    result=read(folder/'results.json');maps=read(folder/'maps.json')
    expected=[dict(kind=k,pattern=p,compact=c,gate=g,batch=b,count=n,sample_start=s)
        for k in range(5) for p in [1,0,1,2,3,4,5,6,7,8,9,10] for c in [0,1] for g in [0,1]
        for b,n in [(1,1),(5,1),(5,5),(32,1),(32,7),(32,31),(32,32)] for s in [0,17,237,992]]
    assert result['cases']==expected and result['prefix_cases']==6720 and result['hand_vector_cases']==94080 and result['exact']
    real=json.loads(gzip.decompress((RAW/'d13-fixed-ranks-v1.json.gz').read_bytes()))
    d19=json.loads(gzip.decompress((RAW/'d19-static-cdf-maps.json.gz').read_bytes()))
    audited=[]
    for kind in range(5):
        prefix=[];hand=[];offsets=[0]
        for sample in range(1024):
            pm=[0xffffffff]*170;pm[0]=0;hm=[-1]*169;rank=0;group=0
            while rank<169:
                if kind==4:
                    h=real['order'][sample*169+rank];upper=real['upper'][sample*169+h]
                    assert real['lower'][sample*169+h]==rank
                else:
                    size=169 if kind==0 else 1 if kind==1 else (5 if rank==30 else 1) if kind==2 else 1+(rank*7+sample*3)%19
                    upper=min(169,rank+size)
                for r in range(rank,upper):
                    h=real['order'][sample*169+r] if kind==4 else (r*37+sample*11)%169
                    if kind==4:assert (real['lower'][sample*169+h],real['upper'][sample*169+h])==(rank,upper)
                    assert hm[h]==-1;hm[h]=group
                group+=1;rank=upper;pm[rank]=group
            assert min(hm)>=0
            prefix.extend(pm);hand.extend(hm);offsets.append(offsets[-1]+group+1)
        stride=max(offsets[min(1024,s+32)]-offsets[s] for s in range(1024))
        reconstructed=dict(kind=kind,prefix=prefix,hand_group=hand,sample_offsets=offsets,stride=stride)
        assert maps[kind]==reconstructed
        if kind==4:
            assert stride==d19['row_stride']==2160
            for key in ['prefix','hand_group','sample_offsets']:assert reconstructed[key]==d19[key]
        audited.append(dict(kind=kind,stride=stride,required_prefixes=offsets[-1]))
    prefixes=unused=0
    for case in expected:
        m=maps[case['kind']];s=case['sample_start'];n=case['count']
        rows=1 if case['gate'] else 2
        written=rows*(m['sample_offsets'][s+n]-m['sample_offsets'][s])
        prefixes+=written;unused+=4*m['stride']+32-written
    assert prefixes==result['required_prefixes_checked']==9364968
    assert unused==result['unused_slots_checked']==63813144

    # Reconstruct the entire appended source. Only storage addresses change.
    control=(folder/'control.cu').read_text();candidate=(folder/'candidate.cu').read_text()
    a=control.index('extern "C" __global__ void pf_exact_reuse_cdf(')
    b=control.index('extern "C" __global__ void pf_exact_reuse_terminal(',a)
    writer=control[a:b].replace('pf_exact_reuse_cdf(','pf_static_cdf(')
    changes=[
        ('u32 batch_capacity, const u32* aliases)','u32 batch_capacity, const u32* aliases, u32 row_stride, const u32* prefix_map, const u32* sample_offsets)'),
        ('size_t base = ((size_t)(compact ? blockIdx.x : slot) * batch_capacity + local) * (NC + 1);','size_t base = (size_t)(compact ? blockIdx.x : slot) * row_stride + sample_offsets[particle] - sample_offsets[sample_start];'),
        ('if (index < NC) cdf[base + index + 1] = carry + value;','if (index < NC) { u32 packed = prefix_map[(size_t)particle * (NC + 1) + index + 1]; if (packed != 0xffffffffu) cdf[base + packed] = carry + value; }')]
    for old,new in changes:assert writer.count(old)==1;writer=writer.replace(old,new)
    a=control.index('template<int Q, int O>');b=control.index('extern "C" __global__ void pf_multiway_terminal(',a)
    original=control[a:b].replace('pf_multiway_sum','pf_original_init').replace('u32 sample_start, u32 sample_count)','u32 sample_start, u32 sample_count, float initial)').replace('float sum = 0.f;','float sum = initial;')
    reader=original.replace('pf_original_init','pf_static_init')
    for old,new in [
        ('u32 sample_start, u32 sample_count, float initial)','u32 sample_start, u32 sample_count, float initial, const u32* sample_offsets)'),
        ('u32 lo = lower[hand], hi = upper[hand];','u32 lo = lower[hand], hi = lo + 1;\n        u32 local_offset = sample_offsets[sample_start + local] - sample_offsets[sample_start];'),
        ('u32 base = opponent_bases[q] + local * (NC + 1);','u32 base = opponent_bases[q] + local_offset;')]:
        assert reader.count(old)==1;reader=reader.replace(old,new)
    expected_source=control+writer+original+reader
    for o in range(2,9):
        q=(o+2)//2
        for packed in [False,True]:
            name='packed' if packed else 'original'
            call=f'pf_static_init<{q},{o}>(h,bases,cdf,lo,hi,start,count,initial[h],offsets)' if packed else f'pf_original_init<{q},{o}>(h,bases,cdf,lo,hi,start,count,initial[h])'
            expected_source+=f'\nextern "C" __global__ void {name}_{o}(const u32* bases,const float* cdf,const u32* lo,const u32* hi,u32 start,u32 count,const float* initial,const u32* offsets,float* out){{u32 h=threadIdx.x;if(h<NC)out[h]={call};}}\n'
    assert candidate==expected_source
    assert sha(folder/'control.ptx')==sha(RAW/'r03-compiler-v2/exact-candidate.ptx')
    a=entries((folder/'control.ptx').read_text());b=entries((folder/'candidate.ptx').read_text())
    added={'pf_static_cdf'}|{f'{name}_{o}' for name in ['packed','original'] for o in range(2,9)}
    assert len(a)==20 and set(b)-set(a)==added and all(a[k]==b[k] for k in a)
    resources={x['kernel']:x for x in result['resources']}
    selected=[resources[k] for k in ['pf_static_cdf']+[f'packed_{o}' for o in range(2,9)]]
    gates=dict(no_spills=all(x['local_bytes']==0 for x in selected),no_shared_memory=all(x['shared_bytes']==0 for x in selected),registers=all(x['registers']<=64 for x in selected))
    receipt=read(RAW/'c23-static-frozen.json');assert receipt['source_run']=='c23-static-v1' and sha(LAB/'target/c23-static-frozen.exe')==receipt['sha256']
    out=dict(verified=True,admitted=all(gates.values()),retained=False,status='Static boundary CDF admitted to full solver integration' if all(gates.values()) else 'Static boundary CDF rejected at compiler screen',
        prefix_cases=6720,hand_vector_cases=94080,hand_values_compared=94080*169,required_prefixes_checked=prefixes,unused_slots_checked=unused,
        original_entries_unchanged=20,maps=audited,resources=resources,gates=gates,independent_map_and_address_audit=True,
        frozen_executable_sha256=receipt['sha256'],protocol_sha256=sha(HERE/'C23_PROTOCOL.md'),artifacts={p.name:sha(p) for p in folder.iterdir() if p.is_file()},
        scope='Standalone writer and reader exactness only. Full solver integration, saved continuation, allocation recovery and complete-work speed remain unqualified.')
    for filename in ['c23-screen-verified.json','c23-verified.json']:
        dest=RAW/filename
        if dest.exists():assert read(dest)==out
        else:dest.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
