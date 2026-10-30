import sys,json,shutil,subprocess,time,importlib.util,re
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'));import common as h
import affinity
assert len(sys.argv)==2;P=h.read(H/'protocol.json')
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
verify();O=H/'execution';O.mkdir(exist_ok=False)
spec=importlib.util.spec_from_file_location('times',H/'sampler.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
def progress(row,finished):
 with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
  status=h.read(h.ar.STATUS);item=next(x for x in status['experiments'] if x['id']=='E103')
  item.update(status='running',stage=('Completed ' if finished else 'Running ')+row['id']+' ('+row['kind']+')')
  status.update(updated_at=h.now(),active_experiment='E103',stage=item['stage'],activity='Fixed CPU-placement comparison: '+row['id']+' '+('finished with exact state.' if finished else 'running.')+' Both arms use original E080 bytes and16workers; full clocks and terminalcosts retained. No gain adopted.');h.ar.atomic_json(h.ar.STATUS,status)
def run(row):
 directory=ROOT/'runs'/row['id'];directory.mkdir(exist_ok=False);env=h.env();assert env['RAYON_NUM_THREADS']=='16'
 command=[P['unit_binary'],'--nocapture','--test-threads=1'] if row['kind']=='unit' else [P['benchmark_binary'],'--exact','postflop_complete_cycle','--ignored','--nocapture','--test-threads=1']
 mask=P['masks'][row['arm']];started=h.now();clock=time.perf_counter();proc=handle=None;error=cleanup=None;terminal=None;witnesses=[]
 h.save(directory/'invocation.json',{'at':started,'command':command,'cwd':str(h.REPO),'arm':row['arm'],'kind':row['kind'],'block':row.get('block'),'mask':mask,'binary_sha256':h.sha(command[0]),'environment':{n:env[n] for n in ['RAYON_NUM_THREADS','POSTFLOP_AUTORESEARCH_STORAGE','POSTFLOP_AUTORESEARCH_PROFILE']},'original_NVRTC_path':str(h.ar.NVRTC),'affinity_set_cost_scope':'Parentwallclockstartsbeforeset/spawn/restore; nativecompletecycleclockoriginalandunchanged.'})
 print('Starting',row['id'],row['arm'],row['kind'],flush=True)
 try:
  with(directory/'stdout.log').open('xb') as stdout:
   proc=affinity.spawn(mask,witnesses,command,cwd=h.REPO,env=env,stdout=stdout,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
   handle=s.KERNEL.OpenProcess(0x1000,False,proc.pid)
   if not handle:raise s.c.WinError(s.c.get_last_error())
   announced=0
   while True:
    try:proc.wait(timeout=10);break
    except subprocess.TimeoutExpired:
     elapsed=time.perf_counter()-clock
     if elapsed>P['native_timeout_seconds']:raise TimeoutError(row['id'])
     if elapsed-announced>=30:print(row['id'],'running',int(elapsed),'seconds;PID',proc.pid,flush=True);announced=elapsed
   terminal=s.process_times(handle,True)
  assert proc.returncode==0,(row['id'],(directory/'stdout.log').read_text(encoding='utf-8',errors='replace')[-2500:])
 except BaseException as exc:error=repr(exc);cleanup=h.ar.cleanup_child(proc);raise
 finally:
  if handle:assert s.KERNEL.CloseHandle(handle)
  h.save(directory/'exit.json',{'started_at':started,'finished_at':h.now(),'returncode':proc.returncode if proc else None,'error':error,'cleanup':cleanup,'terminal_process_times':terminal,'parent_wall_ms':(time.perf_counter()-clock)*1000,'affinity_spawn_witnesses':witnesses,'parent_final_affinity':affinity.query()})
 text=(directory/'stdout.log').read_text(encoding='utf-8');results=[json.loads(x.split('AUTORESEARCH_RESULT ',1)[1]) for x in text.splitlines() if 'AUTORESEARCH_RESULT ' in x]
 assert witnesses and witnesses[0]['actual_child_at_spawn']['process_mask']==mask
 assert affinity.query()=={'process_mask':P['masks']['baseline'],'system_mask':P['masks']['baseline']}
 if row['kind']=='unit':
  assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',text)==[('86','0','4','0','0')]
 else:
  assert 'test result: ok. 1 passed; 0 failed; 0 ignored;' in text and len(results)==3 and all(x['runtime_nvrtc_jit_included'] is True for x in results)
 h.save(directory/'report.json',{'id':row['id'],'at':h.now(),'status':'measured','returncode':proc.returncode,'workers':16,'arm':row['arm'],'affinity_mask':mask,'kind':row['kind'],'block':row.get('block'),'results':results,'stdout_sha256':h.sha(directory/'stdout.log'),'terminal_process_times':terminal,'protocol_sha256':sys.argv[1],'source_sha256':h.custody(),'binary_sha256':h.sha(command[0]),'performance_qualification_sample':row['kind']=='scored','candidate_accepted':False})
 if row['kind']!='unit':assert h.exact(row['id'])==h.read(ROOT/'epoch/exact-anchor.json')
 print('Completed',row['id'],'exact',flush=True)
with h.ar.exclusive_lock(ROOT/'epoch-sequence.lock'):
 with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
  h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
  for row in P['sequence']:
   verify();h.ar.refuse_active(h.ar.live_status());progress(row,False);run(row);verify();progress(row,True)
  h.save(O/'complete.json',{'at':h.now(),'all_owned_children_terminal':True,'protocol_sha256':sys.argv[1],'sequence':[x['id'] for x in P['sequence']],'units_per_arm':86,'ignored_units_per_arm':4,'warmups_unscored':2,'scored_processes':6,'scored_full_records_exact':18,'scored_checkpoints_exact':138,'all_samples_retained':True,'extension_runs':0,'historical_samples_scored':0,'new_gain_accepted':False})
verify();print('E103 fixed primary complete; no sample exclusions or adoption.',flush=True)
