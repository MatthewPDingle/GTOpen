"""Copy small, completed qualification evidence; retain native files privately."""
import argparse
import json
from pathlib import Path
import re
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run_id')
    args = parser.parse_args()
    if not re.fullmatch(r'api-[a-z0-9-]+', args.run_id):
        raise ValueError('Invalid run ID')
    source = ROOT / 'target/autoresearch/preflop-20260910/target/research-api-qualification' / args.run_id
    summary = json.loads((source / 'summary.json').read_text())
    if summary.get('outcome') == 'incomplete' or not summary.get('finished_utc'):
        raise ValueError('Qualification has not finished')
    summary['interpretation'] = 'One short API/budget qualification, not a general speed or convergence estimate.'
    summary['cases'] = {}
    copies = []
    for side in ('candidate', 'original'):
        result_file = source / side / 'qualification.json'
        if not result_file.exists():
            continue
        result = json.loads(result_file.read_text())
        summary['cases'][side] = {key: result.get(key) for key in (
            'completed', 'error', 'guard_failures', 'timed_out', 'loaded_native_exact',
            'api_native_profile_first_difference', 'first_published_checkpoint_seconds',
            'publication_interval_lower_seconds', 'publication_interval_upper_seconds', 'layout')}
        for filename, suffix in [('qualification.json', '.json'), ('server.log', '.log')]:
            copies.append((source / side / filename, HERE / 'raw' / (args.run_id + '-' + side + suffix)))
    resolved = source / 'original-resolved-budget.json'
    if resolved.exists():
        summary['original_resolved_budget'] = json.loads(resolved.read_text())
    target = HERE / (args.run_id + '.json')
    if target.exists() or any(destination.exists() for _, destination in copies):
        raise ValueError('Refusing to overwrite qualification evidence')
    summary['raw_evidence'] = [str(destination.relative_to(HERE)).replace('\\', '/') for _, destination in copies]
    for path, destination in copies:
        shutil.copyfile(path, destination)
    with target.open('x', encoding='utf-8') as stream:
        json.dump(summary, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(target)


if __name__ == '__main__':
    main()
