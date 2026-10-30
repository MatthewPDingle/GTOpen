from pathlib import Path
import json,shutil,sys
H=Path(__file__).resolve().parent;R=H.parent.parent;sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
from replay import replay
assert len(sys.argv)==2;old.pin(H/'protocol-r2.json',sys.argv[1]);P=old.read(H/'protocol-r2.json');B=H/'build';E=H/'execution'
def verify():
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody()
verify();assert B.exists()and E.exists()and not(H/'report.json').exists()
with old.ar.exclusive_lock(R/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
 old.pin(B/'probe.exe',P['retained_probe_sha256']);old.child(P['test_r2_compile_command'],B,'rustc-tests-r2',old.env(),600);verify()
 old.child([str(B/'marker-tests-r2.exe'),'--exact','marker_controls::fold_producer_markers_are_private_and_exact','--test-threads=1'],E,'unit-r2',old.env(),300);verify();unit=(E/'unit-r2.stdout.log').read_text(encoding='utf-8');assert '1 passed; 0 failed'in unit and 'fold_producer_markers_are_private_and_exact ... ok'in unit
 results=[]
 for spec in P['cases']:
  case=spec['id'];label=f'case-{case:02d}';raw=E/(label+'.bin');old.pin(spec['reference'],spec['reference_sha256']);old.ar.refuse_active(old.ar.live_status());old.child([str(B/'probe.exe'),str(case),str(raw)],E,label,old.env(),240);verify();r=replay(raw,case,spec['reference']);r.update(raw_sha256=old.sha(raw),raw_bytes=raw.stat().st_size);old.save(E/(label+'.replay.json'),r);results.append(r);print(json.dumps({k:r[k]for k in['case','root_checks','accepted_baseline_words','exact_private_fold_markers']}),flush=True)
 report={'id':'E078-plan-control','at':old.now(),'status':'pass_compiled_private_fold_marker_full_metadata','protocol_sha256':sys.argv[1],'cases':results,'original_public_plan_values_unchanged':True,'all53baselinefields_match_retained_accepted':True,'all52otherfields_values_and_all53capacities_structs_exact':True,'exact_private_marker_count':sum(x['exact_private_fold_markers']for x in results),'baseline_encoded_words':sum(x['accepted_baseline_words']for x in results),'root_checks':sum(x['root_checks']for x in results),'raw_bytes':sum(x['raw_bytes']for x in results),'source_unit_and_both_plan_units_pass':True,'native_processes':13,'Rust_compilers_total_including_original':3,'original_failed_unit_preserved':True,'already_passed_original_plan_tests_not_repeated':True,'retained_probe_binary_not_rebuilt':True,'test_fixture_amendment_sha256':old.sha(H/'test-fixture-amendment.json'),'all_owned_children_terminal':True,'GPU_or_solver_executions':0,'performance_measured':False,'source_activated':False,'candidate_accepted':False,'source_main_live_PTX_custody_pass':True,'limits':'Two exactaccepted source plan modules/customacceptedgame/retainedRLIB and exactcandidatehostmarker plus sourceunit compiled off-tree. Fullactual53field/capacity/struct/reference replay, not compiledintegratedGpuSolverconstructor/kernelcaller, GPUstate/numeric/speed ormaterialproof. AllGPUraw/broad/completecycle/material gates remain.'};old.save(H/'report.json',report);verify()
print('E078host controls terminal: all12fullmetadata maps and units pass',flush=True)
