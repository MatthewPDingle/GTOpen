"""Freeze original-metadata full showdown controls for E122."""
import ast, json, shutil, sys, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists()
assert shutil.disk_usage(ROOT).free > 96 * 1024**3
A = ROOT / 'runs/E120-kernel-control'
H = ROOT / 'runs/E122-kernel-control'
S = ROOT / 'runs/E122-source'
RES = ROOT / 'runs/E122-resource'
N = ROOT / 'runs/D301-predicated-correction-native'
ptx_report = ROOT / 'runs/D300-predicated-correction-PTX/report.json'
q = h.read(RES / 'report.json')
assert all(q['gates'].values())
assert h.read(N / 'report.json')['status'] == 'pass_scoped_native_selector_removal_and_all30_original_priority_pairs'
assert h.read(ptx_report)['status'] == 'pass_scoped_predicated_correction_PTX_original_words_priority_and_barriers'
H.mkdir(exist_ok=False)
for name in ['baseline.cu', 'candidate.cu']:
    shutil.copyfile(S / name, H / name)
for arm in ['baseline', 'candidate']:
    p = RES / ('baseline-compute_120.ptx' if arm == 'baseline' else 'execution/candidate-compute_120.ptx')
    h.pin(p, q['PTX_sha256'][arm + '-compute_120'])
    shutil.copyfile(p, H / (arm + '.ptx'))
shutil.copyfile(A / 'accepted-evaluator.rs', H / 'accepted-evaluator.rs')
corpus_path = ROOT / 'runs/E121-show-control/corpus.json'
c = h.read(corpus_path)
old = h.read(A / 'corpus.json')
assert len(c['cases']) == 2660 and len(c['geometries']) == 244
assert c['cases'][:2636] == old['cases'] and c['geometries'] == old['geometries']
shutil.copyfile(corpus_path, H / 'corpus.json')
gs = {g['id']: g for g in c['geometries']}
pairs = len(c['cases']) * 5
launches = pairs * 2
active = 5 * sum(2 * gs[x['geometry']]['nh_p'] if x['count'] else 0 for x in c['cases'])
guards = 5 * sum(2 * (len(gs[x['geometry']]['output_initial']) - (2 * gs[x['geometry']]['nh_p'] if x['count'] else 0)) for x in c['cases'])
probe = (A / 'probe.rs').read_text().replace('E120', 'E122')
for before, after in [('cs.len(),2636', 'cs.len(),2660'), ('"comparison_pairs":13180', f'"comparison_pairs":{pairs}'), ('launches,26360', f'launches,{launches}'), ('active_words,7645180', f'active_words,{active}'), ('guard_checks,63032880', f'guard_checks,{guards}'), ('input_checks,553560', f'input_checks,{pairs * 42}')]:
    assert before in probe, before
    probe = probe.replace(before, after)
(H / 'probe.rs').write_bytes(probe.encode())
for name in ['execute.py', 'audit.py']:
    code = (A / name).read_text().replace('E120', 'E122').replace('13183', str(pairs + 3)).replace('13180', str(pairs)).replace('26360', str(launches)).replace('pass_scoped_full_sparse_card_raw_equivalence', 'pass_scoped_full_predicated_correction_raw_equivalence')
    ast.parse(code)
    (H / name).write_bytes(code.encode())
wrapper = ROOT / 'runs/E122-run-direct.py'
code = (ROOT / 'runs/E120-run-direct.py').read_text().replace('E120', 'E122').replace('13180', str(pairs)).replace('26360', str(launches))
ast.parse(code)
with wrapper.open('xb') as f:
    f.write(code.encode())
parent = h.read(A / 'protocol.json')
command = [x.replace(str(A), str(H)) for x in parent['rustc_command']]
files = [Path(__file__), wrapper, RES / 'report.json', N / 'report.json', ptx_report, ROOT / 'epoch/common.py', corpus_path]
files += [p for p in H.iterdir() if p.is_file()]
files += [p for p in (ROOT / 'reference/accepted-e080-deps').iterdir() if p.is_file()]
files += [A / n for n in ['probe.rs', 'execute.py', 'audit.py', 'corpus.json', 'protocol.json']]
h.save(H / 'protocol.json', {
    'id': 'E122-kernel-control', 'at': h.now(), 'status': 'FROZEN_PRE_FIRST_APPLICATION_KERNEL',
    'rustc_command': command, 'input_sha256': {str(p): h.sha(p) for p in files},
    'resource_report': str(RES / 'report.json'), 'native_mechanism_report': str(N / 'report.json'),
    'widths': [1, 32, 64, 128, 256], 'base_cases': 2660, 'geometries': 244,
    'original_cases_retained_exact': 2636, 'expected_pairs': pairs, 'expected_application_launches': launches,
    'expected_active_words': active, 'expected_guard_word_checks': guards,
    'sealed_PTX_sha256': {a: h.sha(H / (a + '.ptx')) for a in ['baseline', 'candidate']},
    'scope': 'E120 original2636cases retained exact prefix plus24single-opponent reachcases from E121 corpus data only. Original unencoded E120 probe and metadata for BOTH arms; no E121 encoder/source composition. All21actual device inputs literal equal and expected, whole physical CFV/guards/NaN bits, rankoracle/2roundingwitnesses, five widths. Sealed E122 PTX; no NVRTC/solver/timing. Any genuine failure closes fixed E122 without source/asm/predicate/constraint/architecture/width/helper/flags/quality/sample rescue. Fullraw canonical/engine/broad/material/fresh16/holdout/currentRAM cumulative/app before adoption.',
    'admission_free_bytes': shutil.disk_usage(ROOT).free, 'raw_output_cap_bytes': 8 * 1024**3,
    'peak_reservation_bytes': 32 * 1024**3, 'minimum_free_bytes': 64 * 1024**3,
    'candidate_adopted': False, 'performance_measurement': False})
for p in [ptx_report, N / 'report.json', H / 'protocol.json']:
    key = p.parent.name + '/' + p.name
    dst = h.ar.DASHBOARD / 'evidence' / key
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        assert dst.read_bytes() == p.read_bytes()
    else:
        shutil.copyfile(p, dst)
    with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/evidence/' + key, timeout=20) as z:
        assert z.read() == p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'), timeout=3):
    status = h.read(h.ar.STATUS)
    e = next(x for x in status['experiments'] if x['id'] == 'E122')
    e.update(stage='Frozen full raw showdown controls', correctness='Resource/PTX/native mechanism passed; numerical controls pending', reason='13,300 pairs / 26,600 launches, original metadata and full original corpus plus24 single-opponent cases. Showdown registers38to40 warning; no performance claim. All broad and adoption gates remain.')
    e['evidence'] += [{'label': p.parent.name, 'url': 'evidence/' + p.parent.name + '/' + p.name} for p in [ptx_report, N / 'report.json', H / 'protocol.json']]
    status.update(updated_at=h.now(), stage=e['stage'], activity=e['reason'])
    h.ar.atomic_json(h.ar.STATUS, status)
h.custody()
print(json.dumps({'protocol_sha256': h.sha(H / 'protocol.json'), 'pairs': pairs, 'launches': launches, 'active_words': active, 'guard_words': guards}), flush=True)
