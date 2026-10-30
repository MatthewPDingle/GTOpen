"""Host-only additive R2 seal; no compiler, GPU, checkout or R1 writes."""
from pathlib import Path
import ast, datetime, difflib, hashlib, json
HERE=Path(__file__).resolve().parent
R1=HERE.with_name('E020-wide-turn-holdout-implementation')
ROOT=HERE.parent.parent
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def save(path,value):
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
old=read(R1/'prepared-manifest.json')
assert sha(R1/'prepared-manifest.json')=='cac3399c20ce42c85fd0f2074f41cbb93d790ebe345673808857f46892f43340'
for name,h in old['artifact_sha256'].items():assert sha(R1/name)==h,name
for name in ['commands.json','build-authorization.example.json','resource-authorization.example.json','cohort-authorization.example.json']:
    text=(R1/name).read_text(encoding='utf-8').replace('E020-wide-turn-holdout-implementation','E020-wide-turn-holdout-implementation-r2').replace('E020-qualification-plan','E020-qualification-plan-r3')
    (HERE/name).write_text(text,encoding='utf-8',newline='\n')
readme=(R1/'README.md').read_text(encoding='utf-8')
readme=readme.replace('# E020 wide-turn holdout implementation','# E020 wide-turn holdout implementation R2',1)
readme=readme.replace('It uses a separate `build-holdout-e020` target directory, release/locked/offline Cargo, and1800-second fixed timeout per arm.',
    'It uses separate, previously absent `build-holdout-e020-r2/E015` and `build-holdout-e020-r2/E020` target directories, release/locked/offline Cargo, and the unchanged1800-second fixed timeout per arm.')
readme=readme.replace('runs/E020-qualification-plan/all-builds-ready.json','runs/E020-qualification-plan-r3/all-builds-ready.json')
readme+='''
## Additive build-only correction

The R1 build is invalid for arm comparison. Both holdout executable hashes were `d9cc5d1168b89c1753690467d94e63997cc40fabc312332e8ae3db9356f0def9`; E020 Cargo reported the solver and test artifacts `fresh: true` in the shared target directory. Both executables contain the exact E015 CUDA source and lack E020 CUDA. Root found this before any native holdout/resource invocation. The earlier source reviews and build report missed this cache-identity defect. R1 prepared inputs, logs, binaries, manifests and premature readiness remain unchanged and invalid; no measurement is discarded or replaced because none ran.

R2 copies all pinned R1 prepared inputs and makes no evaluator, fixture, protocol, production source, Cargo dependency/profile or numerical-comparison change. The only executable-code change is runner build provenance: the target root must not exist; each arm starts with its own empty target; every Cargo artifact path must be inside that arm target; solver/test source and manifest paths must match that workspace and the shared evaluator; solver/test artifacts must be newly compiled (`fresh: false`). Each holdout executable must embed its complete expected CUDA source and omit the opposite variant. The resource executable intentionally embeds both. The holdout binary hashes must differ. Binary/source guards repeat during readiness validation before and after native children.

`build-guard-selftest.json` records13 host-only checks, including rejection of the actual invalid R1 candidate binary and shared-target records. Synthetic relocated metadata is explicitly labeled; it is not a successful compile. The source/raw codec is byte-identical, so the copied R1 codec self-test remains historical evidence rather than a claimed new run. `prepare.py` is also the unchanged historical R1 preparation input and must not be rerun. `seal-r2.py` records this additive revision only.

Root must use new immutable build/resource/cohort authorizations pinned to this R2 manifest, and a new readiness record under qualification-plan-r3. The original readiness file must never authorize R2 or native execution. Qualification R3 changes only canonical holdout binding to this directory; its broader seven binaries are reused under their original source/build pins. This revision has no compiler/GPU execution or acceptance/deployment outcome.
'''
(HERE/'README.md').write_text(readme,encoding='utf-8',newline='\n')
before=(R1/'run.py').read_text(encoding='utf-8');after=(HERE/'run.py').read_text(encoding='utf-8')
assert before[before.index("            elif args.phase=='resource':"):]==after[after.index("            elif args.phase=='resource':"):]
assert before[before.index('def binary_equal('):before.index('def main():')]==after[after.index('def binary_equal('):after.index('def embedded_cuda(')]
changed=[name for name,h in old['artifact_sha256'].items() if sha(HERE/name)!=h]
assert sorted(changed)==sorted(['run.py','README.md','commands.json','resource-authorization.example.json','cohort-authorization.example.json'])
for p in HERE.rglob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p))
assert sha(HERE/'evaluator.rs')==old['artifact_sha256']['evaluator.rs']
assert sha(HERE/'resource.rs')==old['artifact_sha256']['resource.rs']
assert sha(HERE/'plan-protocol.json')=='33d4a047f67d1b23bd125cbfc8c31b564b6cf6a8417da768023beb8389c71510'
assert not (ROOT/'build-holdout-e020-r2').exists()
assert not (HERE/'build').exists() and not (HERE/'resource').exists() and not (HERE/'cohort').exists()
save(HERE/'preserved-r1-evidence.json',{'status':'invalid_wrong_arm_cache_reuse_no_native_tests',
 'R1_prepared_manifest_sha256':sha(R1/'prepared-manifest.json'),
 'R1_files':{str(p):sha(p) for p in sorted(R1.rglob('*')) if p.is_file()},
 'invalid_readiness':{'path':str(ROOT/'runs/E020-qualification-plan/all-builds-ready.json'),'sha256':sha(ROOT/'runs/E020-qualification-plan/all-builds-ready.json')},
 'native_tests':0,'gpu_executions':0})
save(HERE/'r2-mechanical-checks.json',{'status':'pass','changed_R1_prepared_inputs':changed,
 'unchanged_R1_inputs':len(old['artifact_sha256'])-len(changed),'protocol_evaluator_resource_workspaces_byte_identical':True,
 'resource_cohort_execution_and_numerical_parser_byte_identical':True,'Python_AST_pass':True,
 'new_target_root_absent':True,'build_guard_selftest_sha256':sha(HERE/'build-guard-selftest.json'),
 'compiler_executions':0,'gpu_executions':0,'checkout_edits':0,'R1_edits':0})
with (HERE/'runner-r2.patch').open('x',encoding='utf-8',newline='\n') as f:
    f.writelines(difflib.unified_diff(before.splitlines(keepends=True),after.splitlines(keepends=True),fromfile='R1/run.py',tofile='R2/run.py'))
for name,h in old['artifact_sha256'].items():assert sha(R1/name)==h,name
for p,h in read(HERE/'preserved-r1-evidence.json')['R1_files'].items():assert sha(Path(p))==h,p
manifest={**{k:v for k,v in old.items() if k!='artifact_sha256'},'id':HERE.name,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status':'frozen_prepared_R2_build_only_repair_not_built_or_executed','R1_prepared_manifest_sha256':sha(R1/'prepared-manifest.json'),
 'artifact_sha256':{p.relative_to(HERE).as_posix():sha(p) for p in sorted(HERE.rglob('*')) if p.is_file()},
 'source_only_checks':['Python AST','all scientific/evaluator/workspace inputs unchanged','resource/cohort and raw parser unchanged','13 host-only build-guard checks','R1 evidence unchanged']}
save(HERE/'prepared-manifest.json',manifest)
print(json.dumps({'path':str(HERE),'manifest_sha256':sha(HERE/'prepared-manifest.json'),'runner_sha256':sha(HERE/'run.py'),'files':len(manifest['artifact_sha256']),'checks':sha(HERE/'r2-mechanical-checks.json')}))
