"""Repair only the metadata reader; retain compilers/tests/case0 and run remaining cases."""
from pathlib import Path
import ast,json,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
H=R/'runs/E077-plan-control';E=H/'execution';B=H/'build';M=R/'runs/E077-host-manager-r2';old.custody();assert not(R/'gpu-run.lock').exists()and not M.exists()
P0=old.read(H/'protocol.json')
for p,h in P0['input_sha256'].items():old.pin(p,h)
receipt=old.read(R/'runs/E077-host-manager/host.exit.json');assert receipt['returncode']==1
assert 'TypeError: can only extend with array of same kind'in(R/'runs/E077-host-manager/host.stderr.log').read_text(encoding='utf-8')
for folder,label in [(B,'rustc'),(B,'rustc-tests'),(E,'unit'),(E,'case-00')]:
 q=old.read(folder/(label+'.exit.json'));assert q['returncode']==0 and q['error']is q['cleanup']is None
assert sorted(p.name for p in E.glob('case-*.bin'))==['case-00.bin']and 'test result: ok. 3 passed;'in(E/'unit.stdout.log').read_text(encoding='utf-8')
code=(H/'replay.py').read_text(encoding='utf-8');assert code.count('original.extend(a)')==code.count('encoded.extend(b)')==1
code=code.replace('original.extend(a)','original.extend(int(x) for x in a)').replace('encoded.extend(b)','encoded.extend(int(x) for x in b)');ast.parse(code);(H/'replay_r2.py').write_text(code,encoding='utf-8',newline='\n')
old.save(H/'reader-amendment.json',{'at':old.now(),'original_protocol_sha256':old.sha(H/'protocol.json'),'original_reader_sha256':old.sha(H/'replay.py'),'corrected_reader_sha256':old.sha(H/'replay_r2.py'),'error':'Python array(Q).extend(array(I)) rejects a different typecode before reading the candidate raw data. Replace only this container conversion with an integer iterator.','retained_successful_work':'Both compilers, three-test native process and native case00 terminal0; saved case00 raw bytes reused. No rebuild, test rerun or case00 native reexecution.','remaining_native_cases':list(range(1,12)),'source_inputs_maps_case_order_and_validation_criteria_unchanged':True,'no_performance_samples':True})
runner=r'''from pathlib import Path
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
'''
ast.parse(runner);(H/'execute-r2.py').write_text(runner,encoding='utf-8',newline='\n')
inputs=dict(P0['input_sha256'])
for p in [Path(__file__),H/'protocol.json',H/'replay_r2.py',H/'reader-amendment.json',H/'execute-r2.py',B/'probe.exe',B/'tests.exe',B/'rustc.exit.json',B/'rustc-tests.exit.json',E/'unit.stdout.log',E/'unit.exit.json',E/'case-00.bin',E/'case-00.stdout.log',E/'case-00.exit.json',R/'runs/E077-host-manager/host.exit.json',R/'runs/E077-host-manager/host.stderr.log']:inputs[str(p)]=old.sha(p)
P={'id':'E077-plan-control-r2','at':old.now(),'status':'FROZEN_PRE_REMAINING_NATIVE_CASES','input_sha256':inputs,'models':P0['models'],'scope':'Reuse both original compilers, three tests and raw native case00; corrected reader replays case00, runs only original remaining native cases01..11, replays each. No source/input/criteria/case/order change, no native sample repeated.','candidate_accepted':False};old.save(H/'protocol-r2.json',P)
for p in [H/'replay_r2.py',H/'reader-amendment.json',H/'execute-r2.py',H/'protocol-r2.json']:
 key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
M.mkdir();print('E077 reader-repair protocol',old.sha(H/'protocol-r2.json'),flush=True);old.child([sys.executable,'-B',str(H/'execute-r2.py'),old.sha(H/'protocol-r2.json')],M,'host',old.env(),1800);old.custody();print('E077 host reader repair and remaining cases complete.',flush=True)
