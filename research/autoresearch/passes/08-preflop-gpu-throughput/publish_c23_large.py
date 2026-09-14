"""Publish verified provisional large timing; never mark C23 retained here."""
import json
from run_c23 import HERE, RAW, read

verified = read(RAW/'c23-large-repeats-verified.json')
assert verified['passed_timing'] and not verified['retained']
verified['waiting_reason'] = 'Live idle guard refused small screening before launch: a new user preflop solve was running. No small benchmark process started.'
(RAW/'c23-verified.json').write_text(json.dumps(verified, indent=2)+'\n', encoding='utf-8')
path = HERE/'experiments.json'
original = path.read_bytes()
data = json.loads(original)
entry = next(row for row in data if row['id'] == 'c23')
entry.pop('kind', None)
entry['detail'] = 'Three exact large-game pairs passed: 61.41/60.74/60.66s control versus 52.45/52.26/52.48s candidate; median 13.95% less time. All 529,900,514 arena entries fingerprint and six gap/EV checkpoints match. Small-game timing and native/default regressions remain pending; guard yielded to new user work. Not retained or deployed.'
text = json.dumps(data, indent=2, ensure_ascii=False)+'\n'
if b'\r\n' in original:
    text = text.replace('\n', '\r\n')
path.write_bytes(text.encode('utf-8'))
