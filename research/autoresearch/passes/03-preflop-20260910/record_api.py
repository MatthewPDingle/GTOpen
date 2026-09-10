"""Publish completed private-server evidence without copying native saves."""
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RUN_ID = 'api-first-strategy-eight-a'
SOURCE = ROOT / 'target/autoresearch/preflop-20260910/target/research-api-qualification' / RUN_ID


def main():
    summary = json.loads((SOURCE / 'summary.json').read_text())
    if summary.get('full_native_exact') is not True or summary.get('native_iteration') != 50:
        raise ValueError('API qualification is incomplete or nonexact')
    summary['publication_intervals_seconds'] = {}
    copies = []
    for side in ('original', 'candidate'):
        result = json.loads((SOURCE / side / 'result.json').read_text())
        if result.get('completed') is not True or result.get('error') or result.get('guard_failures'):
            raise ValueError('API case failed: ' + side)
        summary['publication_intervals_seconds'][side] = {
            'lower': result['publication_interval_lower_seconds'],
            'upper': result['publication_interval_upper_seconds'],
        }
        for filename, suffix in [('result.json', '.json'), ('server.log', '.log')]:
            copies.append((SOURCE / side / filename, HERE / 'raw' / (RUN_ID + '-' + side + suffix)))
    destination = HERE / (RUN_ID + '.json')
    if destination.exists() or any(target.exists() for _, target in copies):
        raise ValueError('Refusing to overwrite published API evidence')
    summary['evidence_files'] = [str(target.relative_to(HERE)).replace('\\', '/') for _, target in copies]
    for source, target in copies:
        shutil.copyfile(source, target)
    with destination.open('x', encoding='utf-8') as stream:
        json.dump(summary, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(destination)


if __name__ == '__main__':
    main()
