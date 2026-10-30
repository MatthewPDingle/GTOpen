import pathlib,json,hashlib,datetime,statistics,math,re,csv,collections
ROOT=pathlib.Path(r'S:\GTOpen-research\postflop-gpu-20261016'); REPO=pathlib.Path(r'X:\Dev\GTOpen-gpu-research-20261016')
OUT=ROOT/'comparisons/E019-independent-review'; PLAN=ROOT/'runs/E019-primary-plan'; EX=ROOT/'runs/E019-primary-execution'
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
P=load(PLAN/'protocol.json');C=load(ROOT/'comparisons/E019-three-pair-comparison/report.json');A=load(PLAN/'authorization.json');F=load(ROOT/'baseline-manifest.json')
pin(PLAN/'protocol.json','c74dfd6cbd57804c1fd8e9bad65744a8ab2b525f3e6aa230b5ed46c6959b1fba')
pin(OUT/'prospective-checklist.json','0527137908d158ab5dad070291ab82d2d4b292c66455da2b512881e58bdb4cc6')
for n,h in load(PLAN/'scripts-manifest.json')['script_sha256'].items():pin(PLAN/n,h)
for p,h in A['evidence_sha256'].items():pin(p,h)
ck(A['probe_exactness_pass'] and A['independent_review_pass'],'probe_prerequisite')
BM={}
for name in ['E015-postflop_autoresearch','E019-postflop_autoresearch','E019-solver']:
    m=load(ROOT/f'binaries/{name}.manifest.json');BM[name]=m;pin(ROOT/f'binaries/{name}.exe',m['binary_sha256'])
    ck(hashlib.sha256(json.dumps(m['source_sha256'],sort_keys=True).encode()).hexdigest()==m['source_manifest_sha256'],'build_source_manifest_digest')
    pin(m['build_log'],m['build_log_sha256']);pin(m['patch'],m['patch_sha256'])
    if 'build_stderr_sha256' in m:pin(m['build_stderr_log'],m['build_stderr_sha256'])
    if name.startswith('E019'):
        ck(m['source_matches_prebuild'] and m['source_sha256']==load(ROOT/'runs/E019-build/source-before.json')['source_sha256'],'build_before_after_source')
        ck(m['build_script_sha256']==sha(PLAN/'build.py') and m['primary_protocol_sha256']==sha(PLAN/'protocol.json') and m['probe_authorization_sha256']==sha(PLAN/'authorization.json'),'build_sealed_inputs')
        ck(m['probe_evidence_sha256']==A['evidence_sha256'],'build_probe_evidence')
ck(BM['E015-postflop_autoresearch']['binary_sha256']==P['reference_binary_sha256'],'pinned_E015_binary');pin(ROOT/'binaries/E015-postflop_autoresearch.manifest.json',P['reference_manifest_sha256'])
Bsrc=BM['E015-postflop_autoresearch']['source_sha256'];Csrc=BM['E019-postflop_autoresearch']['source_sha256'];owned='crates/solver/src/gpu/kernels.cu'
ck(set(Bsrc)==set(Csrc),'same_complete_source_keyset');ck([k for k in Bsrc if Bsrc[k]!=Csrc[k]]==[owned],'only_cuda_kernel_source_changed')
ck(Bsrc[owned]==P['accepted_kernel_sha256'] and Csrc[owned]==A['candidate_sha256'],'exact_D036_kernel_identity')
pin(ROOT/'runs/E019-build/candidate.cu',Csrc[owned]);pin(ROOT/'runs/E019-source/candidate.cu',Csrc[owned]);pin(ROOT/'runs/E019-source/accepted.cu',Bsrc[owned]);pin(A['candidate_source'],Csrc[owned])
for name in ['bench_spot.json','crates/solver/tests/postflop_autoresearch.rs']:
    ck(Bsrc[name]==Csrc[name]==F.get('source_sha256',F.get('hashes'))[name],'frozen_evaluator_and_workload')
BE=load(ROOT/'runs/E019-build/exit.json');ck(BE['returncode']==0 and BE['error'] is None and BE['cleanup'] is None,'build_terminal_success')
buildrows=[json.loads(s) for s in pathlib.Path(BM['E019-postflop_autoresearch']['build_log']).read_text().splitlines()]
ck(any(x.get('reason')=='build-finished' and x['success'] for x in buildrows),'cargo_raw_terminal_success')
targets=[x for x in buildrows if x.get('reason')=='compiler-artifact' and x.get('profile',{}).get('test') and x.get('executable') and x['target']['name'] in ['solver','postflop_autoresearch']]
ck(len(targets)==2 and {x['target']['name'] for x in targets}=={'solver','postflop_autoresearch'},'two_expected_build_targets')
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
    which='E019-solver' if identity=='V019-unit' else ('E015-postflop_autoresearch' if identity.startswith('B') else 'E019-postflop_autoresearch')
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
    expected=('84','0','4','0','0') if identity=='V019-unit' else ('1','0','0','0','0')
    ck(len(summary)==1 and tuple(summary[0][:5])==expected,'full_native_test_summary')
    ck(r['test_pass_count']==int(expected[0]),'reported_pass_count')
    summary_runtime[identity]=float(summary[0][-1])
    if identity=='V019-unit':unit_names=sorted(re.findall(r'^test (\S+) \.\.\. (?:ok|ignored)',text,re.M));continue
    ck(r['command'][1:]==['postflop_complete_cycle','--nocapture','--test-threads=1','--ignored'],'fixed_native_invocation')
    ck([x['fixture_id'] for x in rs]==['rainbow','two-tone','river'],'fixed_fixture_order')
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
priorunit=(ROOT/'runs/V015-unit/stdout.log').read_text();ck(unit_names==sorted(re.findall(r'^test (\S+) \.\.\. (?:ok|ignored)',priorunit,re.M)),'same_88_test_inventory')
EXCLUDE={'build_ms','init_ms','solve_ms','readback_ms','full_cycle_ms','fingerprint_ms_excluded'}
sexclude=EXCLUDE|{'solve_checks_elapsed_ms'}
ref=rawresults['B059'];refst=rawstages['B059'];trajectory=[]
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
ck(score<2 and not C['performance']['aggregate_gate_met'] and not any(t['guard']['failed'] for t in fixture_tables),'terminal_rejection_gate')
ck(C['decision']=='rejected' and not C['accepted'] and not C['deployed'] and C['excluded_runs']==[],'rejected_not_accepted_or_deployed_no_exclusions')
ck(C['correctness']['broader_validation']=='not run' and C['correctness']['f32_storage']=='not run','honest_unrun_broader_scope')
pairs=[]
for i,(b,c) in enumerate(zip(bs,cs)):
    pb=sum(x['full_cycle_ms'] for x in b['results']);pc=sum(x['full_cycle_ms'] for x in c['results'])
    close(C['pairs'][i]['baseline_full_cycle_ms'],pb,'pair_baseline_sum');close(C['pairs'][i]['candidate_full_cycle_ms'],pc,'pair_candidate_sum');close(C['pairs'][i]['observed_gain_pct'],gain(pb,pc),'pair_gain')
    pairs.append({'baseline':b['id'],'candidate':c['id'],'baseline_sum_ms':pb,'candidate_sum_ms':pc,'gain_pct':gain(pb,pc),'component_sum_candidate_minus_baseline_ms':{k:sum(x[k] for x in c['results'])-sum(x[k] for x in b['results']) for k in components},'process_wall_ms':{'baseline':b['process_wall_ms'],'candidate':c['process_wall_ms']},'whole_test_seconds':{'baseline':summary_runtime[b['id']],'candidate':summary_runtime[c['id']]}})
chron=[{'id':i,'started_at':runs[i]['started_at'],'finished_at':runs[i]['finished_at']} for i in ids[1:]];ck(C['chronology']==chron,'published_chronology')
ASSESS=ROOT/'runs/E019-assessment';ai=load(ASSESS/'invocation.json');link=load(ASSESS/'logical-run-link.json')
pin(PLAN/'assess.py',ai['script_sha256']);ck(ai['protocol_sha256']==sha(PLAN/'protocol.json'),'assessment_protocol_pin')
ck(ai['command'][ai['command'].index('--candidate-id')+1]=='E019R1' and '--reject' in ai['command'] and '--excluded-runs' not in ai['command'],'physical_comparison_identity')
ck(link['actual_run_ids']==[p['candidate'] for p in P['pairs']] and link['logical_candidate']=='E019' and not link['synthesized_measurement'],'explicit_logical_alias')
pin(link['patch_alias'],link['patch_sha256']);pin(link['source_patch'],link['patch_sha256']);ck(pathlib.Path(link['patch_alias']).read_bytes()==pathlib.Path(link['source_patch']).read_bytes(),'byte_exact_patch_alias')
ck(not (ROOT/'runs/E019/report.json').exists(),'no_synthetic_E019_measurement');ck(load(ASSESS/'exit.json')['returncode']==0,'assessment_terminal_success')
assessment_stdout=load(ASSESS/'stdout.log');ck(assessment_stdout['performance']==C['performance'] and assessment_stdout['decision']=='rejected','assessment_stdout_matches_report')
for item in C['preserved_artifacts']+C['input_reports']+[C['frozen_manifest'],C['original_candidate_report']]:pin(item['path'],item['sha256'])
ck(C['original_candidate_report']['id']=='E019R1' and C['candidate_id']=='E019R1','comparison_records_true_physical_id')
for folder in [PLAN,EX,ASSESS,ROOT/'runs/E019-build',ROOT/'runs/E019-source']:
    for p in folder.iterdir():
        if p.is_file():sha(p)
for p in [REPO/'tools/postflop_compare.py',REPO/'tools/postflop_autoresearch.py',OUT/'prospective-checklist.json',ROOT/'runs/V015-unit/stdout.log']:sha(p)
result={'id':'E019-independent-terminal-review','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'verdict':'CONFIRMED_REJECTED: aggregate improvement below registered2percent gate','primary':{'baseline_sum_fixture_medians_ms':Bsum,'candidate_sum_fixture_medians_ms':Csum,'gain_pct':score,'minimum_pct':2,'fixture_guard_failed':False},'all18_complete_non_timing_results_exact':True,'all_convergence_trajectories_exact':True,'trajectories':trajectory,'unit_inventory':{'passed':84,'failed':0,'ignored':4,'measured':0,'filtered':0,'matches_E015_inventory':True},'source_scope':C['source_changes'],'source_entries_each':len(Bsrc),'chronology':chron,'components':fixture_tables,'pairs':pairs,'component_median_caution':'Per-component medians and median paired deltas are descriptive; their sums need not equal median whole-cycle differences and do not establish causes.','checks':dict(checks),'check_assertions':sum(checks.values()),'broader_correctness':'Not run after failed primary screen; no original F32/menu/resume/continuation qualification or cumulative cohort for E019','scope_limits':['Exact compressed CPU state plus exploitability/trajectory checks do not establish all possible raw F32 states','D036 standalone proof and candidate-shared unit references do not replace immutable original broader controls','Full-cycle score includes runtime NVRTC/JIT and readback; excludes Cargo, fingerprinting/final destruction/browser/API/disk saving','Warm-driver-cache cohort; no experimentally controlled cold startup or statistical significance claim','Original E015 source remains retained baseline; no revival or additional timing extension authorized'],'review_actions':'Read-only source/evidence analysis and additive review artifacts; no builds/GPU/production/status mutation','artifacts':artifacts}
with (OUT/'validation.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'primary':result['primary'],'checks':sum(checks.values()),'source_entries':len(Bsrc),'trajectory_checks':sum(t['count'] for t in trajectory),'components':[{ 'fixture':t['fixture_id'],'delta_ms':{k:round(v['candidate_minus_baseline_median_ms'],4) for k,v in t['components'].items()}} for t in fixture_tables],'pairs':[p['gain_pct'] for p in pairs],'validation_sha256':sha(OUT/'validation.json')},indent=2))
