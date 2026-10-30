"""Typed version-8 shared-query inference candidate; full-bank qualification required."""
from showdown_root_policy_v1 import prepare
from exact_initial_hybrid_policy_v1 import prepare as prepare_exact
from sampled_visible_hybrid_gpu_bank_shared_v1 import (
    VisibleHybridCudaBank64,
    prepare_cuda_queries,
)


class ShowdownRootCudaBankShared64:
    def __init__(self, documents, weights_by_player, *, completed_iterations,
                 context_source, catalog_source, matrix_sha256, entry_mass,
                 models_per_chunk=8, guard):
        docs, roots = prepare(documents, completed_iterations, context_source,
            catalog_source, matrix_sha256, entry_mass)
        exact_docs, exact = prepare_exact([d['exact_model'] for d in docs],
            completed_iterations, context_source, catalog_source, matrix_sha256, entry_mass)
        self.bank = VisibleHybridCudaBank64([d['base_model'] for d in exact_docs],
            weights_by_player, context_source=context_source,
            models_per_chunk=models_per_chunk, guard=guard)
        for pair, table, root in zip(self.bank.tables, exact, roots):
            pair[1] = table.compose(pair[1])
            pair[0] = root.compose(pair[0])
        self.geometry = roots[0]
        self.exact_geometry = exact[0]

    def average(self, queries, *, guard):
        return self.average_prepared(prepare_cuda_queries(queries, guard=guard), guard=guard)

    def average_prepared(self, prepared, *, guard):
        queries = prepared.queries
        self.geometry.validate_queries(queries['observations'])
        self.exact_geometry.validate_queries(queries['observations'])
        return self.bank.average_prepared(prepared, guard=guard)
