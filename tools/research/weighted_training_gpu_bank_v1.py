"""Typed weighted-model bank; reuse only the shared numerical CUDA evaluator."""
from types import SimpleNamespace
import numpy as np
from sampled_visible_hybrid_gpu_bank_shared_v1 import VisibleHybridCudaBank64, prepare_cuda_queries
from weighted_training_checkpoint_v1 import validate_model
from weighted_training_policy_v1 import RootTable
from weighted_preflop_table_v1 import Table


class WeightedCudaBank64(VisibleHybridCudaBank64):
    def __init__(self, documents, weights_by_player, *, completed_iterations,
                 context_source, catalog_source, matrix_sha256, entry_mass,
                 models_per_chunk=8, guard):
        import torch
        models = list(documents)
        if type(completed_iterations) is not int or completed_iterations < 1 or len(models) != completed_iterations:
            raise ValueError('Complete played model bank required')
        if type(models_per_chunk) is not int or models_per_chunk < 1:
            raise ValueError('Positive model chunk required')
        if not torch.cuda.is_available() or torch.backends.cuda.matmul.allow_tf32 or torch.backends.cudnn.allow_tf32:
            raise ValueError('CUDA with explicitly disabled TF32 required')
        weights = np.asarray(weights_by_player, dtype=np.float64)
        if weights.shape != (2, completed_iterations) or not np.isfinite(weights).all() or np.any(weights <= 0) or not np.isfinite(weights.sum()):
            raise ValueError('Two positive finite weight sequences required')
        self.tables = []
        self.context_source = context_source
        self.exact_geometry = None
        shapes = {'w0': (64, 302), 'b0': (64,), 'w1': (64, 64), 'b1': (64,), 'w2': (4, 64), 'b2': (4,)}
        values = {name: [] for name in shapes}
        for generation, document in enumerate(models):
            guard()
            root_state, _, exact = validate_model(document, context_source=context_source,
                catalog_source=catalog_source, matrix_sha256=matrix_sha256, entry_mass=entry_mass)
            if document['generation'] != generation:
                raise ValueError('Reordered or unplayed weighted model')
            pair = [None if d is None else Table(d, context_source) for d in document['preflop_tables']]
            root = RootTable(root_state, context_source, catalog_source)
            rows = {} if pair[0] is None else dict(pair[0].rows)
            rows.update(root.rows)
            pair[0] = SimpleNamespace(player=0, context=root.context, rows=rows)
            pair[1] = exact.compose(pair[1])
            self.tables.append(pair)
            self.exact_geometry = exact
            for name, shape in shapes.items():
                # Stored float32 parameters widened exactly, as in the reference reader.
                value = np.asarray([net[name] for net in document['networks']], dtype=np.float32)
                values[name].append(value.reshape(2, *shape))
        self.parameters = {name: torch.as_tensor(np.stack(value).astype(np.float64), device='cuda')
                           for name, value in values.items()}
        self.weights = torch.as_tensor(weights.copy(), device='cuda')
        self.count = completed_iterations
        self.chunk = models_per_chunk

    def average(self, queries, *, guard):
        return self.average_prepared(prepare_cuda_queries(queries, guard=guard), guard=guard)

    def average_prepared(self, prepared, *, guard):
        obs = prepared.queries['observations']
        for o in obs:
            if int(o['hi']) == 1 and (o['actor'] != 0 or o['own_history'] != []):
                raise ValueError('Root must have no own-action ancestors')
        self.exact_geometry.validate_queries(obs)
        return super().average_prepared(prepared, guard=guard)
