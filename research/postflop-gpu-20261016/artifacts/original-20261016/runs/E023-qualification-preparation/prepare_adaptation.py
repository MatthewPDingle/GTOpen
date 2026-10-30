"""Preparation only: copy preserved qualification machinery; no native process."""
from pathlib import Path
import ast, datetime, hashlib, json, shutil

ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
OLDQ=ROOT/'runs/E020-qualification-plan-r3'
OLDH=ROOT/'runs/E020-wide-turn-holdout-implementation-r2'
Q=ROOT/'runs/E023-qualification-plan'
H=ROOT/'runs/E023-wide-turn-holdout-implementation'
DESIGN=ROOT/'runs/E023-design'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def text(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def save(p,s):text(p,json.dumps(s,indent=2,allow_nan=False)+'\n')
def replace(s,a,b,n=1):
    assert s.count(a)==n,(a,s.count(a),n)
    return s.replace(a,b)
def fnv(data):
    h=0xcbf29ce484222325
    for b in data:h=((h^b)*0x100000001b3)&((1<<64)-1)
    return f'{h:016x}'

assert not Q.exists() and not H.exists()
Q.mkdir();H.mkdir()
d=read(DESIGN/'manifest.json')
base=read(ROOT/'binaries/E020-postflop_autoresearch.manifest.json')['source_sha256']
sources=dict(base);sources.update(d['candidate_owned_sha256'])
save(Q/'primary-source.json',sources)
save(H/'protected-checkout.json',sources)
for label,folder in [('E020','base'),('E023','candidate')]:
    shutil.copyfile(DESIGN/f'{folder}/kernels.cu',H/f'{label}-kernels.cu')
kernel=(H/'E023-kernels.cu').read_bytes()
assert kernel.startswith((H/'E020-kernels.cu').read_bytes())
assert b'__global__ void up_action_opponent(' in kernel

# Broader scripts retain the existing workload and use an explicit feature-only test.
for name in ['common.py','build.py','controls.py','cumulative.py','assess.py']:
    s=(OLDQ/name).read_text(encoding='utf-8').replace('E020','E023').replace('V020','V023')
    s=s.replace('E023-wide-turn-holdout-implementation-r2','E023-wide-turn-holdout-implementation')
    text(Q/name,s)
s=(Q/'common.py').read_text(encoding='utf-8')
s=replace(s,"[('84','0','4','0','0')]","[('86','0','4','0','0')]")
s=replace(s,"    PINS = read(HERE/'input-pins.json')","    PINS = read(HERE/'input-pins.json')\n    PINS.update(AUTH['execution_input_sha256'])\n    for identity in ('E023-postflop_autoresearch','E023-solver'):\n        for suffix in ('.exe','.manifest.json'):\n            assert str(ROOT/'binaries'/(identity+suffix)) in AUTH['execution_input_sha256']\n    for name in ('comparisons/E023-three-pair-comparison/report.json','runs/V023-unit/report.json','runs/V023-unit/stdout.log'):\n        assert str(ROOT/name) in AUTH['execution_input_sha256']")
s=replace(s,"{'E015-holdout.exe','E023-holdout.exe','E015-resource.exe'}","{'E020-holdout.exe','E023-holdout.exe','E020-resource.exe'}")
# Bind exact convergence records in F32 and cumulative, not merely equal truncation.
s=replace(s,"    return [{k:v for k,v in r.items() if k not in TIMING} for r in results]", """    checks=[json.loads(line.split('AUTORESEARCH_STAGE ',1)[1]) for line in raw.splitlines() if 'AUTORESEARCH_STAGE ' in line]
    checks=[{k:s[k] for k in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']} for s in checks if s.get('stage')=='convergence_check']
    assert len(checks)==23 and [r['iteration'] for r in results]==[200,200,60]
    for fixture,stop in zip(cmp.FIXTURES,[200,200,60]):
        assert [s['iteration'] for s in checks if s['fixture_id']==fixture]==list(range(20,stop+1,20))
    return {'results':[{k:v for k,v in r.items() if k not in TIMING} for r in results], 'checks':checks}""")
text(Q/'common.py',s)
s=(Q/'controls.py').read_text(encoding='utf-8')
s=replace(s,"'continuation_tests':3 if status=='pass' else None,","'continuation_tests':3 if status=='pass' else None,'capacity_tests':1 if status=='pass' else None,")
text(Q/'controls.py',s)
s=(Q/'cumulative.py').read_text(encoding='utf-8')
s=replace(s,"==(160,3,6,3)","==(160,3,6,3)\n    assert b['capacity_tests']==1 and any(x['id']=='V023-capacity' and x['passed']==1 for x in b['checks'])")
text(Q/'cumulative.py',s)
p=json.loads(json.dumps(read(OLDQ/'protocol.json')).replace('E020','E023').replace('V020','V023'))
p.update(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='DRAFT_CONDITIONAL_SOURCE_ONLY',
    entry_gate='Qualifying fixed E023 primary and independent audit; original unit screen86passed/4ignored. No new primary runs.',
    target_directory=str(ROOT/'build-e023-qualification'))
capacity=d['conditional_broader_feature_test']
p['controls'].append(dict(id='V023-capacity',binary='E023-continuation-tests',test=capacity,ordinary=True,storage='compressed',passes=1))
p['control_gates'].append(dict(id='V023-capacity',gate='Exactly named feature-only test1passed; mixed and uniform plans assert actual/estimated immutable metadata equality. Required separately from the three continuation controls.'))
p['primary_delta']='Exactly five E023-design files; unchanged original evaluator, action/down/eval arithmetic and E020 showdown cache. Immutable primary GPU-only binary retained for F32/cumulative.'
p['scope']='Original160 snapshots;3F32 fixtures;6GPU integration tests;3continuation controls;1explicit mixed/uniform capacity test. Exact original comparisons are distinct from shared-kernel integration tests.'
p['limits']=[x.replace('changed up_show','candidate training-up route') for x in p['limits']]
p['holdout_gate']='Unchanged E020 workload protocol33d4a047... and evaluator/fixture, with E020/E023 execution bindings. Broad and holdout terminal/audit pass required before cumulative.'
p['cumulative_ids_status']='Reserved by root before final freeze; draft placeholders cannot execute.'
for row in p['cumulative_order']:
    if row['binary']=='baseline-complete':row['id']={'B065':'UNRESERVED-B1','B066':'UNRESERVED-B2','B067':'UNRESERVED-B3'}[row['id']]
for row in p['pairs']:row['baseline']={'B065':'UNRESERVED-B1','B066':'UNRESERVED-B2','B067':'UNRESERVED-B3'}[row['baseline']]
for item in p['build_order']:
    item['command'][3:3]=['--locked','--offline']
save(Q/'protocol.json',p)
oldpins=read(OLDQ/'input-pins.json')
pins={k:v for k,v in oldpins.items() if any(x in k for x in ['baseline-manifest.json','baseline-complete.','\\tools\\','V000-','V004-f32-baseline','E020-wide-turn-holdout-plan','E020-wide-turn-holdout-review'])}
for path in [DESIGN/'manifest.json',ROOT/'comparisons/E023-source-review/report.json',ROOT/'comparisons/E023-source-review/manifest.json',ROOT/'runs/E023-primary-plan/scripts-manifest.json',OLDQ/'prepared-manifest.json',OLDH/'prepared-manifest.json']:
    pins[str(path)]=sha(path)
save(Q/'input-pins.json',pins)

# The complete numerical evaluator, fixture, protocol and codec remain exact bytes.
for name in ['evaluator.rs','fixture.json','plan-fixture.json','plan-protocol.json','plan-manifest.json','plan-frozen-primary.rs','plan-source-derived-bounds.json','runner-primitives-source.py','codec_selftest.py']:
    shutil.copyfile(OLDH/name,H/name)
maps={}
for role in ['E020','E023']:
    target=H/'workspaces'/role
    shutil.copytree(OLDH/'workspaces/E020',target)
    # Accepted production map is exact except the separately appended two Cargo test declarations.
    for name,h in base.items():
        if name=='crates/solver/Cargo.toml':
            original=(target/name).read_bytes().split(b'\n[[test]]\nname = "postflop_wide_turn_holdout"')[0]
            assert hashlib.sha256(original).hexdigest()==h,(role,name)
        else:assert sha(target/name)==h,(role,name)
    if role=='E023':
        for name,h in d['candidate_owned_sha256'].items():
            shutil.copyfile(DESIGN/'candidate'/Path(name).name,target/name)
            assert sha(target/name)==h
    maps[role]={x.relative_to(target).as_posix():sha(x) for x in sorted(target.rglob('*')) if x.is_file()}
assert [name for name in maps['E020'] if maps['E020'][name]!=maps['E023'][name]]==sorted(d['owned_sources'])
save(H/'workspace-source-maps.json',maps)
s=(OLDH/'resource.rs').read_text(encoding='utf-8').replace('E020','E023').replace('E015','E020')
s=s.replace('//! D037:','//! E023 fixed holdout:')
s=replace(s,'22624',str(len((H/'E020-kernels.cu').read_bytes())))
s=replace(s,'3f0594b037a1dda3',fnv((H/'E020-kernels.cu').read_bytes()))
s=replace(s,'let multiplier=if variant=="baseline" {8u32} else {16};','let multiplier=16u32;')
text(H/'resource.rs',s)
s=(OLDH/'run.py').read_text(encoding='utf-8').replace('E020','E023').replace('E015','E020').replace('build-holdout-e020-r2','build-holdout-e023')
start=s.index('def embedded_cuda(');end=s.index('\ndef check_cargo_artifacts',start)
s=s[:start]+'''def embedded_cuda(binary,name):
    data=Path(binary).read_bytes()
    counts={role:data.count((HERE/f'{role}-kernels.cu').read_bytes()) for role in ['E020','E023']}
    marker=b'__global__ void up_action_opponent('
    if name=='E020-resource':
        assert all(n>0 for n in counts.values()) and marker in data,('resource exact sources missing',counts)
    elif name=='E020-holdout':
        assert counts['E020']>0 and counts['E023']==0 and marker not in data,('wrong baseline CUDA',counts)
    else:
        assert name=='E023-holdout'
        assert counts['E023']>0 and counts['E020']>0 and marker in data,('wrong candidate CUDA',counts)
    return counts

''' + s[end:]
old="""    primary=read(HERE/'primary-audit-validation.json')
    assert primary['verdict']=='CONFIRMED_PROVISIONAL_QUALIFYING'
    assert primary['primary']['aggregate_gate_met'] is True and primary['primary']['fixture_guard_failed'] is False
    assert primary['all18_complete_non_timing_results_exact'] is True and primary['all_convergence_trajectories_exact'] is True"""
new="""    primary_path=pin(authorization['primary_report'])
    assert primary_path.resolve()==(ROOT/'comparisons/E023-three-pair-comparison/report.json').resolve()
    primary=read(primary_path);assert primary['decision']=='qualifying'
    assert authorization['all18_primary_states_exact'] is True and authorization['all138_primary_checks_exact'] is True
    assert authorization['independent_primary_audit'] in authorization['required_evidence']
    pin(authorization['independent_primary_audit'])"""
s=replace(s,old,new)
s=replace(s,"        assert sha(args.authorization)==args.authorization_sha256","        assert sha(args.authorization)==args.authorization_sha256\n        pin(authorization['primary_report'])")
s=replace(s,"[13160,21808],['3f0594b037a1dda3','fd544fbd87847b9c']",f"[21808,21808],{[fnv((H/'E020-kernels.cu').read_bytes()),fnv(kernel)]!r}")
# These evaluator fields are frozen historical metadata, not current resource queries.
s=replace(s,"                    assert admission['baseline_dynamic_shared_bytes']==[13160,13160]", "                    # Unchanged evaluator carries historical E015/E020 size labels; actual E020/E023 resources are checked above.\n                    assert admission['baseline_dynamic_shared_bytes']==[13160,13160]")
s=replace(s,"'candidate_accepted':False,'deployment_changed':False,'protocol_sha256':sha(HERE/'plan-protocol.json')", "'candidate_accepted':False,'deployment_changed':False,'protocol_sha256':sha(HERE/'plan-protocol.json'),\n                    'execution_binding_sha256':sha(HERE/'execution-binding.json'),'arms':{'baseline':'E020','candidate':'E023'},\n                    'actual_dynamic_shared_bytes':{'E020':[21808,21808],'E023':[21808,21808]},\n                    'frozen_admission_size_labels':'Historical E015/E020 labels retained in byte-identical evaluator; actual current sizes are in resource evidence'}")
text(H/'run.py',s)
save(H/'execution-binding.json',dict(candidate='E023',baseline='E020',workload_protocol_sha256=sha(H/'plan-protocol.json'),
    evaluator_sha256=sha(H/'evaluator.rs'),fixture_sha256=sha(H/'fixture.json'),
    order=['B1','C1','C2','B2','B3','C3'],gate='median slowdown>3% AND at least2of3 paired slowdowns>3%; exact all6 states/checks; no retuning',
    actual_dynamic_shared_bytes=dict(E020=[21808,21808],E023=[21808,21808]),
    unchanged_historical_admission_fields='The evaluator emits original E015/E020 formula labels13160/21808. These are retained unchanged and are not current-arm resource measurements.',
    source_map_difference_exactly=sorted(d['owned_sources']),accepted=False,deployed=False))
save(H/'input-identities.json',dict(workload_protocol_sha256=sha(H/'plan-protocol.json'),reference_prepared_manifest_sha256=sha(OLDH/'prepared-manifest.json'),
    baseline_primary_manifest_sha256=sha(ROOT/'binaries/E020-postflop_autoresearch.manifest.json'),candidate_design_manifest_sha256=sha(DESIGN/'manifest.json'),
    source_map_difference_exactly=sorted(d['owned_sources']),copied_files_per_workspace={k:len(v) for k,v in maps.items()}))
for folder in [Q,H]:
    for file in folder.glob('*.py'):ast.parse(file.read_text(encoding='utf-8'),filename=str(file))
save(Path(__file__).parent/'draft-generated.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    status='draft_source_only',broader_directory=str(Q),holdout_directory=str(H),evaluator_byte_identical=True,
    fixture_byte_identical=True,workspaces_differ_exactly_five_owned_sources=True,compiler_executions=0,gpu_executions=0))
print('Draft conditional packages prepared; no build/native execution.')
