"""One compiler per probe/test and exactly12 CPU maps; no GPU/solver timing."""
from pathlib import Path
import json,shutil,sys
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
from replay import replay
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
def verify():
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody()
verify()
with old.ar.exclusive_lock(R/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
 B=H/'build';E=H/'execution';assert not B.exists()and not E.exists();B.mkdir();E.mkdir()
 for label,cmd in P['compile_commands'].items():old.child(cmd,B,label,old.env(),600);verify()
 old.child([str(B/'tests.exe'),'--test-threads=1'],E,'unit',old.env(),300);verify();assert 'test result: ok. 3 passed;'in(E/'unit.stdout.log').read_text(encoding='utf-8')
 binary=old.sha(B/'probe.exe');results=[]
 for case in range(12):
  verify();old.ar.refuse_active(old.ar.live_status());old.pin(B/'probe.exe',binary)
  label=f'case-{case:02d}';raw=E/(label+'.bin');old.child([str(B/'probe.exe'),str(case),str(raw)],E,label,old.env(),180);verify()
  r=replay(raw,case,P['models'][case]['reference'],P['models'][case]['tags']);r['raw_sha256']=old.sha(raw);results.append(r);old.save(E/(label+'.replay.json'),r);print(json.dumps(r),flush=True)
 old.save(H/'report.json',{'id':'E077-plan-control','at':old.now(),'status':'pass_compiled_prefix_tags_against_retained_model','protocol_sha256':sys.argv[1],'binary_sha256':binary,'cases':results,'all52_other_fields_values_capacities_structs_exact':True,'original_public_plan_values_unchanged':True,'all12_compiled_tag_arrays_match_D124':True,'original_and_candidate_plan_tests_pass':True,'plan_tests':3,'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'GPU_or_solver_executions':0,'performance_measurement':False,'candidate_accepted':False,'limits':'Complete CPU metadata and compiled tag controls only. No GPU numerical/state or actual CPU/material/capacity/full-cycle performance conclusion. Root replay is not external independent audit.'});verify()
print('E077 compiled host maps and3 plan tests pass; no GPU numeric/speed result.',flush=True)
