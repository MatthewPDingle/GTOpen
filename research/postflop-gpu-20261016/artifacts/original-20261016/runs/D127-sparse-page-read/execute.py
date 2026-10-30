"""Execute the one frozen sparse read component; no sample extensions or rescue."""
from pathlib import Path
import json,shutil,statistics,struct,sys
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
assert len(sys.argv)==2;old.pin(H/'execution-plan.json',sys.argv[1]);P=old.read(H/'execution-plan.json')
def verify():
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody()
def markers(path):return [json.loads(x.split('D127 ',1)[1])for x in path.read_text(encoding='utf-8').splitlines()if x.startswith('D127 ')]
def replay_images(path):
 raw=path.read_bytes();pos=0
 def take(n):
  nonlocal pos
  assert pos+n<=len(raw);v=raw[pos:pos+n];pos+=n;return v
 assert take(16)==b'D127-PAGE-RAW1\0\0';checks=0;words=0;pages=0
 for signed in [False,True]:
  for length in [0,1,2,2047,2048,2049,4095,4096,4097,8192,8193]:
   for offset in [0,1,15,2047]:
    case,sign,off,n,page,count=struct.unpack('<6I',take(24));start=struct.unpack('<Q',take(8))[0]
    assert(case,sign,off,n)==(checks,int(signed),offset,length)and page>=2 and page&(page-1)==0 and start%2==0
    expected_pages=0 if not length else (start+length*2-1)//page-start//page+1;assert count==expected_pages
    expected=[(i*73+17)&65535 for i in range(offset+length+17)];images=[]
    for j in range(2):
     size=struct.unpack('<Q',take(8))[0];assert size==len(expected);actual=list(struct.unpack('<'+str(size)+'H',take(size*2)));assert actual==expected;images.append(actual);words+=size
    assert images[0]==images[1];checks+=1;pages+=count
 assert pos==len(raw)and checks==88
 return {'cases':checks,'full_before_after_words_checked':words,'touched_pages':pages,'bytes':len(raw),'sha256':old.sha(path)}
verify();B=H/'build';E=H/'execution';assert not B.exists()and not E.exists()
with old.ar.exclusive_lock(R/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3;B.mkdir();E.mkdir()
 old.child(P['rustc_command'],B,'rustc',old.env(),600);verify();binary=B/'probe.exe';binary_sha=old.sha(binary);old.save(B/'complete.json',{'at':old.now(),'binary_sha256':binary_sha,'protocol_sha256':sys.argv[1],'native_executions':0})
 old.child([str(binary),'ability'],E,'ability',old.env(),120);verify();records=markers(E/'ability.stdout.log');assert len(records)==1;a=records[0]
 assert a['stage']=='ability'and a['native_cases']==88 and a['all_full_owned_words_and_guards_exact']and a['predicate_eligibility_controls']==15
 assert(a['system_info_bytes'],a['filetime_bytes'],a['memory_counter_bytes'])==(48,8,72)and a['rayon_threads']==16 and a['cpu_after_ticks100ns']>=a['cpu_before_ticks100ns']
 image=replay_images(E/'ability-images.bin');assert image['touched_pages']==a['touched_pages']
 old.save(H/'ability-report.json',{'at':old.now(),'status':'pass_full_owned_images_ABI_predicate_eligibility_counters','actual':a,'independent_full_raw_replay':image,'binary_sha256':binary_sha,'GPU_executions':0,'full_solve_performance_measured':False})
 results={}
 for spec in P['order']:
  verify();old.ar.refuse_active(old.ar.live_status());old.pin(binary,binary_sha);label=spec['id'];old.child([str(binary),spec['arm']],E,label,old.env(),180);verify()
  m=markers(E/(label+'.stdout.log'));assert len(m)==4 and m[-1]=={'GPU_executions':0,'arm':spec['arm'],'fixtures':3,'full_solve_performance_measured':False,'stage':'complete'};rows=m[:-1]
  for i,row in enumerate(rows):
   assert row['stage']=='CPU_zero_scan'and row['fixture_index']==i and row['arm']==spec['arm']and row['all4_original_full_checks_pass']==[True]*4 and row['GPU_executions']==0 and row['full_solve_performance_measured']is False
   assert row['component_ms']>0 and row['process_cpu_ms']>=0 and row['rayon_threads']==16 and row['page_size']==a['page_size']
   assert row['process_cpu_ms']==(row['cpu_after_ticks100ns']-row['cpu_before_ticks100ns'])/10000
   for left,right in [('before','mid'),('mid','after')]:assert row[left]['peak_working_set_bytes']<=row[right]['peak_working_set_bytes']
   assert row['process_page_fault_delta']==(row['after']['page_faults']-row['before']['page_faults'])%2**32
   assert row['pre_scan_page_fault_delta']==(row['mid']['page_faults']-row['before']['page_faults'])%2**32
   assert row['original_scan_page_fault_delta']==(row['after']['page_faults']-row['mid']['page_faults'])%2**32
   assert row['process_page_fault_delta']==row['pre_scan_page_fault_delta']+row['original_scan_page_fault_delta']
   applicable=spec['arm']=='touch'and row['q_bytes']>=P['component_admission']['minimum_total_touch_bytes']
   if applicable:assert row['touched_q_bytes']==row['q_bytes']and row['q_bytes']//row['page_size']<=row['touched_pages']<=row['q_bytes']//row['page_size']+8
   else:assert row['touched_q_bytes']==row['touched_pages']==0
  results[label]=rows;old.save(E/(label+'.replay.json'),{'at':old.now(),'id':label,'all_geometry_counter_original_predicate_invariants_pass':True,'rows':rows,'stdout_sha256':old.sha(E/(label+'.stdout.log'))})
  print(json.dumps({'id':label,'wall_ms':[x['component_ms']for x in rows],'all_thread_CPU_ms':[x['process_cpu_ms']for x in rows],'pre_scan_faults':[x['pre_scan_page_fault_delta']for x in rows],'original_scan_faults':[x['original_scan_page_fault_delta']for x in rows]}),flush=True)
 fixtures=[]
 for i in range(3):
  bs=[results[f'D127B{k}'][i]for k in range(1,4)];cs=[results[f'D127T{k}'][i]for k in range(1,4)]
  assert all((x['board'],x['q_bytes'],x['cpu_arena_bytes'],x['nodes'],x['plan_levels'])==(bs[0]['board'],bs[0]['q_bytes'],bs[0]['cpu_arena_bytes'],bs[0]['nodes'],bs[0]['plan_levels'])for x in bs+cs)
  b=statistics.median(x['component_ms']for x in bs);c=statistics.median(x['component_ms']for x in cs);paired=[x['component_ms']-y['component_ms']for x,y in zip(bs,cs)];bcpu=statistics.median(x['process_cpu_ms']for x in bs);ccpu=statistics.median(x['process_cpu_ms']for x in cs);applicable=bs[0]['q_bytes']>=P['component_admission']['minimum_total_touch_bytes'];cpulimit=bcpu*P['component_admission']['maximum_CPU_median_ratio']+P['component_admission']['CPU_median_allowance_ms']
  fixtures.append({'fixture_index':i,'board':bs[0]['board'],'q_bytes':bs[0]['q_bytes'],'touch_applicable':applicable,'baseline_wall_ms':[x['component_ms']for x in bs],'candidate_wall_ms':[x['component_ms']for x in cs],'baseline_wall_median_ms':b,'candidate_wall_median_ms':c,'saving_of_medians_ms':b-c,'paired_saving_ms':paired,'improving_pairs':sum(x>0 for x in paired),'wall_guard_pass':not applicable or(b>c and sum(x>0 for x in paired)>=2),'baseline_CPU_ms':[x['process_cpu_ms']for x in bs],'candidate_CPU_ms':[x['process_cpu_ms']for x in cs],'baseline_CPU_median_ms':bcpu,'candidate_CPU_median_ms':ccpu,'CPU_limit_ms':cpulimit,'CPU_guard_pass':not applicable or ccpu<=cpulimit,'baseline_total_faults':[x['process_page_fault_delta']for x in bs],'candidate_total_faults':[x['process_page_fault_delta']for x in cs],'baseline_pre_scan_faults':[x['pre_scan_page_fault_delta']for x in bs],'candidate_pre_scan_faults':[x['pre_scan_page_fault_delta']for x in cs],'baseline_original_scan_faults':[x['original_scan_page_fault_delta']for x in bs],'candidate_original_scan_faults':[x['original_scan_page_fault_delta']for x in cs]})
 saving=sum(x['saving_of_medians_ms']for x in fixtures);admit=saving>=P['component_admission']['minimum_sum_fixture_median_saving_ms']and all(x['wall_guard_pass']and x['CPU_guard_pass']for x in fixtures);status='admit_one_integrated_sparse_read_trial_component_only'if admit else'decline_CPU_sparse_read_wall_budget_or_fixture_or_CPU_cost'
 report={'id':'D127','at':old.now(),'status':status,'protocol_sha256':sys.argv[1],'binary_sha256':binary_sha,'ability_report_sha256':old.sha(H/'ability-report.json'),'complete_fixed_six_process_cohort':True,'results':results,'fixtures':fixtures,'sum_fixture_CPU_component_saving_ms':saving,'required_component_saving_ms':P['component_admission']['minimum_sum_fixture_median_saving_ms'],'admit_one_integrated_trial':admit,'native_component_processes':len(results),'new_GPU_or_solver_executions':0,'full_solve_performance_measured':False,'source_activated':False,'candidate_accepted':False,'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'excluded_samples':[],'extension_runs':0,'limits':'CPU-only isolated source component, not private production upload or full solve. Same accepted Spot/Solver/GpuPlan/RLIB/mimalloc. Original4serialpredicates copied exactly and retained after read-only sparse pass. No CUDA context/pinning/device/layout construction. Mid counters inside both arm windows. Whole-process faults not hard-fault/physical-memory causal attribution. CPU time sums all threads, may exceed wall; process-time granularity and all raw observations retained. Fixed component wall budget and10%+5ms CPU screen do not establish no-tradeoff adoption. Full GPU exact/broad/material/full-cycle1%/strict fixture/fresh16/holdout/cumulative gates remain if admitted. No sample/source/chunk/threshold/thread/helper/API/placement rescue after actual failure.'};old.save(H/'report.json',report);verify()
print(json.dumps({'status':status,'sum_component_saving_ms':saving,'admit_one_integrated_trial':admit,'native_processes':len(results)}),flush=True)
