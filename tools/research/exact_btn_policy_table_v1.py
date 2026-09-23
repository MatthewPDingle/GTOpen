"""Distinct runtime override for exact cumulative BTN first-response regrets.

This is not a retained-sample table. It adds no reservoir rows or observation
counts. The current trainer and evaluation do not import this module.
"""
import hashlib
import json
import re
from types import SimpleNamespace
import numpy as np
from exact_btn_regret_accumulator_v1 import ExactBtnRegrets
from sampled_physical_preflop_table_v1 import Table, validate_preflop
from sampled_physical_root_evaluation_v1 import hand_class

METHOD = 'exact-btn-first-response-policy-table-v1'


def digest(source):
    return hashlib.sha256(source.encode('utf-8')).hexdigest()


def document(state, *, context_source, catalog_source, matrix_sha256):
    result = dict(format=2, method=METHOD, context_sha256=digest(context_source),
        catalog_sha256=digest(catalog_source), matrix_sha256=matrix_sha256,
        player=1, state=state.document(),
        missing_policy='Preserve the supplied base policy until positive accumulated shove reach.',
        meaning='Exact cumulative counterfactual regrets override this first response; no sampled count or retained mean.')
    ExactBtnTable(result, context_source, catalog_source,
                  matrix_sha256=matrix_sha256, entry_mass=state.mass)
    return result


class ExactBtnTable:
    def __init__(self, value, context_source, catalog_source, *, matrix_sha256, entry_mass):
        if value.get('format') != 2 or value.get('method') != METHOD or value.get('player') != 1:
            raise ValueError('Explicit exact BTN policy-table format required')
        if value.get('context_sha256') != digest(context_source) or value.get('catalog_sha256') != digest(catalog_source):
            raise ValueError('Context or visible catalog changed')
        if not isinstance(matrix_sha256, str) or not re.fullmatch('[0-9a-f]{64}', matrix_sha256) or value.get('matrix_sha256') != matrix_sha256:
            raise ValueError('Admitted exact population matrix identity required')
        state = ExactBtnRegrets.restore(value['state'], context_sha256=digest(context_source), entry_mass=entry_mass)
        context = json.loads(context_source)
        root = context['nodes'][0]
        jams = [i for i, a in enumerate(root['actions']) if a['kind'] == 'jam']
        if root['kind'] != 0 or root['actor'] != 0 or len(jams) != 1:
            raise ValueError('BB first decision with one initial shove required')
        response_index = root['children'][jams[0]]
        response = context['nodes'][response_index]
        if response['kind'] != 0 or response['actor'] != 1 or [a['kind'] for a in response['actions']] != ['fold', 'call']:
            raise ValueError('Direct BTN fold/call response required')
        if any(context['nodes'][i]['kind'] == 0 for i in response['children']):
            raise ValueError('Initial all-in response must end preflop decisions')
        catalog = json.loads(catalog_source)
        if catalog['context_source'] != context_source:
            raise ValueError('Catalog belongs to another game')
        probabilities = state.probabilities(np.full((169, 2), .5))
        rows = {}
        seen = set()
        for item in catalog['native_observations']:
            if item['player'] != 1:
                continue
            o = item['observation']
            key = validate_preflop(o, context, 1)
            if key[0] != response_index + 1 or o['phase'] != 0 or o['n'] != 2 or o['own_history'] != []:
                raise ValueError('Catalog response is not the first BTN action')
            lo = int(o['lo'])
            c = hand_class([lo & 63, (lo >> 6) & 63])
            if c != item['hand_class'] or c in seen or state.mass[c] <= 0:
                raise ValueError('Duplicate, absent or mislabeled response class')
            seen.add(c)
            if state.reach[c] > 0:
                p = np.zeros(4)
                p[:2] = probabilities[c]
                rows[key] = (2, tuple(sorted(o['active_features'])), p)
        if seen != set(np.flatnonzero(state.mass > 0)):
            raise ValueError('Catalog must cover every incoming BTN class exactly once')
        self.player = 1
        self.context = context
        self.context_sha256 = digest(context_source)
        self.rows = rows
        self.completed_updates = state.steps
        self.response_hi = response_index + 1

    def apply(self, observations, probabilities):
        # This method validates query features, keys, action count and phase.
        # It consumes only a probability lookup; no sampled-table serialization
        # or invented count is passed to the older Table constructor.
        self.validate_queries(observations)
        return Table.apply(self, observations, probabilities)

    def validate_queries(self, observations):
        for o in observations:
            if int(o['hi']) == self.response_hi and o['own_history'] != []:
                raise ValueError('Initial BTN response cannot have own-action ancestors')

    def compose(self, sampled):
        """Exact rows take precedence; other sampled rows remain untouched."""
        if sampled is not None and (sampled.player != 1 or sampled.context != self.context):
            raise ValueError('Wrong base table context or actor')
        rows = {} if sampled is None else dict(sampled.rows)
        rows.update(self.rows)
        combined = SimpleNamespace(player=1, context=self.context, rows=rows)
        def apply(observations, probabilities):
            self.validate_queries(observations)
            return Table.apply(combined, observations, probabilities)
        combined.apply = apply
        return combined
