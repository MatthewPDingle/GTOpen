"""One-shot CPU control of the independent arithmetic/physical-card auditor.

Artificial payoff vectors and synthetic policies on retained real geometries.
No scientific draws, training, native solves, GPU or production access.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
import copy
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback
import numpy as np
from stack_context_independent_audit_v1 import audit_comparison, audit_ranges, physical_population, numerical_context, DEPTHS, N
from stack_context_matched_analysis_v1 import context_analysis, finish
from stack_context_preflop_export_v1 import export
from sampled_physical_root_evaluation_v1 import hand_class

OUT = Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
NAME = 'stack-context-independent-audit-check-v1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, sort_keys=True, separators=(',', ':'), allow_nan=False)
        stream.write('\n')


def json_copy(value):
    return json.loads(json.dumps(value, allow_nan=False))


class Mixture:
    """64 distinct deterministic fixture policies with true per-model own reach."""
    def average(self, queries, *, guard):
        rows = queries['observations']
        classes = np.array([hand_class([(int(r['lo']) >> (6*j)) & 63 for j in (0, 1)]) for r in rows])
        numerator = np.zeros((len(rows), 4)); support = np.zeros(len(rows))
        arities = np.array([r['n'] for r in rows])
        for generation in range(64):
            probability = np.zeros((len(rows), 4))
            for i, row in enumerate(rows):
                node = int(row['hi'])-1
                values = 1+((np.arange(row['n'])+classes[i]+node+generation) % 7).astype(float)
                if node == 0:
                    values[-1] = 0  # An unreachable branch must remain explicitly unavailable.
                probability[i, :row['n']] = values/values.sum()
            own = np.full(len(rows), generation+1., dtype=float)
            for i, row in enumerate(rows):
                for ancestor, action, _ in row['own_history']:
                    own[i] *= probability[ancestor, action]
            numerator += probability*own[:, None]
            support += own
        result = np.divide(numerator, support[:, None], out=np.zeros_like(numerator), where=support[:, None] > 0)
        for i in np.flatnonzero(support == 0):
            result[i, :arities[i]] = 1/arities[i]
        return result, support


def main():
    paths = {kind:OUT/(NAME+'-'+kind+'.json') for kind in ('attempt', 'result', 'failure')}
    if any(p.exists() for p in paths.values()):
        raise ValueError('Preserve the existing started/completed check; no automatic repeat')
    population_path = OUT/'stack-context-population-v1-result.json'
    population = json.loads(population_path.read_bytes())
    inputs = {str(Path(__file__).resolve()):sha(__file__), str(population_path):sha(population_path)}
    for module in list(sys.modules.values()):
        name = getattr(module, '__file__', None)
        if name and Path(name).is_relative_to('T:/Dev/GTOpen') and Path(name).suffix == '.py':
            inputs[str(Path(name))] = sha(name)
    for depth in (20, 60, 400):
        record = next(r for r in population['contexts'].values() if r['depth'] == depth)
        for name in ('context_path', 'physical_catalog', 'matrix'):
            inputs[record[name]] = sha(record[name])
    write(paths['attempt'], dict(inputs=inputs, new_scientific_deals=False, synthetic_payoffs=True, synthetic_policies=True))
    start = time.monotonic(); rejected = []; scenarios = []; ranges = []
    try:
        def rejects(name, fn):
            try:
                fn()
            except (ValueError, KeyError, TypeError):
                rejected.append(name)
            else:
                raise AssertionError('Corruption accepted: '+name)

        for mode in ('positive', 'adverse', 'zero', 'heterogeneous', 'bounded-extremes'):
            raw = {}; reports = []
            for depth in DEPTHS:
                rng = np.random.default_rng(731000+depth)
                values = np.zeros((N, 2, 4, 2))
                common = rng.uniform(-.02, .02, N)*depth
                for seed in range(2):
                    bb_gain = (.2+.01*seed)*depth+common/10
                    btn_gain = (.15+.01*seed)*depth-common/10
                    if mode == 'adverse' and depth == 60 and seed == 0:
                        bb_gain = -.001*depth+common/10
                    if mode == 'zero':
                        bb_gain = np.zeros(N); btn_gain = np.zeros(N)
                    if mode == 'heterogeneous':
                        bb_gain = rng.normal(.002, .05, N)*depth
                        btn_gain = rng.normal(-.001, .1, N)*depth
                    for pairing, (bb, btn) in enumerate(((0, 0), (0, 1), (1, 0), (1, 1))):
                        v = common+bb*bb_gain-btn*btn_gain
                        values[:, seed, pairing, 0] = v
                        values[:, seed, pairing, 1] = .5-v
                if mode == 'bounded-extremes':
                    # Stress clipping/variance/tails; not claimed to be a legal poker policy.
                    values = np.where(rng.integers(0, 2, values.shape), float(-depth), depth+.5)
                raw[depth] = values
                reports.append(context_analysis(values, depth=depth, dead_money=.5))
            comparison = json_copy(finish(reports))
            audit = audit_comparison(comparison, raw)
            assert audit['independent_primary_gate'] is (mode == 'positive')
            scenarios.append(dict(mode=mode, **audit))
            if mode == 'positive':
                positive_raw, positive_comparison = raw, comparison

        def changed_context(field, value):
            changed = copy.deepcopy(positive_comparison); changed['contexts'][0][field] = value
            return changed
        for field, value in (('deals', 2048), ('family_error_probability', .05), ('dead_money', 0.),
                ('split', 'heldout'), ('profile_order', []), ('bounds_best_response_above', True),
                ('accuracy_qualified', True), ('exploratory_normal_family_size', 8)):
            rejects('context/'+field, lambda f=field, v=value:audit_comparison(changed_context(f, v), positive_raw))
        for field in ('mean', 'sample_variance', 'radius', 'lower', 'upper', 'standard_error',
                'negative_deal_fraction', 'paired_loss_95_bb', 'paired_loss_99_bb',
                'worst_observed_paired_loss_bb', 'mean_positive_paired_loss_bb'):
            changed = copy.deepcopy(positive_comparison)
            changed['contexts'][0]['contrasts'][0][field] += .1
            rejects('contrast/'+field, lambda x=changed:audit_comparison(x, positive_raw))
        for field, value in (('registered_policy_improvement_criterion_met', False), ('production_promotion', True),
                             ('preflop_accuracy_qualified', True), ('simultaneous_family_alpha', .1)):
            changed = copy.deepcopy(positive_comparison); changed[field] = value
            rejects('summary/'+field, lambda x=changed:audit_comparison(x, positive_raw))
        changed = copy.deepcopy(positive_comparison)
        changed['equal_depth_normalized_gains'][0]['mean'] += .01
        rejects('pooled-normalization', lambda:audit_comparison(changed, positive_raw))
        rejects('missing-depth', lambda:audit_comparison(positive_comparison, {20:positive_raw[20]}))
        rejects('interim-look', lambda:numerical_context(positive_raw[20][:32], 20))
        for bad in (float('nan'), 21., -21.):
            values = positive_raw[20].copy(); values[0, 0, 0, 0] = bad
            rejects('nonfinite-or-out-of-bounds/'+str(bad), lambda v=values:numerical_context(v, 20))

        for depth in (20, 60, 400):
            record = next(r for r in population['contexts'].values() if r['depth'] == depth)
            source = Path(record['context_path']).read_text(); context = json.loads(source)
            catalog = json.loads(Path(record['physical_catalog']).read_bytes())
            matrix = json.loads(Path(record['matrix']).read_bytes())
            answer = json_copy(export(source, catalog, matrix['class_mass'], Mixture(), guard=lambda:None))
            audit = audit_ranges(context, answer, guard=lambda:None)
            assert audit['zero_arrival_nodes'] > 0
            assert audit['decision_nodes'] == len(answer['nodes'])
            cards, classes, physical = physical_population(context)
            assert len(cards) == 1326 and len(set(classes)) == 169
            assert len(cards[np.all(cards == [48, 49], axis=1)]) == 1
            assert classes[np.flatnonzero(np.all(cards == [48, 49], axis=1))[0]] == 168
            aggregate = np.bincount((classes[:, None]*169+classes[None, :]).ravel(),
                weights=physical.ravel(), minlength=169*169).reshape(169, 169)
            mass_error = float(np.max(np.abs(aggregate-np.asarray(matrix['class_mass']))))
            assert mass_error < 1e-12
            ranges.append(dict(depth=depth, **audit, independently_reconstructed_class_mass_error=mass_error))
            if depth != 60:
                continue
            for field in ('probability_of_reaching_node', 'entry_mass_by_class', 'conditional_range_by_class',
                    'conditional_action_frequencies', 'own_history_weighted_model_support_by_class'):
                changed = copy.deepcopy(answer)
                if isinstance(changed['nodes'][0][field], list):changed['nodes'][0][field][0] += .1
                else:changed['nodes'][0][field] += .1
                rejects('range/'+field, lambda x=changed:audit_ranges(context, x, guard=lambda:None))
            for field, value in (('actor', 1), ('path', [[0, 1]]), ('in_arriving_range', [False]*169)):
                changed = copy.deepcopy(answer); changed['nodes'][0][field] = value
                rejects('range/'+field, lambda x=changed:audit_ranges(context, x, guard=lambda:None))
            changed = copy.deepcopy(answer); changed['nodes'][0]['action_probabilities_by_class'][0][0] += .1
            rejects('range/unnormalized-policy', lambda:audit_ranges(context, changed, guard=lambda:None))
            changed = copy.deepcopy(answer); changed['nodes'] = changed['nodes'][:-1]
            rejects('range/missing-node', lambda:audit_ranges(context, changed, guard=lambda:None))
            changed = copy.deepcopy(answer); changed['nodes'].append(copy.deepcopy(changed['nodes'][0]))
            rejects('range/repeated-node', lambda:audit_ranges(context, changed, guard=lambda:None))
            changed = copy.deepcopy(answer)
            next(r for r in changed['nodes'] if r['zero_node_reach'])['conditional_action_frequencies'] = [1.]
            rejects('range/invented-zero-node-frequency', lambda:audit_ranges(context, changed, guard=lambda:None))
        for path, digest in inputs.items():
            assert sha(path) == digest
        result = dict(complete=True, passed=True, seconds=time.monotonic()-start, inputs=inputs,
            arithmetic_scenarios=scenarios, physical_range_checks=ranges, negative_cases=rejected,
            new_scientific_deals=False, new_labels=False, new_fits=False, native_execution=False,
            gpu_used=False, production_modified=False, full_readback_controller_complete=False,
            scientific_accuracy_qualified=False)
        write(paths['result'], result)
        print(json.dumps(dict(passed=True, seconds=result['seconds'], arithmetic_scenarios=len(scenarios),
            physical_contexts=len(ranges), negative_cases=len(rejected))))
    except BaseException as error:
        write(paths['failure'], dict(error=repr(error), traceback=traceback.format_exc(), preserve_evidence=True,
            automatic_repeat_allowed=False))
        raise


if __name__ == '__main__':main()
