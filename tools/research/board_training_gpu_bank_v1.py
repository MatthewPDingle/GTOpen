"""Board-root bank candidate. CUDA equivalence qualification is still required."""
from board_training_bank_layout_v1 import prepare_layout,validate_queries
from sampled_visible_hybrid_gpu_bank_shared_v1 import VisibleHybridCudaBank64,prepare_cuda_queries


class BoardRootCudaBank64(VisibleHybridCudaBank64):
    def __init__(self,documents,weights_by_player,*,completed_iterations,context_source,
                 catalog_source,matrix_sha256,entry_mass,root_config,models_per_chunk=8,guard):
        import torch
        if type(models_per_chunk) is not int or models_per_chunk<1:raise ValueError('Positive model chunk required')
        if not torch.cuda.is_available() or torch.backends.cuda.matmul.allow_tf32 or torch.backends.cudnn.allow_tf32:
            raise ValueError('CUDA with explicitly disabled TF32 required')
        layout=prepare_layout(documents,weights_by_player,completed_iterations=completed_iterations,
            context_source=context_source,catalog_source=catalog_source,matrix_sha256=matrix_sha256,
            entry_mass=entry_mass,root_config=root_config,guard=guard)
        self.parameters={name:torch.as_tensor(value,device='cuda') for name,value in layout['parameters'].items()}
        self.weights=torch.as_tensor(layout['weights'],device='cuda')
        self.tables=layout['tables'];self.context_source=context_source
        self.exact_geometry=layout['exact_geometry'];self.count=layout['count'];self.chunk=models_per_chunk

    def average(self,queries,*,guard):
        return self.average_prepared(prepare_cuda_queries(queries,guard=guard),guard=guard)

    def average_prepared(self,prepared,*,guard):
        validate_queries(dict(context_source=self.context_source,exact_geometry=self.exact_geometry),prepared.queries)
        return super().average_prepared(prepared,guard=guard)
