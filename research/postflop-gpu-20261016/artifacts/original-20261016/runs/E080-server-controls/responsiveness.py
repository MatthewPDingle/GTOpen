"""Fixed temporary-server HTTP observation; never sends POST to the live server."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import hashlib,json,math,os,socket,subprocess,sys,time,urllib.request,traceback
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');E=H/'execution';MAIN=Path(P['main']);PORT=P['port'];BASE='http://127.0.0.1:'+str(PORT)
def verify():
    old.custody();old.pin(H/'protocol.json',sys.argv[1])
    for p,h in P['input_sha256'].items():old.pin(p,h)
def port_free():
    with socket.socket()as s:s.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1);s.bind(('127.0.0.1',PORT))
def req(path,body=None,timeout=10,base=BASE):
    assert base in[BASE,old.ar.LIVE]and(body is None or base==BASE)
    data=None if body is None else json.dumps(body).encode();rq=urllib.request.Request(base+path,data=data,headers={'Content-Type':'application/json'})
    t=time.perf_counter_ns()
    with urllib.request.urlopen(rq,timeout=timeout)as response:raw=response.read();code=response.status
    ms=(time.perf_counter_ns()-t)/1e6;return raw,ms,code
def api(path,body=None,timeout=10,base=BASE):return json.loads(req(path,body,timeout,base)[0])
def live():
    old.ar.refuse_active(old.ar.live_status());return{p:api(p,base=old.ar.LIVE)for p in['/api/status','/api/preflop/status','/api/reports/status']}
def listener(proc,binary):
    assert proc.poll()is None
    code="$ls=@(Get-NetTCPConnection -LocalPort "+str(PORT)+" -State Listen -ErrorAction Stop); $p=Get-CimInstance Win32_Process -Filter 'ProcessId="+str(proc.pid)+"'; @{owners=@($ls|Select-Object -ExpandProperty OwningProcess -Unique);pid=$p.ProcessId;path=$p.ExecutablePath;created=$p.CreationDate.ToUniversalTime().ToString('o')} | ConvertTo-Json -Compress"
    v=subprocess.run(['powershell.exe','-NoProfile','-Command',code],capture_output=True,text=True,timeout=20,check=True,creationflags=subprocess.CREATE_NO_WINDOW);j=json.loads(v.stdout);assert j['owners']==[proc.pid]and j['pid']==proc.pid and Path(j['path']).resolve()==binary.resolve();return j
def finite(v):
    if isinstance(v,float):assert math.isfinite(v)
    elif isinstance(v,dict):
        for x in v.values():finite(x)
    elif isinstance(v,list):
        for x in v:finite(x)
def quantile(v,p):v=sorted(v);return v[max(0,math.ceil(len(v)*p)-1)]
verify();assert old.read(H/'build/report.json')['unit_pass_count']==20;assert not E.exists();E.mkdir();rows={};pins={}
for x in old.read(H/'build/report.json')['outputs']:
    old.pin(x['binary'],x['sha256']);old.pin(Path(x['binary']).with_suffix('.manifest.json'),x['manifest_sha256']);pins[x['binary']]=x['sha256']
old.save(H/'HTTP-binary-binding.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'candidate_binaries':pins,'baseline_binary':P['baseline_binary'],'baseline_sha256':P['baseline_binary_sha256'],'HTTP_observations':0})
with old.ar.exclusive_lock(R/'gpu-run.lock'):
    before=live();old.save(E/'live-before.json',before)
    for row in P['order']:
        verify();old.ar.refuse_active(old.ar.live_status());port_free();identity=row['id'];d=E/identity;d.mkdir();binary=Path(P['baseline_binary']if row['arm']=='baseline'else P['output_binary']);old.pin(binary,P['baseline_binary_sha256']if row['arm']=='baseline'else pins[str(binary)]);proc=None;polls=[];result={'id':identity,'arm':row['arm'],'at':old.now(),'passed':False,'binary_sha256':old.sha(binary)}
        try:
            e=old.env();e.update(PORT=str(PORT),SOLVER_GPU='1',SOLVER_COMPRESS='1');e.pop('POSTFLOP_AUTORESEARCH_FIXTURE',None)
            with(d/'stdout.log').open('xb')as out,(d/'stderr.log').open('xb')as err:proc=subprocess.Popen([str(binary)],cwd=MAIN,env=e,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
            old.save(d/'invocation.json',{'at':old.now(),'command':[str(binary)],'cwd':str(MAIN),'PID':proc.pid,'port':PORT,'binary_sha256':old.sha(binary),'environment':{'SOLVER_GPU':'1','SOLVER_COMPRESS':'1','RAYON_NUM_THREADS':'16'},'live_listener_excluded':43735})
            deadline=time.monotonic()+60
            while True:
                assert proc.poll()is None
                try:initial=api('/api/status',timeout=1);break
                except(OSError,TimeoutError):
                    if time.monotonic()>deadline:raise TimeoutError('temporary server readiness60s')
                    time.sleep(.05)
            assert initial['state']=='idle'and initial['tree']is None;result['listener']=listener(proc,binary)
            html,_,_=req('/');assert html==(MAIN/'web/index.html').read_bytes();old.save(d/'initial-status.json',initial)
            def poll(phase,round_index):
                first=None
                for endpoint in P['poll_endpoints']:
                    raw,ms,code=req(endpoint,timeout=P['request_timeout_seconds']);data=json.loads(raw);finite(data);polls.append({'phase':phase,'round':round_index,'endpoint':endpoint,'at':old.now(),'latency_ms':ms,'http_status':code,'response_sha256':hashlib.sha256(raw).hexdigest(),'response':data})
                    if endpoint=='/api/status':first=data
                assert first is not None;return first
            t=time.monotonic();n=0
            with ThreadPoolExecutor(max_workers=1)as pool:
                future=pool.submit(api,'/api/spot',old.read(H/'spot-request.json'),120)
                while not future.done():
                    assert proc.poll()is None;n+=1;poll('build',n);assert time.monotonic()-t<=120;time.sleep(P['poll_interval_ms']/1000)
                tree=future.result()
            result['build_rounds']=n;old.save(d/'tree.json',tree);assert tree['gpu_available']and tree['arena_mb']>64
            old.save(d/'solve-response.json',api('/api/solve',old.read(H/'solve-request.json')));t=time.monotonic();n=0
            while True:
                assert proc.poll()is None;n+=1;status=poll('solve',n)
                if status['state']!='running':break
                assert time.monotonic()-t<=120;time.sleep(P['poll_interval_ms']/1000)
            result['solve_rounds']=n;old.save(d/'final-status.json',status);assert status['state']=='done'and status['gpu']is True and not status['error']and not status['gpu_note']and status['iteration']==200 and len(status['history'])==10
            for label,path in[('root',[]),('child',[{'type':'action','index':0}])]:
                node=api('/api/node',{'path':path},timeout=30);finite(node);assert node['node_type']=='action'and len(node['players'])==2;old.save(d/(label+'-node.json'),node)
            result['science']={k:v for k,v in status.items()if k!='elapsed_secs'};result['tree']=tree;result['node_sha256']={label:old.sha(d/(label+'-node.json'))for label in['root','child']};result['main_UI_bytes_exact']=True;result['passed']=True
        except BaseException as exc:result.update(passed=False,error=repr(exc),traceback=traceback.format_exc())
        finally:
            if proc is not None:
                if proc.poll()is None:proc.terminate()
                try:proc.wait(timeout=10)
                except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=10)
                result['owned_process_stopped']=proc.poll()is not None;result['owned_exit_code']=proc.returncode
            port_free();result['temporary_port_released']=True;old.save(d/'polls.json',polls);old.save(d/'result.json',result)
        assert result['passed'],result;verify();rows[identity]=result;print('Temporary server complete',identity,'build/solve rounds',result['build_rounds'],result['solve_rounds'],flush=True)
    after=live();old.save(E/'live-after.json',after);assert before==after
verify();assert not(R/'gpu-run.lock').exists();guards=P['responsiveness_guards'];checks=[]
def ck(label,v):checks.append({'label':label,'passed':bool(v)});return bool(v)
anchor=rows[P['order'][0]['id']];stats=defaultdict(lambda:defaultdict(list))
for identity,row in rows.items():
    ck(identity+' final full science exact',row['science']==anchor['science']);ck(identity+' full tree exact',row['tree']==anchor['tree']);ck(identity+' full root/child query bytes exact',row['node_sha256']==anchor['node_sha256']);ck(identity+' build sample coverage',row['build_rounds']>=guards['minimum_build_rounds_each']);ck(identity+' solve sample coverage',row['solve_rounds']>=guards['minimum_solve_rounds_each']);ck(identity+' own process stopped',row['owned_process_stopped']and row['temporary_port_released'])
    for sample in old.read(E/identity/'polls.json'):
        ck(identity+' response and absolute latency',sample['http_status']==200 and sample['latency_ms']<=guards['absolute_max_ms']);stats[(sample['phase'],sample['endpoint'])][row['arm']].append(sample['latency_ms'])
derived=[]
for(phase,endpoint),arms in sorted(stats.items()):
    b,c=arms['baseline'],arms['candidate'];bp,cp=quantile(b,.95),quantile(c,.95);bm,cm=max(b),max(c);pl=max(guards['p95_absolute_floor_ms'],bp*guards['p95_relative_ratio']+guards['p95_additive_allowance_ms']);ml=max(guards['max_absolute_floor_ms'],bm*guards['max_relative_ratio']+guards['max_additive_allowance_ms']);passed=ck(phase+' '+endpoint+' p95/max responsiveness',cp<=pl and cm<=ml);derived.append({'phase':phase,'endpoint':endpoint,'baseline_samples':len(b),'candidate_samples':len(c),'baseline_p95_ms':bp,'candidate_p95_ms':cp,'p95_limit_ms':pl,'baseline_max_ms':bm,'candidate_max_ms':cm,'maximum_limit_ms':ml,'passed':passed})
passed=all(x['passed']for x in checks);report={'at':old.now(),'status':'pass_registered_application_responsiveness'if passed else'rejected_application_or_responsiveness','all_checks_pass':passed,'checks':checks,'checks_count':len(checks),'derived':derived,'protocol_sha256':sys.argv[1],'rows':rows,'all_owned_server_processes_terminal':True,'live_API_unchanged':before==after,'source_main_live_unchanged':True,'candidate_adopted':False,'timing_score':False,'limits':'Local temporary-server HTTP poll RTT only during fixed primary rainbow build/init/solve; this does not measure browser rendering/input latency or benchmark speed gains. All six final scientific status records and complete root/child JSON bytes compared exactly, including full convergence history. No save/load/report mutations, source variants, sample exclusions, extensions or primary timing pooling.'};old.save(H/'responsiveness-report.json',report);print(json.dumps({'status':report['status'],'derived':derived,'checks':len(checks)}),flush=True)
