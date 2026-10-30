"""Importance-weighted BB root sums; raw visit counts remain separate."""
import copy
import numpy as np
from action_integrated_root_accumulator_v1 import IntegratedRootRegrets
from weighted_deal_binding_v1 import DealWeightGeneration

METHOD = 'source-deal-weighted-bb-root-regrets-v1'


class WeightedRootRegrets(IntegratedRootRegrets):
    def __init__(self, context_sha256, matrix_sha256):
        super().__init__(context_sha256, matrix_sha256)
        self.masses = np.zeros(169, dtype=np.float64)

    def step(self, iteration, audits, *, generation, bindings, expected_deals, expected_batches):
        if (not isinstance(generation, DealWeightGeneration)
                or generation.context_sha256 != self.context_sha256
                or len(generation.deals) != expected_deals or len(bindings) != len(audits)):
            raise ValueError('Complete validated source and paired bindings required')
        # Reuse original target-identity and complete-generation admission on a
        # private copy. No accumulator or sampling RNG changes on rejection.
        admission = IntegratedRootRegrets(self.context_sha256, self.matrix_sha256)
        admission.steps = self.steps
        admission.step(iteration, audits, expected_deals=expected_deals, expected_batches=expected_batches)
        weighted = copy.deepcopy(audits)
        masses = self.masses.copy(); coverage = np.zeros(expected_deals, dtype=np.uint8)
        for original, audit, binding in zip(audits, weighted, bindings):
            start, stop = generation.verify(binding)
            if original['queries_sha256'] != binding['queries_sha256'] or stop-start != len(audit['bb_root_corrections']):
                raise ValueError('Audit detached from native subbatch')
            if np.any(coverage[start:stop]): raise ValueError('Repeated source deals')
            coverage[start:stop] = 1
            for row in audit['bb_root_corrections']:
                i = row['deal']; c = row['hand_class']
                if c != binding['hand_classes'][i]: raise ValueError('Root hand class changed')
                weight = binding['deal_weights'][i]
                row['advantages'] = (np.asarray(row['advantages']) * weight).tolist()
                masses[c] += weight
        if not np.all(coverage) or not np.isfinite(masses).all():
            raise ValueError('Incomplete source coverage or mass overflow')
        # This temporary transport reuses the numerical reducer only; it is
        # never written as an unweighted scientific audit or checkpoint.
        staged = IntegratedRootRegrets(self.context_sha256, self.matrix_sha256)
        staged.steps = self.steps; staged.counts = self.counts.copy(); staged.regrets = self.regrets.copy()
        staged.step(iteration, weighted, expected_deals=expected_deals, expected_batches=expected_batches)
        self.steps, self.counts, self.regrets, self.masses = staged.steps, staged.counts, staged.regrets, masses

    def document(self):
        result = super().document()
        result.update(format=3, method=METHOD, importance_mass=self.masses.tolist(),
            meaning='Source-deal importance-weighted BB root advantage sums; sample_counts are actual visits. Not action EVs or an exact postflop solve.')
        return result

    @classmethod
    def restore(cls, document, *, context_sha256, matrix_sha256):
        if document.get('format') != 3 or document.get('method') != METHOD:
            raise ValueError('Explicit weighted root checkpoint required')
        legacy = dict(document, format=2, method='action-integrated-bb-root-regrets-v1')
        state = IntegratedRootRegrets.restore(legacy, context_sha256=context_sha256, matrix_sha256=matrix_sha256)
        masses = np.asarray(document['importance_mass'], dtype=np.float64)
        if (masses.shape != (169,) or not np.isfinite(masses).all() or np.any(masses < 0)
                or np.any((masses > 0) != (state.counts > 0))
                or np.any(masses > state.counts.astype(float) * 65536)):
            raise ValueError('Invalid accumulated importance mass')
        result = cls(context_sha256, matrix_sha256)
        result.steps, result.counts, result.regrets, result.masses = state.steps, state.counts, state.regrets, masses.copy()
        return result
