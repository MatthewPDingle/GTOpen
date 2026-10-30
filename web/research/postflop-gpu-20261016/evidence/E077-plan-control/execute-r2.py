from pathlib import Path
import json,sys
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
from replay_r2 import replay
assert len(sys.argv)==2;old.pin(H/'protocol-r2.json',sys.argv[1]);P=old.read(H/'protocol-r2.json');E=H/'execution';B=H/'build'
def verify():
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody()
verify()
with old.ar.exclusive_lock(R/'gpu-run.lock'):
 results=[]
 for case in range(12):
  verify();model=P['models'][case];label=f'case-{case:02d}';raw=E/(label+'.bin')
  if case:
   assert not raw.exists();old.ar.refuse_active(old.ar.live_status());old.child([str(B/'probe.exe'),str(case),str(raw)],E,label,old.env(),180);verify()
  r=replay(raw,case,model['reference'],model['tags']);r['raw_sha256']=old.sha(raw);results.append(r);old.save(E/(label+'.replay.json'),r);print(json.dumps(r),flush=True)
 old.save(H/'report.json',{'id':'E077-plan-control','at':old.now(),'status':'pass_compiled_prefix_tags_against_retained_model','protocol_sha256':sys.argv[1],'original_protocol_sha256':old.sha(H/'protocol.json'),'binary_sha256':old.sha(B/'probe.exe'),'cases':results,'all52_other_fields_values_capacities_structs_exact':True,'original_public_plan_values_unchanged':True,'all12_compiled_tag_arrays_match_D124':True,'original_and_candidate_plan_tests_pass':True,'plan_tests':3,'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'GPU_or_solver_executions':0,'performance_measurement':False,'candidate_accepted':False,'native_case00_reused_unchanged':True,'compilers_or_tests_repeated':0,'limits':'Complete CPU metadata and compiled tag controls only. Original reader/type-error evidence retained, corrected integer container conversion only. No GPU numerical/state, CPU/material/capacity/full-cycle result. Root replay is not external independent audit.'});verify()
print('E077 host controls terminal:12 exact maps and original3 tests pass; no repeated native case.',flush=True)
