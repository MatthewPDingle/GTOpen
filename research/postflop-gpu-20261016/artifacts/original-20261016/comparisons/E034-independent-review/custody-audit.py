"""Read-only E034 terminal evidence audit; writes only this review directory."""
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
source=J('runs/E034-design/manifest.json'); plan=J('runs/E034-primary-plan/scripts-manifest.json')
check(pins[str(R/'runs/E034-design/manifest.json')]=='882eadeae0c7615b041dfd635b148c484363689a6a901454f658534bab3224d8','frozen source seal')
check(pins[str(R/'runs/E034-primary-plan/scripts-manifest.json')]=='255ad6bb57df3d92413aad1a1edc3ca5e08a8befd6640166706ec49e07c651ce','frozen R2 script seal')
pinmap(source['artifact_sha256'],R/'runs/E034-design');pinmap(plan['script_sha256'],R/'runs/E034-primary-plan')
protocol=J('runs/E034-primary-plan/protocol.json');auth=J('runs/E034-primary-plan/authorization.json');act=J('runs/E034-source/activation.json')
check(sha(R/'runs/E034-primary-plan/authorization.json')=='d35ff333cc47f606226bddccb7acaf135b40009895d482263e3816cc0ff6416d','root authorization exact')
pinmap(auth['evidence_sha256'])
for v in auth['prerequisites'].values():check(sha(v['path'])==v['sha256'],'authorization prerequisite')
base=J('binaries/E020-postflop_autoresearch.manifest.json')['source_sha256']; expected=base|source['candidate_owned_sha256']
check(len(base)==162 and len(expected)==163,'162 accepted / 163 candidate maps')
check(act['source_sha256']==expected and act['authorization_sha256']==sha(R/'runs/E034-primary-plan/authorization.json'),'activation candidate map and authorization')
for k,v in auth['candidate_sources'].items():check(sha(v['path'])==expected[k]==v['sha256'],'authorized candidate source '+k)
feature=J('runs/E034-compile-check/complete.json'); unitmanifest=J('binaries/E034-solver.manifest.json'); benchmanifest=J('binaries/E034-postflop_autoresearch.manifest.json')
check(feature['status']=='COMPILE_ONLY_CHECKS_PASSED' and feature['native_executions']==0 and len(feature['commands'])==1,'single compile-only feature command')
check(feature['target_dir']!=unitmanifest['target_dir'],'separate feature and GPU target')
cuda=(R/'runs/E034-design/base/kernels.cu').read_bytes(); cleanup=(R/'runs/E034-design/cleanup-source.cu').read_bytes()
for folder in ['E034-compile-check','E034-build']:
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
    p=R/'binaries'/('E034-'+name+'.exe');check(sha(p)==m['binary_sha256']==sha(m['cargo_artifact']['executable']),'GPU frozen binary '+name)
    check(cuda in p.read_bytes() and cleanup in p.read_bytes(),'GPU numerical CUDA plus cleanup embedded '+name)
    for art in [m['cargo_artifact'],m['solver_artifact']]:
        check(art['features']==['gpu'] and art['fresh'] is False,'GPU artifact feature/fresh '+name)
        check(all(Path(x).is_relative_to(Path(m['target_dir'])) for x in art['filenames']),'GPU artifact paths '+name)
    check(m['primary_protocol_sha256']==sha(R/'runs/E034-primary-plan/protocol.json') and m['compile_check_sha256']==sha(R/'runs/E034-compile-check/complete.json'),'GPU prerequisite bindings '+name)
    check(m['probe_authorization_sha256']==sha(R/'runs/E034-primary-plan/authorization.json'),'GPU authorization binding '+name)
    for key,pathkey in [('build_log_sha256','build_log'),('build_stderr_sha256','build_stderr_log')]:check(sha(m[pathkey])==m[key],'GPU raw log pin '+name)
# Cargo terminal success and recorded no-run commands, never execute these commands here.
for folder,label in [('E034-compile-check','lib-tests'),('E034-build','build')]:
    ep='lib-tests.exit.json' if label=='lib-tests' else 'exit.json'; ex=J('runs/'+folder+'/'+ep)
    check(ex['returncode']==0 and '--no-run' in ex['command'] and '--locked' in ex['command'] and '--offline' in ex['command'],folder+' terminal compile only')
    rows=[json.loads(x) for x in (R/'runs'/folder/(label+'.jsonl')).read_text().splitlines() if x.strip()]
    check(rows[-1]=={'reason':'build-finished','success':True},folder+' cargo final success')
    check(not [x for x in rows if x.get('reason')=='compiler-message' and x.get('message',{}).get('level')=='error'],folder+' no compiler errors')

inv=J('runs/E034-primary-execution/invocation.json');done=J('runs/E034-primary-execution/complete.json');clean=J('runs/E034-cleanup/report.json')
check(inv['order']==done['order']==protocol['order']==['V034-unit','B107','E034R1','E034R2','B108','B109','E034R3'],'exact completed fixed order')
actual_invocations=sorted(x.name for x in (R/'runs/E034-primary-execution').glob('*.invocation.json'))
check(actual_invocations==sorted(x+'.invocation.json' for x in protocol['order']),'only fixed seven native invocation records')
for identity in protocol['order']:
    record=J('runs/'+identity+'/report.json');check(record['provenance']['source_sha256']==expected,'runtime current source '+identity)
    check(record['status']=='measured' and record['returncode']==0,'terminal native '+identity)
    ex=J('runs/E034-primary-execution/'+identity+'.exit.json');check(ex['returncode']==0 and ex['error'] is None,'terminal wrapper '+identity)
    for suffix in ['invocation.json','stdout.log','stderr.log']:sha(R/'runs/E034-primary-execution'/(identity+'.'+suffix))
    sha(R/'runs'/identity/'stdout.log')
unit=J('runs/V034-unit/report.json');comparison=J('comparisons/E034-three-pair-comparison/report.json')
check(sha(R/'runs/E034-cleanup/report.json')=='f707af76f79f0964a77eb12aeaf249380aa761bbd6344353c5ea0cf07a36e23f','root cleanup exact')
check(clean['source_before']['source_sha256']==expected and clean['source_after']['source_sha256']==base and clean['accepted_sources_restored'],'cleanup before/after custody')
pinmap(clean['candidate_files_sha256'],R/'runs/E034-cleanup');pinmap(base,REPO)
check(not (REPO/'crates/solver/src/gpu/cache_policy.rs').exists(),'new module removed')
for p,h in plan['reference_sha256'].items():
    if 'research-fixtures' in p:check(sha(p)==h,'preexisting PTX unchanged')
live=Path(r'X:\Dev\GTOpen\target\desktop-runtime\release\gto-server.exe');check(sha(live)==clean['live_executable_sha256']=='b7b808b8baff6b3a92c4f3cc8c54ee74ee2c0bb079a8ca68be4da9703f6b84bd','exact live desktop executable unchanged')
main_head=subprocess.check_output(['git','-C',r'X:\Dev\GTOpen','rev-parse','HEAD'],text=True).strip();check(main_head=='ae823c8bd6d723c75e096da139fd638d7dd397eb','main HEAD unchanged')
check(auth['at']<=act['at']<feature['at']<unitmanifest['built_at']<inv['at']<=unit['started_at']<unit['finished_at']<=done['at']<=comparison['created_at']<=clean['at'],'authorization/activation/feature/GPU/unit/cohort/assessment/cleanup chronology')
for rel in ['runs/E034-qualification-plan','runs/E034-wide-turn-holdout-implementation','comparisons/E034-qualification','comparisons/E034-cumulative-comparison']:
    check(not (R/rel).exists(),'no conditional qualification output '+rel)
check(comparison['decision']=='rejected' and not comparison['accepted'] and not comparison['deployed'],'rejection preserved')
validation=J('comparisons/E034-independent-review/validation.json');check(validation['verdict']=='CONFIRMED_REJECTED' and validation['numerical_audit_pass'],'independent numerical audit complete')
report={'id':'E034','verdict':'PASS_SOURCE_BUILD_RUNTIME_CUSTODY','source_build_custody_pass':True,'accepted_sources_restored':True,'candidate_accepted':False,'deployment_changed':False,'facts':['One modified mod.rs plus new cache_policy.rs exactly match the frozen two-file candidate, activation and163-entry maps in both fresh builds and all seven runtime reports.','Feature lib-test build used preflop-research/gpu and no-run; separate GPU-only lib+benchmark build completed before any native test. Frozen binary hashes match Cargo artifacts; all three compiled executables contain the unchanged numerical CUDA and scoped cleanup CUDA.','Authorization/source/script/parent failure prerequisites and every source copy/patch checked. Native run order is exactly V034-unit,B107,E034R1,E034R2,B108,B109,E034R3, all terminal0; no additional wrapper invocations.','The entire accepted162-source map is restored, new module absent, both candidate files preserved; two preexisting generated PTX files, mainHEAD and exact desktop-runtime live executable unchanged.','No broader/holdout/cumulative qualification was performed after primary rejection.'],'checks_passed':len(checks),'input_sha256':pins,'limits':['Existing file-backed build and source provenance is audited; reviewer did not build or execute CUDA/native code.','Native numerical and policy evidence is separately evaluated in validation.json; neither this custody pass nor small positive observed gain is acceptance.']}
(O/'source-custody.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
(O/'combined-summary.md').write_text('E034 is rejected:9567.6953 to9518.9007ms, observed gain0.5099932478%, below the fixed2% gate. All fixture guards pass; river median slowdown0.938408451% does not exceed3% despite2/3paired regressions exceeding3%. All six samples were retained.\n\nAll18 complete non-timing results and138 convergence checks match, units87passed/0failed/4ignored, and all18 candidate policy records have exact extents and setup/cleanup placement inside original measured boundaries. Separate feature and GPU builds, exact source/binary custody, fixed serial order and restoration are verified. E033 failure remains preserved.\n\nAccepted E020 sources and live desktop executable are unchanged. No broader qualification, extra sample, rescue, adoption, deployment, causal or statistical significance claim.\n',encoding='utf-8')
files=['audit-numerical.py','validation.json','summary.md','custody-audit.py','source-custody.json','combined-summary.md']
(O/'manifest.json').write_text(json.dumps({'id':'E034-independent-review','verdict':'CONFIRMED_REJECTED','artifact_sha256':{f:hashlib.sha256((O/f).read_bytes()).hexdigest() for f in files},'candidate_accepted':False,'deployment_changed':False},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'custody_sha256':sha(O/'source-custody.json'),'manifest_sha256':sha(O/'manifest.json'),'checks':len(checks),'pins':len(pins)}))
