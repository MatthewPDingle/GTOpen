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
base = ar.RESEARCH
assert not (base / 'gpu-run.lock').exists()
protocol = base / 'runs/E034-primary-plan/protocol.json'
assert ar.sha256(protocol) == 'UNSEALED_PROTOCOL_SHA256'
plan = json.loads(protocol.read_text(encoding='utf-8'))
here=protocol.parent
authorization=json.loads((here/'authorization.json').read_text(encoding='utf-8'))
assert authorization['evidence_sha256'][str(here/'scripts-manifest.json')]==ar.sha256(here/'scripts-manifest.json')
seal=json.loads((here/'scripts-manifest.json').read_text(encoding='utf-8'))
for name,h in seal['script_sha256'].items(): assert ar.sha256(here/name)==h,name
for path,h in seal['reference_sha256'].items(): assert ar.sha256(Path(path))==h,path
completed = json.loads((base / 'runs/E034-primary-execution/complete.json').read_text(encoding='utf-8'))
assert completed['order'] == plan['order']
def verify_policy_markers(raw, candidate, plan):
    lines = raw.splitlines()
    assert 'E033_CACHE_CLEANUP_ERROR' not in raw, 'Cleanup failure marker'
    policy = [(i, json.loads(line.split('E033_CACHE_POLICY ', 1)[1]))
              for i, line in enumerate(lines) if 'E033_CACHE_POLICY ' in line]
    if not candidate:
        assert policy == [], 'Baseline unexpectedly contains candidate policy markers'
        return []
    assert len(policy) == 6, 'Require exactly three enabled and three clean markers'
    stages = [(i, json.loads(line.split('AUTORESEARCH_STAGE ', 1)[1]))
              for i, line in enumerate(lines) if 'AUTORESEARCH_STAGE ' in line]
    verified = []
    for fixture, owned_bytes, window_bytes in [('rainbow',5387252,5387136),('two-tone',5387252,5387136),('river',132,128)]:
        def position(stage):
            found = [i for i, row in stages if row.get('fixture_id') == fixture and row.get('stage') == stage]
            assert len(found) == 1, (fixture, stage, found)
            return found[0]
        start, build, ready, stop = [position(s) for s in ['fixture_start','build_complete','gpu_ready','timing_complete']]
        checks = [(i,r) for i,r in stages if r.get('fixture_id')==fixture and r.get('stage')=='convergence_check']
        assert checks and checks[-1][1]['iteration']==plan['expected_stops'][fixture]
        assert start < build < ready < checks[-1][0] < stop
        rows = [(i,r) for i,r in policy if start < i < stop]
        assert len(rows)==2 and [r['stage'] for _,r in rows]==['enabled','clean'], fixture
        assert build < rows[0][0] < ready and checks[-1][0] < rows[1][0] < stop, fixture
        for _, row in rows:
            assert set(row)=={'stage','enabled','owned_bytes','window_bytes','normalized_lines','cleanup_complete','errors'}
            assert row['enabled'] is True and row['errors'] is False, fixture
            assert row['owned_bytes']==owned_bytes and row['window_bytes']==window_bytes, fixture
            assert row['normalized_lines']==(0 if row['stage']=='enabled' else window_bytes//128), fixture
            assert row['cleanup_complete'] is (row['stage']=='clean'), fixture
            verified.append({'fixture_id':fixture,**row})
    assert [r for _,r in policy]==[{k:v for k,v in r.items() if k!='fixture_id'} for r in verified], 'Policy markers outside fixed fixture order'
    return verified



baseline_ids = [p['baseline'] for p in plan['pairs']]
candidate_ids = [p['candidate'] for p in plan['pairs']]
baseline = [compare.load_run(r)[0] for r in baseline_ids]
candidate = [compare.load_run(r)[0] for r in candidate_ids]
frozen = json.loads((base / 'baseline-manifest.json').read_text(encoding='utf-8'))
# The shared helper checks an explicit tuple; the protocol requires every non-timing field.
excluded_timing = {'build_ms', 'init_ms', 'solve_ms', 'readback_ms', 'full_cycle_ms', 'fingerprint_ms_excluded'}
reference = [{k:v for k,v in result.items() if k not in excluded_timing} for result in baseline[0]['results']]
reference_checks=None
policy_evidence={}
for run in baseline + candidate:
    raw = (base / 'runs' / run['id'] / 'stdout.log').read_text(encoding='utf-8')
    policy_evidence[run['id']]=verify_policy_markers(raw,run['id'] in candidate_ids,plan)
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
out = base / 'runs/E034-assessment'
out.mkdir(exist_ok=False)
ar.atomic_json(out/'policy-markers.json',policy_evidence)
source = base / 'runs/E034-build/candidate.patch'
target = base / 'runs/E034R1.patch'
assert not target.exists()
shutil.copyfile(source, target)
assert ar.sha256(target) == ar.sha256(source)
ar.atomic_json(out / 'logical-run-link.json', {
    'at': ar.now(), 'logical_candidate':'E034', 'actual_first_run':'E034R1',
    'actual_run_ids':candidate_ids, 'synthesized_measurement':False,
    'patch_alias':str(target), 'source_patch':str(source), 'patch_sha256':ar.sha256(source),
    'reason':'Existing comparison helper consumes a physical run ID; logical display row mirrors its outcome only.'})
command = [sys.executable,'-B','tools/postflop_compare.py','--id','E034-three-pair-comparison',
           '--candidate-id','E034R1','--baseline-runs',*baseline_ids,'--candidate-runs',*candidate_ids,'--warm-cache-cohort']
if failures: command.append('--reject')
ar.atomic_json(out / 'invocation.json', {'at':ar.now(),'command':command,'decision_gate_failures':failures,
    'script_sha256':ar.sha256(Path(__file__)),'protocol_sha256':ar.sha256(protocol)})
with (out / 'stdout.log').open('xb') as stdout, (out / 'stderr.log').open('xb') as stderr:
    result = subprocess.run(command,cwd=repo,stdout=stdout,stderr=stderr)
ar.atomic_json(out / 'exit.json', {'at':ar.now(),'returncode':result.returncode})
assert result.returncode == 0, (out / 'stderr.log').read_text(encoding='utf-8')
report = json.loads((base / 'comparisons/E034-three-pair-comparison/report.json').read_text(encoding='utf-8'))
assert report['performance'] == assessment['performance']
assert report['decision'] == ('rejected' if failures else 'qualifying')
print(json.dumps({'decision':report['decision'],'performance':report['performance'],'candidate_accepted':False,'deployment_changed':False},indent=2))
