import sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
assert h.read(ROOT / 'comparisons/D146-readback/report.json')['observer_usefulness_pass']
mapping = []
for name in ['launch', 'execute', 'assess', 'prepare']:
    old = ROOT / f'runs/D146-{name}.py'
    new = ROOT / f'runs/D147-{name}.py'
    assert not new.exists()
    text = old.read_text(encoding='utf-8').replace('D146', 'D147')
    if name == 'prepare':
        text = text.replace("S = ROOT / 'runs/D147-readback-source'", "S = ROOT / 'runs/D146-readback-source'")
        needle = "original = (h.REPO / 'crates/solver/tests/postflop_autoresearch.rs').read_text(encoding='utf-8')"
        insertion = "A = ROOT / 'runs/D147-arena-observer-source'\nam = h.read(A / 'manifest.json')\nh.pin(A / 'baseline.rs', h.custody()['crates/solver/src/gpu/arena.rs'])\nh.pin(A / 'diagnostic.rs', am['diagnostic_arena_sha256'])\nshutil.copyfile(A / 'diagnostic.rs', gpu / 'arena.rs')\n"
        assert text.count(needle) == 1
        text = text.replace(needle, insertion + needle, 1)
        text = text.replace("'kernels_arena_and_all_numerical_work_unchanged': True", "'kernels_and_numerical_work_unchanged': True, 'nested_arena_observer_sha256': am['diagnostic_arena_sha256']")
        text = text.replace('The same staged fourteen-span D065 host-wall helper on accepted E080 sync_to_cpu.', 'The staged fourteen-span D065 helper plus D147 optional CPU active/inactive timers. All original writes and joins remain.')
        text = text.replace("'instrumented_production_sha256': m['diagnostic_sha256']", "'instrumented_production_sha256': m['diagnostic_sha256'], 'instrumented_arena_sha256': am['diagnostic_arena_sha256']")
        needle = "files += [p for p in H.rglob('*') if p.is_file()]"
        assert text.count(needle) == 1
        text = text.replace(needle, "files += [ROOT/'runs/D147-subassess.py',ROOT/'runs/D147-workflow-adaptation.json',A/'baseline.rs',A/'diagnostic.rs',A/'manifest.json',A/'source-review.json']\n" + needle, 1)
        text = text.replace("'expected_traces': 9, 'expected_spans': 126", "'expected_traces': 9, 'expected_spans': 126, 'expected_CPU_arena_records': 36, 'inactive_component_admission': 'Optimistic maximum per-process sum of all compact inactive wall spans must reach1% of fresh ordinary aggregate, merely to admit E011 exact component controls; otherwise decline without implementation.'")
        text = text.replace('Analyze fourteen ordered host-wall spans per readback', 'Analyze fourteen ordered host-wall spans per readback and thirty-six nested CPU write records')
    if name in ['execute', 'assess']:
        one = "{'crates/solver/src/gpu/mod.rs': P['instrumented_production_sha256']}"
        two = "{'crates/solver/src/gpu/mod.rs': P['instrumented_production_sha256'], 'crates/solver/src/gpu/arena.rs': P['instrumented_arena_sha256']}"
        assert text.count(one) == (2 if name == 'execute' else 1)
        text = text.replace(one, two)
    if name == 'execute':
        needle = "h.child([sys.executable, str(ROOT / 'runs/D147-assess.py'), sys.argv[1]], O, 'assessment', 600)"
        assert text.count(needle) == 1
        text = text.replace(needle, needle + "\nh.child([sys.executable, str(ROOT / 'runs/D147-subassess.py'), sys.argv[1]], O, 'subassessment', 600)", 1)
        text = text.replace("'report_sha256': h.sha(ROOT / 'comparisons/D147-readback/report.json')", "'report_sha256': h.sha(ROOT / 'comparisons/D147-readback/report.json'), 'substage_report_sha256': h.sha(ROOT / 'comparisons/D147-arena-substages/report.json')")
    compile(text, str(new), 'exec')
    new.write_text(text, encoding='utf-8', newline='\n')
    mapping.append({'template': str(old), 'template_sha256': h.sha(old), 'adapted': str(new), 'adapted_sha256': h.sha(new)})
compile((ROOT / 'runs/D147-subassess.py').read_text(encoding='utf-8'), 'D147-subassess.py', 'exec')
h.save(ROOT / 'runs/D147-workflow-adaptation.json', {'at': h.now(), 'mapping': mapping, 'changes': 'Fresh IDs; add staged arena observer file and its exact source identity; append separate thirty-six-record CPU reader and prospective inactive-stage admission proxy. Original fixed evaluator, exact anchor, three matched observer pairs and coarse10% usefulness rule unchanged.', 'ordinary_source_activated': False, 'new_native_or_compiler_children_started': 0})
print('D147 workflow adapters parsed; prepare/freeze before native work.', flush=True)
