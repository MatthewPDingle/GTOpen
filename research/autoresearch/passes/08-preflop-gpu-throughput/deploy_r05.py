"""User-authorized R05 switch; preserve sessions and verify binary identity."""
import ctypes as c,hashlib,json,os,re,shutil,struct,subprocess,sys,time,urllib.request
from ctypes import wintypes as w
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parents[3];BASE='http://127.0.0.1:56708'
EXE=LAB/'target/r05-server-frozen.exe';EXPECTED='b0f68de9d162d6dea1a30027075ae41443e34fa74f8ade328ca2cccc58ed8260'
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def put(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def api(route,body=None,timeout=180):
    req=urllib.request.Request(BASE+route,data=None if body is None else json.dumps(body).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=timeout) as r:return json.load(r)
def identity():
    script="$n=Get-NetTCPConnection -LocalPort 56708 -State Listen -ErrorAction Stop; if (@($n).Count -ne 1) {throw 'ambiguous listener'}; Get-CimInstance Win32_Process -Filter ('ProcessId='+$n.OwningProcess) | Select-Object ProcessId,ExecutablePath,CommandLine | ConvertTo-Json -Compress"
    return json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',script],text=True))
def context(pid):
    # Read only the target's process parameters, retaining application launch keys.
    k=c.WinDLL('kernel32',use_last_error=True);nt=c.WinDLL('ntdll')
    k.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD];k.OpenProcess.restype=w.HANDLE
    k.ReadProcessMemory.argtypes=[w.HANDLE,c.c_void_p,c.c_void_p,c.c_size_t,c.POINTER(c.c_size_t)];k.ReadProcessMemory.restype=w.BOOL
    k.CloseHandle.argtypes=[w.HANDLE];nt.NtQueryInformationProcess.argtypes=[w.HANDLE,w.ULONG,c.c_void_p,w.ULONG,c.c_void_p];nt.NtQueryInformationProcess.restype=c.c_long
    h=k.OpenProcess(0x1010,False,pid);assert h
    def mem(at,n):
        b=c.create_string_buffer(n);got=c.c_size_t();assert k.ReadProcessMemory(h,at,b,n,c.byref(got)),c.get_last_error();assert got.value==n;return b.raw
    def ptr(at):return struct.unpack('<Q',mem(at,8))[0]
    def string(at):
        b=mem(at,16);n=struct.unpack_from('<H',b)[0];address=struct.unpack_from('<Q',b,8)[0];return mem(address,n).decode('utf-16-le')
    try:
        info=c.create_string_buffer(48);assert nt.NtQueryInformationProcess(h,0,info,48,None)==0
        peb=struct.unpack_from('<Q',info.raw,8)[0];params=ptr(peb+0x20);cwd=string(params+0x38);envptr=ptr(params+0x80)
        data=b''
        for i in range(0,1024*1024,256):
            data+=mem(envptr+i,256)
            text=data.decode('utf-16-le')
            if '\0\0' in text:break
        else:raise RuntimeError('environment terminator missing')
        env={}
        for item in text.split('\0\0',1)[0].split('\0'):
            if '=' not in item or item.startswith('='):continue
            key,value=item.split('=',1)
            if re.match(r'^(SOLVER_|PREFLOP_|GTO|RAYON_|CUDA|REALIZATION_FIT$|PORT$|PATH$)',key,re.I):env[key]=value
        return dict(cwd=cwd,environment=env)
    finally:k.CloseHandle(h)
def idle():
    x={k:api(v,timeout=10) for k,v in [('preflop','/api/preflop/status'),('postflop','/api/status'),('reports','/api/reports/status')]}
    assert x['preflop']['state']!='running' and x['postflop']['state']!='running' and not x['reports']['running'],'user work active'
    return x
def snapshot():
    return dict(status=idle(),session=api('/api/preflop/session'),preflop=api('/api/preflop/node',{'path':[]}),
        postflop=api('/api/node',{'path':[]}),locks=api('/api/locks'),reports=api('/api/reports'),profiles=api('/api/preflop/profiles'))
def inventory(root):
    files=list((root/'saves/reports').rglob('*'))+[p for p in (root/'cache').glob('*.json')]
    return {str(p.relative_to(root)):sha(p) for p in files if p.is_file()}
def prepare(root):
    assert not root.exists();root.mkdir(parents=True);assert sha(EXE)==EXPECTED
    who=identity();ctx=context(who['ProcessId']);app=Path(ctx['cwd']);assert app.is_dir()
    record=dict(old=who,launch=ctx,candidate=str(EXE),candidate_sha256=EXPECTED,backup=str(root),prepared=False)
    put(root/'deployment.json',record);print(json.dumps(dict(phase='capturing',pid=who['ProcessId'],cwd=str(app))),flush=True)
    before=snapshot();put(root/'before.json',before);put(root/'inventory-before.json',inventory(app))
    name='before-r05-'+time.strftime('%Y%m%d-%H%M%S');record['name']=name
    print('Saving preflop session',flush=True);assert api('/api/preflop/save',{'name':name})['ok']
    print('Saving postflop session',flush=True);assert api('/api/save',{'name':name})['ok']
    copies={}
    for label,path in [('preflop',app/'saves/preflop'/f'{name}.gtop'),('postflop',app/'saves'/f'{name}.gto'),('old_binary',Path(who['ExecutablePath'])),('candidate',EXE)]:
        dest=root/(label+path.suffix);shutil.copyfile(path,dest);copies[label]=dict(source=str(path),backup=str(dest),sha256=sha(dest));assert sha(path)==copies[label]['sha256']
    assert identity()==who;idle();assert snapshot()['session']==before['session'];record.update(prepared=True,copies=copies)
    put(root/'deployment.json',record);print(json.dumps(dict(phase='prepared',backup=str(root),name=name)),flush=True)
def launch(record,exe,root,label):
    env=os.environ.copy()
    for key in list(env):
        if re.match(r'^(SOLVER_|PREFLOP_|GTO|RAYON_|CUDA|REALIZATION_FIT$|PORT$)',key,re.I):env.pop(key)
    env.update(record['launch']['environment']);assert env.get('PORT')=='56708',env.get('PORT')
    with (root/(label+'.log')).open('xb') as log:
        child=subprocess.Popen([str(exe)],cwd=record['launch']['cwd'],env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    put(root/(label+'-process.json'),dict(pid=child.pid,executable=str(exe),sha256=sha(exe)))
    until=time.monotonic()+30
    while time.monotonic()<until:
        assert child.poll() is None,'server exited'
        try:
            api('/api/status',timeout=1);assert identity()['ProcessId']==child.pid;return child
        except (OSError,subprocess.CalledProcessError):time.sleep(.2)
    raise TimeoutError('server startup')
def verify(root):
    record=read(root/'deployment.json');before=read(root/'before.json');after=snapshot();put(root/'after.json',after)
    # Loading resets transient publication/engine/progress labels, never saved play.
    for k in ['config','nodes','action_nodes','arena_mb','iteration','seats','hero','frozen','multiway_equity_model']:
        assert before['session'][k]==after['session'][k],('session',k)
    a=dict(before['preflop']);b=dict(after['preflop']);a.pop('publication',None);b.pop('publication',None);assert a==b,'preflop root differs'
    assert before['postflop']==after['postflop'],'postflop root differs'
    for k in ['locks','reports','profiles']:assert before[k]==after[k],k
    for k in ['iteration','spot_request','tree']:assert before['status']['postflop'][k]==after['status']['postflop'][k],('postflop status',k)
    assert inventory(Path(record['launch']['cwd']))==read(root/'inventory-before.json'),'library files differ'
    with urllib.request.urlopen(BASE+'/',timeout=5) as r:assert 'GTOpen' in r.read().decode();assert 'no-cache' in r.headers.get('Cache-Control','')
    return after
def switch(root):
    record=read(root/'deployment.json');assert record['prepared'];assert identity()==record['old'];assert sha(EXE)==EXPECTED
    for copy in record['copies'].values():assert sha(copy['backup'])==copy['sha256'] and sha(copy['source'])==copy['sha256']
    before=read(root/'before.json');assert snapshot()==before,'state changed since backup';idle()
    print('Stopping verified old server',flush=True)
    subprocess.run(['powershell','-NoProfile','-Command',f"Stop-Process -Id {record['old']['ProcessId']} -ErrorAction Stop"],check=True)
    child=None
    try:
        print('Starting qualified R05',flush=True);child=launch(record,EXE,root,'r05')
        print('Restoring preflop',flush=True);api('/api/preflop/load',{'name':record['name']})
        print('Restoring postflop',flush=True);api('/api/load',{'name':record['name']})
        after=verify(root);who=identity();assert who['ProcessId']==child.pid and sha(who['ExecutablePath'])==EXPECTED
        record.update(deployed=True,new=who,verified=True);put(root/'deployment.json',record)
        print(json.dumps(dict(deployed=True,pid=child.pid,preflop_iteration=after['session']['iteration'],postflop_iteration=after['status']['postflop']['iteration'])),flush=True)
    except Exception as exc:
        put(root/'switch-error.json',dict(error=repr(exc)));print('Switch failed; restoring old server',flush=True)
        if child is not None and child.poll() is None:child.terminate();child.wait(timeout=15)
        rollback=launch(record,record['old']['ExecutablePath'],root,'rollback')
        api('/api/preflop/load',{'name':record['name']});api('/api/load',{'name':record['name']});verify(root)
        record.update(deployed=False,rolled_back=True,rollback_pid=rollback.pid,error=repr(exc));put(root/'deployment.json',record);raise
if __name__=='__main__':
    root=Path(sys.argv[2]);assert root.resolve().is_relative_to((LAB/'target/deployments').resolve())
    {'prepare':prepare,'switch':switch,'verify':verify}[sys.argv[1]](root)
