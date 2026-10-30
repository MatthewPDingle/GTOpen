import pathlib,json,hashlib,datetime,statistics,math,re,csv,collections
ROOT=pathlib.Path(r'S:\GTOpen-research\postflop-gpu-20261016')
OUT=ROOT/'comparisons/E037-independent-review';PLAN=ROOT/'runs/E037-primary-plan';EX=ROOT/'runs/E037-primary-execution'
assert not (OUT/'validation.json').exists() and not (OUT/'summary.md').exists(), 'Preserve any prior audit result'
terminal=json.loads((OUT/'terminal-inputs-policy-1pct.json').read_text(encoding='utf-8'))
assert terminal['id']=='E037' and terminal['root_all_stages_terminal'] is True
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
pin(PLAN/'protocol.json','48e8c20d6e9744e6397274596979ac69ff94d6d57a6d7d13a726ae9a16910c86')
pin(PLAN/'scripts-manifest.json','6f00150b84498fc9c9572b07b546f6e01c110d618b22ab9973749b42d53f8540')
pin(ROOT/'comparisons/E037-three-pair-comparison/report.json',terminal['comparison_sha256'])
P=load(PLAN/'protocol.json');C=load(ROOT/'comparisons/E037-three-pair-comparison/report.json')
POLICY=ROOT/'runs/E037-policy-1pct'
pin(POLICY/'policy.json','f2eaef2759f628db85a414e5496f7dec89be1e398f7d00d8d068d1db74be55d4')
pin(POLICY/'scripts-manifest.json','bf84a6f7f685d42ee3fbcf7aed5737a073b8acbf9401544ddaa03c9cc1b4d37a')
pin(POLICY/'authorization.json','df9e39cc5ad89c9eb9c9133b2205acd706926343c67c6d3ee1d326a38c4b9da3')
pin(ROOT/'comparisons/E037-policy-review/report.json','80c14dd34db4fe95c617268fda3a962ac44a0d8e3203d4c876c438a44178c099')
pin(PLAN/'authorization.json','03b36389ca3864e8bfc550c0dcceb724a1b486cf46a9950dc3293a6beaf219dc')
POL=load(POLICY/'policy.json');PA=load(POLICY/'authorization.json');PM=load(POLICY/'scripts-manifest.json')
for name in ['assess.py','compare_policy.py','primary.py','policy_guard.py']:pin(POLICY/name,PM['script_sha256'][name])
ck(POL['required_gain_pct']==1.0 and POL['fixture_slowdown_threshold_pct']==0.0 and POL['original_assessor_prohibited'] and POL['primary_pass_is_preliminary'],'effective_user_policy')
ck(POL['order']==P['order'] and POL['pairs']==P['pairs'],'effective_policy_preserves_workload')
ck(PA['effective_policy_sha256']==sha(POLICY/'policy.json') and PA['policy_manifest_sha256']==sha(POLICY/'scripts-manifest.json') and PA['independent_policy_review_pass'],'policy_authorization_binding')
pin(POL['root_decision']['path'],POL['root_decision']['sha256']);UD=load(POL['root_decision']['path'])
RECEIPT=load(ROOT/'runs/E037-policy-execution/pre-primary.json');PE=load(ROOT/'runs/E037-policy-execution/exit.json')
ck(dt(UD['at'])<=dt(POL['at'])<=dt(PA['at'])<=dt(RECEIPT['at']) and UD['pre_timing_evidence']['native_or_timing_run_started'] is False,'policy_fixed_before_native')
ck(RECEIPT['all_seven_run_directories_absent'] is True and RECEIPT['order']==P['order'] and PE['returncode']==0,'effective_wrapper_complete')
ck(RECEIPT['policy_sha256']==sha(POLICY/'policy.json') and RECEIPT['policy_manifest_sha256']==sha(POLICY/'scripts-manifest.json') and RECEIPT['policy_authorization_sha256']==sha(POLICY/'authorization.json') and RECEIPT['original_authorization_sha256']==sha(PLAN/'authorization.json'),'pre_primary_dual_authority_receipt')
ck(RECEIPT['original_primary_sha256']==sha(PLAN/'primary.py') and RECEIPT['wrapper_sha256']==sha(POLICY/'primary.py'),'unchanged_runner_with_effective_wrapper')
EP=C['effective_policy']
ck(EP['sha256']==sha(POLICY/'policy.json') and EP['policy_manifest_sha256']==sha(POLICY/'scripts-manifest.json') and EP['policy_authorization_sha256']==sha(POLICY/'authorization.json'),'comparison_effective_policy_pins')
ck(EP['original_protocol_sha256']==sha(PLAN/'protocol.json') and EP['original_authorization_sha256']==sha(PLAN/'authorization.json') and EP['root_user_decision']==POL['root_decision'],'comparison_original_authority_pins')
ck(EP['pre_primary_receipt']=={'path':str(ROOT/'runs/E037-policy-execution/pre-primary.json'),'sha256':sha(ROOT/'runs/E037-policy-execution/pre-primary.json')} and EP['changed_before_any_native_timing'] and EP['primary_pass_is_preliminary'] and not EP['candidate_accepted'],'comparison_receipt_and_preliminary_scope')
ck(EP['adoption_requirements']==POL['adoption_requirements'] and EP['no_material_cost_validation']['status']=='pending_resource_and_broader_qualification','confirmation_and_tradeoffs_still_pending')
ck(P['order']==['V037-unit','B116','E037R1','E037R2','B117','B118','E037R3'],'fixed_seven_run_order')
ck(P['pairs']==[{'baseline':'B116','candidate':'E037R1'},{'baseline':'B117','candidate':'E037R2'},{'baseline':'B118','candidate':'E037R3'}],'fixed_pairing')
ck(P['expected_unit_passed']==85 and P['expected_unit_ignored']==4,'frozen_unit_counts')
BM={n:load(ROOT/'binaries'/(n+'.manifest.json')) for n in ['E020-postflop_autoresearch','E037-postflop_autoresearch','E037-solver']}
BE=load(ROOT/'runs/E037-build/exit.json');CK=load(ROOT/'runs/E037-compile-check/complete.json')
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
    which='E037-solver' if identity=='V037-unit' else ('E020-postflop_autoresearch' if identity.startswith('B') else 'E037-postflop_autoresearch')
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
    expected=('85','0','4','0','0') if identity=='V037-unit' else ('1','0','0','0','0')
    ck(len(summary)==1 and tuple(summary[0][:5])==expected,'full_native_test_summary')
    ck(r['test_pass_count']==int(expected[0]),'reported_pass_count')
    summary_runtime[identity]=float(summary[0][-1])
    if identity=='V037-unit':unit_names=sorted(re.findall(r'^test (\S+) \.\.\.',text,re.M));continue
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
for identity in ids:ck(dt(RECEIPT['at'])<=dt(runs[identity]['started_at'])<=dt(runs[identity]['finished_at'])<=dt(PE['at']),'all_runs_after_policy_receipt_before_wrapper_exit')
ck(dt(BE['at'])<dt(runs[ids[0]]['started_at']),'build_terminal_before_unit_and_primary')
priorunit=(ROOT/'runs/V020-unit/stdout.log').read_text(encoding='utf-8')
prior_names=re.findall(r'^test (\S+) \.\.\.',priorunit,re.M)
ck(len(prior_names)==88 and unit_names==sorted(prior_names+P['expected_new_unit_tests']),'exact_E020_inventory_plus_one_show_test')
unitraw=(ROOT/'runs/V037-unit/stdout.log').read_text(encoding='utf8')
for name in P['expected_new_unit_tests']:
    block=re.search(r'^test '+re.escape(name)+r' \.\.\.(.*?)(?=^test |\Z)',unitraw,re.M|re.S)
    ck(block is not None and block.group(1).strip().endswith('ok'),'focused_original_kernel_test_terminal_pass')
focused_records=[json.loads(line.split('E037_SHOW_ZERO_TEST ',1)[1]) for line in unitraw.splitlines() if 'E037_SHOW_ZERO_TEST ' in line]
ck(focused_records==[{'comparison_pairs':34,'kernel_launches':68,'threads':128,'exact':True,'performance_measurement':False}],'exact_focused_original_GPU_marker')
ck(P['focused_unit_marker']=={'prefix':'E037_SHOW_ZERO_TEST ','expected':focused_records[0]},'focused_marker_matches_frozen_protocol')
EXCLUDE={'build_ms','init_ms','solve_ms','readback_ms','full_cycle_ms','fingerprint_ms_excluded'}
sexclude=EXCLUDE|{'solve_checks_elapsed_ms'}
ref=rawresults['B116'];refst=rawstages['B116'];trajectory=[]
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
    guard=(-full['gain_pct']>0 and sum(x>0 for x in regressions)>=2)
    table['guard']={'median_regression_pct':-full['gain_pct'],'paired_regression_pct':regressions,'repeats_above0':sum(x>0 for x in regressions),'failed':guard}
    cg=C['performance']['fixture_regression_guard']['fixtures'][index]
    close(cg['median_regression_pct'],-full['gain_pct'],'guard_median');ck(cg['repetitions_above_0pct']==sum(x>0 for x in regressions) and cg['repeatable_measured_regression']==guard,'guard_repeat_rule')
    fixture_tables.append(table)
score=gain(Bsum,Csum);close(C['performance']['baseline_full_cycle_ms'],Bsum,'primary_baseline_score');close(C['performance']['candidate_full_cycle_ms'],Csum,'primary_candidate_score');close(C['performance']['observed_gain_pct'],score,'primary_gain')
aggregate_pass=score>=1; guardfail=any(t['guard']['failed'] for t in fixture_tables); failed=not aggregate_pass or guardfail
ck(C['performance']['required_gain_pct']==1.0 and C['performance']['fixture_regression_guard']['threshold_pct']==0.0,'published_effective_thresholds')
ck(C['performance']['fixture_median_regression_above_0pct']==[t['fixture_id'] for t in fixture_tables if t['guard']['median_regression_pct']>0],'published_positive_fixture_slowdowns')
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

ck(len(unit_names)==89,'full_89_unit_inventory')
ck(sum(t['count'] for t in trajectory)==138 and len(trajectory)==18,'all138_checkpoints_and18_records')
for report in C['input_reports']:pin(report['path'],report['sha256'])
for label in ['baseline','candidate']:
    expected=[p[label] for p in P['pairs']]
    ck(C['cohorts'][label]['run_ids']==expected and C['cohorts'][label]['count']==3,'all_three_samples_retained')
AI=load(ROOT/'runs/E037-assessment/invocation.json');AE=load(ROOT/'runs/E037-assessment/exit.json')
ck(AE['returncode']==0 and AI['protocol_sha256']==sha(PLAN/'protocol.json'),'assessment_terminal_and_protocol')
ck(AI['script_sha256']==sha(POLICY/'assess.py') and AI['effective_policy']==EP and str(POLICY/'compare_policy.py') in AI['command'] and '--policy-authorization-sha256' in AI['command'] and sha(POLICY/'authorization.json') in AI['command'],'only_effective_policy_assessment')
ck(dt(PE['at'])<=dt(AI['at']),'effective_wrapper_terminal_before_assessment')
ck(dt(DONE['at'])<=dt(AI['at']) and dt(AI['at'])<=dt(C['created_at']),'assessment_after_all_runs')
ck(('--reject' in AI['command'])==failed and not C['performance']['statistical_significance_established'],'decision_no_significance_claim')
sha(ROOT/'runs/V020-unit/stdout.log');sha(OUT/'audit-numerical-policy-1pct.py');sha(OUT/'terminal-inputs-policy-1pct.json')
result={'id':'E037-independent-numerical-review','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'verdict':'CONFIRMED_REJECTED' if failed else 'PASS_PRIMARY_PROVISIONAL_ONLY','numerical_audit_pass':True,
 'effective_policy':EP,'primary':{'baseline_sum_fixture_medians_ms':Bsum,'candidate_sum_fixture_medians_ms':Csum,'gain_pct':score,'minimum_pct':1,'aggregate_gate_met':aggregate_pass,'fixture_guard_failed':guardfail},
 'all18_complete_non_timing_results_exact':True,'all138_convergence_checkpoints_exact':True,'all_complete_normalized_stage_trajectories_exact':True,'trajectories':trajectory,
 'unit_inventory':{'passed':85,'failed':0,'ignored':4,'measured':0,'filtered':0,'matches_E020_inventory_plus_one_show_test':True,'focused_original_kernel_test_passed':True},'focused_unit_records':focused_records,
 'chronology_including_unit':[{'id':i,'started_at':runs[i]['started_at'],'finished_at':runs[i]['finished_at']} for i in ids], 'components':fixture_tables,'pairs':pairs,
 'checks':dict(checks),'assertions':sum(checks.values()),'input_sha256':artifacts,
 'scope':'File-only numerical/order/gate audit. Build/source/prerequisite custody and restoration are independently audited in source-custody.json; this report does not substitute for that audit.',
 'broader_qualification':'Not run; inapplicable after primary rejection. No extension or rescue.' if failed else 'Not run; fresh fixed16-pair confirmation under the user1%/no-repeatable-slowdown policy is mandatory, then raw old/new show/state validation, original controls, F32, holdout, cumulative and material memory/resource/compatibility evidence before acceptance.',
 'limits':['Compressed full-state and convergence equality does not establish every possible F32, nonfinite or zero-row lifecycle state.','Warm-driver-cache complete-cycle scope; includes runtime NVRTC/JIT and readback, excludes Cargo/final fingerprinting/browser/API/disk saving.','Component medians are descriptive and do not establish causality or sum to whole-cycle median differences.','No statistical significance, speedup, acceptance or deployment claim.'],
 'reviewer_preparation_note':'Adapted file-only from the preserved E037 prepared audit after the independently reviewed user1% policy was frozen before native timing. Original numerical18/138 block and85/4 plus34/68 marker checks remain exact; only effective policy/receipt checks and timing-gate semantics change. No candidate script, native solver or GPU work by reviewer.',
 'native_or_gpu_executed_by_reviewer':False,'candidate_accepted':False,'deployment_changed':False}
(OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
summary=f"""# E037 independent numerical audit

**{result['verdict']}.** Fixed sum of fixture medians: {Bsum:.4f} -> {Csum:.4f}ms; observed gain {score:.10f}%. User aggregate gate >=1%: {aggregate_pass}; repeated-fixture slowdown >0% guard failure: {guardfail}. All six measurements retained.

All18 complete non-timing result objects, all138 convergence checkpoints and complete normalized stage trajectories match exactly. Stops200/200/60. Units85passed,0failed,4ignored,0measured,0filtered; exact accepted E020 inventory plus one original-kernel showdown test passed with the34-pair/68-launch marker. All seven runs occurred in frozen order after separate feature compile-only and GPU-only builds.

File-only numerical/order/gate audit passed {sum(checks.values())} assertions. Source/build custody and restoration are independently recorded. Broader qualification: {result['broader_qualification']}

No extra measurements, exclusions, extension, native reviewer execution, causal or statistical-significance claims. No acceptance or deployment from this result.
"""
(OUT/'summary.md').write_text(summary,encoding='utf8')
print(json.dumps({'verdict':result['verdict'],'primary':result['primary'],'assertions':sum(checks.values()),'validation_sha256':sha(OUT/'validation.json')},indent=2))
