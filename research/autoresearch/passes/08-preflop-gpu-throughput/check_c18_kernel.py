"""C18 standalone source, compiler and exact-case verification."""
import hashlib,json,subprocess
from pathlib import Path
from check_d09 import entries
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw';LAB=HERE.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    r=read(RAW/'c18-kernel-v1-exit.json');assert r['returncode']==0 and r['reason'] is None and r['seconds']<=300
    assert '1 passed; 0 failed; 0 ignored' in (RAW/'c18-kernel-v1.log').read_text(encoding='utf-8')
    for p,h in r['inputs'].items():assert sha(Path(p))==h,p
    mapping={str(Path(k)):v for k,v in read(HERE/'artifacts/c18-v1-source-map.json').items()}
    for p,h in r['solver_source_files'].items():
        if p in mapping:assert sha(HERE/mapping[p]['archive'])==mapping[p]['sha256']==h,p
        else:assert hashlib.sha256(subprocess.check_output(['git','show',r['source_commit']+':'+Path(p).as_posix()],cwd=LAB)).hexdigest()==h,p
    folder=RAW/'c18-kernel-v1-compiler';k=read(folder/'resources.json')
    assert k['exact'] and k['cases']==5*3*2*7*4*6==5040 and k['hand_values']==169 and k['guard_values']==23 and k['mapping_bytes']==2080768
    assert len(k['resources'])==14
    for i,v in enumerate(k['resources']):
        o=i%7+2;assert v['opponents']==o and v['compact']==(i>=7) and v['local_bytes']==0
        assert v['shared_bytes']==(169*((o+2)//2)*4 if i>=7 else 0)
    a,b=[entries((folder/(role+'.ptx')).read_text(encoding='utf-8')) for role in ['control','candidate']]
    assert a.keys()==b.keys()
    changed=[key for key in a if a[key]!=b[key]];assert set(changed)=={f'audit_{o}' for o in range(2,9)}
    retained=entries((RAW/'r03-compiler-v2/cohort-candidate.ptx').read_text(encoding='utf-8'))
    assert all(a[key]==body for key,body in retained.items())
    result=dict(verified=True,exact_cases=5040,resources=k['resources'],changed_entries=changed,
        retained_entries_unchanged=len(retained),source_input_hashes_verified=True,
        compiler_hashes={x.name:sha(x) for x in folder.iterdir() if x.is_file()},
        status='Standalone exact compact-product kernel qualified',scope='No complete solver integration or speed result established by this check.')
    dest=RAW/'c18-kernel-verified.json'
    if dest.exists():assert read(dest)==result
    else:dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
