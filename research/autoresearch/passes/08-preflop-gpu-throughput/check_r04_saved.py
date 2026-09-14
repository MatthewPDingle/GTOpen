"""Normal selection must match the immutable retained saved-state witnesses."""
import hashlib,json
from pathlib import Path
from run_c23 import HERE,RAW,read

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

initial=read(RAW/'r04-initial-verified.json');saved={}
for fixture in ['small','large']:
    name=f'r04-{fixture}-adaptive-v1';r=read(RAW/(name+'-exit.json'));x=read(RAW/(name+'.json'));ref=read(RAW/f'r03-{fixture}-retained-v1.json')
    assert r['returncode']==0 and r['reason'] is None and r['seconds']<=180
    assert r['solver_source_files']==initial['solver_source_files'] and r['exe_sha256']==initial['executable_sha256']
    for path,h in r['inputs'].items():assert sha(path)==h,path
    for k in ['nodes','initial_iteration','arena_fingerprint','continued_fingerprint','continued_iteration','continued_gaps','continued_evs','layout','metadata_preserved','save_reload_arenas_bitwise_equal']:
        assert x[k]==ref[k],(fixture,k)
    assert len(x['rows'])==6 and x['metadata_preserved'] and x['save_reload_arenas_bitwise_equal']
    for a,b in zip(x['rows'],ref['rows']):
        for k in ['index','iteration','gaps','evs']:assert a[k]==b[k],(fixture,k)
    for k in ['selection','reload_selection']:
        s=x[k];assert s['mode']=='retained_cohorts' and s['narrow_offsets'] and s['static_cdf']
        assert s['fallback_reason'] is None and s['static_cdf_fallback_reason'] is None
    assert sha(x['save'])==sha(ref['save'])
    saved[fixture]={'saved_sha256':sha(x['save']),'arena_fingerprint':x['arena_fingerprint'],'continued_fingerprint':x['continued_fingerprint']}
result={'verified':True,'passed':True,'saved':saved,'exact_seventh_iteration_after_reload':True,'static_tables_selected_initial_and_reload':True,'executable_sha256':initial['executable_sha256']}
dest=RAW/'r04-saved-verified.json'
if dest.exists():assert read(dest)==result
else:dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
