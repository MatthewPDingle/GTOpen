"""Audit the 47-board feasibility trial; estimate cost without approving strategy."""
import json
from pathlib import Path
import integrated_coverage_review as review

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/representative-coverage-20260919'


def main():
    data = json.loads((OUT/'report47-trial-result.json').read_text())
    status = json.loads((OUT/'report47-trial-status.json').read_text())
    resources = json.loads((OUT/'report47-trial-resources.json').read_text())
    assert status['exit_code'] == 0 and status['error'] is None
    assert len(data['boards']) == 47 and data['records'][-1]['iteration'] == 20
    assert data['manifest'] == json.loads((OUT/'report-47.json').read_text())
    audit = review.audit_result(data)
    first, last = data['records'][0], data['records'][-1]
    # Includes the second checkpoint evaluation. Conservative for sparse
    # checkpointing, but this short extrapolation is not a timing guarantee.
    seconds_per_iteration = (last['elapsed_seconds']-first['elapsed_seconds'])/(last['iteration']-first['iteration'])
    assert seconds_per_iteration > 0
    host = min(r['free_host_bytes'] for r in resources)
    gpu = min(r['free_gpu_bytes'] for r in resources)
    assert host >= 20_000_000_000 and gpu >= 3_000_000_000
    result = dict(passed=True, accounting=audit, minimum_free_host_bytes=host,
                  minimum_free_gpu_bytes=gpu, seconds_per_iteration=seconds_per_iteration,
                  estimated_2000_iteration_seconds=first['elapsed_seconds']+1999*seconds_per_iteration,
                  workspace_bytes=data['workspace_bytes'], transferred_bytes=data['transferred_bytes'],
                  note='Short-run feasibility only. The 20-iteration policy is not an accuracy result; extrapolated time is uncertain.')
    output = OUT/'report47-trial-review.json'
    assert not output.exists()
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
