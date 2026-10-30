"""Review exact SSD fixture evidence; run before changing frozen source files."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT/'research/preflop-evolution/ssd-storage-20260920'
OUT = STUDY.parent/'representative-coverage-20260919'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    runtime = json.loads((STUDY/'ssd-paging-v1-runtime-freeze.json').read_text())
    for p, expected in runtime['inputs'].items():
        assert sha(ROOT/p) == expected, p
    exe = Path(runtime['executable'])
    assert sha(exe) == runtime['executable_sha256']
    status = json.loads((OUT/'ssd-paging-v1-diagnostic-status.json').read_text())
    assert status['exit_code'] == 0 and status['error'] is None
    log = (OUT/'ssd-paging-v1-diagnostic.log').read_text()
    assert 'test result: ok. 2 passed; 0 failed;' in log
    rows = [json.loads(x.split('SSD_PAGING ',1)[1]) for x in log.splitlines() if 'SSD_PAGING {' in x]
    assert len(rows) == 720
    expected = {(e,t,p) for e in range(6) for t in range(1,61) for p in range(2)}
    assert {(r['entry'],r['iteration'],r['player']) for r in rows} == expected
    for row in rows:
        assert all(row[k] is True for k in ['passed','arrays_bitwise_equal','values_bitwise_equal','park_restore_bitwise_equal'])
    summaries = [json.loads(x.split('SSD_PAGING_SUMMARY ',1)[1]) for x in log.splitlines() if 'SSD_PAGING_SUMMARY {' in x]
    assert len(summaries) == 1
    summary = summaries[0]
    assert summary['failures'] == 0 and summary['passes'] == 720
    assert summary['read_payload_bytes'] == 2*summary['write_payload_bytes']
    assert summary['unused_candidate_pinned_staging_released'] is True
    assert 'SSD_FORMAT_CHECKS {"passed":true,"checks":9}' in log
    retained = ROOT/'target/qualified-paging/ssd-paging-v1-diagnostic.exe'
    assert not retained.exists()
    shutil.copyfile(exe,retained)
    assert sha(retained) == runtime['executable_sha256']
    resources = json.loads((OUT/'ssd-paging-v1-diagnostic-resources.json').read_text())
    result = dict(passed=True,summary=summary,guard=status,
        minimum_sampled_free_host_bytes=min(x['free_host_bytes'] for x in resources),
        minimum_sampled_free_gpu_bytes=min(x['free_gpu_bytes'] for x in resources),
        retained_executable=str(retained),retained_executable_sha256=sha(retained),
        production_ready=False,integrated_game_qualified=False,
        evidence_sha256={str(p.relative_to(ROOT)):sha(p) for p in [
            OUT/'ssd-paging-v1-diagnostic.log',OUT/'ssd-paging-v1-diagnostic-status.json',
            STUDY/'ssd-paging-v1-runtime-freeze.json']})
    with (STUDY/'ssd-paging-v1-review.json').open('x') as f:
        json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
