"""File-only E037 build/runtime custody audit; never execute candidate code."""
from pathlib import Path
import hashlib,json,re,subprocess,datetime
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016');O=Path(__file__).parent
terminal=json.loads((O/'terminal-inputs.json').read_text(encoding='utf-8'))
assert terminal['root_all_stages_terminal'] is True and terminal['cleanup_sha256']
pins={};checks=[]
def check(ok,label):
 if not ok:raise AssertionError(label)
 checks.append(label)
def sha(p):
 p=Path(p);h=hashlib.sha256(p.read_bytes()).hexdigest();pins[str(p)]=h;return h
def J(rel):
 p=R/rel;sha(p);return json.loads(p.read_text(encoding='utf-8'))
def pinmap(m,base=R):
 for p,h in m.items():check(sha(Path(p) if Path(p).is_absolute() else base/p)==h,'hash:'+str(p))
def stamp(v):return datetime.datetime.fromisoformat(v.replace('Z','+00:00'))
assert not (O/'source-custody.json').exists() and not (O/'manifest.json').exists()
source=J('runs/E037-design/manifest.json');plan=J('runs/E037-primary-plan/scripts-manifest.json')
check(sha(R/'runs/E037-design/manifest.json')=='70569ef1572507bf53830b14fb2774faf07870f4f322007a01df488afd3d0766','frozen source')
check(sha(R/'runs/E037-primary-plan/scripts-manifest.json')=='6f00150b84498fc9c9572b07b546f6e01c110d618b22ab9973749b42d53f8540','frozen scripts')
pinmap(source['artifact_sha256'],R/'runs/E037-design');pinmap(source['reference_sha256']);pinmap(plan['script_sha256'],R/'runs/E037-primary-plan');pinmap(plan['reference_sha256'])
protocol=J('runs/E037-primary-plan/protocol.json');auth=J('runs/E037-primary-plan/authorization.json');act=J('runs/E037-source/activation.json')
authhash=sha(R/'runs/E037-primary-plan/authorization.json');check(authhash=='03b36389ca3864e8bfc550c0dcceb724a1b486cf46a9950dc3293a6beaf219dc','root exact authorization')
pinmap(auth['evidence_sha256'])
for v in auth['prerequisites'].values():check(sha(v['path'])==v['sha256'],'root prerequisite')
base=J('binaries/E020-postflop_autoresearch.manifest.json')['source_sha256'];expected=base|source['candidate_owned_sha256']
check(len(base)==len(expected)==162 and sum(base[k]!=expected[k] for k in base)==2,'two changed /162 total')
check(sha(R/'runs/E037-source/activation.json')=='40fbc8e5a250dc4d2c0f00cb1f9563e5ac5e34e882a1d3060cd212d63aba9490','root exact activation')
check(act['source_before']['source_sha256']==base and act['source_after']['source_sha256']==expected and act['authorization_sha256']==authhash,'activation exact before/after')
for k,v in auth['candidate_sources'].items():check(sha(v['path'])==expected[k]==v['sha256'],'authorized candidate '+k)
feature=J('runs/E037-compile-check/complete.json');unitmanifest=J('binaries/E037-solver.manifest.json');benchmanifest=J('binaries/E037-postflop_autoresearch.manifest.json')
check(feature['status']=='COMPILE_ONLY_CHECKS_PASSED' and feature['native_executions']==0 and len(feature['commands'])==1,'single compile-only feature command')
check(feature['target_dir']!=unitmanifest['target_dir'],'separate feature/GPU targets')
old=(R/'runs/E037-design/base/kernels.cu').read_bytes();candidate=(R/'runs/E037-design/candidate/kernels.cu').read_bytes()
for folder in ['E037-compile-check','E037-build']:
 env=J('runs/'+folder+'/build-environment.json');check(env['target_previously_absent'] and env['compiler_override_absence']=={},folder+' fresh and no overrides')
 check(J('runs/'+folder+'/source-before.json')['source_sha256']==expected,folder+' source custody')
 for name in ['kernels.cu','mod.rs']:check(sha(R/'runs'/folder/('candidate-'+name))==source['candidate_owned_sha256']['crates/solver/src/gpu/'+name],folder+' copy '+name)
 check(sha(R/'runs'/folder/'candidate.patch')==source['artifact_sha256']['candidate.patch'],folder+' exact patch')
for data in [feature,unitmanifest,benchmanifest]:check(data['source_sha256']==expected,'full build source map')
pinmap(feature['evidence_sha256']);pinmap(feature['artifact_sha256'])
feature_art=feature['artifacts'][0];a=feature_art['cargo_artifact']
check(a['features']==['gpu','preflop-research'] and a['fresh'] is False and a['profile']['test'],'feature artifact flags')
check(sha(feature_art['path'])==feature_art['sha256']==sha(a['executable']),'frozen feature binary')
data=Path(feature_art['path']).read_bytes();check(candidate in data and old not in data,'feature expected CUDA presence/old full absence')
check(feature['protocol_sha256']==sha(R/'runs/E037-primary-plan/protocol.json') and feature['authorization_sha256']==authhash,'feature exact prerequisites')
for name,m in [('solver',unitmanifest),('postflop_autoresearch',benchmanifest)]:
 p=R/'binaries'/('E037-'+name+'.exe');check(sha(p)==m['binary_sha256']==sha(m['cargo_artifact']['executable']),'GPU frozen '+name)
 data=p.read_bytes();check(candidate in data and old not in data,'GPU complete CUDA provenance '+name)
 for artifact in [m['cargo_artifact'],m['solver_artifact']]:
  check(artifact['features']==['gpu'] and artifact['fresh'] is False,'GPU feature/fresh '+name)
  check(all(Path(x).is_relative_to(Path(m['target_dir'])) for x in artifact['filenames']),'GPU contained paths '+name)
  check(Path(artifact['manifest_path']).resolve()==(REPO/'crates/solver/Cargo.toml').resolve(),'GPU Cargo manifest '+name)
 check(m['primary_protocol_sha256']==sha(R/'runs/E037-primary-plan/protocol.json') and m['compile_check_sha256']==sha(R/'runs/E037-compile-check/complete.json'),'GPU preceding compile pin '+name)
 check(m['probe_authorization_sha256']==authhash,'GPU authorization '+name)
 for hkey,pkey in [('build_log_sha256','build_log'),('build_stderr_sha256','build_stderr_log')]:check(sha(m[pkey])==m[hkey],'GPU log '+name)
for folder,label in [('E037-compile-check','lib-tests'),('E037-build','build')]:
 ep='lib-tests.exit.json' if label=='lib-tests' else 'exit.json';ex=J('runs/'+folder+'/'+ep)
 check(ex['returncode']==0 and ex['error'] is None and '--no-run' in ex['command'] and '--locked' in ex['command'] and '--offline' in ex['command'],folder+' terminal command')
 rows=[json.loads(x) for x in (R/'runs'/folder/(label+'.jsonl')).read_text(encoding='utf-8').splitlines() if x.strip()]
 check(rows[-1]=={'reason':'build-finished','success':True},folder+' final Cargo success')
 check(not [x for x in rows if x.get('reason')=='compiler-message' and x.get('message',{}).get('level')=='error'],folder+' no compiler errors')
 for item in rows:
  if item.get('reason')=='compiler-artifact':check(all(Path(x).resolve().is_relative_to(Path(feature['target_dir'] if label=='lib-tests' else unitmanifest['target_dir']).resolve()) for x in item.get('filenames',[])+([item['executable']] if item.get('executable') else [])),folder+' all artifact containment')
inv=J('runs/E037-primary-execution/invocation.json');done=J('runs/E037-primary-execution/complete.json');clean=J('runs/E037-cleanup/report.json')
check(inv['order']==done['order']==protocol['order']==['V037-unit','B116','E037R1','E037R2','B117','B118','E037R3'],'fixed complete order')
actual=sorted(x.name for x in (R/'runs/E037-primary-execution').glob('*.invocation.json'))
check(actual==sorted(x+'.invocation.json' for x in protocol['order']),'only fixed seven wrappers')
for identity in protocol['order']:
 record=J('runs/'+identity+'/report.json');check(record['provenance']['source_sha256']==expected,'runtime current source '+identity)
 check(record['status']=='measured' and record['returncode']==0,'native terminal '+identity)
 ex=J('runs/E037-primary-execution/'+identity+'.exit.json');check(ex['returncode']==0 and ex['error'] is None,'wrapper terminal '+identity)
 for suffix in ['invocation.json','stdout.log','stderr.log']:sha(R/'runs/E037-primary-execution'/(identity+'.'+suffix))
 text=(R/'runs'/identity/'stdout.log').read_text(encoding='utf-8');sha(R/'runs'/identity/'stdout.log')
 check(not re.search(r'panicked at|test result: FAILED|CUDA_ERROR_|stack backtrace:',text),'no native fatal markers '+identity)
unit=J('runs/V037-unit/report.json');comparison=J('comparisons/E037-three-pair-comparison/report.json')
policy=J('runs/E037-policy-1pct/policy.json');policyseal=J('runs/E037-policy-1pct/scripts-manifest.json')
check(sha(R/'runs/E037-policy-1pct/scripts-manifest.json')=='bf84a6f7f685d42ee3fbcf7aed5737a073b8acbf9401544ddaa03c9cc1b4d37a','final policy seal')
check(sha(R/'runs/E037-policy-1pct/policy.json')=='f2eaef2759f628db85a414e5496f7dec89be1e398f7d00d8d068d1db74be55d4','final effective policy')
pinmap(policyseal['script_sha256'],R/'runs/E037-policy-1pct');pinmap(policyseal['reference_sha256'])
policyauth=J('runs/E037-policy-1pct/authorization.json');policy_auth_hash=sha(R/'runs/E037-policy-1pct/authorization.json')
check(policy_auth_hash==terminal['policy_authorization_sha256'],'root separate policy authorization')
pinmap(policyauth['evidence_sha256'])
receipt=J('runs/E037-policy-execution/pre-primary.json');wrapperexit=J('runs/E037-policy-execution/exit.json')
check(receipt['policy_authorization_sha256']==policy_auth_hash and receipt['original_authorization_sha256']==authhash,'dual authorization provenance')
check(receipt['policy_sha256']==sha(R/'runs/E037-policy-1pct/policy.json') and receipt['policy_manifest_sha256']==sha(R/'runs/E037-policy-1pct/scripts-manifest.json'),'receipt exact policy')
check(receipt['all_seven_run_directories_absent'] and receipt['order']==protocol['order'],'policy receipt before fixed cohort')
check(wrapperexit['returncode']==0 and wrapperexit['error'] is None,'policy wrapper terminal success')
check(stamp(policy['at'])<=stamp(policyauth['at'])<=stamp(receipt['at']),'policy frozen/authorized before receipt')
for identity in protocol['order']:
 run_start=stamp(J('runs/'+identity+'/report.json')['started_at'])
 check(run_start.microsecond==0 and stamp(receipt['at']).replace(microsecond=0)<=run_start,'policy/run timestamp intervals compatible '+identity)
assessment_inv=J('runs/E037-assessment/invocation.json')
check(assessment_inv['script_sha256']==sha(R/'runs/E037-assessment-time-repair/assess.py'),'effective assessor executed')
check(str(R/'runs/E037-assessment-time-repair/compare_policy.py') in assessment_inv['command'],'isolated effective compare command')
check(comparison['effective_policy']==assessment_inv['effective_policy'],'published effective policy custody')
check(comparison['effective_policy']['policy_authorization_sha256']==policy_auth_hash and comparison['effective_policy']['pre_primary_receipt']['sha256']==sha(R/'runs/E037-policy-execution/pre-primary.json'),'reported effective receipt')
check(comparison['performance']['required_gain_pct']==1.0 and comparison['performance']['fixture_regression_guard']['threshold_pct']==0.0,'effective1percent/no-repeatable-slowdown policy')
check(comparison['effective_policy']['primary_pass_is_preliminary'] and not comparison['effective_policy']['candidate_accepted'],'no automatic adoption')
repair=J('runs/E037-assessment-time-repair/scripts-manifest.json')
check(sha(R/'runs/E037-assessment-time-repair/scripts-manifest.json')=='505079cf57dfa3b5b3428d8acbfa2963f7f2b50a116fd9d7f64f5e0671597806','assessment repair exact seal')
pinmap(repair['script_sha256'],R/'runs/E037-assessment-time-repair');pinmap(repair['reference_sha256'])
check(sha(R/'runs/E037-assessment-preparation-error/error.json')=='b8ab72850519b9810cf0165cbcea499aed94c1cb8604868de6e03a1c88e959fe','initial assessor timestamp failure preserved')
check(comparison['effective_policy']['assessment_timestamp_repair']['manifest_sha256']==sha(R/'runs/E037-assessment-time-repair/scripts-manifest.json'),'published repair provenance')
check(sha(R/'comparisons/E037-three-pair-comparison/report.json')==terminal['comparison_sha256'],'root comparison pin')
check(sha(R/'runs/E037-cleanup/report.json')==terminal['cleanup_sha256'],'root cleanup pin')
if 'pre_cleanup_error_sha256' in clean:check(sha(R/'runs/E037-cleanup-preparation/error.json')==clean['pre_cleanup_error_sha256'],'preserved root pre-cleanup read error')
check(clean['source_before']['source_sha256']==expected and clean['source_after']['source_sha256']==base and clean['all162_accepted_entries_exact'],'cleanup exact before/after')
for name,v in clean['preserved_candidate_sources'].items():check(sha(v['path'])==v['sha256']==expected[name],'archived candidate '+name)
pinmap(base,REPO)
for n,v in protocol['preexisting_target_artifacts'].items():check(sha(REPO/n)==v['sha256'] and (REPO/n).stat().st_size==v['bytes'],'existing PTX unchanged')
live=Path(r'X:\Dev\GTOpen\target\desktop-runtime\release\gto-server.exe');check(sha(live)==clean['live_exe_sha256']=='b7b808b8baff6b3a92c4f3cc8c54ee74ee2c0bb079a8ca68be4da9703f6b84bd','exact live desktop binary unchanged')
main_head=subprocess.check_output(['git','-C',r'X:\Dev\GTOpen','rev-parse','HEAD'],text=True).strip();check(main_head==clean['main_head']=='ae823c8bd6d723c75e096da139fd638d7dd397eb','main HEAD unchanged')
check(stamp(auth['at'])<=stamp(act['at'])<stamp(feature['at'])<stamp(unitmanifest['built_at'])<stamp(inv['at'])<=stamp(unit['started_at'])<stamp(unit['finished_at'])<=stamp(done['at'])<=stamp(comparison['created_at'])<=stamp(clean['at']),'full chronological custody')
check(clean['assessment_sha256']==sha(R/'comparisons/E037-three-pair-comparison/report.json') and clean['activation_sha256']==sha(R/'runs/E037-source/activation.json'),'cleanup outcome pins')
check(clean['compiler_and_native_terminal'] and clean['no_extra_samples'] and clean['broader_qualification_run'] is False,'root closed scope')
for rel in ['runs/E037-qualification-plan','runs/E037-wide-turn-holdout-implementation','comparisons/E037-qualification','comparisons/E037-cumulative-comparison']:check(not (R/rel).exists(),'no conditional output '+rel)
check(not (R/'gpu-run.lock').exists(),'GPU lock released')
check(comparison['decision']==terminal['expected_decision'] and not comparison['accepted'] and not comparison['deployed'],'root terminal decision preserved without acceptance')
validation=J('comparisons/E037-independent-review/validation.json');check(validation['numerical_audit_pass'],'independent numerical completion')
report={'id':'E037','verdict':'PASS_SOURCE_BUILD_RUNTIME_CUSTODY','source_build_custody_pass':True,'accepted_sources_restored':True,'candidate_accepted':False,'deployment_changed':False,
'facts':['Exactly kernels.cu and the focused-test mod.rs differ within the162-entry source map; frozen source, authorization, activation, both build snapshots, archived copies and seven runtime source maps agree.','One preflop-research lib-test compile-only command and a separate fresh GPU-only unit/evaluator build completed before native tests. All three frozen candidate binaries match their Cargo artifacts, contain complete candidate CUDA and omit the full accepted CUDA string.','Only V037-unit,B116,E037R1,E037R2,B117,B118,E037R3 wrapper invocations are present, all terminal0 in order; raw outputs and fixed gates are independently validated in validation.json.','Both candidate files remain archived; all162 acceptedE020 source hashes are restored, both generated PTX files/mainHEAD/exact live desktop-runtime binary unchanged, GPU lock absent. No conditional broader/holdout/cumulative outputs were executed within this fixed primary.'],
'preparation_scope':'Inherited E036 file-only audit, corrected only after reading actual terminal and cleanup schema; no result asserted before terminal.',
'checks_passed':len(checks),'input_sha256':pins,'limits':['File-backed custody audit only; no reviewer compiler/native/GPU work.','Focused34-pair equality and all21-input immutability rely on the source-pinned native unit assertions and success marker; full direct-test output arrays were not retained as a replayable dump.','The independently recomputed primary outcome is reported in validation.json; no performance acceptance, causality or statistical-significance claim.']}
with (O/'source-custody.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps({'custody_sha256':sha(O/'source-custody.json'),'checks':len(checks),'pins':len(pins)}))
