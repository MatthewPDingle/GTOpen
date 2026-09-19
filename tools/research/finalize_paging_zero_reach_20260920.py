"""Verify and archive completed diagnostics without rerunning or changing them."""
import gzip
import hashlib
import json
from pathlib import Path
import paging_candidate_review as review

ROOT = Path(__file__).resolve().parents[2]
CAND = Path('T:/Dev/GTOpen-paging-research')
REL = Path('research/preflop-evolution/representative-coverage-20260919')
OUT = ROOT/REL
SYM = OUT.parent/'symmetric-bridge-20260919'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert read(OUT/'paging-candidate-qualification-status.json')['step'] == 'complete-passed-research-only'
    frozen = read(OUT/'paging-candidate-qualification-freeze.json')['inputs_absolute']
    for path, digest in frozen.items():
        assert sha(Path(path)) == digest, path
    paired = read(OUT/'paging-candidate-paired-review.json')
    for path, digest in paired['input_sha256'].items():
        assert sha(Path(path)) == digest, path
    baseline = OUT/'ownavg-fresh-baseline-result.json'
    candidate = CAND/REL/'ownavg-two-result.json'
    checked = review.compare(read(baseline), read(candidate))
    assert checked['passed'] and checked['scientific_content_sha256'] == paired['scientific_content_sha256']
    for root, label in [(OUT, 'ownavg-fresh-baseline'), (CAND/REL, 'ownavg-two'), (CAND/REL, 'ownavg-switch-test')]:
        status = read(root/(label+'-status.json'))
        assert status['exit_code'] == 0 and status['error'] is None
    assert '1 passed; 0 failed' in (CAND/REL/'ownavg-switch-test.log').read_text()
    resources = {}
    for root, label in [(OUT, 'ownavg-fresh-baseline'), (CAND/REL, 'ownavg-two')]:
        rows = read(root/(label+'-resources.json'))
        resources[label] = dict(samples=len(rows), minimum_free_host_bytes=min(r['free_host_bytes'] for r in rows),
                               minimum_free_gpu_bytes=min(r['free_gpu_bytes'] for r in rows))
        assert resources[label]['minimum_free_host_bytes'] >= 20_000_000_000
    archives = {}
    for source in [baseline, candidate]:
        archive = source.with_suffix('.json.gz')
        raw = source.read_bytes()
        if archive.exists():
            assert gzip.decompress(archive.read_bytes()) == raw
        else:
            archive.write_bytes(gzip.compress(raw, mtime=0))
        archives[str(archive)] = dict(sha256=sha(archive), decompressed_sha256=sha(source))
    b, c = paired['baseline_seconds'], paired['candidate_seconds']
    late = paired['late_interval_seconds']
    result = dict(passed=True, qualified_scope='Isolated full-F32 paged research continuation harness',
                  production_deployed=False, compact_qualified=False, host_storage_saving=False,
                  runtime_reduction_percent=100*(1-c/b), speed_factor=b/c,
                  late_interval_reduction_percent=100*(1-late['candidate']/late['baseline']),
                  arena_traffic_reduction_percent=100*(1-paired['arena_traffic_ratio']),
                  resources=resources, archives=archives,
                  timing_context='One sequential GPU-uncontended pair. CPU population diagnostics overlapped the early candidate phase and finished before its 500 checkpoint. Light host activity also occurred. No randomized repetitions or uncertainty estimate; historical baseline was slower than the fresh baseline. The generated paired review uses uncontended to mean no competing research GPU solve, not a completely idle host.',
                  evidence_sha256={str(p):sha(p) for p in [OUT/'paging-candidate-exact-review.json', OUT/'paging-candidate-paired-review.json', OUT/'paging-candidate-qualification-status.json', CAND/REL/'ownavg-switch-test.log']})
    with (OUT/'paging-final-qualification.json').open('x') as f:
        json.dump(result, f, indent=2)
    runtime = read(SYM/'zero-reach-runtime-freeze.json')
    for path, digest in runtime['inputs'].items():
        assert sha(ROOT/path) == digest, path
    assert sha(Path(runtime['executable'])) == runtime['executable_sha256']
    assert sha(SYM/'zero-reach-build.log') == runtime['build_log_sha256']
    assert read(SYM/'zero-reach-build-status.json')['exit_code'] == 0
    status = read(OUT/'zero-reach-contract-diagnostic-status.json')
    assert status['exit_code'] == 0 and status['error'] is None
    log = OUT/'zero-reach-contract-diagnostic.log'
    cases = [json.loads(line.split('ZERO_REACH ', 1)[1]) for line in log.read_text().splitlines() if 'ZERO_REACH ' in line]
    assert len(cases) == 2 and {r['mode'] for r in cases} == {'zero_opponent', 'zero_own'}
    assert all(r['passed'] for r in cases) and '1 passed; 0 failed' in log.read_text()
    with (SYM/'zero-reach-contract-review.json').open('x') as f:
        json.dump(dict(passed=True, cases=cases, compact_qualified=False, solver_core_changed=False,
                       conclusion='The existing CPU zero-opponent pruning rule and unpruned GPU average accumulation differ. This diagnostic does not select the desired contract or resolve the smooth compact trajectory failures.',
                       evidence_sha256={str(p):sha(p) for p in [log, SYM/'zero-reach-runtime-freeze.json', SYM/'zero-reach-build-status.json', OUT/'zero-reach-contract-diagnostic-status.json']}), f, indent=2)
    print(json.dumps({k:result[k] for k in ['runtime_reduction_percent','late_interval_reduction_percent','arena_traffic_reduction_percent','resources']}))


if __name__ == '__main__':
    main()
