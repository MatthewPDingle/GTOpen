"""Native target producer for the genuinely all-node cumulative model contract.

Reuses the checked tree/row/card-removal reduction from v1. The played policy
comes exclusively from ExpectedPolicy; no unused legacy root/BTN states needed.
Caller must still authenticate actual native execution and complete-cycle I/O.
"""
import hashlib
import json
from pathlib import Path

import numpy as np

from board_root_accumulator_v1 import digest
from preflop_expected_native_targets_v1 import FrozenExpectedTargets as Transport
from preflop_expected_native_targets_v1 import physical_class_mass, text_sha
from preflop_expected_policy_v1 import ExpectedPolicy
from preflop_expected_regret_accumulator_v1 import PreflopExpectedRegrets
from sampled_physical_deals_v1 import PhysicalDeals
from stack_context_preflop_expected_components_v2 import PreflopExpectedComponents

METHOD = 'typed-all-preflop-native-targets-v2'


class FrozenExpectedTargets(Transport):
    def __init__(self, *, state, model_source, registry, resources):
        if not isinstance(state, PreflopExpectedRegrets):
            raise ValueError('Qualified complete cumulative state required')
        key = state.config['context_sha256']
        if key not in registry.fit_contexts:
            raise ValueError('Board learning requires a fitted context')
        args = resources[key]; source = registry.source(key)
        self._state = PreflopExpectedRegrets.restore(state.document(),
            context_source=source, matrix_source=args['matrix_source'],
            expected_config=args['expected_config'])
        self._state_sha = self._state.document()['state_sha256']
        self._plan = self._state.plan()
        model = json.loads(model_source)
        self.policy = self._base = ExpectedPolicy(model, registry,
            context_sha256=key, resources=resources)
        if (self.policy.generation != self._state.steps
                or self.policy._state.document()['state_sha256'] != self._state_sha):
            raise ValueError('Target producer and played model need the same frozen state')
        self._pre = self.policy.played_preflop()
        self._geometry = PreflopExpectedComponents(self._state.context, self._state.matrix, self._pre)
        self._sampler = PhysicalDeals(source, mode='full_deck', seed=0)
        raw_mass, pair_mass = physical_class_mass(self._sampler.weights)
        if (not np.isclose(pair_mass, self._sampler.masses[0], rtol=1e-13, atol=1e-10)
                or np.max(abs(raw_mass/pair_mass-self._state.matrix.mass)) > 1e-12):
            raise ValueError('Matrix must retain the original compatible entry law')
        self._exact = {i:r['q'] for i, r in self._geometry.exact().items()}
        self._recipe = dict(method=METHOD, generation=self._state.steps,
            model_sha256=text_sha(model_source), context_sha256=key,
            registry_sha256=registry.sha256, matrix_sha256=state.config['matrix_sha256'],
            physical_catalog_sha256=args['physical_catalog_sha256'],
            cumulative_state_sha256=self._state_sha,
            played_preflop_sha256=digest(self._state.encoded(self._pre)),
            provider_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            transport_sha256=hashlib.sha256(Path(__import__('preflop_expected_native_targets_v1').__file__).read_bytes()).hexdigest(),
            policy_sha256=hashlib.sha256(Path(__import__('preflop_expected_policy_v1').__file__).read_bytes()).hexdigest(),
            entry_rule='Original PhysicalDeals weights, including inherited 1e-5 cutoff',
            private_domain='All 1081 board-legal hands per actor, including zero-weight hands',
            preflop_override='Complete ExpectedPolicy state; legacy sparse/root/BTN states refused',
            maximum_preflop_suit_difference=self.policy.maximum_preflop_suit_difference)
