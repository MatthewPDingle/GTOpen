"""Build the frozen test-only graph diagnostic; never run it or alter acceptance."""
import hashlib, json, os, shutil, subprocess, sys
from pathlib import Path
repo=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0,str(repo/'tools'))
import postflop_autoresearch as ar
owned=['crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/graph_device_events.rs']
assert len(sys.argv)==4,'Provide reviewed mod.rs, diagnostic module and archived patch hashes'
for name,expected in zip(owned,sys.argv[1:3]):assert ar.sha256(repo/name)==expected,name
archive=ar.RESEARCH/'runs/D033-implementation'
patch=archive/'candidate.patch';assert ar.sha256(patch)==sys.argv[3]
out=ar.RESEARCH/'runs/D033-build'
inputs={
 'runs/D033-graph-event-design/protocol.json':'3c0187465cbcf7faa347a11fe2f769dfafd5e29ec027eb5754e60f10c20745e2',
 'runs/D033-graph-event-design/anchor-rainbow.json':'94e7d8299c7ea549e59d5b33cf12a37cd1a74cbc9d652850f06e23adb5e11e52',
 'runs/D033-graph-event-design/README.md':'1e1511e23918a92ff0630c1d2c1b3110509ae6d8ac01abc90bda06d42df9712d',
 'runs/D033-graph-event-design/source-manifest.json':'e4fde2a0c1042f389c5168e3a1d214332351e804bc2d3b2e03907fdd47099abe',
 'runs/D033-oracle-anchors/anchors.json':'7c2da4aa20e34a8693e6eec39c40af5d43324aa502fac5e9941444270fb04d8f',
 'binaries/E015-postflop_autoresearch.manifest.json':'934c29e800d180397ee330340d425f1084078c24831ba87c4de5e74729821fd2',
}

def verify_inputs():
    for relative,expected in inputs.items():assert ar.sha256(ar.RESEARCH/relative)==expected,relative
    sealed=json.loads((ar.RESEARCH/'runs/D033-graph-event-design/source-manifest.json').read_text(encoding='utf-8'))
    for name,expected in sealed['source_sha256'].items():
        data=subprocess.check_output(['git','show','HEAD:'+name],cwd=repo) if name==owned[0] else (repo/name).read_bytes()
        assert hashlib.sha256(data).hexdigest()==expected,name
    for group in ('cudarc_files','evidence_inputs'):
        for name,expected in sealed[group].items():assert ar.sha256(Path(name))==expected,name
    for name,expected in zip(owned,sys.argv[1:3]):assert ar.sha256(repo/name)==expected,name
    assert ar.sha256(patch)==sys.argv[3]
    accepted=json.loads((ar.RESEARCH/'binaries/E015-postflop_autoresearch.manifest.json').read_text(encoding='utf-8'))['source_sha256']
    current=ar.source_identity()['source_sha256']
    assert set(current)==set(accepted)|{owned[1]}
    for name,expected in accepted.items():
        if name!=owned[0]:assert current[name]==expected,name

def heartbeat():
    with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
        s=json.loads(ar.STATUS.read_text(encoding='utf-8'))
        s.update(updated_at=ar.now(),stage='Building frozen D033 graph diagnostic',active_experiment='D033',
                 activity='Test-only diagnostic with unchanged E015 production kernels and frozen primary benchmark. No new performance result.')
        ar.atomic_json(ar.STATUS,s)

with ar.exclusive_lock(ar.RESEARCH/'gpu-run.lock'):
    ar.refuse_active(ar.live_status())
    assert shutil.disk_usage(ar.RESEARCH).free>=50*1024**3
    verify_inputs()
    out.mkdir(exist_ok=False)
    before=ar.source_identity();ar.atomic_json(out/'source-before.json',before)
    assert before['benchmark_sha256']['crates/solver/tests/postflop_autoresearch.rs']=='f13d79410a22f140c05cb9a822fe9685c2180e5baeda4b625d52ae03feebd327'
    assert ar.sha256(repo/'crates/solver/src/gpu/kernels.cu')=='8fe86cb859124592f9df13821f4a300450045620e6947e99466e4228b78c20d0'
    tracked=subprocess.check_output(['git','diff','--name-only','HEAD','--','crates/solver'],cwd=repo,text=True).splitlines()
    untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard','--','crates/solver/src'],cwd=repo,text=True).splitlines()
    assert set(tracked+untracked)==set(owned),(tracked,untracked)
    original=subprocess.check_output(['git','show','HEAD:crates/solver/src/gpu/mod.rs'],cwd=repo)
    current=(repo/owned[0]).read_bytes()
    assert current.startswith(original),'Production source was changed, not merely appended'
    addition=current[len(original):].decode('utf-8').replace('\r\n','\n').strip()
    assert addition=='#[cfg(test)]\nmod graph_device_events;',repr(addition)
    for name in owned:
        dest=out/'source'/Path(name).name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(repo/name,dest)
    shutil.copyfile(patch,out/'candidate.patch')
    command=['cargo','test','--release','-p','solver','--features','gpu','--lib','--no-run','--message-format=json']
    env=os.environ.copy();env.update(CARGO_TARGET_DIR=str(ar.RESEARCH/'build'),RAYON_NUM_THREADS='16')
    log,err=out/'build.jsonl',out/'build.stderr.log'
    heartbeat();print('Building frozen D033 test-only graph diagnostic.',flush=True)
    with log.open('xb') as stdout,err.open('xb') as stderr:
        proc=subprocess.Popen(command,cwd=repo,env=env,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
        while True:
            try:code=proc.wait(timeout=10);break
            except subprocess.TimeoutExpired:heartbeat()
    ar.atomic_json(out/'exit.json',{'returncode':code,'at':ar.now(),'command':command})
    assert code==0,err.read_text(encoding='utf-8',errors='replace')[-8000:]
    verify_inputs()
    assert before['source_sha256']==ar.source_identity()['source_sha256'],'Source changed during build'
    artifacts=[]
    for line in log.read_text(encoding='utf-8').splitlines():
        item=json.loads(line)
        if item.get('reason')=='compiler-artifact' and item.get('profile',{}).get('test') and item.get('executable') and item['target']['name']=='solver':artifacts.append(item)
    assert len(artifacts)==1
    destination=ar.RESEARCH/'binaries/D033-solver.exe';assert not destination.exists();shutil.copyfile(artifacts[0]['executable'],destination)
    manifest={**before,'candidate':'D033','scope':'Test-only instrumented-device diagnostic; no performance acceptance',
      'binary_sha256':ar.sha256(destination),'built_at':ar.now(),'build_command':command,
      'build_log':str(log),'build_log_sha256':ar.sha256(log),'build_stderr_log':str(err),'build_stderr_sha256':ar.sha256(err),
      'patch':str(out/'candidate.patch'),'patch_sha256':ar.sha256(patch),'source_matches_prebuild':True,
      'test_only_append_verified':True,'diagnostic_inputs_sha256':inputs}
    ar.atomic_json(destination.with_suffix('.manifest.json'),manifest)
    print(destination.name,manifest['binary_sha256'],flush=True)
