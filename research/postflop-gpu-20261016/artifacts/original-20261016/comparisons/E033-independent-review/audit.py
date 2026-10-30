"""Read-only E033 terminal evidence audit; writes only this review directory."""
from pathlib import Path
import hashlib,json,re,subprocess,datetime
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016'); REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016'); O=Path(__file__).parent
pins={}; checks=[]
def check(ok,label):
    if not ok: raise AssertionError(label)
    checks.append(label)
def sha(p):
    p=Path(p); h=hashlib.sha256(p.read_bytes()).hexdigest(); pins[str(p)]=h; return h
def J(rel):
    p=R/rel;sha(p);return json.loads(p.read_text(encoding='utf-8'))
def pinmap(m,base=R):
    for p,h in m.items():check(sha(Path(p) if Path(p).is_absolute() else base/p)==h,'hash:'+str(p))
source=J('runs/E033-design/manifest.json'); plan=J('runs/E033-primary-plan-r2/scripts-manifest.json')
check(pins[str(R/'runs/E033-design/manifest.json')]=='ce92311e2aa1cec5977e7ed5cf9fad6cb96fd2f1f373fced496c9ca208f92324','frozen source seal')
check(pins[str(R/'runs/E033-primary-plan-r2/scripts-manifest.json')]=='09d71fb28ed17f672bf837bfbc16d02bbe31e55cb6057157bdad8034e3f95050','frozen R2 script seal')
pinmap(source['artifact_sha256'],R/'runs/E033-design');pinmap(plan['script_sha256'],R/'runs/E033-primary-plan-r2')
protocol=J('runs/E033-primary-plan-r2/protocol.json');auth=J('runs/E033-primary-plan-r2/authorization.json');act=J('runs/E033-source/activation.json')
check(sha(R/'runs/E033-primary-plan-r2/authorization.json')=='460c16ed8a1485ae714f1ba98a0878f20730f9247e64799279b891de63126d51','root authorization exact')
pinmap(auth['evidence_sha256'])
for v in auth['prerequisites'].values():check(sha(v['path'])==v['sha256'],'authorization prerequisite')
base=J('binaries/E020-postflop_autoresearch.manifest.json')['source_sha256']; expected=base|source['candidate_owned_sha256']
check(len(base)==162 and len(expected)==163,'162 accepted / 163 candidate maps')
check(act['source_sha256']==expected and act['authorization_sha256']==sha(R/'runs/E033-primary-plan-r2/authorization.json'),'activation candidate map and authorization')
for k,v in auth['candidate_sources'].items():check(sha(v['path'])==expected[k]==v['sha256'],'authorized candidate source '+k)
feature=J('runs/E033-compile-check/complete.json'); unitmanifest=J('binaries/E033-solver.manifest.json'); benchmanifest=J('binaries/E033-postflop_autoresearch.manifest.json')
check(feature['status']=='COMPILE_ONLY_CHECKS_PASSED' and feature['native_executions']==0 and len(feature['commands'])==1,'single compile-only feature command')
check(feature['target_dir']!=unitmanifest['target_dir'],'separate feature and GPU target')
cuda=(R/'runs/E033-design/base/kernels.cu').read_bytes(); cleanup=(R/'runs/E033-design/cleanup-source.cu').read_bytes()
for folder in ['E033-compile-check','E033-build']:
    env=J('runs/'+folder+'/build-environment.json');check(env['target_previously_absent'] and env['compiler_override_absence']=={},folder+' fresh target / no inherited compiler override')
    check(J('runs/'+folder+'/source-before.json')['source_sha256']==expected,folder+' prebuild source custody')
    for name in ['mod.rs','cache_policy.rs']:check(sha(R/'runs'/folder/('candidate-'+name))==source['candidate_owned_sha256']['crates/solver/src/gpu/'+name],folder+' candidate copy '+name)
    check(sha(R/'runs'/folder/'candidate.patch')==source['artifact_sha256']['candidate.patch'],folder+' exact patch')
for data in [feature,unitmanifest,benchmanifest]:
    check(data['source_sha256']==expected,'complete build source identity')
for p,h in feature['evidence_sha256'].items():check(sha(p)==h,'feature evidence hash')
feature_art=feature['artifacts'][0]; a=feature_art['cargo_artifact'];check(a['features']==['gpu','preflop-research'] and a['fresh'] is False and a['profile']['test'],'feature lib-test artifact')
check(sha(feature_art['path'])==feature_art['sha256']==sha(a['executable']),'frozen feature binary')
check(cuda in Path(feature_art['path']).read_bytes() and cleanup in Path(feature_art['path']).read_bytes(),'feature numerical CUDA and cleanup source embedded')
for name,m in [('solver',unitmanifest),('postflop_autoresearch',benchmanifest)]:
    p=R/'binaries'/('E033-'+name+'.exe');check(sha(p)==m['binary_sha256']==sha(m['cargo_artifact']['executable']),'GPU frozen binary '+name)
    check(cuda in p.read_bytes() and cleanup in p.read_bytes(),'GPU numerical CUDA plus cleanup embedded '+name)
    for art in [m['cargo_artifact'],m['solver_artifact']]:
        check(art['features']==['gpu'] and art['fresh'] is False,'GPU artifact feature/fresh '+name)
        check(all(Path(x).is_relative_to(Path(m['target_dir'])) for x in art['filenames']),'GPU artifact paths '+name)
    check(m['primary_protocol_sha256']==sha(R/'runs/E033-primary-plan-r2/protocol.json') and m['compile_check_sha256']==sha(R/'runs/E033-compile-check/complete.json'),'GPU prerequisite bindings '+name)
    check(m['probe_authorization_sha256']==sha(R/'runs/E033-primary-plan-r2/authorization.json'),'GPU authorization binding '+name)
    for key,pathkey in [('build_log_sha256','build_log'),('build_stderr_sha256','build_stderr_log')]:check(sha(m[pathkey])==m[key],'GPU raw log pin '+name)
# Cargo terminal success and recorded no-run commands, never execute these commands here.
for folder,label in [('E033-compile-check','lib-tests'),('E033-build','build')]:
    ep='lib-tests.exit.json' if label=='lib-tests' else 'exit.json'; ex=J('runs/'+folder+'/'+ep)
    check(ex['returncode']==0 and '--no-run' in ex['command'] and '--locked' in ex['command'] and '--offline' in ex['command'],folder+' terminal compile only')
    rows=[json.loads(x) for x in (R/'runs'/folder/(label+'.jsonl')).read_text().splitlines() if x.strip()]
    check(rows[-1]=={'reason':'build-finished','success':True},folder+' cargo final success')
    check(not [x for x in rows if x.get('reason')=='compiler-message' and x.get('message',{}).get('level')=='error'],folder+' no compiler errors')
run=J('runs/V033-unit/report.json'); rawpath=R/'runs/V033-unit/stdout.log'; raw=rawpath.read_text(); rawsha=sha(rawpath)
check(run['status']=='invalid' and run['returncode']==101 and run['results']==[] and run['stages']==[],'unit native rc101 / no primary result')
check(rawsha==run['stdout_sha256'] and run['binary_sha256']==unitmanifest['binary_sha256'],'unit raw and binary custody')
check(run['command']==[str(R/'binaries/E033-solver.exe'),'--nocapture','--test-threads=1'],'exact serialized unit command')
check(run['binary_build_manifest']['sha256']==sha(R/'binaries/E033-solver.manifest.json') and run['binary_build_manifest']['data']==unitmanifest,'unit embedded build manifest')
summary=re.findall(r'test result: FAILED\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)
check(summary==[('86','1','4','0','0')],'exact failed summary86/1/4/0/0')
starts=list(re.finditer(r'(?m)^test ([^ ]+) \.\.\. ',raw)); statuses={}
for i,m in enumerate(starts):
    block=raw[m.end():starts[i+1].start() if i+1<len(starts) else raw.index('\nfailures:',m.end())]
    statuses[m.group(1)]='ignored' if block.startswith('ignored') else ('failed' if re.search(r'(?m)^FAILED\s*$',block) else ('passed' if re.search(r'(?m)^ok\s*$',block) else 'unknown'))
check(len(statuses)==91 and list(statuses.values()).count('passed')==86 and list(statuses.values()).count('ignored')==4,'independent per-test inventory')
failed=[k for k,v in statuses.items() if v=='failed'];check(failed==['gpu::tests::shared_evaluation_matches_independent_sweeps'],'sole failed test')
check(all(statuses[x]=='passed' for x in protocol['expected_new_unit_tests']),'all three new tests terminal passed')
check('E033_CACHE_CLEANUP_ERROR' not in raw,'no cleanup failure marker')
check(raw.count(' panicked at ')==1 and 'mod.rs:1586:17' in raw and 'evaluation qualification requires enabled policy' in raw,'exact panic and assertion')
policy=[json.loads(x) for x in re.findall(r'E033_CACHE_POLICY (\{[^\n]+\})',raw)]
check(any(x['owned_bytes']==36 and x['window_bytes']==0 and not x['enabled'] for x in policy),'36-byte / zero-window fallback directly observed')
inv=J('runs/E033-primary-execution/invocation.json'); ex=J('runs/E033-primary-execution/V033-unit.exit.json'); ui=J('runs/E033-primary-execution/V033-unit.invocation.json')
check(inv['order']==protocol['order']==['V033-unit','B104','E033R1','E033R2','B105','B106','E033R3'],'frozen intended order')
check(ex['returncode']==1 and ex['error'] is None,'wrapper propagated native failure')
for p in (R/'runs/E033-primary-execution').iterdir():sha(p)
check([x.name for x in (R/'runs/E033-primary-execution').glob('*.invocation.json')]==['V033-unit.invocation.json'],'only unit native invocation')
check(not (R/'runs/E033-primary-execution/complete.json').exists(),'no completed cohort')
for identity in protocol['order'][1:]:check(not (R/'runs'/identity).exists(),'timing ID absent '+identity)
check(not (R/'comparisons/E033-three-pair-comparison').exists(),'no primary comparison')
clean=J('runs/E033-cleanup/report.json');check(sha(R/'runs/E033-cleanup/report.json')=='6ba602f0bfa292d1c8dd53b28b93f10cc0b738b4e23b4a23a28dde9544804fea','root cleanup exact')
check(clean['source_before']['source_sha256']==expected and clean['source_after']['source_sha256']==base and clean['accepted_sources_restored'],'cleanup before/after custody')
pinmap(clean['candidate_files_sha256'],R/'runs/E033-cleanup');pinmap(base,REPO)
check(not (REPO/'crates/solver/src/gpu/cache_policy.rs').exists(),'new module removed')
for p,h in plan['reference_sha256'].items():
    if 'research-fixtures' in p:check(sha(p)==h,'preexisting PTX unchanged')
live=Path(r'X:\Dev\GTOpen\target\desktop-runtime\release\gto-server.exe');check(sha(live)==clean['live_executable_sha256']=='b7b808b8baff6b3a92c4f3cc8c54ee74ee2c0bb079a8ca68be4da9703f6b84bd','exact live desktop executable unchanged')
main_head=subprocess.check_output(['git','-C',r'X:\Dev\GTOpen','rev-parse','HEAD'],text=True).strip();check(main_head=='ae823c8bd6d723c75e096da139fd638d7dd397eb','main HEAD unchanged')
check(auth['at']<=act['at']<feature['at']<unitmanifest['built_at']<inv['at']<=run['started_at']<run['finished_at']<=clean['at'],'authorization/activation/feature/GPU/unit/cleanup chronology')
report={'id':'E033','verdict':'PASS_AUDIT_FAILED_UNIT_GATE','unit_gate_pass':False,'primary_executed':False,'performance_measured':False,'candidate_accepted':False,'accepted_sources_restored':True,'native_unit_returncode':101,'wrapper_returncode':1,'unit_summary':{'passed':86,'failed':1,'ignored':4,'measured':0,'filtered_out':0},'failed_tests':failed,'new_tests':{x:statuses[x] for x in protocol['expected_new_unit_tests']},'feature_compile_only_pass':True,'separate_gpu_build_pass':True,'failure_classification':'Added test eligibility assertion contradicts intentional zero-window fallback; no numerical mismatch is reported.','source_evidence':['E033 candidate mod.rs1558-1599: existing six-case matrix; new unconditional enabled assertion at1586 precedes40-iteration/numerical/lock comparisons.','E033 cache_policy.rs30-33,65-78: prefix is floor(bytes/128)*128; zero prefix yields None.','Raw unit log shows9nodes,owned_bytes36,window_bytes0,enabledfalse immediately before sole assertion panic.'],'limits':['The failing test is not passed: the zero-window river subcase stopped before its numerical comparisons, and its later rake subcase was not reached.','All three added tests passed in this unit run; this does not replace the failed full unit gate or conditional broader qualification.','Feature-only lifecycle test was compiled, not executed. No six-run primary samples, quality-result comparisons, speed result, adoption or deployment.','Raw full arrays are not retained here; passed test claims rest on source-pinned native assertions, not an independent replay of device contents.'],'review_correction':'The earlier source review missed the unconditional policy requirement on the existing sub-line fixture. Its sealed report is preserved; this additive terminal audit records that limitation.','successor_recommendation':'A separately registered successor limited to correcting this test eligibility assertion is justified before any performance data: explicitly require absent policy and disabled stream window for W=0; retain required enabled/exact-size checks for supported eligible nonzero fixtures, every workload/numerical assertion, and fresh compile/unit/primary gates. Do not rerun or relabel E033.','reviewer_operations':'Only file reading/hashing/JSON and raw-log parsing plus read-only git HEAD; no compiler/native/CUDA/GPU/source/status operations.','main_head':main_head,'checks_passed':len(checks),'input_sha256':pins}
(O/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
(O/'summary.md').write_text('E033 remains failed at the unit gate: 86 passed, 1 failed, 4 ignored; native exit101. The sole failure is an incorrect unconditional eligibility assertion for a36-byte buffer whose intentional aligned window is0. All3newtests passed. Both builds and restoration were verified; no primary benchmarks ran.\n\nThe prior source review missed this assertion scope. A separately registered assertion-only successor is justified with all numerical assertions and fresh gates retained. This is no numerical or performance acceptance.\n',encoding='utf-8')
manifest={'id':'E033-independent-review','artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),O/'report.json',O/'summary.md']},'candidate_accepted':False}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'verdict':report['verdict'],'checks':len(checks),'pins':len(pins),'report_sha256':sha(O/'report.json'),'manifest_sha256':sha(O/'manifest.json')}))
