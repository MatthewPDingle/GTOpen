"""Review direct GPU restore/gather against complete resident state, before edits."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[2]
STUDY=ROOT/'research/preflop-evolution/ssd-storage-20260920'
OUT=STUDY.parent/'representative-coverage-20260919'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    freeze=json.loads((STUDY/'gpu-stored-v3-runtime-freeze.json').read_text())
    for path,digest in freeze['inputs'].items():assert sha(ROOT/path)==digest,path
    exe=Path(freeze['executable']);assert sha(exe)==freeze['executable_sha256']
    status=json.loads((OUT/'gpu-stored-v3-diagnostic-status.json').read_text())
    assert status['exit_code']==0 and status['error'] is None
    log=(OUT/'gpu-stored-v3-diagnostic.log').read_text()
    assert 'test result: ok. 1 passed; 0 failed;' in log
    rows=[json.loads(line.split('GPU_STORED_PASS ',1)[1]) for line in log.splitlines() if 'GPU_STORED_PASS {' in line]
    assert len(rows)==720 and all(r['passed'] is True for r in rows)
    assert {(r['entry'],r['iteration'],r['player']) for r in rows}=={(e,t,p) for e in range(6) for t in range(1,61) for p in range(2)}
    summaries=[json.loads(line.split('GPU_STORED_SUMMARY ',1)[1]) for line in log.splitlines() if 'GPU_STORED_SUMMARY {' in line]
    assert len(summaries)==1
    summary=summaries[0]
    assert all(summary[k] is True for k in ['full_device_arrays_bitwise_equal','restored_arrays_bitwise_equal','values_bitwise_equal'])
    retained=ROOT/'target/qualified-paging/gpu-stored-v3-diagnostic.exe'
    assert not retained.exists();shutil.copyfile(exe,retained);assert sha(retained)==sha(exe)
    resources=json.loads((OUT/'gpu-stored-v3-diagnostic-resources.json').read_text())
    result=dict(passed=True,summary=summary,guard=status,retained_executable=str(retained),retained_sha256=sha(retained),
        sampled_free_host_min=min(r['free_host_bytes'] for r in resources),
        sampled_free_gpu_min=min(r['free_gpu_bytes'] for r in resources),
        scope='Six small games, 720 alternating player passes; full device arrays, reconstructed CPU arrays and returned CFVs exactly matched.',
        production_ready=False,larger_connected_qualified=False,
        log_sha256=sha(OUT/'gpu-stored-v3-diagnostic.log'))
    with (STUDY/'gpu-stored-v3-review.json').open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
