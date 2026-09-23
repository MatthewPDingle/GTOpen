"""Exhaustive BTN-vs-shove endpoint for two fixed, fully audited candidates.

Only run after both original evaluation families and the complete equity cache
have passed. No model selection, fitting, population sampling or deployment.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '2'
os.environ['OMP_NUM_THREADS'] = '2'
os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
import json
from pathlib import Path
import time
import numpy as np
import psutil
from sampled_physical_root_evaluation_v1 import ROOT, sha, save, hand_class
from sampled_allin_protocol_v3 import AllinCache
from finite_btn_response_v1 import integrate
from reboot_research_idle_v1 import idle

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'exhaustive-btn-response-v1'
STORE = Path('S:/GTOpen-research')/PREFIX
LOCK = ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER = ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
CANDIDATES = {'combined_269': 'sampled-physical-hybrid-allin',
              'visible_302': 'sampled-visible-hybrid-completion'}


def read(p):
    return json.loads(Path(p).read_text())


def admit_candidate(prefix, inputs):
    for phase in ('evaluation', 'btn-evaluation'):
        paths = {kind: OUT/f'{prefix}-{phase}-v1-{kind}.json' for kind in ('registration', 'result', 'independent-review', 'status')}
        d = {k: read(p) for k, p in paths.items()}
        assert d['status']['state'] == 'complete' and d['independent-review']['passed']
        assert d['result']['registration_sha256'] == sha(paths['registration'])
        if phase == 'evaluation':
            assert d['result']['terminal'] and d['independent-review']['result_sha256'] == sha(paths['result'])
            assert d['independent-review']['registration_sha256'] == sha(paths['registration'])
            assert d['independent-review']['terminal_status_sha256'] == sha(paths['status'])
            reg, result = d['registration'], d['result']
            assert result['played_generations'] == list(range(78)) and result['excluded_unused_generation'] == 78
        else:
            assert d['result']['passed'] and d['independent-review']['inputs'][str(paths['result'])] == sha(paths['result'])
            for p, h in d['independent-review']['inputs'].items():
                assert sha(p) == h, p
        for p, h in d['registration']['inputs'].items():
            assert sha(p) == h, p
        inputs.update({str(p): sha(p) for p in paths.values()})
    trainpath = Path(reg['training_review']); train = read(trainpath)
    assert train['passed'] and train['terminal_complete'] and train['completed_iterations'] == reg['selected_iterations'] == 78
    assert train['source_registration_sha256'] == sha(reg['training_registration'])
    assert train['checkpoint'] == reg['checkpoint']
    for p, h in train['evidence_hashes'].items():
        assert sha(p) == h, p
    inputs[str(trainpath)] = sha(trainpath)
    return reg, result


def load_models(name, registration, source):
    if name == 'combined_269':
        from sampled_physical_hybrid_checkpoint_v1 import read_object, model_document, verify_bank
        from sampled_physical_hybrid_cpu64_v1 import HybridCpuBank64 as CpuBank
        from sampled_physical_hybrid_gpu_bank_v2 import HybridCudaBank64 as GpuBank
    else:
        assert name == 'visible_302'
        from sampled_visible_hybrid_checkpoint_v1 import read_object, model_document, verify_bank
        from sampled_visible_hybrid_cpu64_v1 import VisibleHybridCpuBank64 as CpuBank
        from sampled_visible_hybrid_gpu_bank_v1 import VisibleHybridCudaBank64 as GpuBank
    objects = Path(registration['objects'])
    checkpoint = json.loads(read_object(objects, registration['checkpoint']))
    verify_bank(objects, 78, checkpoint['played_bank'], checkpoint['next_model'], context_source=source)
    return [model_document(objects, r, context_source=source) for r in checkpoint['played_bank']], CpuBank, GpuBank


def main():
    began = time.monotonic(); last = 0.
    def guard():
        nonlocal last
        now = time.monotonic()
        assert now-began < 900, 'Endpoint execution deadline'
        if now-last >= 2:
            assert idle() and psutil.virtual_memory().available >= 20_000_000_000
            last = now
    guard()
    assert not STORE.exists() and not LOCK.exists() and not OTHER.exists()
    context_path = OUT/'bb-context-candidate.json'; source = context_path.read_text(); context = json.loads(source)
    cache_review_path = OUT/'complete-private-allin-cache-v1-independent-review.json'
    cache_result_path = OUT/'complete-private-allin-cache-v1-result.json'
    cache_registration_path = OUT/'complete-private-allin-cache-v1-registration.json'
    cr, cres, creg = read(cache_review_path), read(cache_result_path), read(cache_registration_path)
    assert cr['passed'] and cr['result_sha256'] == sha(cache_result_path)
    assert cr['registration_sha256'] == cres['registration_sha256'] == sha(cache_registration_path)
    assert cr['canonical_private_pairs'] == 47478 and cr['physical_private_pairs'] == 776650
    population_path = Path(creg['population']); population = read(population_path)
    assert sha(population_path) == creg['population_sha256'] and population['context_sha256'] == sha(context_path)
    cache = AllinCache(cr['cache_artifact'], cr['cache_sha256'])
    catalog_result_path = OUT/'preflop-catalog-control-v1-result.json'; catalog_result = read(catalog_result_path)
    catalog_registration_path = OUT/'preflop-catalog-control-v1-registration.json'
    assert catalog_result['passed'] and catalog_result['registration_sha256'] == sha(catalog_registration_path)
    for p, h in read(catalog_registration_path)['inputs'].items():
        assert sha(p) == h, p
    catalog_path = Path(catalog_result['catalog_artifact'])
    assert sha(catalog_path) == catalog_result['catalog_sha256']
    catalog = read(catalog_path); assert catalog['context_source'] == source
    ordered = catalog['native_observations']; observations = [r['observation'] for r in ordered]
    assert len(ordered) == 265 and all(o['own_history'] == [] for o in observations)
    paths = [Path(__file__), ROOT/'tools/research/hu_exhaustive_btn_response_review_20260923.py',
        context_path, population_path, cache_review_path, cache_result_path, cache_registration_path,
        Path(cr['cache_artifact']), catalog_path, catalog_result_path, catalog_registration_path,
        *[ROOT/'tools/research'/n for n in ('finite_btn_response_v1.py', 'sampled_allin_protocol_v3.py',
            'sampled_physical_hybrid_checkpoint_v1.py', 'sampled_visible_hybrid_checkpoint_v1.py',
            'sampled_physical_hybrid_cpu64_v1.py', 'sampled_visible_hybrid_cpu64_v1.py',
            'sampled_physical_hybrid_gpu_bank_v2.py', 'sampled_visible_hybrid_gpu_bank_v1.py',
            'sampled_physical_preflop_table_v1.py', 'reboot_research_idle_v1.py')]]
    inputs = {str(p): sha(p) for p in paths}
    candidates = {name: admit_candidate(prefix, inputs) for name, prefix in CANDIDATES.items()}
    for reg, result in candidates.values():
        assert sha(reg['context']) == sha(context_path)
        inputs.update(reg['inputs'])
    registration = dict(inputs=inputs, candidates=CANDIDATES, population=str(population_path),
        exact_cache=str(cr['cache_artifact']), exact_cache_sha256=cache.sha256,
        catalog=str(catalog_path), complete_played_models=78, excluded_generation=78,
        maximum_seconds=900, endpoint='BTN fold/call after BB jam, with both incoming ranges and BB policy fixed',
        alternatives=['best-class-response', 'always-fold', 'always-call'],
        normalization='bb per original spot entry; conditional rates divide by jam reach',
        sampling_intervals=False, policy_selection=False, production_modified=False)
    registration_path = OUT/f'{PREFIX}-registration.json'
    assert not registration_path.exists(); save(registration_path, registration)
    acquired = False; error = None
    try:
        with LOCK.open('x') as f:
            f.write(str(os.getpid()))
        acquired = True; STORE.mkdir()
        import torch
        torch.set_num_threads(2); torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False
        assert torch.cuda.is_available() and torch.cuda.mem_get_info()[0] >= 3_000_000_000
        output = {}; artifacts = {}
        for name, (reg, prior_result) in candidates.items():
            guard(); models, CpuBank, GpuBank = load_models(name, reg, source)
            queries = dict(context_source=source, observations=observations)
            cpu = CpuBank(models, context_source=source)
            gpu = GpuBank(models, np.ones((2, 78)), context_source=source, models_per_chunk=8, guard=guard)
            p, support = cpu.average(queries, guard=guard)
            q, gpu_support = gpu.average(queries, guard=guard)
            numeric_error = float(np.max(abs(p-q)))
            assert numeric_error < 1e-10 and np.array_equal(support, np.full(265, 78.)) and np.array_equal(support, gpu_support)
            root = np.zeros((169, 4)); btn = [None]*169; keyed = {}
            for row, probability in zip(ordered, p):
                player, c = row['player'], row['hand_class']
                keyed[(player, c)] = (row['observation'], probability)
                if player == 0:
                    root[c] = probability
                else:
                    assert probability[2] == probability[3] == 0
                    btn[c] = float(probability[1])
            native_error = 0.; native_rows = 0; native_keys = set()
            jam_hi = context['nodes'][0]['children'][3] + 1
            for offset in range(0, 256, 16):
                guard(); folder = Path(reg['store'])/f'{reg["id"]}-train-{offset}'
                summary_path = folder/'summary.json'; summary = read(summary_path)
                assert sha(summary_path) == prior_result['batch_summary_hashes'][folder.name]
                profile_path = folder/'profiles.json'
                assert sha(profile_path) == summary['artifacts']['profiles.json']
                profile = read(profile_path); assert profile['context_source'] == source
                baseline = profile['profiles'][0]; assert baseline['name'] == 'baseline'
                for r in baseline['policies']:
                    if int(r['hi']) not in (1, jam_hi):
                        continue
                    actor = 0 if int(r['hi']) == 1 else 1
                    lo = int(r['lo']); c = hand_class([lo & 63, (lo >> 6) & 63])
                    o, wanted = keyed[(actor, c)]
                    assert r['actor'] == actor and int(o['lo']) == lo and o['n'] == r['n']
                    native_error = max(native_error, float(np.max(abs(wanted-r['probabilities']))))
                    native_rows += 1; native_keys.add((actor, c))
                artifacts[str(summary_path)] = sha(summary_path); artifacts[str(profile_path)] = sha(profile_path)
            assert native_rows > 0 and native_error < 1e-10
            policy_path = STORE/f'{name}-policy.json'
            save(policy_path, dict(context_sha256=sha(context_path), checkpoint=reg['checkpoint'],
                played_generations=list(range(78)), excluded_generation=78,
                root_probabilities=root.tolist(), btn_call_probabilities=btn))
            values = integrate(source, population, root, btn, cache.rows)
            output[name] = dict(values=values, policy_artifact=str(policy_path), policy_sha256=sha(policy_path),
                full_catalog_rows=265, maximum_cpu_gpu_error=numeric_error,
                native_reference_rows=native_rows, native_reference_distinct_rows=len(native_keys), maximum_native_reference_error=native_error)
            artifacts[str(policy_path)] = sha(policy_path)
            del gpu, cpu, models
            torch.cuda.empty_cache()
        for path, h in {**inputs, **artifacts}.items():
            assert sha(path) == h, path
        guard()
        result = dict(passed=True, registration_sha256=sha(registration_path), candidates=output,
            artifacts=artifacts, canonical_private_pairs=47478, physical_private_pairs=776650,
            best_response_gain_change_bb_per_entry=output['visible_302']['values']['gains_per_entry']['best']-output['combined_269']['values']['gains_per_entry']['best'],
            seconds=time.monotonic()-began, accuracy_qualified=False, production_modified=False,
            scope='Exhaustive class-based BTN response at the specified all-in node, within the fixed model and numerical checks. No full-game best response, postflop qualification, matched opponent-policy comparison or cross-context claim.')
        save(OUT/f'{PREFIX}-result.json', result)
        print(json.dumps({k: v['values']['gains_per_entry'] for k, v in output.items()}))
    except Exception as exc:
        error = repr(exc)
        raise
    finally:
        save(OUT/f'{PREFIX}-status.json', dict(state='stopped' if error else 'complete', error=error, seconds=time.monotonic()-began, production_modified=False))
        if acquired:
            assert LOCK.read_text().strip() == str(os.getpid())
            LOCK.unlink()


if __name__ == '__main__':
    main()
