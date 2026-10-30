import importlib.util,json,os,shutil,subprocess,sys,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;H=ROOT/'runs/D212-current-RAM-activity';P=h.read(H/'protocol.json');O=H/'execution'
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
verify();assert not(ROOT/'gpu-run.lock').exists() and not(ROOT/'epoch-sequence.lock').exists();O.mkdir(exist_ok=False)
spec=importlib.util.spec_from_file_location('d212_times',H/'sampler.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
with h.ar.exclusive_lock(ROOT/'epoch-sequence.lock'):
 with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
  h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];h.child(P['rustc_command'],O,'rustc',1200);verify();data=(H/'postflop-trace.exe').read_bytes();assert(h.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes() in data;h.save(O/'binary.json',{'at':h.now(),'sha256':h.sha(H/'postflop-trace.exe'),'original_CUDA_embedded':True,'accepted_source_unchanged':True})
  for row in P['sequence']:
   verify();h.ar.refuse_active(h.ar.live_status());directory=ROOT/'runs'/row['id'];directory.mkdir(exist_ok=False);env=h.env();assert not env.get('CUDA_INJECTION64_PATH') and not env.get('CUDA_INJECTION32_PATH')
   for key in ['D087_TRACE_FILE','D087_META_FILE']:env.pop(key,None)
   exe=H/'postflop-trace.exe' if row['arm']=='trace' else ROOT/'binaries/E080-postflop_autoresearch.exe'
   if row['arm']=='trace':env['PATH']=str(H/'private')+os.pathsep+env['PATH'];env['D087_TRACE_FILE']=str(directory/'trace.bin');env['D087_META_FILE']=str(directory/'collector.jsonl')
   command=[str(exe),'--exact','postflop_complete_cycle','--ignored','--nocapture','--test-threads=1'];clock=time.perf_counter();started=h.now();proc=handle=None;error=cleanup=terminal=None
   h.save(directory/'invocation.json',{'at':started,'command':command,'cwd':str(h.REPO),'arm':row['arm'],'environment':{k:env.get(k) for k in ['RAYON_NUM_THREADS','POSTFLOP_AUTORESEARCH_STORAGE','POSTFLOP_AUTORESEARCH_PROFILE','D087_TRACE_FILE','D087_META_FILE']},'private_DLL_path':str(H/'private') if row['arm']=='trace' else None,'binary_sha256':h.sha(exe)})
   print('Starting',row['id'],row['arm'],flush=True)
   try:
    with(directory/'stdout.log').open('xb') as stdout,(directory/'stderr.log').open('xb') as stderr:
     proc=subprocess.Popen(command,cwd=h.REPO,env=env,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW);handle=s.KERNEL.OpenProcess(0x1000,False,proc.pid)
     if not handle:raise s.c.WinError(s.c.get_last_error())
     announced=0
     while True:
      try:proc.wait(timeout=10);break
      except subprocess.TimeoutExpired:
       elapsed=time.perf_counter()-clock
       if elapsed>1200:raise TimeoutError(row['id'])
       if elapsed-announced>=30:print(row['id'],'running',int(elapsed),'seconds; PID',proc.pid,flush=True);announced=elapsed
     terminal=s.process_times(handle,True)
    assert proc.returncode==0,(row['id'],(directory/'stderr.log').read_text(encoding='utf-8',errors='replace')[-2500:])
   except BaseException as exc:error=repr(exc);cleanup=h.ar.cleanup_child(proc);raise
   finally:
    if handle:assert s.KERNEL.CloseHandle(handle)
    h.save(directory/'exit.json',{'started_at':started,'finished_at':h.now(),'returncode':proc.returncode if proc else None,'error':error,'cleanup':cleanup,'terminal_process_times':terminal,'parent_wall_ms':(time.perf_counter()-clock)*1000})
   text=(directory/'stdout.log').read_text(encoding='utf-8');results=[json.loads(x.split('AUTORESEARCH_RESULT ',1)[1]) for x in text.splitlines() if 'AUTORESEARCH_RESULT ' in x];assert 'test result: ok. 1 passed; 0 failed; 0 ignored;' in text and len(results)==3
   h.save(directory/'report.json',{'id':row['id'],'at':h.now(),'status':'measured','returncode':proc.returncode,'arm':row['arm'],'results':results,'stdout_sha256':h.sha(directory/'stdout.log'),'terminal_process_times':terminal,'protocol_sha256':sys.argv[1],'source_sha256':h.custody(),'binary_sha256':h.sha(exe),'performance_qualification_sample':False,'candidate_accepted':False});assert h.exact(row['id'])==h.read(ROOT/'epoch/exact-anchor.json');verify();print('Completed',row['id'],'exact',flush=True)
  h.child([sys.executable,'-X','utf8',str(ROOT/'runs/D212-audit-profile.py')],O,'audit',600);verify();r=h.read(H/'report.json');h.save(O/'complete.json',{'at':h.now(),'all_owned_compilers_native_readers_terminal':True,'protocol_sha256':sys.argv[1],'report_sha256':h.sha(H/'report.json'),'new_performance_qualification_samples':0,'all_samples_retained':True,'source_main_live_protected_PTX_unchanged':True})
for name in ['report.json','execution/complete.json']:
 p=H/name;dst=h.ar.DASHBOARD/'evidence'/H.name/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+name,timeout=20) as response:assert response.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=h.read(h.ar.STATUS);item=next(x for x in st['experiments'] if x['id']=='D212');item.update(status='measured',stage='Full current-RAM activity cohort complete',correctness='18_science_records_138_checkpoints_exact',reason='Observer useful: '+str(r['observer_usefulness_pass'])+'. Target activity budget met: '+str(r['E105_target_budget']['passed'])+'. No speed gain or adoption from profiling.');item.setdefault('evidence',[]).append({'label':'Raw activity cohort and fresh target budget','url':'evidence/'+H.name+'/report.json'});st.update(updated_at=h.now(),active_experiment='D212',stage=item['stage'],activity='Current full-workload profile retained with fresh control pairs. All original science exact; observer and target-cost decisions published. E080 remains live.');h.ar.atomic_json(h.ar.STATUS,st)
print(json.dumps({'status':r['status'],'observer_usefulness_pass':r['observer_usefulness_pass'],'E105_target_budget':r['E105_target_budget'],'all_owned_children_terminal':True}),flush=True)
