"""Pre-execution reader robustness: libtest may prefix the printed marker."""
import ast, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
H = ROOT / 'runs/D269-host-layout'
assert not (H / 'execution').exists()
original = ROOT / 'runs/D269-execute-host-layout.py'
text = original.read_text(encoding='utf-8')
assert text.count("if line.startswith('D269_LAYOUT ')") == 1
text = text.replace("if line.startswith('D269_LAYOUT ')", "if 'D269_LAYOUT ' in line")
text = text.replace("H / 'protocol.json'", "H / 'protocol.v2.json'")
ast.parse(text)
dest = ROOT / 'runs/D269-execute-host-layout-v2.py'
with dest.open('x', encoding='utf-8', newline='\n') as f:
    f.write(text)
P = h.read(H / 'protocol.json')
P.update(at=h.now(), status='FROZEN_PRE_FULL_CRATE_HOST_TYPECHECK_READER_PREFLIGHT')
P['reader_preflight'] = {'prior_protocol_sha256': h.sha(H / 'protocol.json'), 'change': 'Accept exact marker after optional libtest name prefix; no command, scientific source, case, gate or output change. Zero compilers/helpers executed before refreeze.'}
P['input_sha256'].update({str(dest): h.sha(dest), str(Path(__file__)): h.sha(__file__), str(H / 'protocol.json'): h.sha(H / 'protocol.json')})
h.save(H / 'protocol.v2.json', P)
print(h.sha(H / 'protocol.v2.json'), flush=True)
