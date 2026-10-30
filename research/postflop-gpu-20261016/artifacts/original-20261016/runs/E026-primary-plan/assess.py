"""Assess every frozen primary measurement once; never accept a candidate."""
import hashlib, json, shutil, subprocess, sys
from pathlib import Path
repo = Path(r'X:\Dev\GTOpen-gpu-research-20261016')
here=Path(__file__).resolve().parent
seal=json.loads((here/'scripts-manifest.json').read_text(encoding='utf-8'))
authorization=json.loads((here/'authorization.json').read_text(encoding='utf-8'))
def pinned_sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
assert authorization['evidence_sha256'][str(here/'scripts-manifest.json')]==pinned_sha(here/'scripts-manifest.json')
for name,h in seal['script_sha256'].items():assert pinned_sha(here/name)==h,name
for path,h in seal['reference_sha256'].items():assert pinned_sha(path)==h,path
for path,h in authorization['evidence_sha256'].items():assert pinned_sha(path)==h,path
sys.path.insert(0, str(repo / 'tools'))
import postflop_autoresearch as ar
import postflop_compare as compare
assert authorization['D050_terminal_ptx_pass'] is True
assert authorization['direct_up_show_exact_pass'] is True
for role in ['D050_terminal_review', 'direct_up_show_terminal_review']:
    pin=authorization['prerequisites'][role]
    assert ar.sha256(Path(pin['path']))==pin['sha256']
    assert authorization['evidence_sha256'][pin['path']]==pin['sha256']
d050_pin=authorization['prerequisites']['D050_terminal_review']
d050=json.loads(Path(d050_pin['path']).read_text(encoding='utf-8'))
assert d050['verdict']=='PASS_SCOPED_COMPILER_CAPACITY_AND_PTX'
assert d050['capacity_prerequisite_pass'] is True and d050['source_ptx_prerequisite_pass'] is True
assert d050['numerical_validation']=='not executed' and d050['candidate_accepted'] is False
assert Path(d050_pin['path']).resolve()==(ar.RESEARCH/'comparisons/D050-independent-review/validation.json').resolve()
assert d050_pin['sha256']=='9aa099575d3ada3b00653fe5eddc88ed7a4b07d31fbedbd2b6b21a721c0eb8e5'
direct_pin=authorization['prerequisites']['direct_up_show_terminal_review']
assert Path(direct_pin['path']).resolve()==(ar.RESEARCH/'comparisons/D051-independent-review/validation.json').resolve()
direct=json.loads(Path(direct_pin['path']).read_text(encoding='utf-8'))
assert direct['id']=='D051' and direct['verdict']=='PASS_EXACT_COMPLETE_UP_SHOW_COMPARISON'
assert direct['exactness_pass'] is True and direct['numerical_validation']=='executed'
assert direct['baseline_cuda_sha256']=='075651690d59ede225c17ff9674662e040d40460a5e2b5436fd6fa7d4f5d663b'
assert direct['candidate_cuda_sha256']=='01ea83f9b15df2e973b336b9dc76e6b4a4d15025c406f57cee507327d36cf558'
assert (direct['baseline_physical_threads'],direct['candidate_physical_threads'],direct['logical_scan_threads'])==(128,256,128)
assert direct['comparison_pairs']==148 and direct['kernel_launches']==296
assert direct['performance_measurement'] is False and direct['candidate_accepted'] is False
base = ar.RESEARCH
assert not (base / 'gpu-run.lock').exists()
protocol = base / 'runs/E026-primary-plan/protocol.json'
assert ar.sha256(protocol) == '9ba20afba65a286279f531bb6dd46e2104edf01a35e70a9475dc3c78f5567388'
plan = json.loads(protocol.read_text(encoding='utf-8'))
here=protocol.parent
authorization=json.loads((here/'authorization.json').read_text(encoding='utf-8'))
assert authorization['evidence_sha256'][str(here/'scripts-manifest.json')]==ar.sha256(here/'scripts-manifest.json')
seal=json.loads((here/'scripts-manifest.json').read_text(encoding='utf-8'))
for name,h in seal['script_sha256'].items(): assert ar.sha256(here/name)==h,name
for path,h in seal['reference_sha256'].items(): assert ar.sha256(Path(path))==h,path
completed = json.loads((base / 'runs/E026-primary-execution/complete.json').read_text(encoding='utf-8'))
assert completed['order'] == plan['order']
baseline_ids = [p['baseline'] for p in plan['pairs']]
candidate_ids = [p['candidate'] for p in plan['pairs']]
baseline = [compare.load_run(r)[0] for r in baseline_ids]
candidate = [compare.load_run(r)[0] for r in candidate_ids]
frozen = json.loads((base / 'baseline-manifest.json').read_text(encoding='utf-8'))
# The shared helper checks an explicit tuple; the protocol requires every non-timing field.
excluded_timing = {'build_ms', 'init_ms', 'solve_ms', 'readback_ms', 'full_cycle_ms', 'fingerprint_ms_excluded'}
reference = [{k:v for k,v in result.items() if k not in excluded_timing} for result in baseline[0]['results']]
reference_checks=None
for run in baseline + candidate:
    raw = (base / 'runs' / run['id'] / 'stdout.log').read_text(encoding='utf-8')
    results = [json.loads(line.split('AUTORESEARCH_RESULT ',1)[1]) for line in raw.splitlines() if 'AUTORESEARCH_RESULT ' in line]
    assert results == run['results'], run['id']
    assert len(results)==3 and [v['fixture_id'] for v in results]==plan['expected_fixtures']
    assert all(v['iteration']==plan['expected_stops'][v['fixture_id']] and v['target_met'] is True for v in results)
    checks=[json.loads(line.split('AUTORESEARCH_STAGE ',1)[1]) for line in raw.splitlines() if 'AUTORESEARCH_STAGE ' in line]
    checks=[{k:s[k] for k in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']} for s in checks if s.get('stage')=='convergence_check']
    assert len(checks)==plan['expected_convergence_records_per_run']==23,run['id']
    for fixture in plan['expected_fixtures']:
        assert [v['iteration'] for v in checks if v['fixture_id']==fixture]==list(range(20,plan['expected_stops'][fixture]+1,20))
    if reference_checks is None: reference_checks=checks
    else: assert checks==reference_checks,run['id']
    assert [{k:v for k,v in result.items() if k not in excluded_timing} for result in results] == reference, run['id']
assessment = compare.summarize(baseline, candidate, compare.source_hashes(frozen))
failures = compare.rejection_reasons(assessment['performance'])
out = base / 'runs/E026-assessment'
out.mkdir(exist_ok=False)
source = base / 'runs/E026-build/candidate.patch'
target = base / 'runs/E026R1.patch'
assert not target.exists()
shutil.copyfile(source, target)
assert ar.sha256(target) == ar.sha256(source)
ar.atomic_json(out / 'logical-run-link.json', {
    'at': ar.now(), 'logical_candidate':'E026', 'actual_first_run':'E026R1',
    'actual_run_ids':candidate_ids, 'synthesized_measurement':False,
    'patch_alias':str(target), 'source_patch':str(source), 'patch_sha256':ar.sha256(source),
    'reason':'Existing comparison helper consumes a physical run ID; logical display row mirrors its outcome only.'})
command = [sys.executable,'-B','tools/postflop_compare.py','--id','E026-three-pair-comparison',
           '--candidate-id','E026R1','--baseline-runs',*baseline_ids,'--candidate-runs',*candidate_ids,'--warm-cache-cohort']
if failures: command.append('--reject')
ar.atomic_json(out / 'invocation.json', {'at':ar.now(),'command':command,'decision_gate_failures':failures,
    'script_sha256':ar.sha256(Path(__file__)),'protocol_sha256':ar.sha256(protocol)})
with (out / 'stdout.log').open('xb') as stdout, (out / 'stderr.log').open('xb') as stderr:
    result = subprocess.run(command,cwd=repo,stdout=stdout,stderr=stderr)
ar.atomic_json(out / 'exit.json', {'at':ar.now(),'returncode':result.returncode})
assert result.returncode == 0, (out / 'stderr.log').read_text(encoding='utf-8')
report = json.loads((base / 'comparisons/E026-three-pair-comparison/report.json').read_text(encoding='utf-8'))
assert report['performance'] == assessment['performance']
assert report['decision'] == ('rejected' if failures else 'qualifying')
print(json.dumps({'decision':report['decision'],'performance':report['performance'],'candidate_accepted':False,'deployment_changed':False},indent=2))
