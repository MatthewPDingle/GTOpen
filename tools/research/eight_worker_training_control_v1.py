"""Eight-process dispatch parity on previously qualified physical fixtures."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
import ast
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time
import traceback
import numpy as np
import psutil
import weighted_training_workers_v1 as baseline
import river_training_workers_v1 as river
from eight_worker_training_pools_v1 import baseline_pool, river_pool
from weighted_deal_binding_v1 import DealWeightGeneration
from board_training_checkpoint_v1 import model_document
from board_training_policy_v1 import probabilities
from preflop_allin_matrix_v1 import AllinMatrix
from exact_initial_training_ingest_v2 import InitialTargets
from sampled_allin_protocol_v3 import AllinCache
from bounded_parallel_evaluation_archive_v2 import production_available
from board_prefix_publication_v1 import atomic_json

ROOT = Path('T:/Dev/GTOpen'); OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME = 'eight-worker-training-control-v1'; STORE = OUT/NAME
REG = OUT/(NAME+'-registration.json'); RESULT = OUT/(NAME+'-result.json')
CONTEXT = OUT/'bb-context-candidate.json'; LIMIT = 80_000_000


def read(p): return json.loads(Path(p).read_bytes())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not any(p.exists() for p in (STORE, REG, RESULT))
    assert production_available() and psutil.cpu_percent(interval=1) < 40
    assert psutil.virtual_memory().available > 40_000_000_000
    # This short qualification may share CPU with the pilot's qualification,
    # whose cost is excluded. Never silently overlap measured training/evaluation.
    statuspath = OUT/'river-matched-training-pilot-v1-status.json'
    current = read(statuspath); process = psutil.Process(current['pid'])
    assert process.create_time() == current['process_created']
    assert current['state'] == 'qualifying_full_update_and_restart'
    began = time.monotonic(); last = 0.
    def guard():
        nonlocal last
        now = time.monotonic(); assert now-began < 90
        if now-last > 2:
            assert production_available() and psutil.virtual_memory().available > 24_000_000_000
            assert read(statuspath)['state'] == 'qualifying_full_update_and_restart'
            assert sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file()) < LIMIT
            last = now
    pr = OUT/'river-weighted-overlay-control-v2-registration.json'
    pe = OUT/'river-training-workers-control-v1-result.json'
    oldreg, old = read(pr), read(pe)
    assert old['passed'] and old['registration_sha256'] == sha(OUT/'river-training-workers-control-v1-registration.json')
    source = CONTEXT.read_text()
    prior = OUT/'river-training-workers-control-v1'
    generation_path = OUT/'river-weighted-overlay-control-v2/source-generation.json'
    generation = DealWeightGeneration(read(generation_path), source)
    cp = Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    mp = OUT/'preflop-allin-matrix-control-v1-matrix.json'
    matrix = AllinMatrix(read(mp), source); catalog = read(cp)
    reviewpath = OUT/'complete-private-allin-cache-v2-independent-review.json'
    review = read(reviewpath); assert review['passed']
    cache = AllinCache(review['cache_artifact'], review['cache_sha256'])
    exe = ROOT/'target/release/examples'
    binaries = dict(executable=exe/'hu_sampled_allin_bridge_v3.exe', trace_executable=exe/'hu_sampled_action_trace_v2.exe',
        integration_executable=exe/'hu_sampled_profile_allin_evaluation_v1.exe', river_executable=exe/'hu_river_two_stage_stream_v1.exe')
    paths = [Path(__file__), pr, pe, generation_path, cp, mp, reviewpath, *binaries.values()]
    for module in list(sys.modules.values()):
        p = getattr(module, '__file__', None)
        if p and Path(p).is_relative_to(ROOT) and Path(p).suffix == '.py': paths.append(Path(p))
    for a, b in (('board_training_pipeline_v1.py', 'board_training_pipeline_eight_v1.py'),
                 ('river_training_pipeline_v1.py', 'river_training_pipeline_eight_v1.py')):
        paths.extend([ROOT/'tools/research'/a, ROOT/'tools/research'/b])
        trees = [ast.parse(p.read_bytes()) for p in paths[-2:]]
        for tree in trees: tree.body = [n for n in tree.body if not isinstance(n, (ast.Import, ast.ImportFrom))]
        assert ast.dump(trees[0]) == ast.dump(trees[1])
    inputs = dict(read(OUT/'river-training-workers-control-v1-registration.json')['inputs'])
    inputs.update({str(p): sha(p) for p in paths})
    for p, h in inputs.items(): assert sha(p) == h, p
    STORE.mkdir()
    atomic_json(REG, dict(inputs=inputs, workers=8, maximum_bytes=LIMIT, maximum_seconds=90,
        models=2, fixture_cases=8, repeats_per_case_per_method=2, baseline_and_river=True,
        new_poker_deals=0, gpu_used=False, production_modified=False,
        concurrent_pilot_pid=process.pid, scope='Dispatch/byte parity only; concurrent qualification timings are not performance evidence.'))
    reports = []
    try:
        for bank in oldreg['policies']:
            guard()
            args = dict(catalog_source=cp.read_text(), matrix_sha256=sha(mp), entry_mass=matrix.btn_mass, root_config=bank['root_config'])
            model = model_document(bank['folder'], bank['reference'], context_source=source, **args)
            modelraw = (Path(bank['folder'])/bank['reference']['file']).read_text()
            initial, _ = probabilities(dict(context_source=source, observations=[r['observation'] for r in catalog['native_observations']]), model, device='cpu', **args)
            root = np.zeros((169, 4)); calls = np.zeros(169)
            for item, row in zip(catalog['native_observations'], initial):
                if item['player'] == 0: root[item['hand_class']] = row
                else: calls[item['hand_class']] = row[1]
            targets = InitialTargets(mp.read_text(), source, root, calls, matrix_sha256=sha(mp), generation=77)
            common = dict(context_path=CONTEXT, cache=cache, targets=targets, generation=generation, iteration=78,
                          **{k: v for k, v in binaries.items() if k != 'river_executable'})
            cases = [c for c in old['cases'] if c['case'].endswith(bank['arm'])]
            assert len(cases) == 4
            for label, factory, worker in (('baseline', baseline_pool, baseline), ('river', river_pool, river)):
                options = dict(common)
                if label == 'river': options.update(river_executable=binaries['river_executable'],
                    river_payload=dict(model_source=modelraw, policy_id=hashlib.sha256(modelraw.encode()).hexdigest(), model_args=args))
                tasks = []
                for repeat in range(2):
                    for case in cases:
                        folder = STORE/(label+'-'+case['case']+'-'+str(repeat)); folder.mkdir()
                        for name in ('batch.json', 'queries.json', 'policies.json'):
                            shutil.copyfile(prior/case['case']/'parallel'/name, folder/name)
                        expected = {k.replace('\\', '/')[9:]: h for k, h in case['artifacts'].items()
                                    if k.replace('\\', '/').startswith('parallel/')}
                        if label == 'baseline': expected = {k: h for k, h in expected.items() if '/' not in k and k != 'river-targets.json'}
                        # Source offset is the prior one-deal fixture's dNNN.
                        tasks.append((case, folder, expected, int(case['case'][1:4])))
                assert len(tasks) == 8
                with factory(8, **options) as pool:
                    futures = [pool.submit(worker.complete, str(folder), offset) for _, folder, _, offset in tasks]
                    values = [future.result(timeout=30) for future in futures]
                pids = sorted({v['pid'] for v in values})
                assert len(pids) >= 2
                for (case, folder, expected, offset), value in zip(tasks, values):
                    guard()
                    actual = {k.replace('\\', '/'): h for k, h in value['artifacts'].items()}
                    assert actual == expected and actual
                    assert value['start'] == offset and value['counts'] == case['counts']
                    assert len(value['events']) == sum(case['counts'])
                    for filename, digest in actual.items(): assert sha(folder/filename) == digest
                    reports.append(dict(method=label, case=case['case'], folder=folder.name,
                        identical_artifacts=len(actual), events=len(value['events']), pid=value['pid'],
                        worker_rss_bytes=value['rss_bytes'], artifacts=actual))
                print(json.dumps(dict(method=label, model=bank['arm'], passed=True, observed_worker_pids=pids)), flush=True)
        for p, h in inputs.items(): guard(); assert sha(p) == h, p
        assert len(reports) == 32 and sum(r['events'] for r in reports) == 524
        guard()
        atomic_json(RESULT, dict(passed=True, complete=True, registration_sha256=sha(REG), cases=reports,
            seconds=time.monotonic()-began, workers_requested=8, distinct_worker_pids=len({r['pid'] for r in reports}),
            core_pipeline_ast_unchanged=True, new_poker_deals=0, gpu_used=False, production_modified=False,
            performance_claim=False, scope='Byte-identical original target and integration artifacts; unchanged original ordered commit functions. Full eight-worker training timing remains unmeasured.'))
        print(json.dumps(dict(passed=True, tasks=len(reports), result=str(RESULT))), flush=True)
    except BaseException as error:
        atomic_json(OUT/(NAME+'-failure.json'), dict(error=repr(error), traceback=traceback.format_exc(), preserve_evidence=True))
        raise


if __name__ == '__main__': main()
