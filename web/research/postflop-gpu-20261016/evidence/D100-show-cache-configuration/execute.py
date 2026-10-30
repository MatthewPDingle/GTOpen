"""One owned cache-config diagnostic, with resource gate before any kernel."""
import json,os,shutil,struct,subprocess,sys,time
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;old.pin(H/'protocol-r2.json',sys.argv[1]);P=old.read(H/'protocol-r2.json')
def verify():
 old.pin(H/'protocol-r2.json',sys.argv[1])
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody()
def child(command,out,label,env,timeout):
 proc=None;fault=None;cleanup=None;clock=time.monotonic();started=old.now()
 old.save(out/(label+'.invocation.json'),{'at':started,'command':command,'cwd':str(out)})
 try:
  with (out/(label+'.stdout.log')).open('xb') as stdout,(out/(label+'.stderr.log')).open('xb') as stderr:
   proc=subprocess.Popen(command,cwd=out,env=env,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
   while True:
    try:proc.wait(timeout=10);break
    except subprocess.TimeoutExpired:
     elapsed=time.monotonic()-clock
     if elapsed>=timeout:raise TimeoutError(label)
     print(label,'running',int(elapsed),'seconds; owned child',proc.pid,flush=True)
 except BaseException as e:fault=repr(e);cleanup=old.ar.cleanup_child(proc);raise
 finally:old.save(out/(label+'.exit.json'),{'at':old.now(),'started_at':started,'command':command,'returncode':proc.returncode if proc else None,'error':fault,'cleanup':cleanup})
 assert proc.returncode==0,(label,(out/(label+'.stderr.log')).read_text(encoding='utf-8',errors='replace')[-3000:])
verify();B=H/'build';E=H/'execution';assert not B.exists() and not E.exists() and not (H/'probe.exe').exists()
with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=54*1024**3;B.mkdir();E.mkdir()
 env=old.env();env['PATH']=str(B)+os.pathsep+P['private_cupti_dll_dir']+os.pathsep+env['PATH'];env['D100_TRACE_FILE']=str(E/'trace.bin');env['D100_META_FILE']=str(E/'trace-meta.jsonl')
 assert not any(k in env for k in ['CUDA_INJECTION64_PATH','CUDA_INJECTION32_PATH','CUPTI_INJECTION64_PATH','NVBIT_TOOL'])
 child(P['collector_command'],B,'collector',env,180);verify()
 child(P['rustc_command'],B,'rustc',env,180);verify()
 old.save(B/'complete.json',{'at':old.now(),'binary_sha256':old.sha(H/'probe.exe'),'collector_sha256':old.sha(B/'D100Collector.dll'),'all_compilers_terminal':True,'native_executions':0})
 child([str(H/'probe.exe')],E,'probe',env,300);verify()
 markers=[json.loads(x.split('D100_EXACT ',1)[1]) for x in (E/'probe.stdout.log').read_text(encoding='utf-8').splitlines() if x.startswith('D100_EXACT ')]
 resources=[x for x in markers if x['stage']=='resource_gate'];assert len(resources)==1;resource=resources[0]
 assert resource['code_identical'] and resource['kernel_launches']==0 and len(resource['occupancy'])==216
 if not resource['passed']:
  assert markers[-1]['stage']=='resource_rejected' and not (E/'trace.bin').exists() and not (E/'raw-results.jsonl').exists()
  report={'id':'D100','at':old.now(),'status':'rejected_resource_prerequisite','resource':resource,'kernel_launches':0,'all_owned_children_terminal':True,'source_activated':False,'performance_measured':False,'candidate_accepted':False,'protocol_sha256':sys.argv[1]}
 else:
  assert all(c['candidate_blocks']>=c['baseline_blocks'] and c['candidate_blocks']>0 for c in resource['occupancy'])
  assert resource['baseline_attributes']==resource['candidate_attributes']
  complete=markers[-1];assert complete['stage']=='complete' and complete['comparison_pairs']==364 and complete['kernel_launches']==728 and complete['all_output_bits_exact'] and complete['all_inputs_unchanged']
  assert (E/'baseline.ptx').read_bytes()==(E/'candidate.ptx').read_bytes()
  metadata=[json.loads(x) for x in (E/'trace-meta.jsonl').read_text().splitlines()];assert metadata[0]['event']=='start' and metadata[-1]['event']=='complete'
  m=metadata[-1];assert all(m[k]==0 for k in ['dropped','errors','invalid_timestamps','outstanding_buffers']) and m['kernels']==728
  assert not any(x['event']=='error' for x in metadata)
  schema=struct.Struct('<6I4Q10I80s');raw=(E/'trace.bin').read_bytes();assert raw[:16]==b'D100-TRACE-v1\0\0\0' and (len(raw)-16)%schema.size==0
  rows=list(schema.iter_unpack(raw[16:]));kernels=sorted([r for r in rows if r[0] in [3,10]],key=lambda r:r[6]);assert len(rows)==m['records'] and len(kernels)==728
  apis={}
  for row in rows:
   if row[0]==4:apis.setdefault(row[4],[]).append(row)
  corpus=old.read(H/'corpus.json');cases=corpus['cases'];gs={g['id']:g for g in corpus['geometries']};observations=[]
  case_markers=[x for x in markers if x['stage']=='full_show_exact'];assert len(case_markers)==364
  changed=[]
  for i,case in enumerate(cases):
   g=gs[case['geometry']];pair=[]
   for arm,row in zip(['baseline','candidate'],kernels[2*i:2*i+2]):
    assert row[20].split(b'\0')[0]==b'up_show' and tuple(row[11:14])==(g['grid_blocks'],1,1) and tuple(row[14:17])==(128,1,1)
    assert row[19]==g['dynamic_shared_bytes'] and row[17]==resource['baseline_attributes'][0] and row[18]==resource['baseline_attributes'][2]
    joined=[a for a in apis.get(row[4],[]) if a[10]==0];assert len(joined)==1
    detail=row[5];cache=detail&255;flag=(detail>>8)&255;percent=(detail>>16)&255;assert flag in [0,1] and (flag or percent==0) and (not flag or cache==0)
    pair.append({'arm':arm,'correlation':row[4],'cache_requested':None if flag else cache&15,'cache_executed':None if flag else cache>>4,'explicit_carveout_requested':bool(flag),'carveout_requested_pct':percent if flag else None,'driver_shared_memory_executed':row[8]})
   different=pair[0]['driver_shared_memory_executed']!=pair[1]['driver_shared_memory_executed'] or (not pair[0]['explicit_carveout_requested'] and not pair[1]['explicit_carveout_requested'] and pair[0]['cache_executed']!=pair[1]['cache_executed'])
   if different:changed.append(case['id'])
   observations.append({'case_id':case['id'],'geometry':case['geometry'],'dynamic_shared_bytes':g['dynamic_shared_bytes'],'driver_configuration_changed':different,'pair':pair})
  report={'id':'D100','at':old.now(),'status':'pass_mechanism_pending_integrated_qualification' if changed else 'declined_no_observed_executed_configuration_change','protocol_sha256':sys.argv[1],'resource':resource,'raw_control_complete':complete,'trace_complete':m,'observations':observations,'configuration_changed_cases':changed,'configuration_changed_count':len(changed),'kernel_launches':728,'all_owned_children_terminal':True,'source_activated':False,'performance_measured':False,'candidate_accepted':False,'limits':'Identical CUDA code, one per-function preference in an owned diagnostic context. Actual CUPTI configuration fields and exact raw direct-kernel cases only; not whole-solver graph, capacity, speed, confidence or universal driver/hardware evidence. Configuration may depend on prior kernel preferences; baseline/candidate direct cases alternate in one context.'}
 old.save(H/'report.json',report);old.save(E/'complete.json',{'at':old.now(),'report_sha256':old.sha(H/'report.json'),'all_owned_children_terminal':True,'source_main_live_ptx_unchanged':True});verify()
print(json.dumps({'status':report['status'],'kernel_launches':report['kernel_launches'],'resource_pass':resource['passed'],'changed_cases':report.get('configuration_changed_count'),'report_sha256':old.sha(H/'report.json')}),flush=True)
