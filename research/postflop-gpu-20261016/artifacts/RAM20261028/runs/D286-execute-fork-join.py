import json,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D286-fork-join-primitive';P=h.read(H/'protocol.json');assert len(sys.argv)==2;O=H/'execution'
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
def child(cmd,label,timeout):
 h.save(O/(label+'.invocation.json'),{'at':h.now(),'command':cmd,'cwd':str(O)});started=h.now();proc=None;error=cleanup=None;t=time.monotonic();announced=0
 try:
  with (O/(label+'.stdout.log')).open('xb')as out,(O/(label+'.stderr.log')).open('xb')as err:
   proc=subprocess.Popen(cmd,cwd=O,env=h.env(),stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
   while True:
    try:proc.wait(timeout=10);break
    except subprocess.TimeoutExpired:
     elapsed=time.monotonic()-t
     if elapsed>timeout:raise TimeoutError(label)
     if elapsed-announced>=30:print(label,'running',int(elapsed),'seconds; PID',proc.pid,flush=True);announced=elapsed
  assert proc.returncode==0,(label,(O/(label+'.stderr.log')).read_text(encoding='utf-8',errors='replace')[-4000:])
 except BaseException as e:error=repr(e);cleanup=h.ar.cleanup_child(proc);raise
 finally:h.save(O/(label+'.exit.json'),{'started_at':started,'finished_at':h.now(),'returncode':proc.returncode if proc else None,'error':error,'cleanup':cleanup})
verify();assert not O.exists();O.mkdir()
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];print('Starting one Rust compiler',flush=True);child(P['rustc_command'],'rustc',300);verify();binary=H/'probe.exe';assert (H/'baseline.ptx').read_bytes()in binary.read_bytes();h.save(O/'binary.json',{'sha256':h.sha(binary),'original_sealed_PTX_embedded':True})
 print('Starting one fork/join primitive process',flush=True);child([str(binary)],'probe',600);verify();markers=[json.loads(l.split('D286_RESULT ',1)[1])for l in (O/'probe.stdout.log').read_text(encoding='utf-8').splitlines()if l.startswith('D286_RESULT ')];assert len(markers)==76 and markers[0]['stage']=='device'and markers[-1]['stage']=='complete'
 summary=markers[-1];assert summary['snapshots']==74 and summary['graphs_inspected']==15 and summary['captured_kernel_nodes']==59 and summary['actual_application_kernel_executions']==291 and summary['all_streams_events_graphs_buffers_context_released'];assert (O/'probe.stderr.log').read_bytes()==b''
 h.save(O/'native-complete.json',{'at':h.now(),'protocol_sha256':sys.argv[1],'binary_sha256':h.sha(binary),'summary':summary,'raw_sha256':h.sha(O/'raw-results.jsonl'),'raw_bytes':(O/'raw-results.jsonl').stat().st_size,'DAG_sha256':h.sha(O/'graph-dags.json'),'native_terminal':True});assert (O/'raw-results.jsonl').stat().st_size<P['raw_reservation_bytes'];print('Starting complete retained-data reader',flush=True);child([sys.executable,str(H/'audit.py')],'reader',300);verify();q=h.read(H/'report.json');assert q['status']=='pass_scoped_disjoint_buffer_fork_join_eager_capture_replay_primitive';h.save(O/'complete.json',{'at':h.now(),'all_owned_children_terminal':True,'report_sha256':h.sha(H/'report.json'),'CFR_solver_NVRTC_speed_samples':0,'candidate_accepted':False})
print('D286 primitive complete; no solver or speed claim.',flush=True)
