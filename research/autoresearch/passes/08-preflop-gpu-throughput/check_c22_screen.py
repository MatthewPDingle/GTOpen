"""Independent manifest, case, scratch accounting and compiler audit for C22."""
import gzip,hashlib,json,re,subprocess
from pathlib import Path
from check_d09 import entries
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw';LAB=HERE.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def clean(s):return re.sub(r'\s+','',s)
def main():
    r=read(RAW/'c22-pipeline-v1-exit.json');folder=RAW/'c22-pipeline-v1'
    assert r['returncode']==0 and r['reason'] is None and r['seconds']<=300
    assert '1 passed; 0 failed; 0 ignored' in (RAW/'c22-pipeline-v1.log').read_text()
    for p,h in r['inputs'].items():assert sha(Path(p))==h
    mapping={str(Path(k)):v for k,v in read(HERE/'artifacts/c22-v1-source-map.json').items()}
    for p,h in r['solver_source_files'].items():
        if p in mapping:assert sha(HERE/mapping[p]['archive'])==mapping[p]['sha256']==h
        else:assert hashlib.sha256(subprocess.check_output(['git','show',r['source_commit']+':'+Path(p).as_posix()],cwd=LAB)).hexdigest()==h
    parent=(HERE/'artifacts/c22-v1/src/preflop/gpu.rs').read_bytes()
    old=subprocess.check_output(['git','show',r['source_commit']+':crates/solver/src/preflop/gpu.rs'],cwd=LAB)
    assert parent==old+b'\n#[cfg(all(test, feature = "preflop-research"))]\nmod rank_pipeline;\n'
    # Reconstruct synthetic rank partition sizes independently.
    group_counts=[]
    for kind in range(4):
        counts=[]
        for s in range(1024):
            cursor=0;spans=[]
            while cursor<169:
                if kind==0:width=169
                elif kind==1:width=1
                elif kind==2:width=5 if cursor==30 else 1
                else:width=1+(cursor*7+s*3)%19
                spans.append((cursor,min(169,cursor+width)));cursor=spans[-1][1]
            counts.append(len(spans))
        group_counts.append(counts)
    real=json.loads(gzip.decompress((RAW/'d13-fixed-ranks-v1.json.gz').read_bytes()))
    group_counts.append([len(set(zip(real['lower'][s*169:(s+1)*169],real['upper'][s*169:(s+1)*169]))) for s in range(1024)])
    expected=[];slots=0;hands=0
    for kind in range(5):
      groups=max(group_counts[kind])
      for density in range(3):
       for nonzero in [False,True]:
        for o in range(2,9):
         for start in [0,1,37,992]:
          for count in [1,5,7,23,31,32]:
            total,cap=[(1,1),(2,1),(3,2),(5,4),(9,4)][len(expected)%5]
            expected.append(dict(kind=kind,density=density,nonzero_initial=nonzero,opponents=o,start=start,count=count,terminals=total,capacity=cap,groups=groups))
            slots+=((total+cap-1)//cap)*(36+cap*32*groups*5);hands+=total*169
    x=read(folder/'results.json')
    assert x['exact'] and x['all_unused_slots_checked'] and x['case_count']==5040
    assert x['cases']==expected and x['scratch_slots_checked']==slots==398566240 and x['hand_values_checked']==hands==3407040
    a=entries((folder/'control.ptx').read_text());b=entries((folder/'candidate.ptx').read_text())
    retained=entries((RAW/'r03-compiler-v2/cohort-candidate.ptx').read_text())
    assert len(a)==18 and a==retained and all(a[k]==b[k] for k in a)
    assert set(b)-set(a)=={f'{name}_{o}' for o in range(2,9) for name in ['original','producer','consumer']}
    control=(folder/'control.cu').read_text();candidate=(folder/'candidate.cu').read_text()
    helper=(HERE/'artifacts/c22-v1/src/preflop/gpu/rank_pipeline.cu').read_text()
    assert candidate.startswith(control+helper)
    # The product arithmetic must remain the original helper's ordered block.
    original=control[control.index('float pf_original_init('):]
    # Compare through the opponent-loop closing braces with a brace parser.
    def product_block(s):
        start=s.index('float product[Q];');loop=s.index('for (int ',s.index('product[t] = 1.f;',start));brace=s.index('{',loop)
        at=brace+1;depth=1
        while depth:depth+=(s[at]=='{')-(s[at]=='}');at+=1
        return s[start:at]
    p=product_block(helper).replace('opponent','q').replace('bases[q]','opponent_bases[q]')
    assert clean(product_block(original))==clean(p)
    assert 'sum += weight * scratch[((size_t)local * groups + group) * quadratures + t];' in helper
    assert helper.count('#pragma unroll 2')==2 and '__syncthreads' not in helper
    resources=x['resources'];assert [(v['opponents'],v['kernel']) for v in resources]==[(o,k) for o in range(2,9) for k in ['original','producer','consumer']]
    kernels=[v for v in resources if v['kernel']!='original']
    gates=dict(no_local_spills=all(v['local_bytes']==0 for v in kernels),no_shared_memory=all(v['shared_bytes']==0 for v in kernels),bounded_registers=all(v['registers']<=128 for v in kernels),no_block_barriers=all('bar.sync' not in b[f'{k}_{o}'] for o in range(2,9) for k in ['producer','consumer']))
    frozen=read(RAW/'c22-pipeline-frozen.json');assert frozen['source_run']=='c22-pipeline-v1' and sha(LAB/'target/c22-pipeline-frozen.exe')==frozen['sha256']
    admitted=all(gates.values())
    out=dict(verified=True,admitted=admitted,retained=False,status='Separate rank kernels admitted to full solver qualification' if admitted else 'Separate rank kernels rejected at resource screen',exact_cases=5040,hand_values_checked=hands,scratch_slots_checked=slots,original_entries_unchanged=18,resources=resources,gates=gates,frozen_executable_sha256=frozen['sha256'],protocol_sha256=sha(HERE/'C22_PROTOCOL.md'),artifacts={p.name:sha(p) for p in folder.iterdir() if p.is_file()},scope='Standalone GPU exactness and compiler resource screen only; integration and complete-work timing remain unqualified.')
    for name in ['c22-screen-verified.json','c22-verified.json']:
        dest=RAW/name
        if dest.exists():assert read(dest)==out
        else:dest.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
