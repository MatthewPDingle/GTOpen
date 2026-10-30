import sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
assert h.read(ROOT / 'runs/E091-final-build/complete.json')['all_compilers_terminal']
assert h.read(ROOT / 'comparisons/E091-raw-control/report.json')['status'] == 'pass_scoped_down_action_raw_equivalence'
assert h.read(ROOT / 'comparisons/D144-incidence/report.json')['decision'] == 'eligible_for_frozen_whole_solve_screen'
mapping = []
for old_name, new_name in [('E090-primary-native.py', 'E091-primary-native.py'), ('E090-primary-assess.py', 'E091-primary-assess.py'), ('E090-primary-root-check.py', 'E091-primary-root-check.py'), ('E090-freeze-primary.py', 'E091-freeze-primary.py')]:
    old = ROOT / 'runs' / old_name
    new = ROOT / 'runs' / new_name
    assert not new.exists()
    original = old.read_text(encoding='utf-8')
    revised = original.replace('E090', 'E091').replace('V090', 'V091').replace('B293', 'B296').replace('B294', 'B297').replace('B295', 'B298')
    revised = revised.replace('comparisons/E091-engine-control/', 'comparisons/E091-raw-control/').replace('runs/E091-engine-control/', 'runs/E091-raw-control/')
    if new_name == 'E091-freeze-primary.py':
        needle = "P={'id':'E091-primary'"
        assert revised.count(needle) == 1
        extra = "files += [ROOT/'runs/E091-primary-adapter.json',ROOT/'comparisons/D144-incidence/report.json',ROOT/'runs/E091-resource/report.json',ROOT/'runs/E091-resource/protocol.json']\n"
        revised = revised.replace(needle, extra + needle, 1)
    compile(revised, str(new), 'exec')
    new.write_text(revised, encoding='utf-8', newline='\n')
    mapping.append({'template': str(old), 'template_sha256': h.sha(old), 'adapted': str(new), 'adapted_sha256': h.sha(new)})
h.save(ROOT / 'runs/E091-primary-adapter.json', {'at': h.now(), 'mapping': mapping, 'sequence': ['V091-unit', 'B296', 'E091R1', 'E091R2', 'B297', 'B298', 'E091R3'], 'changed': 'Candidate/run IDs, raw-control evidence paths and added prerequisite identities only. Same frozen primary score, exact anchor, strict fixture guard, source custody and no-rescue policy as current-RAM E090 screen.', 'candidate_source_or_evaluator_changed': False, 'native_primary_children_started': 0})
print('E091 primary adapters parsed; freeze before native tests/timing.', flush=True)
