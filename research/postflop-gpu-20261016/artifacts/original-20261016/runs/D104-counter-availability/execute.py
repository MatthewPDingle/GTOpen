import json,os,shutil,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
OUT=H/'execution'
with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 old.custody();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=54*1024**3;assert not OUT.exists();OUT.mkdir();(H/'build').mkdir()
 gpu=old.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version','--format=csv,noheader'],timeout=10);assert gpu['returncode']==0 and P['gpu_uuid'] in gpu['stdout'];old.save(OUT/'before.json',{'at':old.now(),'gpu':gpu,'protocol_sha256':sys.argv[1]})
 old.child(P['compile_command_line'],OUT,'cl',old.env(),120)
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.save(OUT/'build-complete.json',{'at':old.now(),'binary_sha256':old.sha(H/'build/probe.exe'),'native_executions':0})
 env=old.env();env['PATH']=str(Path(P['sdk_dll_paths'][0]).parent)+os.pathsep+env.get('PATH','')
 # old.child uses REPO cwd; launch an owned subprocess from this script into OUT
 # so CreateFile(CREATE_NEW) writes metadata only to the off-tree research directory.
 import subprocess,time
 started=old.now();proc=None;fault=None;cleanup=None
 old.save(OUT/'probe.invocation.json',{'at':started,'command':[str(H/'build/probe.exe'),*P['sdk_dll_paths']],'cwd':str(OUT)})
 try:
  with (OUT/'probe.stdout.log').open('xb') as out,(OUT/'probe.stderr.log').open('xb') as err:
   proc=subprocess.Popen([str(H/'build/probe.exe'),*P['sdk_dll_paths']],cwd=OUT,env=env,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW);proc.wait(timeout=120)
 except BaseException as e:fault=repr(e);cleanup=old.ar.cleanup_child(proc);raise
 finally:old.save(OUT/'probe.exit.json',{'started_at':started,'finished_at':old.now(),'returncode':proc.returncode if proc else None,'error':fault,'cleanup':cleanup})
 assert proc.returncode==0,(OUT/'probe.stderr.log').read_text(encoding='utf-8',errors='replace')[-2000:]
 markers=[json.loads(x.split('D104_RESULT ',1)[1]) for x in (OUT/'probe.stdout.log').read_text(encoding='utf-8').splitlines() if x.startswith('D104_RESULT ')];assert markers[0]['stage']=='identity' and markers[-1]['stage']=='complete';c=markers[-1]
 assert c['cleanup_success'] and c['current_context_after_is_null'] and c['guards_exact'] and c['private_contexts_created']==c['private_contexts_destroyed']
 assert all(c[k]==0 for k in ['application_kernel_launches','profiling_sessions','counter_collections','live_process_attachments']);assert c['size_queries'] in [0,1] and c['fill_queries'] in [0,1]
 image=OUT/'counter-availability.bin'
 if c['availability_image_obtained']:assert image.is_file() and image.stat().st_size==c['returned_bytes'] and 0<image.stat().st_size<=16*1024**2
 else:assert not image.exists()
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody();report={'id':'D104-counter-availability','at':old.now(),'status':'availability_metadata_obtained_collection_unverified' if c['availability_image_obtained'] else 'availability_query_unavailable','protocol_sha256':sys.argv[1],'markers':markers,'binary_sha256':old.sha(H/'build/probe.exe'),'stdout_sha256':old.sha(OUT/'probe.stdout.log'),'image':{'path':str(image),'bytes':image.stat().st_size,'sha256':old.sha(image)} if image.exists() else None,'all_owned_children_terminal':True,'application_kernel_launches':0,'profiling_sessions':0,'counter_collections':0,'source_activated':False,'performance_measured':False,'candidate_accepted':False,'limits':'Availability metadata query only, not runtime hardware counter values. Success does not establish permission to enable/collect, replay/graph correctness, observer overhead or speed. Private context destroyed and profiler deinitialized; no elevation/retries/global changes/live attach.'};old.save(H/'report.json',report);print(json.dumps(report),flush=True)
