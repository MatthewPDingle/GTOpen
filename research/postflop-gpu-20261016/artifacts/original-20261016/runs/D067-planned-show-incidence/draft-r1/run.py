"""Root-only single D067 invocation through the existing serialized native runner."""
import hashlib, json, os, re, shutil, signal, subprocess, sys
from pathlib import Path

repo=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
assert hashlib.sha256((repo/'tools/postflop_autoresearch.py').read_bytes()).hexdigest()=='d6943a80d80d1cd515e1b83bb9109f5d27d78ce5c9dfc2ce21b16e0e1d188b70'
sys.path.insert(0,str(repo/'tools'))
import postflop_autoresearch as ar
here=Path(__file__).resolve().parent
assert len(sys.argv)==2,'Provide the reviewed root authorization.json SHA256'
auth_path=here/'authorization.json'
assert ar.sha256(auth_path)==sys.argv[1]
auth=json.loads(auth_path.read_text(encoding='utf-8'))
assert auth['candidate']=='D067' and all(auth[x] is True for x in ['E020_accepted','E020_server_qualification_pass','independent_source_review_pass','independent_script_review_pass'])
protocol_path=here/'protocol.json'
protocol_hash='PENDING_PROTOCOL_SHA256'
protocol=json.loads(protocol_path.read_text(encoding='utf-8'))
seal=json.loads((here/'scripts-manifest.json').read_text(encoding='utf-8'))
name='D067-solver'; identity='D067R1'
binary=ar.RESEARCH/'binaries'/(name+'.exe')
manifest_path=binary.with_suffix('.manifest.json')
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
binary_hash=ar.sha256(binary);manifest_hash=ar.sha256(manifest_path)
current=ar.source_identity()['source_sha256']

def verify():
    assert ar.sha256(auth_path)==sys.argv[1] and ar.sha256(protocol_path)==protocol_hash
    assert auth['evidence_sha256'][str(here/'scripts-manifest.json')]==ar.sha256(here/'scripts-manifest.json')
    for path,h in auth['evidence_sha256'].items():assert ar.sha256(Path(path))==h,path
    assert seal['status']=='FROZEN_PROSPECTIVE_NOT_EXECUTED'
    for path,h in seal['script_sha256'].items():assert ar.sha256(here/path)==h,path
    for path,h in seal['reference_sha256'].items():assert ar.sha256(Path(path))==h,path
    gates=json.loads((here/'protocol.json').read_text(encoding='utf-8'))['prerequisite_reports']
    for role,gate in gates.items():
        pin=auth['prerequisites'][role]
        assert pin['path']==gate['path'] and ar.sha256(Path(pin['path']))==pin['sha256']
        assert auth['evidence_sha256'][pin['path']]==pin['sha256']
        value=json.loads(Path(pin['path']).read_text(encoding='utf-8'))
        for key,expected in gate['required_fields'].items(): assert value[key]==expected,(role,key)
    assert ar.sha256(binary)==binary_hash==manifest['binary_sha256']
    assert ar.sha256(manifest_path)==manifest_hash
    assert manifest['candidate']=='D067' and manifest['test_only_append_verified'] is True
    assert manifest['source_sha256']==current==ar.source_identity()['source_sha256'] and len(current)==163
    assert manifest['probe_authorization_sha256']==sys.argv[1]
    assert manifest['primary_protocol_sha256']==protocol_hash
    assert manifest['build_script_sha256']==ar.sha256(here/'build.py')
    assert manifest['probe_evidence_sha256']==auth['evidence_sha256']
    for path,h in [(manifest['build_log'],manifest['build_log_sha256']),(manifest['build_stderr_log'],manifest['build_stderr_sha256']),(manifest['patch'],manifest['patch_sha256'])]:assert ar.sha256(Path(path))==h
    assert json.loads((ar.RESEARCH/'runs/D067-build/exit.json').read_text(encoding='utf-8'))['returncode']==0
    for name,pin in protocol['preexisting_target_artifacts'].items():
        assert ar.sha256(repo/name)==pin['sha256'] and (repo/name).stat().st_size==pin['bytes']

def interrupted(signum,_frame):raise KeyboardInterrupt(f'received signal {signum}')
for sig in [signal.SIGTERM,getattr(signal,'SIGBREAK',None)]:
    if sig is not None:signal.signal(sig,interrupted)

verify()
assert not (ar.RESEARCH/'gpu-run.lock').exists(),'A build or GPU operation still holds the lock'
assert shutil.disk_usage(ar.RESEARCH).free>=50*1024**3
assert not (ar.RESEARCH/'runs'/identity).exists()
assert not any(x['id']==identity for x in json.loads(ar.STATUS.read_text(encoding='utf-8'))['experiments'])
out=ar.RESEARCH/'runs/D067-execution';out.mkdir(exist_ok=False)
census=out/'mapping';census.mkdir(exist_ok=False)
command=[sys.executable,'tools/postflop_autoresearch.py','--id',identity,'--title','D067 CPU-only planned showdown mapping derivation',
    '--kind','diagnostic','--binary',str(binary),'--build-manifest',str(manifest_path),
    '--test',protocol['test_filter']]
env=os.environ.copy();env.pop('POSTFLOP_AUTORESEARCH_FIXTURE',None)
env.pop('POSTFLOP_AUTORESEARCH_LIFECYCLE_PROFILE',None)
env['D067_MAPPING_DIR']=str(census)
env['D067_CENSUS_DIR']=str(ar.RESEARCH/'runs/D066-execution/census')
env.update(POSTFLOP_AUTORESEARCH_PROFILE='0',POSTFLOP_AUTORESEARCH_STORAGE='compressed',RAYON_NUM_THREADS='16')
ar.atomic_json(out/'invocation.json',{'at':ar.now(),'command':command,'actual_run':identity,'logical_dashboard_row':'D067',
    'binary_sha256':binary_hash,'build_manifest_sha256':manifest_hash,'source_sha256':current,
    'protocol_sha256':protocol_hash,'authorization_sha256':sys.argv[1],'script_sha256':ar.sha256(Path(__file__)),
    'mapping_directory':str(census),'run_env':{k:env.get(k) for k in ['D067_MAPPING_DIR','D067_CENSUS_DIR','POSTFLOP_AUTORESEARCH_FIXTURE','POSTFLOP_AUTORESEARCH_LIFECYCLE_PROFILE','POSTFLOP_AUTORESEARCH_PROFILE','POSTFLOP_AUTORESEARCH_STORAGE','RAYON_NUM_THREADS']},
    'build_complete_before_launch':True,'performance_acceptance':False,'timeout_seconds':900})
proc=None;fault=None;cleanup=None
try:
    with (out/'stdout.log').open('xb') as stdout,(out/'stderr.log').open('xb') as stderr:
        proc=subprocess.Popen(command,cwd=repo,env=env,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
        proc.wait(timeout=900) # Existing child runner supplies its10s dashboard heartbeat and GPU lock.
except BaseException as error:
    fault=repr(error);cleanup=ar.cleanup_child(proc);raise
finally:
    ar.atomic_json(out/'exit.json',{'at':ar.now(),'returncode':proc.returncode if proc else None,'error':fault,'cleanup':cleanup})
assert proc.returncode==0
verify()
report=json.loads((ar.RESEARCH/'runs'/identity/'report.json').read_text(encoding='utf-8'))
assert report['status']=='measured' and report['returncode']==0 and report['test_pass_count']==1
raw=(ar.RESEARCH/'runs'/identity/'stdout.log').read_text(encoding='utf-8')
assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)==[('1','0','0','0','88')]
assert 'panicked at' not in raw and 'D067 invalid diagnostic' not in raw
expected_files=set(protocol['expected_files'])
assert {p.name for p in census.iterdir()}==expected_files
artifact_pins={}
for path in sorted(census.iterdir()):
    assert path.is_file() and not path.is_symlink() and path.resolve().parent==census.resolve()
    artifact_pins[path.name]={'sha256':ar.sha256(path),'bytes':path.stat().st_size}
ar.atomic_json(out/'mapping-artifacts.json',{'mapping_directory':str(census),'files':artifact_pins,'raw_float_payload_retained':False,'cpu_only_mapping':True})
ar.atomic_json(out/'complete.json',{'at':ar.now(),'actual_run':identity,'native_test_pass':True,'mapping_artifacts_sha256':ar.sha256(out/'mapping-artifacts.json'),'assessment_pending':True,'performance_acceptance':False})
print('D067R1 completed once; all mapping checks and historical row-flag joins remain required; no performance measurement.',flush=True)
