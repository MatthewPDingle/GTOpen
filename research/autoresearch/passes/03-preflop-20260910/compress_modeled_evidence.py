"""Losslessly package generated model evidence for GitHub's file-size limit."""
import gzip
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
RAW = (HERE / 'raw').resolve()
IDS = ['api-auto-modeled-b', 'api-modeled23000-a']


def digest(stream):
    result = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
        result.update(chunk)
    return result.hexdigest()


def main():
    rows = []
    for run_id in IDS:
        for side in ['candidate', 'original']:
            path = (RAW / (run_id + '-' + side + '.json')).resolve()
            if path.parent != RAW:
                raise ValueError('Evidence path escaped the intended raw directory')
            target = path.with_suffix('.json.gz')
            size = path.stat().st_size
            with path.open('rb') as original:
                original_hash = digest(original)
            with path.open('rb') as original, target.open('xb') as output:
                with gzip.GzipFile(filename='', mode='wb', fileobj=output, mtime=0) as compressed:
                    shutil.copyfileobj(original, compressed)
            with gzip.open(target, 'rb') as verified:
                if digest(verified) != original_hash:
                    raise ValueError('Lossless verification failed: ' + str(target))
            with target.open('rb') as compressed:
                compressed_hash = digest(compressed)
            rows.append({'file': target.name, 'original_bytes': size,
                         'original_sha256': original_hash, 'compressed_bytes': target.stat().st_size,
                         'compressed_sha256': compressed_hash, 'decompressed_bytes_exact': True})
            # This is only the generated publication copy. The immutable original
            # qualification.json remains in its private research run directory.
            path.unlink()
        compact = HERE / (run_id + '.json')
        value = json.loads(compact.read_text())
        value['raw_evidence'] = [name + '.gz' if name.endswith('.json') else name for name in value['raw_evidence']]
        compact.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    with (HERE / 'modeled-evidence-compression.json').open('x', encoding='utf-8') as stream:
        json.dump(rows, stream, indent=2)
        stream.write('\n')
    print(json.dumps(rows, indent=2))


if __name__ == '__main__':
    main()
