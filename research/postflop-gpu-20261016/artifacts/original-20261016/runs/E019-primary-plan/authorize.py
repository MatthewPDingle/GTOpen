import json, shutil, subprocess, sys
from pathlib import Path

repo = Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0, str(repo / 'tools'))
import postflop_autoresearch as ar

base = ar.RESEARCH
here = Path(__file__).resolve().parent
owned = 'crates/solver/src/gpu/kernels.cu'
candidate = base / 'runs/D036-fold-shuffle-probe-r3/candidate.cu'
candidate_sha = '9eff0e598c69bafcf4dc8a04ad116bd25482b06bd9bde34c143d45688ab5505a'
pins = {
 'comparisons/D036-independent-review/validation.json': 'c914634aae876c82f37f7d3c87ce387790e4b8fcf6d657c4d5bae96f0d173a42',
 'comparisons/D036-independent-review/summary.md': 'cd04148c9236a11b12cc1a07a3185fd34470d94e302ff094b78d4020c80e9fcb',
 'comparisons/D036-independent-review/manifest.json': '91cd2a56c871cbecc5895746b5b925763262a6d3173a820a81981feb5ac816be',
 'comparisons/D036-probe-source-review-r3/review.md': '60b67df1f4796328f702140f6a69d6d1463a27cf5895f92664a88e53f3439d01',
 'comparisons/D036-probe-source-review-r3/manifest.json': '6ef6edb0b91abe2dc48c320e47fd5c4181c93534aa23475156b0b626444b89f9',
 'comparisons/E019-harness-review/review.md': '6fdda1672e1a4ca652a6aeefc5cb602bf25333e22217794d5f7f12c7a3e7f623',
 'comparisons/E019-harness-review/manifest.json': 'fd6c6a6bc5a859067fa6ecc9be3cc43176965c288478751261c1c294540607ed',
 'runs/E019-primary-plan/protocol.json': 'c74dfd6cbd57804c1fd8e9bad65744a8ab2b525f3e6aa230b5ed46c6959b1fba',
 'runs/E019-primary-plan/scripts-manifest.json': 'fe2d98e59c127b4ab56945a170a06aa702d22689190e5e732d83c8d9558851a8',
 'runs/E019-primary-plan/build.py': '9a70f07528879b6316c3cddf5ae3751696360946d64e96046ca1712110e85e25',
 'runs/E019-primary-plan/primary.py': '993fcac3be703a7f003e4d9a424b880bb9a6da04e72e876dd33b4f6d1a422564',
 'runs/D036-fold-shuffle-probe-r3/prepared-manifest.json': 'b0fd45d3bceffb9fb5ba6de294dc3af3ede144a1707cd3ceacbd616e0e4d8279',
}
for name, expected in pins.items():
    assert ar.sha256(base / name) == expected, name
assert ar.sha256(candidate) == candidate_sha
assert not (base / 'gpu-run.lock').exists()
ar.refuse_active(ar.live_status())
accepted = json.loads((base / 'binaries/E015-postflop_autoresearch.manifest.json').read_text(encoding='utf-8'))
before = ar.source_identity()
assert before['source_sha256'] == accepted['source_sha256'], 'Expected exact accepted source before change'
assert not (here / 'authorization.json').exists()
out = base / 'runs/E019-source'
out.mkdir(exist_ok=False)
ar.atomic_json(out / 'source-before.json', before)
shutil.copyfile(repo / owned, out / 'accepted.cu')
shutil.copyfile(candidate, out / 'candidate.cu')
for name in ['runs/D036-fold-shuffle-probe-r3/report.json',
             'runs/D036-fold-shuffle-probe-r3/execution-manifest.json',
             'comparisons/D036-probe-source-review-r3/ptx-review.md',
             'comparisons/D036-probe-source-review-r3/ptx-manifest.json']:
    pins[name] = ar.sha256(base / name)
shutil.copyfile(candidate, repo / owned)
after = ar.source_identity()
assert set(after['source_sha256']) == set(before['source_sha256'])
assert [k for k, v in before['source_sha256'].items() if after['source_sha256'][k] != v] == [owned]
assert after['source_sha256'][owned] == candidate_sha
ar.atomic_json(out / 'source-after.json', after)
(out / 'candidate.patch').write_bytes(subprocess.check_output(['git','diff','--binary','HEAD','--',owned], cwd=repo))
ar.atomic_json(here / 'authorization.json', {
    'at': ar.now(), 'candidate': 'E019', 'probe_exactness_pass': True,
    'independent_review_pass': True, 'candidate_source': str(candidate),
    'candidate_sha256': candidate_sha, 'evidence_sha256': {str(base/k):v for k,v in pins.items()},
    'scope': 'Root authorizes only frozen build and fixed primary benchmark after reviewing source, runtime exactness and independent audits. No performance acceptance or deployment.'})

published = []
for name in ['comparisons/D036-independent-review/summary.md','comparisons/D036-independent-review/validation.json',
             'comparisons/D036-independent-review/manifest.json','comparisons/D036-probe-source-review-r3/review.md',
             'comparisons/D036-probe-source-review-r3/ptx-review.md','runs/E019-primary-plan/protocol.json']:
    source = base / name
    target = ar.DASHBOARD / 'evidence' / source.parent.name / source.name
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists(): assert ar.sha256(target) == ar.sha256(source)
    else: shutil.copyfile(source, target)
    published.append('evidence/' + source.parent.name + '/' + source.name)
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'), timeout=3):
    status = json.loads(ar.STATUS.read_text(encoding='utf-8'))
    row = next(r for r in status['experiments'] if r['id'] == 'D036')
    row.update(correctness='pass', updated_at=ar.now(), reason='Independent audit passed: all 180 full-kernel and 1,120 raw-total pairs match exactly, including mandatory overflow outputs. Guards and finite-domain CPU raw-total oracle pass. Kernel resources unchanged; emitted 128-thread path removes four block barriers. Diagnostic only; no full-solve speed or acceptance claim. R2 compiler failure preserved.')
    for label, url in [('Independent raw-result audit', published[0]),('Independent numerical validation', published[1]),('Emitted PTX mechanism review', published[4])]:
        if not any(e['url'] == url for e in row['evidence']): row['evidence'].append({'label':label,'url':url})
    assert not any(r['id'] == 'E019' for r in status['experiments'])
    status['experiments'].append({'id':'E019','at':ar.now(),'title':'Exact fold reduction with fewer block barriers','kind':'candidate','status':'planned','correctness':'pending','fixture':'All three fixtures','stage':'Preparing source-frozen build','reason':'Standalone numerical probe and independent audit passed. One CUDA kernel change; fixed three-pair complete-cycle benchmark and subsequent qualification pending.','evidence':[{'label':'Audited standalone exactness','url':published[0]},{'label':'Fixed primary protocol','url':published[-1]}]})
    status.update(updated_at=ar.now(),stage='Preparing E019 native candidate',active_experiment='E019',activity='D036 independent audit passed. Testing a single fold-kernel change with four fewer block barriers; accepted complete-solve gain remains E015 at9.62%.')
    ar.atomic_json(ar.STATUS,status)
print('Authorization SHA256:', ar.sha256(here / 'authorization.json'))
print('Only production change:', owned)
