"""Source-level work counts; no solver/GPU invocation or timing claim."""
import array,gzip,hashlib,json,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def digest(b):return hashlib.sha256(b).hexdigest()
def decode_struct(data):
    assert data[:8]==b'D10V1\0\0\0';np,nt=struct.unpack_from('<2I',data,8);at=16;rows=[]
    for mode in [0,1]:
        for seat in range(np):
            m,p,n=struct.unpack_from('<3I',data,at);at+=12;assert (m,p)==(mode,seat);at+=4*n;hist=[0]*9
            for _ in range(nt):
                k=struct.unpack_from('<I',data,at)[0];at+=4;assert k==0 or 2<=k<np;hist[k]+=1;at+=4*k
            rows.append({'mode':mode,'player':seat,'baseline_rows':n,'opponents':hist})
    assert at==len(data);return np,nt,rows

def decode_array(data):
    a=array.array('I');a.frombytes(data[8:]);assert a.itemsize==4
    if sys.byteorder!='little':a.byteswap()
    np,nt=a[:2];at=2;rows=[]
    for i in range(2*np):
        mode,seat,n=a[at:at+3];assert mode==i//np and seat==i%np;at+=3+n;h=[0]*9
        for _ in range(nt):
            k=a[at];h[k]+=1;at+=k+1
        rows.append({'mode':mode,'player':seat,'baseline_rows':n,'opponents':h})
    assert at==len(a);return np,nt,rows

def main():
    sources={};fixtures={};d10=read(RAW/'d10-verified.json');assert not d10['admitted']
    flop_per=[0,0,18,25,46,56,86,99,138]
    for o in range(2,9):
        q=(o+2)//2
        # Explicit expansion independently checks the closed form.
        ops=sum(1+sum(3 for _ in range(q)) for _ in range(o))+sum(2 for _ in range(q))
        assert ops==o+3*q*o+2*q==flop_per[o]
    for fixture in ['small','large']:
        name=f'd10-{fixture}-v1';paths=[RAW/(name+'-witness.bin.gz'),RAW/(name+'-witness-manifest.json'),RAW/(name+'.json')]
        for path in paths:sources[path.name]=digest(path.read_bytes())
        m=read(paths[1]);data=paths[0].read_bytes();assert digest(data)==m['compressed_sha256'];data=gzip.decompress(data)
        assert digest(data)==m['witness_sha256'] and len(data)==m['witness_bytes']
        a=decode_struct(data);assert a==decode_array(data);np,nt,rows=a
        saved=read(paths[2]);assert saved['arenas_unchanged'] and saved['read_only'] and len(saved['rows'])==len(rows)
        modes={}
        for mode,label in [(0,'learning'),(1,'check')]:
            hist=[0]*9
            for r,old in zip(rows,saved['rows']):
                assert r['mode']==old['mode'] and r['player']==old['player'] and r['baseline_rows']==old['unique_distributions']
                h=r['opponents'];assert sum(h)==nt and sum(h[2:])==old['positive_terminals'] and sum(o*h[o] for o in range(2,9))==old['weighted_terminals']
                if r['mode']==mode:hist=[x+y for x,y in zip(hist,h)]
            distinct=d10['fixtures'][fixture]['tiles']['128']['current' if mode==0 else 'average']['baseline_rows']
            if mode==0:assert distinct==sum(r['baseline_rows'] for r in rows if r['mode']==0)
            work=sum(hist[o]*flop_per[o] for o in range(2,9))*169*1024
            gathers=sum(hist[o]*2*o for o in range(2,9))*169*1024*4
            volume=distinct*1024*170*4
            modes[label]={'terminal_opponent_histogram':hist,'positive_terminal_tasks':sum(hist[2:]),'distinct_distribution_rows':distinct,
                'logical_fp_operations':work,'fmax_operations':sum(hist[o]*o for o in range(2,9))*169*1024,'logical_cdf_gather_bytes':gathers,
                'minimum_logical_cdf_write_bytes':volume,'reference_fp32_only_seconds':work/(35.6*1e12),'reference_cdf_write_seconds':volume/(936*1e9)}
        fixtures[fixture]={'players':np,'terminals':nt,'iteration':saved['iteration'],'modes':modes}
    sources['d10-verified.json']=digest((RAW/'d10-verified.json').read_bytes())
    result={'verified':True,'independent_decoders_agree':True,'sources':sources,'source_flops_per_hand_sample_by_opponents':flop_per,
        'reference_specs':{'url':'https://www.nvidia.com/content/PDF/nvidia-ampere-ga-102-gpu-architecture-whitepaper-v2.pdf','table':9,'printed_pages':[44,45],'fp32_tflops':35.6,'memory_GBps':936,'reference_design_only':True},
        'fixtures':fixtures,'scope':'Logical work at immutable starting snapshots. Not measured instructions, DRAM traffic or a hardware lower bound. Bounded classifier may do additional work; real learning states evolve. Reference-design peaks do not characterize local boost clocks.'}
    dest=RAW/'d11-work-census.json'
    if dest.exists():assert read(dest)==result
    else:dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
