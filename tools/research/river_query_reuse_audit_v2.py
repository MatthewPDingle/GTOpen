"""Descriptive audit of repeated visible inputs in one fixed archived batch.

Replays all 38 existing native exports in the fixed first batch. Does not run inference, create deals,
train a model, or change the active experiment. A reuse count is not a speedup.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                  MKL_NUM_THREADS='1', RAYON_NUM_THREADS='1',
                  PYTHONDONTWRITEBYTECODE='1')
import argparse
from collections import Counter
import gc
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
FIXTURE = Path('S:/GTOpen-research/weighted-complete-river-training-pilot-v1/A-river/generation-0079-bb713ca9')
METRIC_SHA = '6dbaecaaf825f95e48a5379e74de9d2acd0efde3b37ae0220aa1158b86abcfa5'
NATIVE_SHA = '8dc03e7dd21cbcfc6ed1fd8f7c068137e0fbcb6eebfc9de329744165f79bba62'
EXE = ROOT / 'target/release/examples/hu_river_two_stage_stream_v1.exe'
CONTEXT = OUT / 'bb-context-candidate.json'
RESULT = OUT / 'river-query-reuse-audit-v2-result.json'
ORDER = tuple(f'chunk-{i:03d}-{mode}' for i in range(19) for mode in ('history', 'selected'))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def selection():
    raw = (FIXTURE / 'metrics.json').read_bytes()
    assert sha(raw) == METRIC_SHA
    metric = json.loads(raw)
    assert metric['iteration'] == 79 and metric['subbatches'][0]['chunk'] == 0
    artifacts = metric['subbatches'][0]['artifacts']
    batch = FIXTURE / 'batch-00'
    def checked(relative):
        data = (batch / relative).read_bytes()
        assert sha(data) == artifacts[str(Path(relative))], relative
        return data
    original = json.loads(checked('queries.json'))
    assert CONTEXT.read_text() == original['context_source']
    evidence = json.loads(checked('conditional/evidence.json'))
    assert evidence['native_sha256'] == NATIVE_SHA == sha(EXE.read_bytes())
    streams = []
    for name in ORDER:
        request = checked(f'conditional/{name}-request.json')
        archived = json.loads(checked(f'conditional/{name}-process.json'))
        assert archived['code'] == 0 and len(request) <= 64 * 1024
        streams.append((name, request, archived))
    return streams, original['context_source'], evidence['policy_id']


def canonical_fingerprint(observation, observations):
    row = dict(observation)
    history = []
    for index, action, arity in row['own_history']:
        assert type(index) is int and 0 <= index < len(observations)
        ancestor = observations[index]
        assert ancestor['actor'] == row['actor'] and ancestor['n'] == arity
        history.append([ancestor['hi'], ancestor['lo'], action, arity])
    row['own_history'] = history
    return sha(json.dumps(row, sort_keys=True, separators=(',', ':')).encode())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    streams, source, policy_id = selection()
    if not args.run:
        print(json.dumps(dict(ready=True,streams=list(ORDER),replays_started=False,
                              fixture=str(FIXTURE),metrics_sha256=METRIC_SHA)))
        return
    assert not RESULT.exists(), 'Preserve existing audit evidence; use a new version'
    import psutil
    sys.path.insert(0, str(ROOT / 'tools/research'))
    from bounded_parallel_evaluation_archive_v2 import production_available
    started = time.monotonic()
    last_probe = 0.
    peak_rss = 0
    process = psutil.Process()
    def guard(force=False):
        nonlocal last_probe, peak_rss
        now = time.monotonic()
        assert now - started < 300, 'Five-minute audit budget exceeded'
        peak_rss = max(peak_rss, process.memory_info().rss)
        assert peak_rss < 2_000_000_000, 'Audit memory budget exceeded'
        if force or now - last_probe > 5:
            assert production_available(), 'Production activity has priority'
            assert psutil.virtual_memory().available > 32_000_000_000
            assert psutil.cpu_percent(interval=.2) < 60, 'CPU headroom unavailable'
            last_probe = time.monotonic()
    result = dict(format=1,passed=False,selection='All 19 chunks, in original history/selected order, first batch of A-river update 79.',
                  fixture=str(FIXTURE),metrics_sha256=METRIC_SHA,native_sha256=NATIVE_SHA,
                  context_sha256=sha(CONTEXT.read_bytes()),policy_id=policy_id,
                  script_sha256=sha(Path(__file__).read_bytes()),started_unix=time.time(),
                  inference_run=False,fresh_deals=0,training_changed=False,gpu_used=False,
                  streams=[],scope='One archived batch only. Descriptive input reuse, not measured caching performance or poker accuracy.')
    seen = {}
    try:
        guard(True)
        for name, request, archived in streams:
            guard(True)
            assert sha(EXE.read_bytes()) == NATIVE_SHA
            t = time.monotonic()
            completed = subprocess.run([str(EXE),str(CONTEXT)],input=request,capture_output=True,
                                       timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
            export_seconds = time.monotonic() - t
            assert completed.returncode == archived['code'] == 0
            assert len(completed.stdout) == archived['stdout_bytes'] <= 64_000_000
            assert sha(completed.stdout) == archived['stdout_sha256'], 'Native replay changed'
            t = time.monotonic()
            document = json.loads(completed.stdout)
            decode_seconds = time.monotonic() - t
            assert document['format'] == 3 and document['context_source'] == source
            assert document['request_source'] == request.decode()
            assert document['mode'] == json.loads(request)['mode']
            assert document['queries']['context_source'] == source
            assert document['queries']['batch_source'] == document['request_source']
            observations = document['queries']['observations']
            local = set()
            repeated = 0
            phases = Counter()
            repeated_phases = Counter()
            t = time.monotonic()
            for index, observation in enumerate(observations):
                if index % 4096 == 0:
                    guard()
                key = (observation['hi'],observation['lo'])
                assert key not in local, 'Duplicate key inside native query batch'
                local.add(key)
                fingerprint = canonical_fingerprint(observation,observations)
                phase = observation['phase']
                phases[phase] += 1
                if key in seen:
                    assert seen[key] == fingerprint, 'Same key has different canonical visible input'
                    repeated += 1
                    repeated_phases[phase] += 1
                else:
                    seen[key] = fingerprint
            row = dict(name=name,request_sha256=sha(request),stdout_sha256=archived['stdout_sha256'],
                       stdout_bytes=len(completed.stdout),observations=len(observations),
                       new_observations=len(observations)-repeated,repeated_observations=repeated,
                       phases=dict(phases),repeated_phases=dict(repeated_phases),
                       export_seconds=export_seconds,decode_seconds=decode_seconds,
                       identity_check_seconds=time.monotonic()-t)
            result['streams'].append(row)
            print(json.dumps(dict(stream=name,observations=len(observations),repeated=repeated)),flush=True)
            del document, observations, completed, local
            gc.collect()
        guard(True)
        assert sha(EXE.read_bytes()) == NATIVE_SHA
        total = sum(r['observations'] for r in result['streams'])
        repeated = sum(r['repeated_observations'] for r in result['streams'])
        assert total == len(seen) + repeated
        result.update(passed=True,total_observations=total,unique_observations=len(seen),
                      repeated_observations=repeated,repeat_fraction=repeated/total)
    except Exception as error:
        result.update(error=str(error),traceback=traceback.format_exc())
    result.update(seconds=time.monotonic()-started,finished_unix=time.time(),peak_python_rss_bytes=peak_rss)
    with RESULT.open('x',encoding='utf-8',newline='\n') as handle:
        json.dump(result,handle,indent=2);handle.write('\n')
    print(json.dumps({k:result[k] for k in ('passed','seconds','peak_python_rss_bytes')}),flush=True)
    if not result['passed']:
        raise RuntimeError(result['error'])


if __name__ == '__main__':
    main()
