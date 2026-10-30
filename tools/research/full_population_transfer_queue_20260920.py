"""Bounded, separately registered population supplement; never changes production.

Run manually only after review of the four original comparisons. Reuse requires
the identical physical board, game, executable, source and completed 2,000 steps.
The original panel artifacts are read-only. --preflight performs no GPU work.
"""
from datetime import datetime
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil
import continuation_transfer_aggregate as aggregate
import integrated_coverage_review as accounting
from loopback_research_validation import idle

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/representative-coverage-20260919'
DEV = ROOT/'research/preflop-evolution/integrated-coverage-20260919'
SUB = ROOT/'research/preflop-evolution/conditional-hu-20260919/subtree.json'
EXE = ROOT/'target/release/examples/continuation_transfer_streamed.exe'
PROTOCOL = OUT/'POPULATION-SUPPLEMENT-RUNTIME.md'
DEADLINE = datetime.fromisoformat('2026-09-20T09:00:00+09:30').timestamp()
SOURCES = {'ab': DEV/'panel-ab-result.json', 'report47': OUT/'report47-full-result.json'}
TRAINING_PANELS = {'ab': DEV/'panel-ab.json', 'report47': OUT/'report-47.json'}


def rel(path):
    return str(Path(path).relative_to(ROOT))


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_hashes(inputs):
    for path, digest in inputs.items():
        assert sha(ROOT/path) == digest, f'Changed registered input: {path}'


def verify_previous_aggregate(result, paths):
    for path in paths:
        assert result['inputs_sha256'][rel(path)] == sha(path), f'Changed original aggregate input: {path}'


def validate_worker(prefix, board, source, frozen):
    """Validate existing artifacts without relabeling or changing their weights."""
    status = read(OUT/(prefix+'-status.json'))
    assert status['exit_code'] == 0 and status['error'] is None, prefix
    freeze = read(OUT/(prefix+'-freeze.json'))
    for path in [EXE, SUB, source]:
        assert freeze['inputs'][rel(path)] == frozen[rel(path)], prefix
    manifest_path = OUT/(prefix+'-manifest.json')
    assert freeze['inputs'][rel(manifest_path)] == sha(manifest_path), prefix
    manifest = read(manifest_path)
    assert len(manifest['boards']) == 1 and manifest['boards'][0]['board'] == board
    assert manifest['suit_orbits'] is True and manifest['bet_menu'] == '50'
    packed = OUT/(prefix+'-result.json.gz')
    raw = OUT/(prefix+'-result.json')
    if raw.exists():
        assert gzip.decompress(packed.read_bytes()) == raw.read_bytes(), prefix
    data = aggregate.read(packed)
    assert data['boards'] == [board] and data['manifest'] == manifest, prefix
    assert data['records'][-1]['iteration'] == 2000 and data['terminal_values'] is not None
    assert data['entry_cutoff'] == 1e-5 and data['preflop_unchanged'] is True
    expected = aggregate.policy_bits(read(source)['records'][-1]['evaluation']['preflop_policy'])
    for record in data['records']:
        assert aggregate.policy_bits(record['evaluation']['preflop_policy']) == expected, prefix
    accounting.audit_result(data)
    return packed


def preflight():
    assert read(OUT/'overnight-accuracy-status.json')['step'] == 'complete-awaiting-scientific-review'
    assert not (OUT/'overnight-accuracy.lock').exists(), 'Original parent still owns GPU queue'
    assert not (OUT/'running.lock').exists(), 'Research worker still active'
    original = read(OUT/'overnight-accuracy-v2-freeze.json')['inputs']
    verify_hashes(original)
    verify_hashes(read(OUT/'transfer-sources-freeze.json'))
    verify_hashes(read(OUT/'full-population-supplement-freeze.json')['inputs_sha256'])
    comparisons = read(OUT/'independent-transfer-summary.json')
    expected = {(p,s) for p in ['reserved10','validation95'] for s in SOURCES}
    assert len(comparisons) == 4 and {(x['panel'],x['source']) for x in comparisons} == expected
    for item in comparisons:
        assert 0 <= item['postflop_gap_total'] < .01
        prefix = f"held-{item['panel']}-{item['source']}-result"
        result = read(OUT/(prefix+'.json'))
        review = read(OUT/(prefix+'-review.json'))
        assert review['preflop_exactly_preserved'] is True and review['iteration'] == 2000
        accounting.audit_result(result)
        assert result['records'][-1]['evaluation']['postflop_gap_total'] == item['postflop_gap_total']
    ref = read(SOURCES['report47'])['records'][-1]
    assert ref['iteration'] == 2000 and ref['evaluation']['gap_total'] < .01
    files = [Path(__file__), PROTOCOL, SUB, EXE, *SOURCES.values(), *TRAINING_PANELS.values(),
             OUT/'supplement-excluded-69.json', OUT/'combined-population-164.json',
             OUT/'full-population-supplement-freeze.json', OUT/'transfer-sources-freeze.json',
             OUT/'overnight-accuracy-v2-freeze.json', OUT/'independent-transfer-summary.json',
             ROOT/'tools/research/continuation_transfer_aggregate.py',
             ROOT/'tools/research/continuation_transfer_review.py',
             ROOT/'tools/research/integrated_coverage_review.py',
             ROOT/'tools/research/loopback_research_validation.py',
             ROOT/'tools/research/paged_continuation_validation.py']
    frozen = {**original, **{rel(p):sha(p) for p in files}}
    reused = {}
    for source_name, source in SOURCES.items():
        reused[source_name] = {}
        for panel_name, panel in [('reserved10', DEV/'reserved.json'), ('validation95', OUT/'validation-95.json')]:
            prior = read(OUT/f'held-{panel_name}-{source_name}-result.json')
            verify_previous_aggregate(prior,[SUB,panel,source])
            for i, row in enumerate(read(panel)['boards']):
                prefix = f'held-{panel_name}-{source_name}-{i:03}'
                packed = validate_worker(prefix, row['board'], source, frozen)
                verify_previous_aggregate(prior,[packed])
                assert row['board'] not in reused[source_name]
                reused[source_name][row['board']] = rel(packed)
                for suffix in ['-result.json.gz','-manifest.json','-freeze.json','-status.json']:
                    path = OUT/(prefix+suffix)
                    frozen[rel(path)] = sha(path)
    excluded = read(OUT/'supplement-excluded-69.json')
    combined = read(OUT/'combined-population-164.json')
    assert len(excluded['boards']) == 69 and len(combined['boards']) == 164
    for name in SOURCES:
        assert read(SOURCES[name])['manifest'] == read(TRAINING_PANELS[name])
        assert sum(b['board'] not in reused[name] for b in excluded['boards']) == 59
        assert set(b['board'] for b in combined['boards']) == set(reused[name]) | set(b['board'] for b in excluded['boards'])
        assert {b['board'] for b in read(TRAINING_PANELS[name])['boards']} <= {b['board'] for b in excluded['boards']}
    return frozen, reused


def main():
    frozen, reused = preflight()
    if sys.argv[1:] == ['--preflight']:
        print(json.dumps(dict(passed=True, reused_workers=sum(map(len,reused.values())), additional_workers=118)))
        return
    assert not sys.argv[1:], 'Only --preflight is accepted'
    assert DEADLINE-time.time() >= 7200, 'Less than two hours left; do not start supplement'
    assert idle(), 'Production active'
    assert psutil.virtual_memory().available >= 20_000_000_000
    free_gpu = int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0])*1024**2
    assert free_gpu >= 3_000_000_000
    lock = OUT/'full-population-supplement.lock'
    with lock.open('x') as f:
        f.write(str(os.getpid()))

    def status(step, **extra):
        data = dict(step=step,pid=os.getpid(),updated_adelaide=datetime.now().astimezone().isoformat(),**extra)
        (OUT/'population-supplement-status.json').write_text(json.dumps(data,indent=2))
        print(json.dumps(data),flush=True)

    def run(step,args,gpu=False):
        # Source/implementation identity stays fixed throughout. Worker archive
        # hashes are rechecked at aggregation, avoiding repeated large reads.
        verify_hashes({p:d for p,d in frozen.items() if 'held-' not in p})
        assert time.time() < DEADLINE, '09:00 deadline reached'
        status(step)
        env = os.environ.copy()
        env['OPENBLAS_NUM_THREADS'] = '1'
        env['GTO_RESEARCH_PROTOCOL'] = rel(PROTOCOL)
        env['GTO_RESEARCH_MAX_SECONDS'] = str(min(900,DEADLINE-time.time()))
        # The production/resource guard owns and stops its GPU child. Never
        # time out that parent externally and leave an orphan GPU process.
        subprocess.run([sys.executable,*map(str,args)],cwd=ROOT,env=env,check=True,
                       timeout=None if gpu else min(300,DEADLINE-time.time()))

    try:
        freeze_path = OUT/'population-supplement-runtime-freeze.json'
        with freeze_path.open('x') as f:
            json.dump(dict(inputs=frozen,reused_workers=reused,deadline_adelaide='2026-09-20T09:00:00+09:30',
                           pid=os.getpid(),process_create_time=psutil.Process().create_time()),f,indent=2)
        excluded = read(OUT/'supplement-excluded-69.json')
        summary = []
        for source_name, source in SOURCES.items():
            workers = dict(reused[source_name])
            for i, board in enumerate(excluded['boards']):
                if board['board'] in workers:
                    continue
                label = f'population-extra-{source_name}-{i:03}'
                manifest = OUT/(label+'-manifest.json')
                with manifest.open('x') as f:
                    json.dump({**excluded,'boards':[board]},f,indent=2)
                output = OUT/(label+'-result.json')
                assert not output.exists()
                run(label,['tools/research/loopback_research_validation.py',rel(EXE),label,
                           rel(SUB),rel(manifest),rel(output),'2000',rel(source)],gpu=True)
                raw = output.read_bytes()
                compressed = gzip.compress(raw,mtime=0)
                assert gzip.decompress(compressed) == raw
                with output.with_suffix('.json.gz').open('xb') as f:
                    f.write(compressed)
                packed = validate_worker(label,board['board'],source,frozen)
                workers[board['board']] = rel(packed)
                frozen[rel(packed)] = sha(packed)
            verify_hashes(frozen)
            for panel_name, panel in [('excluded69',OUT/'supplement-excluded-69.json'),
                                     ('population164',OUT/'combined-population-164.json'),
                                     ('sourcepanel',TRAINING_PANELS[source_name])]:
                leaves = [workers[b['board']] for b in read(panel)['boards']]
                combined = OUT/f'{panel_name}-{source_name}-result.json'
                run(f'aggregate-{panel_name}-{source_name}',['tools/research/continuation_transfer_aggregate.py',
                    rel(SUB),rel(panel),rel(source),rel(combined),*leaves])
                run(f'review-{panel_name}-{source_name}',['tools/research/continuation_transfer_review.py',
                    rel(combined),rel(source),'heldout'])
                e = read(combined)['records'][-1]['evaluation']
                assert 0 <= e['postflop_gap_total'] < .01, 'Supplement postflop residual gate failed'
                summary.append(dict(panel=panel_name,source=source_name,
                    **{k:e[k] for k in ['ev','gaps','gap_total','postflop_gap_total','root_frequencies']}))
                (OUT/'population-supplement-summary.json').write_text(json.dumps(summary,indent=2))
        status('complete-awaiting-scientific-review',comparisons=len(summary))
    except Exception as ex:
        status('stopped-for-review',error=str(ex))
        raise
    finally:
        lock.unlink()


if __name__ == '__main__':
    main()
