"""Audit the terminal physical pilot before admitting its fresh-deal evaluation.

Reads completed artifacts only. Never resumes training or starts evaluation.
"""
import json
from pathlib import Path
import time

import psutil

from loopback_research_validation import idle
from sampled_physical_pilot_audit_v1 import OUT, PREFIX, audit
from sampled_physical_root_evaluation_v1 import ROOT, sha, save


def main():
    started = time.monotonic()

    def guard():
        assert time.monotonic() - started < 600, 'Independent audit deadline'
        assert idle(), 'Production activity; defer independent audit'
        assert psutil.virtual_memory().available >= 20_000_000_000

    guard()
    regpath = OUT / (PREFIX + '-registration.json')
    statuspath = OUT / (PREFIX + '-status.json')
    resourcepath = OUT / (PREFIX + '-resources.json')
    admissionpath = OUT / (PREFIX + '-admission.json')
    reg = json.loads(regpath.read_text())
    status = json.loads(statuspath.read_text())
    assert status['state'] in ('complete', 'stopped'), 'Pilot is not terminal'
    store = Path(reg['store'])
    latestpath = store / 'latest.json'
    latest = json.loads(latestpath.read_text())
    completed = latest['completed_iterations']
    assert completed > 0
    assert not (ROOT / 'research/preflop-evolution/representative-coverage-20260919/running.lock').exists()
    # A status file alone is insufficient evidence that all research work ended.
    controller = ROOT / 'tools/research/hu_sampled_physical_pilot_20260922.py'
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if not (process.info['name'] or '').lower().startswith('python'):
            continue
        command = process.info['cmdline'] or []
        assert not any(Path(arg).name == controller.name for arg in command[1:]), (
            'Pilot controller or worker is still present', process.info['pid'])

    resources = json.loads(resourcepath.read_text())
    assert resources and all(b['seconds'] > a['seconds'] for a, b in zip(resources, resources[1:]))
    assert all(r['free_host_bytes'] >= reg['host_reserve_bytes']
               and r['free_gpu_bytes'] >= reg['gpu_reserve_bytes']
               and r['free_disk_bytes'] >= reg['disk_reserve_bytes']
               and r['store_bytes'] <= reg['maximum_store_bytes'] for r in resources)
    # The controller's total_seconds includes its queue wait. Do not use it as
    # execution time. Admission is written after the execution clock starts;
    # compare that wall-clock boundary with execution-relative resource records.
    publication_elapsed = statuspath.stat().st_mtime - admissionpath.stat().st_mtime
    cap = reg['maximum_seconds']
    budget_exhausted = False
    if status['state'] == 'complete':
        assert status['error'] is None and status['exit_code'] == 0
        assert completed == reg['config']['max_iterations']
    else:
        assert status['error'] == 'Execution deadline or production activity', status
        assert publication_elapsed >= cap, 'Wall-clock evidence does not establish execution cap'
        assert cap - 15 <= resources[-1]['seconds'] < cap, 'Missing near-deadline resource evidence'
        budget_exhausted = True

    evidence_paths = [regpath, statuspath, resourcepath, admissionpath, latestpath,
                      Path(__file__), ROOT / 'tools/research/sampled_physical_pilot_audit_v1.py']
    hashes = {str(p): sha(p) for p in evidence_paths}
    result = audit(completed, guard)
    assert result['checkpoint'] == latest['checkpoint']
    assert result['completed_prefix_verified']
    for path, expected in hashes.items():
        assert sha(path) == expected, path
    guard()
    result.update(
        passed=True,
        pilot_status_sha256=hashes[str(statuspath)],
        pilot_latest_sha256=hashes[str(latestpath)],
        all_published_iterations_verified=True,
        budget_exhaustion_verified=budget_exhausted,
        terminal_state=status['state'],
        terminal_error=status['error'],
        stop_evidence=dict(
            maximum_execution_seconds=cap,
            terminal_publication_minus_admission_seconds=publication_elapsed,
            last_resource_execution_seconds=resources[-1]['seconds'],
            note='Wall-clock publication timestamps corroborate the execution-relative resource records and the controller deadline assertion. Queue-inclusive total_seconds is not execution time.'),
        resource_summary=dict(
            samples=len(resources),
            minimum_free_host_bytes=min(r['free_host_bytes'] for r in resources),
            minimum_free_gpu_bytes=min(r['free_gpu_bytes'] for r in resources),
            minimum_free_disk_bytes=min(r['free_disk_bytes'] for r in resources),
            maximum_store_bytes=max(r['store_bytes'] for r in resources)),
        excluded_iteration_directories=[p.name for p in sorted(store.glob('iteration-*'))
                                        if p.is_dir() and int(p.name.split('-')[-1]) > completed],
        evidence_hashes=hashes,
        review_seconds=time.monotonic() - started,
        accuracy_qualified=False,
        evaluation_admission_only=True)
    destination = OUT / (PREFIX + '-independent-review.json')
    save(destination, result)
    print(json.dumps(dict(passed=True, review=str(destination), completed_iterations=completed,
                          budget_exhaustion_verified=budget_exhausted,
                          fresh_deals_replayed=result['fresh_deals_replayed'],
                          review_seconds=result['review_seconds'])))


if __name__ == '__main__':
    main()
