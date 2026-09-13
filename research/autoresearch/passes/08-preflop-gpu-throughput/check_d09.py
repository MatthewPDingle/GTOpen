"""Independent compiler/device admission audit for bounded CDF writer indices."""
import re,json,hashlib,subprocess
from pathlib import Path
from check_r03_saved import HERE,RAW,LAB,read,sha

def entries(text):
    out={}
    for m in re.finditer(r'\.visible \.entry (\w+)\(',text):
        begin=text.index('{',m.end());depth=1;at=begin+1
        while depth:
            depth+=(text[at]=='{')-(text[at]=='}');at+=1
        out[m[1]]=text[m.start():at]
    return out

def address_ops(text):
    ops=[]
    for line in text.splitlines():
        words=line.strip().split()
        if words and words[0].startswith('@'):words=words[1:]
        if words and re.match(r'^(add|sub|mul|mad|shl|shr|cvt|cvta|and|or)\.',words[0]) and re.search(r'\.[usb](32|64)(\.|$)',words[0]):ops.append(words[0])
    return ops

def main():
    source=None;mapping={str(Path(k)):v for k,v in read(HERE/'artifacts/d09-source-map.json').items()}
    for name,cap in [('d09-writer-v1',300),('d09-bounds-v1',90)]:
        r=read(RAW/(name+'-exit.json'));assert r['returncode']==0 and r['reason'] is None and r['seconds']<cap
        assert '1 passed; 0 failed' in (RAW/(name+'.log')).read_text(encoding='utf8')
        for f,h in r['inputs'].items():assert sha(f)==h,f
        for f,h in r['solver_source_files'].items():
            if f in mapping:assert sha(HERE/mapping[f])==h,f
            else:assert hashlib.sha256(subprocess.check_output(['git','show','53288a0:'+Path(f).as_posix()],cwd=LAB)).hexdigest()==h,f
        if source is None:source=r['solver_source_files']
        else:assert source==r['solver_source_files']
    archived=(HERE/'artifacts/d09-v1/narrow_cdf.rs').read_text(encoding='utf8')
    assert (LAB/'crates/solver/src/preflop/gpu/narrow_cdf.rs').read_text(encoding='utf8')==archived.replace('#[test]\nfn bounded_writer_matches_retained_prefix','#[test]\n#[ignore = "manual CUDA writer compiler screen; requires output directory"]\nfn bounded_writer_matches_retained_prefix')
    old_gpu=subprocess.check_output(['git','show','53288a0:crates/solver/src/preflop/gpu.rs'],cwd=LAB).decode().replace('\r\n','\n')
    assert (LAB/'crates/solver/src/preflop/gpu.rs').read_text(encoding='utf8')==old_gpu+'\n#[cfg(all(test, feature = "preflop-research"))]\nmod narrow_cdf;\n'
    assert sha(LAB/'target/r03-v3-server-frozen.exe')==read(RAW/'r03-release-verified.json')['executable_sha256']
    exe=LAB/'target/d09-writer-frozen.exe';assert read(RAW/'d09-bounds-v1-exit.json')['exe_sha256']==sha(exe)
    address=json.loads(re.search(r'R03_ADDRESS (\{[^\n]+\})',(RAW/'d09-bounds-v1.log').read_text(encoding='utf8'))[1])
    assert address['exact'] and address['cases']==48 and address['max_byte_offset']>2**32 and address['oversized_buffers_refused']
    folder=RAW/'d09-compiler-v1';x=read(folder/'results.json')
    assert x['exact'] and x['cases_per_variant']==252 and len(x['cases'])==252 and x['guard_and_untouched_slots_checked']
    expected=[dict(zero=z,compact=c,gate=g,batch=b,count=n,sample_start=s) for z in [False,True,False] for c in [0,1] for g in [0,1] for b,n in [(1,1),(5,1),(5,5),(32,1),(32,7),(32,31),(32,32)] for s in [0,17,992]]
    assert x['cases']==expected
    control=(folder/'control.cu').read_text(encoding='utf8');candidate=(folder/'candidate.cu').read_text(encoding='utf8')
    a=control.index('extern "C" __global__ void pf_exact_reuse_cdf(');b=control.index('extern "C" __global__ void pf_exact_reuse_terminal(',a)
    writer=control[a:b]
    for old,new in [('size_t base = ((size_t)(compact ? blockIdx.x : slot) * batch_capacity + local) * (NC + 1);','u32 base = ((compact ? blockIdx.x : slot) * batch_capacity + local) * (NC + 1);'),('cdf[base]','cdf[(size_t)base]'),('cdf[base + index + 1]','cdf[(size_t)(base + index + 1)]')]:
        assert writer.count(old)==1;writer=writer.replace(old,new)
    assert candidate==control[:a]+writer+control[b:]
    assert sha(folder/'control.ptx')==sha(RAW/'r03-compiler-v2/exact-candidate.ptx')
    ptx={role:entries((folder/(role+'.ptx')).read_text(encoding='utf8')) for role in ['control','candidate']};assert ptx['control'].keys()==ptx['candidate'].keys()
    changed=[k for k,v in ptx['control'].items() if ptx['candidate'][k]!=v];assert changed==['pf_exact_reuse_cdf'],changed
    counts={role:len(address_ops(ptx[role]['pf_exact_reuse_cdf'])) for role in ptx}
    resources={r['variant']:r for r in x['resources']};a=resources['control'];b=resources['candidate']
    admitted=(b['registers']<a['registers'] or counts['candidate']<counts['control']) and b['local_bytes']<=a['local_bytes']
    result={'exact':True,'admitted':admitted,'decision':'prototype admitted' if admitted else 'rejected at compiler screen',
        'cases_per_variant':252,'address_witnesses':address,'resources':resources,'integer_address_ptx_ops':counts,
        'other_ptx_entries_unchanged':len(ptx['control'])-1,'source_input_executable_hashes_checked':True,
        'scope':'Static compiler/device screen, not measured runtime or convergence. No normal GPU dispatch change.'}
    target=RAW/'d09-verified.json'
    if target.exists():assert read(target)==result
    else:target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
