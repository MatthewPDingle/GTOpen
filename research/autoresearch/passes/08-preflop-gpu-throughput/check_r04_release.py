"""Final release-readiness audit, independent of the isolated harness asserts."""
import hashlib,json,re,socket
from pathlib import Path
from run_c23 import HERE,RAW,read,run07

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    initial=read(RAW/'r04-initial-verified.json');overhead=read(RAW/'r04-overhead-verified.json');saved=read(RAW/'r04-saved-verified.json')
    assert initial['verified'] and overhead['passed'] and saved['passed']
    for p,h in initial['solver_source_files'].items():assert sha(run07.LAB/p)==h,p
    runs={};counts={}
    for stage,count in [('native',20),('default',181),('server-tests',20),('server-build',None),('server-live',None)]:
        name='r04-'+stage+'-v1';r=read(RAW/(name+'-exit.json'))
        assert r['returncode']==0 and r['reason'] is None and r['seconds']<=(480 if stage=='server-live' else 300)
        assert r['solver_source_files']==initial['solver_source_files']
        for p,h in r['inputs'].items():assert sha(p)==h,p
        if count is not None:
            log=(RAW/(name+'.log')).read_text(encoding='utf-8')
            parsed=re.findall(r'test result: ok\. (\d+) passed; (\d+) failed;',log)
            assert parsed and all(int(f)==0 for _,f in parsed)
            assert sum(int(p) for p,_ in parsed)==count
            counts[stage]=count
        runs[stage]={'seconds':r['seconds'],'exit_sha256':sha(RAW/(name+'-exit.json'))}
    frozen=read(RAW/'r04-server-frozen.json');assert sha(frozen['path'])==frozen['sha256']
    server=read(RAW/'r04-server-live-v1.json')
    assert server['passed'] and server['port']==56710 and server['owned_port_closed']
    assert server['executable_sha256']==frozen['sha256'] and server['web_served']
    assert server['initial_other_endpoints']==server['final_other_endpoints']
    assert server['initial_other_endpoints']['postflop']['state']=='idle'
    assert len(server['static_cdf_selections'])==10
    for selection in server['static_cdf_selections']:
        assert selection['static_cdf'] and selection['narrow_offsets'] and selection['mode']=='retained_cohorts'
        assert selection['fallback_reason'] is None and selection['static_cdf_fallback_reason'] is None
    for fixture,age in [('small',1000),('large',1050)]:
        row=server['fixtures'][fixture];reference=read(RAW/f'r03-{fixture}-retained-v1.json')
        assert row['loaded']['iteration']==age and row['six']['iteration']==age+6 and row['seven']['iteration']==age+7
        assert row['six']['gaps']==reference['rows'][-1]['gaps'] and row['six']['evs']==reference['rows'][-1]['evs']
        assert row['seven']['gaps']==reference['continued_gaps'] and row['seven']['evs']==reference['continued_evs']
        assert row['six_save']['sha256']==sha(row['six_save']['path'])==saved['saved'][fixture]['saved_sha256']
        assert row['observed_active']['state']=='running' and row['observed_active']['iteration']>age+7
        assert row['stopped']['state']=='stopped' and row['stopped']['gpu']
        assert row['resume_a']['sha256']==row['resume_b']['sha256']==sha(row['resume_a']['path'])==sha(row['resume_b']['path'])
        assert row['exact_saved_reference'] and row['exact_resume_replay']
    with socket.socket() as probe:assert probe.connect_ex(('127.0.0.1',56710))!=0
    result={'verified':True,'ready_for_deployment':True,'retained':False,'admitted':True,'deployed':False,
        'status':'R04 release ready; 56708 remains R03',
        'server_sha256':frozen['sha256'],'server_executable':frozen['path'],
        'regression_tests':counts,'initial_integration_tests':13,'runs':runs,
        'overhead_median_ratios':{k:v['median_ratio'] for k,v in overhead['fixtures'].items()},
        'exact_checkpoints_and_arena':True,'saved_continuation_exact':True,'live_stop_reload_replay_exact':True,
        'static_tables_selected_on_all_ten_server_solves':True,'isolated_server_closed':True,
        'scope':'Normal-build integration and isolated server qualified. Deployment is separate; no new convergence or 10x claim.'}
    dest=RAW/'r04-release-verified.json'
    if dest.exists():assert read(dest)==result
    else:dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (RAW/'r04-verified.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
