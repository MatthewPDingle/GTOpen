"""Explicit action-integrated root override, separate from sampled reservoir tables."""
import hashlib
import json
from types import SimpleNamespace
import numpy as np
from showdown_root_accumulator_v1 import ShowdownRootRegrets
from sampled_physical_preflop_table_v1 import Table, validate_preflop
from sampled_physical_root_evaluation_v1 import hand_class

METHOD = 'showdown-controlled-bb-root-policy-table-v1'


def digest(source):
    return hashlib.sha256(source.encode('utf-8')).hexdigest()


def document(state, *, context_source, catalog_source):
    value = dict(format=4, method=METHOD, player=0,
        context_sha256=digest(context_source), catalog_sha256=digest(catalog_source),
        matrix_sha256=state.matrix_sha256, coefficients_sha256=state.coefficients_sha256, state=state.document(),
        missing_policy='Preserve supplied base probabilities until a class has at least one root sample.',
        meaning='Action-integrated BB root regret sums override the sampled root table; later nodes and base network are unchanged.')
    ShowdownRootTable(value, context_source, catalog_source,
                     matrix_sha256=state.matrix_sha256)
    return value


class ShowdownRootTable:
    def __init__(self, value, context_source, catalog_source, *, matrix_sha256):
        if value.get('format') != 4 or value.get('method') != METHOD or value.get('player') != 0:
            raise ValueError('Explicit action-integrated root policy format required')
        if (value.get('context_sha256') != digest(context_source)
                or value.get('catalog_sha256') != digest(catalog_source)
                or value.get('matrix_sha256') != matrix_sha256):
            raise ValueError('Root policy context, catalog or matrix changed')
        state = ShowdownRootRegrets.restore(value['state'],
            context_sha256=digest(context_source), matrix_sha256=matrix_sha256,
            coefficients_sha256=value['coefficients_sha256'])
        context = json.loads(context_source); root = context['nodes'][0]
        if (root['kind'] != 0 or root['actor'] != 0
                or [a['kind'] for a in root['actions']] != ['fold', 'call', 'raise', 'jam']):
            raise ValueError('Four-action BB root required')
        catalog = json.loads(catalog_source)
        if catalog['context_source'] != context_source:
            raise ValueError('Catalog belongs to another context')
        p = state.probabilities(np.full((169,4), .25)); rows = {}; seen = set()
        for item in catalog['native_observations']:
            if item['player'] != 0:
                continue
            o = item['observation']; key = validate_preflop(o, context, 0)
            if key[0] != 1 or o['phase'] != 0 or o['n'] != 4 or o['own_history'] != []:
                raise ValueError('Root catalog must contain first BB decisions')
            c = hand_class([key[1] & 63, (key[1] >> 6) & 63])
            if c in seen or c != item['hand_class']:
                raise ValueError('Duplicate or mislabeled root class')
            seen.add(c)
            if state.counts[c]:
                rows[key] = (4, tuple(sorted(o['active_features'])), p[c])
        if seen != set(range(169)):
            raise ValueError('Complete BB root class catalog required')
        self.player = 0; self.context = context; self.rows = rows
        self.completed_updates = state.steps

    def validate_queries(self, observations):
        for o in observations:
            if int(o['hi']) == 1 and (o['actor'] != 0 or o['own_history'] != []):
                raise ValueError('BB root must have no own-action ancestors')

    def apply(self, observations, probabilities):
        self.validate_queries(observations)
        return Table.apply(self, observations, probabilities)

    def compose(self, sampled):
        if sampled is not None and (sampled.player != 0 or sampled.context != self.context):
            raise ValueError('Wrong base table context or actor')
        rows = {} if sampled is None else dict(sampled.rows)
        rows.update(self.rows)
        combined = SimpleNamespace(player=0, context=self.context, rows=rows)
        def apply(observations, probabilities):
            self.validate_queries(observations)
            return Table.apply(combined, observations, probabilities)
        combined.apply = apply
        return combined
