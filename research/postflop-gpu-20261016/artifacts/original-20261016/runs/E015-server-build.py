"""Build and freeze an isolated server candidate without touching the live executable."""
import json, os, shutil, subprocess, sys, threading
from pathlib import Path

APP = Path(r'X:\Dev\GTOpen')
sys.path.insert(0, r'X:\Dev\GTOpen-gpu-research-20261016\tools')
import postflop_autoresearch as ar
OUT = ar.RESEARCH / 'runs/E015-server-build'
OUT.mkdir(exist_ok=False)

def sources():
    files = [APP / n for n in ('Cargo.toml', 'Cargo.lock', 'crates/server/Cargo.toml', 'crates/solver/Cargo.toml', 'crates/solver/build.rs')]
    for folder in ('crates/server/src', 'crates/solver/src'):
        files.extend(p for p in (APP / folder).rglob('*') if p.suffix in ('.rs', '.cu', '.cuh', '.h'))
    return {p.relative_to(APP).as_posix(): ar.sha256(p) for p in sorted(files) if p.is_file()}

def heartbeat():
    with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'), timeout=3):
        status = json.loads(ar.STATUS.read_text(encoding='utf-8'))
        status.update(updated_at=ar.now(), state='running', stage='Building isolated server candidate',
                      activity='E015 passed complete-cycle and accuracy qualification; preparing an isolated server smoke test. Live deployment remains blocked.', active_experiment=None)
        ar.atomic_json(ar.STATUS, status)

def main():
    with ar.exclusive_lock(ar.RESEARCH / 'gpu-run.lock'):
        ar.refuse_active(ar.live_status())
        assert not subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=no'], cwd=APP)
        before = sources()
        assert before['crates/solver/src/gpu/mod.rs'] == '7de2cd46ef93742c603042306cfe2ad08a83ff52a2be1123efd9d201aca15f1a'
        ar.atomic_json(OUT / 'source-before.json', before)
        commit = subprocess.check_output(['git','rev-parse','HEAD'], cwd=APP, text=True).strip()
        env = os.environ.copy()
        env.update(CARGO_TARGET_DIR=str(ar.RESEARCH/'build'), RAYON_NUM_THREADS='16')
        commands = [
            ['cargo','build','--release','-p','server','--features','gpu','--message-format=json'],
            ['cargo','test','--release','-p','server','--features','gpu','--no-run','--message-format=json'],
        ]
        for index, command in enumerate(commands):
            heartbeat()
            log, err = OUT/f'build-{index}.jsonl', OUT/f'build-{index}.stderr.log'
            print(' '.join(command), flush=True)
            with log.open('xb') as stdout, err.open('xb') as stderr:
                process = subprocess.Popen(command, cwd=APP, env=env, stdout=stdout, stderr=stderr, creationflags=subprocess.CREATE_NO_WINDOW)
                while True:
                    try:
                        code = process.wait(timeout=10)
                        break
                    except subprocess.TimeoutExpired:
                        heartbeat()
            ar.atomic_json(OUT/f'build-{index}-exit.json', {'command':command,'returncode':code,'finished_at':ar.now()})
            assert code == 0, err.read_text(errors='replace')[-6000:]
            assert before == sources(), 'source changed during server build'
            binaries = [d for line in log.read_text().splitlines() if (d:=json.loads(line)).get('reason')=='compiler-artifact' and d.get('executable') and d['target']['name']=='gto-server']
            assert len(binaries)==1, binaries
            destination = ar.RESEARCH/'binaries'/('E015-gto-server.exe' if index==0 else 'E015-server-tests.exe')
            assert not destination.exists()
            shutil.copyfile(binaries[0]['executable'], destination)
            manifest = {'candidate':'E015','source_root':str(APP),'source_commit':commit,'source_sha256':before,
                        'binary_sha256':ar.sha256(destination),'source_matches_prebuild':True,'built_at':ar.now(),
                        'build_command':command,'build_log':str(log),'build_log_sha256':ar.sha256(log),
                        'build_stderr':str(err),'build_stderr_sha256':ar.sha256(err),
                        'live_executable_touched':False,'scope':'Main-source build, isolated validation only; no performance claim'}
            ar.atomic_json(destination.with_suffix('.manifest.json'),manifest)
            print(destination.name, manifest['binary_sha256'], flush=True)
        ar.atomic_json(OUT/'result.json',{'status':'pass','source_commit':commit,'source_unchanged':before==sources(),'live_executable_touched':False,'finished_at':ar.now()})

if __name__ == '__main__':
    main()
