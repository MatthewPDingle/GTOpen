"""Later-only curated build/test driver. No work without --execute.

Build phase stages GPU runtime BEFORE any non-GPU build can replace it. Test
phase executes frozen compiler-artifact executables serially, in crate cwd.
Windows Job Objects own all children; only those owned jobs are terminated.
"""
import argparse
import ctypes
from ctypes import wintypes as wt
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LAB = ROOT / 'target/autoresearch/preflop-interactive-20260911'
PRODUCTION = ROOT / 'target/autoresearch/preflop-interactive-production-20260911'
SOURCE = '53ce9dec08de9fa2f93f246d7f5efcccc8c22c68'
DEADLINE = dt.datetime.fromisoformat('2026-09-11T03:03:27+00:00')
spec = importlib.util.spec_from_file_location('production_live_guard', HERE / 'guarded_run.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write_new(path, data):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def now():
    return dt.datetime.now(dt.timezone.utc)


def source_check():
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=PRODUCTION, text=True).strip()
    require(head == SOURCE, 'curated source commit changed')
    dirty = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=PRODUCTION)
    require(not dirty.strip(), 'tracked production source is dirty')


def environment(gpu):
    env = os.environ.copy()
    removed = {}
    for key in list(env):
        if key.startswith(('PREFLOP_MW_', 'PREFLOP_GPU_', 'PREFLOP_PHASE_')):
            removed[key] = env.pop(key)
    cache = (ROOT / 'cache/preflop_eq169.bin').read_bytes()
    samples = int.from_bytes(cache[:4], 'little')
    require(len(cache) == 4 + 169 * 169 * 4 and samples > 0, 'bad equity cache')
    fixed = {'CARGO_TARGET_DIR': str(LAB / 'target'), 'CARGO_BUILD_JOBS': '8',
             'SOLVER_THREADS': '16', 'RAYON_NUM_THREADS': '16',
             'SOLVER_GPU': '1' if gpu else '0', 'SOLVER_GPU_MEM_MB': '23000',
             'PREFLOP_EQ_SAMPLES': str(samples),
             'REALIZATION_FIT': str(ROOT / 'cache/realization_fit.json')}
    env.update(fixed)
    env['PATH'] = str(ROOT / '.cuda-nvrtc/nvidia/cuda_nvrtc/bin') + os.pathsep + env.get('PATH', '')
    return env, fixed, removed


class OwnedJob:
    """Assign a suspended child before any Cargo/rustc descendants can spawn."""
    def __init__(self):
        require(os.name == 'nt', 'Windows ownership guard required')
        class Basic(ctypes.Structure):
            _fields_ = [('process_time', ctypes.c_longlong), ('job_time', ctypes.c_longlong),
                        ('flags', wt.DWORD), ('min_ws', ctypes.c_size_t), ('max_ws', ctypes.c_size_t),
                        ('active_processes', wt.DWORD), ('affinity', ctypes.c_size_t),
                        ('priority', wt.DWORD), ('scheduling', wt.DWORD)]
        class Io(ctypes.Structure):
            _fields_ = [(name, ctypes.c_ulonglong) for name in ('ro', 'wo', 'oo', 'rb', 'wb', 'ob')]
        class Extended(ctypes.Structure):
            _fields_ = [('basic', Basic), ('io', Io), ('process_memory', ctypes.c_size_t),
                        ('job_memory', ctypes.c_size_t), ('peak_process', ctypes.c_size_t),
                        ('peak_job', ctypes.c_size_t)]
        self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        self.kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wt.LPCWSTR]
        self.kernel.CreateJobObjectW.restype = wt.HANDLE
        self.kernel.SetInformationJobObject.argtypes = [wt.HANDLE, ctypes.c_int, ctypes.c_void_p, wt.DWORD]
        self.kernel.AssignProcessToJobObject.argtypes = [wt.HANDLE, wt.HANDLE]
        self.kernel.CloseHandle.argtypes = [wt.HANDLE]
        self.handle = self.kernel.CreateJobObjectW(None, None)
        require(self.handle, 'CreateJobObject failed')
        limits = Extended()
        limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.kernel.SetInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
            self.close()
            raise RuntimeError('SetInformationJobObject failed')

    def start(self, command, cwd, env, log):
        process = subprocess.Popen(command, cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT,
                                   creationflags=subprocess.CREATE_NO_WINDOW | 0x4)  # CREATE_SUSPENDED
        try:
            require(self.kernel.AssignProcessToJobObject(self.handle, wt.HANDLE(int(process._handle))),
                    'could not assign owned suspended child to job')
            ntdll = ctypes.WinDLL('ntdll')
            ntdll.NtResumeProcess.argtypes = [wt.HANDLE]
            ntdll.NtResumeProcess.restype = ctypes.c_long
            require(ntdll.NtResumeProcess(wt.HANDLE(int(process._handle))) == 0, 'resume owned process failed')
            return process
        except BaseException:
            process.kill()  # Popen retains the exact newly created process handle.
            process.wait(timeout=10)
            raise

    def close(self):
        if self.handle:
            self.kernel.CloseHandle(self.handle)
            self.handle = None


def run_owned(command, cwd, env, log, cap, deadline, records, label):
    require(now() < deadline, 'qualification deadline reached')
    guard.live_idle()
    source_check()
    require(Path(command[0]).is_file(), 'resolved executable missing')
    row = {'label': label, 'command': [str(v) for v in command], 'cwd': str(cwd),
           'launcher_sha256': sha(command[0]), 'log': str(log), 'started_utc': now().isoformat(),
           'timeout_seconds': cap, 'ownership': 'suspended child assigned to kill-on-close Windows Job Object'}
    records.append(row)
    job = OwnedJob()
    process = None
    start = time.monotonic()
    try:
        with Path(log).open('xb') as output:
            process = job.start(command, cwd, env, output)
            row['owned_pid'] = process.pid
            while process.poll() is None:
                time.sleep(0.5)
                guard.live_idle()
                require(time.monotonic() - start < cap, 'owned job timeout')
                require(now() < deadline, 'combined qualification deadline')
            row['returncode'] = process.returncode
            require(process.returncode == 0, f'{label} failed; see bounded log')
    except BaseException as error:
        row['error'] = str(error)
        raise
    finally:
        job.close()  # Contains any remaining children even after Cargo exits.
        if process is not None:
            process.wait(timeout=15)
            row['returncode'] = process.returncode
        row['seconds'] = time.monotonic() - start
        row['finished_utc'] = now().isoformat()
    print(json.dumps({'phase': label, 'seconds': round(row['seconds'], 3), 'returncode': row['returncode']}), flush=True)


def build_steps(cargo):
    common = ['--release', '--message-format=json-render-diagnostics']
    return [
        ('gpu-runtime', [cargo, 'build', '-p', 'server', '--features', 'gpu', *common], True),
        ('gpu-solver', [cargo, 'test', '-p', 'solver', '--features', 'gpu', '--lib', '--test', 'gpu', '--test', 'preflop_gpu', '--no-run', *common], True),
        ('gpu-server', [cargo, 'test', '-p', 'server', '--features', 'gpu', '--no-run', *common], True),
        ('cpu-solver', [cargo, 'test', '-p', 'solver', '--lib', '--bins', '--tests', '--no-run', *common], False),
        ('cpu-server', [cargo, 'test', '-p', 'server', '--no-run', *common], False),
    ]


def collect_artifacts(log, phase, folder):
    out = []
    for line in Path(log).read_text(encoding='utf-8', errors='replace').splitlines():
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        executable = message.get('executable')
        if message.get('reason') != 'compiler-artifact' or not executable:
            continue
        path = Path(executable).resolve()
        require(path.is_relative_to((LAB / 'target').resolve()), 'artifact outside shared Cargo target')
        digest = sha(path)
        target = message['target']
        frozen = folder / f'{phase}-{target["name"]}-{digest[:16]}.exe'
        if not frozen.exists():
            shutil.copy2(path, frozen)
        require(sha(frozen) == digest, 'frozen compiler-artifact changed')
        out.append({'phase': phase, 'target': target['name'], 'kind': target['kind'],
                    'source_path': target['src_path'], 'test': message['profile']['test'],
                    'features': message['features'], 'original_executable': str(path),
                    'executable': str(frozen), 'sha256': digest})
    require(out, f'no executable compiler artifacts for {phase}')
    return out


def stage_gpu_runtime(artifacts):
    matches = [a for a in artifacts if a['target'] == 'gto-server' and not a['test']]
    require(len(matches) == 1, 'unique GPU runtime required')
    runtime = PRODUCTION / 'target/qualification/gto-server.exe'
    if not runtime.exists():
        with Path(matches[0]['executable']).open('rb') as src, runtime.open('xb') as dst:
            shutil.copyfileobj(src, dst)
    require(sha(runtime) == matches[0]['sha256'], 'existing staged runtime differs; never overwrite it silently')
    return {'path': str(runtime), 'sha256': matches[0]['sha256'], 'source_commit': SOURCE}


def selected_tests(artifacts):
    selected = []
    for artifact in artifacts:
        if not artifact['test']:
            continue
        phase = artifact['phase']
        args = ['--test-threads=1']
        if phase == 'gpu-solver':
            if artifact['target'] == 'solver' and 'lib' in artifact['kind']:
                args = ['detached_iterations_preserve_exact_trajectory_stale_host_stop_and_resume', *args]
        elif phase == 'gpu-server':
            args = ['preflop_preview_tests', *args]
        elif phase not in ('cpu-solver', 'cpu-server'):
            continue
        package = 'server' if phase.endswith('server') else 'solver'
        selected.append((artifact, args, PRODUCTION / 'crates' / package))
    return selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['build', 'tests', 'all'], default='all')
    parser.add_argument('--id', default='production-53ce9de-a')
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    require(args.id.replace('-', '').replace('_', '').isalnum(), 'invalid ID')
    if not args.execute:
        print(json.dumps({'source_commit': SOURCE, 'production': str(PRODUCTION), 'shared_target': str(LAB / 'target'),
                          'phases': [x[0] for x in build_steps('cargo')], 'max_combined_seconds': 900,
                          'deadline': DEADLINE.isoformat(), 'note': 'No build/test performed. Explicit --execute required.'}, indent=2))
        return
    source_check()
    cargo = shutil.which('cargo')
    require(cargo, 'cargo not on PATH')
    artifact_records, runs = [], []
    status, failure = 'running', None
    if args.phase == 'tests':
        require(args.manifest is not None, 'tests require frozen --manifest')
        manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
        require(manifest['source_commit'] == SOURCE and manifest['status'] == 'built', 'wrong/incomplete build manifest')
        require(manifest['driver_sha256'] == sha(__file__), 'driver changed since build protocol was frozen')
        directory = Path(manifest['directory'])
        require(directory.resolve().is_relative_to((PRODUCTION / 'target/qualification').resolve()), 'manifest output outside production qualification')
        deadline = dt.datetime.fromisoformat(manifest['qualification_deadline'])
        artifact_records = manifest['artifacts']
        runtime = manifest['runtime']
    else:
        directory = PRODUCTION / 'target/qualification' / args.id
        directory.mkdir(parents=True, exist_ok=False)
        deadline = min(DEADLINE, now() + dt.timedelta(seconds=900))
        manifest = {'source_commit': SOURCE, 'directory': str(directory), 'started_utc': now().isoformat(),
                    'qualification_deadline': deadline.isoformat(), 'driver_sha256': sha(__file__),
                    'cargo': cargo, 'cargo_sha256': sha(cargo), 'artifacts': artifact_records,
                    'build_commands': [{'label': label, 'command': command, 'gpu': gpu} for label,command,gpu in build_steps(cargo)],
                    'test_policy': 'All non-GPU solver lib/bin/integration and server tests plus solver doctests; GPU solver detached filter, gpu/preflop_gpu integrations, server preview filter',
                    'equity_cache_sha256': sha(ROOT / 'cache/preflop_eq169.bin'),
                    'realization_fit_sha256': sha(ROOT / 'cache/realization_fit.json')}
        write_new(directory / 'protocol.json', manifest)
        runtime = None
    require(now() < deadline, 'combined15-minute qualification window has expired')
    lock = PRODUCTION / 'target/qualification/owned-job.lock'
    with lock.open('x', encoding='utf-8') as f:
        f.write(json.dumps({'owner_pid': os.getpid(), 'source': SOURCE, 'directory': str(directory)}))
    try:
        if args.phase in ('build', 'all'):
            for label, command, gpu in build_steps(cargo):
                env, fixed, removed = environment(gpu)
                log = directory / f'{label}.jsonl'
                run_owned(command, PRODUCTION, env, log, 420, deadline, runs, label)
                rows = collect_artifacts(log, label, directory)
                artifact_records.extend(rows)
                runs[-1].update(fixed_environment=fixed, removed_environment=removed)
                if label == 'gpu-runtime':
                    runtime = stage_gpu_runtime(rows)
            manifest.update(status='built', artifacts=artifact_records, runtime=runtime, build_runs=runs.copy())
            write_new(directory / 'build-manifest.json', manifest)
        if args.phase in ('tests', 'all'):
            require(runtime and sha(runtime['path']) == runtime['sha256'], 'staged GPU runtime no longer matches')
            for index, (artifact, arguments, cwd) in enumerate(selected_tests(artifact_records)):
                require(sha(artifact['executable']) == artifact['sha256'], 'frozen test artifact changed')
                env, fixed, removed = environment(artifact['phase'].startswith('gpu'))
                label = f'test-{index:02}-{artifact["phase"]}-{artifact["target"]}'
                run_owned([artifact['executable'], *arguments], cwd, env, directory / f'{label}.log',
                          240, deadline, runs, label)
                runs[-1].update(fixed_environment=fixed, removed_environment=removed,
                                test_executable_sha256=artifact['sha256'])
            env, _, _ = environment(False)
            run_owned([cargo, 'test', '--release', '-p', 'solver', '--doc'], PRODUCTION, env,
                      directory / 'cpu-doctests.log', 180, deadline, runs, 'cpu-doctests')
        require(sha(ROOT / 'cache/preflop_eq169.bin') == manifest['equity_cache_sha256'], 'source equity cache changed')
        require(sha(ROOT / 'cache/realization_fit.json') == manifest['realization_fit_sha256'], 'source fit changed')
        status = 'built' if args.phase == 'build' else 'selected_tests_passed'
    except BaseException as error:
        status, failure = 'failed', str(error)
        raise
    finally:
        write_new(directory / f'{args.phase}-result.json', {'status': status, 'error': failure,
                  'source_commit': SOURCE, 'finished_utc': now().isoformat(), 'runtime': runtime,
                  'artifacts': artifact_records, 'runs': runs, 'gpu_integrations_included': True,
                  'scope': 'Full non-GPU test targets+doctests; focused changed GPU/server tests and GPU integrations; no examples rebuilt; no deployment'})
        lock.unlink()
    print(json.dumps({'status': status, 'directory': str(directory), 'runtime': runtime}), flush=True)


if __name__ == '__main__':
    main()
