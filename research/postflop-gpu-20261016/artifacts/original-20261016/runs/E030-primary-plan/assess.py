"""Assess every frozen primary measurement once; never accept a candidate."""
import hashlib, json, shutil, subprocess, sys
from pathlib import Path
repo = Path(r'X:\Dev\GTOpen-gpu-research-20261016')
here=Path(__file__).resolve().parent
seal=json.loads((here/'scripts-manifest.json').read_text(encoding='utf-8'))
authorization=json.loads((here/'authorization.json').read_text(encoding='utf-8'))

assert authorization['direct_up_fold_exact_pass'] is True
_direct_pin=authorization['prerequisites']['direct_up_fold_terminal_review']
_direct_path=Path(_direct_pin['path'])
assert _direct_path.resolve()==Path(r'S:\GTOpen-research\postflop-gpu-20261016\comparisons\E030-direct-independent-review\validation.json').resolve()
assert authorization['evidence_sha256'][str(_direct_path)]==_direct_pin['sha256']
assert __import__('hashlib').sha256(_direct_path.read_bytes()).hexdigest()==_direct_pin['sha256']
_direct=json.loads(_direct_path.read_text(encoding='utf-8'))
assert _direct['id']=='E030-direct' and _direct['verdict']=='PASS_EXACT_COMPLETE_UP_FOLD_COMPARISON'
assert _direct['exactness_pass'] is True and _direct['numerical_validation']=='executed'
assert _direct['baseline_cuda_sha256']=='075651690d59ede225c17ff9674662e040d40460a5e2b5436fd6fa7d4f5d663b'
assert _direct['candidate_cuda_sha256']=='5ee2ffbf0daeb7447d69584f2f64bd2c13733c7be028e580cc3fd95c7196f829'
_prepared_path=Path(r'S:\GTOpen-research\postflop-gpu-20261016\runs\E030-fold-card-order-exact\prepared-manifest.json')
assert _direct['prepared_manifest_sha256']==authorization['evidence_sha256'][str(_prepared_path)]
assert __import__('hashlib').sha256(_prepared_path.read_bytes()).hexdigest()==_direct['prepared_manifest_sha256']
assert _direct['production_threads']==128 and _direct['block_shapes']==[128,16,32,64,256]
assert _direct['each_pair_same_block_shape'] is True
assert _direct['comparison_pairs']==180 and _direct['kernel_launches']==360
assert _direct['performance_measurement'] is False and _direct['candidate_accepted'] is False
def pinned_sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
assert authorization['evidence_sha256'][str(here/'scripts-manifest.json')]==pinned_sha(here/'scripts-manifest.json')
for name,h in seal['script_sha256'].items():assert pinned_sha(here/name)==h,name
for path,h in seal['reference_sha256'].items():assert pinned_sha(path)==h,path
for path,h in authorization['evidence_sha256'].items():assert pinned_sha(path)==h,path
sys.path.insert(0, str(repo / 'tools'))
import postflop_autoresearch as ar
import postflop_compare as compare
base = ar.RESEARCH
assert not (base / 'gpu-run.lock').exists()
protocol = base / 'runs/E030-primary-plan/protocol.json'
assert ar.sha256(protocol) == '9fab8ec1104ebe797dc2c56c9d17293dc82914f0d6b7b968540454b21dd3a0ac'
plan = json.loads(protocol.read_text(encoding='utf-8'))
here=protocol.parent
authorization=json.loads((here/'authorization.json').read_text(encoding='utf-8'))
assert authorization['evidence_sha256'][str(here/'scripts-manifest.json')]==ar.sha256(here/'scripts-manifest.json')
seal=json.loads((here/'scripts-manifest.json').read_text(encoding='utf-8'))
for name,h in seal['script_sha256'].items(): assert ar.sha256(here/name)==h,name
for path,h in seal['reference_sha256'].items(): assert ar.sha256(Path(path))==h,path
completed = json.loads((base / 'runs/E030-primary-execution/complete.json').read_text(encoding='utf-8'))
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
out = base / 'runs/E030-assessment'
out.mkdir(exist_ok=False)
source = base / 'runs/E030-build/candidate.patch'
target = base / 'runs/E030R1.patch'
assert not target.exists()
shutil.copyfile(source, target)
assert ar.sha256(target) == ar.sha256(source)
ar.atomic_json(out / 'logical-run-link.json', {
    'at': ar.now(), 'logical_candidate':'E030', 'actual_first_run':'E030R1',
    'actual_run_ids':candidate_ids, 'synthesized_measurement':False,
    'patch_alias':str(target), 'source_patch':str(source), 'patch_sha256':ar.sha256(source),
    'reason':'Existing comparison helper consumes a physical run ID; logical display row mirrors its outcome only.'})
command = [sys.executable,'-B','tools/postflop_compare.py','--id','E030-three-pair-comparison',
           '--candidate-id','E030R1','--baseline-runs',*baseline_ids,'--candidate-runs',*candidate_ids,'--warm-cache-cohort']
if failures: command.append('--reject')
ar.atomic_json(out / 'invocation.json', {'at':ar.now(),'command':command,'decision_gate_failures':failures,
    'script_sha256':ar.sha256(Path(__file__)),'protocol_sha256':ar.sha256(protocol)})
with (out / 'stdout.log').open('xb') as stdout, (out / 'stderr.log').open('xb') as stderr:
    result = subprocess.run(command,cwd=repo,stdout=stdout,stderr=stderr)
ar.atomic_json(out / 'exit.json', {'at':ar.now(),'returncode':result.returncode})
assert result.returncode == 0, (out / 'stderr.log').read_text(encoding='utf-8')
report = json.loads((base / 'comparisons/E030-three-pair-comparison/report.json').read_text(encoding='utf-8'))
assert report['performance'] == assessment['performance']
assert report['decision'] == ('rejected' if failures else 'qualifying')
print(json.dumps({'decision':report['decision'],'performance':report['performance'],'candidate_accepted':False,'deployment_changed':False},indent=2))
