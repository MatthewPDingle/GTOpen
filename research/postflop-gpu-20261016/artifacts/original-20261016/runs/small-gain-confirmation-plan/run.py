"""Root only: five unit screens, then exactly128 frozen evaluator processes."""
import shutil, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
assert len(sys.argv)==2,'Provide root authorization SHA256'
AUTH=sys.argv[1];verify(AUTH);custody()
assert not (ROOT/'gpu-run.lock').exists(),'Compiler/native work remains active'
bins=binaries()
assert read(BUILD/'complete.json')['authorization_sha256']==AUTH
all_ids=S['unit_order']+S['measurement_order']
assert len(all_ids)==133 and len(set(all_ids))==133
status=read(ar.STATUS)
for identity in all_ids:
    assert not (ROOT/'runs'/identity).exists(),identity
    assert not any(x['id']==identity for x in status['experiments']),identity
assert not EXEC.exists();EXEC.mkdir()
save(EXEC/'invocation.json',{'at':now(),'authorization_sha256':AUTH,'protocol_sha256':sha(HERE/'protocol.json'),'schedule_sha256':sha(HERE/'schedule.json'),'build_complete_sha256':sha(BUILD/'complete.json'),'source_sha256':BASE,'binary_pins':{f'{c}/{n}':v for (c,n),v in bins.items()},'all_native_ids_previously_absent':True,'all_compilers_terminal_before_any_native':True,'source_vs_binary':'Current checkout is accepted E020; candidate build manifests independently identify frozen candidate source.'})
anchor=exact_raw(P['anchor'])
reference_env=None;reference_gpu=None

def run_one(identity,c,ordinary=False):
    global reference_env,reference_gpu
    verify(AUTH);custody()
    assert shutil.disk_usage(ROOT).free>=P['run_disk_reserve_gib']*1024**3
    b=bins[(c,'solver' if ordinary else 'postflop_autoresearch')]
    pin(b['path'],b['sha256']);pin(b['manifest'],b['manifest_sha256'])
    command=[sys.executable,'-B','tools/postflop_autoresearch.py','--id',identity,'--title',f'Fresh confirmation {c} '+('unit screen' if ordinary else 'complete cycle'),'--kind','validation' if ordinary else ('baseline' if c=='E020' else 'candidate'),'--binary',b['path'],'--build-manifest',b['manifest'],'--test','*' if ordinary else 'postflop_complete_cycle']
    if ordinary:command.append('--not-ignored')
    # The frozen ar runner alone acquires/holds gpu-run.lock around this child tree.
    child(command,EXEC,identity,env(),P['run_timeout_seconds'])
    pin(b['path'],b['sha256']);pin(b['manifest'],b['manifest_sha256'])
    custody()
    if ordinary:unit_check(c)
    else:
        report=read(ROOT/'runs'/identity/'report.json')
        compare.validate_run(report,{})
        assert report['binary_sha256']==b['sha256'] and report['binary_build_manifest']['sha256']==b['manifest_sha256']
        assert report['provenance']['source_sha256']==BASE
        assert report['binary_build_manifest']['data']['source_sha256']==expected(c)
        assert exact_raw(identity)==anchor,('Exact result/checkpoint mismatch',identity)
        if reference_env is None:reference_env=report['environment'];reference_gpu=compare.gpu_identity(report)
        assert report['environment']==reference_env and compare.gpu_identity(report)==reference_gpu
    print('Completed',identity,flush=True)

for c in P['build_order']:run_one(P['arms'][c]['unit_id'],c,True)
save(EXEC/'units-complete.json',{'at':now(),'unit_order':S['unit_order'],'all_passed':True,'build_complete_sha256':sha(BUILD/'complete.json'),'evidence_sha256':{str(ROOT/'runs'/i/'report.json'):sha(ROOT/'runs'/i/'report.json') for i in S['unit_order']}})
for pair in S['pairs']:
    for identity in pair['order']:run_one(identity,'E020' if identity==pair['baseline'] else pair['candidate'])
custody()
save(EXEC/'complete.json',{'at':now(),'unit_order':S['unit_order'],'measurement_order':S['measurement_order'],'comparison_pairs':64,'evaluator_processes':128,'fixture_results':384,'convergence_records':2944,'units_complete_sha256':sha(EXEC/'units-complete.json'),'schedule_sha256':sha(HERE/'schedule.json'),'authorization_sha256':AUTH,'all_samples_retained':True,'candidate_accepted':False})
print('Fixed family complete; assessment and independent audit remain required.',flush=True)
