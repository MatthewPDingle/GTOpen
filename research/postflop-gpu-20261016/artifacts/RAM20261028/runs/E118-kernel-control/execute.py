"""Own one compiler and one fixed12140pair numerical process using sealed PTX."""
from pathlib import Path
import json,shutil,subprocess,sys,time
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'epoch'));import common as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');O=H/'execution'
def verify():
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody()
def child(command,label,timeout):
 proc=None;error=None;cleanup=None;started=old.now();t=time.monotonic()
 old.save(O/(label+'.invocation.json'),{'at':started,'command':command,'cwd':str(O)})
 try:
  with(O/(label+'.stdout.log')).open('xb')as stdout,(O/(label+'.stderr.log')).open('xb')as stderr:
   proc=subprocess.Popen(command,cwd=O,env=old.env(),stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
   while True:
    try:proc.wait(timeout=10);break
    except subprocess.TimeoutExpired:
     if time.monotonic()-t>=timeout:raise TimeoutError(label)
     print(label,'running; child',proc.pid,flush=True)
  assert proc.returncode==0,(label,(O/(label+'.stderr.log')).read_text(encoding='utf-8',errors='replace')[-4000:])
 except BaseException as exc:error=repr(exc);cleanup=old.ar.cleanup_child(proc);raise
 finally:old.save(O/(label+'.exit.json'),{'started_at':started,'finished_at':old.now(),'returncode':proc.returncode if proc else None,'error':error,'cleanup':cleanup})
verify()
with old.ar.exclusive_lock(R/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3;assert not O.exists()and not(H/'probe.exe').exists();O.mkdir()
 assert old.read(P['resource_report'])['status']=='pass_compiled_resources_mechanism_pending'
 assert all(old.read(P['resource_report'])['gates'].values())
 child(P['rustc_command'],'rustc',180);verify()
 binary=H/'probe.exe';data=binary.read_bytes()
 assert(H/'baseline.ptx').read_bytes()in data and(H/'candidate.ptx').read_bytes()in data
 old.save(O/'build-complete.json',{'at':old.now(),'binary_sha256':old.sha(binary),'exact_sealed_PTX_embedded':True,'compiler_terminal':True,'numerical_launches':0})
 child([str(binary)],'probe',900);verify()
 markers=[json.loads(x.split('E118_EXACT ',1)[1])for x in(O/'probe.stdout.log').read_text(encoding='utf-8').splitlines()if'E118_EXACT 'in x]
 assert len(markers)==12143 and markers[0]['stage']=='corpus_validated'and markers[1]['stage']=='device'and markers[-1]['stage']=='complete'
 corpus=old.read(H/'corpus.json');matrix=[(w,c)for w in P['widths']for c in corpus['cases']]
 for (width,case),row in zip(matrix,markers[2:-1]):assert row['stage']=='full_show_exact'and row['case_id']==case['id']and row['threads']==width and row['all_output_bits_exact']and row['input_bits_unchanged']
 summary=markers[-1];assert summary['comparison_pairs']==12140 and summary['kernel_launches']==24280 and summary['all_output_bits_exact']and summary['all_inputs_unchanged']and summary['tested_block_widths']==P['widths']
 assert(O/'probe.stderr.log').read_bytes()==b''
 for arm in ['baseline','candidate']:assert(O/(arm+'.ptx')).read_bytes()==(H/(arm+'.ptx')).read_bytes()
 raw=O/'raw-results.jsonl';assert raw.stat().st_size<8*1024**3
 old.save(O/'complete.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'summary':summary,'binary_sha256':old.sha(binary),'raw_sha256':old.sha(raw),'raw_bytes':raw.stat().st_size,'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'performance_measured':False,'candidate_accepted':False});verify()
 print(json.dumps({'summary':summary,'raw_sha256':old.sha(raw),'raw_bytes':raw.stat().st_size}),flush=True)
