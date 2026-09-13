"""Audit sparse predicate prefix exactness and independently reconstruct source."""
import hashlib,json,re,subprocess
from pathlib import Path
from check_d09 import entries
from check_c19_screen import instructions
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw';LAB=HERE.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    rec=read(RAW/'c21-prefix-v1-exit.json');folder=RAW/'c21-prefix-v1'
    assert rec['returncode']==0 and rec['reason'] is None and rec['seconds']<=300
    assert '1 passed; 0 failed; 0 ignored' in (RAW/'c21-prefix-v1.log').read_text(encoding='utf-8')
    for p,h in rec['inputs'].items():assert sha(Path(p))==h
    mapping={str(Path(k)):v for k,v in read(HERE/'artifacts/c21-v1-source-map.json').items()}
    for p,h in rec['solver_source_files'].items():
        if p in mapping:
            v=mapping[p];assert sha(HERE/v['archive'])==h==v['sha256']
        else:assert hashlib.sha256(subprocess.check_output(['git','show',rec['source_commit']+':'+Path(p).as_posix()],cwd=LAB)).hexdigest()==h
    result=read(folder/'results.json')
    expected=[dict(pattern=p,zero=p in [0,7,8],compact=c,gate=g,batch=b,count=n,sample_start=s)
        for p in [1,0,1,2,3,4,5,6,7,8,9,10] for c in [0,1] for g in [0,1]
        for b,n in [(1,1),(5,1),(5,5),(32,1),(32,7),(32,31),(32,32)] for s in [0,17,992]]
    assert result['cases']==expected and result['cases_per_variant']==1008 and result['exact'] and result['guard_and_untouched_slots_checked']
    control=(folder/'control.cu').read_text();candidate=(folder/'candidate.cu').read_text()
    start=control.index('extern "C" __global__ void pf_exact_reuse_cdf(')
    end=control.index('extern "C" __global__ void pf_exact_reuse_terminal(',start)
    writer=control[start:end];scan=re.search(r'        #pragma unroll\n        for \(int step = 1; step < 32; step <<= 1\) \{.*?\n        }',writer,re.S).group()
    replacement=r'''        if (__any_sync(0xffffffff, value != 0.f)) {
            #pragma unroll
            for (int step = 1; step < 32; step <<= 1) {
                asm volatile("{ .reg .f32 other; .reg .pred valid;\n"
                    "shfl.sync.up.b32 other|valid, %0, %1, 0, 0xffffffff;\n"
                    "@valid add.rn.f32 %0, %0, other;\n}"
                    : "+f"(value) : "r"(step));
            }
        }'''
    sparse=writer.replace('pf_exact_reuse_cdf(','pf_exact_reuse_cdf_sparse_predicate(').replace(scan,replacement)
    assert candidate==control+'\n'+sparse
    assert sha(folder/'control.ptx')==sha(RAW/'r03-compiler-v2/exact-candidate.ptx')
    a=entries((folder/'control.ptx').read_text());b=entries((folder/'candidate.ptx').read_text())
    assert len(a)==20 and set(b)-set(a)=={'pf_exact_reuse_cdf_sparse_predicate'} and all(a[k]==b[k] for k in a)
    body=b['pf_exact_reuse_cdf_sparse_predicate'];lines=body.splitlines();bypasses=[]
    for i,line in enumerate(lines):
        if 'vote.sync.any.pred' not in line:continue
        vote=re.search(r'vote.sync.any.pred\s+(%p\d+),',line).group(1)
        neg=re.search(r'not.pred\s+(%p\d+),\s*'+re.escape(vote)+r';',lines[i+1]).group(1)
        target=re.search(r'@'+re.escape(neg)+r' bra\s+(\S+);',lines[i+2]).group(1)
        j=next(j for j in range(i+3,len(lines)) if lines[j].strip()==target+':')
        skipped='\n'.join(lines[i+3:j])
        assert skipped.count('shfl.sync.up.b32')==5 and skipped.count('@valid add.rn.f32')==5
        assert skipped.count('other|valid')==5
        bypasses.append(dict(target=target,skipped_static_instructions=len(instructions(skipped)),shuffles=5,guarded_additions=5))
    assert len(bypasses)==6 and body.count('@valid add.rn.f32')==30
    counts=dict(control=len(instructions(a['pf_exact_reuse_cdf'])),candidate=len(instructions(body)))
    resources={x['variant']:x for x in result['resources']};c=resources['candidate']
    gates=dict(no_spills=c['local_bytes']==0,registers=c['registers']<=48,no_shared_memory=c['shared_bytes']==0,
        static_code_size=counts['candidate']<=1.2*counts['control'],six_real_scan_bypasses=len(bypasses)==6)
    admitted=all(gates.values());receipt=read(RAW/'c21-prefix-frozen.json')
    assert sha(LAB/'target/c21-prefix-frozen.exe')==receipt['sha256'] and receipt['source_run']=='c21-prefix-v1'
    out=dict(verified=True,admitted=admitted,retained=False,
        status='Sparse predicate scan admitted to solver qualification' if admitted else 'Sparse predicate scan rejected at compiler cost screen',
        exact_prefix_cases=1008,resources=resources,gates=gates,static_ptx_instruction_counts=counts,
        static_instruction_ratio=counts['candidate']/counts['control'],original_entries_unchanged=len(a),
        scan_bypasses=bypasses,frozen_executable_sha256=receipt['sha256'],protocol_sha256=sha(HERE/'C21_PROTOCOL.md'),
        artifacts={p.name:sha(p) for p in folder.iterdir() if p.is_file()},
        scope='Standalone exactness and static compiler screen only; complete-work timing still required.')
    dest=RAW/'c21-screen-verified.json'
    if dest.exists():assert read(dest)==out
    else:dest.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    latest=RAW/'c21-verified.json'
    if not latest.exists():latest.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
