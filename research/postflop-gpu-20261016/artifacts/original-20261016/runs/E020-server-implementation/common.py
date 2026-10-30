"""Small source/authorization guards shared by isolated server scripts."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,os,signal,subprocess,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
MAIN=Path(r'X:\Dev\GTOpen')
TARGET=ROOT/'build-server-e020'
NVRTC=MAIN/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin'
spec=importlib.util.spec_from_file_location('server_primitives',HERE/'runner-primitives.py')
ar=importlib.util.module_from_spec(spec);spec.loader.exec_module(ar)
SOURCES=json.loads((HERE/'source-pins.json').read_text(encoding='utf-8'))
LIVE=json.loads((HERE/'live-exclusion.json').read_text(encoding='utf-8'))
KEYS={'RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','CARGO_BUILD_RUSTFLAGS','CARGO_BUILD_RUSTC','CARGO_BUILD_RUSTC_WRAPPER','CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER','CARGO_BUILD_TARGET'}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return ar.sha256(Path(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,data):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(data,f,indent=2,allow_nan=False);f.write('\n')
def pin(r):
    p=Path(r['path']);assert sha(p)==r['sha256'],str(p);return p
def capture(command):
    r=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
    assert r.returncode==0,(command,r.stderr);return r.stdout.strip()
def powershell(code):return json.loads(capture(['powershell.exe','-NoProfile','-Command',code]))
def live_identity():
    value=powershell("$ls=@(Get-NetTCPConnection -LocalPort 43735 -State Listen -ErrorAction Stop); $p=Get-CimInstance Win32_Process -Filter 'ProcessId=37268'; @{listeners=@($ls|Select-Object -ExpandProperty OwningProcess -Unique);pid=$p.ProcessId;path=$p.ExecutablePath} | ConvertTo-Json -Compress")
    assert value['listeners']==[LIVE['pid']] and value['pid']==LIVE['pid']
    assert Path(value['path']).resolve()==Path(LIVE['executable']).resolve()
    assert sha(value['path'])==LIVE['sha256'];return value
def initialize(phase,auth_hash):
    global AUTH,AUTH_HASH,AUTH_PATH,PREPARED
    AUTH_HASH=auth_hash;AUTH_PATH=HERE/(phase+'-authorization.json');assert sha(AUTH_PATH)==auth_hash
    AUTH=read(AUTH_PATH);assert AUTH['candidate']=='E020' and AUTH['phase']==phase and AUTH['independent_source_review_pass'] is True
    assert AUTH['live_deployment_authorized'] is False
    PREPARED=read(HERE/'prepared-manifest.json');assert AUTH['prepared_manifest_sha256']==sha(HERE/'prepared-manifest.json')
    def interrupted(signum,_frame):raise KeyboardInterrupt(f'signal {signum}')
    for sig in [signal.SIGTERM,getattr(signal,'SIGBREAK',None)]:
        if sig is not None:signal.signal(sig,interrupted)
    verify()
def verify():
    assert sha(AUTH_PATH)==AUTH_HASH
    for n,h in PREPARED['artifact_sha256'].items():assert sha(HERE/n)==h,n
    for n,h in PREPARED['nvrtc_dll_sha256'].items():assert sha(NVRTC/n)==h,n
    for n,h in SOURCES.items():assert sha(REPO/n)==h,n
    ap=pin(AUTH['acceptance']);assert ap==ROOT/'comparisons/E020-qualification/report.json'
    a=read(ap);assert a['id']=='E020' and a['status']=='validated' and a['deployed'] is False
    primary={k:v for k,v in SOURCES.items() if not k.startswith('crates/server/')}
    assert a['binary_source_sha256']==primary
    expected={k:SOURCES[k] for k in ['crates/solver/src/gpu/kernels.cu','crates/solver/src/gpu/mod.rs']}
    assert a['source_sha256']==expected
    for repo,field in [(REPO,'research_commit'),(MAIN,'main_commit')]:
        assert capture(['git','-C',str(repo),'rev-parse','HEAD'])==a[field]
        for n,h in a['compiled_shared_source_sha256'].items():assert sha(repo/n)==h,n
        for n,h in expected.items():assert sha(repo/n)==h,n
    for r in AUTH['required_evidence']:pin(r)
    assert AUTH['required_evidence'];live_identity()
def env(build=False):
    e=os.environ.copy();bad={k:v for k,v in e.items() if k in KEYS or k.startswith('CARGO_PROFILE_RELEASE_') or (k.startswith('CARGO_TARGET_') and k.endswith('_RUSTFLAGS'))}
    assert not bad,('compiler overrides',bad)
    for k in ['CARGO_TARGET_DIR','POSTFLOP_AUTORESEARCH_FIXTURE','POSTFLOP_AUTORESEARCH_STORAGE','POSTFLOP_AUTORESEARCH_PROFILE']:e.pop(k,None)
    e['RAYON_NUM_THREADS']='16';e['PATH']=str(NVRTC)+os.pathsep+e.get('PATH','')
    if build:e['CARGO_TARGET_DIR']=str(TARGET)
    return e
def embedded(binary):
    data=Path(binary).read_bytes();counts={x:data.count((HERE/(x+'-kernels.cu')).read_bytes()) for x in ['E015','E020']}
    assert counts['E020']>0 and counts['E015']==0,counts;return counts
def binary(name):
    p=ROOT/'binaries'/(name+'.exe');m=p.with_suffix('.manifest.json');j=read(m)
    assert p.resolve()!=Path(LIVE['executable']).resolve() and sha(p)!=LIVE['sha256']
    assert j['binary_sha256']==sha(p) and j['source_sha256']==SOURCES
    assert j['prepared_manifest_sha256']==sha(HERE/'prepared-manifest.json')
    assert j['embedded_cuda_occurrences']==embedded(p)
    return p,m

def heartbeat(activity,out):
    try:
        with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
            value=read(ar.STATUS);value.update(updated_at=ar.now(),stage='E020 isolated server validation',activity=activity)
            ar.atomic_json(ar.STATUS,value)
    except Exception as error:
        try:
            with (out/'heartbeat-errors.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'at':now(),'error':repr(error)})+'\n')
        except Exception:pass
