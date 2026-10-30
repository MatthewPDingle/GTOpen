"""Independent file-only custody audit. Does not import or execute runtime helpers."""
from pathlib import Path
import hashlib,json,re,csv,datetime,subprocess,traceback
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016');O=Path(__file__).parent;P=R/'runs/small-gain-confirmation-plan';B=R/'runs/small-gain-confirmation-build';E=R/'runs/small-gain-confirmation-execution'
pins={};checks=[]
def check(ok,label):
 if not ok:raise AssertionError(label)
 checks.append(label)
def sha(p):
 p=Path(p);k=str(p)
 if k not in pins:pins[k]=hashlib.sha256(p.read_bytes()).hexdigest()
 return pins[k]
def J(p):sha(p);return json.loads(Path(p).read_text(encoding='utf-8'))
def pin(p,h):check(sha(p)==h,'pin '+str(p))
def pinmap(m,root=R):
 for n,h in m.items():pin(Path(n) if Path(n).is_absolute() else root/n,h)
def t(x):return datetime.datetime.fromisoformat(x.replace('Z','+00:00'))
def raw(identity):
 report=J(R/'runs'/identity/'report.json');f=R/'runs'/identity/'stdout.log';pin(f,report['stdout_sha256']);txt=f.read_text(encoding='utf-8')
 check(not re.search(r'panicked at|test result: FAILED|CUDA_ERROR_|stack backtrace:',txt),'no fatal markers '+identity)
 results=[json.loads(x.split('AUTORESEARCH_RESULT ',1)[1]) for x in txt.splitlines() if 'AUTORESEARCH_RESULT ' in x]
 check(results==report['results'],'raw results equal report '+identity)
 stages=[json.loads(x.split('AUTORESEARCH_STAGE ',1)[1]) for x in txt.splitlines() if 'AUTORESEARCH_STAGE ' in x]
 convergence=[{k:x[k] for k in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']} for x in stages if x.get('stage')=='convergence_check']
 excluded={'build_ms','init_ms','solve_ms','readback_ms','full_cycle_ms','fingerprint_ms_excluded'}
 return report,txt,([{k:v for k,v in x.items() if k not in excluded} for x in results],convergence)
def audit():
 terminal=J(O/'custody-terminal-inputs.json');check(terminal['root_all_stages_terminal'],'root terminal trigger')
 auth=J(P/'authorization.json');pin(P/'authorization.json',terminal['authorization_sha256']);AUTH=sha(P/'authorization.json')
 seal=J(P/'scripts-manifest.json');pin(P/'scripts-manifest.json','34e9a0372539975170a01d3d137f483fb9656839d0faeb6dd3f6a3a67044131f')
 pinmap(seal['script_sha256'],P);pinmap(seal['reference_sha256']);pr=J(P/'protocol.json');s=J(P/'schedule.json')
 check(auth['execute_fixed_package'] and auth['scripts_manifest_sha256']==sha(P/'scripts-manifest.json') and auth['protocol_sha256']==sha(P/'protocol.json'),'single exact root authorization')
 pinmap(auth['evidence_sha256']);pin(auth['script_review']['path'],auth['script_review']['sha256']);check(J(auth['script_review']['path'])['independent_script_review_pass'],'independent script pass')
 sm=J(pr['source_package']['path']);source=Path(pr['source_package']['path']).parent;pinmap(sm['artifact_sha256'],source)
 base=J(pr['accepted_manifest']['path'])['source_sha256'];check(len(base)==162,'accepted map162');expected={c:base|pr['arms'][c]['candidate_owned_sha256'] for c in pr['build_order']}
 bc=J(B/'complete.json');pin(B/'complete.json',terminal['build_complete_sha256']);pinmap(bc['evidence_sha256'])
 check(bc['build_order']==['E020','E007','E008','E032','E036'] and bc['all_compilers_terminal'] and bc['native_executions']==0 and bc['accepted162_restored'],'five builds only and restored')
 check(bc['authorization_sha256']==AUTH and bc['protocol_sha256']==sha(P/'protocol.json'),'build root pins')
 bt=J(R/'runs/small-gain-confirmation-root/build-terminal.json');pin(R/'runs/small-gain-confirmation-root/build-terminal.json',terminal['build_terminal_sha256'])
 check(bt['observed_exit_code']==0 and bt['native_executions_so_far']==0 and bt['build_complete_sha256']==sha(B/'complete.json'),'root build terminal')
 binaries={};prev=t(auth['at']);compiler_versions=None
 for c in pr['build_order']:
  a=pr['arms'][c];out=B/c;before=J(out/'before.json');active=J(out/'activation.json');restore=J(out/'restoration.json')
  check(before['source_sha256']==base and before['authorization_sha256']==AUTH and active['source_sha256']==expected[c],'before/activation '+c)
  check(prev<=t(before['at'])<=t(active['at']),'activation chronology '+c);prev=t(active['at'])
  check(restore['restored_sources']==a['owned_sources'] and restore['accepted162_exact'] and restore['main_live_ptx_unchanged'] and restore['error'] is None,'restoration '+c)
  for n in a['owned_sources']:pin(out/('candidate-'+Path(n).name),expected[c][n]);pin(source/c/'candidate'/Path(n).name,expected[c][n]);pin(source/c/'base'/Path(n).name,base[n])
  if a['owned_sources']:check(sha(out/'candidate.patch')==sha(source/c/'candidate.patch'),'preserved patch '+c)
  cuda=(source/c/'candidate/kernels.cu').read_bytes() if 'crates/solver/src/gpu/kernels.cu' in a['owned_sources'] else (source/'E007/base/kernels.cu').read_bytes()
  accepted_cuda=(source/'E007/base/kernels.cu').read_bytes()
  for mode in ['feature','primary']:
   env=J(out/(mode+'.environment.json'));ex=J(out/(mode+'.exit.json'));inv=J(out/(mode+'.invocation.json'));done=J(out/(mode+'.complete.json'));target=R/f'build-small-gain-{c.lower()}-{mode}'
   check(env['previously_absent'] and env['overrides']=={} and Path(env['target'])==target,'fresh isolated target '+c+mode)
   versions=[env['rustc'],env['cargo']]
   if compiler_versions is None:compiler_versions=versions
   check(versions==compiler_versions and all(x['returncode']==0 for x in versions),'same successful compiler versions '+c+mode)
   command=['cargo','test','--release','--locked','--offline','-p','solver','--features','preflop-research' if mode=='feature' else 'gpu','--lib']+([] if mode=='feature' else ['--test','postflop_autoresearch'])+['--no-run','--message-format=json']
   check(ex['command']==inv['command']==done['command']==command and ex['returncode']==0 and ex['error'] is None and ex['cleanup'] is None,'exact compile command terminal '+c+mode)
   check(prev<=t(inv['at'])<=t(ex['started_at'])<=t(ex['finished_at'])<=t(done['at']),'compiler serialization '+c+mode);prev=t(done['at'])
   check(done['source_sha256']==expected[c] and done['returncode']==0 and done['native_executions']==0 and done['authorization_sha256']==AUTH,'compile source custody '+c+mode)
   check(done['protocol_sha256']==sha(P/'protocol.json') and done['build_script_sha256']==sha(P/'build.py'),'compile script pins '+c+mode)
   pin(out/(mode+'.stdout.log'),done['stdout_sha256']);pin(out/(mode+'.stderr.log'),done['stderr_sha256']);pinmap(done['artifact_sha256']);pinmap(done['dependency_sha256'])
   rows=[json.loads(x) for x in (out/(mode+'.stdout.log')).read_text(encoding='utf-8').splitlines() if x.strip()]
   check(rows[-1]=={'reason':'build-finished','success':True},'Cargo success '+c+mode)
   check(not any(x.get('reason')=='compiler-message' and x.get('message',{}).get('level')=='error' for x in rows),'no compiler errors '+c+mode)
   arts=[x for x in rows if x.get('reason')=='compiler-artifact']
   for x in arts:check(all(Path(n).resolve().is_relative_to(target.resolve()) for n in x.get('filenames',[])+([x['executable']] if x.get('executable') else [])),'Cargo contained artifacts '+c+mode)
   tests=[x for x in arts if x.get('profile',{}).get('test') and x.get('executable') and x['target']['name'] in ['solver','postflop_autoresearch']]
   check(sorted(x['target']['name'] for x in tests)==(['solver'] if mode=='feature' else ['postflop_autoresearch','solver']),'compiled test inventory '+c+mode)
   for x in tests:
    check(x['fresh'] is False and x['features']==(['gpu','preflop-research'] if mode=='feature' else ['gpu']),'feature flags/fresh '+c+mode)
    check(Path(x['manifest_path']).resolve()==(REPO/'crates/solver/Cargo.toml').resolve(),'Cargo source manifest '+c+mode)
    data=Path(x['executable']).read_bytes();check(cuda in data,'full candidate CUDA in compiler output '+c+mode)
    check(c in ['E020','E032'] or accepted_cuda not in data,'CUDA accepted absence/preserved choice '+c+mode)
    if mode=='primary':
     name=x['target']['name'];binary=R/'binaries'/f'SG-{c}-{name}.exe';mp=binary.with_suffix('.manifest.json');m=J(mp)
     check(sha(binary)==m['binary_sha256']==sha(x['executable']),'frozen exact binary '+c+name)
     check(m['cargo_artifact']==x and m['source_sha256']==expected[c] and m['authorization_sha256']==AUTH,'binary source identity '+c+name)
     check(m['primary_protocol_sha256']==sha(P/'protocol.json') and m['build_script_sha256']==sha(P/'build.py') and m['feature_complete_sha256']==sha(out/'feature.complete.json'),'binary build pins '+c+name)
     check(m['solver_artifact']['features']==['gpu'] and not m['solver_artifact']['fresh'] and m['solver_artifact'] in arts,'fresh solver linkage '+c+name)
     pinmap(m['dependency_artifact_sha256']);binaries[c,name]={'path':str(binary),'sha256':sha(binary),'manifest':str(mp),'manifest_sha256':sha(mp),'data':m}
  check(prev<=t(restore['at']),'restore after all compilers '+c);prev=t(restore['at'])
 check(prev<=t(bc['at'])<=t(bt['at']),'all build stages terminal before root observation')
 inv=J(E/'invocation.json');done=J(E/'complete.json');units=J(E/'units-complete.json');nt=J(R/'runs/small-gain-confirmation-root/native-terminal.json')
 pin(E/'complete.json',terminal['execution_complete_sha256']);pin(R/'runs/small-gain-confirmation-root/native-terminal.json',terminal['native_terminal_sha256'])
 check(inv['authorization_sha256']==AUTH and inv['protocol_sha256']==sha(P/'protocol.json') and inv['build_complete_sha256']==sha(B/'complete.json'),'runtime exact authorization/build')
 check(inv['schedule_sha256']==sha(P/'schedule.json') and inv['source_sha256']==base and inv['all_native_ids_previously_absent'] and inv['all_compilers_terminal_before_any_native'],'runtime current source and fixed fresh scope')
 check(inv['binary_pins']=={f'{c}/{n}':{k:v for k,v in m.items() if k!='data'} for (c,n),m in binaries.items()},'all runtime binary pins')
 check(done['unit_order']==units['unit_order']==s['unit_order'] and done['measurement_order']==s['measurement_order'],'exact fixed order')
 check(done['comparison_pairs']==64 and done['evaluator_processes']==128 and done['fixture_results']==384 and done['convergence_records']==2944 and done['all_samples_retained'],'fixed complete counts')
 check(done['authorization_sha256']==AUTH and done['schedule_sha256']==sha(P/'schedule.json') and done['units_complete_sha256']==sha(E/'units-complete.json'),'complete pins')
 check(units['all_passed'] and units['build_complete_sha256']==sha(B/'complete.json'),'unit gate completion');pinmap(units['evidence_sha256'])
 ids=s['unit_order']+s['measurement_order'];check(len(ids)==len(set(ids))==133,'133unique processes')
 check(sorted(p.name for p in E.glob('*.invocation.json'))==sorted(i+'.invocation.json' for i in ids),'only fixed133 wrapper invocations')
 check(sorted(p.name for p in (R/'runs').glob('SG-*') if p.is_dir())==sorted(ids),'only fixed family run directories')
 arm_by_id={pr['arms'][c]['unit_id']:c for c in pr['build_order']}
 for pair in s['pairs']:arm_by_id[pair['baseline']]='E020';arm_by_id[pair['candidate_run']]=pair['candidate']
 anchor=raw(pr['anchor'])[2];check(len(anchor[0])==3 and len(anchor[1])==23,'historical non-timing correctness anchor only')
 previous=t(inv['at']);check(t(bt['at'])<=previous,'root build observation before native');first_env=first_gpu=None
 for i in ids:
  ordinary=i in s['unit_order'];c=arm_by_id[i];kind='solver' if ordinary else 'postflop_autoresearch';b=binaries[c,kind]
  ex=J(E/(i+'.exit.json'));call=J(E/(i+'.invocation.json'))
  check(ex['command']==call['command'] and ex['returncode']==0 and ex['error'] is None and ex['cleanup'] is None,'successful native wrapper '+i)
  check(previous<=t(call['at'])<=t(ex['started_at'])<=t(ex['finished_at']),'serial native wrappers '+i);previous=t(ex['finished_at'])
  if i==s['measurement_order'][0]:check(t(units['at'])<=t(ex['started_at']),'all five units before any measurement')
  for suffix in ['stdout.log','stderr.log']:sha(E/(i+'.'+suffix))
  rr,txt,normalized=raw(i)
  check(rr['status']=='measured' and rr['returncode']==0 and not rr['accepted'],'native success pending acceptance '+i)
  check(rr['command']==[b['path']]+(['--nocapture','--test-threads=1'] if ordinary else ['postflop_complete_cycle','--nocapture','--test-threads=1','--ignored']),'exact native command '+i)
  check(rr['binary_sha256']==b['sha256'] and rr['binary_build_manifest']['sha256']==b['manifest_sha256'] and rr['binary_build_manifest']['data']==b['data'] and rr['binary_build_manifest']['binary_hash_verified'],'native binary/build manifest '+i)
  check(rr['provenance']['source_sha256']==base,'accepted checkout during native '+i)
  check(t(ex['started_at']).replace(microsecond=0)<=t(rr['started_at'])<=t(rr['finished_at'])<=t(ex['finished_at']),'whole-second native timestamp envelope '+i)
  en=rr['environment'];check(en['RAYON_NUM_THREADS']=='16' and en['POSTFLOP_AUTORESEARCH_FIXTURE'] is None and en['POSTFLOP_AUTORESEARCH_STORAGE']=='compressed' and en['POSTFLOP_AUTORESEARCH_PROFILE']=='0','registered environment '+i)
  gpu=rr['telemetry_before']['gpu'];check(gpu['returncode']==0,'retained GPU identity exists '+i);gid=[v[:4] for v in csv.reader(gpu['stdout'].splitlines(),skipinitialspace=True)]
  if first_env is None:first_env=en;first_gpu=gid
  check(en==first_env and gid==first_gpu,'consistent environment/GPU/driver '+i)
  if ordinary:
   ui=pr['arms'][c]['unit_inventory'];check(re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',txt)==[(str(ui['passed']),'0',str(ui['ignored']),'0','0')] and rr['test_pass_count']==ui['passed'],'exact unit inventory '+i)
   for name in pr['arms'][c]['focused_tests']:check(re.search(r'(?m)^test '+re.escape(name)+r' \.\.\. ',txt) is not None,'focused test '+name)
   marker=pr['arms'][c]['test_marker']
   if marker:check([json.loads(v.split(marker['prefix'],1)[1]) for v in txt.splitlines() if marker['prefix'] in v]==[marker['fields']],'exact E03634/68 marker')
  else:check(rr['test_pass_count']==1 and normalized==anchor,'raw non-timing/checkpoint anchor '+i)
 check(previous<=t(done['at'])<=t(nt['at']) and nt['observed_exit_code']==0 and nt['complete_sha256']==sha(E/'complete.json') and nt['units_complete_sha256']==sha(E/'units-complete.json'),'native terminal root custody')
 comparison=J(R/'comparisons/small-gain-confirmation/report.json');pin(R/'comparisons/small-gain-confirmation/report.json',terminal['comparison_sha256'])
 check(t(nt['at'])<=t(comparison['at']) and comparison['complete_sha256']==sha(E/'complete.json') and comparison['build_complete_sha256']==sha(B/'complete.json'),'assessment after root native terminal')
 check(comparison['authorization_sha256']==AUTH and comparison['protocol_sha256']==sha(P/'protocol.json') and comparison['schedule_sha256']==sha(P/'schedule.json') and comparison['effective_policy']==pr['policy'],'assessment exact registered policy')
 check(comparison['historical_timing_samples_used']==0 and comparison['excluded_samples']==[] and comparison['extension_runs']==0 and not comparison['candidate_accepted'],'no old pooling/extension/adoption')
 check(all(a['decision']=='rejected' and not a['candidate_accepted'] for a in comparison['arms'].values()),'root all rejected outcome preserved');pinmap(comparison['preserved_artifacts'])
 pinmap(base,REPO);main=J(P/'protected-main.json');mp=Path(main['root']);pinmap(main['source_sha256'],mp)
 check(subprocess.check_output(['git','-C',str(mp),'rev-parse','HEAD'],text=True).strip()==main['git_head'],'final main HEAD unchanged')
 for n in main['absent_research_paths']:check(not (mp/n).exists(),'main absent '+n)
 pin(main['live_path'],main['live_sha256'])
 for n,v in pr['preexisting_target_artifacts'].items():pin(REPO/n,v['sha256']);check((REPO/n).stat().st_size==v['bytes'],'PTX bytes '+n)
 check(not (R/'gpu-run.lock').exists(),'no GPU lock after completion')
 val=J(O/'numerical-validation.json');pin(O/'numerical-validation.json','46c3d9186db62a9d3f32b3131f777d5736b1afcc12172269ff9e6e9003c4ea87')
 report={'id':'small-gain-confirmation-custody-review','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'verdict':'PASS_SOURCE_BUILD_NATIVE_CUSTODY','source_build_custody_pass':True,'accepted_sources_restored':True,'candidate_accepted':False,'deployment_changed':False,'checks_passed':len(checks),'input_sha256':pins,'builds':{'arms':pr['build_order'],'feature_compile_only_commands':5,'separate_gpu_compile_only_commands':5,'all_restorations_exact':True,'compiled_binary_images_verified':15},'native':{'unit_processes':5,'evaluator_processes':128,'comparison_pairs':64,'recorded_wrapper_invocations':133,'all_terminal_zero':True,'all_units_before_timings':True,'raw_complete_non_timing_results_anchored':384,'convergence_records_anchored':2944},'facts':['Single frozen root authorization, exact final plan/source/schedule and reviewed policy bind the entire family.','Every fresh feature and GPU-only build has exact source copies, Cargo options/artifacts/dependencies, full CUDA inclusion, frozen binary identity and a successful per-arm accepted-source restoration before the next arm.','The fixed133 native commands have serial high-resolution wrapper intervals, exact binary/build/current-source provenance and raw log hashes. Recorded whole-second native timestamps are checked within compatible wrapper envelopes.','All162 accepted sources, protected main157 sources/HEAD and five absent research paths, exact live desktop-runtime binary and two preexisting PTX artifacts match at audit time.','All four outcomes are rejected; no sample extension, old timing pooling, combination or candidate adoption is present. Numerical outcomes are independently recomputed in numerical-validation.json.'],'preserved_failures':'No build/native/assessment or reviewer execution failure observed. Earlier plan preparation corrections remain pinned in the frozen package.','limits':['File-only review; no compiler, candidate script import, native or GPU execution by reviewer.','The ordinary E03634/68 direct test supplies source-pinned native assertions/marker, not replayable retained raw direct-test arrays.','Protected identities are checked; root-reported policy-document/dashboard wording changes outside those maps and off-tree E038 preparation are not claimed absent. No partial running outcomes were audited.','No significance, no-tradeoffs universal claim, broader qualification or adoption follows this screen.']}
 with (O/'custody-validation.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(report,f,indent=2);f.write('\n')
 print(json.dumps({'verdict':report['verdict'],'checks':len(checks),'custody_sha256':sha(O/'custody-validation.json'),'pins':len(pins)}))
if __name__=='__main__':
 try:audit()
 except BaseException as error:
  with (O/'custody-reviewer-failure.json').open('x',encoding='utf-8',newline='\n') as f:json.dump({'error':repr(error),'traceback':traceback.format_exc(),'scope':'Reviewer host evidence parsing only; no candidate/native execution.'},f,indent=2);f.write('\n')
  raise
