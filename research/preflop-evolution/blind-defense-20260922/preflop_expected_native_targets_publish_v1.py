"""Publish already-passed software evidence; no scientific job or production change."""
import ast
import hashlib
import json
from pathlib import Path

STAGE = Path(__file__).parent
REPO = Path(r'T:\Dev\GTOpen')
TOOLS = REPO/'tools/research'
OUT = REPO/'research/preflop-evolution/blind-defense-20260922'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def put(path, raw):
    if path.exists():
        if path.read_bytes() != raw:
            raise ValueError('Conflicting retained artifact: '+str(path))
    else:
        with path.open('xb') as stream:
            stream.write(raw)
    return sha(path)

def main():
    result_path = STAGE/'preflop-expected-native-targets-check-v2-result.json'
    result = json.loads(result_path.read_bytes())
    assert result['passed'] and not result['scientific_attempt'] and not result['accuracy_qualified']
    for path, expected in result['inputs'].items():
        assert sha(path) == expected, path
    copies = {'preflop_expected_native_targets_v1.py': TOOLS/'preflop_expected_native_targets_v1.py'}
    for name in ('preflop_expected_native_targets_check_v1.py',
                 'preflop-expected-native-targets-check-v1-failure.json',
                 'preflop_expected_native_targets_check_v2.py',
                 'preflop-expected-native-targets-check-v2-result.json'):
        copies[name] = OUT/(Path(name).stem+'-staging'+Path(name).suffix)
    for stack in (20, 200):
        for suffix in ('request', 'started', 'result', 'tree'):
            name = f'preflop-native-software-template-stack-{stack}-{suffix}.json'
            copies[name] = OUT/name
    outputs = {}
    for name, target in copies.items():
        raw = (STAGE/name).read_bytes()
        if target.suffix == '.py': ast.parse(raw)
        outputs[str(target)] = put(target, raw)
    control = (STAGE/'preflop_expected_native_targets_check_v2.py').read_text(encoding='utf-8')
    old = 'STAGE = Path(__file__).parent'
    assert control.count(old) == 1
    control = control.replace(old, "import argparse\n_parser = argparse.ArgumentParser()\n_parser.add_argument('--evidence-dir', type=Path, required=True)\n_parser.add_argument('--result', type=Path, required=True)\n_args = _parser.parse_args()\nSTAGE = _args.evidence_dir.resolve()\nRESULT = _args.result.resolve()")
    control = control.replace("path = STAGE/'preflop-expected-native-targets-check-v2-result.json'", 'path = RESULT')
    control = control.replace("failure = STAGE/'preflop-expected-native-targets-check-v2-failure.json'", "failure = RESULT.with_name(RESULT.stem+'-failure.json')")
    control = control.replace("sha(STAGE/'preflop_expected_native_targets_v1.py')", "sha(TOOLS/'preflop_expected_native_targets_v1.py')")
    ast.parse(control)
    target = TOOLS/'preflop_expected_native_targets_check_v3.py'
    outputs[str(target)] = put(target, control.encode('utf-8'))
    receipt = dict(passed=True, inputs={str(STAGE/name):sha(STAGE/name) for name in copies},
        outputs=outputs, source_sha256=sha(__file__),
        source_publication_changes='Control output/evidence destinations only; provider copied byte-for-byte.',
        scientific_attempt=False, production_modified=False, published_control_still_required=True)
    put(OUT/Path(__file__).name, Path(__file__).read_bytes())
    put(OUT/'preflop-expected-native-targets-publication-v1.json',
        json.dumps(receipt, indent=2, allow_nan=False).encode('utf-8'))
    print(json.dumps(dict(passed=True, copied=len(outputs), published_control_still_required=True)))

if __name__ == '__main__':
    main()
