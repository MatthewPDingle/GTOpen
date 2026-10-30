"""Fixed E038 unit/upload controls followed by one three-pair primary screen."""
import json,os,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'))
import common as old
ar=old.ar
read,sha,pin,save,now,child=old.read,old.sha,old.pin,old.save,old.now,old.child
assert len(sys.argv)==2;pin(HERE/'protocol.json',sys.argv[1]);P=read(HERE/'protocol.json')
ROOT=ar.RESEARCH;OUT=ROOT/'runs/E038-native-execution';BASE=read(P['baseline']['path'])['source_sha256']

def verify():
    pin(HERE/'protocol.json',sys.argv[1])
    for p,h in P['input_sha256'].items():pin(p,h)
    old.custody()

def binary(stem):
    path=ROOT/'binaries'/(stem+'.exe');mp=path.with_suffix('.manifest.json');m=read(mp)
    pin(path,m['binary_sha256']);assert m['protocol_sha256']==sys.argv[1]
    assert m['source_sha256']==BASE|{'crates/solver/src/gpu/arena.rs':next(p['source_sha256'] for p in P['build_phases'] if stem in p['outputs'].values())}
    return {'path':str(path),'sha256':sha(path),'manifest':str(mp),'manifest_sha256':sha(mp),'data':m}

verify();assert not (ROOT/'gpu-run.lock').exists()
built=read(ROOT/'runs/E038-build/complete.json');assert built['all_compilers_terminal'] and built['protocol_sha256']==sys.argv[1]
for p,h in built['evidence_sha256'].items():pin(p,h)
assert not OUT.exists();OUT.mkdir()
ids=P['control_ids']+P['measurement_order']
status=read(ar.STATUS)
for identity in ids:
    assert not (ROOT/'runs'/identity).exists(),identity
    assert not any(e['id']==identity for e in status['experiments']),identity
save(OUT/'invocation.json',{'at':now(),'protocol_sha256':sys.argv[1],'build_complete_sha256':sha(ROOT/'runs/E038-build/complete.json'),'all_native_ids_previously_absent':True,'all_compilers_terminal':True,'native_script_sha256':sha(HERE/'native.py')})

def run_one(identity,b,test,ordinary=False,extra=None):
    verify();pin(b['path'],b['sha256']);pin(b['manifest'],b['manifest_sha256'])
    command=[sys.executable,'-B','tools/postflop_autoresearch.py','--id',identity,'--title','E038 '+identity,'--kind','validation' if identity in P['control_ids'] else ('baseline' if identity.startswith('B') else 'candidate'),'--binary',b['path'],'--build-manifest',b['manifest'],'--test',test]
    if ordinary:command.append('--not-ignored')
    e=old.env();e.pop('E038_CONTROL_DIR',None);e.pop('E038_CONTROL_EXPECT_FAST_PATH',None)
    if extra:e.update(extra)
    child(command,OUT,identity,e,1200)
    verify();r=read(ROOT/'runs'/identity/'report.json')
    pin(ROOT/'runs'/identity/'stdout.log',r['stdout_sha256'])
    assert r['returncode']==0 and r['status']=='measured' and r['binary_sha256']==b['sha256']
    assert r['provenance']['source_sha256']==BASE
    assert r['binary_build_manifest']['sha256']==b['manifest_sha256'] and r['binary_build_manifest']['binary_hash_verified'] is True
    assert r['binary_build_manifest']['data']==b['data']
    print('Completed',identity,flush=True)
    return r,(ROOT/'runs'/identity/'stdout.log').read_text(encoding='utf-8')

unit=binary('E038-solver')
r,raw=run_one('V038-unit',unit,'*',True)
assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)==[('85','0','4','0','0')]
assert 'test gpu::arena::tests::zero_upload_accepts_all_u16_quants_with_positive_zero_scale ... ok' in raw
control_root=ROOT/'runs/E038-control-execution';assert not control_root.exists();control_root.mkdir()
for arm,flag,filtered in [('base','0',88),('candidate','1',89)]:
    b=binary('E038-control-'+arm+'-solver')
    identity='V038-'+arm+'-upload';dest=control_root/arm;assert not dest.exists()
    r,raw=run_one(identity,b,P['control_filter'],False,{'E038_CONTROL_DIR':str(dest),'E038_CONTROL_EXPECT_FAST_PATH':flag})
    assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)==[('1','0','0','0',str(filtered))]
    assert 'E038_CONTROL_CLEANUP_ERROR' not in raw
    records=[json.loads(line.split('E038_UPLOAD_CONTROL ',1)[1]) for line in raw.splitlines() if 'E038_UPLOAD_CONTROL ' in line]
    evidence=read(dest/'evidence.json')
    assert len(records)==3 and [x['stage'] for x in records]==['layout_complete','layout_complete','complete']
    assert records[-1]==evidence and len(evidence['layouts'])==2
    assert evidence['solve_iterations']==0 and evidence['performance_measurement'] is False and evidence['candidate_accepted'] is False
    assert len([p for p in dest.rglob('*') if p.is_file()])==27
    for case,label in zip(evidence['layouts'],['full','compact']):
        assert case['layout']==label and case['u16_zero_fast_path']==(flag=='1')
        assert all(case[k] is True for k in ['host_query_save_preserved','device_unchanged_after_readbacks','repeat_restores_first_readback','cleanup_complete'])
        assert len(case['files'])==13
        for f in case['files']:assert (dest/label/f['file']).stat().st_size==f['bytes']
        case.pop('u16_zero_fast_path')
    if arm=='base':reference=evidence
    else:assert evidence==reference,'control geometry/state summary mismatch'
files={p.relative_to(control_root/'base').as_posix():sha(p) for p in (control_root/'base').rglob('*') if p.is_file() and p.name!='evidence.json'}
assert len(files)==26
for name,h in files.items():pin(control_root/'candidate'/name,h)
save(control_root/'comparison.json',{'at':now(),'protocol_sha256':sys.argv[1],'exact_files':files,'file_count':26,'layouts':['full','compact'],'all_exact':True,'host_queries_and_saves_preserved':True,'performance_measurement':False,'candidate_accepted':False})
save(OUT/'controls-complete.json',{'at':now(),'unit_id':'V038-unit','control_ids':P['control_ids'][1:],'comparison_sha256':sha(control_root/'comparison.json'),'all_passed':True})
anchor=old.exact_raw('E020C1');baseline=P['baseline_binary'];baseline['data']=read(baseline['manifest'])
pin(baseline['path'],baseline['sha256']);pin(baseline['manifest'],baseline['manifest_sha256'])
assert baseline['data']['source_sha256']==BASE
candidate=binary('E038-postflop_autoresearch');environment=None;gpu=None
for identity in P['measurement_order']:
    b=baseline if identity.startswith('B') else candidate
    r,_=run_one(identity,b,'postflop_complete_cycle')
    old.compare.validate_run(r,{})
    assert old.exact_raw(identity)==anchor,'full result/checkpoint mismatch'
    if environment is None:environment=r['environment'];gpu=old.compare.gpu_identity(r)
    assert r['environment']==environment and old.compare.gpu_identity(r)==gpu
save(OUT/'complete.json',{'at':now(),'protocol_sha256':sys.argv[1],'measurement_order':P['measurement_order'],'all_samples_retained':True,'fixture_results':18,'convergence_records':138,'controls_complete_sha256':sha(OUT/'controls-complete.json'),'candidate_accepted':False})
print('Fixed E038 primary screen complete; assess before any confirmation or adoption.',flush=True)
