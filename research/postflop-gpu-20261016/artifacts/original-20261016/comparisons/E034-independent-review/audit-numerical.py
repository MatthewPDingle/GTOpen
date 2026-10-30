import pathlib,json,hashlib,datetime,statistics,math,re,csv,collections
ROOT=pathlib.Path(r'S:\GTOpen-research\postflop-gpu-20261016')
OUT=ROOT/'comparisons/E034-independent-review';PLAN=ROOT/'runs/E034-primary-plan';EX=ROOT/'runs/E034-primary-execution'
assert not (OUT/'validation.json').exists() and not (OUT/'summary.md').exists(), 'Preserve any prior audit result'
checks=collections.Counter();artifacts={}
def ck(b,label):
    if not b:raise AssertionError(label)
    checks[label]+=1
def sha(p):
    p=pathlib.Path(p);v=hashlib.sha256(p.read_bytes()).hexdigest();artifacts[str(p)]=v;return v
def load(p):sha(p);return json.loads(pathlib.Path(p).read_text(encoding='utf-8-sig'))
def pin(p,h):ck(sha(p)==h,'artifact_hash')
def dt(x):return datetime.datetime.fromisoformat(x.replace('Z','+00:00'))
def norm(d,exclude):return {k:v for k,v in d.items() if k not in exclude}
def gain(b,c):return 100*(b-c)/b
def close(a,b,label):ck(math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-9),label)
pin(PLAN/'protocol.json','76ab3c0940fb85dbb94855ad28654239861d96a5f8016190c7ae3e13263d2241')
pin(PLAN/'scripts-manifest.json','255ad6bb57df3d92413aad1a1edc3ca5e08a8befd6640166706ec49e07c651ce')
P=load(PLAN/'protocol.json');C=load(ROOT/'comparisons/E034-three-pair-comparison/report.json')
ck(P['order']==['V034-unit','B107','E034R1','E034R2','B108','B109','E034R3'],'fixed_seven_run_order')
ck(P['pairs']==[{'baseline':'B107','candidate':'E034R1'},{'baseline':'B108','candidate':'E034R2'},{'baseline':'B109','candidate':'E034R3'}],'fixed_pairing')
ck(P['expected_unit_passed']==87 and P['expected_unit_ignored']==4,'frozen_unit_counts')
BM={n:load(ROOT/'binaries'/(n+'.manifest.json')) for n in ['E020-postflop_autoresearch','E034-postflop_autoresearch','E034-solver']}
BE=load(ROOT/'runs/E034-build/exit.json');CK=load(ROOT/'runs/E034-compile-check/complete.json')
ck(BE['returncode']==0 and CK['status']=='COMPILE_ONLY_CHECKS_PASSED' and CK['native_executions']==0,'terminal_build_stage_results')
ck(dt(CK['at'])<=dt(BE['at']),'separate_compile_before_primary_build')
INV=load(EX/'invocation.json');DONE=load(EX/'complete.json')
ck(INV['order']==DONE['order']==P['order'] and INV['primary_protocol_sha256']==sha(PLAN/'protocol.json'),'fixed_primary_invocation_completion')
ids=P['order'];runs={};rawstages={};rawresults={};unit_names=[];summary_runtime={}
for identity in ids:
    r=load(ROOT/f'runs/{identity}/report.json');runs[identity]=r
    ck(r['id']==identity and r['status']=='measured' and r['returncode']==0,'successful_physical_run')
    pin(ROOT/f'runs/{identity}/stdout.log',r['stdout_sha256']);pin(r['command'][0],r['binary_sha256'])
    bm=r['binary_build_manifest'];pin(bm['path'],bm['sha256']);ck(bm['data']==load(bm['path']) and bm['binary_hash_verified'] and bm['data']['binary_sha256']==r['binary_sha256'],'runtime_binary_manifest_link')
    which='E034-solver' if identity=='V034-unit' else ('E020-postflop_autoresearch' if identity.startswith('B') else 'E034-postflop_autoresearch')
    ck(bm['data']==BM[which],'right_binary_for_run')
    subinv=load(EX/f'{identity}.invocation.json');subexit=load(EX/f'{identity}.exit.json')
    ck(subexit['returncode']==0 and dt(subinv['at'])<=dt(r['started_at'])<=dt(r['finished_at'])<=dt(subexit['at']),'wrapper_terminal_order')
    ck(r['environment']==C['environment'],'fixed_primary_environment')
    ck(r['environment']['RAYON_NUM_THREADS']=='16' and r['environment']['POSTFLOP_AUTORESEARCH_PROFILE']=='0' and r['environment']['POSTFLOP_AUTORESEARCH_STORAGE']=='compressed' and r['environment']['POSTFLOP_AUTORESEARCH_FIXTURE'] is None,'fixed_workload_environment')
    for live in ['live_status_before','live_status_at_launch']:
        state=r[live];ck(state['/api/status']['state']!='running' and not state['/api/reports/status']['running'],'live_server_not_solving')
    ck(r['disk_free_bytes']>=50*1024**3,'disk_reserve')
    telemetry=r['telemetry_before']['gpu'];ck(telemetry['returncode']==0,'gpu_identity_read')
    gpu=[row[:4] for row in csv.reader(telemetry['stdout'].splitlines(),skipinitialspace=True)];ck(gpu==C['gpu_identity'],'same_GPU_driver')
    text=(ROOT/f'runs/{identity}/stdout.log').read_text(encoding='utf-8');st=[];rs=[]
    for line in text.splitlines():
        for marker,dest in [('AUTORESEARCH_STAGE ',st),('AUTORESEARCH_RESULT ',rs)]:
            if marker in line:dest.append(json.loads(line.split(marker,1)[1]))
    ck(rs==r['results'] and st==[x['data'] for x in r['stages']],'raw_json_exact_report')
    rawstages[identity]=st;rawresults[identity]=rs
    summary=re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out; finished in ([0-9.]+)s',text)
    expected=('87','0','4','0','0') if identity=='V034-unit' else ('1','0','0','0','0')
    ck(len(summary)==1 and tuple(summary[0][:5])==expected,'full_native_test_summary')
    ck(r['test_pass_count']==int(expected[0]),'reported_pass_count')
    summary_runtime[identity]=float(summary[0][-1])
    if identity=='V034-unit':unit_names=sorted(re.findall(r'^test (\S+) \.\.\.',text,re.M));continue
    ck(r['command'][1:]==['postflop_complete_cycle','--nocapture','--test-threads=1','--ignored'],'fixed_native_invocation')
    ck([x['fixture_id'] for x in rs]==['rainbow','two-tone','river'],'fixed_fixture_order')
    ck(len(rs)==3 and [x['iteration'] for x in rs]==[200,200,60] and len([x for x in st if x['stage']=='convergence_check'])==23,'full_three_fixture23_check_completeness')
    ck(st[0]['stage']=='suite_start' and st[0]['primary_suite'] and not st[0]['smoke_only'] and not st[0]['profile_after_timing'] and st[-1]['stage']=='suite_complete' and st[-1]['fixtures_completed']==3,'complete_full_primary_suite')
    for z in rs:
        ck(z['target_met'] and z['target_pct']==0.3 and z['check_every']==20 and z['max_iterations']==400 and z['storage']=='compressed','fixed_quality_settings')
        ck(z['runtime_nvrtc_jit_included'] and z['flushed_progress_logging_included'],'fixed_boundary_flags')
        for field in ['build_ms','init_ms','solve_ms','readback_ms','full_cycle_ms','fingerprint_ms_excluded']:ck(math.isfinite(z[field]) and z[field]>0,'finite_positive_timing')
        timing=next(x for x in st if x['stage']=='timing_complete' and x['fixture_id']==z['fixture_id'])
        for k,v in timing.items():
            if k!='stage':ck(z[k]==v,'raw_stage_final_result_agreement')
for a,b in zip(ids,ids[1:]):ck(dt(runs[a]['finished_at'])<=dt(runs[b]['started_at']),'serialized_chronology')
ck(dt(BE['at'])<dt(runs[ids[0]]['started_at']),'build_terminal_before_unit_and_primary')
priorunit=(ROOT/'runs/V020-unit/stdout.log').read_text(encoding='utf-8')
prior_names=re.findall(r'^test (\S+) \.\.\.',priorunit,re.M)
ck(len(prior_names)==88 and unit_names==sorted(prior_names+P['expected_new_unit_tests']),'exact_E020_inventory_plus_three_policy_tests')
unitraw=(ROOT/'runs/V034-unit/stdout.log').read_text(encoding='utf8')
ck('E033_CACHE_CLEANUP_ERROR' not in unitraw,'no_unit_cleanup_error')
for name in P['expected_new_unit_tests']+['gpu::tests::shared_evaluation_matches_independent_sweeps']:
    block=re.search(r'^test '+re.escape(name)+r' \.\.\.(.*?)(?=^test |\Z)',unitraw,re.M|re.S)
    ck(block is not None and block.group(1).strip().endswith('ok'),'new_and_corrected_test_terminal_pass')
policy_records={}
for identity in ids[1:]:
    text=(ROOT/f'runs/{identity}/stdout.log').read_text(encoding='utf8'); events=[]; policies=[]
    for line in text.splitlines():
        if 'AUTORESEARCH_STAGE ' in line:events.append(('stage',json.loads(line.split('AUTORESEARCH_STAGE ',1)[1])))
        if 'E033_CACHE_POLICY ' in line:
            v=json.loads(line.split('E033_CACHE_POLICY ',1)[1]); policies.append(v);events.append(('policy',v))
    ck('E033_CACHE_CLEANUP_ERROR' not in text,'no_candidate_cleanup_error')
    candidate=identity.startswith('E034')
    ck(len(policies)==(6 if candidate else 0),'fixed_policy_marker_count')
    expected=[]; labeled=[]
    if candidate:
        for row in rawresults[identity]:
            fixture=row['fixture_id'];owned=row['nodes']*4;window=owned//128*128
            enabled={'cleanup_complete':False,'enabled':True,'errors':False,'normalized_lines':0,'owned_bytes':owned,'stage':'enabled','window_bytes':window}
            clean={'cleanup_complete':True,'enabled':True,'errors':False,'normalized_lines':window//128,'owned_bytes':owned,'stage':'clean','window_bytes':window}
            expected.extend([enabled,clean]);labeled.extend([{'fixture_id':fixture,**enabled},{'fixture_id':fixture,**clean}])
            start=next(i for i,(kind,v) in enumerate(events) if kind=='stage' and v.get('fixture_id')==fixture and v['stage']=='fixture_start')
            stop=next(i for i,(kind,v) in enumerate(events) if kind=='stage' and v.get('fixture_id')==fixture and v['stage']=='timing_complete')
            seg=events[start:stop+1]
            build=next(i for i,(kind,v) in enumerate(seg) if kind=='stage' and v['stage']=='build_complete')
            ready=next(i for i,(kind,v) in enumerate(seg) if kind=='stage' and v['stage']=='gpu_ready')
            en=next(i for i,(kind,v) in enumerate(seg) if kind=='policy' and v==enabled)
            cl=next(i for i,(kind,v) in enumerate(seg) if kind=='policy' and v==clean)
            last=max(i for i,(kind,v) in enumerate(seg) if kind=='stage' and v['stage']=='convergence_check')
            ck(build<en<ready and last<cl<len(seg)-1,'setup_and_cleanup_inside_original_timing_boundary')
        ck(policies==expected,'all_policy_fields_extents_and_order_exact')
    record=load(EX/f'{identity}.policy-markers.json')
    ck(record['markers']==labeled and record['candidate']==candidate,'runner_marker_record_recomputed')
    policy_records[identity]=labeled
EXCLUDE={'build_ms','init_ms','solve_ms','readback_ms','full_cycle_ms','fingerprint_ms_excluded'}
sexclude=EXCLUDE|{'solve_checks_elapsed_ms'}
ref=rawresults['B107'];refst=rawstages['B107'];trajectory=[]
for identity in ids[1:]:
    for a,b in zip(ref,rawresults[identity]):ck(norm(a,EXCLUDE)==norm(b,EXCLUDE),'complete_non_timing_result_exact')
    ck([norm(x,sexclude) for x in refst]==[norm(x,sexclude) for x in rawstages[identity]],'complete_non_timing_stage_trajectory_exact')
    for z in rawresults[identity]:
        ts=[x for x in rawstages[identity] if x['stage']=='convergence_check' and x['fixture_id']==z['fixture_id']]
        ck([x['iteration'] for x in ts]==list(range(20,z['iteration']+1,20)),'convergence_check_cadence')
        ck(ts[-1]['exploit_bits']==z['exploit_bits'] and ts[-1]['iteration']==z['iteration'],'same_stopping_check')
        trajectory.append({'run':identity,'fixture':z['fixture_id'],'count':len(ts),'iteration':z['iteration'],'fingerprint':z['fingerprint'],'exploit_bits':z['exploit_bits']})
bs=[runs[p['baseline']] for p in P['pairs']];cs=[runs[p['candidate']] for p in P['pairs']]
components=['build_ms','init_ms','solve_ms','readback_ms','full_cycle_ms'];fixture_tables=[];Bsum=Csum=0
for index,fixture in enumerate(['rainbow','two-tone','river']):
    table={'fixture_id':fixture,'components':{}}
    for k in components:
        b=[r['results'][index][k] for r in bs];c=[r['results'][index][k] for r in cs];bm=statistics.median(b);cm=statistics.median(c)
        table['components'][k]={'baseline_raw_ms':b,'candidate_raw_ms':c,'baseline_median_ms':bm,'candidate_median_ms':cm,'candidate_minus_baseline_median_ms':cm-bm,'gain_pct':gain(bm,cm),'paired_candidate_minus_baseline_ms':[y-x for x,y in zip(b,c)],'median_paired_candidate_minus_baseline_ms':statistics.median([y-x for x,y in zip(b,c)])}
        observed=C['fixtures'][index]
        ck(observed['fixture_id']==fixture,'comparison_fixture_order')
        ck(observed['baseline'][k]['raw_ms']==b and observed['candidate'][k]['raw_ms']==c,'comparison_raw_components')
        close(observed['baseline'][k]['median_ms'],bm,'comparison_baseline_component_median');close(observed['candidate'][k]['median_ms'],cm,'comparison_candidate_component_median')
    full=table['components']['full_cycle_ms'];Bsum+=full['baseline_median_ms'];Csum+=full['candidate_median_ms']
    regressions=[100*(c['results'][index]['full_cycle_ms']-b['results'][index]['full_cycle_ms'])/b['results'][index]['full_cycle_ms'] for b,c in zip(bs,cs)]
    guard=(-full['gain_pct']>3 and sum(x>3 for x in regressions)>=2)
    table['guard']={'median_regression_pct':-full['gain_pct'],'paired_regression_pct':regressions,'repeats_above3':sum(x>3 for x in regressions),'failed':guard}
    cg=C['performance']['fixture_regression_guard']['fixtures'][index]
    close(cg['median_regression_pct'],-full['gain_pct'],'guard_median');ck(cg['repetitions_above_3pct']==sum(x>3 for x in regressions) and cg['repeatable_material_regression']==guard,'guard_repeat_rule')
    fixture_tables.append(table)
score=gain(Bsum,Csum);close(C['performance']['baseline_full_cycle_ms'],Bsum,'primary_baseline_score');close(C['performance']['candidate_full_cycle_ms'],Csum,'primary_candidate_score');close(C['performance']['observed_gain_pct'],score,'primary_gain')
aggregate_pass=score>=2; guardfail=any(t['guard']['failed'] for t in fixture_tables); failed=not aggregate_pass or guardfail
ck(C['performance']['aggregate_gate_met']==aggregate_pass and C['performance']['fixture_regression_guard']['failed']==guardfail,'independent_registered_gates')
expected_decision='rejected' if failed else 'qualifying'
ck(C['decision']==expected_decision and not C['accepted'] and not C['deployed'] and C['excluded_runs']==[],'correct_provisional_decision_no_exclusions')
ck(C['correctness']['broader_validation']=='not run' and C['correctness']['f32_storage']=='not run','honest_unrun_broader_scope')
pairs=[]
for i,(b,c) in enumerate(zip(bs,cs)):
    pb=sum(x['full_cycle_ms'] for x in b['results']);pc=sum(x['full_cycle_ms'] for x in c['results'])
    close(C['pairs'][i]['baseline_full_cycle_ms'],pb,'pair_baseline_sum');close(C['pairs'][i]['candidate_full_cycle_ms'],pc,'pair_candidate_sum');close(C['pairs'][i]['observed_gain_pct'],gain(pb,pc),'pair_gain')
    pairs.append({'baseline':b['id'],'candidate':c['id'],'baseline_sum_ms':pb,'candidate_sum_ms':pc,'gain_pct':gain(pb,pc),'component_sum_candidate_minus_baseline_ms':{k:sum(x[k] for x in c['results'])-sum(x[k] for x in b['results']) for k in components},'process_wall_ms':{'baseline':b['process_wall_ms'],'candidate':c['process_wall_ms']},'whole_test_seconds':{'baseline':summary_runtime[b['id']],'candidate':summary_runtime[c['id']]}})
chron=[{'id':i,'started_at':runs[i]['started_at'],'finished_at':runs[i]['finished_at']} for i in ids[1:]];ck(C['chronology']==chron,'published_chronology')

ck(len(unit_names)==91,'full_91_unit_inventory')
ck(sum(t['count'] for t in trajectory)==138 and len(trajectory)==18,'all138_checkpoints_and18_records')
for report in C['input_reports']:pin(report['path'],report['sha256'])
for label in ['baseline','candidate']:
    expected=[p[label] for p in P['pairs']]
    ck(C['cohorts'][label]['run_ids']==expected and C['cohorts'][label]['count']==3,'all_three_samples_retained')
AI=load(ROOT/'runs/E034-assessment/invocation.json');AE=load(ROOT/'runs/E034-assessment/exit.json')
ck(AE['returncode']==0 and AI['protocol_sha256']==sha(PLAN/'protocol.json'),'assessment_terminal_and_protocol')
ck(dt(DONE['at'])<=dt(AI['at']) and dt(AI['at'])<=dt(C['created_at']),'assessment_after_all_runs')
ck(('--reject' in AI['command'])==failed and not C['performance']['statistical_significance_established'],'decision_no_significance_claim')
sha(ROOT/'runs/V020-unit/stdout.log');sha(OUT/'audit-numerical.py')
result={'id':'E034-independent-numerical-review','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'verdict':'CONFIRMED_REJECTED' if failed else 'PASS_PRIMARY_PROVISIONAL_ONLY','numerical_audit_pass':True,
 'primary':{'baseline_sum_fixture_medians_ms':Bsum,'candidate_sum_fixture_medians_ms':Csum,'gain_pct':score,'minimum_pct':2,'aggregate_gate_met':aggregate_pass,'fixture_guard_failed':guardfail},
 'all18_complete_non_timing_results_exact':True,'all138_convergence_checkpoints_exact':True,'all_complete_normalized_stage_trajectories_exact':True,'trajectories':trajectory,
 'unit_inventory':{'passed':87,'failed':0,'ignored':4,'measured':0,'filtered':0,'matches_E020_inventory_plus_three_policy_tests':True,'corrected_evaluation_test_passed':True},'policy_records':policy_records,
 'chronology_including_unit':[{'id':i,'started_at':runs[i]['started_at'],'finished_at':runs[i]['finished_at']} for i in ids], 'components':fixture_tables,'pairs':pairs,
 'checks':dict(checks),'assertions':sum(checks.values()),'input_sha256':artifacts,
 'scope':'File-only numerical/order/gate audit. Build/source/cache-prerequisite custody and restoration are independently audited in source-custody.json; this report does not substitute for that audit.',
 'broader_qualification':'Not run; inapplicable after primary rejection. No extension or rescue.' if failed else 'Not run; mandatory before acceptance, including scoped policy/lifecycle, original controls, F32, holdout and cumulative.',
 'limits':['Compressed full-state and convergence equality does not establish every possible F32 or cache-policy lifecycle state.','Warm-driver-cache complete-cycle scope; includes runtime NVRTC/JIT and readback, excludes Cargo/final fingerprinting/browser/API/disk saving.','Component medians are descriptive and do not establish causality or sum to whole-cycle median differences.','No statistical significance, speedup, acceptance or deployment claim.'],
 'reviewer_preparation_note':'Adapted file-only from the sealed E029 numerical parser before outcomes; E034 fixed IDs,87/4 inventory, three policy tests and corrected existing evaluation test; independent marker placement/extent checks added. No candidate script, native solver or GPU work by reviewer.',
 'native_or_gpu_executed_by_reviewer':False,'candidate_accepted':False,'deployment_changed':False}
(OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
summary=f"""# E034 independent numerical audit

**{result['verdict']}.** Fixed sum of fixture medians: {Bsum:.4f} -> {Csum:.4f}ms; observed gain {score:.10f}%. Aggregate gate: {aggregate_pass}; repeated-fixture guard failure: {guardfail}. All six measurements retained.

All18 complete non-timing result objects, all138 convergence checkpoints and complete normalized stage trajectories match exactly. Stops200/200/60. Units87passed,0failed,4ignored,0measured,0filtered; exact accepted E020 inventory plus three policy tests and corrected evaluation test passed. Candidate policy markers have exact extents and timed placement. All seven runs occurred in frozen order after separate feature compile-only and GPU-only builds.

File-only numerical/order/gate audit passed {sum(checks.values())} assertions. Source/build custody and restoration are independently recorded. Broader qualification: {result['broader_qualification']}

No extra measurements, exclusions, extension, native reviewer execution, causal or statistical-significance claims. No acceptance or deployment from this result.
"""
(OUT/'summary.md').write_text(summary,encoding='utf8')
print(json.dumps({'verdict':result['verdict'],'primary':result['primary'],'assertions':sum(checks.values()),'validation_sha256':sha(OUT/'validation.json')},indent=2))
