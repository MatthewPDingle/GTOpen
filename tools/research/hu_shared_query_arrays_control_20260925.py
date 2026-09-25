"""CPU-only equivalence and timing control using two inspected query batches.

The reference executes the original bank's CPU preparation statements directly,
extracted from its source AST. No GPU, fresh deals, policies or live-source edits.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import ast
import dataclasses
import hashlib
import json
from pathlib import Path
import time

import numpy as np

from sampled_evidence_archive_v1 import read_artifact
from sampled_physical_bank_v1 import histories
from sampled_visible_features_bulk_v1 import features as visible_features
from shared_visible_query_arrays_v1 import prepare

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'shared-visible-query-arrays-control-v1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_new(path, doc):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(doc, stream, indent=2)


def main():
    start = time.monotonic()
    reference = ROOT/'tools/research/sampled_visible_hybrid_gpu_bank_bulk_v1.py'
    tree = ast.parse(reference.read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'VisibleHybridCudaBank64')
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'average')
    def assigned(node, name):
        return isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets)
    begin = next(i for i, n in enumerate(fn.body) if assigned(n, 'history'))
    end = next(i for i, n in enumerate(fn.body) if assigned(n, 'features'))
    body = fn.body[begin:end]
    assert ast.unparse(body[0]) == 'history = histories(observations)'
    assert len(body) == 9 and isinstance(body[-1], ast.For)
    compiled = compile(ast.Module(body=body, type_ignores=[]), str(reference), 'exec')

    source_result = OUT/'later-action-recovered-evaluation-control-v1-result.json'
    source_review = OUT/'later-action-recovered-evaluation-control-v1-independent-review.json'
    result, review = (json.loads(p.read_text()) for p in (source_result, source_review))
    assert result['passed'] and result['complete'] and review['passed']
    assert review['source_result_sha256'] == sha(source_result)
    folders = [Path(result['store'])/name for name in ('test-000000', 'test-000032')]
    inputs = [Path(__file__).resolve(), reference, source_result, source_review,
        ROOT/'tools/research/shared_visible_query_arrays_v1.py',
        ROOT/'tools/research/sampled_visible_features_bulk_v1.py',
        ROOT/'tools/research/sampled_physical_bank_v1.py',
        ROOT/'tools/research/sampled_evidence_archive_v1.py']
    queries = []
    for folder in folders:
        manifest_path = folder/'manifest.json'
        assert sha(manifest_path) == result['archive_manifest_hashes'][folder.name]
        manifest = json.loads(manifest_path.read_text())
        queries.append(json.loads(read_artifact(folder, manifest, 'queries.json', guard=lambda: None)))
        inputs.extend([manifest_path, folder/'queries.json.gz'])
    registration = OUT/f'{PREFIX}-registration.json'
    hashes = {str(p): sha(p) for p in inputs}
    save_new(registration, dict(inputs=hashes, sources=list(map(str, folders)),
        reference_ast_sha256=hashlib.sha256(ast.dump(ast.Module(body=body, type_ignores=[])).encode()).hexdigest(),
        benchmark_order=['repeated', 'shared', 'shared', 'repeated'], banks=4,
        maximum_seconds=120, gpu_used=False, fresh_deals=False,
        scope='Only common CPU input preparation; no policy, transfer or end-to-end speed claim'))

    def legacy(query):
        scope = dict(np=np, histories=histories, visible_features=visible_features,
                     observations=query['observations'])
        exec(compiled, scope)
        return tuple(scope[name] for name in ('x', 'actors', 'mask', 'prior', 'action', 'valid'))

    checks = []
    for source, query in zip(folders, queries):
        expected = legacy(query)
        prepared = prepare(query)
        actual = tuple(getattr(prepared, f.name) for f in dataclasses.fields(prepared))
        arrays = []
        for field, a, b in zip(dataclasses.fields(prepared), expected, actual):
            assert a.dtype == b.dtype and a.shape == b.shape and a.tobytes() == b.tobytes()
            assert not b.flags.writeable
            arrays.append(dict(name=field.name, shape=list(a.shape), dtype=str(a.dtype),
                sha256=hashlib.sha256(a.tobytes()).hexdigest()))
        checks.append(dict(source=source.name, observations=len(query['observations']), arrays=arrays))
        del expected, actual, prepared

    timings = []
    for mode in ('repeated', 'shared', 'shared', 'repeated'):
        assert time.monotonic()-start < 120
        before = time.monotonic()
        for query in queries:
            if mode == 'repeated':
                for _ in range(4):
                    arrays = legacy(query)
                    del arrays
            else:
                arrays = prepare(query)
                # Four consumers read the same immutable arrays; no GPU work.
                for _ in range(4):
                    assert arrays.features.shape[0] == len(query['observations'])
                del arrays
        timings.append(dict(mode=mode, seconds=time.monotonic()-before))
    for path, digest in hashes.items():
        assert sha(path) == digest
    repeated = sum(t['seconds'] for t in timings if t['mode'] == 'repeated')
    shared = sum(t['seconds'] for t in timings if t['mode'] == 'shared')
    final = dict(passed=True, registration_sha256=sha(registration), checks=checks,
        timings=timings, preparation_speedup=repeated/shared,
        seconds_saved_per_two_batch_pass=(repeated-shared)/2,
        seconds=time.monotonic()-start, gpu_used=False, live_sources_modified=False,
        production_modified=False, scope='Frozen common-query CPU arrays only; unintegrated candidate')
    save_new(OUT/f'{PREFIX}-result.json', final)
    print(json.dumps({k: v for k, v in final.items() if k != 'checks'}), flush=True)


if __name__ == '__main__':
    main()
