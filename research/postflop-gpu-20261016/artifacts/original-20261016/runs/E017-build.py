"""Freeze the source-reviewed E017 and build the unit/fixed-evaluator binaries."""
import json,os,subprocess,sys,shutil
from pathlib import Path
repo=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0,str(repo/'tools'))
import postflop_autoresearch as ar
owned=['crates/solver/src/gpu/'+n for n in ('mod.rs','plan.rs','continuation_capacity.rs')]
assert len(sys.argv)==4,'Provide reviewed mod.rs, plan.rs and continuation_capacity.rs hashes'
for name,expected in zip(owned,sys.argv[1:]):assert ar.sha256(repo/name)==expected,name
out=ar.RESEARCH/'runs/E017-build';out.mkdir(exist_ok=False)

def heartbeat():
    with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
        status=json.loads(ar.STATUS.read_text(encoding='utf-8'))
        status.update(updated_at=ar.now(),stage='Building frozen E017 candidate',activity='Actor0-only down-action list candidate from accepted E015; source frozen, no accepted gain yet.',active_experiment='E017')
        ar.atomic_json(ar.STATUS,status)

with ar.exclusive_lock(ar.RESEARCH/'gpu-run.lock'):
    ar.refuse_active(ar.live_status())
    assert shutil.disk_usage(ar.RESEARCH).free>=50*1024**3
    before=ar.source_identity();ar.atomic_json(out/'source-before.json',before)
    assert before['benchmark_sha256']['crates/solver/tests/postflop_autoresearch.rs']=='f13d79410a22f140c05cb9a822fe9685c2180e5baeda4b625d52ae03feebd327'
    changed=subprocess.check_output(['git','diff','--name-only','HEAD','--','crates/solver'],cwd=repo,text=True).splitlines()
    assert set(changed)==set(owned),changed
    patch=out/'candidate.patch';patch.write_bytes(subprocess.check_output(['git','diff','--binary','HEAD','--',*owned],cwd=repo))
    for name in owned:
        dest=out/'source'/Path(name).name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(repo/name,dest)
    env=os.environ.copy();env.update(CARGO_TARGET_DIR=str(ar.RESEARCH/'build'),RAYON_NUM_THREADS='16')
    command=['cargo','test','--release','-p','solver','--features','gpu','--lib','--test','postflop_autoresearch','--no-run','--message-format=json']
    log,err=out/'build.jsonl',out/'build.stderr.log'
    heartbeat();print('Building frozen E017 source.',flush=True)
    with log.open('xb') as stdout,err.open('xb') as stderr:
        proc=subprocess.Popen(command,cwd=repo,env=env,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
        while True:
            try:code=proc.wait(timeout=10);break
            except subprocess.TimeoutExpired:heartbeat()
    ar.atomic_json(out/'exit.json',{'returncode':code,'at':ar.now(),'command':command})
    assert code==0,err.read_text(encoding='utf-8',errors='replace')[-6000:]
    assert before['source_sha256']==ar.source_identity()['source_sha256'],'Source changed during build'
    artifacts=[]
    for line in log.read_text(encoding='utf-8').splitlines():
        item=json.loads(line)
        if item.get('reason')!='compiler-artifact' or not item.get('profile',{}).get('test') or not item.get('executable'):continue
        name=item['target']['name']
        if name not in ('solver','postflop_autoresearch'):continue
        dest=ar.RESEARCH/'binaries'/f'E017-{name}.exe';assert not dest.exists();shutil.copyfile(item['executable'],dest)
        manifest={'candidate':'E017','binary_sha256':ar.sha256(dest),'built_at':ar.now(),**before,
          'build_command':command,'build_log':str(log),'build_log_sha256':ar.sha256(log),'build_stderr_log':str(err),'build_stderr_sha256':ar.sha256(err),
          'patch':str(patch),'patch_sha256':ar.sha256(patch),'source_copies':str(out/'source'),'source_matches_prebuild':True,
          'change':'From E015: filter inactive actor1 down-action CTAs in second paired sweep, with allocation and capacity accounting; CUDA math/evaluator unchanged'}
        ar.atomic_json(dest.with_suffix('.manifest.json'),manifest);artifacts.append(name)
        print(name,manifest['binary_sha256'],flush=True)
    assert set(artifacts)=={'solver','postflop_autoresearch'},artifacts
    print('E017 build frozen.',flush=True)
