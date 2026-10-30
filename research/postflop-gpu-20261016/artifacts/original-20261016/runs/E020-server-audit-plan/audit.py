"""File-only terminal E020 server audit. No subprocess, network, native or GPU calls."""
from pathlib import Path
import datetime,hashlib,json,math,re,sys
ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
IMPL=ROOT/'runs/E020-server-implementation'
BUILD=ROOT/'runs/E020-server-build'
UNIT=ROOT/'runs/V020-server-unit'
SMOKE=ROOT/'runs/E020-server-smoke'
OUT=ROOT/'comparisons/E020-server-qualification'
REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
MAIN=Path(r'X:\Dev\GTOpen')
PINS={}
def sha(p):
    p=Path(p);h=hashlib.sha256()
    with p.open('rb') as f:
        while block:=f.read(1024*1024):h.update(block)
    PINS[str(p)]=h.hexdigest();return h.hexdigest()
def read(p):sha(p);return json.loads(Path(p).read_text(encoding='utf-8'))
def pin(r):assert sha(r['path'])==r['sha256'];return Path(r['path'])
def save(p,data):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(data,f,indent=2,allow_nan=False);f.write('\n')
def finite(v):
    if isinstance(v,float):assert math.isfinite(v)
    elif isinstance(v,dict):
        for x in v.values():finite(x)
    elif isinstance(v,list):
        for x in v:finite(x)
def node(v):
    finite(v);assert v['node_type']=='action' and len(v['board'])==5 and v['actions'] and len(v['players'])==2
    actor=v['player'];count=0;error=0.0
    for player in v['players']:
        assert player['hands']
        for hand in player['hands']:
            if hand['reach']>0 and hand['valid']>0:assert isinstance(hand['ev'],(int,float)) and isinstance(hand['eq'],(int,float))
    for hand in v['players'][actor]['hands']:
        strategy=hand['strategy'];assert len(strategy)==len(v['actions']) and all(-1e-7<=x<=1.0000001 for x in strategy)
        delta=abs(sum(strategy)-1);assert delta<1e-5;error=max(error,delta);count+=1
    assert count>0
    return {'acting_hands_checked':count,'max_strategy_sum_error':error,'actions':[a['label'] for a in v['actions']],'player':actor}
def run():
    assert sha(IMPL/'prepared-manifest.json')=='99ded8f3ce4f3c0671e0b405c7fcd3f256133825e863dcc4788c91ad99ee7e5b'
    prep=read(IMPL/'prepared-manifest.json')
    for n,h in prep['artifact_sha256'].items():assert sha(IMPL/n)==h,n
    for n,h in prep['nvrtc_dll_sha256'].items():assert sha(MAIN/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin'/n)==h,n
    source=read(IMPL/'source-pins.json');assert len(source)==168
    for n,h in source.items():assert sha(REPO/n)==h,n
    ap=ROOT/'comparisons/E020-qualification/report.json';assert sha(ap)=='32ccca351c6bee424b183db7afc39fd922b3b0d751f6b0b7ff3c3b5768c6e304'
    accepted=read(ap);assert accepted['id']=='E020' and accepted['status']=='validated' and accepted['deployed'] is False
    assert accepted['binary_source_sha256']=={k:v for k,v in source.items() if not k.startswith('crates/server/')}
    assert accepted['source_sha256']=={k:source[k] for k in ['crates/solver/src/gpu/kernels.cu','crates/solver/src/gpu/mod.rs']}
    for n,h in accepted['compiled_shared_source_sha256'].items():assert sha(MAIN/n)==sha(REPO/n)==h
    for phase in ['build','smoke']:
        auth=read(IMPL/(phase+'-authorization.json'));assert auth['candidate']=='E020' and auth['phase']==phase and auth['independent_source_review_pass'] is True and auth['live_deployment_authorized'] is False
        assert auth['prepared_manifest_sha256']==sha(IMPL/'prepared-manifest.json') and pin(auth['acceptance'])==ap
        for record in auth['required_evidence']:pin(record)
    live=read(IMPL/'live-exclusion.json');assert live['pid']==37268 and live['port']==43735 and sha(live['executable'])==live['sha256']
    br=read(BUILD/'report.json');assert br['status']=='pass' and br['source_unchanged'] is True and br['tests_executed']==0 and br['server_launched'] is False and br['live_executable_touched'] is False
    started=read(BUILD/'started.json');assert started['authorization_sha256']==sha(IMPL/'build-authorization.json') and started['source_sha256']==source and started['target_previously_absent'] is True
    binaries={}
    for index,name in enumerate(['E020-gto-server','E020-server-tests']):
        d=BUILD/str(index);e=read(d/'exit.json');assert e['returncode']==0 and e['error'] is None and e['cleanup'] is None
        invocation=read(d/'invocation.json');assert invocation['cwd']==str(REPO) and invocation['compiler_override_absence_checked'] is True
        b=ROOT/'binaries'/(name+'.exe');mp=b.with_suffix('.manifest.json');m=read(mp)
        assert m['candidate']=='E020' and m['source_sha256']==source and m['source_matches_prebuild'] is True and m['source_commit']==accepted['research_commit']
        assert m['binary_sha256']==sha(b) and m['prepared_manifest_sha256']==sha(IMPL/'prepared-manifest.json')
        assert m['live_executable_touched'] is False and b.resolve()!=Path(live['executable']).resolve() and sha(b)!=live['sha256']
        assert pin(m['acceptance'])==ap and m['command']==invocation['args']
        assert m['build_log_sha256']==sha(d/'stdout.jsonl') and m['build_stderr_sha256']==sha(d/'stderr.log')
        rows=[json.loads(x) for x in (d/'stdout.jsonl').read_text(encoding='utf-8').splitlines()]
        assert any(x.get('reason')=='build-finished' and x.get('success') is True for x in rows)
        item=m['cargo_artifact'];assert item in rows and item['target']['name']=='gto-server' and item['profile']['test']==bool(index) and item['fresh'] is False
        target=ROOT/'build-server-e020';assert Path(item['executable']).resolve().is_relative_to(target.resolve()) and sha(item['executable'])==sha(b)
        assert Path(item['manifest_path'])==REPO/'crates/server/Cargo.toml'
        solver=m['solver_artifact'];assert solver in rows
        if index==0:assert solver['fresh'] is False
        for artifact in rows:
            if artifact.get('reason')=='compiler-artifact':
                for path in artifact.get('filenames',[]):assert Path(path).resolve().is_relative_to(target.resolve())
        for path,h in m['dependency_sha256'].items():assert sha(path)==h
        data=b.read_bytes();counts={role:data.count((IMPL/(role+'-kernels.cu')).read_bytes()) for role in ['E015','E020']}
        assert counts['E020']>0 and counts['E015']==0 and counts==m['embedded_cuda_occurrences']
        matches=[r for r in br['outputs'] if r['path']==str(b)];assert len(matches)==1 and matches[0]['sha256']==sha(b) and matches[0]['manifest_sha256']==sha(mp)
        binaries[name]={'path':str(b),'sha256':sha(b),'manifest_sha256':sha(mp),'embedded_cuda':counts}
    unit=read(UNIT/'report.json');raw=UNIT/'stdout.log';assert sha(raw)==unit['stdout_sha256']
    text=raw.read_text(encoding='utf-8');assert unit['status']=='measured' and unit['returncode']==0 and unit['test_pass_count']==20
    assert unit['binary_sha256']==binaries['E020-server-tests']['sha256']
    assert unit['command']==[binaries['E020-server-tests']['path'],'--nocapture','--test-threads=1']
    assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',text)==[('20','0','1','0','0')]
    inventory=read(IMPL/'unit-inventory.json');assert sorted(re.findall(r'^test ([\w:]+) \.\.\.',text,re.M))==inventory['expected_test_names']
    assert 'test report_tests::report_adaptation_benchmark ... ignored' in text and 'FAILED' not in text
    sr=read(SMOKE/'result.json');launch=read(SMOKE/'launch.json');auth=read(IMPL/'smoke-authorization.json')
    assert sr['passed'] is True and sr['port']==43736 and sr['authorization_sha256']==sha(IMPL/'smoke-authorization.json')
    assert sr['binary']==binaries['E020-gto-server']['path'] and sr['binary_sha256']==binaries['E020-gto-server']['sha256'] and sr['manifest_sha256']==binaries['E020-gto-server']['manifest_sha256']
    assert auth['server_binary_sha256']==sr['binary_sha256'] and auth['server_manifest_sha256']==sr['manifest_sha256'] and pin(auth['server_unit_report'])==UNIT/'report.json'
    assert sr['owned_process_stopped'] is True and sr['test_port_released'] is True and sr['live_api_unchanged'] is True
    assert sr['owned_pid']==launch['owned_pid']!=live['pid'] and int((SMOKE/'server.pid').read_text())==sr['owned_pid']
    identity=sr['listener_identity'];assert identity['pid']==sr['owned_pid'] and identity['listeners']==[sr['owned_pid']] and Path(identity['path'])==Path(sr['binary'])
    assert launch['live_exclusion']==live and launch['environment']=={'PORT':'43736','SOLVER_GPU':'1','SOLVER_COMPRESS':'1','RAYON_NUM_THREADS':'16','NVRTC':str(MAIN/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')}
    assert isinstance(sr['owned_process_exit_code'],int) and not any(k in sr for k in ['error','cleanup_error','final_verification_error'])
    assert read(SMOKE/'live-before.json')==read(SMOKE/'live-after.json')
    initial=read(SMOKE/'initial-status.json');assert initial['state']=='idle' and initial['tree'] is None
    for f in ['spot-request.json','solve-request.json']:assert read(SMOKE/f)==read(IMPL/f)
    status=read(SMOKE/'final-status.json');finite(status);assert status==sr['final_status'] and status['state']=='done' and status['iteration']==100 and status['gpu'] is True and not status['error'] and not status['gpu_note']
    polls=read(SMOKE/'status-polls.json');assert polls and polls[-1]['status']==status;finite(polls)
    root_check=node(read(SMOKE/'root-node.json'));child_check=node(read(SMOKE/'check-child-node.json'))
    assert root_check==sr['root_checks'] and child_check==sr['child_checks']
    assert datetime.datetime.fromisoformat(br['at'])<datetime.datetime.fromisoformat(unit['process_started_at'].replace('Z','+00:00'))
    assert datetime.datetime.fromisoformat(unit['finished_at'].replace('Z','+00:00'))<datetime.datetime.fromisoformat(sr['started_at'])<datetime.datetime.fromisoformat(sr['finished_at'])
    for folder in [BUILD,SMOKE]:assert not list(folder.rglob('failure.json'))
    for f in SMOKE.iterdir():
        if f.is_file():sha(f)
    return {'id':'E020-server-qualification','candidate_id':'E020','status':'pass','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Isolated server integration only; no performance, deployment or universal accuracy claim','acceptance_sha256':sha(ap),'prepared_manifest_sha256':sha(IMPL/'prepared-manifest.json'),'source_files_verified':168,'binaries':binaries,'unit_tests':{'passed':20,'failed':0,'ignored':1,'measured':0,'filtered_out':0,'inventory_exact':True},'smoke':{'iterations':100,'gpu':True,'root_checks':root_check,'child_checks':child_check,'owned_pid':sr['owned_pid'],'owned_process_stopped':True,'test_port_released':True,'live_unchanged':True},'deployment_changed':False,'deployed':False,'live_deployment_remains_blocked':True,'prerequisite_for_next_research_candidate':True}
def main():
    assert not OUT.exists();OUT.mkdir()
    try:
        report=run();save(OUT/'inputs.json',PINS);report['inputs_sha256']=sha(OUT/'inputs.json');report['audit_source_sha256']=sha(Path(__file__))
        save(OUT/'report.json',report);save(OUT/'manifest.json',{'id':'E020-server-qualification','status':'pass','report_sha256':sha(OUT/'report.json'),'inputs_sha256':sha(OUT/'inputs.json'),'audit_source_sha256':sha(Path(__file__)),'audit_native_executions':0,'audit_gpu_jobs':0})
        print(json.dumps({'status':'pass','report':str(OUT/'report.json'),'sha256':sha(OUT/'report.json'),'unit_passed':20,'unit_ignored':1,'gpu_iterations':100,'live_unchanged':True}))
    except BaseException as exc:
        save(OUT/'failure.json',{'status':'failed','error':repr(exc),'checked_input_sha256':PINS,'no_native_execution_by_audit':True});raise
if __name__=='__main__':main()
