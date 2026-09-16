"""Run the frozen N15 helper with N06's original numerical threading setup."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import sys
from pathlib import Path
from threadpoolctl import threadpool_info
import continuation_shrunk_residual as candidate


def run():
    pools=[{key:row.get(key) for key in ['user_api','internal_api','num_threads','version','prefix']}
        for row in threadpool_info()]
    assert all(row['num_threads']==1 for row in pools if row['user_api']=='blas')
    assert candidate.network.torch.get_num_threads()==2
    candidate.study.freeze(candidate.OUT/'training-runtime.json',dict(python=sys.version,
        torch=candidate.network.torch.__version__,thread_pools=pools,
        launcher_sha256=candidate.study.pilot.sha(Path(__file__)),production_enabled=False,
        note='Matches original N06: BLAS one thread, Torch two. Initial direct launch imported NumPy before setting BLAS threads and was rejected by exact control reproduction; no score or candidate from that attempt was accepted.'))
    candidate.screen()


if __name__=='__main__':run()
