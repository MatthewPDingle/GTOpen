"""Exact BB deviation that only reallocates existing fold/shove probability.

Uses the same two fully audited policies as the exhaustive BTN endpoint. Does
not infer new policies, train a responder, alter call/raise paths or deploy.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '2'
os.environ['OMP_NUM_THREADS'] = '2'
import json
from pathlib import Path
import time
import numpy as np
from finite_bb_root_components_v1 import components, exact_difference
from sampled_allin_protocol_v3 import AllinCache
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from reboot_research_idle_v1 import idle

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'bb-fold-jam-response-v1'
SOURCE = 'exhaustive-btn-response-v1'
LOCK = ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER = ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def read(path):
    return json.loads(Path(path).read_text())


def reallocate(baseline, fold_value, jam_value):
    """Preserve nonterminal frequencies; retain the original mix on a tie."""
    response = list(baseline)
    mass = baseline[0]+baseline[3]
    if jam_value > fold_value:
        response[0], response[3] = 0., mass
    elif fold_value > jam_value:
        response[0], response[3] = mass, 0.
    return response


def main():
    began = time.monotonic(); assert idle() and not LOCK.exists() and not OTHER.exists()
    rp = OUT/f'{PREFIX}-registration.json'; assert not rp.exists()
    source_paths = {k: OUT/f'{SOURCE}-{k}.json' for k in ('registration', 'result', 'independent-review', 'status')}
    prior = {k: read(p) for k, p in source_paths.items()}
    assert prior['status']['state'] == 'complete' and prior['status']['error'] is None
    assert prior['result']['passed'] and prior['independent-review']['passed']
    assert prior['result']['registration_sha256'] == prior['independent-review']['registration_sha256'] == sha(source_paths['registration'])
    assert prior['independent-review']['result_sha256'] == sha(source_paths['result'])
    assert set(prior['result']['candidates']) == {'combined_269', 'visible_302'}
    assert prior['result']['canonical_private_pairs'] == 47478 and prior['result']['physical_private_pairs'] == 776650
    context_path = OUT/'bb-context-candidate.json'; source = context_path.read_text()
    population_path = Path(prior['registration']['population']); population = read(population_path)
    cache = AllinCache(prior['registration']['exact_cache'], prior['registration']['exact_cache_sha256'])
    paths = [Path(__file__), ROOT/'tools/research/hu_bb_fold_jam_response_review_20260923.py',
        *source_paths.values(), context_path, population_path,
        *[ROOT/'tools/research'/n for n in ('finite_bb_root_components_v1.py',
            'finite_btn_response_v1.py', 'sampled_allin_protocol_v3.py',
            'sampled_physical_root_evaluation_v1.py', 'reboot_research_idle_v1.py')]]
    inputs = {**prior['registration']['inputs'], **prior['result']['artifacts'],
              **{str(p):sha(p) for p in paths}}
    for p, h in inputs.items():
        assert sha(p) == h, p
    registration = dict(inputs=inputs, candidates=['combined_269', 'visible_302'],
        source_result=str(source_paths['result']), source_registration=str(source_paths['registration']),
        maximum_seconds=180, fixed_alternative='Keep call/raise frequencies; move combined fold/jam mass to the higher conditional-value action for each class',
        ties='Retain baseline fold/jam mix on exact ties', units='bb per original spot entry',
        selection=False, sampling_intervals=False, production_modified=False)
    save(rp, registration)
    error = None; acquired = False
    try:
        with LOCK.open('x') as f:
            f.write(str(os.getpid()))
        acquired = True; output = {}
        for name in registration['candidates']:
            assert idle() and time.monotonic()-began < 180
            item = prior['result']['candidates'][name]; policy = read(item['policy_artifact'])
            assert sha(item['policy_artifact']) == item['policy_sha256']
            assert policy['context_sha256'] == sha(context_path)
            assert policy['played_generations'] == list(range(78)) and policy['excluded_generation'] == 78
            baseline = np.asarray(policy['root_probabilities'])
            table = components(source, population, baseline, policy['btn_call_probabilities'], cache.rows)
            response = baseline.copy(); rows = []
            for c, row in enumerate(table['classes']):
                mass = row['entry_probability']
                assert mass > 0  # The admitted full BB incoming support covers all classes.
                qf = row['fold_value_per_entry']/mass; qj = row['conditional_jam_value']
                response[c] = reallocate(baseline[c], qf, qj)
                gain = ((response[c, 0]-baseline[c, 0])*row['fold_value_per_entry']
                        +(response[c, 3]-baseline[c, 3])*row['jam_value_per_entry'])
                assert gain >= -1e-10
                rows.append(dict(hand_class=c, entry_probability=mass,
                    fold_value=qf, jam_value=qj, gain_per_entry=gain,
                    baseline=baseline[c].tolist(), response=response[c].tolist()))
            assert np.array_equal(response[:, 1:3], baseline[:, 1:3])
            gain = exact_difference(table, baseline, response)
            assert gain >= -1e-10 and abs(gain-sum(r['gain_per_entry'] for r in rows)) < 1e-10
            output[name] = dict(gain_bb_per_entry=gain, classes=rows,
                unchanged_call_raise=True, positive_gain_classes=sum(r['gain_per_entry']>1e-10 for r in rows))
        for p, h in inputs.items():
            assert sha(p) == h, p
        assert idle() and time.monotonic()-began < 180
        save(OUT/f'{PREFIX}-result.json', dict(passed=True, registration_sha256=sha(rp),
            candidates=output, seconds=time.monotonic()-began, accuracy_qualified=False,
            production_modified=False,
            scope='Restricted profitable-deviation lower bound against each fixed opponent. Call/raise behavior cancels unchanged; no full best-response upper bound, common-opponent ranking or postflop accuracy claim.'))
        print(json.dumps({k:v['gain_bb_per_entry'] for k,v in output.items()}))
    except BaseException as exc:
        error = repr(exc); raise
    finally:
        save(OUT/f'{PREFIX}-status.json', dict(state='stopped' if error else 'complete', error=error,
            seconds=time.monotonic()-began, production_modified=False))
        if acquired:
            assert LOCK.read_text().strip() == str(os.getpid())
            LOCK.unlink()


if __name__ == '__main__':
    main()
