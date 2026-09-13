"""Audit source, device coverage and compiler admission; no runtime claim."""
import hashlib,json,re,subprocess
from pathlib import Path
from check_d09 import entries
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw';LAB=HERE.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def instructions(body):
    result=[]
    for line in body.splitlines():
        line=line.strip()
        if line.startswith('@'):line=line.split(None,1)[1]
        if re.match(r'^[a-z][a-z0-9_]*(?:\.[a-zA-Z0-9_:]+)*(?:\s|;)',line):result.append(line)
    return result
def main():
    rec=read(RAW/'c19-prefix-v1-exit.json');folder=RAW/'c19-prefix-v1'
    assert rec['returncode']==0 and rec['reason'] is None and rec['seconds']<=300
    log=(RAW/'c19-prefix-v1.log').read_text(encoding='utf-8')
    assert '1 passed; 0 failed; 0 ignored' in log
    for p,h in rec['inputs'].items():assert sha(Path(p))==h,p
    mapping={str(Path(k)):v for k,v in read(HERE/'artifacts/c19-v1-source-map.json').items()}
    for p,h in rec['solver_source_files'].items():
        if p in mapping:
            info=mapping[p];assert sha(HERE/info['archive'])==h==info['sha256']
        else:assert hashlib.sha256(subprocess.check_output(['git','show',rec['source_commit']+':'+Path(p).as_posix()],cwd=LAB)).hexdigest()==h,p
    x=read(folder/'results.json')
    expected=[dict(pattern=p,zero=p==0,compact=c,gate=g,batch=b,count=n,sample_start=s)
        for p in [1,0,1,2,3,4,5,6] for c in [0,1] for g in [0,1]
        for b,n in [(1,1),(5,1),(5,5),(32,1),(32,7),(32,31),(32,32)] for s in [0,17,992]]
    assert x['cases']==expected and x['cases_per_variant']==672 and x['exact'] and x['guard_and_untouched_slots_checked']
    control=(folder/'control.cu').read_text(encoding='utf-8');candidate=(folder/'candidate.cu').read_text(encoding='utf-8')
    a=control.index('extern "C" __global__ void pf_exact_reuse_cdf(')
    b=control.index('extern "C" __global__ void pf_exact_reuse_terminal(',a)
    writer=control[a:b];begin=writer.index('    float carry = 0.f;');end=writer.rindex('\n}')
    scan=''
    for tile in range(6):
        scan+=f'    u32 i{tile} = {tile*32}u + lane;\n    float v{tile} = i{tile} < NC ? normalized[(size_t)(compact ? blockIdx.x : slot) * NC + order[(size_t)particle * NC + i{tile}]] : 0.f;\n'
    for step in [1,2,4,8,16]:
        for tile in range(6):scan+=f'    {{ float add = __shfl_up_sync(0xffffffff, v{tile}, {step}); if (lane >= {step}u) v{tile} += add; }}\n'
    scan+='    float carry = 0.f;\n'
    for tile in range(6):scan+=f'    if (i{tile} < NC) cdf[base + i{tile} + 1] = carry + v{tile};\n    carry += __shfl_sync(0xffffffff, v{tile}, 31);\n'
    assert candidate==control[:a]+writer[:begin]+scan+writer[end:]+control[b:]
    assert sha(folder/'control.ptx')==sha(RAW/'r03-compiler-v2/exact-candidate.ptx')
    pt={v:entries((folder/(v+'.ptx')).read_text(encoding='utf-8')) for v in ['control','candidate']}
    assert pt['control'].keys()==pt['candidate'].keys()
    changed=[k for k in pt['control'] if pt['control'][k]!=pt['candidate'][k]]
    assert changed in [[],['pf_exact_reuse_cdf']]
    counts={v:len(instructions(pt[v]['pf_exact_reuse_cdf'])) for v in pt}
    assert min(counts.values())>100
    resources={v['variant']:v for v in x['resources']};c=resources['candidate']
    admitted=bool(changed) and c['local_bytes']==0 and c['registers']<=48 and counts['candidate']<=1.2*counts['control']
    frozen=LAB/'target/c19-prefix-frozen.exe';receipt=read(RAW/'c19-prefix-frozen.json')
    assert sha(frozen)==receipt['sha256'] and receipt['source_run']=='c19-prefix-v1'
    assert sha(LAB/'target/r03-v3-server-frozen.exe')==read(RAW/'r03-release-verified.json')['executable_sha256']
    out=dict(verified=True,admitted=admitted,retained=False,
        status='CDF interleaving admitted to solver qualification' if admitted else 'CDF interleaving rejected at compiler screen',
        exact_prefix_cases=672,resources=resources,static_ptx_instruction_counts=counts,
        changed_entries=changed,other_entries_unchanged=len(pt['control'])-len(changed),
        frozen_executable_sha256=receipt['sha256'],protocol_sha256=sha(HERE/'C19_PROTOCOL.md'),
        artifacts={p.name:sha(p) for p in folder.iterdir() if p.is_file()},
        source_inputs_archives_verified=True,
        scope='Standalone device/compiler admission only. Full solver qualification and complete timings remain unperformed.')
    dest=RAW/'c19-screen-verified.json'
    if dest.exists():assert read(dest)==out
    else:dest.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    latest=RAW/'c19-verified.json'
    if not latest.exists():latest.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
