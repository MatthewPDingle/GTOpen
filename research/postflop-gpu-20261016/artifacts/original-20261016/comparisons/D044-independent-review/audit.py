import pathlib,json,hashlib,statistics,math,re,datetime,sys
assert sys.argv[1:]==['--root-confirmed-terminal'], 'Execute only after root confirms cohort and assessment terminal'
R=pathlib.Path(r'S:\GTOpen-research\postflop-gpu-20261016');W=pathlib.Path(r'X:\Dev\GTOpen-gpu-research-20261016');P=R/'runs/D044-constructor-diagnostic';O=R/'comparisons/D044-independent-review';E=R/'runs/D044-execution'
inputs={}
def sha(p):
 p=pathlib.Path(p);h=hashlib.sha256(p.read_bytes()).hexdigest();inputs[str(p)]=h;return h
def rd(p):sha(p);return json.loads(pathlib.Path(p).read_text(encoding='utf-8-sig'))
def pin(p,h):assert sha(p)==h,str(p)
def dt(s):return datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
def close(x,y):assert math.isclose(x,y,abs_tol=1e-9,rel_tol=1e-12),(x,y)
def strip(x):return {k:v for k,v in x.items() if k not in T}
T={'build_ms','init_ms','solve_ms','readback_ms','full_cycle_ms','fingerprint_ms_excluded','solve_checks_elapsed_ms'}
pin(P/'authorization.json','822a0fb14ac5116ef717b8b53ef7a2cff734201b4b2d45f4029e495ad5fa608a');pin(P/'protocol.json','f6565a31fccabb51e51ce9017026e7f5ba23e65c03e0a507f183ef6265aab58a');pin(P/'scripts-manifest.json','179fa88dc90ee3b551debf76f837aef38b0af2012468f0c41d91e87839642bf8')
A=rd(P/'authorization.json');S=rd(P/'scripts-manifest.json');Q=rd(P/'protocol.json');C=rd(R/'comparisons/D044-constructor-diagnostic/report.json')
for group in ['script_sha256','supporting_sha256']:
 for n,h in S[group].items():pin(P/n,h)
for p,h in {**S['reference_sha256'],**A['evidence_sha256']}.items():pin(p,h)
review=rd(A['prerequisites']['D044_source_review']['path']);scriptreview=rd(A['prerequisites']['D044_script_review']['path']);assert review['independent_source_review_pass'] and scriptreview['independent_script_review_pass'] and review['findings']==scriptreview['findings']==[]
assert all(A[k] is True for k in ['E020_accepted','E020_server_qualification_pass','independent_source_review_pass','independent_script_review_pass'])
pin(P/'activation.json','9a4b2025fe74fb5183efff688db7dae451d1b2f5041177c77729fb14d68eead3');activation=rd(P/'activation.json')
B=rd(R/'binaries/E020-postflop_autoresearch.manifest.json');D=rd(R/'binaries/D044-postflop_autoresearch.manifest.json')
for n,m in [('E020',B),('D044',D)]:pin(R/f'binaries/{n}-postflop_autoresearch.exe',m['binary_sha256'])
assert D['primary_protocol_sha256']==sha(P/'protocol.json') and D['probe_authorization_sha256']==sha(P/'authorization.json') and D['build_script_sha256']==sha(P/'build.py')
assert len(D['source_sha256'])==len(B['source_sha256'])==162 and set(D['source_sha256'])==set(B['source_sha256'])
assert [k for k in D['source_sha256'] if D['source_sha256'][k]!=B['source_sha256'][k]]==['crates/solver/src/game.rs']
for k,v in A['candidate_sources'].items():pin(v['path'],v['sha256']);assert D['source_sha256'][k]==v['sha256'];pin(D['source_copies'][k]['path'],v['sha256'])
pin(R/'binaries/D044-postflop_autoresearch.exe','89969e159d68179d784c6a843ac99832b8dd9ce8b7c0764d343ac4a51c4257e3')
assert activation['source_before']['source_sha256']==B['source_sha256'] and activation['source_after']['source_sha256']==D['source_sha256']
assert activation['authorization_sha256']==sha(P/'authorization.json') and activation['owned_files']==Q['owned_sources'] and activation['unchanged_source_entries']==161 and activation['all_accepted_sources_verified_before'] and not activation['main_or_live_changes']
assert D['source_matches_prebuild'] and D['source_sha256']==rd(R/'runs/D044-build/source-before.json')['source_sha256']
assert D['probe_evidence_sha256']==A['evidence_sha256']
for field,hfield in [('build_log','build_log_sha256'),('build_stderr_log','build_stderr_sha256'),('patch','patch_sha256')]:pin(D[field],D[hfield])
be=rd(R/'runs/D044-build/exit.json');assert be['returncode']==0 and be['error'] is None and be['cleanup'] is None
logs=[json.loads(l) for l in pathlib.Path(D['build_log']).read_text().splitlines()];assert any(x.get('reason')=='build-finished' and x['success'] for x in logs)
for f in ['solver_artifact','cargo_artifact']:
 a=D[f];assert not a['fresh'] and pathlib.Path(a['manifest_path']).resolve()==(W/'crates/solver/Cargo.toml').resolve()
 for n in a.get('filenames',[])+([a['executable']] if a.get('executable') else []):assert pathlib.Path(n).resolve().is_relative_to(pathlib.Path(Q['build_target_root']).resolve())
assert D['solver_artifact']['target']['src_path']==str(W/'crates/solver/src/lib.rs') and D['cargo_artifact']['target']['src_path']==str(W/'crates/solver/tests/postflop_autoresearch.rs')
cuda=(R/'runs/D037-showdown-cache-design/candidate/kernels.cu').read_bytes()
for name,m in [('E020',B),('D044',D)]:
 data=(R/f'binaries/{name}-postflop_autoresearch.exe').read_bytes();assert cuda in data and (b'SPOT_CONSTRUCTOR_PROFILE' in data)==(name=='D044')
inv=rd(E/'invocation.json');done=rd(E/'complete.json');assert inv['order']==done['order']==Q['order']==['D044B1','D044P1','D044P2','D044B2','D044B3','D044P3']
assert inv['source_sha256']==D['source_sha256'] and inv['script_sha256']==sha(P/'cohort.py') and inv['primary_protocol_sha256']==sha(P/'protocol.json') and inv['build_terminal_before_launch']
assert dt(review['at'])<dt(A['authorized_at']) and dt(S['at'])<=dt(scriptreview['at'])<dt(A['authorized_at'])<=dt(activation['at'])<dt(be['at'])<dt(inv['at'])
envbuild=rd(R/'runs/D044-build/build-environment.json');assert envbuild['target_previously_absent'] and envbuild['compiler_override_absence']=={} and envbuild['RAYON_NUM_THREADS']=='16' and envbuild['target_dir']==Q['build_target_root']
for row in logs:
 if row.get('reason')=='compiler-artifact':
  for f in row.get('filenames',[])+([row['executable']] if row.get('executable') else []):assert pathlib.Path(f).resolve().is_relative_to(pathlib.Path(Q['build_target_root']).resolve())

schema=rd(P/'schema.json');identity_expected={v['fixture_id']:v for v in schema['expected_identity']}
raw={};marks=[];ref=refchecks=refst=None;chron=[];env=None;check_count=0
for identity in Q['order']:
 d=R/f'runs/{identity}';r=rd(d/'report.json');pin(d/'stdout.log',r['stdout_sha256']);instrumented=identity.startswith('D044P');m=D if instrumented else B
 assert r['status']=='measured' and r['returncode']==0 and r['test_pass_count']==1 and r['kind']=='diagnostic'
 assert r['binary_sha256']==m['binary_sha256'] and r['binary_build_manifest']['data']==m and r['binary_build_manifest']['binary_hash_verified'];pin(r['binary_build_manifest']['path'],r['binary_build_manifest']['sha256'])
 assert r['provenance']['source_sha256']==D['source_sha256']
 assert r['command'][1:]==['postflop_complete_cycle','--nocapture','--test-threads=1','--ignored']
 pin(r['command'][0],m['binary_sha256'])
 expected={'RAYON_NUM_THREADS':'16','POSTFLOP_AUTORESEARCH_FIXTURE':None,'POSTFLOP_AUTORESEARCH_STORAGE':'compressed','POSTFLOP_AUTORESEARCH_PROFILE':'0'}
 assert all(r['environment'][k]==v for k,v in expected.items())
 if env is None:env=r['environment']
 assert r['environment']==env
 si=rd(E/f'{identity}.invocation.json');se=rd(E/f'{identity}.exit.json');assert se['returncode']==0 and se['error'] is None and se['cleanup'] is None
 assert dt(si['at'])<=dt(r['started_at'])<=dt(r['finished_at'])<=dt(se['at'])
 txt=(d/'stdout.log').read_text();assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',txt)==[('1','0','0','0','0')]
 st=[];rs=[];pr=[];fixture=stage=None;starts={};builds={}
 for line in txt.splitlines():
  if 'AUTORESEARCH_STAGE ' in line:
   v=json.loads(line.split('AUTORESEARCH_STAGE ',1)[1]);st.append(v);stage=v['stage']
   if stage=='fixture_start':
    fixture=v['fixture_id'];assert fixture not in starts;starts[fixture]=v
   if stage=='build_complete':
    assert fixture==v['fixture_id'] and fixture not in builds;builds[fixture]=v
  if 'AUTORESEARCH_RESULT ' in line:rs.append(json.loads(line.split('AUTORESEARCH_RESULT ',1)[1]))
  if 'SPOT_CONSTRUCTOR_PROFILE ' in line:
   assert stage=='fixture_start';v=json.loads(line.split('SPOT_CONSTRUCTOR_PROFILE ',1)[1]);assert set(v)==set(schema['record']);pr.append({'run_id':identity,'fixture_id':fixture,**v})
 assert rs==r['results'] and st==[v['data'] for v in r['stages']]
 assert list(starts)==list(builds)==[v['fixture_id'] for v in rs]==Q['expected_fixtures'] and [v['iteration'] for v in rs]==[200,200,60] and all(v['target_met'] for v in rs)
 assert st[0]['stage']=='suite_start' and st[0]['primary_suite'] and not st[0]['smoke_only'] and not st[0]['profile_after_timing'] and st[-1]['stage']=='suite_complete' and st[-1]['fixtures_completed']==3
 checks=[strip(v) for v in st if v['stage']=='convergence_check'];assert len(checks)==23;check_count+=len(checks)
 for v in rs:
  assert [x['iteration'] for x in checks if x['fixture_id']==v['fixture_id']]==list(range(20,v['iteration']+1,20))
  assert v['target_pct']==.3 and v['check_every']==20 and v['max_iterations']==400 and v['storage']=='compressed'
  assert all(type(v[k]) in (int,float) and math.isfinite(v[k]) and v[k]>=0 for k in T if k in v)
  assert v['full_cycle_ms']>0 and v['build_ms']==builds[v['fixture_id']]['build_ms']
 exact=[strip(v) for v in rs];exactst=[strip(v) for v in st]
 if ref is None:ref,refchecks,refst=exact,checks,exactst
 assert exact==ref and checks==refchecks and exactst==refst
 assert len(pr)==(3 if instrumented else 0)
 if instrumented:assert [v['fixture_id'] for v in pr]==Q['expected_fixtures']
 for v in pr:
  assert type(v['schema_version']) is int and v['schema_version']==1 and v['diagnostic_only'] is True and v['instrumentation']=='D044_unconditional_source_only'
  assert type(v['extra_cuda_synchronizations']) is int and v['extra_cuda_synchronizations']==0
  assert set(v['stage_us'])==set(Q['stage_names'])=={'tree_build','river_table','suit_symmetry'}
  assert all(type(x) in (int,float) and math.isfinite(x) and x>=0 for x in [*v['stage_us'].values(),v['constructor_us_before_logging']])
  assert all(type(v[k]) is int for k in ['board_mask','board_cards','node_count','suit_permutations']) and 1<=v['suit_permutations']<=24
  assert len(v['hands'])==2 and all(type(x) is int and x>0 for x in v['hands'])
  ident=identity_expected[v['fixture_id']];build=builds[v['fixture_id']]
  assert all(v[k]==ident[k] for k in ['board_mask','board_cards','node_count','hands']) and starts[v['fixture_id']]['board']==ident['board']
  assert build['nodes']==v['node_count'] and build['hands']==v['hands']
  assert v['constructor_us_before_logging']+1e-6>=sum(v['stage_us'].values()) and build['build_ms']*1000+1e-6>=v['constructor_us_before_logging']
 marks.extend(pr);raw[identity]={'report':r,'results':rs,'profiles':pr};chron.append({'id':identity,'start':r['started_at'],'finish':r['finished_at']})
for x,y in zip(chron,chron[1:]):assert dt(x['finish'])<dt(y['start'])
assert dt(inv['at'])<=dt(chron[0]['start']) and dt(chron[-1]['finish'])<=dt(done['at'])
assert len(marks)==9 and marks==C['raw_profiles'] and C['all_complete_states_exact']==18 and C['convergence_checks_exact']==check_count==138 and C['profile_records']==9 and C['uninstrumented_records']==0
Bids=[p['baseline'] for p in Q['pairs']];Pids=[p['candidate'] for p in Q['pairs']];bs=ps=0.0;table=[];grouped={k:0.0 for k in Q['stage_names']}
for i,f in enumerate(Q['expected_fixtures']):
 b=[raw[x]['results'][i]['full_cycle_ms'] for x in Bids];p=[raw[x]['results'][i]['full_cycle_ms'] for x in Pids];bm=statistics.median(b);pm=statistics.median(p);bs+=bm;ps+=pm;decl=C['fixtures'][i]
 assert decl['fixture_id']==f and decl['ordinary_full_cycles_ms']==b and decl['instrumented_full_cycles_ms']==p;close(decl['ordinary_median_ms'],bm);close(decl['instrumented_median_ms'],pm);close(decl['median_change_pct'],100*(pm/bm-1))
 for x,y,z in zip(b,p,decl['paired_change_pct']):close(z,100*(y/x-1))
 records=[raw[x]['profiles'][i] for x in Pids];assert len({v['suit_permutations'] for v in records})==1
 assert decl['identity']=={**identity_expected[f],'suit_permutations':records[0]['suit_permutations']}
 for names,key in [(Bids,'ordinary_build_ms'),(Pids,'instrumented_build_ms')]:assert decl[key]==[raw[n]['results'][i]['build_ms'] for n in names]
 values={k:[v['stage_us'][k]/1000 for v in records] for k in Q['stage_names']}
 values['constructor_before_logging']=[v['constructor_us_before_logging']/1000 for v in records]
 values['unprofiled_constructor_and_timer_overhead']=[(v['constructor_us_before_logging']-sum(v['stage_us'].values()))/1000 for v in records]
 values['unprofiled_constructor_CPU_storage_and_timing_logging_overhead']=[raw[n]['results'][i]['build_ms']-sum(v['stage_us'].values())/1000 for n,v in zip(Pids,records)]
 values['outer_build_minus_constructor_CPU_storage_return_logging_other_overhead']=[raw[n]['results'][i]['build_ms']-v['constructor_us_before_logging']/1000 for n,v in zip(Pids,records)]
 assert {v['stage'] for v in decl['components']}==set(values)
 parts={}
 for stage,vs in values.items():
  median=statistics.median(vs);c=next(x for x in decl['components'] if x['stage']==stage)
  assert c['all_profiled_ms']==vs and c['range_ms']==[min(vs),max(vs)];close(c['median_ms'],median);parts[stage]={'raw_ms':vs,'median_ms':median,'range_ms':[min(vs),max(vs)]}
  if stage in grouped:grouped[stage]+=median
 table.append({'fixture':f,'ordinary_ms':bm,'instrumented_ms':pm,'median_change_pct':100*(pm/bm-1),'paired_change_pct':decl['paired_change_pct'],'components':parts})
change=100*(ps/bs-1);useful=abs(change)<=10
for k,v in [('ordinary_sum_fixture_medians_ms',bs),('instrumented_sum_fixture_medians_ms',ps),('observed_outer_change_pct',change)]:close(C[k],v)
for k,v in grouped.items():close(C['grouped_stage_sum_fixture_medians_ms'][k],v);close(C['grouped_stage_fraction_of_ordinary_pct'][k],100*v/bs)
assert C['absolute_change_limit_pct']==Q['usefulness_guard']['maximum_percent']==10 and C['diagnostic_usefulness_guard_pass']==useful and C['status']==('pass' if useful else 'inconclusive')
assert not C['candidate_accepted'] and not C['possible_2pct_saving_established'] and not C['deployment_changed'] and not Q['performance_acceptance'] and not Q['outcome_triggered_extensions'] and Q['exclusions']==[]
for n in Q['order']:
 assert C['evidence'][n]['report_sha256']==sha(R/f'runs/{n}/report.json') and C['evidence'][n]['stdout_sha256']==sha(R/f'runs/{n}/stdout.log')
 close(C['native_process_wall_ms_including_teardown'][n],raw[n]['report']['process_wall_ms'])
assert C['protocol_sha256']==sha(P/'protocol.json') and C['schema_sha256']==sha(P/'schema.json')
assert C['binary_manifests']=={'ordinary':sha(R/'binaries/E020-postflop_autoresearch.manifest.json'),'instrumented':sha(R/'binaries/D044-postflop_autoresearch.manifest.json')}
current={k:sha(W/k) for k in D['source_sha256']};assert current==D['source_sha256']
result={'id':'D044-independent-review','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'verdict':'PASS_SCOPED_DIAGNOSTIC' if useful else 'EXACT_BUT_USEFULNESS_INCONCLUSIVE','full_non_timing_records_exact':18,'convergence_checks_exact':138,'complete_stage_trajectories_exact':True,'profile_markers_verified':9,'markers_per_instrumented_run':3,'ordinary_profile_markers':0,'all162_current_source_entries_match_build':True,'game_candidate_sha256':current['crates/solver/src/game.rs'],'chronology':chron,'ordinary_sum_fixture_medians_ms':bs,'instrumented_sum_fixture_medians_ms':ps,'outer_change_pct':change,'absolute10pct_guard_pass':useful,'grouped_stage_sum_fixture_medians_ms':grouped,'grouped_stage_fraction_of_ordinary_pct':{k:100*v/bs for k,v in grouped.items()},'fixtures':table,'accepted':False,'interpretation':'Grouped diagnostic host spans only. River-table time includes ranking, sorting, allocation, scheduling and cleanup; no removable fraction or speedup is established. Constructor and outer residuals overlap different setup/return/destruction/logging work. The outer10% guard does not bound component bias. No optimization accepted.','review_actions':'File reads and additive audit outputs only; no native, build, GPU or checkout mutation','input_sha256':inputs}
with (O/'validation.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({k:result[k] for k in ['verdict','outer_change_pct','grouped_stage_sum_fixture_medians_ms','grouped_stage_fraction_of_ordinary_pct']},indent=2));print('validation_sha256',sha(O/'validation.json'))
