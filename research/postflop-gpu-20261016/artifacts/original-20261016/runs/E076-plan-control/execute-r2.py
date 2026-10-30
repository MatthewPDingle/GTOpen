"""One compiler per fixed probe/test and twelve CPU-only complete metadata controls."""
from pathlib import Path
import json,shutil,sys
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
from replay import replay
assert len(sys.argv)==2;old.pin(H/'protocol-r2.json',sys.argv[1]);P=old.read(H/'protocol-r2.json')
def verify():
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody()
verify()
with old.ar.exclusive_lock(R/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
 B=H/'build';E=H/'execution';assert not B.exists()and not E.exists();B.mkdir();E.mkdir()
 for label,cmd in P['compile_commands'].items():old.child(cmd,B,label,old.env(),600);verify()
 old.child([str(B/'tests.exe'),'--test-threads=1'],E,'unit',old.env(),300)
 verify();assert 'test result: ok.'in (E/'unit.stdout.log').read_text(encoding='utf-8')
 results=[];binary=old.sha(B/'probe.exe')
 for case in range(12):
  verify();old.ar.refuse_active(old.ar.live_status());old.pin(B/'probe.exe',binary)
  label=f'case-{case:02d}';raw=E/(label+'.bin')
  old.child([str(B/'probe.exe'),str(case),str(raw)],E,label,old.env(),180)
  verify();model=P['models'][case]
  r=replay(raw,case,model['reference'],model['map']);r['raw_sha256']=old.sha(raw)
  old.save(E/(label+'.replay.json'),r);results.append(r)
  print(json.dumps(r),flush=True)
 assert len(results)==12
 old.save(H/'report.json',{'id':'E076-plan-control','at':old.now(),'status':'pass_compiled_CFV_layout_against_retained_model','protocol_sha256':sys.argv[1],'binary_sha256':binary,'cases':results,'all_51_other_fields_values_capacities_structs_exact':True,'all_12_baseline_fields_match_retained':True,'all_12_CFV_maps_match_frozen_D122':True,'original_and_candidate_plan_unit_tests_pass':True,'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'GPU_or_solver_executions':0,'performance_measurement':False,'candidate_accepted':False,'limits':'Full CPU metadata and compiled plan invariant controls only. No GPU numeric/alias/NaN proof, actual CPU temporary peak/capacity/responsiveness or complete-solve speed claim. Root decoder is not an external independent auditor.'});verify()
print('E076 CPU metadata and invariant controls terminal; no GPU/speed result.',flush=True)
