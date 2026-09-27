"""Validate a complete stratified draw before binding its native subbatches."""
import copy
import json
import numpy as np
from class_stratified_physical_deals_v1 import METHOD as SAMPLER_METHOD
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import CLASSES, PAIRS
from sampled_physical_root_evaluation_v1 import hand_class
from exact_initial_training_ingest_v2 import digest
from weighted_physical_reservoir_v1 import checked_weight

METHOD = 'validated-stratified-source-deal-binding-v1'


class DealWeightGeneration:
    def __init__(self, document, context_source):
        d = copy.deepcopy(document)
        base = PhysicalDeals(context_source, mode='full_deck', seed=0)
        mass = np.bincount(CLASSES, weights=base.first[0], minlength=169)
        active = np.flatnonzero(mass > 0)
        if (d.get('format') != 1 or d.get('method') != SAMPLER_METHOD
                or d.get('context_sha256') != base.context_sha256):
            raise ValueError('Explicit stratified source identity required')
        n = len(d['deals'])
        if not len(active) <= n <= 65536:
            raise ValueError('Complete bounded stratified generation required')
        if len(d['hand_classes']) != n or len(d['deal_weights']) != n:
            raise ValueError('Deal metadata length mismatch')
        classes = []
        pair_index = {tuple(map(int, p)): i for i, p in enumerate(PAIRS)}
        for cards in d['deals']:
            if (len(cards) != 9 or any(type(c) is not int or not 0 <= c < 52 for c in cards)
                    or len(set(cards)) != 9 or cards[:2] != sorted(cards[:2])
                    or cards[2:4] != sorted(cards[2:4]) or cards[4:7] != sorted(cards[4:7])):
                raise ValueError('Canonical physical deal required')
            i, j = pair_index[tuple(cards[:2])], pair_index[tuple(cards[2:4])]
            if base.weights[0, i] <= 0 or base.weights[1, j] <= 0:
                raise ValueError('Deal outside source range support')
            classes.append(hand_class(cards[:2]))
        if (any(type(c) is not int for c in d['hand_classes']) or classes != d['hand_classes']):
            raise ValueError('Hand class detached from physical cards')
        counts = np.bincount(classes, minlength=169)
        declared = d['class_counts']
        if (len(declared) != 169 or any(type(x) is not int for x in declared)
                or declared != counts.tolist() or np.any(counts[mass == 0])
                or np.any(counts[active] < n // len(active))
                or np.any(counts[active] > (n + len(active) - 1) // len(active))):
            raise ValueError('Invalid class allocation')
        supplied_mass = np.asarray(d['class_mass'], dtype=np.float64)
        if (supplied_mass.shape != (169,) or not np.isfinite(supplied_mass).all()
                or np.max(abs(supplied_mass - mass)) > 1e-14):
            raise ValueError('Class masses do not match original game')
        weights = np.array([checked_weight(w) for w in d['deal_weights']])
        expected = n * mass[classes] / counts[classes]
        if np.max(abs(weights - expected)) > 1e-12:
            raise ValueError('Weights do not recover original physical distribution')
        self.context_source = context_source
        self.context_sha256 = base.context_sha256
        self.sha256 = digest(d)
        self.deals = tuple(tuple(c) for c in d['deals'])
        self.classes = tuple(classes)
        self.weights = tuple(map(float, weights))

    def bind(self, queries, start):
        if type(start) is not int or start < 0 or queries['context_source'] != self.context_source:
            raise ValueError('Invalid subbatch context or offset')
        batch = json.loads(queries['batch_source'])
        deals = batch['deals']; stop = start + len(deals)
        if not deals or stop > len(self.deals) or tuple(tuple(c) for c in deals) != self.deals[start:stop]:
            raise ValueError('Native deals do not match weighted source slice')
        return dict(format=1, method=METHOD, source_sha256=self.sha256,
            context_sha256=self.context_sha256, queries_sha256=digest(queries),
            start=start, stop=stop, hand_classes=list(self.classes[start:stop]),
            deal_weights=list(self.weights[start:stop]))

    def verify(self, binding):
        if (binding.get('format') != 1 or binding.get('method') != METHOD
                or binding.get('source_sha256') != self.sha256
                or binding.get('context_sha256') != self.context_sha256):
            raise ValueError('Wrong source-deal binding')
        start, stop = binding['start'], binding['stop']
        if (type(start) is not int or type(stop) is not int or not 0 <= start < stop <= len(self.deals)
                or binding['hand_classes'] != list(self.classes[start:stop])
                or binding['deal_weights'] != list(self.weights[start:stop])):
            raise ValueError('Source weights or slice changed')
        return start, stop
