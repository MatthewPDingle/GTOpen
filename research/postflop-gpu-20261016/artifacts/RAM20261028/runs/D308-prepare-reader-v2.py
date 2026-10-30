"""Normalize ignored reuse hints in negative fixtures before first execution."""
import ast, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
H = ROOT / 'runs/D308-packed-arithmetic'
old = ROOT / 'runs/D308-native-reader.py'
new = ROOT / 'runs/D308-native-reader-v2.py'
h.save(H / 'reader-preflight-v1.json', {'at': h.now(), 'original_reader_sha256': h.sha(old),
    'original_protocol_sha256': h.sha(H / 'reader-protocol.json'), 'reader_v1_executed': False,
    'observation': 'Pre-execution review found native .reuse hints are ignored by positive parser but remain in raw text used for negative string mutation. First subtraction has .reuse, so literal mutation would be unchanged.',
    'repair': 'V2 removes only .reuse hints from negative-fixture text after positive original-file inspection. Actual captured files and all positive cases/constraints unchanged; no source/compiler/module/native/solver/performance repeat.'})
code = old.read_text(encoding='utf-8').replace("'reader-protocol.json'", "'reader-protocol-v2.json'")
needle = "first = result['packed_regret_pair']"
assert code.count(needle) == 1
code = code.replace(needle, "text = re.sub(r'\\.reuse\\b', '', text)\n" + needle)
needle = "files = [Path(__file__), H / 'protocol.json',"
assert code.count(needle) == 1
code = code.replace(needle, "files = [Path(__file__), H / 'reader-protocol.json', H / 'reader-preflight-v1.json', ROOT / 'runs/D308-native-reader.py', H / 'protocol.json',")
ast.parse(code)
with new.open('xb') as stream:
    stream.write(code.encode())
print(new, flush=True)
