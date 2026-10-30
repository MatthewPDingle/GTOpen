import shutil, sys, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
S = ROOT / 'runs/E115-source-v2'
M = h.read(S / 'manifest.json')
for n, v in M['owned'].items():
    h.pin(v['candidate'], v['candidate_sha256'])
h.pin(h.REPO / 'crates/solver/src/gpu/kernels.cu', M['accepted_source_sha256']['crates/solver/src/gpu/kernels.cu'])
paths = [ROOT / 'runs/D266-metadata-order-history/report.json',
         ROOT / 'runs/D267-node-order-model/protocol.json',
         ROOT / 'runs/D267-node-order-model/execution/model.exit.json',
         ROOT / 'runs/D267-node-order-model/execution/model.stderr.log',
         ROOT / 'runs/D267b-node-order-model/protocol.json',
         ROOT / 'runs/D267b-node-order-model/model-report.json',
         ROOT / 'runs/D267b-node-order-model/root-report.json',
         ROOT / 'runs/D267b-node-order-model/execution/complete.json',
         ROOT / 'runs/D268-record-layout/protocol.json',
         ROOT / 'runs/D268-record-layout/report.json',
         ROOT / 'runs/E115-source/generation-failure.json', S / 'manifest.json',
         ROOT / 'runs/D269-host-layout/protocol.json',
         ROOT / 'runs/D269-host-layout/protocol.v2.json']
for p in paths:
    # Separate execution receipts keep their parent context in the published name.
    key = p.parent.name + '/' + p.name
    if p.parent.name == 'execution': key = p.parent.parent.name + '/' + p.name
    dst = h.ar.DASHBOARD / 'evidence' / key
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists(): assert dst.read_bytes() == p.read_bytes()
    else: shutil.copyfile(p, dst)
    with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/evidence/' + key, timeout=20) as z:
        assert z.read() == p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'), timeout=3):
    s = h.read(h.ar.STATUS)
    assert not any(e['id'] == 'E115' for e in s['experiments'])
    s['experiments'].append({
        'id': 'E115', 'at': h.now(), 'title': 'GPU metadata rows in existing execution order',
        'kind': 'candidate', 'status': 'running', 'accepted': False,
        'stage': 'Full crate typecheck and actual host layout', 'correctness': 'CPU feasibility only; GPU proof pending',
        'reason': 'D267 six-plan CPU model reverses all24 arrays/114255649 words exactly,18 reader negative fixtures pass. D268 proposed action ID fields fit existing32/40-byte record padding. Isolated5-file prototype preserves original CUDA/FP/physical arenas/worklist order; extra setup, locks, full host layout, actual all-call-path correctness/material and every complete-solve gate remain. No performance result or gain adopted.',
        'evidence': [{'label': 'Reversible six-plan model', 'url': 'evidence/D267b-node-order-model/root-report.json'},
                     {'label': 'Actual private record padding', 'url': 'evidence/D268-record-layout/report.json'},
                     {'label': 'Fixed isolated source form and limits', 'url': 'evidence/E115-source-v2/manifest.json'},
                     {'label': 'Frozen full-host typecheck', 'url': 'evidence/D269-host-layout/protocol.v2.json'}],
    })
    s.update(updated_at=h.now(), state='running', goal_status='active', active_experiment='E115',
             stage='Metadata layout: full crate typecheck',
             activity='New RAM baseline10456.4109ms; E080/GPU/compressed/16/default affinity remains best qualified/live. E115 CPU projection and record padding pass; actual full-host compilation/layout is next. No new GPU or speed samples. All new bulk X; S archive read-only; no T access.')
    h.ar.atomic_json(h.ar.STATUS, s)
print('E115 stage and14 immutable evidence artifacts HTTP byte-verified.', flush=True)
