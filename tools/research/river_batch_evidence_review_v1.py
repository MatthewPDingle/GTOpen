"""Seal and read back the two terminal river batch cost experiments."""
import hashlib
import json
import os
from pathlib import Path
import time

OUT = Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
DEST = OUT / 'river-batch-evidence-review-v1.json'


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not DEST.exists()
    cases = []
    for name in ('river-learned-batch-cost-v1', 'river-shared-export-control-v1'):
        folder = OUT / name
        rp = OUT / (name + '-registration.json')
        result_path = OUT / (name + '-result.json')
        reg, result = read(rp), read(result_path)
        assert result['passed'] and result['complete']
        assert result['registration_sha256'] == sha(rp)
        assert not (OUT / (name + '-failure.json')).exists()
        assert not result['gpu_used'] and not result['training'] and not result['production_modified']
        for path, digest in reg['inputs'].items():
            assert sha(Path(path)) == digest, path
        assert len(result['cases']) == 8
        for case in result['cases']:
            assert read(folder / case['case'] / 'result.json') == case
            for path, digest in case.get('artifacts', {}).items():
                assert sha(folder / case['case'] / path) == digest
        for item in result.get('exports', []):
            assert sha(Path(item['path'])) == item['sha256']
        artifacts = {str(p.relative_to(folder)): dict(bytes=p.stat().st_size, sha256=sha(p))
                     for p in sorted(folder.rglob('*')) if p.is_file()}
        total = sum(a['bytes'] for a in artifacts.values())
        assert total < 512_000_000
        cases.append(dict(name=name, registration_sha256=sha(rp), result_sha256=sha(result_path),
                          retained_bytes=total, artifacts=artifacts, unchanged_inputs=len(reg['inputs'])))
    payload = dict(passed=True, reviewed_unix=time.time(), source_sha256=sha(Path(__file__)),
                   experiments=cases, scope='Terminal evidence integrity and archive manifest; no new quality test.')
    raw = (json.dumps(payload, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()
    with DEST.open('xb') as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())
    assert read(DEST) == payload
    print(json.dumps(dict(passed=True, experiments=len(cases),
                          files=sum(len(c['artifacts']) for c in cases),
                          retained_bytes=sum(c['retained_bytes'] for c in cases))))


if __name__ == '__main__':
    main()
