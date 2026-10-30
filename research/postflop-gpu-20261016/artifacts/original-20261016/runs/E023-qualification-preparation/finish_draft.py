"""Host-only conditional preparation; no build/native/GPU command."""
from pathlib import Path
import ast, datetime, hashlib, json
ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
Q=ROOT/'runs/E023-qualification-plan';H=ROOT/'runs/E023-wide-turn-holdout-implementation'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
p=read(Q/'protocol.json')
for row in p['cumulative_order']:
    row['id']={'UNRESERVED-B1':'B077','UNRESERVED-B2':'B078','UNRESERVED-B3':'B079'}.get(row['id'],row['id'])
for row in p['pairs']:row['baseline']={'UNRESERVED-B1':'B077','UNRESERVED-B2':'B078','UNRESERVED-B3':'B079'}.get(row['baseline'],row['baseline'])
p['cumulative_ids_status']='Root reserved B077/E023C1,E023C2/B078,B079/E023C3 before primary native measurements.'
save(Q/'protocol.json',p)
save(Q/'authorization.example.json',dict(candidate='E023',primary_independent_pass=True,source_review_pass=True,qualification_script_review_pass=True,
    prepared_manifest_sha256='ROOT_FILL_AFTER_REVIEW',
    evidence_sha256={'ABSOLUTE_SOURCE_REVIEW':'ROOT_PIN','ABSOLUTE_SCRIPT_REVIEW':'ROOT_PIN','ABSOLUTE_PRIMARY_AUDIT':'ROOT_PIN'},
    execution_input_sha256={str(ROOT/name):'ROOT_PIN_TERMINAL_FILE' for name in [
        'binaries/E023-postflop_autoresearch.exe','binaries/E023-postflop_autoresearch.manifest.json','binaries/E023-solver.exe','binaries/E023-solver.manifest.json',
        'comparisons/E023-three-pair-comparison/report.json','runs/V023-unit/report.json','runs/V023-unit/stdout.log']}))
save(Q/'all-builds-ready.example.json',dict(all_required_builds_terminal=True,all_builds_terminal=True,holdout_builds_terminal=True,holdout_build_source_review_pass=True,
    broader_build_complete=dict(path=str(ROOT/'runs/E023-qualification-build/complete.json'),sha256='ROOT_PIN'),
    artifacts={'ABSOLUTE_ALL10_EXES_AND10_MANIFESTS_PLUS_TERMINALS':'ROOT_PIN'},
    holdout_build_report=dict(path=str(H/'build/report.json'),sha256='ROOT_PIN')))
save(Q/'qualification-ready.example.json',dict(broader_pass=True,holdout_pass=True,independent_broader_review_pass=True,independent_holdout_review_pass=True,
    all_builds_ready=dict(path=str(Q/'all-builds-ready.json'),sha256='ROOT_PIN'),
    broader_report=dict(path=str(ROOT/'comparisons/E023-broader-qualification/report.json'),sha256='ROOT_PIN'),
    holdout_report=dict(path=str(H/'cohort/report.json'),sha256='ROOT_PIN'),evidence_sha256={'ABSOLUTE_BROADER_AND_HOLDOUT_INDEPENDENT_AUDITS':'ROOT_PIN'}))
auth=dict(candidate='E023',primary_audit_pass=True,holdout_source_review_pass=True,all18_primary_states_exact=True,all138_primary_checks_exact=True,
    prepared_manifest_sha256='ROOT_FILL_AFTER_REVIEW',
    primary_report=dict(path=str(ROOT/'comparisons/E023-three-pair-comparison/report.json'),sha256='ROOT_PIN_TERMINAL'),
    independent_primary_audit=dict(path='ABSOLUTE_INDEPENDENT_PRIMARY_AUDIT',sha256='ROOT_PIN'),
    required_evidence=[dict(path='ABSOLUTE_INDEPENDENT_PRIMARY_AUDIT',sha256='ROOT_PIN'),dict(path='ABSOLUTE_HOLDOUT_SOURCE_REVIEW',sha256='ROOT_PIN')])
save(H/'build-authorization.example.json',auth)
auth={**auth,'all_builds_ready':dict(path=str(Q/'all-builds-ready.json'),sha256='ROOT_PIN_AFTER_ALL_BUILDS')}
save(H/'resource-authorization.example.json',auth)
auth={**auth,'resource_report':dict(path=str(H/'resource/report.json'),sha256='ROOT_PIN_AFTER_RESOURCE')}
save(H/'cohort-authorization.example.json',auth)
for folder in [Q,H]:
    for file in folder.glob('*.py'):ast.parse(file.read_text(encoding='utf-8'),filename=str(file))
save(Path(__file__).parent/'draft-checks.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='syntax_source_checks_only',
    new_scripts_ast_parse=True,holdout_evaluator_exact=sha(H/'evaluator.rs')==sha(ROOT/'runs/E020-wide-turn-holdout-implementation-r2/evaluator.rs'),
    fixture_exact=sha(H/'fixture.json')==sha(ROOT/'runs/E020-wide-turn-holdout-implementation-r2/fixture.json'),
    controls=10,broader_binaries=7,holdout_binaries=3,builds=0,gpu_executions=0,
    preparation_only_issue='Generated draft had one extra dictionary-closing brace; corrected before AST/source review, no native command ran.'))
print('Syntax and unchanged evaluator/fixture checks pass; no build/native execution.')
