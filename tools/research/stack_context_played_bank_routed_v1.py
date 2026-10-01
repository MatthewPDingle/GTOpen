"""Separate candidate: route repeated played-bank overrides to preflop rows.

The constructor, feature/history validation, networks, generation order, local
override order, own-history reach, weights and unsupported fallback remain the
original ones. This module is not installed in the registered comparison.
"""
import numpy as np
from stack_context_played_bank_v1 import PlayedBank as OriginalBank
from weighted_preflop_table_v1 import Table
from exact_btn_policy_table_v1 import ExactBtnTable
from board_training_policy_v1 import RootTable


class PlayedBank(OriginalBank):
    def average(self, queries, *, guard):
        guard()
        # Keep the original first preparation, including its complete validation.
        prepared = self.engines[0].prepare(queries)
        observations = queries['observations']
        actor, arity = prepared['actors'], prepared['arity']
        ids = np.flatnonzero([row['phase'] == 0 for row in observations])
        subset = [observations[i] for i in ids]
        numerator = np.zeros((len(actor), 4), dtype=np.float64)
        denominator = np.zeros(len(actor), dtype=np.float64)
        uniform = prepared['legal'].astype(np.float64) / arity[:, None]
        for generation, engine in enumerate(self.engines):
            guard()
            table = uniform.copy()
            mask = np.zeros(len(actor), dtype=bool)
            if engine.tables:
                # These are precisely the current preflop-only overlay types.
                # A future overlay contract needs separate qualification.
                if any(type(overlay) not in (Table, ExactBtnTable, RootTable)
                       for overlay in engine.tables):
                    raise ValueError('Unqualified played-bank overlay type')
                if np.any(~np.isin(arity, (2, 3, 4))):
                    raise ValueError('Invalid input actor or legal action probabilities')
                if len(ids):
                    routed = table[ids]
                    for overlay in engine.tables:
                        routed, matched = overlay.apply(subset, routed)
                        mask[ids[np.asarray(matched, dtype=int)]] = True
                    table[ids] = routed
            view = dict(prepared, table=table, mask=mask, owner=engine)
            probability = engine.infer(view)
            reach = self.weights[actor, generation].copy()
            for row, history in enumerate(prepared['own_history']):
                for parent, action in history:
                    reach[row] *= probability[parent, action]
            numerator += reach[:, None] * probability
            denominator += reach
        supported = denominator > 0
        result = uniform.copy()
        result[supported] = numerator[supported] / denominator[supported, None]
        if (not np.isfinite(result).all() or not np.isfinite(denominator).all()
                or np.any(result < 0) or np.any(denominator < 0)
                or np.any(result[~prepared['legal']])
                or np.max(abs(result.sum(1) - 1)) > 1e-12):
            raise ValueError('Invalid complete played average')
        return result, denominator
