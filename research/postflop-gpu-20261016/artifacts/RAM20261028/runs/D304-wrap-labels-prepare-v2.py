import ast, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
H = ROOT / 'runs/D304-tracker-display-metadata'
old = ROOT / 'runs/D304-wrap-validation-labels.py'
new = ROOT / 'runs/D304-wrap-validation-labels-v2.py'
h.save(H / 'layout-preparation-v1.json', {'at': h.now(), 'error': 'Original preparer assumed HTML CRLF; actual existing index has189LF/0CRLF. Assertion stopped before backup or mutation. Source and original script retained.',
    'script_sha256': h.sha(old), 'index_sha256': h.sha(h.ar.DASHBOARD / 'index.html'),
    'repair': 'V2 uses existing LF for the single inserted CSS line. No data/solver/native changes.'})
code = old.read_text(encoding='utf-8')
code = code.replace("assert before.count(b'\\n') == before.count(b'\\r\\n')", "assert before.count(b'\\r\\n') == 0")
code = code.replace("overflow-wrap:anywhere}\\r\\n'", "overflow-wrap:anywhere}\\n'")
ast.parse(code)
with new.open('xb') as stream:
    stream.write(code.encode())
print(new, flush=True)
