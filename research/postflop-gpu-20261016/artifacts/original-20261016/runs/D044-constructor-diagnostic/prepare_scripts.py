"""Prepare the D042-derived D044 scripts only; never execute Cargo or a solver."""
from pathlib import Path
import datetime,hashlib,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
OLD=ROOT/'runs/D042-zero-proof-diagnostic'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s):
    with p.open('x',encoding='utf-8',newline='\n') as f:f.write(s)
def save(p,v):write(p,json.dumps(v,indent=2,allow_nan=False)+'\n')
source=read(HERE/'source-manifest.json')
assert sha(HERE/'source-manifest.json')=='8f522e9f4c2c71537495492119b95be8c50f48be117d57206a3a2c602f59b013'
for name,h in source['artifact_sha256'].items():assert sha(HERE/name)==h,name
p=read(OLD/'protocol.json')
p=json.loads(json.dumps(p).replace('D042','D044').replace('zero-proof-diagnostic','constructor-diagnostic').replace('build-d042-zero-proof','build-d044-constructor'))
p.update(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),owned_sources=[source['owned_source']],
    accepted_owned_sha256={source['owned_source']:source['accepted_source_sha256']},
    candidate_owned_sha256={source['owned_source']:source['candidate_source_sha256']},
    source_archive_path=str(HERE/'source-manifest.json'),source_archive_sha256=sha(HERE/'source-manifest.json'),
    expected_profile_records_per_run=3,marker='SPOT_CONSTRUCTOR_PROFILE',
    profile_order_per_fixture='Exactly one successful constructor record between fixture_start and build_complete',
    schema_sha256=sha(HERE/'schema.json'),stage_names=['tree_build','river_table','suit_symmetry'],
    expected_identity=read(HERE/'schema.json')['expected_identity'],
    exactness='All18 complete results/configuration/state objects and138 convergence checks exact across6 runs. Exactly3 constructor markers per instrumented run, none in ordinary controls; identities match frozen schema and build_complete stages.',
    component_aggregation='For each fixture/stage retain all3 profiled spans and raw ranges, then report median. Sum per-fixture medians only as grouped diagnostic host time, not measured saving.',
    component_interpretation='River-table span includes the unchanged entire table builder, not isolated ranking time. Tree and symmetry spans similarly include their existing work. No projected saving or 2% candidate qualification follows.',
    residual_interpretation='constructor minus3stage spans is unprofiled constructor work/timer overhead. Outer build minus3spans is unprofiled constructor/CPU storage and timing/logging overhead. Outer build minus constructor includes CPU storage, return/logging/timer/evaluator overhead; do not attribute it to ranking or allocation alone.',
    restore='Reverse only exact game.rs instrumentation patch after fixed cohort/audit; verify all162 acceptedE020 source hashes. Preserve every log and artifact.',
    additional_solver_work=0,extra_host_census=0,extra_device_or_arena_allocations=0)
for key in ['predicate_interpretation','duplicate_predicate_calls']:p.pop(key,None)
save(HERE/'protocol.json',p)
protocol_hash=sha(HERE/'protocol.json')
for name in ['build.py','cohort.py']:
    s=(OLD/name).read_text(encoding='utf-8')
    s=s.replace('D042','D044').replace('D042','D044').replace('zero-proof-diagnostic','constructor-diagnostic').replace('build-d042-zero-proof','build-d044-constructor')
    s=s.replace('3ff2d365177915d851fca29e6d54e3472dc743dffd1d30ff5b64d74cf54e657c',protocol_hash)
    s=s.replace('crates/solver/src/gpu/arena.rs','crates/solver/src/game.rs').replace('candidate-arena.rs','candidate-game.rs')
    s=s.replace('ZERO_UPLOAD_PROFILE','SPOT_CONSTRUCTOR_PROFILE').replace('zero-proof diagnostic','constructor diagnostic').replace('arena diagnostic file','game constructor diagnostic file')
    s=s.replace('Time the single original zero-proof call and existing device-zero allocation/wait separately; predicate, evaluator, CUDA, host arenas and error behavior unchanged. Diagnostic only, no performance acceptance.',
                'Time unchanged Spot tree/river-table/symmetry construction stages and constructor envelope. Evaluator, CUDA, math, call order and errors unchanged. Diagnostic only, no performance acceptance.')
    write(HERE/name,s)
a=read(OLD/'authorization.example.json')
a=json.loads(json.dumps(a).replace('D042','D044').replace('zero-proof-diagnostic','constructor-diagnostic'))
a['candidate_sources']={source['owned_source']:{'path':str(HERE/'candidate/game.rs'),'sha256':source['candidate_source_sha256']}}
a['evidence_sha256']={str(HERE/'scripts-manifest.json'):'ROOT_FILL_AFTER_REVIEW',str(HERE/'protocol.json'):protocol_hash,
    str(HERE/'source-manifest.json'):sha(HERE/'source-manifest.json'),'ROOT_FILL_ALL_PREREQUISITE_PATHS':'ROOT_FILL'}
a['scope']='Root pins immutable E020 acceptance/server and independent D044 source/script review. One temporary game.rs diagnostic; no accuracy shortcut, solver work or performance acceptance. Placeholders do not authorize execution.'
save(HERE/'authorization.example.json',a)
save(HERE/'commands.json',dict(build=['python','-B',str(HERE/'build.py'),'<authorization-sha256>'],
    cohort=['python','-B',str(HERE/'cohort.py')],assess=['python','-B',str(HERE/'assess.py')],
    activation='Root only: assert exact acceptedE020 then apply candidate.patch; no agent activation. Restore only instrumentation after cohort/audit.',
    fixed_order=p['order'],executed=False))
print(json.dumps({'protocol_sha256':protocol_hash,'scripts':'build/cohort prepared; assessor next','builds':0,'gpu':0}))
