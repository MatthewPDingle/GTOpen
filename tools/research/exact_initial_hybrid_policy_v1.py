"""Version-4 exact-response policy runtime; separate from the active evaluator."""
import numpy as np
from exact_initial_hybrid_checkpoint_v1 import validate_model
from sampled_visible_hybrid_policy_v1 import predict as base_predict
from sampled_visible_hybrid_cpu64_v1 import VisibleHybridCpuBank64
from sampled_visible_hybrid_gpu_bank_v1 import VisibleHybridCudaBank64


def predict(queries, model, *, catalog_source, matrix_sha256, entry_mass, device):
    table = validate_model(model, queries['context_source'], catalog_source, matrix_sha256, entry_mass)
    table.validate_queries(queries['observations'])
    scores, p, coverage = base_predict(queries, model['base_model'], device)
    p, rows = table.apply(queries['observations'], p)
    return scores, p, dict(base_table_rows=coverage, exact_btn_rows=len(rows))


def probabilities(queries, model, *, catalog_source, matrix_sha256, entry_mass, device):
    _, p, coverage = predict(queries, model, catalog_source=catalog_source,
        matrix_sha256=matrix_sha256, entry_mass=entry_mass, device=device)
    return p, coverage


def prepare(documents, completed_iterations, context_source, catalog_source, matrix_sha256, entry_mass):
    documents = list(documents)
    if type(completed_iterations) is not int or completed_iterations < 1 or len(documents) != completed_iterations:
        raise ValueError('Exactly the declared number of played models required')
    tables = []
    for generation, value in enumerate(documents):
        table = validate_model(value, context_source, catalog_source, matrix_sha256, entry_mass)
        if value['generation'] != generation:
            raise ValueError('Complete ordered played model bank required')
        tables.append(table)
    return documents, tables


class ExactInitialCpuBank64:
    def __init__(self, documents, *, completed_iterations, context_source, catalog_source,
                 matrix_sha256, entry_mass, weights_by_player):
        documents, exact = prepare(documents, completed_iterations, context_source,
                                   catalog_source, matrix_sha256, entry_mass)
        self.bank = VisibleHybridCpuBank64([d['base_model'] for d in documents],
            context_source=context_source, weights_by_player=weights_by_player)
        for (_, pair), table in zip(self.bank.models, exact):
            pair[1] = table.compose(pair[1])
        self.geometry = exact[0]

    def average(self, queries, *, guard):
        self.geometry.validate_queries(queries['observations'])
        # Base averaging propagates own-history reach after the composed table
        # has replaced its exact response rows, never before the override.
        return self.bank.average(queries, guard=guard)


class ExactInitialCudaBank64:
    def __init__(self, documents, weights_by_player, *, completed_iterations,
                 context_source, catalog_source, matrix_sha256, entry_mass,
                 models_per_chunk=8, guard):
        documents, exact = prepare(documents, completed_iterations, context_source,
                                   catalog_source, matrix_sha256, entry_mass)
        self.bank = VisibleHybridCudaBank64([d['base_model'] for d in documents],
            weights_by_player, context_source=context_source,
            models_per_chunk=models_per_chunk, guard=guard)
        for pair, table in zip(self.bank.tables, exact):
            pair[1] = table.compose(pair[1])
        self.geometry = exact[0]

    def average(self, queries, *, guard):
        self.geometry.validate_queries(queries['observations'])
        return self.bank.average(queries, guard=guard)
