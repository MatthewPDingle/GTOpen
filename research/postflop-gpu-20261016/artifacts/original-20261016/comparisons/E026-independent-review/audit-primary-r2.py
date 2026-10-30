import pathlib,json,hashlib,datetime,statistics,math,re,csv,collections,sys
assert len(sys.argv)==5, "After root terminal notification provide authorization, comparison, primary binary and unit binary SHA256 pins"
AUTH_PIN,COMPARISON_PIN,PRIMARY_PIN,UNIT_PIN=sys.argv[1:]
ROOT=pathlib.Path(r'S:\GTOpen-research\postflop-gpu-20261016'); REPO=pathlib.Path(r'X:\Dev\GTOpen-gpu-research-20261016')
OUT=ROOT/'comparisons/E026-independent-review'; PLAN=ROOT/'runs/E026-primary-plan'; EX=ROOT/'runs/E026-primary-execution'
checks=collections.Counter(); artifacts={}
def ck(b,label):
    if not b: raise AssertionError(label)
    checks[label]+=1
def sha(p):
    p=pathlib.Path(p);s=str(p)
    if s not in artifacts:artifacts[s]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
    return artifacts[s]['sha256']
def load(p):sha(p);return json.loads(pathlib.Path(p).read_text(encoding='utf-8-sig'))
def pin(p,h):ck(sha(p)==h,'artifact_hash')
def dt(x):return datetime.datetime.fromisoformat(x.replace('Z','+00:00'))
def norm(d,exclude):return {k:v for k,v in d.items() if k not in exclude}
def gain(b,c):return 100*(b-c)/b
def close(a,b,label):ck(math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-9),label)
P=load(PLAN/'protocol.json');C=load(ROOT/'comparisons/E026-three-pair-comparison/report.json');A=load(PLAN/'authorization.json');F=load(ROOT/'baseline-manifest.json')
pin(PLAN/'protocol.json','9ba20afba65a286279f531bb6dd46e2104edf01a35e70a9475dc3c78f5567388')
pin(ROOT/'comparisons/E026-three-pair-comparison/report.json',COMPARISON_PIN)
for n,h in load(PLAN/'scripts-manifest.json')['script_sha256'].items():pin(PLAN/n,h)
for p,h in A['evidence_sha256'].items():pin(p,h)
pin(PLAN/'authorization.json',AUTH_PIN)
ck(A['E020_accepted'] and A['E020_server_qualification_pass'] and A['independent_source_review_pass'] and A['independent_script_review_pass'],'accepted_server_and_review_prerequisites')
seal=load(PLAN/'scripts-manifest.json');pin(PLAN/'scripts-manifest.json','f7f0e7f395d5b2b6d8b6589d647f8583e33b9ccbe10bf00479f029742b9d7a2d')
for n,h in seal['supporting_sha256'].items():pin(PLAN/n,h)
for p,h in seal['reference_sha256'].items():pin(p,h)
for role,pininfo in A['prerequisites'].items():pin(pininfo['path'],pininfo['sha256']);ck(A['evidence_sha256'][pininfo['path']]==pininfo['sha256'],'prerequisite_authorization_pin')
accepted_record=load(A['prerequisites']['E020_acceptance']['path']);server_record=load(A['prerequisites']['E020_server_qualification']['path']);source_review=load(A['prerequisites']['E026_source_review']['path']);script_review=load(A['prerequisites']['E026_script_review']['path'])
ck(accepted_record['id']=='E020' and accepted_record['status']=='validated' and server_record['candidate_id']=='E020' and server_record['status']=='pass','actual_prerequisite_semantics')
ck(source_review['status'].startswith('PASS') and script_review['status'].startswith('PASS') and source_review.get('actionable_findings',source_review.get('findings',[]))==[] and script_review.get('actionable_findings',script_review.get('findings',[]))==[],'actual_source_and_script_review_pass')
BM={}
for name in ['E020-postflop_autoresearch','E026-postflop_autoresearch','E026-solver']:
    m=load(ROOT/f'binaries/{name}.manifest.json');BM[name]=m;pin(ROOT/f'binaries/{name}.exe',m['binary_sha256'])
    ck(hashlib.sha256(json.dumps(m['source_sha256'],sort_keys=True).encode()).hexdigest()==m['source_manifest_sha256'],'build_source_manifest_digest')
    pin(m['build_log'],m['build_log_sha256']);pin(m['patch'],m['patch_sha256'])
    if 'build_stderr_sha256' in m:pin(m['build_stderr_log'],m['build_stderr_sha256'])
    if name.startswith('E026'):
        ck(m['source_matches_prebuild'] and m['source_sha256']==load(ROOT/'runs/E026-build/source-before.json')['source_sha256'],'build_before_after_source')
        ck(m['build_script_sha256']==sha(PLAN/'build.py') and m['primary_protocol_sha256']==sha(PLAN/'protocol.json') and m['probe_authorization_sha256']==sha(PLAN/'authorization.json'),'build_sealed_inputs')
        ck(m['probe_evidence_sha256']==A['evidence_sha256'],'build_probe_evidence')
ck(BM['E020-postflop_autoresearch']['binary_sha256']==P['reference_binary_sha256'],'pinned_E020_binary');pin(ROOT/'binaries/E020-postflop_autoresearch.manifest.json',P['reference_manifest_sha256'])
Bsrc=BM['E020-postflop_autoresearch']['source_sha256'];Csrc=BM['E026-postflop_autoresearch']['source_sha256'];owned=P['owned_sources']
ck(len(Bsrc)==len(Csrc)==162 and set(Bsrc)==set(Csrc),'same_complete162_source_keyset')
ck(sorted(k for k in Bsrc if Bsrc[k]!=Csrc[k])==sorted(owned),'exactly_two_owned_sources_changed')
ck(sorted(A['candidate_sources'])==sorted(owned),'authorized_two_source_set')
activation=load(ROOT/'runs/E026-source/activation.json');ck(activation['source_before']['source_sha256']==Bsrc,'activation_began_at_exact_E020')
ck(activation['source_after']['source_sha256']==Csrc,'activation_matches_exact_candidate')
for k in owned:
    ck(Bsrc[k]==P['accepted_owned_sha256'][k] and Csrc[k]==A['candidate_sources'][k]['sha256'],'authorized_owned_source_identity')
    pin(A['candidate_sources'][k]['path'],Csrc[k])
    for n in ['E026-postflop_autoresearch','E026-solver']:
        ck(BM[n]['candidate_sources']==A['candidate_sources'],'build_candidate_authorization_map')
        item=BM[n]['source_copies'][k];ck(item['sha256']==Csrc[k],'build_copy_hash');pin(item['path'],item['sha256'])
    fname=pathlib.Path(k).name
    pin(ROOT/f'runs/E026-design/candidate/{fname}',Csrc[k]);pin(ROOT/f'runs/E026-design/base/{fname}',Bsrc[k])
for name in ['bench_spot.json','crates/solver/tests/postflop_autoresearch.rs']:
    ck(Bsrc[name]==Csrc[name]==F.get('source_sha256',F.get('hashes'))[name].lower(),'frozen_evaluator_and_workload')
BE=load(ROOT/'runs/E026-build/exit.json');ck(BE['returncode']==0 and BE['error'] is None and BE['cleanup'] is None,'build_terminal_success')
buildrows=[json.loads(s) for s in pathlib.Path(BM['E026-postflop_autoresearch']['build_log']).read_text().splitlines()]
ck(any(x.get('reason')=='build-finished' and x['success'] for x in buildrows),'cargo_raw_terminal_success')
targets=[x for x in buildrows if x.get('reason')=='compiler-artifact' and x.get('profile',{}).get('test') and x.get('executable') and x['target']['name'] in ['solver','postflop_autoresearch']]
ck(len(targets)==2 and {x['target']['name'] for x in targets}=={'solver','postflop_autoresearch'},'two_expected_build_targets')
target=ROOT/'build-primary-e026';env=load(ROOT/'runs/E026-build/build-environment.json')
ck(env['target_previously_absent'] and pathlib.Path(env['target_dir'])==target and env['compiler_override_absence']=={} and env['RAYON_NUM_THREADS']=='16','fresh_fixed_build_environment')
solver_lib=[x for x in buildrows if x.get('reason')=='compiler-artifact' and x['target']['name']=='solver' and x['target']['kind']==['lib'] and not x.get('profile',{}).get('test')]
ck(len(solver_lib)==1,'one_solver_library_artifact')
for item in solver_lib+targets:
    ck(item['fresh'] is False and pathlib.Path(item['manifest_path']).resolve()==(REPO/'crates/solver/Cargo.toml').resolve(),'newly_compiled_correct_package')
    expected_src='crates/solver/tests/postflop_autoresearch.rs' if item['target']['name']=='postflop_autoresearch' else 'crates/solver/src/lib.rs'
    ck(pathlib.Path(item['target']['src_path']).resolve()==(REPO/expected_src).resolve(),'correct_artifact_source_path')
for item in buildrows:
    if item.get('reason')=='compiler-artifact':
        for f in item.get('filenames',[])+([item['executable']] if item.get('executable') else []):ck(pathlib.Path(f).resolve().is_relative_to(target.resolve()),'fresh_target_containment')
accepted_cuda=(ROOT/'runs/E026-design/base/kernels.cu').read_bytes()
candidate_cuda=(ROOT/'runs/E026-design/candidate/kernels.cu').read_bytes()
ck(hashlib.sha256(accepted_cuda).hexdigest()==P['accepted_kernel_sha256'],'accepted_CUDA_archive_identity')
ck(hashlib.sha256(candidate_cuda).hexdigest()==P['candidate_owned_sha256']['crates/solver/src/gpu/kernels.cu'],'candidate_CUDA_archive_identity')
for n in ['E026-solver','E026-postflop_autoresearch']:
    data=(ROOT/f'binaries/{n}.exe').read_bytes();ck(candidate_cuda in data and accepted_cuda not in data,'linked_complete_candidate_CUDA_not_E020')
    ck(BM[n]['expected_cuda_present'] and BM[n]['accepted_cuda_absent'] and pathlib.Path(BM[n]['target_dir'])==target,'recorded_linked_identity')

INV=load(EX/'invocation.json');DONE=load(EX/'complete.json')
ck(INV['order']==DONE['order']==P['order'],'fixed_seven_run_order');ck(INV['source_sha256']==Csrc,'execution_candidate_source_identity')
ck(INV['script_sha256']==sha(PLAN/'primary.py') and INV['primary_protocol_sha256']==sha(PLAN/'protocol.json'),'execution_script_and_protocol_pins')
for n,v in INV['candidate_binary_pins'].items():pin(ROOT/f'binaries/{n}.exe',v['binary_sha256']);pin(ROOT/f'binaries/{n}.manifest.json',v['manifest_sha256'])
ids=P['order'];runs={};rawstages={};rawresults={};unit_names=[];summary_runtime={}
for identity in ids:
    r=load(ROOT/f'runs/{identity}/report.json');runs[identity]=r
    ck(r['id']==identity and r['status']=='measured' and r['returncode']==0,'successful_physical_run')
    pin(ROOT/f'runs/{identity}/stdout.log',r['stdout_sha256']);pin(r['command'][0],r['binary_sha256'])
    bm=r['binary_build_manifest'];pin(bm['path'],bm['sha256']);ck(bm['data']==load(bm['path']) and bm['binary_hash_verified'] and bm['data']['binary_sha256']==r['binary_sha256'],'runtime_binary_manifest_link')
    which='E026-solver' if identity=='V026-unit' else ('E020-postflop_autoresearch' if identity.startswith('B') else 'E026-postflop_autoresearch')
    ck(bm['data']==BM[which],'right_binary_for_run')
    ck(r['provenance']['source_sha256']==Csrc,'runtime_current_snapshot_candidate_not_baseline_identity')
    ck(r['provenance']['source_manifest_sha256']==hashlib.sha256(json.dumps(Csrc,sort_keys=True).encode()).hexdigest(),'runtime_snapshot_digest')
    subinv=load(EX/f'{identity}.invocation.json');subexit=load(EX/f'{identity}.exit.json')
    ck(subexit['returncode']==0 and dt(subinv['at'])<=dt(r['started_at'])<=dt(r['finished_at'])<=dt(subexit['at']),'wrapper_terminal_order')
    ck(r['environment']==C['environment'],'fixed_primary_environment')
    ck(r['environment']['RAYON_NUM_THREADS']=='16' and r['environment']['POSTFLOP_AUTORESEARCH_PROFILE']=='0' and r['environment']['POSTFLOP_AUTORESEARCH_STORAGE']=='compressed' and r['environment']['POSTFLOP_AUTORESEARCH_FIXTURE'] is None,'fixed_workload_environment')
    for live in ['live_status_before','live_status_at_launch']:
        state=r[live];ck(state['/api/status']['state']!='running' and not state['/api/reports/status']['running'],'live_server_not_solving')
    ck(r['disk_free_bytes']>=50*1024**3,'disk_reserve')
    telemetry=r['telemetry_before']['gpu'];ck(telemetry['returncode']==0,'gpu_identity_read')
    gpu=[row[:4] for row in csv.reader(telemetry['stdout'].splitlines(),skipinitialspace=True)];ck(gpu==C['gpu_identity'],'same_GPU_driver')
    text=(ROOT/f'runs/{identity}/stdout.log').read_text();st=[];rs=[]
    for line in text.splitlines():
        for marker,dest in [('AUTORESEARCH_STAGE ',st),('AUTORESEARCH_RESULT ',rs)]:
            if marker in line:dest.append(json.loads(line.split(marker,1)[1]))
    ck(rs==r['results'] and st==[x['data'] for x in r['stages']],'raw_json_exact_report')
    rawstages[identity]=st;rawresults[identity]=rs
    summary=re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out; finished in ([0-9.]+)s',text)
    expected=('84','0','4','0','0') if identity=='V026-unit' else ('1','0','0','0','0')
    ck(len(summary)==1 and tuple(summary[0][:5])==expected,'full_native_test_summary')
    ck(r['test_pass_count']==int(expected[0]),'reported_pass_count')
    summary_runtime[identity]=float(summary[0][-1])
    if identity=='V026-unit':unit_names=sorted(re.findall(r'^test (\S+) \.\.\.',text,re.M));continue
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
priorunit=(ROOT/'runs/V020-unit/stdout.log').read_text();ck(unit_names==sorted(re.findall(r'^test (\S+) \.\.\.',priorunit,re.M)),'same_88_test_inventory')
EXCLUDE={'build_ms','init_ms','solve_ms','readback_ms','full_cycle_ms','fingerprint_ms_excluded'}
sexclude=EXCLUDE|{'solve_checks_elapsed_ms'}
ref=rawresults['B086'];refst=rawstages['B086'];trajectory=[]
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
ASSESS=ROOT/'runs/E026-assessment';ai=load(ASSESS/'invocation.json');link=load(ASSESS/'logical-run-link.json')
pin(PLAN/'assess.py',ai['script_sha256']);ck(ai['protocol_sha256']==sha(PLAN/'protocol.json'),'assessment_protocol_pin')
ck(ai['command'][ai['command'].index('--candidate-id')+1]=='E026R1' and ('--reject' in ai['command'])==failed and '--excluded-runs' not in ai['command'],'physical_comparison_identity')
ck(link['actual_run_ids']==[p['candidate'] for p in P['pairs']] and link['logical_candidate']=='E026' and not link['synthesized_measurement'],'explicit_logical_alias')
pin(link['patch_alias'],link['patch_sha256']);pin(link['source_patch'],link['patch_sha256']);ck(pathlib.Path(link['patch_alias']).read_bytes()==pathlib.Path(link['source_patch']).read_bytes(),'byte_exact_patch_alias')
ck(not (ROOT/'runs/E026/report.json').exists(),'no_synthetic_E026_measurement');ck(load(ASSESS/'exit.json')['returncode']==0,'assessment_terminal_success')
assessment_stdout=load(ASSESS/'stdout.log');ck(assessment_stdout['performance']==C['performance'] and assessment_stdout['decision']==expected_decision,'assessment_stdout_matches_report')
for item in C['preserved_artifacts']+C['input_reports']+[C['frozen_manifest'],C['original_candidate_report']]:pin(item['path'],item['sha256'])
ck(C['original_candidate_report']['id']=='E026R1' and C['candidate_id']=='E026R1','comparison_records_true_physical_id')
for folder in [PLAN,EX,ASSESS,ROOT/'runs/E026-build',ROOT/'runs/E026-source']:
    for p in folder.iterdir():
        if p.is_file():sha(p)
for p in [REPO/'tools/postflop_compare.py',REPO/'tools/postflop_autoresearch.py',OUT/'source-custody.json',ROOT/'runs/V020-unit/stdout.log']:sha(p)
# E026's full wide-turn policy was frozen inside the primary protocol; execution is a later gated stage.
ck(P['wide_turn_holdout_if_pass']['reference']=='accepted E020' and P['wide_turn_holdout_if_pass']['candidate']=='E026','own_wide_holdout_required')
ck(P['wide_turn_holdout_if_pass']['fixed_order']==['B1','C1','C2','B2','B3','C3'] and P['wide_turn_holdout_if_pass']['separate_from_primary_score'],'fixed_separate_wide_policy')
pin(PLAN/'wide-turn-fixture.json',P['wide_turn_holdout_if_pass']['fixture_sha256'])
ck(dt(P['at'])<=dt(script_review['at'])<dt(INV['at']) and dt(source_review['at'])<dt(INV['at']) and dt(accepted_record['accepted_at'])<dt(INV['at']) and dt(server_record['at'])<dt(INV['at']),'review_and_E020_qualification_precede_execution')
ck(sum(t['count'] for t in trajectory)==138 and len(trajectory)==18,'exactly138_checks_and18_full_records')
ck(INV['build_terminal_before_launch'] and dt(BE['at'])<dt(INV['at']) and dt(DONE['at'])>=dt(runs[ids[-1]]['finished_at']),'whole_execution_terminal_chain')
ck(C['cohorts']['baseline']['run_ids']==[p['baseline'] for p in P['pairs']] and C['cohorts']['candidate']['run_ids']==[p['candidate'] for p in P['pairs']],'exact_declared_cohorts')
ck(P['exclusions']==[] and not P['outcome_triggered_extensions'],'no_exclusions_or_extensions_authorized')
holdout={'frozen_at':P['at'],'independently_reviewed_at':script_review['at'],'primary_invoked_at':INV['at'],'unit_started_at':runs[ids[0]]['started_at'],'protocol_sha256':sha(PLAN/'protocol.json'),'policy':P['wide_turn_holdout_if_pass'],'entry_condition':'Only primary qualification plus independent terminal review permits later separately frozen broader/holdout work. If this screen fails, no next qualification gate. No holdout result or acceptance claimed.'}

# Pin terminal outputs supplied only after root reports completion; no evaluation imported or executed.
pin(ROOT/'binaries/E026-postflop_autoresearch.exe',PRIMARY_PIN)
pin(ROOT/'binaries/E026-solver.exe',UNIT_PIN)
ck(set(owned)=={'crates/solver/src/gpu/kernels.cu','crates/solver/src/gpu/mod.rs'} and P['order']==['V026-unit','B086','E026R1','E026R2','B087','B088','E026R3'],'two_showdown_files_and_fixed_IDs')
ck(len(unit_names)==88,'complete_unit_inventory88')
d050=load(A['prerequisites']['D050_terminal_review']['path']);d051=load(A['prerequisites']['direct_up_show_terminal_review']['path'])
pin(A['prerequisites']['D050_terminal_review']['path'],'9aa099575d3ada3b00653fe5eddc88ed7a4b07d31fbedbd2b6b21a721c0eb8e5')
pin(A['prerequisites']['direct_up_show_terminal_review']['path'],'61bb07d463e980aba6adfa1a271e537b26b84282e3ea61794070d8f133d9dfe6')
ck(A['D050_terminal_ptx_pass'] and A['direct_up_show_exact_pass'],'D050_D051_authorization')
ck(d050['verdict']=='PASS_SCOPED_COMPILER_CAPACITY_AND_PTX' and d050['capacity_prerequisite_pass'] and d050['source_ptx_prerequisite_pass'],'sealed_D050_compiler_prerequisite')
contract={'id':'D051','verdict':'PASS_EXACT_COMPLETE_UP_SHOW_COMPARISON','exactness_pass':True,'numerical_validation':'executed','baseline_cuda_sha256':P['accepted_kernel_sha256'],'candidate_cuda_sha256':P['candidate_owned_sha256']['crates/solver/src/gpu/kernels.cu'],'baseline_physical_threads':128,'candidate_physical_threads':256,'logical_scan_threads':128,'comparison_pairs':148,'kernel_launches':296,'performance_measurement':False,'candidate_accepted':False}
ck(all(d051[k]==v for k,v in contract.items()),'sealed_D051_numerical_prerequisite')
ck(dt(d051['at'])<=dt(A['at']) and dt(d050['at'])<=dt(A['at']),'D050_D051_before_authorization')

ck(dt(A['at'])<=dt(activation['at'])<=dt(BE['at'])<dt(INV['at']),'activation_build_execution_order')
custody=load(OUT/'source-custody.json');ck(custody['source_sha256']==Csrc and custody['source_entry_count']==162,'active_candidate162_captured_before_restore')
ck(all(Csrc[k]==P['candidate_owned_sha256'][k] for k in owned),'frozen_two_source_candidate_bytes')
result={'id':'E026-independent-terminal-review','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'verdict':'CONFIRMED_PROVISIONAL_QUALIFYING' if not failed else 'CONFIRMED_REJECTED','primary':{'baseline_sum_fixture_medians_ms':Bsum,'candidate_sum_fixture_medians_ms':Csum,'gain_pct':score,'minimum_pct':2,'aggregate_gate_met':aggregate_pass,'fixture_guard_failed':guardfail},'all18_complete_non_timing_results_exact':True,'all_convergence_trajectories_exact':True,'trajectories':trajectory,'unit_inventory':{'passed':84,'failed':0,'ignored':4,'measured':0,'filtered':0,'matches_E020_inventory':True},'source_scope':C['source_changes'],'source_entries_each':len(Bsrc),'chronology':chron,'components':fixture_tables,'pairs':pairs,'component_median_caution':'Per-component medians and median paired deltas are descriptive; their sums need not equal median whole-cycle differences and do not establish causes.','checks':dict(checks),'check_assertions':sum(checks.values()),'broader_correctness':'Not run at this primary audit. If rejected, no broader/holdout/cumulative or extension qualifies; if qualifying, original broader/F32/GPU/continuation controls, wide-turn and fresh cumulative qualification remain mandatory.','scope_limits':['Exact compressed CPU state plus exploitability/trajectory checks do not establish all possible raw F32 states','Source compatibility is not native proof; candidate-shared unit references do not replace immutable original broader controls','Full-cycle score includes runtime NVRTC/JIT and readback; excludes Cargo, fingerprinting/final destruction/browser/API/disk saving','Warm-driver-cache cohort; no experimentally controlled cold startup or statistical significance claim','Original E020 source remains retained baseline; no revival or additional timing extension authorized'],'reviewer_attempt_note':'Narrow adaptation of successful E025 file-only audit after root terminal notification. Changed fixed IDs/pins, two owned showdown files, embedded changed-CUDA provenance and sealed D050/D051 prerequisite pins; authorization timestamp remains at. No proof rerun, helper import, compiler/native/GPU execution or outcome-triggered extension.', 'holdout_freeze':holdout, 'review_actions':'Read-only source/evidence analysis and additive review artifacts; no builds/GPU/production/status mutation','artifacts':artifacts}
with (OUT/'validation.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'primary':result['primary'],'checks':sum(checks.values()),'source_entries':len(Bsrc),'trajectory_checks':sum(t['count'] for t in trajectory),'components':[{ 'fixture':t['fixture_id'],'delta_ms':{k:round(v['candidate_minus_baseline_median_ms'],4) for k,v in t['components'].items()}} for t in fixture_tables],'pairs':[p['gain_pct'] for p in pairs],'validation_sha256':sha(OUT/'validation.json')},indent=2))
