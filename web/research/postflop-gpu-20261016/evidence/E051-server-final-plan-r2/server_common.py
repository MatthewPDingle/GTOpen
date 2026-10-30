"""Frozen E051 server qualification guards; no production mutation."""
from pathlib import Path
import json,os,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parent
REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016');MAIN=Path(r'X:\Dev\GTOpen')
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
read,sha,save,now=old.read,old.sha,old.save,old.now
ar=old.ar;P=read(HERE/'protocol.json');SOURCES=P['source_sha256'];LIVE=P['live_identity']
NVRTC=ar.NVRTC;TARGET=Path(P['target'])
KEYS={'RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER','CARGO_BUILD_RUSTFLAGS','CARGO_BUILD_RUSTC','CARGO_BUILD_RUSTC_WRAPPER','CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER','CARGO_BUILD_TARGET'}
def pin(r):old.pin(r['path'],r['sha256']);return Path(r['path'])
def capture(command):
 r=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
 assert r.returncode==0,(command,r.stderr);return r.stdout.strip()
def powershell(code):return json.loads(capture(['powershell.exe','-NoProfile','-Command',code]))
def live_identity():
 v=powershell("$ls=@(Get-NetTCPConnection -LocalPort 43735 -State Listen -ErrorAction Stop); $p=Get-CimInstance Win32_Process -Filter 'ProcessId="+str(LIVE['pid'])+"'; @{listeners=@($ls|Select-Object -ExpandProperty OwningProcess -Unique);pid=$p.ProcessId;path=$p.ExecutablePath;created=$p.CreationDate.ToUniversalTime().ToString('o')} | ConvertTo-Json -Compress")
 assert v==LIVE,(v,LIVE);old.pin(v['path'],P['live_sha256']);return v
def initialize(phase,h):
 global AUTH,AUTH_PATH,AUTH_HASH
 AUTH_PATH=HERE/('protocol.json' if phase=='build' else 'smoke-protocol.json');AUTH_HASH=h;old.pin(AUTH_PATH,h);AUTH=read(AUTH_PATH)
 verify()
def verify():
 old.custody();old.pin(AUTH_PATH,AUTH_HASH)
 for rel,h in P['source_sha256'].items():old.pin(REPO/rel,h)
 for rel,h in P['server_source_sha256'].items():old.pin(MAIN/rel,h)
 for path,h in P['input_sha256'].items():old.pin(path,h)
 a=read(pin(P['acceptance']));assert a['status']=='accepted_source_integrated' and a['candidate']=='E051' and a['decision']=='accept_no_observed_tradeoff_in_registered_scope'
 live_identity()
def env(build=False):
 e=old.env();bad={k:v for k,v in e.items() if k in KEYS or k.startswith('CARGO_PROFILE_RELEASE_') or(k.startswith('CARGO_TARGET_')and k.endswith('_RUSTFLAGS'))};assert not bad,('compiler overrides',bad)
 e.pop('CARGO_TARGET_DIR',None)
 if build:e['CARGO_TARGET_DIR']=str(TARGET)
 return e
def embedded(binary):
 data=Path(binary).read_bytes();accepted=(REPO/'crates/solver/src/gpu/kernels.cu').read_bytes();prior=(ROOT/'runs/E020-server-implementation/E020-kernels.cu').read_bytes()
 counts={'E051':data.count(accepted),'E020':data.count(prior)};assert counts['E051']>0 and counts['E020']==0,counts;return counts
def binary(name):
 p=ROOT/'binaries'/(name+'.exe');m=p.with_suffix('.manifest.json');j=read(m)
 old.pin(p,j['binary_sha256']);assert j['source_sha256']==SOURCES and j['protocol_sha256']==sha(HERE/'protocol.json')
 assert j['embedded_cuda_occurrences']==embedded(p);return p,m
def heartbeat(activity):
 with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
  s=read(ar.STATUS);s.update(updated_at=now(),state='running',goal_status='active',active_experiment='E051-server',stage='E051 isolated server qualification',activity=activity);ar.atomic_json(ar.STATUS,s)
