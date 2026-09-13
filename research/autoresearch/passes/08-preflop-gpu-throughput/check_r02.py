"""Audit real allocator error, partial-state cleanup and exact recovery witnesses."""
import hashlib,json,re,subprocess
from pathlib import Path
from check_c07 import HERE,LAB,RAW,read,digest

def source(version):
    record=read(RAW/f'r02-partial-allocation-{version}-exit.json')
    mapping={str(Path(k)):v for k,v in read(HERE/f'artifacts/r02-{version}-source-map.json').items()}
    for p,h in record['solver_source_files'].items():
        if p in mapping:assert digest(HERE/mapping[p])==h,p
        else:assert hashlib.sha256(subprocess.check_output(['git','show',record['source_commit']+':'+Path(p).as_posix()],cwd=LAB)).hexdigest()==h,p
    for p,h in record['inputs'].items():assert digest(p)==h,p
    return record

def main():
    failed=source('v1');assert failed['returncode']==101 and failed['reason'] is None
    old=(RAW/'r02-partial-allocation-v1.log').read_text()
    assert 'unwrap_err()` on an `Ok` value' in old and '0 passed; 1 failed' in old
    result=source('v2');assert result['returncode']==0 and result['reason'] is None and result['seconds']<300
    log=(RAW/'r02-partial-allocation-v2.log').read_text();assert '1 passed; 0 failed' in log
    rows=[json.loads(line) for line in re.findall(r'R02_RECOVERY (\{[^\n]+\})',log)]
    assert [r['narrow'] for r in rows]==[False,True]
    for r in rows:
        assert r['exact_rounds']==3
        for k in ['full_arenas_roots_gap_ev_equal','captured_stop_sync_equal','retry_optimized_succeeded','point_lock_and_frozen_seat']:assert r[k] is True,k
        assert r['selection']['mode']=='normal_gpu' and r['selection']['configured_budget_mb']==2000
        assert r['selection']['cohort_limit_mb']==1463
        assert len(r['events'])==1;e=r['events'][0]
        assert e['narrow']==r['narrow'] and e['stage']=='first_extra_values_buffer'
        assert e['value_buffers']==1 and min(e['work_entries'],e['map_entries'],e['value_entries'])>0
        assert e['partial_extra_bytes']==4*(e['work_entries']+e['map_entries']+e['value_entries'])
        assert e['requested_bytes']==2**50 and e['requested_bytes']>e['memory']['total']
        assert 'CUDA_ERROR_OUT_OF_MEMORY' in e['error'] and r['selection']['fallback_reason']==e['error']
        used=r['before']['used'];normal=r['normal_allocation_bytes'];assert normal>0
        assert e['memory']['used']>=used+normal+e['partial_extra_bytes']
        assert r['fallback_memory']['used']==used+normal
        assert r['after_drop']['used']==used and r['after_retry']['used']==used
        for state in ['before','fallback_memory','after_drop','after_retry']:
            assert r[state]['reserved']>=r[state]['used'] and r[state]['total']>=r[state]['free']>0
    suite=read(RAW/'r02-selection-suite-v2-exit.json')
    assert suite['returncode']==0 and suite['reason'] is None and suite['seconds']<240
    assert suite['solver_source_files']==result['solver_source_files']
    assert '3 passed; 0 failed; 1 ignored' in (RAW/'r02-selection-suite-v2.log').read_text()
    for p,h in suite['inputs'].items():assert digest(p)==h,p
    verified=dict(retained=False,status='Qualified - partial GPU allocation recovery',
        versions_archived=['v1','v2'],v1_physical_capacity_assumption_rejected=True,
        actual_cuda_oom=True,partial_allocations_released=True,exact_fallback_and_optimized_retry=True,
        source_input_hashes_verified=True,rows=rows,
        scope='Test-only failure injection. R01 wide and C14 narrow construction share the tested selection/fallback. Production integration and isolated-server qualification remain; no deployment or speed claim.')
    target=RAW/'r02-verified.json'
    if target.exists():assert read(target)==verified
    else:target.write_text(json.dumps(verified,indent=2)+'\n',encoding='utf8')
    print(json.dumps(verified,indent=2))

if __name__=='__main__':main()
