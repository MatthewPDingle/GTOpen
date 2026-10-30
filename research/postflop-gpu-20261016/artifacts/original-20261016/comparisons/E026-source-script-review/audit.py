import ast, datetime, hashlib, json
from pathlib import Path
root=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
repo=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
out=Path(__file__).parent
plan=root/'runs/E026-primary-plan'
design=root/'runs/E026-design'
inputs={}
checks=[]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(name, value):
    assert value,name
    checks.append(name)
def pin(path, expected):
    path=Path(path); actual=sha(path); check('sha256:'+str(path),actual==expected); inputs[str(path)]=actual
def readj(p): return json.loads(Path(p).read_text(encoding='utf-8'))
pin(plan/'scripts-manifest.json','f7f0e7f395d5b2b6d8b6589d647f8583e33b9ccbe10bf00479f029742b9d7a2d')
pin(design/'manifest.json','d74b90eb938b12aed3032ec0a1b404b09c108b417a2683c71a39f52a666eb09e')
seal=readj(plan/'scripts-manifest.json'); sm=readj(design/'manifest.json')
for key in ('script_sha256','supporting_sha256'):
    for n,h in seal[key].items(): pin(plan/n,h)
for n,h in seal['reference_sha256'].items(): pin(n,h)
for n,h in sm['artifact_sha256'].items(): pin(design/n,h)
for n,h in sm['reference_pins'].items(): pin(n,h)
accepted=readj(root/'binaries/E020-postflop_autoresearch.manifest.json')['source_sha256']
check('accepted source count162',len(accepted)==162)
for n,h in accepted.items(): pin(repo/n,h)
p=readj(plan/'protocol.json')
check('fixed order',p['order']==['V026-unit','B086','E026R1','E026R2','B087','B088','E026R3'])
check('fixed pair mapping',p['pairs']==[{'baseline':'B086','candidate':'E026R1'},{'baseline':'B087','candidate':'E026R2'},{'baseline':'B088','candidate':'E026R3'}])
check('full fixture/stopping anchors',p['expected_fixtures']==['rainbow','two-tone','river'] and p['expected_stops']=={'rainbow':200,'two-tone':200,'river':60} and p['expected_convergence_records_per_run']==23)
check('no exclusion/extension',p['exclusions']==[] and p['outcome_triggered_extensions'] is False)
check('exact owned sources',p['owned_sources']==['crates/solver/src/gpu/kernels.cu','crates/solver/src/gpu/mod.rs'])
for n in p['owned_sources']:
    check('archived base matches accepted:'+n,sha(design/'base'/Path(n).name)==accepted[n])
    check('candidate pinned:'+n,sha(design/'candidate'/Path(n).name)==p['candidate_owned_sha256'][n])
check('CUDA is exact D050 candidate',(design/'candidate/kernels.cu').read_bytes()==(root/'runs/D050-show-physical256-resource/candidate.cu').read_bytes())
base=(design/'base/mod.rs').read_bytes(); candidate=(design/'candidate/mod.rs').read_bytes()
old=b'.launch(Self::cfg(sp.count, show_shared))'
new=b'.launch(LaunchConfig {\n                            block_dim: (256, 1, 1),\n                            ..Self::cfg(sp.count, show_shared)\n                        })'
check('two launch sites only',base.count(old)==2 and candidate.count(new)==2 and candidate==base.replace(old,new))
check('accepted cfg preserves grid/shared',b'grid_dim: (blocks, 1, 1)' in base and b'shared_mem_bytes: shared' in base)
for name in ('build.py','primary.py','assess.py'):
    source=(plan/name).read_text(encoding='utf-8')
    ast.parse(source,filename=name)
    check('AST parsed:'+name,True)
    for required in ("direct['verdict']=='PASS_EXACT_COMPLETE_UP_SHOW_COMPARISON'","direct['numerical_validation']=='executed'","direct['comparison_pairs']==148 and direct['kernel_launches']==296","direct['performance_measurement'] is False and direct['candidate_accepted'] is False","(128,256,128)","comparisons/D051-independent-review/validation.json","9aa099575d3ada3b00653fe5eddc88ed7a4b07d31fbedbd2b6b21a721c0eb8e5"):
        check('prerequisite '+name+':'+required,required in source)
check('no D051 terminal evidence yet',not (root/'comparisons/D051-independent-review/validation.json').exists())
for n in p['order']:
    check('unused run:'+n,not (root/'runs'/n).exists())
for n in ('runs/E026-build','runs/E026-primary-execution','runs/E026-assessment','build-primary-e026','binaries/E026-solver.exe','binaries/E026-postflop_autoresearch.exe'):
    check('unused output:'+n,not (root/n).exists())
check('no root authorization yet',not (plan/'authorization.json').exists())
build=(plan/'build.py').read_text(encoding='utf-8')
primary=(plan/'primary.py').read_text(encoding='utf-8')
assess=(plan/'assess.py').read_text(encoding='utf-8')
for label,condition in [
 ('fresh target', "assert not target.exists()" in build),
 ('fresh solver and tests',"solver_lib[0]['fresh'] is False" in build and "assert item['fresh'] is False" in build),
 ('embedded changed CUDA',"candidate_cuda in data and accepted_cuda not in data" in build),
 ('GPU build lock',"with ar.exclusive_lock(ar.RESEARCH / 'gpu-run.lock'):" in build),
 ('owned child cleanup',"cleanup = ar.cleanup_child(process)" in build and "cleanup=ar.cleanup_child(proc)" in primary),
 ('clear fixture filter',"env.pop('POSTFLOP_AUTORESEARCH_FIXTURE',None)" in primary),
 ('unit inventory',"('84', '0', '4', '0', '0')" in primary),
 ('complete nontiming comparison',"if k not in excluded_timing" in assess and "== reference, run['id']" in assess),
 ('raw trajectory equality',"checks==reference_checks" in assess and "==23" in assess),
 ('no acceptance',"compare.rejection_reasons(assessment['performance'])" in assess and "'qualifying'" in assess and "'candidate_accepted':False" in assess)]:
    check(label,condition)
result={'id':'E026','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS_SOURCE_AND_PROSPECTIVE_SCRIPTS',
 'independent_source_review_pass':True,'independent_script_review_pass':True,'actionable_findings':[],
 'source_manifest_sha256':sha(design/'manifest.json'),'scripts_manifest_sha256':sha(plan/'scripts-manifest.json'),
 'protocol_sha256':sha(plan/'protocol.json'),'check_count':len(checks),'input_count':len(inputs),'checks':checks,
 'inputs_sha256':inputs,'current_accepted_source_entries_exact':162,
 'pending_requirement':'Terminal independent D051 exact PASS and immutable root authorization are still required before activation/build.',
 'D051_numerical_validation':'not executed','activation_authorized':False,'candidate_accepted':False,
 'review_scope':'File-only frozen source/primary script review; no script import/execution, compiler, native test, CUDA call, timing, checkout or status mutation.'}
(out/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':result['status'],'checks':len(checks),'inputs':len(inputs),'validation_sha256':sha(out/'validation.json')}))
