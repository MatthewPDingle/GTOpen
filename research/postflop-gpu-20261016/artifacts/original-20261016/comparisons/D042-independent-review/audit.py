import pathlib,json,hashlib,statistics,math,re,datetime,sys
assert sys.argv[1:]==['--root-confirmed-terminal'], 'Execute only after root confirms cohort and assessment terminal'
R=pathlib.Path(r'S:\GTOpen-research\postflop-gpu-20261016');W=pathlib.Path(r'X:\Dev\GTOpen-gpu-research-20261016');P=R/'runs/D042-zero-proof-diagnostic';O=R/'comparisons/D042-independent-review';E=R/'runs/D042-execution'
inputs={}
def sha(p):
 p=pathlib.Path(p);h=hashlib.sha256(p.read_bytes()).hexdigest();inputs[str(p)]=h;return h
def rd(p):sha(p);return json.loads(pathlib.Path(p).read_text(encoding='utf-8-sig'))
def pin(p,h):assert sha(p)==h,str(p)
def dt(s):return datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
def close(x,y):assert math.isclose(x,y,abs_tol=1e-9,rel_tol=1e-12),(x,y)
def strip(x):return {k:v for k,v in x.items() if k not in T}
T={'build_ms','init_ms','solve_ms','readback_ms','full_cycle_ms','fingerprint_ms_excluded','solve_checks_elapsed_ms'}
pin(P/'authorization.json','4291cd11f9666792051a7aef9ed5b926ca19401de19788d102d3a1da03ae5791');pin(P/'protocol.json','3ff2d365177915d851fca29e6d54e3472dc743dffd1d30ff5b64d74cf54e657c');pin(P/'scripts-manifest.json','b7721a495e97489fbb9bb1825f63c28b08c94e390e8b1c1aa8ea55df2164deb2')
A=rd(P/'authorization.json');S=rd(P/'scripts-manifest.json');Q=rd(P/'protocol.json');C=rd(R/'comparisons/D042-zero-proof-diagnostic/report.json')
for group in ['script_sha256','supporting_sha256']:
 for n,h in S[group].items():pin(P/n,h)
for p,h in {**S['reference_sha256'],**A['evidence_sha256']}.items():pin(p,h)
review=rd(A['prerequisites']['D042_source_review']['path']);assert review['independent_source_review_pass'] and review['independent_script_review_pass'] and review['findings']==[]
B=rd(R/'binaries/E020-postflop_autoresearch.manifest.json');D=rd(R/'binaries/D042-postflop_autoresearch.manifest.json')
for n,m in [('E020',B),('D042',D)]:pin(R/f'binaries/{n}-postflop_autoresearch.exe',m['binary_sha256'])
assert D['primary_protocol_sha256']==sha(P/'protocol.json') and D['probe_authorization_sha256']==sha(P/'authorization.json') and D['build_script_sha256']==sha(P/'build.py')
assert len(D['source_sha256'])==len(B['source_sha256'])==162 and set(D['source_sha256'])==set(B['source_sha256'])
assert [k for k in D['source_sha256'] if D['source_sha256'][k]!=B['source_sha256'][k]]==['crates/solver/src/gpu/arena.rs']
for k,v in A['candidate_sources'].items():pin(v['path'],v['sha256']);assert D['source_sha256'][k]==v['sha256'];pin(D['source_copies'][k]['path'],v['sha256'])
assert D['source_matches_prebuild'] and D['source_sha256']==rd(R/'runs/D042-build/source-before.json')['source_sha256']
assert D['probe_evidence_sha256']==A['evidence_sha256']
for field,hfield in [('build_log','build_log_sha256'),('build_stderr_log','build_stderr_sha256'),('patch','patch_sha256')]:pin(D[field],D[hfield])
be=rd(R/'runs/D042-build/exit.json');assert be['returncode']==0 and be['error'] is None and be['cleanup'] is None
logs=[json.loads(l) for l in pathlib.Path(D['build_log']).read_text().splitlines()];assert any(x.get('reason')=='build-finished' and x['success'] for x in logs)
for f in ['solver_artifact','cargo_artifact']:
 a=D[f];assert not a['fresh'] and pathlib.Path(a['manifest_path']).resolve()==(W/'crates/solver/Cargo.toml').resolve()
 for n in a.get('filenames',[])+([a['executable']] if a.get('executable') else []):assert pathlib.Path(n).resolve().is_relative_to(pathlib.Path(Q['build_target_root']).resolve())
assert D['solver_artifact']['target']['src_path']==str(W/'crates/solver/src/lib.rs') and D['cargo_artifact']['target']['src_path']==str(W/'crates/solver/tests/postflop_autoresearch.rs')
cuda=(R/'runs/D037-showdown-cache-design/candidate/kernels.cu').read_bytes()
for name,m in [('E020',B),('D042',D)]:
 data=(R/f'binaries/{name}-postflop_autoresearch.exe').read_bytes();assert cuda in data and (b'ZERO_UPLOAD_PROFILE' in data)==(name=='D042')
inv=rd(E/'invocation.json');done=rd(E/'complete.json');assert inv['order']==done['order']==Q['order']==['D042B1','D042P1','D042P2','D042B2','D042B3','D042P3']
assert inv['source_sha256']==D['source_sha256'] and inv['script_sha256']==sha(P/'cohort.py') and inv['primary_protocol_sha256']==sha(P/'protocol.json') and inv['build_terminal_before_launch']
assert dt(S['at'])<=dt(review['at'])<dt(A['at'])<dt(be['at'])<dt(inv['at'])
raw={};marks=[];ref=None;refchecks=None;chron=[];counts={};env=None
for identity in Q['order']:
 d=R/f'runs/{identity}';r=rd(d/'report.json');pin(d/'stdout.log',r['stdout_sha256']);instrumented=identity.startswith('D042P');m=D if instrumented else B
 assert r['status']=='measured' and r['returncode']==0 and r['test_pass_count']==1 and r['kind']=='diagnostic'
 assert r['binary_sha256']==m['binary_sha256'] and r['binary_build_manifest']['data']==m and r['binary_build_manifest']['binary_hash_verified'];pin(r['binary_build_manifest']['path'],r['binary_build_manifest']['sha256'])
 assert r['provenance']['source_sha256']==D['source_sha256']
 assert r['command'][1:]==['postflop_complete_cycle','--nocapture','--test-threads=1','--ignored']
 expected={'RAYON_NUM_THREADS':'16','POSTFLOP_AUTORESEARCH_FIXTURE':None,'POSTFLOP_AUTORESEARCH_STORAGE':'compressed','POSTFLOP_AUTORESEARCH_PROFILE':'0'}
 assert all(r['environment'][k]==v for k,v in expected.items())
 if env is None:env=r['environment']
 assert r['environment']==env
 si=rd(E/f'{identity}.invocation.json');se=rd(E/f'{identity}.exit.json');assert se['returncode']==0 and se['error'] is None and se['cleanup'] is None
 assert dt(si['at'])<=dt(r['started_at'])<=dt(r['finished_at'])<=dt(se['at'])
 txt=(d/'stdout.log').read_text();assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',txt)==[('1','0','0','0','0')]
 st=[];rs=[];pr=[];fixture=stage=None
 for line in txt.splitlines():
  if 'AUTORESEARCH_STAGE ' in line:
   v=json.loads(line.split('AUTORESEARCH_STAGE ',1)[1]);st.append(v);stage=v['stage']
   if stage=='fixture_start':fixture=v['fixture_id']
  if 'AUTORESEARCH_RESULT ' in line:rs.append(json.loads(line.split('AUTORESEARCH_RESULT ',1)[1]))
  if 'ZERO_UPLOAD_PROFILE ' in line:
   assert stage=='build_complete';v=json.loads(line.split('ZERO_UPLOAD_PROFILE ',1)[1]);pr.append({'run_id':identity,'fixture_id':fixture,**v})
 assert rs==r['results'] and st==[v['data'] for v in r['stages']]
 assert [v['fixture_id'] for v in rs]==Q['expected_fixtures'] and [v['iteration'] for v in rs]==[200,200,60] and all(v['target_met'] for v in rs)
 assert st[0]['stage']=='suite_start' and st[0]['primary_suite'] and not st[0]['smoke_only'] and st[-1]['stage']=='suite_complete' and st[-1]['fixtures_completed']==3
 checks=[strip(v) for v in st if v['stage']=='convergence_check'];assert len(checks)==23
 for v in rs:assert [x['iteration'] for x in checks if x['fixture_id']==v['fixture_id']]==list(range(20,v['iteration']+1,20))
 exact=[strip(v) for v in rs]
 if ref is None:ref,refchecks=exact,checks
 assert exact==ref and checks==refchecks
 assert len(pr)==(12 if instrumented else 0)
 for result in rs:
  ps=[v for v in pr if v['fixture_id']==result['fixture_id']]
  if not instrumented:continue
  assert [[v['player'],v['which']] for v in ps]==Q['profile_order_per_fixture']
  for v in ps:
   assert v['schema_version']==1 and v['diagnostic_only'] and v['zero'] and v['zero_path_executed'] and v['extra_cuda_synchronizations']==0 and v['predicate_calls']==1
   assert set(v['stage_us'])=={'predicate','alloc_zeros_host_call','existing_stream_wait'} and all(math.isfinite(x) and x>=0 for x in v['stage_us'].values())
   kind='regrets' if v['which']==0 else 'strategy_sums';a=next(a for a in result['state_fingerprint']['arenas'] if a['player']==v['player'] and a['arena']==kind)
   assert v['variant']==a['kind']==('i16' if v['which']==0 else 'u16') and v['q_words']==a['entries'] and v['scale_words']==a['scale_entries']
   assert v['q_bytes']==2*v['q_words'] and v['scale_bytes']==4*v['scale_words'] and v['q_bytes']+v['scale_bytes']==a['bytes'] and 0<v['device_elements']<=v['q_words'] and v['device_bytes']==4*v['device_elements']
   key=(v['fixture_id'],v['player'],v['which']);value={k:v[k] for k in ['variant','q_words','scale_words','device_elements']}
   if key in counts:assert value==counts[key]
   counts[key]=value
 marks.extend(pr);raw[identity]={'report':r,'results':rs,'profiles':pr};chron.append({'id':identity,'start':r['started_at'],'finish':r['finished_at']})
for x,y in zip(chron,chron[1:]):assert dt(x['finish'])<dt(y['start'])
assert dt(inv['at'])<=dt(chron[0]['start']) and dt(chron[-1]['finish'])<=dt(done['at'])
assert len(marks)==36 and marks==C['raw_profiles'] and C['all_complete_states_exact']==18 and C['convergence_checks_exact']==138
Bids=[p['baseline'] for p in Q['pairs']];Pids=[p['candidate'] for p in Q['pairs']];bs=ps=upper=0.0;table=[]
for i,f in enumerate(Q['expected_fixtures']):
 b=[raw[x]['results'][i]['full_cycle_ms'] for x in Bids];p=[raw[x]['results'][i]['full_cycle_ms'] for x in Pids];bm=statistics.median(b);pm=statistics.median(p);bs+=bm;ps+=pm;decl=C['fixtures'][i]
 assert decl['fixture_id']==f and decl['ordinary_full_cycles_ms']==b and decl['instrumented_full_cycles_ms']==p;close(decl['ordinary_median_ms'],bm);close(decl['instrumented_median_ms'],pm);close(decl['median_change_pct'],100*(pm/bm-1))
 for x,y,z in zip(b,p,decl['paired_change_pct']):close(z,100*(y/x-1))
 parts={}
 for variant in ['i16','u16']:
  for stage in ['predicate','alloc_zeros_host_call','existing_stream_wait']:
   values=[sum(v['stage_us'][stage] for v in raw[x]['profiles'] if v['fixture_id']==f and v['variant']==variant)/1000 for x in Pids];median=statistics.median(values);c=next(x for x in decl['components'] if x['variant']==variant and x['stage']==stage)
   assert c['all_profiled_ms']==values and c['range_ms']==[min(values),max(values)];close(c['median_ms'],median);parts[variant+'_'+stage]=median
   if variant=='u16' and stage=='predicate':upper+=median
 table.append({'fixture':f,'ordinary_ms':bm,'instrumented_ms':pm,'paired_change_pct':decl['paired_change_pct'],'components_median_ms':parts})
change=100*(ps/bs-1);useful=abs(change)<=10
for k,v in [('ordinary_sum_fixture_medians_ms',bs),('instrumented_sum_fixture_medians_ms',ps),('observed_outer_change_pct',change),('U16_predicate_upper_sum_fixture_medians_ms',upper),('U16_predicate_upper_fraction_of_ordinary_pct',100*upper/bs)]:close(C[k],v)
assert C['diagnostic_usefulness_guard_pass']==useful and C['status']==('pass' if useful else 'inconclusive') and C['upper_bound_exceeds_2pct']==(upper>.02*bs)
assert not C['candidate_accepted'] and not C['possible_2pct_headroom_established'] and not Q['performance_acceptance'] and not Q['outcome_triggered_extensions'] and Q['exclusions']==[]
current={k:sha(W/k) for k in D['source_sha256']};assert current==D['source_sha256']
result={'id':'D042-independent-review','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'verdict':'PASS_SCOPED_DIAGNOSTIC' if useful else 'EXACT_BUT_USEFULNESS_INCONCLUSIVE','full_non_timing_records_exact':18,'convergence_checks_exact':138,'profile_markers_verified':36,'ordinary_profile_markers':0,'all162_current_source_entries_match_build':True,'arena_candidate_sha256':current['crates/solver/src/gpu/arena.rs'],'chronology':chron,'ordinary_sum_fixture_medians_ms':bs,'instrumented_sum_fixture_medians_ms':ps,'outer_change_pct':change,'absolute10pct_guard_pass':useful,'U16_predicate_sum_fixture_medians_ms':upper,'fraction_ordinary_pct':100*upper/bs,'upper_bound_exceeds2pct':upper>.02*bs,'fixtures':table,'accepted':False,'interpretation':'Whole U16 predicate spans upper-bound only the measured direct U16 q scan, including scales and snapshot checks. They do not bound global cache effects or hypothetical complete-cycle savings. Passing outer10% guard does not remove component bias. No optimization accepted.','review_actions':'File reads and additive audit outputs only; no native, build, GPU or checkout mutation','input_sha256':inputs}
with (O/'validation.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({k:result[k] for k in ['verdict','outer_change_pct','U16_predicate_sum_fixture_medians_ms','fraction_ordinary_pct','upper_bound_exceeds2pct']},indent=2));print('validation_sha256',sha(O/'validation.json'))
