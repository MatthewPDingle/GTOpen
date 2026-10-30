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
 old.child([str(H/'build/probe.exe'),*P['sdk_dll_paths']],OUT,'probe',env,120)
 markers=[json.loads(x.split('D103_RESULT ',1)[1]) for x in (OUT/'probe.stdout.log').read_text(encoding='utf-8').splitlines() if x.startswith('D103_RESULT ')];assert markers[0]['stage']=='identity' and markers[-1]['stage']=='complete';c=markers[-1]
 assert c['cleanup_success'] and all(c[k]==0 for k in ['application_kernel_launches','profiling_sessions','counter_collections','live_process_attachments','explicit_cuda_context_creations']);assert c['support_queries'] in [0,1]
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody();report={'id':'D103-profiler-support','at':old.now(),'status':'configuration_reports_compatible_collection_unverified' if c['device_configuration_compatible'] else 'profiler_configuration_unavailable','protocol_sha256':sys.argv[1],'markers':markers,'binary_sha256':old.sha(H/'build/probe.exe'),'stdout_sha256':old.sha(OUT/'probe.stdout.log'),'all_children_terminal':True,'application_kernel_launches':0,'counter_collections':0,'profiling_sessions':0,'source_activated':False,'performance_measured':False,'candidate_accepted':False,'limits':'Installed official SDK compatibility query in fresh owned process only. A supported result does not establish counter availability/permission, actual collection, replay fidelity, graph support, low observer overhead or a speedup. No elevation, retries, driver/global settings, live attach or application kernels.'};old.save(H/'report.json',report);print(json.dumps(report),flush=True)
