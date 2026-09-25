"""Explicit inference adapter for version-7 postflop-target models."""
from later_action_checkpoint_v1 import inner_model
from action_integrated_policy_v1 import probabilities as parent_probabilities


def probabilities(queries,model,*,device,catalog_source,matrix_sha256,entry_mass):
    args=dict(context_source=queries['context_source'],catalog_source=catalog_source,
        matrix_sha256=matrix_sha256,entry_mass=entry_mass)
    return parent_probabilities(queries,inner_model(model,**args),device=device,
        catalog_source=catalog_source,matrix_sha256=matrix_sha256,entry_mass=entry_mass)
