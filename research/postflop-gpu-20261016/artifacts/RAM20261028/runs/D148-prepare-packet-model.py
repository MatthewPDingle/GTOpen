import sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
H = ROOT / 'runs/D148-packet-model'
H.mkdir(exist_ok=False)
lengths = [0, 1, 2, 3, 7, 15, 16, 17, 31, 32, 33, 63, 64, 65, 127, 128, 129, 257, 511, 512, 513, 1023, 1024, 1326]
cases = []
for index in range(len(lengths)):
    blocks, source, host = [], 3, 5
    high = (1 << 32) + 17 if index % 2 else 0
    for j in range(7):
        length = lengths[(index + 3 * j) % len(lengths)]
        blocks.append({'source': high + source, 'host': host, 'length': length, 'node': 1 + 2 * j})
        source += length + 3
        host += length + 5
    for capacity in [7, 19, 67, 257, 2048, 8192]:
        for max_desc in [1, 3, 7]:
            cases.append({'blocks': blocks, 'source_len': high + source + 7, 'host_len': host + 7, 'scale_len': 19, 'cfv_words': capacity, 'staging_words': capacity + 7, 'max_desc': max_desc, 'salt': 0x5eed0000 + index})
assert len(cases) == 432
h.save(H / 'cases.json', cases)
valid = {'blocks': [{'source': 3, 'host': 5, 'length': 9, 'node': 1}], 'source_len': 32, 'host_len': 32, 'scale_len': 4, 'cfv_words': 100, 'staging_words': 100, 'max_desc': 3}
invalid = []
for field, value in [('source_len', -1), ('source_len', 1 << 63), ('host_len', -1), ('host_len', 1 << 63), ('max_desc', 0), ('cfv_words', -1), ('staging_words', 3), ('scale_len', 1)]:
    invalid.append({'reason': field, 'arguments': valid | {field: value}})
for field, value in [('source', -1), ('host', -1), ('length', -1), ('length', 1 << 32), ('source', (1 << 64) - 4), ('source', 30), ('host', 30), ('node', 4)]:
    invalid.append({'reason': field, 'arguments': valid | {'blocks': [valid['blocks'][0] | {field: value}]}})
invalid.append({'reason': 'duplicate scale owner', 'arguments': valid | {'blocks': valid['blocks'] * 2}})
invalid.append({'reason': 'overlapping host output', 'arguments': valid | {'blocks': valid['blocks'] + [{'source': 20, 'host': 9, 'length': 3, 'node': 2}]}})
invalid.append({'reason': 'overlapping source ownership', 'arguments': valid | {'blocks': valid['blocks'] + [{'source': 9, 'host': 20, 'length': 3, 'node': 2}]}})
h.save(H / 'invalid-cases.json', invalid)
script = ROOT / 'runs/D148-packet-model.py'
compile(script.read_text(encoding='utf-8'), str(script), 'exec')
files = [Path(__file__), script, H / 'cases.json', H / 'invalid-cases.json', ROOT / 'runs/D148-packed-readback-design/design-review.json', ROOT / 'epoch/common.py', ROOT / 'epoch/accepted-source.json', ROOT / 'epoch/protected-main.json']
h.save(H / 'protocol.json', {'id': 'D148-packet-model', 'at': h.now(), 'status': 'FROZEN_PRE_MODEL_EXECUTION', 'cases': 432, 'invalid_cases': len(invalid), 'input_sha256': {str(p): h.sha(p) for p in files}, 'scope': 'One fixed finite CPU model, independent direct host scatter, every physical host/scratch guard word, odd tails and injected output-corruption witnesses. High source offsets modeled as integers; no GPU allocation or FP quantization is implied. No extensions or source variants after a real model failure. No application kernel before this model passes.'})
print(h.sha(H / 'protocol.json'), flush=True)
