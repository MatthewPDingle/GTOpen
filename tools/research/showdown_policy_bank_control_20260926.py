"""Complete played-bank inference check on an existing native history query set."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',CUBLAS_WORKSPACE_CONFIG=':4096:8')
import json
from pathlib import Path
import time
import numpy as np
from hu_paired_continuation_support_20260925 import setup_cuda, LOCK, OTHER
from reboot_research_idle_v1 import idle
from hu_action_integrated_exact_20260925 import bank_args
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read
from showdown_root_checkpoint_v1 import model_document,restore_checkpoint
from showdown_root_policy_v1 import ShowdownRootCpuBank64,ShowdownRootCudaBank64


def main():
    assert idle() and not LOCK.exists() and not OTHER.exists()
    setup_cuda();started=time.monotonic()
    def guard():
        assert idle() and not LOCK.exists() and not OTHER.exists() and time.monotonic()-started<180
    prefix='showdown-training-integration-control-v1'
    path=OUT/f'{prefix}-result.json';result=read(path)
    review=read(OUT/f'{prefix}-independent-review.json')
    assert result['passed'] and review['passed'] and review['source_result_sha256']==sha(path)
    objects=Path(result['store'])/'objects';args=bank_args((OUT/'bb-context-candidate.json').read_text())
    state=restore_checkpoint(objects,result['final_checkpoint'],config=result['config'],**args)
    docs=[model_document(objects,ref,**args) for ref in state['played_bank']]
    assert len(docs)==2 and [d['generation'] for d in docs]==[0,1]
    assert state['next_model']['generation']==2
    source_path=OUT/'later-action-joint-control-v1-result.json';source=read(source_path)
    query_path=Path(source['store'])/'average-queries.json'
    assert source['passed'] and sha(query_path)==source['artifacts'][str(query_path)]
    queries=read(query_path);weights=np.tile(np.arange(1,3,dtype=float),(2,1))
    guard()
    cpu=ShowdownRootCpuBank64(docs,completed_iterations=2,weights_by_player=weights,**args)
    gpu=ShowdownRootCudaBank64(docs,weights,completed_iterations=2,models_per_chunk=2,guard=guard,**args)
    a,ra=cpu.average(queries,guard=guard);b,rb=gpu.average(queries,guard=guard)
    error=float(np.max(abs(a-b)));reach_error=float(np.max(abs(ra-rb)))
    assert error<1e-10 and reach_error<1e-10
    assert np.isfinite(a).all() and np.isfinite(ra).all()
    rejections=[]
    for name,bad in [('reversed bank',docs[::-1]),('unplayed final model',docs+[model_document(objects,state['next_model'],**args)])]:
        try:ShowdownRootCpuBank64(bad,completed_iterations=2,weights_by_player=weights,**args)
        except ValueError:rejections.append(name)
        else:raise AssertionError('Accepted '+name)
    sources=[path,source_path,query_path,Path(__file__).resolve(),ROOT/'tools/research/showdown_root_policy_v1.py']
    output=dict(passed=True,complete_played_generations=[0,1],excluded_unplayed_generation=2,
        observations=len(queries['observations']),maximum_policy_error=error,maximum_reach_error=reach_error,
        rejections=rejections,source_hashes={str(p):sha(p) for p in sources},seconds=time.monotonic()-started,
        production_modified=False,accuracy_qualified=False,
        scope='CPU/CUDA equivalence and complete played-bank selection; not independent proof of averaging theory or poker strength.')
    dest=OUT/'showdown-policy-bank-control-v1-result.json';assert not dest.exists();save(dest,output)
    print(json.dumps(output))


if __name__=='__main__':main()
