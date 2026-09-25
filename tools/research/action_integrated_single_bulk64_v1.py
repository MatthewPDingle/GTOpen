"""Single-model bulk inference; unchanged root and exact-initial overrides.

This candidate is deliberately separate from the frozen active experiment.
"""
from action_integrated_checkpoint_v1 import validate_model
from exact_initial_single_policy_bulk64_v1 import predict as exact_predict
from later_action_checkpoint_v1 import inner_model


def predict(queries, model, *, catalog_source, matrix_sha256, entry_mass, device):
    table = validate_model(model, queries['context_source'], catalog_source,
                           matrix_sha256, entry_mass)
    scores, p, coverage = exact_predict(queries, model['exact_model'],
        catalog_source=catalog_source, matrix_sha256=matrix_sha256,
        entry_mass=entry_mass, device=device)
    p, rows = table.apply(queries['observations'], p)
    return scores, p, dict(coverage, action_integrated_root_rows=len(rows))


def probabilities(queries, model, **kwargs):
    _, p, coverage = predict(queries, model, **kwargs)
    return p, coverage


def later_probabilities(queries, model, *, device, catalog_source,
                        matrix_sha256, entry_mass):
    args = dict(context_source=queries['context_source'],
                catalog_source=catalog_source, matrix_sha256=matrix_sha256,
                entry_mass=entry_mass)
    return probabilities(queries, inner_model(model, **args), device=device,
        catalog_source=catalog_source, matrix_sha256=matrix_sha256,
        entry_mass=entry_mass)
