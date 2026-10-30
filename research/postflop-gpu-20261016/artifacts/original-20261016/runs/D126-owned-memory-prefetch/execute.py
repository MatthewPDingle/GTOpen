"""One fixed Windows ability/process cohort; component timing is not solve timing."""
from pathlib import Path
import json,shutil,statistics,subprocess,sys,urllib.request
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
assert len(sys.argv)==2;old.pin(H/'execution-plan.json',sys.argv[1]);P=old.read(H/'execution-plan.json')
def verify():
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody()
def read_markers(path):
 return [json.loads(x.split('D126 ',1)[1])for x in path.read_text(encoding='utf-8').splitlines()if x.startswith('D126 ')]
verify();B=H/'build';E=H/'execution';assert not B.exists()and not E.exists()
with old.ar.exclusive_lock(R/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3;B.mkdir();E.mkdir()
 old.child(P['rustc_command'],B,'rustc',old.env(),600);verify();binary=B/'probe.exe';binary_sha=old.sha(binary)
 old.save(B/'complete.json',{'at':old.now(),'binary_sha256':binary_sha,'protocol_sha256':sys.argv[1],'native_executions':0})
 old.child([str(binary),'ability'],E,'ability',old.env(),120);verify()
 records=read_markers(E/'ability.stdout.log');assert len(records)==1;ability=records[0]
 assert ability['stage']=='ability'and ability['prefetch_calls']==1 and ability['owned_range_bytes']==8192
 expected=[(i*73+17)&65535 for i in range(4128)]
 assert ability['full_before_u16']==ability['full_after_u16']==expected and ability['all_guards_and_data_exact']
 assert ability['predicate_controls']==15 and ability['range_struct_bytes']==16 and ability['memory_counter_bytes']==72
 old.save(H/'ability-report.json',{'at':old.now(),'status':'pass_owned_API_and_predicate_ability'if ability['prefetch_success']else'decline_API_unavailable','actual':ability,'all_full_owned_words_exact':True,'binary_sha256':binary_sha,'GPU_executions':0,'full_solve_performance_measured':False})
 results={};API_failure=None
 if ability['prefetch_success']:
  for spec in P['order']:
   verify();old.ar.refuse_active(old.ar.live_status());old.pin(binary,binary_sha)
   label=spec['id'];old.child([str(binary),spec['arm']],E,label,old.env(),180);verify()
   markers=read_markers(E/(label+'.stdout.log'));assert len(markers)==4 and markers[-1]=={'GPU_executions':0,'arm':spec['arm'],'fixtures':3,'full_solve_performance_measured':False,'stage':'complete'}
   rows=markers[:-1]
   for i,row in enumerate(rows):
    assert row['stage']=='CPU_zero_scan'and row['fixture_index']==i and row['arm']==spec['arm']and row['all4_original_full_checks_pass']==[True]*4 and row['GPU_executions']==0 and row['full_solve_performance_measured']is False
    assert row['component_ms']>0 and 0<=row['prefetch_ms_contained']<=row['component_ms']
    assert row['before']['peak_working_set_bytes']<=row['after']['peak_working_set_bytes']and row['after']['working_set_bytes']<=row['after']['peak_working_set_bytes']
    assert row['process_page_fault_delta']==(row['after']['page_faults']-row['before']['page_faults'])%(2**32)
    if spec['arm']=='baseline':assert row['prefetch_calls']==0 and row['prefetch_bytes']==0
    elif row['q_bytes']>=P['component_admission']['minimum_total_prefetch_bytes']:
     assert row['prefetch_calls']==1 and row['prefetch_range_count']==4 and row['prefetch_bytes']==row['q_bytes']
     if not row['prefetch_success']:API_failure={'id':label,'fixture':i,'error':row['prefetch_error']}
    else:assert row['prefetch_calls']==0 and row['prefetch_bytes']==0
   results[label]=rows;old.save(E/(label+'.replay.json'),{'at':old.now(),'id':label,'all_row_geometry_counter_predicate_invariants_pass':True,'rows':rows,'stdout_sha256':old.sha(E/(label+'.stdout.log'))})
   print(json.dumps({'id':label,'arm':spec['arm'],'component_ms':[x['component_ms']for x in rows],'page_faults':[x['process_page_fault_delta']for x in rows],'prefetch_ms':[x['prefetch_ms_contained']for x in rows]}),flush=True)
   if API_failure:break
 complete=ability['prefetch_success']and API_failure is None and len(results)==6
 fixtures=[];saving=None;admit=False
 if complete:
  for i in range(3):
   bases=[results[f'D126B{k}'][i]for k in range(1,4)];cands=[results[f'D126T{k}'][i]for k in range(1,4)]
   assert all((r['board'],r['q_bytes'],r['cpu_arena_bytes'],r['nodes'],r['plan_levels'])==(bases[0]['board'],bases[0]['q_bytes'],bases[0]['cpu_arena_bytes'],bases[0]['nodes'],bases[0]['plan_levels'])for r in bases+cands)
   b=statistics.median(x['component_ms']for x in bases);c=statistics.median(x['component_ms']for x in cands);paired=[x['component_ms']-y['component_ms']for x,y in zip(bases,cands)];applicable=bases[0]['q_bytes']>=P['component_admission']['minimum_total_prefetch_bytes']
   fixtures.append({'fixture_index':i,'board':bases[0]['board'],'q_bytes':bases[0]['q_bytes'],'prefetch_applicable':applicable,'baseline_component_raw_ms':[x['component_ms']for x in bases],'candidate_component_raw_ms':[x['component_ms']for x in cands],'baseline_median_ms':b,'candidate_median_ms':c,'saving_of_medians_ms':b-c,'paired_saving_ms':paired,'improving_pairs':sum(x>0 for x in paired),'median_paired_saving_ms':statistics.median(paired),'component_guard_pass':not applicable or(b>c and sum(x>0 for x in paired)>=2),'baseline_faults':[x['process_page_fault_delta']for x in bases],'candidate_faults':[x['process_page_fault_delta']for x in cands],'baseline_working_set_after':[x['after']['working_set_bytes']for x in bases],'candidate_working_set_after':[x['after']['working_set_bytes']for x in cands],'candidate_prefetch_ms_contained':[x['prefetch_ms_contained']for x in cands]})
  saving=sum(x['saving_of_medians_ms']for x in fixtures);admit=saving>=P['component_admission']['minimum_sum_fixture_median_saving_ms']and all(f['component_guard_pass']for f in fixtures)
 status='admit_one_integrated_prefetch_trial_component_only'if admit else('decline_CPU_prefetch_component_budget_or_guard'if complete else'decline_API_or_ability_prerequisite')
 report={'id':'D126','at':old.now(),'status':status,'protocol_sha256':sys.argv[1],'binary_sha256':binary_sha,'ability_report_sha256':old.sha(H/'ability-report.json'),'complete_fixed_six_process_cohort':complete,'API_failure':API_failure,'results':results,'fixtures':fixtures,'sum_fixture_CPU_component_saving_ms':saving,'required_component_saving_ms':P['component_admission']['minimum_sum_fixture_median_saving_ms'],'admit_one_integrated_trial':admit,'native_component_processes':len(results),'new_GPU_or_solver_executions':0,'full_solve_performance_measured':False,'source_activated':False,'candidate_accepted':False,'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'excluded_samples':[],'extension_runs':0,'limits':'Fresh-process CPU-only component model, not production upload execution, full-solve timing or causal fault attribution. Same accepted Spot/Solver/GpuPlan and mimalloc, exact original predicate body. GPU context/pinning/allocations/layout construction absent. Process counters cannot isolate hard faults or OS physical-cache cost. Prefetch eligibility/call/timer overhead included. Preset budget is screening only, not a no-tradeoff or universal headroom bound. All integrated exactness/material/1%/strict-fixture/fresh16/broad/holdout/cumulative gates would remain. No threshold/filter/API/flag/source or sample rescue after failed admission.'};old.save(H/'report.json',report);verify()
print(json.dumps({'status':status,'sum_component_saving_ms':saving,'admit_one_integrated_trial':admit,'native_processes':len(results)}),flush=True)
