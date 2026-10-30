"""One fixed CPU-only compiler/test/cohort; no variant, extension or GPU execution."""
from pathlib import Path
import json,shutil,statistics,sys
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
 old.child([str(B/'tests.exe'),'--test-threads=1'],E,'unit',old.env(),300);verify()
 assert 'test result: ok. 2 passed;'in (E/'unit.stdout.log').read_text(encoding='utf-8')
 results=[];binary=old.sha(B/'probe.exe')
 for case in range(12):
  verify();old.ar.refuse_active(old.ar.live_status());old.pin(B/'probe.exe',binary)
  label=f'case-{case:02d}';raw=E/(label+'.bin');old.child([str(B/'probe.exe'),str(case),str(raw)],E,label,old.env(),240);verify()
  r=replay(raw,case,P['references'][case]['path']);r['raw_sha256']=old.sha(raw)
  markers=[json.loads(x.split('D123 ',1)[1])for x in (E/(label+'.stdout.log')).read_text(encoding='utf-8').splitlines()if x.startswith('D123 ')]
  assert len(markers)==1;m=markers[0];assert m['id']==case and m['all53_fields_bitwise_equal']and m['all_vec_capacities_equal']and m['struct_size_equal']
  times=m['measured_pairs'];assert len(times)==9
  for i,t in enumerate(times):assert t['pair']==i and t['first']==('candidate'if(case+i)%2 else'baseline')and t['baseline_ms']>0 and t['candidate_ms']>0
  r.update(board=m['board'],iso_requested=m['iso_requested'],iso_active=m['iso_active'],full_arenas=m['full_arenas'],nodes=m['nodes'],measured_pairs=times,baseline_median_ms=statistics.median(t['baseline_ms']for t in times),candidate_median_ms=statistics.median(t['candidate_ms']for t in times),median_paired_saving_ms=statistics.median(t['baseline_ms']-t['candidate_ms']for t in times))
  r['saving_of_medians_ms']=r['baseline_median_ms']-r['candidate_median_ms'];results.append(r);old.save(E/(label+'.replay.json'),r)
  print(json.dumps({k:r[k]for k in ['case','board','iso_active','full_arenas','baseline_median_ms','candidate_median_ms','saving_of_medians_ms','median_paired_saving_ms']}),flush=True)
 canonical=[results[i]for i in [2,6,10]];saving=sum(c['saving_of_medians_ms']for c in canonical)
 admit=saving>=P['component_admission']['minimum_sum_canonical_saving_ms']and all(c['saving_of_medians_ms']>=0 and c['median_paired_saving_ms']>=0 for c in canonical)
 report={'id':'D123','at':old.now(),'status':'admit_one_integrated_trial_component_screen_only'if admit else'decline_CPU_component_saving_budget_not_met','protocol_sha256':sys.argv[1],'binary_sha256':binary,'cases':results,'canonical_case_ids':[2,6,10],'canonical_sum_CPU_plan_saving_ms':saving,'required_component_saving_ms':P['component_admission']['minimum_sum_canonical_saving_ms'],'admit_one_integrated_trial':admit,'original_and_candidate_plan_tests_pass':True,'all53_values_capacities_structs_match_retained_accepted':True,'all12_fixed_CPU_processes_completed':True,'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'GPU_or_solver_executions':0,'complete_solve_performance_measured':False,'candidate_accepted':False,'excluded_samples':[],'extension_runs':0,'limits':'CPU planner component screen only. Predetermined saving budget is a screening heuristic, not a hardware/headroom bound, necessary condition, causal attribution, accepted speedup or complete-solve qualification. No allocator physical/temporary/driver peak or native GPU evidence. Fixed9 pairs per each12 cases retained. No source/layout/initialization/helper/threshold variants or extra samples after a failed control or component gate.'};old.save(H/'report.json',report);verify()
print(json.dumps({k:report[k]for k in ['status','canonical_sum_CPU_plan_saving_ms','required_component_saving_ms','admit_one_integrated_trial']}),flush=True)
