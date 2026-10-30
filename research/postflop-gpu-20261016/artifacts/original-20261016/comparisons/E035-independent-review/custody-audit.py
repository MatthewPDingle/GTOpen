"""File-only E035 build/runtime custody audit; never execute candidate code."""
from pathlib import Path
import hashlib,json,re,subprocess,datetime
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016');O=Path(__file__).parent
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
source=J('runs/E035-design/manifest.json');plan=J('runs/E035-primary-plan/scripts-manifest.json')
check(sha(R/'runs/E035-design/manifest.json')=='044151bbf7a9118b96d71ddf8d08d4ee2c36122d1a87ecd3ffa098591320d126','frozen source')
check(sha(R/'runs/E035-primary-plan/scripts-manifest.json')=='a4b09bda1d72111f9df3444737dd76c2a1ed51890a8d0adb256148ab7ec22793','frozen scripts')
pinmap(source['artifact_sha256'],R/'runs/E035-design');pinmap(source['reference_sha256']);pinmap(plan['script_sha256'],R/'runs/E035-primary-plan');pinmap(plan['reference_sha256'])
protocol=J('runs/E035-primary-plan/protocol.json');auth=J('runs/E035-primary-plan/authorization.json');act=J('runs/E035-source/activation.json')
authhash=sha(R/'runs/E035-primary-plan/authorization.json');check(authhash=='6625ce6b5f608de5f2662cc659f79614a220ed4de3e99773f98d9e5ddc2a4790','root exact authorization')
pinmap(auth['evidence_sha256'])
for v in auth['prerequisites'].values():check(sha(v['path'])==v['sha256'],'root prerequisite')
base=J('binaries/E020-postflop_autoresearch.manifest.json')['source_sha256'];expected=base|source['candidate_owned_sha256']
check(len(base)==len(expected)==162 and sum(base[k]!=expected[k] for k in base)==2,'two changed /162 total')
check(act['source_before']['source_sha256']==base and act['source_after']['source_sha256']==expected and act['authorization_sha256']==authhash,'activation exact before/after')
for k,v in auth['candidate_sources'].items():check(sha(v['path'])==expected[k]==v['sha256'],'authorized candidate '+k)
feature=J('runs/E035-compile-check/complete.json');unitmanifest=J('binaries/E035-solver.manifest.json');benchmanifest=J('binaries/E035-postflop_autoresearch.manifest.json')
check(feature['status']=='COMPILE_ONLY_CHECKS_PASSED' and feature['native_executions']==0 and len(feature['commands'])==1,'single compile-only feature command')
check(feature['target_dir']!=unitmanifest['target_dir'],'separate feature/GPU targets')
old=(R/'runs/E035-design/base/kernels.cu').read_bytes();candidate=(R/'runs/E035-design/candidate/kernels.cu').read_bytes()
for folder in ['E035-compile-check','E035-build']:
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
check(feature['protocol_sha256']==sha(R/'runs/E035-primary-plan/protocol.json') and feature['authorization_sha256']==authhash,'feature exact prerequisites')
for name,m in [('solver',unitmanifest),('postflop_autoresearch',benchmanifest)]:
 p=R/'binaries'/('E035-'+name+'.exe');check(sha(p)==m['binary_sha256']==sha(m['cargo_artifact']['executable']),'GPU frozen '+name)
 data=p.read_bytes();check(candidate in data and old not in data,'GPU complete CUDA provenance '+name)
 for artifact in [m['cargo_artifact'],m['solver_artifact']]:
  check(artifact['features']==['gpu'] and artifact['fresh'] is False,'GPU feature/fresh '+name)
  check(all(Path(x).is_relative_to(Path(m['target_dir'])) for x in artifact['filenames']),'GPU contained paths '+name)
  check(Path(artifact['manifest_path']).resolve()==(REPO/'crates/solver/Cargo.toml').resolve(),'GPU Cargo manifest '+name)
 check(m['primary_protocol_sha256']==sha(R/'runs/E035-primary-plan/protocol.json') and m['compile_check_sha256']==sha(R/'runs/E035-compile-check/complete.json'),'GPU preceding compile pin '+name)
 check(m['probe_authorization_sha256']==authhash,'GPU authorization '+name)
 for hkey,pkey in [('build_log_sha256','build_log'),('build_stderr_sha256','build_stderr_log')]:check(sha(m[pkey])==m[hkey],'GPU log '+name)
for folder,label in [('E035-compile-check','lib-tests'),('E035-build','build')]:
 ep='lib-tests.exit.json' if label=='lib-tests' else 'exit.json';ex=J('runs/'+folder+'/'+ep)
 check(ex['returncode']==0 and ex['error'] is None and '--no-run' in ex['command'] and '--locked' in ex['command'] and '--offline' in ex['command'],folder+' terminal command')
 rows=[json.loads(x) for x in (R/'runs'/folder/(label+'.jsonl')).read_text(encoding='utf-8').splitlines() if x.strip()]
 check(rows[-1]=={'reason':'build-finished','success':True},folder+' final Cargo success')
 check(not [x for x in rows if x.get('reason')=='compiler-message' and x.get('message',{}).get('level')=='error'],folder+' no compiler errors')
 for item in rows:
  if item.get('reason')=='compiler-artifact':check(all(Path(x).resolve().is_relative_to(Path(feature['target_dir'] if label=='lib-tests' else unitmanifest['target_dir']).resolve()) for x in item.get('filenames',[])+([item['executable']] if item.get('executable') else [])),folder+' all artifact containment')
inv=J('runs/E035-primary-execution/invocation.json');done=J('runs/E035-primary-execution/complete.json');clean=J('runs/E035-cleanup/report.json')
check(inv['order']==done['order']==protocol['order']==['V035-unit','B110','E035R1','E035R2','B111','B112','E035R3'],'fixed complete order')
actual=sorted(x.name for x in (R/'runs/E035-primary-execution').glob('*.invocation.json'))
check(actual==sorted(x+'.invocation.json' for x in protocol['order']),'only fixed seven wrappers')
for identity in protocol['order']:
 record=J('runs/'+identity+'/report.json');check(record['provenance']['source_sha256']==expected,'runtime current source '+identity)
 check(record['status']=='measured' and record['returncode']==0,'native terminal '+identity)
 ex=J('runs/E035-primary-execution/'+identity+'.exit.json');check(ex['returncode']==0 and ex['error'] is None,'wrapper terminal '+identity)
 for suffix in ['invocation.json','stdout.log','stderr.log']:sha(R/'runs/E035-primary-execution'/(identity+'.'+suffix))
 text=(R/'runs'/identity/'stdout.log').read_text(encoding='utf-8');sha(R/'runs'/identity/'stdout.log')
 check(not re.search(r'panicked at|test result: FAILED|CUDA_ERROR_|stack backtrace:',text),'no native fatal markers '+identity)
unit=J('runs/V035-unit/report.json');comparison=J('comparisons/E035-three-pair-comparison/report.json')
check(sha(R/'comparisons/E035-three-pair-comparison/report.json')=='1c919a8579ae12c109674a70e93564954eecfe007cabbce468aa7e020926201b','root comparison pin')
check(sha(R/'runs/E035-cleanup/report.json')=='c19ce0a577a27c444fe816737be09acd2a06d5bd8c5cfc1acf749cdce2b92564','root cleanup pin')
check(clean['source_before']['source_sha256']==expected and clean['source_after']['source_sha256']==base and clean['all162_accepted_entries_exact'],'cleanup exact before/after')
for name,v in clean['preserved_candidate_sources'].items():check(sha(v['path'])==v['sha256']==expected[name],'archived candidate '+name)
pinmap(base,REPO)
for n,v in protocol['preexisting_target_artifacts'].items():check(sha(REPO/n)==v['sha256'] and (REPO/n).stat().st_size==v['bytes'],'existing PTX unchanged')
live=Path(r'X:\Dev\GTOpen\target\desktop-runtime\release\gto-server.exe');check(sha(live)==clean['live_exe_sha256']=='b7b808b8baff6b3a92c4f3cc8c54ee74ee2c0bb079a8ca68be4da9703f6b84bd','exact live desktop binary unchanged')
main_head=subprocess.check_output(['git','-C',r'X:\Dev\GTOpen','rev-parse','HEAD'],text=True).strip();check(main_head==clean['main_head']['stdout'].strip()=='ae823c8bd6d723c75e096da139fd638d7dd397eb','main HEAD unchanged')
check(stamp(auth['at'])<=stamp(act['at'])<stamp(feature['at'])<stamp(unitmanifest['built_at'])<stamp(inv['at'])<=stamp(unit['started_at'])<stamp(unit['finished_at'])<=stamp(done['at'])<=stamp(comparison['created_at'])<=stamp(clean['at']),'full chronological custody')
check(clean['comparison_sha256']==sha(R/'comparisons/E035-three-pair-comparison/report.json') and clean['primary_complete_sha256']==sha(R/'runs/E035-primary-execution/complete.json'),'cleanup outcome pins')
check(clean['all_builds_and_native_terminal'] and clean['no_broader_runs_or_extra_samples'],'root closed scope')
for rel in ['runs/E035-qualification-plan','runs/E035-wide-turn-holdout-implementation','comparisons/E035-qualification','comparisons/E035-cumulative-comparison']:check(not (R/rel).exists(),'no conditional output '+rel)
check(not (R/'gpu-run.lock').exists(),'GPU lock released')
check(comparison['decision']=='rejected' and not comparison['accepted'] and not comparison['deployed'],'rejection preserved')
validation=J('comparisons/E035-independent-review/validation.json');check(validation['verdict']=='CONFIRMED_REJECTED' and validation['numerical_audit_pass'],'independent numerical completion')
report={'id':'E035','verdict':'PASS_SOURCE_BUILD_RUNTIME_CUSTODY','source_build_custody_pass':True,'accepted_sources_restored':True,'candidate_accepted':False,'deployment_changed':False,
'facts':['Exactly kernels.cu and the focused-test mod.rs differ within the162-entry source map; frozen source, authorization, activation, both build snapshots, archived copies and seven runtime source maps agree.','One preflop-research lib-test compile-only command and a separate fresh GPU-only unit/evaluator build completed before native tests. All three frozen candidate binaries match their Cargo artifacts, contain complete candidate CUDA and omit the full accepted CUDA string.','Only V035-unit,B110,E035R1,E035R2,B111,B112,E035R3 wrapper invocations are present, all terminal0 in order; raw outputs and fixed gates are independently validated in validation.json.','Both candidate files remain archived; all162 acceptedE020 source hashes are restored, both generated PTX files/mainHEAD/exact live desktop-runtime binary unchanged, GPU lock absent. No conditional broader/holdout/cumulative outputs follow rejection.'],
'checks_passed':len(checks),'input_sha256':pins,'limits':['File-backed custody audit only; no reviewer compiler/native/GPU work.','Focused26-pair equality and all14-input immutability rely on the source-pinned native unit assertions and success marker; full direct-test output arrays were not retained as a replayable dump.','The0.029646percent observed aggregate difference is below the fixed2percent gate; no performance acceptance, causality or statistical-significance claim.']}
with (O/'source-custody.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(report,f,indent=2);f.write('\n')
summary='E035 is rejected:9552.0106 to9549.1788ms, observed gain0.0296461145%, below the fixed2% gate. No fixture guard failed; all six timing samples were retained.\n\nAll18 complete non-timing results,138 convergence checkpoints and normalized stage trajectories match exactly. Units85passed/0failed/4ignored include the pinned original-GPU fold test (26pairs/52launches), with no extra benchmarks. Separate fresh feature and GPU-only builds, exact two-source/binary custody, fixed serial order and restoration are verified.\n\nAll162 acceptedE020 sources, the two existing PTX files, mainHEAD and exact live desktop-runtime binary are unchanged. No broader qualification, rescue, adoption, deployment, causal or statistical-significance claim. Direct-test array equality rests on retained source-pinned native assertions; raw arrays were not separately dumped.\n'
with (O/'combined-summary.md').open('x',encoding='utf-8',newline='\n') as f:f.write(summary)
files=['preparation.json','audit-numerical.py','validation.json','summary.md','custody-audit.py','source-custody.json','combined-summary.md']
manifest={'id':'E035-independent-review','verdict':'CONFIRMED_REJECTED','artifact_sha256':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in files},'candidate_accepted':False,'deployment_changed':False}
with (O/'manifest.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(manifest,f,indent=2);f.write('\n')
print(json.dumps({'custody_sha256':sha(O/'source-custody.json'),'manifest_sha256':sha(O/'manifest.json'),'checks':len(checks),'pins':len(pins)}))