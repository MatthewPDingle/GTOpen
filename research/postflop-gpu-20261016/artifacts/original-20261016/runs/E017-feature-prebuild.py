"""Compile changed feature-gated capacity code before primary timing; keep the primary GPU-only binary frozen."""
import json, os, shutil, subprocess, sys
from pathlib import Path
repo=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0,str(repo/'tools'))
import postflop_autoresearch as ar
with ar.exclusive_lock(ar.RESEARCH/'gpu-run.lock'):
    ar.refuse_active(ar.live_status())
    before=ar.source_identity()
    primary=json.loads((ar.RESEARCH/'binaries/E017-postflop_autoresearch.manifest.json').read_text(encoding='utf-8'))
    assert before['source_sha256']==primary['source_sha256']
    log=ar.RESEARCH/'runs/E017-feature-prebuild.jsonl'
    err=ar.RESEARCH/'runs/E017-feature-prebuild.stderr.log'
    targets={'solver':'continuation-tests'}
    command=['cargo','test','--release','-p','solver','--features','preflop-research','--lib','--no-run','--message-format=json']
    env=os.environ.copy();env.update(CARGO_TARGET_DIR=str(ar.RESEARCH/'build'),RAYON_NUM_THREADS='16')
    print('Building E017 feature-gated continuation controls',flush=True)
    with log.open('xb') as stdout,err.open('xb') as stderr:
        result=subprocess.run(command,cwd=repo,env=env,stdout=stdout,stderr=stderr)
    assert result.returncode==0,err.read_text(encoding='utf-8',errors='replace')[-8000:]
    assert ar.source_identity()['source_sha256']==before['source_sha256']
    binaries=[d for line in log.read_text(encoding='utf-8').splitlines() if (d:=json.loads(line)).get('reason')=='compiler-artifact' and d.get('profile',{}).get('test') and d.get('executable') and d['target']['name'] in targets]
    assert {d['target']['name'] for d in binaries}==set(targets)
    for binary in binaries:
        destination=ar.RESEARCH/'binaries'/('E017-'+targets[binary['target']['name']]+'.exe')
        assert not destination.exists()
        shutil.copyfile(binary['executable'],destination)
        manifest={**before,'candidate':'E017','binary_sha256':ar.sha256(destination),'built_at':ar.now(),
              'build_command':command,'build_log':str(log),'build_log_sha256':ar.sha256(log),
              'build_stderr':str(err),'build_stderr_sha256':ar.sha256(err),
              'source_matches_primary_binary':True,'source_matches_prebuild':True,
              'scope':'Feature-gated continuation correctness only; not the primary performance binary'}
        ar.atomic_json(destination.with_suffix('.manifest.json'),manifest)
        print(destination.name,manifest['binary_sha256'],flush=True)
