"""Verify immutable broader evidence; does not accept or deploy the candidate."""
import json, re, shutil, subprocess, sys
from pathlib import Path
repo=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0,str(repo/'tools'))
import postflop_autoresearch as ar
import postflop_compare as comp
subprocess.run([sys.executable,'tools/postflop_validate_controls.py','--id','E016-controls-comparison',
 '--baseline-runs','V000-state-baseline','V000-menu-baseline','V000-resume-baseline-r',
 '--candidate-runs','V016-state','V016-menu','V016-resume'],cwd=repo,check=True)
verified={}
def load(identity):
    report, provenance=comp.load_run(identity)
    assert report['status']=='measured' and report['returncode']==0
    manifest=report['binary_build_manifest']
    assert manifest['binary_hash_verified'] and manifest['data']['binary_sha256']==report['binary_sha256']
    checks=[(Path(provenance['path']),provenance['sha256']),
            (Path(report['command'][0]),report['binary_sha256']),
            (Path(manifest['path']),manifest['sha256']),
            (ar.RESEARCH/'runs'/identity/'stdout.log',report['stdout_sha256'])]
    for path,expected in checks:
        actual=ar.sha256(path);assert actual==expected.lower(),str(path)
        verified[str(path)]=actual
    return report
def publish(identity,data):
    target=ar.RESEARCH/'comparisons'/identity/'report.json'
    assert not target.exists()
    ar.atomic_json(target,data)
    public=ar.DASHBOARD/'evidence'/identity/'report.json'
    public.parent.mkdir(parents=True,exist_ok=True);assert not public.exists()
    shutil.copyfile(target,public)
    return {'label':identity,'url':f'evidence/{identity}/report.json'}
base,candidate=load('V016-f32-reference'),load('V016-f32-candidate')
for run in (base,candidate):
    assert run['test_pass_count']==1
    assert run['command'][1:]==['postflop_complete_cycle','--nocapture','--test-threads=1','--ignored']
    env=run['environment']
    assert env['POSTFLOP_AUTORESEARCH_STORAGE']=='f32' and env['POSTFLOP_AUTORESEARCH_PROFILE']=='0'
    assert env['POSTFLOP_AUTORESEARCH_FIXTURE'] is None and env['RAYON_NUM_THREADS']=='16'
    assert [r['fixture_id'] for r in run['results']]==list(comp.FIXTURES)
    raw=(ar.RESEARCH/'runs'/run['id']/'stdout.log').read_text(encoding='utf-8')
    records=[json.loads(line.split('AUTORESEARCH_RESULT ',1)[1]) for line in raw.splitlines() if 'AUTORESEARCH_RESULT ' in line]
    assert records==run['results']
    hashes=comp.source_hashes(run['binary_build_manifest']['data'])
    for name in comp.EVALUATOR_FILES:
        assert hashes[name]==run['provenance']['benchmark_sha256'][name].lower()
fixtures=[]
for a,b in zip(base['results'],candidate['results']):
    timing=set(comp.TIMINGS)|{'fingerprint_ms_excluded'}
    assert {k:v for k,v in a.items() if k not in timing}=={k:v for k,v in b.items() if k not in timing}
    assert all(a[k]==b[k] for k in comp.EXACT_FIELDS)
    assert a['storage']=='f32' and a['target_met'] and a['target_pct']==0.3 and a['check_every']==20 and a['max_iterations']==400
    fixtures.append({'fixture':a['fixture_id'],'fingerprint':a['fingerprint'],'iteration':a['iteration'],
                     'exploit_bits':a['exploit_bits'],'all_nontiming_fields_equal':True})
f32={'status':'pass','created_at':ar.now(),'scope':'Full F32 state/config/exploitability and stopping equivalence; no F32 performance qualification',
     'baseline_run':base['id'],'candidate_run':candidate['id'],'fixtures':fixtures,
     'verified_artifacts':[{'path':p,'sha256':h} for p,h in verified.items()],'performance_claim':False}
links=[publish('E016-f32-comparison',f32)]
controls=[('V016-continuation-invalidation','gpu::tests::paired_reach_reuse_continuation_invalidates_before_validation_and_changed_roots'),
          ('V016-continuation-paging','paging_preserves_resident_trajectories_and_rejects_invalid_inputs'),
          ('V016-continuation-rejection','symmetric_continuation_rejects_unsupported_inputs_without_mutation'),
          ('V016-continuation-stored','gpu::continuation::storage::device_tests::direct_gpu_storage_preserves_720_full_state_passes')]
checks=[]
for identity,test in controls:
    report=load(identity)
    assert report['test_pass_count']==1 and report['command'][1:]==[test,'--nocapture','--test-threads=1']
    raw=(ar.RESEARCH/'runs'/identity/'stdout.log').read_text(encoding='utf-8')
    assert '1 passed; 0 failed; 0 ignored' in raw and test in raw
    checks.append({'id':identity,'test':test,'passed':1,'failed':0})
paging=(ar.RESEARCH/'runs/V016-continuation-paging/stdout.log').read_text(encoding='utf-8')
assert '160 alternating board/player sweeps' in paging
stored=(ar.RESEARCH/'runs/V016-continuation-stored/stdout.log').read_text(encoding='utf-8')
passes=[json.loads(line.split('GPU_STORED_PASS ',1)[1]) for line in stored.splitlines() if 'GPU_STORED_PASS ' in line]
summary=[json.loads(line.split('GPU_STORED_SUMMARY ',1)[1]) for line in stored.splitlines() if 'GPU_STORED_SUMMARY ' in line]
assert len(passes)==720 and all(p['passed'] for p in passes) and len(summary)==1
assert summary[0]['passes']==720 and all(summary[0][k] for k in ('full_device_arrays_bitwise_equal','restored_arrays_bitwise_equal','values_bitwise_equal'))
environment=ar.RESEARCH/'runs/V016-feature-environment.json'
verified[str(environment)]=ar.sha256(environment)
features={'status':'pass','created_at':ar.now(),'scope':'Selected continuation lifecycle and workspace correctness, no performance claim or forced SSD-spill coverage',
          'checks':checks,'paging_exact_sweeps':160,'stored_exact_passes':720,'stored_summary':summary[0],
          'environment_evidence':str(environment),'verified_artifacts':[{'path':p,'sha256':h} for p,h in verified.items()],
          'accepted':False,'deployed':False}
links.append(publish('E016-feature-controls-comparison',features))
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
    status=json.loads(ar.STATUS.read_text(encoding='utf-8'))
    row=next(e for e in status['experiments'] if e['id']=='E016')
    row['correctness']='pass'
    row['reason']='Primary screen: 4.1126% lower complete-cycle time versus E015. Full F32, 160 saved-state/menu/resume snapshots, 84 solver unit tests, six GPU tests and four continuation controls passed. Final independent audit and cumulative comparison pending.'
    row['evidence']+=links
    status.update(updated_at=ar.now(),stage='E016 broader correctness checks passed',activity='Fresh original-baseline comparison and final evidence audit are next. The accepted headline remains E015 until qualification closes.')
    ar.atomic_json(ar.STATUS,status)
print(json.dumps({'f32':'pass','continuation_controls':4,'paging_exact_sweeps':160,'stored_exact_passes':720}))
