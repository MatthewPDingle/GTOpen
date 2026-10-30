"""Additive syntax repair, before any input model was read or written."""
import ast, shutil, sys, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists()
old = ROOT / 'runs/D267-node-order-model'
assert not (old / 'output').exists()
exit_info = h.read(old / 'execution/model.exit.json')
assert exit_info['returncode'] == 1
stderr = (old / 'execution/model.stderr.log').read_text(encoding='utf-8')
assert "SyntaxError: expected 'else'" in stderr
H = ROOT / 'runs/D267b-node-order-model'
H.mkdir(exist_ok=False)
names = ['model-io', 'node-order-model', 'node-order-audit', 'execute-node-order-model']
created = []
for name in names:
    source = ROOT / ('runs/D267-' + name + '.py')
    dest = ROOT / ('runs/D267b-' + name + '.py')
    text = source.read_text(encoding='utf-8')
    text = text.replace("if name=='d_children'else8", "if name=='d_children' else 8")
    text = text.replace('runs/D267-model-io.py', 'runs/D267b-model-io.py')
    text = text.replace('runs/D267-node-order-model', 'runs/D267b-node-order-model')
    text = text.replace('runs/D267-node-order-audit.py', 'runs/D267b-node-order-audit.py')
    ast.parse(text, filename=str(dest))
    with dest.open('x', encoding='utf-8', newline='\n') as f:
        f.write(text)
    created.append(dest)
P = h.read(old / 'protocol.json')
P.update(id='D267b', at=h.now(), status='FROZEN_PRE_CPU_MODEL_AND_READER_SYNTAX_REPAIR')
P['prior_attempt'] = {
    'protocol_sha256': h.sha(old / 'protocol.json'),
    'failure': 'Helper failed at Python import before reading scientific inputs or creating output; else8 token repaired additively.',
    'no_model_or_CUDA_runs_completed': True,
    'failure_receipts': {str(p): h.sha(p) for p in (old / 'execution').iterdir()},
    'unchanged_mapping_projection_cases_scope_and_acceptance': True,
}
P['input_sha256'] = {p: d for p, d in P['input_sha256'].items()
                      if not Path(p).name.startswith('D267-')}
P['input_sha256'].update({str(p): h.sha(p) for p in created + [Path(__file__), old / 'protocol.json']})
h.save(H / 'protocol.json', P)
dst = h.ar.DASHBOARD / 'evidence' / H.name / 'protocol.json'
dst.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(H / 'protocol.json', dst)
with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/evidence/' + H.name + '/protocol.json', timeout=20) as z:
    assert z.read() == (H / 'protocol.json').read_bytes()
print(h.sha(H / 'protocol.json'), flush=True)
