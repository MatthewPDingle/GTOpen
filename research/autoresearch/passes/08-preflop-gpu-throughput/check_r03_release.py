"""Independent final normal-server readiness audit; does not deploy anything."""
import json,re,subprocess,hashlib
from pathlib import Path
from check_r03_saved import HERE,RAW,LAB,read,sha

def main():
    assert read(RAW/'r03-overhead-v3-verified.json')['passed']
    assert read(RAW/'r03-v3-saved-verified.json')['passed']
    source=read(RAW/'r03-selection-tests-v3-exit.json')['solver_source_files']
    mapping={str(Path(k)):v for k,v in read(HERE/'artifacts/r03-v3-source-map.json').items()}
    for f,h in source.items():
        if f in mapping:assert sha(HERE/mapping[f])==h,f
        else:assert hashlib.sha256(subprocess.check_output(['git','show','db358c8:'+Path(f).as_posix()],cwd=LAB)).hexdigest()==h,f
    stages={}
    for stage,count in [('native',20),('default',181),('server-tests',20),('server-build',None),('server-live',None)]:
        name=f'r03-{stage}-v3';r=read(RAW/(name+'-exit.json'))
        assert r['returncode']==0 and r['reason'] is None and r['seconds']<(600 if stage=='server-live' else 300)
        assert r['solver_source_files']==source
        for f,h in r['inputs'].items():assert sha(f)==h,f
        assert not any('preflop-research' in x for x in r['command'])
        if count is not None:
            found=sum(map(int,re.findall(r'test result: ok\. (\d+) passed;',(RAW/(name+'.log')).read_text())))
            assert found==count,(stage,found)
        if stage.startswith('server'):
            f=str(LAB/'crates/server/src/main.rs')
            assert r['inputs'][f]==sha(HERE/mapping[str(Path('crates/server/src/main.rs'))])
        stages[stage]={'passed':True,'tests':count,'seconds':r['seconds']}
    live=read(RAW/'r03-server-live-v3.json');assert live['passed'] and live['owned_port_closed'] and live['port']==56710
    assert live['web_served'] and live['initial_other_endpoints']==live['final_other_endpoints']
    assert live['executable_sha256']==sha(LAB/'target/r03-v3-server-frozen.exe')
    for fixture,age in [('small',1000),('large',1050)]:
        x=live['fixtures'][fixture];old=read(RAW/f'r03-{fixture}-retained-v1.json')
        assert x['loaded']['iteration']==age and x['loaded']['multiway_equity_model']=='coupled_deck_v1'
        assert x['six']['iteration']==age+6 and x['seven']['iteration']==age+7
        assert x['six']['gaps']==old['rows'][-1]['gaps'] and x['six']['evs']==old['rows'][-1]['evs']
        assert x['seven']['gaps']==old['continued_gaps'] and x['seven']['evs']==old['continued_evs']
        for state in ['six','seven','resumed']:
            assert x[state]['state']=='done' and x[state]['gpu'] and x[state]['gpu_note']=='Shared GPU evaluation'
            assert x[state]['accuracy_iteration']==x[state]['published_iteration']==x[state]['iteration']
        assert x['root_publication']['published_iteration']==age+6
        assert x['observed_active']['state']=='running' and x['observed_active']['iteration']>age+7
        assert x['stopped']['state']=='stopped' and x['stopped']['gpu']
        assert x['resumed']['iteration']==x['interrupted']['iteration']+1
        for name in ['six_save','seven_save','interrupted','resume_a','resume_b']:
            save=x[name];assert Path(save['path']).resolve().is_relative_to(Path(live['root']).resolve())
            assert sha(save['path'])==save['sha256']
        assert x['six_save']['sha256']==sha(old['save'])
        assert x['resume_a']['sha256']==x['resume_b']['sha256']
        assert x['exact_saved_reference'] and x['exact_resume_replay']
    result={'passed':True,'status':'Ready for a separately authorized 56708 switch','deployed':False,
        'stages':stages,'executable':live['executable'],'executable_sha256':live['executable_sha256'],
        'source_input_executable_hashes_checked':True,'exact_saved_continuation_and_stop_resume':True,
        'integration_overhead':read(RAW/'r03-overhead-v3-verified.json')['fixtures'],
        'scope':'Production integration of retained C01+C07+C09+C14. No new speed claim or convergence improvement.'}
    path=RAW/'r03-release-verified.json'
    if path.exists():assert read(path)==result
    else:path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
