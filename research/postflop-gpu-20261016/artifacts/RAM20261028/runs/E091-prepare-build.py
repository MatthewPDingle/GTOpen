import sys, json, shutil, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
assert not (ROOT / 'gpu-run.lock').exists()
h.ar.refuse_active(h.ar.live_status())
raw = h.read(ROOT / 'comparisons/E091-raw-control/report.json')
incidence = h.read(ROOT / 'comparisons/D144-incidence/report.json')
assert raw['status'] == 'pass_scoped_down_action_raw_equivalence' and raw['cases'] == 1530
assert incidence['status'] == 'pass_finite_zero_reach_incidence' and incidence['decision'] == 'eligible_for_frozen_whole_solve_screen'
assert h.read(ROOT / 'runs/D144-incidence/execution-r2/complete.json')['all_owned_children_terminal']
H = ROOT / 'runs/E091-build-plan'
H.mkdir(exist_ok=False)
template = ROOT / 'runs/E090-build.py'
script = ROOT / 'runs/E091-build.py'
assert not script.exists()
source = template.read_text(encoding='utf-8')
code = source.replace('E090', 'E091')
compile(code, str(script), 'exec')
script.write_text(code, encoding='utf-8', newline='\n')
base = h.custody()
manifest = h.read(ROOT / 'runs/E091-source/manifest.json')
owned = {}
for name, paths in manifest['owned'].items():
    owned[name] = {'base': paths['base'], 'base_sha256': base[name], 'candidate': paths['candidate'], 'candidate_sha256': manifest['candidate_owned_sha256'][name]}
    h.pin(paths['base'], base[name])
    h.pin(paths['candidate'], manifest['candidate_owned_sha256'][name])
P = h.read(ROOT / 'runs/E090-build-plan/protocol.json')
P.update(id='E091-final-build', at=h.now(), accepted_source_sha256=base, candidate_owned_sha256=manifest['candidate_owned_sha256'], owned=owned, measurement_epoch='RAM20261028')
for phase in P['phases']:
    phase['target'] = str(ROOT / ('build-e091-final-' + phase['id']))
    phase['outputs'] = {k: v.replace('E090', 'E091') for k, v in phase['outputs'].items()}
    assert not Path(phase['target']).exists()
files = [Path(__file__), template, script, ROOT / 'runs/E090-build-plan/protocol.json', ROOT / 'comparisons/E091-raw-control/report.json', ROOT / 'runs/E091-raw-control/protocol.json', ROOT / 'runs/E091-raw-control/execution/complete.json', ROOT / 'runs/E091-resource/report.json', ROOT / 'runs/E091-resource/protocol.json', ROOT / 'comparisons/D144-incidence/report.json', ROOT / 'runs/D144-incidence/protocol-r2.json', ROOT / 'runs/D144-incidence/execution-r2/complete.json', ROOT / 'epoch/common.py', ROOT / 'epoch/accepted-source.json', ROOT / 'epoch/protected-main.json', ROOT / 'epoch/preexisting-target-artifacts.json', h.REPO / 'research/postflop-gpu-20261016/qualification-policy-20261017.md']
files += [p for p in (ROOT / 'runs/E091-source').iterdir() if p.is_file()]
P['input_sha256'] = {str(p): h.sha(p) for p in files}
P['scope'] = 'One signed-zero-reach shortcut in down_action only. Raw1530 pairs/full actual inputs/outputs/guards and compiled resource prerequisites pass. D144 finds actual zero-reach parent hands in declared subsets; finite guard eligibility and saving remain unmeasured. Two fresh feature/primary Cargo builds on X, restore accepted source after each. No native tests or timing in this protocol.'
h.save(H / 'protocol.json', P)
pub = []
for folder, prefix in [(ROOT / 'runs/E091-raw-control', 'E091-raw-control'), (ROOT / 'comparisons/E091-raw-control', 'E091-raw-control-result'), (ROOT / 'runs/D144-incidence', 'D144-incidence'), (ROOT / 'comparisons/D144-incidence', 'D144-incidence-result'), (H, H.name)]:
    for p in folder.rglob('*'):
        if not p.is_file() or p.suffix not in ['.json', '.rs', '.py', '.log', '.cu', '.patch']:
            continue
        key = prefix + '/' + p.relative_to(folder).as_posix()
        dst = h.ar.DASHBOARD / 'evidence' / key
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            assert dst.read_bytes() == p.read_bytes(), key
        else:
            shutil.copyfile(p, dst)
        with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/evidence/' + key, timeout=20) as response:
            assert response.read() == p.read_bytes()
        pub.append(key)
h.save(H / 'publication.json', {'at': h.now(), 'HTTP_verified_artifacts': pub, 'protocol_sha256': h.sha(H / 'protocol.json'), 'all_new_artifacts_X': True})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'), timeout=3):
    s = h.read(h.ar.STATUS)
    x = next(x for x in s['experiments'] if x['id'] == 'D144')
    x.update(status='measured', stage='Finite incidence check passed', correctness='pass', reason='All three original solve records and23 checkpoints remain exact. Six full input snapshots pass ownership/bounds checks and contain zero-reach hands in the declared flop subsets. Necessary-condition incidence only; finite-sum guard eligibility and speed are unmeasured.')
    x.setdefault('evidence', []).append({'label': 'Actual input incidence', 'url': 'evidence/D144-incidence-result/report.json'})
    x = next(x for x in s['experiments'] if x['id'] == 'E091')
    x.update(stage='Fresh integrated builds', correctness='raw_controls_pass', reason='Compiled resources and1530 full raw pairs pass. Actual sampled zero reach motivates a fixed complete-solve screen, without predicting savings. Build fresh feature/primary binaries first.')
    x.setdefault('evidence', []).append({'label': 'Frozen fresh builds', 'url': 'evidence/E091-build-plan/protocol.json'})
    s.update(updated_at=h.now(), active_experiment='E091', stage='E091 fresh builds', activity='Raw device controls and actual input incidence passed. Build isolated E091 binaries before testing whole-solve performance. E080 remains live with the new10.4564s baseline.')
    h.ar.atomic_json(h.ar.STATUS, s)
h.custody()
print(h.sha(H / 'protocol.json'), flush=True)
