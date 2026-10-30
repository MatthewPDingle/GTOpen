"""Run one frozen compiler, ability process and six ordered component processes."""
from pathlib import Path
import json,shutil,statistics,sys
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
from replay import replay
assert len(sys.argv)==2;old.pin(H/'execution-plan.json',sys.argv[1]);P=old.read(H/'execution-plan.json');B=H/'build';E=H/'execution'

def verify():
    for p,h in P['input_sha256'].items():old.pin(p,h)
    old.custody()
def markers(path):return[json.loads(x.split('D131 ',1)[1])for x in path.read_text(encoding='utf-8').splitlines()if x.startswith('D131 ')]

verify();assert not B.exists()and not E.exists()
with old.ar.exclusive_lock(R/'gpu-run.lock'):
    old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
    B.mkdir();E.mkdir();old.child(P['rustc_command'],B,'rustc',old.env(),600);verify();binary=B/'probe.exe';bsha=old.sha(binary)
    old.child([str(binary),'ability'],E,'ability',old.env(),120);verify();a=markers(E/'ability.stdout.log');assert len(a)==1;a=a[0]
    assert a['stage']=='ability'and a['lifecycle_cases']==12 and a['predicate_cases']==15 and a['wrong_store_tokens_rejected']==14
    assert a['full_words_checked']==7308 and a['all_full_words_before_after_exact']and a['setup_stays_on_caller']and a['cleanup_and_setup_error_priority_pass']and a['CUDA_or_application_executions']==0
    assert len(a['full_images'])==14 and sum(len(x['before'])+len(x['after'])for x in a['full_images'])==7308
    for x in a['full_images']:assert x['before']==x['after']and len(x['before'])==261
    old.save(H/'ability-report.json',{'at':old.now(),'status':'pass_12_lifecycle_15_predicates_14_wrong_tokens_and_7308_full_words','actual':a,'limits':'Actual OS thread-spawn failure and driver-error/resource exhaustion are source-reviewed, not injected. No CUDA in ability process.'})
    results={};raws=[];reference_images={}
    for spec in P['order']:
        verify();old.pin(binary,bsha);old.ar.refuse_active(old.ar.live_status());label=spec['id'];folder=E/label;assert not folder.exists()
        old.child([str(binary),spec['arm'],str(folder)],E,label,old.env(),300);verify();m=markers(E/(label+'.stdout.log'))
        assert len(m)==4 and m[-1]=={'stage':'complete','arm':spec['arm'],'fixtures':3,'application_kernel_launches':0,'GPU_solver_executions':0,'performance_is_full_solve':False};rows=m[:-1]
        for i,row in enumerate(rows):
            raw=folder/f'fixture-{i}.bin'
            assert row['stage']=='zero_setup_component'and row['fixture_index']==i and row['arm']==spec['arm']and row['raw_layout']==str(raw)
            assert row['overlap_eligible']==(spec['arm']=='overlap'and row['q_bytes']>=P['screen']['minimum_total_q_bytes'])
            assert row['component_ms']>0 and row['process_CPU_ms']>=0 and row['application_kernel_launches']==row['GPU_solver_executions']==0 and not row['performance_is_full_solve']
            assert row['setup_CUDA_calls_stay_on_caller']and row['all_original_full_predicates_and_guards']==[True]*4
            assert row['process_CPU_ms']==(row['cpu_after_ticks100ns']-row['cpu_before_ticks100ns'])/10000
            z=replay(raw,i,row['full_private_layout_words_per_arm']);signature=[x['image_sha256']for x in z['images']]
            if i in reference_images:assert signature==reference_images[i]
            else:reference_images[i]=signature
            z.update(id=label,fixture_index=i,raw_path=str(raw));old.save(folder/f'fixture-{i}-replay.json',z);raws.append(z)
        results[label]=rows;old.save(E/(label+'.replay.json'),{'at':old.now(),'rows':rows,'all_full_layout_and_counter_invariants_pass':True,'stdout_sha256':old.sha(E/(label+'.stdout.log'))})
        print(json.dumps({'id':label,'component_ms':[x['component_ms']for x in rows],'all_thread_CPU_ms':[x['process_CPU_ms']for x in rows]}),flush=True)
    fixtures=[]
    for i in range(3):
        bs=[results[f'D131B{k}'][i]for k in range(1,4)];cs=[results[f'D131T{k}'][i]for k in range(1,4)]
        assert all((x['board'],x['nodes'],x['q_bytes'],x['pinned_bytes'])==(bs[0]['board'],bs[0]['nodes'],bs[0]['q_bytes'],bs[0]['pinned_bytes'])for x in bs+cs)
        bm=statistics.median(x['component_ms']for x in bs);cm=statistics.median(x['component_ms']for x in cs)
        bcpu=statistics.median(x['process_CPU_ms']for x in bs);ccpu=statistics.median(x['process_CPU_ms']for x in cs)
        paired=[x['component_ms']-y['component_ms']for x,y in zip(bs,cs)];eligible=bs[0]['q_bytes']>=P['screen']['minimum_total_q_bytes']
        limit=bcpu*P['screen']['maximum_CPU_median_ratio']+P['screen']['CPU_median_allowance_ms']
        fixtures.append({'fixture_index':i,'board':bs[0]['board'],'nodes':bs[0]['nodes'],'q_bytes':bs[0]['q_bytes'],'overlap_applicable':eligible,'baseline_component_ms':[x['component_ms']for x in bs],'candidate_component_ms':[x['component_ms']for x in cs],'baseline_median_ms':bm,'candidate_median_ms':cm,'saving_of_medians_ms':bm-cm,'paired_saving_ms':paired,'improving_pairs':sum(x>0 for x in paired),'wall_guard_pass':not eligible or(bm>cm and sum(x>0 for x in paired)>=2),'baseline_CPU_ms':[x['process_CPU_ms']for x in bs],'candidate_CPU_ms':[x['process_CPU_ms']for x in cs],'baseline_CPU_median_ms':bcpu,'candidate_CPU_median_ms':ccpu,'CPU_limit_ms':limit,'CPU_guard_pass':not eligible or ccpu<=limit})
    saving=sum(x['saving_of_medians_ms']for x in fixtures)
    admit=saving>=P['screen']['minimum_sum_fixture_median_saving_ms']and all(x['wall_guard_pass']and x['CPU_guard_pass']for x in fixtures)
    status='admit_one_integrated_zero_validation_overlap_trial_component_only'if admit else'decline_zero_validation_overlap_component_wall_budget_or_CPU_guard'
    report={'id':'D131','at':old.now(),'status':status,'protocol_sha256':sys.argv[1],'binary_sha256':bsha,'results':results,'fixtures':fixtures,'sum_fixture_component_saving_ms':saving,'required_component_saving_ms':P['screen']['minimum_sum_fixture_median_saving_ms'],'admit_one_integrated_trial':admit,'full_layout_raw_replays':raws,'raw_bytes':sum(x['raw_bytes']for x in raws),'encoded_words_checked':sum(x['encoded_words']for x in raws),'root_checks':sum(x['checks']for x in raws),'fixed_six_fresh_processes_complete':True,'ability_lifecycle_controls':12,'ability_predicate_controls':15,'ability_wrong_store_tokens':14,'ability_full_words':7308,'native_component_processes':6,'CUDA_context_stream_pairs':18,'application_kernel_launches':0,'GPU_solver_executions':0,'performance_is_full_solve':False,'source_activated':False,'candidate_accepted':False,'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'excluded_samples':[],'extension_runs':0,'limits':'This component includes the original full serial predicates and actual NVRTC/module/pinned/layout setup. It omits device arena allocations/uploads and full solving, so its timing is not a full-solve claim. CUDA stays on the caller, one CPU worker retains all original scans, and full layout fields/capacities match original reference construction after every clock. CPU counts cover all process threads and retain raw quantized values. Spawn failure and actual driver exhaustion remain source-reviewed. Broad exactness/F32/state/menu/save/resume/continuation and actual CPU/host/GPU peak/capacity/responsiveness, full-cycle strict fixture/fresh16/holdout/cumulative gates remain mandatory. Fixed screening budget and CPU guard cannot prove no tradeoffs. No rescue variants or extra samples after a failed screen.'}
    old.save(H/'report.json',report);verify()
print(json.dumps({'status':status,'saving_ms':saving,'admit_integrated':admit,'raw_bytes':report['raw_bytes']}),flush=True)
