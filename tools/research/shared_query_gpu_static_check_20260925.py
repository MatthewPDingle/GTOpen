"""Structural checks only; these do not qualify GPU behavior or performance."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path('T:/Dev/GTOpen')
TOOLS = ROOT/'tools/research'
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def method(tree, cls, name):
    return next(n for c in tree.body if isinstance(c, ast.ClassDef) and c.name == cls
                for n in c.body if isinstance(n, ast.FunctionDef) and n.name == name)


def inference_tail(fn):
    begin = next(i for i, n in enumerate(fn.body) if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == 'numerator' for t in n.targets))
    return ast.dump(ast.Module(body=fn.body[begin:], type_ignores=[]))


def main():
    names = ('sampled_visible_hybrid_gpu_bank_bulk_v1.py',
        'sampled_visible_hybrid_gpu_bank_shared_v1.py',
        'action_integrated_policy_bulk_v1.py', 'action_integrated_policy_shared_v1.py',
        'crossed_complete_policy_batch_v1.py', 'crossed_complete_policy_batch_shared_v1.py',
        'shared_visible_query_arrays_v1.py')
    trees = {}
    for name in names:
        source = (TOOLS/name).read_text()
        compile(source, str(TOOLS/name), 'exec')
        trees[name] = ast.parse(source)
    original = method(trees[names[0]], 'VisibleHybridCudaBank64', 'average')
    candidate = method(trees[names[1]], 'VisibleHybridCudaBank64', 'average_prepared')
    assert inference_tail(original) == inference_tail(candidate)
    original_init = method(trees[names[2]], 'ActionIntegratedCudaBankBulk64', '__init__')
    candidate_init = method(trees[names[3]], 'ActionIntegratedCudaBankShared64', '__init__')
    assert ast.dump(original_init) == ast.dump(candidate_init)
    cls = next(n for n in trees[names[1]].body if isinstance(n, ast.ClassDef) and n.name == 'VisibleHybridCudaBank64')
    assert len(cls.bases) == 1 and isinstance(cls.bases[0], ast.Name) and cls.bases[0].id == 'OriginalBank'
    assert not any(isinstance(n, ast.FunctionDef) and n.name == '__init__' for n in cls.body)
    live_registration = OUT/'later-action-compact-evaluation-study-v1-registration.json'
    registered = json.loads(live_registration.read_text())
    original_sources = {p: h for p, h in registered['inputs'].items()
                        if Path(p).suffix == '.py' and '/tools/research/' in Path(p).as_posix()}
    assert original_sources
    for path, expected in original_sources.items():
        assert digest(Path(path)) == expected, path
    record = dict(passed=True, syntax_checked=len(names), constructor_ast_identical=True,
        inference_and_ordered_average_ast_identical=True,
        original_live_sources_unchanged=len(original_sources),
        live_registration_sha256=digest(live_registration),
        inputs={str(TOOLS/name): digest(TOOLS/name) for name in (*names, Path(__file__).name)},
        gpu_executed=False, gpu_qualified=False, performance_qualified=False,
        scope='Source structure and live-source integrity only. Complete GPU equivalence, independent readback and end-to-end timing remain required.')
    path = OUT/'shared-query-gpu-candidate-static-check-v1.json'
    with path.open('x', encoding='utf-8') as stream:
        json.dump(record, stream, indent=2)
    print(json.dumps({k: v for k, v in record.items() if k != 'inputs'}))


if __name__ == '__main__':
    main()
