"""Publish passed all-node model software components without admitting a trial."""
import ast
import hashlib
import json
from pathlib import Path

STAGE = Path(__file__).parent
REPO = Path(r'T:\Dev\GTOpen')
TOOLS = REPO/'tools/research'
OUT = REPO/'research/preflop-evolution/blind-defense-20260922'

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def put(path, raw):
    if path.exists():
        if path.read_bytes() != raw: raise ValueError('Conflicting retained artifact: '+str(path))
    else:
        with path.open('xb') as stream: stream.write(raw)
    return sha(path)

def main():
    names = ['preflop-expected-policy-check-v1-result.json', 'preflop-expected-policy-cuda-check-v1-result.json']
    for name in names:
        value = json.loads((STAGE/name).read_bytes())
        assert value['passed'] and not value['scientific_attempt'] and not value['accuracy_qualified']
        for path, expected in value['inputs'].items(): assert sha(path) == expected, path
    code = ['preflop_expected_policy_v1.py', 'preflop_expected_native_targets_v2.py',
            'preflop_expected_policy_check_v1.py', 'preflop_expected_policy_cuda_check_v1.py']
    outputs = {}
    for name in code:
        raw = (STAGE/name).read_bytes(); ast.parse(raw)
        outputs[str(TOOLS/name)] = put(TOOLS/name, raw)
        outputs[str(OUT/(Path(name).stem+'-staging.py'))] = put(OUT/(Path(name).stem+'-staging.py'), raw)
    for name in names:
        target = OUT/(Path(name).stem+'-staging.json')
        outputs[str(target)] = put(target, (STAGE/name).read_bytes())
    outputs[str(OUT/Path(__file__).name)] = put(OUT/Path(__file__).name, Path(__file__).read_bytes())
    value = dict(passed=True, inputs={str(STAGE/name):sha(STAGE/name) for name in code+names}, outputs=outputs,
        publication='Byte-for-byte copies; control result paths supplied explicitly.',
        scientific_attempt=False, production_modified=False, published_controls_still_required=True)
    put(OUT/'preflop-expected-policy-publication-v1.json', json.dumps(value, indent=2, allow_nan=False).encode())
    print(json.dumps(dict(passed=True, copied=len(outputs))))

if __name__ == '__main__': main()
