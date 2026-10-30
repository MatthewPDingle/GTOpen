"""Publish a reviewed qualification decision; preserve the raw comparisons."""
import json, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, r'X:\Dev\GTOpen-gpu-research-20261016\tools')
import postflop_autoresearch as ar
ROOT=ar.RESEARCH
OUT=ROOT/'comparisons/E015-qualification'
OUT.mkdir(exist_ok=False)
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def artifact(path): return {'path':str(path),'sha256':ar.sha256(path)}
primary=read(ROOT/'comparisons/E015-three-pair-comparison/report.json')
cumulative=read(ROOT/'comparisons/E015-cumulative-comparison/report.json')
review=read(ROOT/'comparisons/E015-independent-review/validation.json')
creview=read(ROOT/'comparisons/E015-independent-review/cumulative-validation.json')
controls=read(ROOT/'comparisons/E015-controls-comparison/report.json')
f32=read(ROOT/'comparisons/E015-f32-comparison/report.json')
for report in (primary,cumulative):
    assert report['performance']['aggregate_gate_met']
    assert not report['performance']['fixture_regression_guard']['failed']
    assert not report['excluded_runs']
    assert all(f['exact_screen']['status']=='pass' for f in report['fixtures'])
assert review['exact_records']['all_nontiming_fields_exact']
assert creview['exact_records']['all_nontiming_fields_equal']
assert controls['status']=='pass' and controls['total_snapshots_each']==160
assert f32['status']=='pass' and all(f['all_exact_fields_equal'] for f in f32['fixtures'])
assert '84 passed; 0 failed; 4 ignored' in (ROOT/'runs/V015-unit/stdout.log').read_text()
assert '6 passed; 0 failed' in (ROOT/'runs/V015-gpu/stdout.log').read_text()
for name in ('validation.json','summary.md','cumulative-validation.json'):
    source=ROOT/'comparisons/E015-independent-review'/name
    target=ar.DASHBOARD/'evidence/E015-independent-review'/name
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists(): assert ar.sha256(target)==ar.sha256(source)
    else: shutil.copyfile(source,target)
source_hash=ar.sha256(ar.REPO/'crates/solver/src/gpu/mod.rs')
assert source_hash=='7de2cd46ef93742c603042306cfe2ad08a83ff52a2be1123efd9d201aca15f1a'
assert ar.sha256(ar.APP/'crates/solver/src/gpu/mod.rs')==source_hash
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ar.REPO,text=True).strip()
assert commit=='e868cfbb125002216f25046af2d88b22a697b2fd'
main_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ar.APP,text=True).strip()
scope=('Three alternating original-baseline/candidate pairs; sum of per-fixture medians. '
       'Fresh compressed native solves on RTX 5090 with a warm driver cache: tree construction, GPU initialization '
       'including runtime NVRTC/JIT, fixed-quality solving/checks and full readback. Cargo builds, fingerprinting, '
       'destruction after fingerprinting, browser/API latency and disk saving excluded. '
       'E004 improves initialization; E015 reduces repeated reach propagation during solving. '
       'F32 and saved/resumed correctness passed; their performance and cold-start performance are not qualified.')
evidence=[
 {'label':'Fresh original-baseline cumulative comparison','url':'evidence/E015-cumulative-comparison/report.json'},
 {'label':'Incremental comparison against E004','url':'evidence/E015-three-pair-comparison/report.json'},
 {'label':'Independent primary and correctness audit','url':'evidence/E015-independent-review/validation.json'},
 {'label':'Independent cumulative audit','url':'evidence/E015-independent-review/cumulative-validation.json'},
 {'label':'160 exact saved-state/menu/resume snapshots','url':'evidence/E015-controls-comparison/report.json'},
 {'label':'Full F32 exact comparison','url':'evidence/E015-f32-comparison/report.json'},
 {'label':'84 solver unit tests','url':'evidence/V015-unit/stdout.log'},
 {'label':'Six GPU integration tests','url':'evidence/V015-gpu/stdout.log'},
]
inputs=[ROOT/'comparisons'/n for n in (
 'E015-three-pair-comparison/report.json','E015-cumulative-comparison/report.json',
 'E015-independent-review/validation.json','E015-independent-review/summary.md',
 'E015-independent-review/cumulative-validation.json','E015-controls-comparison/report.json',
 'E015-f32-comparison/report.json')]
inputs += [ROOT/'binaries/E015-postflop_autoresearch.exe',ROOT/'binaries/E015-postflop_autoresearch.manifest.json',
           ROOT/'runs/V015-unit/stdout.log',ROOT/'runs/V015-gpu/stdout.log']
report={'id':'E015','accepted_at':ar.now(),'status':'validated','scope':scope,
        'performance':cumulative['performance'],'incremental_performance':primary['performance'],
        'pairs':cumulative['pairs'],'incremental_pairs':primary['pairs'],
        'controls_snapshots_each':160,'unit_tests_passed':84,'unit_tests_ignored':4,
        'gpu_integration_tests_passed':6,'f32_whole_arena_exact':True,
        'independent_source_review':'PASS: paired-only scope, kernel width guards, graph order and unchanged standalone refresh independently checked; main production sources match research.',
        'research_commit':commit,'main_commit':main_commit,'mod_rs_sha256':source_hash,
        'binary_sha256':ar.sha256(ROOT/'binaries/E015-postflop_autoresearch.exe'),
        'evidence':evidence,'inputs':[artifact(p) for p in inputs],
        'interpretation':['Cumulative gain is measured against the original implementation in a fresh cohort; percentages are not added.',
                          'Absolute times differ across cohorts; cross-cohort subtraction and a cause for the shift are not established.',
                          'Performance qualification is scoped to the three fixed compressed fixtures, hardware and protocol. No statistical significance or arbitrary-tree guarantee is claimed.'],
        'deployed':False,'deployment':'Automatic approval review blocked live executable replacement/restart with generic reason blocked by policy. Main source integrated; isolated server validation is separate.'}
ar.atomic_json(OUT/'report.json',report)
target=ar.DASHBOARD/'evidence/E015-qualification/report.json'
target.parent.mkdir(parents=True,exist_ok=True)
assert not target.exists()
shutil.copyfile(OUT/'report.json',target)
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
    status=read(ar.STATUS)
    ar.atomic_json(OUT/'status-before.json',status)
    performance=cumulative['performance']; measured=cumulative['created_at']
    accepted={'status':'validated','scope':'complete_run','candidate_id':'E015',
              'baseline_ms':performance['baseline_full_cycle_ms'],'best_ms':performance['candidate_full_cycle_ms'],
              'correctness':'pass','measured_at':measured,'method':scope}
    status['baseline']={'id':'B038 / B039 / B040','commit':'bad4779b','measured_at':measured,'full_cycle_definition':scope}
    status['accepted_complete_run']=accepted
    assert not any(h['candidate_id']=='E015' for h in status['accepted_history'])
    status['accepted_history'].append({**accepted,'at':report['accepted_at']})
    status['validation']={'status':'pass','summary':'E015: exact complete-state results in both three-pair cohorts; full F32 comparison; 160 saved-state/menu/resume snapshots; 84 solver unit tests and six GPU integration tests passed.'}
    status['deployment']={'status':'blocked','candidate_id':'E015','commit':main_commit,
        'summary':'Automatic approval review rejected replacing/restarting the live server: "blocked by policy" (no further reason). Main source includes E004 and E015; isolated server validation is in progress. The live executable remains the original version.'}
    for fixture in status['fixtures']:
        item=next(f for f in cumulative['fixtures'] if f['fixture_id']==fixture['id'])
        fingerprint=item['exact_screen']['fingerprint']
        fixture['baseline']={'full_cycle_ms':item['baseline']['full_cycle_ms']['median_ms'],
            'solve_ms':item['baseline']['solve_ms']['median_ms'],'fingerprint':fingerprint,'repetitions':3,'provisional':False}
        fixture['best']={'status':'accepted','candidate_id':'E015','full_cycle_ms':item['candidate']['full_cycle_ms']['median_ms'],
            'solve_ms':item['candidate']['solve_ms']['median_ms'],'fingerprint':fingerprint}
        fixture['correctness']={'status':'pass','details':'Exact state/configuration and stopping iterations in both cohorts; F32, saved-state, menu, resume and GPU controls passed.'}
        urls={e['url'] for e in fixture['evidence']}
        fixture['evidence']=[e for e in evidence[:6] if e['url'] not in urls]+fixture['evidence']
    row=next(e for e in status['experiments'] if e['id']=='E015')
    row.update(status='accepted',correctness='pass',stage='Qualified and integrated into main source',updated_at=ar.now(),
        full_cycle_ms=performance['candidate_full_cycle_ms'],baseline_full_cycle_ms=performance['baseline_full_cycle_ms'],
        solve_ms=sum(f['candidate']['solve_ms']['median_ms'] for f in cumulative['fixtures']),
        timing_aggregation='Fresh original-baseline comparison: sum of per-fixture medians; individual raw measurements remain linked',
        reason='Validated 3.9828% incremental improvement versus E004; fresh original-baseline comparison gives 9.6192% cumulative complete-cycle improvement. All accuracy controls passed. Main source integrated; live deployment blocked.')
    row['qualification_summary']={'id':'E015-qualification','status':'validated','performance':performance,
        'incremental_performance':primary['performance'],'broader_validation':'pass','f32_storage':'pass','controls_snapshots_each':160}
    decision={'label':'Accepted qualification and scope','url':'evidence/E015-qualification/report.json'}
    row['evidence'] += [decision]+[e for e in evidence if e['url'] not in {x['url'] for x in row['evidence']}]
    status['evidence'] += [decision,evidence[3]]
    status['updated_at']=ar.now()
    ar.atomic_json(ar.STATUS,status)
    ar.atomic_json(OUT/'status-after.json',status)
print(json.dumps({'accepted':'E015','cumulative_gain_pct':performance['observed_gain_pct'],'incremental_gain_pct':primary['performance']['observed_gain_pct'],'qualification_sha256':ar.sha256(OUT/'report.json')}))
