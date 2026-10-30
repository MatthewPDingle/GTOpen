import ast, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
H = ROOT / 'runs/D301-predicated-correction-native'
old = ROOT / 'runs/D301-predicated-correction-native-reader.py'
new = ROOT / 'runs/D301-predicated-correction-native-reader-v2.py'
h.save(H / 'reader-v1-observer-failure.json', {
    'at': h.now(), 'script_sha256': h.sha(old),
    'protocol_sha256': h.sha(H / 'reader-protocol.json'),
    'error': 'AssertionError at assert bad != text: first negative fixture used nineteen literal spaces; nvdisasm emits fifteen before @P1 at PC1ea0.',
    'positive_inspection_completed': True,
    'scope': 'Observer negative-fixture text anchoring repair only. Original source, captures and v1 protocol retained. No compiler/module/native kernel/solver/timing repeat.'})
code = old.read_text().replace("'reader-protocol.json'", "'reader-protocol-v2.json'")
needle = "text.replace('/*1ea0*/                   ' + load, '/*1ea0*/                   ' + changed, 1)"
replacement = "re.sub(r'(/\\*1ea0\\*/\\s*)' + re.escape(load), lambda match: match[1] + changed, text, count=1)"
assert code.count(needle) == 1
code = code.replace(needle, replacement)
ast.parse(code)
with new.open('xb') as f:
    f.write(code.encode())
print(new, flush=True)
