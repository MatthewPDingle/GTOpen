"""Own an isolated normal-feature server; never send mutations to port 56708."""
import hashlib,json,os,re,shutil,socket,subprocess,time,urllib.request
from pathlib import Path

HERE=Path(__file__).resolve().parent;LAB=HERE.parents[3];RAW=HERE/'raw'
PORT=56710;BASE=f'http://127.0.0.1:{PORT}'
ROOT=LAB/'target/r05-server-qualification-v1'
EXE=LAB/'target/r05-server-frozen.exe'
OUT=RAW/'r05-server-live-v1.json'

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def read(path):return json.loads(Path(path).read_text(encoding='utf8'))

def api(route,body=None,timeout=90):
    assert route.startswith('/api/') and PORT!=56708
    request=urllib.request.Request(BASE+route,data=None if body is None else json.dumps(body).encode(),
        headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(request,timeout=timeout) as response:return json.load(response)

def finished(child,timeout=150):
    until=time.monotonic()+timeout
    while time.monotonic()<until:
        assert child.poll() is None,'isolated server exited'
        state=api('/api/preflop/status',timeout=8)
        assert not state['error'],state
        if state['state']!='running':return state
        time.sleep(.2)
    raise TimeoutError('isolated solve did not finish within its cap')

def solve(child,count):
    api('/api/preflop/solve',{'iterations':count,'check_every':1,'target_gap':0})
    state=finished(child)
    assert state['state']=='done' and state['gpu'] and state['gpu_note']=='Shared GPU evaluation',state
    assert state['accuracy_iteration']==state['published_iteration']==state['iteration']
    return state

def save(name):
    result=api('/api/preflop/save',{'name':name});assert result['ok']
    path=ROOT/'saves/preflop'/f'{name}.gtop';assert path.resolve().is_relative_to(ROOT.resolve())
    return {'path':str(path),'sha256':sha(path),'iteration':result['iteration']}

def main():
    assert ROOT.resolve().is_relative_to((LAB/'target').resolve()) and not ROOT.exists() and not OUT.exists()
    with socket.socket() as check:check.bind(('127.0.0.1',PORT))
    assert EXE.is_file()
    (ROOT/'cache').mkdir(parents=True);(ROOT/'saves/preflop').mkdir(parents=True)
    for name in ['preflop_eq169.bin','realization_fit.json']:
        shutil.copyfile(LAB/'cache'/name,ROOT/'cache'/name)
    shutil.copytree(LAB/'web',ROOT/'web')
    sources={
        'small':LAB/'target/convergence/behavioral-fixed-e0-v1/final.gtop',
        'large':LAB/'target/convergence/eight-native-a/final.gtop',
    }
    original={k:sha(v) for k,v in sources.items()}
    for fixture,path in sources.items():shutil.copyfile(path,ROOT/'saves/preflop'/f'r05-{fixture}-source.gtop')
    env=os.environ.copy();env.update(PORT=str(PORT),SOLVER_GPU='1',SOLVER_GPU_MEM_MB='23000',SOLVER_THREADS='8',
        PREFLOP_EQ_SAMPLES=str(int.from_bytes((ROOT/'cache/preflop_eq169.bin').read_bytes()[:4],'little')),
        REALIZATION_FIT=str(ROOT/'cache/realization_fit.json'))
    log_path=RAW/'r05-server-live-v1-server.log';result={'port':PORT,'root':str(ROOT),'executable':str(EXE),'executable_sha256':sha(EXE),'fixtures':{},'original_hashes':original}
    child=None
    try:
        with log_path.open('x',encoding='utf8') as log:
            child=subprocess.Popen([str(EXE)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            result['pid']=child.pid;until=time.monotonic()+20
            while True:
                assert child.poll() is None,'isolated startup failed'
                try:
                    if api('/api/status',timeout=1)['state']=='idle':break
                except OSError:
                    if time.monotonic()>until:raise
                    time.sleep(.1)
            with urllib.request.urlopen(BASE+'/',timeout=5) as response:
                page=response.read().decode('utf8');assert 'GTOpen' in page
                assert 'no-cache' in response.headers.get('Cache-Control','')
            result['web_served']=True
            result['initial_other_endpoints']={'postflop':api('/api/status'),'reports':api('/api/reports/status'),'library':api('/api/reports')}
            for fixture,age in [('small',1000),('large',1050)]:
                fixture_started=time.monotonic()
                old=read(RAW/f'r03-{fixture}-retained-v1.json')
                loaded=api('/api/preflop/load',{'name':f'r05-{fixture}-source'})
                assert loaded['iteration']==age and loaded['nodes']==old['nodes']
                assert loaded['multiway_equity_model']=='coupled_deck_v1'
                six=solve(child,6);assert six['iteration']==age+6
                assert six['gaps']==old['rows'][-1]['gaps'] and six['evs']==old['rows'][-1]['evs']
                node=api('/api/preflop/node',{'path':[]})
                assert node['publication']['published_iteration']==age+6
                six_save=save(f'r05-{fixture}-six')
                assert six_save['sha256']==sha(old['save'])
                reloaded=api('/api/preflop/load',{'name':f'r05-{fixture}-six'})
                assert reloaded['iteration']==age+6 and reloaded['config']==loaded['config'] and reloaded['seats']==loaded['seats']
                seven=solve(child,1);assert seven['iteration']==age+7
                assert seven['gaps']==old['continued_gaps'] and seven['evs']==old['continued_evs']
                seven_save=save(f'r05-{fixture}-seven')
                # Stop after an actual completed sweep, while further work is active.
                api('/api/preflop/solve',{'iterations':1000,'check_every':50,'target_gap':0})
                until=time.monotonic()+25
                while True:
                    active=api('/api/preflop/status',timeout=8)
                    assert active['state']=='running' and not active['error'],active
                    if active['phase']=='iterating' and active['iteration']>age+7:break
                    assert time.monotonic()<until,'no live iteration observed before stop'
                    time.sleep(.05)
                api('/api/preflop/stop',{})
                stopped=finished(child,30);assert stopped['state']=='stopped' and stopped['gpu']
                interrupted=save(f'r05-{fixture}-interrupted')
                resumed=solve(child,1);resume_a=save(f'r05-{fixture}-resume-a')
                api('/api/preflop/load',{'name':f'r05-{fixture}-interrupted'})
                replay=solve(child,1);resume_b=save(f'r05-{fixture}-resume-b')
                for key in ['iteration','gaps','evs']:assert replay[key]==resumed[key],key
                assert resume_a['sha256']==resume_b['sha256']
                result['fixtures'][fixture]={'loaded':loaded,'six':six,'six_save':six_save,'seven':seven,'seven_save':seven_save,
                    'observed_active':active,'stopped':stopped,'interrupted':interrupted,'resumed':resumed,'resume_a':resume_a,'resume_b':resume_b,
                    'root_publication':node['publication'],'exact_saved_reference':True,'exact_resume_replay':True}
                assert time.monotonic()-fixture_started <= 180, 'fixture exceeded registered cap'
                print(json.dumps({'fixture':fixture,'server_qualification':'passed','six_iteration':six['iteration'],'stopped_iteration':stopped['iteration']}),flush=True)
            result['final_other_endpoints']={'postflop':api('/api/status'),'reports':api('/api/reports/status'),'library':api('/api/reports')}
            assert result['initial_other_endpoints']==result['final_other_endpoints']
            assert {k:sha(v) for k,v in sources.items()}==original
            log.flush()
            selected=[json.loads(x) for x in re.findall(r'preflop solving on GPU: (\{[^\n]+\})',log_path.read_text(encoding='utf8'))]
            assert len(selected)==10, len(selected)
            assert all(s['static_cdf'] and s['narrow_offsets'] and s['mode']=='retained_cohorts' and s['fallback_reason'] is None and s['static_cdf_fallback_reason'] is None for s in selected)
            result['static_cdf_selections']=selected
            result['passed']=True
    except Exception as error:
        result['passed']=False;result['error']=repr(error);raise
    finally:
        if child is not None:
            if child.poll() is None:child.terminate()
            result['owned_server_exit']=child.wait(timeout=15)
        with socket.socket() as check:result['owned_port_closed']=check.connect_ex(('127.0.0.1',PORT))!=0
        OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')

if __name__=='__main__':main()
