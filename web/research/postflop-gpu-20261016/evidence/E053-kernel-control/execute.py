"""Fixed328case whole-raw shared-cache control; no production activation or solve."""
import json,re,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
H=ROOT/'runs/E053-kernel-control';OUT=H/'execution';assert len(sys.argv)==2;old.pin(H/'execution-plan.json',sys.argv[1]);P=old.read(H/'execution-plan.json')
def verify():
 old.pin(H/'execution-plan.json',sys.argv[1])
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody()
def child(cmd,label,timeout):
 proc=None;fault=None;cleanup=None;clock=time.monotonic();started=old.now();old.save(OUT/(label+'.invocation.json'),{'at':started,'command':cmd,'cwd':str(OUT)})
 try:
  with (OUT/(label+'.stdout.log')).open('xb') as stdout,(OUT/(label+'.stderr.log')).open('xb') as stderr:
   proc=subprocess.Popen(cmd,cwd=OUT,env=old.env(),stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
   while True:
    try:proc.wait(timeout=10);break
    except subprocess.TimeoutExpired:
     elapsed=time.monotonic()-clock
     if elapsed>=timeout:raise TimeoutError(label)
     print(label,'running',int(elapsed),'seconds; child',proc.pid,flush=True)
 except BaseException as exc:fault=repr(exc);cleanup=old.ar.cleanup_child(proc);raise
 finally:old.save(OUT/(label+'.exit.json'),{'at':old.now(),'started_at':started,'command':cmd,'returncode':proc.returncode if proc else None,'error':fault,'cleanup':cleanup})
 assert proc.returncode==0,(label,(OUT/(label+'.stderr.log')).read_text()[-2000:])
verify()
with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=54*1024**3;assert not OUT.exists() and not (H/'probe.exe').exists();OUT.mkdir()
 child(P['rustc_command'],'rustc',180);verify();old.save(OUT/'build.json',{'at':old.now(),'binary_sha256':old.sha(H/'probe.exe'),'native_executions':0})
 child([str(H/'probe.exe')],'probe',300);verify()
 raw=(OUT/'probe.stdout.log').read_text();markers=[json.loads(x.split('E053_EXACT ',1)[1]) for x in raw.splitlines() if 'E053_EXACT ' in x];assert len(markers)==367
 complete=markers[-1];assert complete['stage']=='complete' and complete['comparison_pairs']==364 and complete['kernel_launches']==728 and complete['all_output_bits_exact'] is True and complete['all_inputs_unchanged'] is True
 corpus=old.read(H/'corpus.json');cases=corpus['cases'];gs={g['id']:g for g in corpus['geometries']};records=[];seen=set();outputs=immutable=guards=0
 names={'nodes':'nodes','win':'node_twin','lose':'node_tlose','tie':'node_ttie','river':'node_river_slot','rsrc':'rsrc_o','po':'p_off','pc':'p_cnt','pi':'p_idx','pl':'p_lower','pu':'p_upper','oo':'o_off','oc':'o_cnt','oi':'o_idx','co':'o_card_off','cp':'o_card_pos','same':'same_p','c1':'pc1','c2':'pc2','slots':'cfv_slot'}
 with (OUT/'raw-results.jsonl').open(encoding='utf-8') as f:
  for index,line in enumerate(f):
   row=json.loads(line);record=row['record'];case=cases[index];g=gs[case['geometry']];assert record['case_id']==case['id'] and record['case_id'] not in seen;seen.add(record['case_id']);assert record==markers[index+2]
   before=row['baseline_output_bits'];after=row['candidate_output_bits'];assert before==after and len(before)==len(g['output_initial']);active=[bool(x) and case['count']>0 for x in g['output_active']]
   for i,(a,b) in enumerate(zip(before,g['output_initial'])):
    if not active[i]:assert a==b;guards+=2
   snapshots=[]
   for arm in ['baseline','candidate']:
    snapshot=row[arm+'_actual_device_inputs'];assert len(snapshot)==21 and len({v['buffer'] for v in snapshot})==21
    expected={n:g['arrays'][key] for n,key in names.items()}|{'reach':case['reach_o_bits']};assert {v['buffer']:v['actual_device_words'] for v in snapshot}==expected
    immutable+=sum(len(v['actual_device_words']) for v in snapshot);snapshots.append(snapshot)
   assert snapshots[0]==snapshots[1];outputs+=len(before)*2;records.append(record)
 assert len(records)==364 and set(seen)=={c['id'] for c in cases};assert guards==complete['output_guard_word_checks'] and immutable==complete['device_input_word_checks']
 report={'id':'E053-kernel-control','at':old.now(),'status':'pass_scoped_show_raw_equivalence','execution_plan_sha256':sys.argv[1],'cases':328,'kernel_launches':656,'complete':complete,'full_output_words_both_arms':outputs,'full_actual_device_input_words_both_arms':immutable,'guard_word_checks_both_arms':guards,'all_full_outputs_exact':True,'all_actual_device_inputs_exact':True,'all_unowned_guards_exact':True,'raw_sha256':old.sha(OUT/'raw-results.jsonl'),'corpus_sha256':old.sha(H/'corpus.json'),'stdout_sha256':old.sha(OUT/'probe.stdout.log'),'performance_measured':False,'solver_executions':0,'candidate_accepted':False,'accepted162_main_live_ptx_unchanged':True}
 old.save(H/'report.json',report);old.save(OUT/'complete.json',{'at':old.now(),'report_sha256':old.sha(H/'report.json'),'all_children_terminal':True,'candidate_accepted':False})
 print(json.dumps({k:v for k,v in report.items() if k!='complete'}),flush=True)
