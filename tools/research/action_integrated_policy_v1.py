"""Action-integrated root override for single inference and CPU/CUDA own-reach averaging."""
from action_integrated_checkpoint_v1 import validate_model
from exact_initial_single_policy64_v1 import predict as exact_predict
from exact_initial_hybrid_policy_v1 import ExactInitialCpuBank64, ExactInitialCudaBank64


def predict(queries,model,*,catalog_source,matrix_sha256,entry_mass,device):
    table = validate_model(model,queries['context_source'],catalog_source,matrix_sha256,entry_mass)
    scores,p,coverage = exact_predict(queries,model['exact_model'],catalog_source=catalog_source,
        matrix_sha256=matrix_sha256,entry_mass=entry_mass,device=device)
    p,rows = table.apply(queries['observations'],p)
    return scores,p,dict(coverage,action_integrated_root_rows=len(rows))


def probabilities(queries,model,**kwargs):
    _,p,coverage = predict(queries,model,**kwargs)
    return p,coverage


def prepare(documents,completed_iterations,context_source,catalog_source,matrix_sha256,entry_mass):
    documents = list(documents)
    if type(completed_iterations) is not int or completed_iterations < 1 or len(documents) != completed_iterations:
        raise ValueError('Complete action-integrated played bank required')
    tables=[]
    for g,d in enumerate(documents):
        tables.append(validate_model(d,context_source,catalog_source,matrix_sha256,entry_mass))
        if d['generation'] != g:
            raise ValueError('Action-integrated played generation order changed')
    return documents,tables


class ActionIntegratedCpuBank64:
    def __init__(self,documents,*,completed_iterations,context_source,catalog_source,
                 matrix_sha256,entry_mass,weights_by_player):
        docs,root = prepare(documents,completed_iterations,context_source,catalog_source,matrix_sha256,entry_mass)
        self.bank = ExactInitialCpuBank64([d['exact_model'] for d in docs],completed_iterations=completed_iterations,
            context_source=context_source,catalog_source=catalog_source,matrix_sha256=matrix_sha256,
            entry_mass=entry_mass,weights_by_player=weights_by_player)
        for (_,pair),table in zip(self.bank.bank.models,root):
            pair[0] = table.compose(pair[0])
        self.geometry = root[0]

    def average(self,queries,*,guard):
        self.geometry.validate_queries(queries['observations'])
        return self.bank.average(queries,guard=guard)


class ActionIntegratedCudaBank64:
    def __init__(self,documents,weights_by_player,*,completed_iterations,context_source,
                 catalog_source,matrix_sha256,entry_mass,models_per_chunk=8,guard):
        docs,root = prepare(documents,completed_iterations,context_source,catalog_source,matrix_sha256,entry_mass)
        self.bank = ExactInitialCudaBank64([d['exact_model'] for d in docs],weights_by_player,
            completed_iterations=completed_iterations,context_source=context_source,catalog_source=catalog_source,
            matrix_sha256=matrix_sha256,entry_mass=entry_mass,models_per_chunk=models_per_chunk,guard=guard)
        for pair,table in zip(self.bank.bank.tables,root):
            pair[0] = table.compose(pair[0])
        self.geometry = root[0]

    def average(self,queries,*,guard):
        self.geometry.validate_queries(queries['observations'])
        return self.bank.average(queries,guard=guard)
