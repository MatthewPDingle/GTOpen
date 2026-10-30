"""Cache model weights and encode each native query batch once per played bank.

The average still uses every played generation and its own complete policy reach.
This adapter does not choose models, approximate reach, or include an unplayed fit.
"""
import numpy as np
from stack_context_current_policy_v1 import CurrentPolicy


class PlayedBank:
    def __init__(self, documents, registry, *, context_sha256, resources,
                 weights_by_player, completed_cycles, device, guard):
        if (type(completed_cycles) is not int or completed_cycles < 1
                or len(documents) != completed_cycles):
            raise ValueError('Exactly the complete played bank is required')
        weights = np.asarray(weights_by_player, dtype=np.float64)
        if (weights.shape != (2, completed_cycles) or not np.isfinite(weights).all()
                or np.any(weights <= 0) or not np.isfinite(weights.sum())):
            raise ValueError('Positive finite weights for both complete played banks required')
        self.weights = weights.copy()
        self.engines = []
        kind = documents[0]['shared']['policy_type']
        for generation, document in enumerate(documents):
            guard()
            if (document['generation'] != generation
                    or document['shared']['policy_type'] != kind):
                raise ValueError('Reordered, unplayed, or mixed-representation model bank')
            self.engines.append(CurrentPolicy(document, registry,
                context_sha256=context_sha256, resources=resources, device=device))
        self.context_sha256 = context_sha256
        self.completed_cycles = completed_cycles

    def average(self, queries, *, guard):
        guard()
        # Keys, public geometry, native features, and genuine ancestor links are
        # model-independent. Model-local table overrides and reach are not.
        prepared = self.engines[0].prepare(queries)
        actor, arity = prepared['actors'], prepared['arity']
        numerator = np.zeros((len(actor), 4), dtype=np.float64)
        denominator = np.zeros(len(actor), dtype=np.float64)
        uniform = prepared['legal'].astype(np.float64) / arity[:, None]
        for generation, engine in enumerate(self.engines):
            guard()
            table = uniform.copy()
            mask = np.zeros(len(actor), dtype=bool)
            # Use each generation's overrides in exactly the established order.
            for overlay in engine.tables:
                table, ids = overlay.apply(queries['observations'], table)
                mask[np.asarray(ids, dtype=int)] = True
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
