"""Independently reproduce D07 using Python OrderedDict and frozen witnesses."""
import gzip,hashlib,json,struct
from collections import OrderedDict
from pathlib import Path
HERE=Path(__file__).resolve().parent
RAW=HERE/'raw';NONE=2**32-1
def sha(b):return hashlib.sha256(b).hexdigest()
def read(name):return json.loads((RAW/name).read_text())
def stats(rows,np):
    seats=[]
    for p in range(np):
        caches=[OrderedDict(),OrderedDict()];misses=[0,0];refs=0;terms=0;shared=0;equal=0
        previous=(NONE,)*9;sources=set();keys=set()
        for node,live,value,*src in rows:
            if not live&(1<<p):continue
            src[p]=NONE;key=tuple(src)
            for id in src[:np]:
                if id==NONE:continue
                refs+=1;sources.add(id);shared+=id in previous
                for i,capacity in enumerate([64,256]):
                    cache=caches[i]
                    if id in cache:cache.move_to_end(id)
                    else:
                        misses[i]+=1;cache[id]=None
                        if len(cache)>capacity:cache.popitem(last=False)
            equal+=terms>0 and key==previous;terms+=1;keys.add(key);previous=key
        seats.append(dict(seat=p,terminals=terms,references=refs,distinct_sources=len(sources),distinct_full_keys=len(keys),adjacent_shared_rows=shared,adjacent_equal_keys=equal,misses=misses))
    return dict(seats=seats,total_misses=[sum(s['misses'][i] for s in seats) for i in range(2)])
def main():
    manifest=read('d07-witness-manifest.json');results={}
    build=read('d07-invariants-v1-exit.json')
    assert build['returncode']==0 and build['reason'] is None
    for name,entry in read('d07-source-map.json').items():
        assert sha((HERE/entry['archive']).read_bytes())==entry['sha256']==build['solver_source_files'][name.replace('/','\\')]
    assert '1 passed; 0 failed; 1 ignored' in (RAW/'d07-invariants-v1.log').read_text()
    for fixture in ['small','large']:
        record=read(f'd07-{fixture}-v1-exit.json');assert record['returncode']==0 and record['reason'] is None
        assert record['solver_source_files']==build['solver_source_files']
        assert manifest['executable_sha256'] in record['inputs'].values()
        assert manifest['fixtures'][fixture]['save_sha256'] in record['inputs'].values()
        data=(RAW/f'd07-{fixture}-topology-v1.bin.gz').read_bytes();m=manifest['fixtures'][fixture]
        assert sha(data)==m['compressed_sha256'];data=gzip.decompress(data)
        assert len(data)==m['witness_bytes'] and sha(data)==m['witness_sha256']
        assert data[:8]==b'D07V1\0\0\0';np,nodes,n=struct.unpack_from('<3I',data,8)
        assert 3<=np<=9 and len(data)==20+n*48
        rows=list(struct.iter_unpack('<12I',data[20:]));seen=set();values=set();last=-1
        for node,live,value,*src in rows:
            assert last<node<nodes and node not in seen;seen.add(node);last=node
            assert value>0 and value not in values;values.add(value)
            assert live.bit_count()>=3 and live<(1<<np)
            live_sources=[]
            for q,id in enumerate(src):
                if q<np and live&(1<<q):assert id<nodes+np-1;live_sources.append(id)
                else:assert id==NONE
            assert len(set(live_sources))==len(live_sources)
        candidate=sorted(rows,key=lambda r:(r[1],r[3:],r[0]))
        assert {r[0] for r in candidate}==seen
        outpath=RAW/f'd07-{fixture}-v1.json';assert sha(outpath.read_bytes())==m['output_sha256']
        out=json.loads(outpath.read_text());assert (out['players'],out['nodes'],out['terminals'])==(np,nodes,n)
        assert out['exact_coverage'] and out['unique_terminal_values']
        assert out['changed_positions']==sum(a[0]!=b[0] for a,b in zip(rows,candidate))>0
        for label,sequence in [('baseline',rows),('candidate',candidate)]:
            calculated=stats(sequence,np);assert calculated==out[label],(fixture,label)
        ratios=[b/a for a,b in zip(out['baseline']['total_misses'],out['candidate']['total_misses'])]
        results[fixture]=dict(miss_ratios=ratios,terminals=n,changed_positions=out['changed_positions'],independent_reproduction=True)
        print(json.dumps(dict(fixture=fixture,**results[fixture])),flush=True)
    passed=all(x<=.90 for x in results['large']['miss_ratios']) and all(x<=1.03 for x in results['small']['miss_ratios'])
    result=dict(status='Static order admitted for a GPU prototype' if passed else 'Static order rejected by locality admission gate',admitted=passed,fixtures=results,scope='Exact topology and independent LRU proxy agreement; no measured GPU speed gain or convergence improvement.')
    target=RAW/'d07-verified.json'
    if target.exists():assert json.loads(target.read_text())==result
    else:target.write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
