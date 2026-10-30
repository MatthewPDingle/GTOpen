"""Execute frozen D110 exactly once, off-tree CPU component diagnostic."""
import sys,json,shutil
from pathlib import Path
ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016');sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
H=ROOT/'runs/D110-plan-stage-profile';assert len(sys.argv)==2;ph=sys.argv[1];old.pin(H/'protocol.json',ph);P=old.read(H/'protocol.json')
def verify():
 old.pin(H/'protocol.json',ph)
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody()
verify();assert shutil.disk_usage(ROOT).free>P['reserve_free_bytes']
old.save(H/'execution-seal.json',{'at':old.now(),'protocol_sha256':ph,'executor_sha256':old.sha(__file__),'rule':'Exactly one compile and 12 serial fresh CPU processes, fixed 3 timing pairs/case, no retry/exclusion/extension.'})
with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());B=H/'build';E=H/'execution';B.mkdir();E.mkdir()
 with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
  s=old.read(old.ar.STATUS);assert not any(x['id']=='D110' for x in s['experiments']);s['experiments'].append({'id':'D110','at':old.now(),'title':'GPU-plan CPU substage profile','kind':'diagnostic','status':'running','correctness':'pending','accepted':False,'stage':'CPU diagnostic compile','reason':'Frozen12cases,3paired observers each, full53field raw comparison. No optimizer or speed claim.','evidence':[]});s.update(updated_at=old.now(),state='running',active_experiment='D110',stage='Profile accepted GPU-plan construction',activity='CPU-only off-tree diagnostic; all accepted/main/live source bytes preserved.');old.ar.atomic_json(old.ar.STATUS,s)
 old.child(P['command'],B,'rustc',old.env(),600);verify();bh=old.sha(B/'probe.exe');old.save(B/'complete.json',{'at':old.now(),'binary_sha256':bh,'compile_terminal':True})
 results=[]
 for case in P['cases']:
  verify();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>P['reserve_free_bytes'];old.pin(B/'probe.exe',bh);label=f'case-{case:02d}'
  print('D110 CPU case '+str(case)+' started',flush=True)
  old.child([str(B/'probe.exe'),str(case),str(E/(label+'.bin'))],E,label,old.env(),180)
  lines=[json.loads(x.split('D110 ',1)[1]) for x in (E/(label+'.stdout.log')).read_text().splitlines() if 'D110 ' in x];assert len(lines)==1;v=lines[0]
  assert v['id']==case and v['all53fields_bitwise_equal'] and v['all_vec_capacities_equal'] and v['struct_size_equal'];assert len(v['baseline_samples_ms'])==len(v['profile_samples_ms'])==len(v['stage_spans_ms'])==3
  v['observer_difference_ms']=v['profile_plan_ms']-v['baseline_plan_ms'];v['observer_tolerance_ms']=max(0.1*v['baseline_plan_ms'],0.05);v['observer_pass']=abs(v['observer_difference_ms'])<=v['observer_tolerance_ms']
  v['raw_sha256']=old.sha(E/(label+'.bin'));v['raw_bytes']=(E/(label+'.bin')).stat().st_size;results.append(v)
  print(json.dumps({'case':case,'baseline_ms':v['baseline_plan_ms'],'profile_ms':v['profile_plan_ms'],'observer_pass':v['observer_pass'],'raw_MB':v['raw_bytes']/1e6}),flush=True)
 verify();old.save(H/'native-report.json',{'at':old.now(),'status':'pass_scoped_plan_diagnostic' if all(v['observer_pass'] for v in results) else 'observer_gate_failed_diagnostic_only','protocol_sha256':ph,'cases':results,'all_owned_children_terminal':True,'native_processes':12,'gpu_executions':0,'new_optimizer':False,'speedup_accepted':False,'source_activated':False})
 print(json.dumps({'status':old.read(H/'native-report.json')['status'],'report_sha256':old.sha(H/'native-report.json')}),flush=True)