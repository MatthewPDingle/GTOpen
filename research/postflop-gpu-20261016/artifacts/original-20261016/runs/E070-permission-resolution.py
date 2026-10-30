"""Publish operational native execution and distinguish stale goal state."""
import json,shutil,subprocess,sys,urllib.request
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (R/'gpu-run.lock').exists()
P=R/'runs/E070-primary-manager/primary.exit.json';receipt=old.read(P)
assert receipt['returncode']==0 and receipt['error'] is None and receipt['cleanup'] is None
W=old.read(R/'runs/E070-primary-wrapper/complete.json');assert W['all_children_terminal'] and W['decision']=='rejected'
D=old.read(R/'runs/E070-initial-closure/decision.json');assert D['performance']['observed_gain_pct']==0.8551867596000117
assert D['performance']['primary_timing_pass'] is False and all(not x['failed'] for x in D['performance']['fixture_regression_guard'])
out=R/'runs/E070-permission-resolution';out.mkdir()
proof={'at':old.now(),'status':'native_full_access_execution_operational','effective_session_permissions':{'sandbox_mode':'danger-full-access','approval_policy':'never','source':'Current authoritative developer permission context'},'commands_issued_without_sandbox_permissions':True,'security_configuration_or_database_modified':False,'current_native_execution_denials':0,'current_approval_requests':0,'isolated_build_phases_completed':2,'direct_GPU_case_pairs_passed':5953,'ordinary_units_passed':84,'primary_complete_solve_processes_completed':6,'primary_complete_fixture_results_exact':18,'primary_convergence_records_exact':138,'primary_gain_pct':D['performance']['observed_gain_pct'],'candidate_rejected_below_one_percent':True,'candidate_adopted':False,'accepted_candidate':'E051','accepted_cumulative_gain_pct':12.4372274192464,'all_owned_children_terminal':True,'GPU_lock_absent':True,'accepted_main_live_PTX_custody_pass':True,'evidence_sha256':{str(p):old.sha(p) for p in [P,R/'runs/E070-final-build/complete.json',R/'runs/E070-input-contract-correction/complete.json',R/'runs/E070-primary-wrapper/complete.json',R/'runs/E070-initial-closure/decision.json',R/'comparisons/E070-root-crosscheck/report.json']},'goal_controller':{'observed_status':'blocked','observed_through':'get_goal tool, after completed native E070 execution','permission_failure_cause_removed':True,'model_resume_tool_available':False,'user_control':'/goal resume','official_documentation':'https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex'},'limits':'Successful full-access execution proves the current execution path works; it does not identify the internal rule behind historical blocked-by-policy failures. No live server deployment or application restart performed.'}
old.save(out/'resolution.json',proof)
def publish(src,key):
 dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==src.read_bytes()
 else:shutil.copyfile(src,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==src.read_bytes()
 return {'url':'evidence/'+key,'sha256':old.sha(src)}
published=publish(out/'resolution.json',out.name+'/resolution.json')
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS)
 st.update(updated_at=old.now(),state='blocked',goal_status='blocked',active_experiment=None,stage='Execution restored; automatic goal continuation awaits resume',activity='Full access/never is operational:5953GPU control pairs, two builds,84ordinary tests and six complete-solve processes finished without approval prompts. E070 measured0.855187%, below1%; rejected. Saved goal still reports its old blocked state and requires native /goal resume once for automatic continuation. E051 accepted benchmark gain remains12.437227%; all owned children terminal.')
 st['execution_permissions']={'status':'operational','approval_policy':'never','full_access':True,'evidence':'evidence/'+out.name+'/resolution.json'}
 st['evidence'].append({'label':'Full-access execution verified; remaining goal resume control','url':'evidence/'+out.name+'/resolution.json'})
 old.ar.atomic_json(old.ar.STATUS,st)
with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/status.json',timeout=15) as response:assert response.read()==old.ar.STATUS.read_bytes()
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes()
entry='\n\nNative E070 manager terminal0 and full accepted/main/live/PTX custody verified. Current danger-full-access/never executed without sandbox override fields or approval prompts; no security settings/database edits. Historical internal deny rule remains unknown. get_goal still reports the old blocked controller state after successful research; resume belongs to native user/system control, with no model resume tool. Status separates operational execution from automatic continuation awaiting /goal resume; no new approval requested. Resolution evidence published and served bytes verified.\n'
nl=b'\r\n' if b'\r\n' in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl))
subprocess.run(['git','commit','--only','-m','research: qualify E070 metadata trial and restore native execution','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True)
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=old.REPO,text=True).strip()
old.save(out/'commit.json',{'at':old.now(),'commit':commit,'scope':'Research ledger only; no push or live deployment.'})
publish(out/'commit.json',out.name+'/commit.json');old.custody()
old.save(out/'publication.json',{'at':old.now(),'resolution':published,'served_status_exact':True,'all_owned_children_terminal':True,'source_main_live_PTX_unchanged':True})
print(json.dumps({'native_full_access_operational':True,'E070_gain_pct':D['performance']['observed_gain_pct'],'E070_decision':'rejected','goal_controller_observed':'blocked','goal_resume_user_control':'/goal resume','research_ledger_commit':commit}),flush=True)
