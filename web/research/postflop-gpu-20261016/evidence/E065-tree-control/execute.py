import json,os,shutil,subprocess,sys,time
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
OUT=H/'execution'
def child(cmd,label,timeout):
 proc=None;fault=None;cleanup=None;start=old.now();clock=time.monotonic();old.save(OUT/(label+'.invocation.json'),{'at':start,'command':cmd,'cwd':str(OUT)})
 try:
  with (OUT/(label+'.stdout.log')).open('xb') as out,(OUT/(label+'.stderr.log')).open('xb') as err:
   proc=subprocess.Popen(cmd,cwd=OUT,env=old.env(),stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
   while True:
    try:proc.wait(timeout=10);break
    except subprocess.TimeoutExpired:
     elapsed=time.monotonic()-clock
     if elapsed>=timeout:raise TimeoutError(label)
     print(label,'running',int(elapsed),'seconds; child',proc.pid,flush=True)
 except BaseException as e:fault=repr(e);cleanup=old.ar.cleanup_child(proc);raise
 finally:old.save(OUT/(label+'.exit.json'),{'started_at':start,'finished_at':old.now(),'returncode':proc.returncode if proc else None,'error':fault,'cleanup':cleanup})
 assert proc.returncode==0,(label,(OUT/(label+'.stderr.log')).read_text(encoding='utf-8',errors='replace')[-4000:])
with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 old.custody();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=66*1024**3;assert not OUT.exists();OUT.mkdir()
 child(P['rustc_command'],'rustc',180);old.custody();old.save(OUT/'build-complete.json',{'at':old.now(),'binary_sha256':old.sha(H/'probe.exe'),'native_executions':0})
 canonical=[];controls=[]
 for label,args in [('canonical-0',['canonical','0']),('canonical-1',['canonical','1']),('canonical-2',['canonical','2']),('controls',['controls','all'])]:
  child([str(H/'probe.exe'),*args],label,600);old.custody()
  markers=[json.loads(x.split('E065_TREE ',1)[1]) for x in (OUT/(label+'.stdout.log')).read_text(encoding='utf-8').splitlines() if x.startswith('E065_TREE ')];assert markers[-1]['stage']=='complete' and markers[-1]['all_exact']
  canonical.extend(m for m in markers if m['stage']=='canonical');controls.extend(m['result'] for m in markers if m['stage']=='control')
 assert len(canonical)==3 and [c['id'] for c in canonical]==[0,1,2] and len(controls)==15+P['extra_control_cases']
 raw_records=[]
 for row in canonical+controls:
  if 'raw_file' in row:
   f=OUT/row['raw_file'];assert f.is_file();raw_records.append({'path':str(f),'sha256':old.sha(f),'bytes':f.stat().st_size,'label':row.get('label','canonical-'+str(row.get('id'))),'checks':row['checks'],'metadata':row['metadata'],'hands':row['hands']})
 saving=sum(c['saving_ms'] for c in canonical);guards=[{'id':c['id'],'positive_median_slowdown':c['positive_median_slowdown'],'slower_pairs':c['slower_pairs'],'failed':c['positive_median_slowdown'] and c['slower_pairs']>=5} for c in canonical];passed=saving>=P['minimum_component_saving_ms'] and not any(g['failed'] for g in guards)
 report={'id':'E065-tree-control','at':old.now(),'status':'advance_to_integrated_qualification' if passed else 'rejected_component_admission','protocol_sha256':sys.argv[1],'canonical':canonical,'controls':controls,'raw_files':raw_records,'sum_component_median_saving_ms':saving,'required_component_saving_ms':P['minimum_component_saving_ms'],'component_guards':guards,'all_tree_fields_capacities_errors_exact':True,'measured_pairs_per_canonical':9,'warmup_pairs_per_canonical':2,'historical_timing_samples_scored':0,'exclusions':[],'extension_samples':0,'binary_sha256':old.sha(H/'probe.exe'),'all_owned_children_terminal':True,'source_activated':False,'gpu_executions':0,'full_cycle_performance_measured':False,'candidate_accepted':False,'limits':'TreeBuilder-only component admission, historical full-cycle number is a frozen reference, not a combined score. Each measured tree fingerprint/capacity matches; final full typed paired trees and every successful control retained. Raw root replay still required. No whole Spot/CPUStore/GPU/quality/process/peak/speedup qualification yet.'};old.save(H/'report.json',report);print(json.dumps({k:v for k,v in report.items() if k not in ['canonical','controls','raw_files']},indent=2),flush=True)
