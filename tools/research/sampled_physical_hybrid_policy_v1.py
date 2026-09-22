"""Current-generation hybrid policy, shared by training and its controls."""
from sampled_batch_model_v1 import predict
from sampled_physical_hybrid_checkpoint_v1 import validate_model
from sampled_physical_preflop_table_v1 import Table


def probabilities(queries, model, device):
    context = queries['context_source']
    validate_model(model, context)
    observations = queries['observations']
    _, result = predict(observations, model['networks'], device)
    covered = [0, 0]
    for player, document in enumerate(model['preflop_tables']):
        if document is not None:
            result, indices = Table(document, context).apply(observations, result)
            covered[player] = len(indices)
    return result, covered
