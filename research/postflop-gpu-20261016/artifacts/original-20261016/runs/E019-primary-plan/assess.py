"""Assess every frozen primary measurement once; never accept a candidate."""
import json, shutil, subprocess, sys
from pathlib import Path
repo = Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0, str(repo / 'tools'))
import postflop_autoresearch as ar
import postflop_compare as compare
base = ar.RESEARCH
assert not (base / 'gpu-run.lock').exists()
protocol = base / 'runs/E019-primary-plan/protocol.json'
assert ar.sha256(protocol) == 'c74dfd6cbd57804c1fd8e9bad65744a8ab2b525f3e6aa230b5ed46c6959b1fba'
plan = json.loads(protocol.read_text(encoding='utf-8'))
completed = json.loads((base / 'runs/E019-primary-execution/complete.json').read_text(encoding='utf-8'))
assert completed['order'] == plan['order']
baseline_ids = [p['baseline'] for p in plan['pairs']]
candidate_ids = [p['candidate'] for p in plan['pairs']]
baseline = [compare.load_run(r)[0] for r in baseline_ids]
candidate = [compare.load_run(r)[0] for r in candidate_ids]
frozen = json.loads((base / 'baseline-manifest.json').read_text(encoding='utf-8'))
assessment = compare.summarize(baseline, candidate, compare.source_hashes(frozen))
failures = compare.rejection_reasons(assessment['performance'])
out = base / 'runs/E019-assessment'
out.mkdir(exist_ok=False)
source = base / 'runs/E019-build/candidate.patch'
target = base / 'runs/E019R1.patch'
assert not target.exists()
shutil.copyfile(source, target)
assert ar.sha256(target) == ar.sha256(source)
ar.atomic_json(out / 'logical-run-link.json', {
    'at': ar.now(), 'logical_candidate':'E019', 'actual_first_run':'E019R1',
    'actual_run_ids':candidate_ids, 'synthesized_measurement':False,
    'patch_alias':str(target), 'source_patch':str(source), 'patch_sha256':ar.sha256(source),
    'reason':'Existing comparison helper consumes a physical run ID; logical display row mirrors its outcome only.'})
command = [sys.executable,'-B','tools/postflop_compare.py','--id','E019-three-pair-comparison',
           '--candidate-id','E019R1','--baseline-runs',*baseline_ids,'--candidate-runs',*candidate_ids,'--warm-cache-cohort']
if failures: command.append('--reject')
ar.atomic_json(out / 'invocation.json', {'at':ar.now(),'command':command,'decision_gate_failures':failures,
    'script_sha256':ar.sha256(Path(__file__)),'protocol_sha256':ar.sha256(protocol)})
with (out / 'stdout.log').open('xb') as stdout, (out / 'stderr.log').open('xb') as stderr:
    result = subprocess.run(command,cwd=repo,stdout=stdout,stderr=stderr)
ar.atomic_json(out / 'exit.json', {'at':ar.now(),'returncode':result.returncode})
assert result.returncode == 0, (out / 'stderr.log').read_text(encoding='utf-8')
report = json.loads((base / 'comparisons/E019-three-pair-comparison/report.json').read_text(encoding='utf-8'))
assert report['performance'] == assessment['performance']
assert report['decision'] == ('rejected' if failures else 'qualifying')
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
    status = json.loads(ar.STATUS.read_text(encoding='utf-8'))
    source_row = next(r for r in status['experiments'] if r['id'] == 'E019R1')
    row = next(r for r in status['experiments'] if r['id'] == 'E019')
    for k in ['status','correctness','reason','qualification_summary']:
        row[k] = source_row[k]
    row.update(updated_at=ar.now(), stage='Primary screen complete; independent audit pending',
               details='All fixed runs retained. Logical row displays the assessment of physical runs E019R1/R2/R3. No acceptance or deployment.')
    for e in source_row['evidence']:
        if not any(x['url'] == e['url'] for x in row['evidence']): row['evidence'].append(e)
    status.update(updated_at=ar.now(), active_experiment=None,
        stage='Auditing E019 primary result',activity=report['reason'])
    ar.atomic_json(ar.STATUS,status)
print(json.dumps({'decision':report['decision'],'performance':report['performance']},indent=2))
