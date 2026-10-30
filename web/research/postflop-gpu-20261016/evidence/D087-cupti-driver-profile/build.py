import os,shutil,subprocess,sys,time
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;old.pin(H/'build-plan.json',sys.argv[1]);P=old.read(H/'build-plan.json');B=Path(P['build_dir'])
for p,h in P['input_sha256'].items():old.pin(p,h)
old.custody();assert shutil.disk_usage(ROOT).free>=54*1024**3
def child(command,label,timeout):
 old.save(B/(label+'.invocation.json'),{'at':old.now(),'command':command,'cwd':str(B)})
 with (B/(label+'.stdout.log')).open('xb') as stdout,(B/(label+'.stderr.log')).open('xb') as stderr:
  proc=subprocess.Popen(command,cwd=B,env=old.env(),stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
  fault=cleanup=None
  try:rc=proc.wait(timeout=timeout)
  except BaseException as exc:fault=repr(exc);cleanup=old.ar.cleanup_child(proc);raise
  finally:old.save(B/(label+'.exit.json'),{'at':old.now(),'returncode':proc.returncode,'error':fault,'cleanup':cleanup})
 assert rc==0,(label,(B/(label+'.stdout.log')).read_text(errors='replace')[-2500:],(B/(label+'.stderr.log')).read_text(errors='replace')[-1500:])
with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert not B.exists();B.mkdir()
 cmd='call "'+P['vcvars']+'" >nul && '+subprocess.list2cmdline(P['collector_command'])
 child('cmd.exe /d /s /c "'+cmd+'"','collector',180);old.custody()
 child(P['ability_command'],'ability',180);old.custody()
 old.save(B/'complete.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'all_compilers_terminal':True,'native_executions':0,'artifact_sha256':{str(p):old.sha(p) for p in [B/'D087Collector.dll',B/'D087Collector.lib',B/'ability.exe']},'private_dll_dirs':P['private_dll_dirs'],'source_production_unchanged':True})
print('D087 collector and ability probe compiled; no native execution.',flush=True)
