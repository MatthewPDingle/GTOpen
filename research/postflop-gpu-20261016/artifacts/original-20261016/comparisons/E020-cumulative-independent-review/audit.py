import pathlib,json,hashlib,datetime,statistics,math,re,collections
R=pathlib.Path(r'S:\GTOpen-research\postflop-gpu-20261016');P=R/'runs/E020-qualification-plan-r3';O=R/'comparisons/E020-cumulative-independent-review';W=pathlib.Path(r'X:\Dev\GTOpen-gpu-research-20261016');art={};checks=collections.Counter()
def ck(v,label):
 assert v,label;checks[label]+=1
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def pin(p,h=None):
 p=pathlib.Path(p);a=sha(p);ck(h is None or a==h,'artifact_hash');art[str(p)]=a;return a
def load(p):pin(p);return json.loads(pathlib.Path(p).read_text(encoding='utf-8-sig'))
def dt(s):return datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
def near(a,b):return math.isclose(a,b,abs_tol=1e-8,rel_tol=1e-12)
def unique(pairs):
 d={}
 for k,v in pairs:ck(k not in d,'raw_unique_keys');d[k]=v
 return d
def bad(s):raise AssertionError('nonfinite JSON '+s)
def records(raw,tag):return [json.loads(l.split(tag+' ',1)[1],object_pairs_hook=unique,parse_constant=bad) for l in raw.splitlines() if tag+' ' in l]
def smap(m):return {k.replace('\\','/'):v.lower() for k,v in m.get('source_sha256',m.get('hashes',{})).items()}
T={'build_ms','init_ms','solve_ms','readback_ms','full_cycle_ms','fingerprint_ms_excluded'}
def nt(x):return {k:v for k,v in x.items() if k not in T|{'solve_checks_elapsed_ms'}}
proto=load(P/'protocol.json');pin(P/'protocol.json','51f48a84a7dce494eae9d6f06f75a4e78dff654c424a8ac3482d02d551686bb9')
auth=load(P/'authorization.json');pin(P/'authorization.json','e935a6b3f29f4de2b44cb7724adc6499119b68afa1934265e218dd76f559c76f')
prep=load(P/'prepared-manifest.json');pin(P/'prepared-manifest.json','e2e1e7a896f70eb54107bf4d83c6d9334953bbcbfcc20d7ad5db94850121110d')
for n,h in prep['artifact_sha256'].items():pin(P/n,h)
q=load(P/'qualification-ready.json');pin(P/'qualification-ready.json','526c3e5d8b5c0b07277acfec09f3f09062c451640462212f015fe9dcce5dbfdb')
for k in ['broader_pass','holdout_pass','independent_broader_review_pass','independent_holdout_review_pass']:ck(q[k] is True,'ready_gate')
for k in ['all_builds_ready','broader_report','holdout_report']:pin(q[k]['path'],q[k]['sha256'])
for p,h in q['evidence_sha256'].items():pin(p,h)
broad=load(R/'comparisons/E020-broader-independent-review/validation.json');hold=load(R/'comparisons/E020-holdout-independent-review/validation.json');primary=load(R/'comparisons/E020-independent-review/validation.json')
ck(broad['verdict']=='PASS_SCOPED_BROADER_CORRECTNESS' and hold['verdict']=='PASS_HOLDOUT_NONREGRESSION_ONLY','carried_reviews_pass')
pin(R/'comparisons/E020-independent-review/validation.json','ee2992d1066faeaf782f5276f7558521990f40a5cfbeece91cade970464fd438')
inv=load(R/'runs/E020-cumulative-execution/invocation.json');term=load(R/'runs/E020-cumulative-execution/terminal.json');complete=load(R/'runs/E020-cumulative-execution/complete.json')
order=[x['id'] for x in proto['cumulative_order']];ck(order==['B065','E020C1','E020C2','B066','B067','E020C3']==inv['order']==term['completed']==complete['order'],'fixed_six_order');ck(term['error'] is None and term['no_exclusions'] and term['no_extension'],'no_exclusion_or_extension')
ck(inv['pairs']==proto['pairs'] and inv['authorization_sha256']==sha(P/'authorization.json') and inv['qualification_ready_sha256']==sha(P/'qualification-ready.json')==complete['qualification_ready_sha256'],'invocation_gates');ck(complete['status']=='pass' and inv['all_builds_terminal'],'terminal_success')
C=load(R/'comparisons/E020-cumulative-comparison/report.json');ck(C['decision']=='qualifying' and C['excluded_runs']==[] and not C['accepted'] and not C['deployed'],'comparison_provisional')
for row in C['preserved_artifacts']+C['input_reports']:pin(row['path'],row['sha256'])
pin(C['frozen_manifest']['path'],C['frozen_manifest']['sha256'])
assessment=R/'runs/E020-cumulative-assessment';ai=load(assessment/'invocation.json');ac=load(assessment/'complete.json');ae=load(assessment/'exit.json')
for n in ['stdout.log','stderr.log']:pin(assessment/n)
ck(ai['failures']==[] and ae['returncode']==0 and ac['all18_nontiming_objects_exact'] and ac['status']=='pass','assessment_terminal');pin(ac['report']['path'],ac['report']['sha256']);ck(ai['authorization_sha256']==sha(P/'authorization.json'),'assessment_auth')
cmd=ai['command'];ck(cmd[cmd.index('--candidate-id')+1]=='E020R1' and cmd[cmd.index('--baseline-runs')+1:cmd.index('--candidate-runs')]==['B065','B066','B067'] and cmd[cmd.index('--candidate-runs')+1:]==['E020C1','E020C2','E020C3','--warm-cache-cohort'],'assessment_exact_alias_and_cohort')
source=load(P/'primary-source.json');base=load(R/'binaries/baseline-complete.manifest.json');cand=load(R/'binaries/E020-postflop_autoresearch.manifest.json');ck(smap(cand)==source,'candidate_source_manifest')
for rel in ['crates/solver/src/gpu/kernels.cu','crates/solver/src/gpu/mod.rs','crates/solver/tests/postflop_autoresearch.rs','bench_spot.json']:pin(W/rel,source[rel])
changed=[k for k,v in smap(base).items() if source[k]!=v];ck(sorted(changed)==sorted(['crates/solver/src/gpu/arena.rs','crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/kernels.cu']),'known_common_original_source_delta')
# Missing baseline manifest entries are unknown, not asserted changes; primary source review supplies the full accepted-E015 two-file proof.
anchor=load(R/'runs/B062/report.json');anchorraw=(R/'runs/B062/stdout.log').read_text();pin(R/'runs/B062/stdout.log',anchor['stdout_sha256']);ar=records(anchorraw,'AUTORESEARCH_RESULT');ast=records(anchorraw,'AUTORESEARCH_STAGE');ck(ar==anchor['results'],'carried_primary_anchor_raw')
runs={};states={};stages={};chronology=[];gpus=[];timing={};whole=[]
for row in proto['cumulative_order']:
 ident=row['id'];d=R/'runs'/ident;r=load(d/'report.json');raw=(d/'stdout.log').read_text();pin(d/'stdout.log',r['stdout_sha256']);ck(r['status']=='measured' and r['returncode']==0 and r['test_pass_count']==1,'run_terminal')
 native=re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out; finished in ([0-9.]+)s',raw);ck(len(native)==1 and tuple(map(int,native[0][:5]))==(1,0,0,0,0),'one_native_test_pass')
 ck(r['command'][1:]==['postflop_complete_cycle','--nocapture','--test-threads=1','--ignored'],'fixed_native_command')
 bp=inv['binary_pins'][row['binary']];pin(r['command'][0],bp['binary_sha256']);bm=r['binary_build_manifest'];pin(bm['path'],bp['manifest_sha256']);m=load(bm['path']);ck(m==bm['data'] and bm['binary_hash_verified'] and r['binary_sha256']==m['binary_sha256']==bp['binary_sha256'],'binary_provenance')
 ck(smap(m)==(smap(base) if row['kind']=='baseline' else source),'actual_binary_source');ck(r['provenance']['source_sha256']==source,'runtime_checkout_snapshot_distinct')
 ck(r['environment']==C['environment'] and r['environment']['RAYON_NUM_THREADS']=='16' and r['environment']['POSTFLOP_AUTORESEARCH_STORAGE']=='compressed' and r['environment']['POSTFLOP_AUTORESEARCH_PROFILE']=='0' and r['environment']['POSTFLOP_AUTORESEARCH_FIXTURE'] is None,'fixed_environment')
 for k in ['live_status_before','live_status_at_launch']:
  live=r[k];ck(live['/api/status']['state']=='idle' and live['/api/preflop/status']['state'] in ['', 'idle'] and not live['/api/reports/status']['running'],'live_idle')
 ck(r['disk_free_bytes']>proto['resource_policy']['disk_reserve_bytes'],'disk_reserve')
 for k in ['telemetry_before','telemetry_after']:
  g=r[k]['gpu'];ck(g['returncode']==0,'telemetry_success');gpus.append(tuple(x.strip() for x in g['stdout'].split(',')[:4]))
 rr=records(raw,'AUTORESEARCH_RESULT');ss=records(raw,'AUTORESEARCH_STAGE');ck(rr==r['results'] and ss==[s['data'] for s in r['stages']],'raw_report_exact')
 ck([x['fixture_id'] for x in rr]==['rainbow','two-tone','river'] and [x['iteration'] for x in rr]==[200,200,60],'fixed_fixtures_stops')
 ck([nt(x) for x in rr]==[nt(x) for x in ar],'all_complete_nontiming_exact');ck([nt(x) for x in ss]==[nt(x) for x in ast],'all_stage_trajectories_exact')
 conv=[x for x in ss if x['stage']=='convergence_check'];ck(len(conv)==23,'23_convergence_records')
 for f,n in zip(['rainbow','two-tone','river'],[200,200,60]):ck([x['iteration'] for x in conv if x['fixture_id']==f]==list(range(20,n+1,20)),'fixed_check_schedule')
 for x in rr:
  ck(x['target_met'] and x['target_pct']==0.3 and x['check_every']==20 and x['max_iterations']==400 and x['algorithm']=='Dcfr' and x['storage']=='compressed' and x['use_isomorphism'],'fixed_quality')
  ck(x['runtime_nvrtc_jit_included'] and x['flushed_progress_logging_included'],'timing_boundaries')
  for t in T:ck(math.isfinite(x[t]) and x[t]>=0,'finite_nonnegative_timing')
  ck(x['full_cycle_ms']>=sum(x[t] for t in ['build_ms','init_ms','solve_ms','readback_ms']),'true_wall_includes_components')
 runs[ident]=r;states[ident]=rr;stages[ident]=ss;timing[ident]={x['fixture_id']:{t:x[t] for t in T} for x in rr};chronology.append({'id':ident,'started_at':r['started_at'],'finished_at':r['finished_at']});whole.append({'id':ident,'process_wall_ms':r['process_wall_ms'],'native_test_seconds':float(native[0][5])})
ck(len(set(gpus))==1 and list(gpus[0])==C['gpu_identity'][0],'same_GPU_driver_memory_identity')
ck(chronology==C['chronology'],'published_chronology')
ck(dt(q['at'])<dt(inv['at'])<=dt(runs[order[0]]['started_at']),'ready_precedes_all_native')
for a,b in zip(order,order[1:]):ck(dt(runs[a]['finished_at'])<dt(runs[b]['started_at']),'serialized_six_chronology')
ck(dt(runs[order[-1]]['finished_at'])<=dt(term['at'])<=dt(ai['at']),'terminal_before_assessment')
B=['B065','B066','B067'];N=['E020C1','E020C2','E020C3'];fixtures=[]
for i,f in enumerate(['rainbow','two-tone','river']):
 pub=C['fixtures'][i];components={}
 for field in ['full_cycle_ms','build_ms','init_ms','solve_ms','readback_ms']:
  bv=[timing[x][f][field] for x in B];nv=[timing[x][f][field] for x in N];bm=statistics.median(bv);nm=statistics.median(nv)
  ck(pub['baseline'][field]['raw_ms']==bv and pub['candidate'][field]['raw_ms']==nv and near(pub['baseline'][field]['median_ms'],bm) and near(pub['candidate'][field]['median_ms'],nm),'raw_component_stats')
  components[field]={'baseline_median_ms':bm,'candidate_median_ms':nm,'median_delta_ms':nm-bm,'paired_delta_ms':[n-b for b,n in zip(bv,nv)]}
 b=components['full_cycle_ms']['baseline_median_ms'];n=components['full_cycle_ms']['candidate_median_ms'];reg=(n/b-1)*100;prs=[(timing[c][f]['full_cycle_ms']/timing[a][f]['full_cycle_ms']-1)*100 for a,c in zip(B,N)];above=sum(p>3 for p in prs);failed=reg>3 and above>=2
 guard=C['performance']['fixture_regression_guard']['fixtures'][i];ck(near(reg,guard['median_regression_pct']) and all(near(a,b) for a,b in zip(prs,guard['paired_regression_pct'])) and above==guard['repetitions_above_3pct'] and failed==guard['repeatable_material_regression'],'recomputed_fixture_guard')
 fixtures.append({'fixture_id':f,'components':components,'median_regression_pct':reg,'paired_regression_pct':prs,'above3_count':above,'guard_failed':failed})
bs=sum(f['components']['full_cycle_ms']['baseline_median_ms'] for f in fixtures);ns=sum(f['components']['full_cycle_ms']['candidate_median_ms'] for f in fixtures);gain=(bs-ns)/bs*100
perf=C['performance'];ck(near(bs,perf['baseline_full_cycle_ms']) and near(ns,perf['candidate_full_cycle_ms']) and near(gain,perf['observed_gain_pct']) and perf['required_gain_pct']==2 and gain>=2 and perf['aggregate_gate_met'],'recomputed_primary_score');ck(not any(x['guard_failed'] for x in fixtures) and not perf['fixture_regression_guard']['failed'],'no_fixture_guard_failure')
paired=[]
for j,(a,c) in enumerate(zip(B,N)):
 b=sum(x['full_cycle_ms'] for x in states[a]);n=sum(x['full_cycle_ms'] for x in states[c]);g=(b-n)/b*100;pub=C['pairs'][j];ck(pub['baseline_id']==a and pub['candidate_id']==c and near(pub['baseline_full_cycle_ms'],b) and near(pub['candidate_full_cycle_ms'],n) and near(pub['observed_gain_pct'],g),'recomputed_pair')
 paired.append({'baseline':a,'candidate':c,'gain_pct':g,'baseline_ms':b,'candidate_ms':n})
result={'id':'E020-cumulative-independent-review','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'verdict':'PASS_REGISTERED_CUMULATIVE_GATE','recommendation':'Accept E020 for the tested postflop GPU corpus, carrying prior primary/broader/holdout reviews; root controls adoption/deployment.','complete_results_exact':18,'convergence_records_exact':138,'all_raw_stages_exact':222,'baseline_sum_fixture_medians_ms':bs,'candidate_sum_fixture_medians_ms':ns,'gain_pct':gain,'aggregate_gate':True,'fixture_guard_failed':False,'fixtures':fixtures,'paired_runs':paired,'chronology':chronology,'whole_test_process_diagnostic':whole,'carried_review_paths':['comparisons/E020-independent-review/validation.json','comparisons/E020-broader-independent-review/validation.json','comparisons/E020-holdout-independent-review/validation.json'],'known_original_manifest_source_deltas':changed,'source_scope_note':'Original manifest records six selected files; absent entries are not evidence of source changes. Full two-file E020 scope versus accepted E015 was independently sealed in primary source audit.','comparison_template_note':'Comparison correctness.pending/broader.not_run/F32.not_run are helper placeholders; qualification-ready and separately sealed broader controls supply actual qualification.','limits':['Three paired observations, no significance or cold-start claim.','10.3798% is fresh-original cumulative performance, not the isolated E020 improvement or addition of historical percentages.','River median is 0.7128% slower; 1/3 pairs above3% means the unchanged material-repeat guard passes.','Fixed fixture median components describe this cohort only; sum of component medians need not equal full-cycle median.','Complete cycle includes runtime NVRTC/JIT, construction, solve/checks and full readback; excludes Cargo, correctness hashing, final destruction, API/disk.','Wide holdout does not establish every wider range/menu/device; F32 correctness was checked, not F32 performance.','Wrong-arm R1 holdout build preserved and unused; corrected R2 build readiness carried.'],'checks':dict(checks),'assertions':sum(checks.values()),'artifact_sha256':art,'review_actions':{'builds':0,'gpu_jobs':0,'native_tests':0,'production_edits':0,'dashboard_edits':0}}
with (O/'validation.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
print(json.dumps({k:result[k] for k in ['verdict','complete_results_exact','convergence_records_exact','gain_pct','fixture_guard_failed','assertions']},indent=2));print('validation_sha256',sha(O/'validation.json'))
