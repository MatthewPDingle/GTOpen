"""One compile and12CPU-only fresh processes, retain every fixed observation."""
import json,shutil,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
def verify():
 old.pin(H/'protocol.json',sys.argv[1])
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody()
verify();B=H/'build';E=H/'execution';assert not B.exists() and not E.exists()
with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=82*1024**3;B.mkdir();E.mkdir()
 old.child(P['command'],B,'rustc',old.env(),600);verify();binary=old.sha(B/'probe.exe')
 old.save(B/'complete.json',{'at':old.now(),'binary_sha256':binary,'compiler_terminal':True,'native_executions':0,'production_source_activated':False})
 results=[]
 for case in P['cases']:
  verify();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=66*1024**3
  label=f'case-{case:02d}';old.pin(B/'probe.exe',binary)
  old.child([str(B/'probe.exe'),str(case),str(E/(label+'.bin'))],E,label,old.env(),180)
  verify();rows=[json.loads(x.split('D112 ',1)[1]) for x in (E/(label+'.stdout.log')).read_text(encoding='utf-8').splitlines() if x.startswith('D112 ')];assert len(rows)==1;v=rows[0]
  assert v['id']==case and v['fields']==53 and v['all52nonorder_fields_bitwise_equal'] and v['all_vec_capacities_equal'] and v['struct_size_equal']
  assert v['measured_pairs']==9 and v['warmup_pairs']==2 and len(v['baseline_samples_ms'])==len(v['candidate_samples_ms'])==9
  assert v['gpu_executions']==0 and v['full_cycle_performance_measured'] is False
  results.append(v);old.save(E/(label+'.result.json'),v)
  print(json.dumps({'case':case,'baseline_plan_ms':v['baseline_plan_ms'],'candidate_plan_ms':v['candidate_plan_ms'],'all52nonorder_fields_exact':True}),flush=True)
 old.save(H/'native-report.json',{'at':old.now(),'id':P['id'],'status':'native_complete_pending_raw_root_replay','protocol_sha256':sys.argv[1],'binary_sha256':binary,'cases':results,'raw_sha256':{p.name:old.sha(p) for p in E.glob('*.bin')},'all_owned_children_terminal':True,'source_activated':False,'gpu_executions':0,'full_cycle_performance_measured':False,'optimization_accepted':False})
 verify();print('D112all12native cases terminal; raw root replay pending; no CPU speed acceptance.',flush=True)
