"""Verify the context-lifetime correction and its saved-game continuation."""
import json,subprocess,hashlib,re
from pathlib import Path
from check_r03_saved import HERE,RAW,LAB,read,sha

def main():
    old=read(RAW/'r03-selection-tests-v2-exit.json')['solver_source_files']
    fresh=read(RAW/'r03-selection-tests-v3-exit.json')['solver_source_files']
    changes={Path(k).as_posix() for k,v in fresh.items() if old[k]!=v}
    assert changes=={'crates/solver/src/preflop/gpu/adaptive_throughput.rs'},changes
    mapping={str(Path(k)):v for k,v in read(HERE/'artifacts/r03-v3-source-map.json').items()}
    for f,h in fresh.items():
        if f in mapping:assert sha(HERE/mapping[f])==h,f
        else:assert hashlib.sha256(subprocess.check_output(['git','show','db358c8:'+Path(f).as_posix()],cwd=LAB)).hexdigest()==h,f
    for name,expected in [('r03-selection-tests-v3','3 passed; 0 failed; 1 ignored'),('r03-numerical-v3','6 passed; 0 failed; 1 ignored')]:
        r=read(RAW/(name+'-exit.json'));assert r['returncode']==0 and r['reason'] is None and r['seconds']<300
        assert r['solver_source_files']==fresh
        assert expected in (RAW/(name+'.log')).read_text()
        for f,h in r['inputs'].items():assert sha(f)==h,f
    witnesses=[json.loads(x) for x in re.findall(r'R02_RECOVERY (\{[^\n]+\})',(RAW/'r03-selection-tests-v3.log').read_text())]
    assert [x['narrow'] for x in witnesses]==[False,True]
    for w in witnesses:
        assert w['selection']['mode']=='normal_gpu' and not w['selection']['narrow_offsets']
        assert len(w['events'])==1 and 'CUDA_ERROR_OUT_OF_MEMORY' in w['events'][0]['error']
        assert w['events'][0]['requested_bytes']==2**50 and w['events'][0]['partial_extra_bytes']>0
        assert w['fallback_memory']['used']==w['before']['used']+w['normal_allocation_bytes']
        assert w['after_drop']['used']==w['after_retry']['used']==w['before']['used']
        assert w['full_arenas_roots_gap_ev_equal'] and w['captured_stop_sync_equal'] and w['retry_optimized_succeeded']
    saved={}
    for fixture in ['small','large']:
        name=f'r03-v3-{fixture}-adaptive-v1';r=read(RAW/(name+'-exit.json'));x=read(RAW/(name+'.json'));ref=read(RAW/f'r03-{fixture}-retained-v1.json')
        assert r['returncode']==0 and r['reason'] is None and r['seconds']<240
        assert r['solver_source_files']==fresh and r['exe_sha256']==sha(LAB/'target/r03-v3-qualification-frozen.exe')
        for f,h in r['inputs'].items():assert sha(f)==h,f
        for k in ['nodes','initial_iteration','arena_fingerprint','continued_fingerprint','continued_iteration','continued_gaps','continued_evs','layout','metadata_preserved','save_reload_arenas_bitwise_equal']:assert x[k]==ref[k],k
        assert len(x['rows'])==6 and x['metadata_preserved'] and x['save_reload_arenas_bitwise_equal']
        for a,b in zip(x['rows'],ref['rows']):
            for k in ['index','iteration','gaps','evs']:assert a[k]==b[k],k
        for k in ['selection','reload_selection']:
            assert x[k]['mode']=='retained_cohorts' and x[k]['narrow_offsets'] and x[k]['fallback_reason'] is None
        assert sha(x['save'])==sha(ref['save'])
        saved[fixture]={'saved_sha256':sha(x['save']),'arena_fingerprint':x['arena_fingerprint'],'continued_fingerprint':x['continued_fingerprint']}
    result={'passed':True,'source_change':'CUDA context lifetime only','source_input_executable_hashes_checked':True,'real_partial_allocation_recovery':True,'saved':saved}
    path=RAW/'r03-v3-saved-verified.json'
    if path.exists():assert read(path)==result
    else:path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
