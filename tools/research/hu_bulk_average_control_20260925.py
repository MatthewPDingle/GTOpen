"""Exact averaged-policy equivalence on both full 78-model played banks."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',CUBLAS_WORKSPACE_CONFIG=':4096:8')
from pathlib import Path
import hashlib
import json
import sys
import time
import numpy as np
from later_average_support_v1 import OUT,read,weights
from sampled_physical_root_evaluation_v1 import sha,save
from hu_action_integrated_exact_20260925 import load_bank,bank_args
from action_integrated_policy_v1 import ActionIntegratedCudaBank64
from action_integrated_policy_bulk_v1 import ActionIntegratedCudaBankBulk64
from hu_paired_continuation_support_20260925 import launch,setup_cuda,guard_for

PREFIX='bulk-average-control-v1'


def worker(reg):
    setup_cuda(); guard=guard_for(reg); guard(); started=time.monotonic()
    source=(OUT/'bb-context-candidate.json').read_text(); args=bank_args(source); rows=[]
    for trial_index,t in enumerate(reg['trials']):
        guard();before=time.monotonic()
        models=load_bank(read(t['registration']),read(t['audit']),source,78)
        loading_seconds=time.monotonic()-before
        banks=[ActionIntegratedCudaBank64(models,weights('linear',78),completed_iterations=78,guard=guard,**args),
               ActionIntegratedCudaBankBulk64(models,weights('linear',78),completed_iterations=78,guard=guard,**args)]
        queries=read(t['query']); times=[[],[]]; digests=None
        for repeat in range(2):
            order=(0,1) if (trial_index+repeat)%2==0 else (1,0)
            for index in order:
                guard();before=time.monotonic()
                p,support=banks[index].average(queries,guard=guard)
                times[index].append(time.monotonic()-before)
                actual=[hashlib.sha256(a.tobytes()).hexdigest() for a in (p,support)]
                if digests is None:digests=actual
                assert actual==digests,'Policy probabilities or own reach changed'
        rows.append(dict(trial=t['name'],models=78,observations=len(queries['observations']),
            reference_seconds=times[0],bulk_seconds=times[1],loading_seconds=loading_seconds,
            probabilities_sha256=digests[0],support_sha256=digests[1],byte_identical=True))
        print(json.dumps(rows[-1]),flush=True)
        del banks,models,p,support
    for path,digest in reg['inputs'].items():guard();assert sha(path)==digest,path
    save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(OUT/f'{PREFIX}-registration.json'),
        trials=rows,seconds=time.monotonic()-started,production_modified=False,
        accuracy_qualified=False,scope='Full-bank CUDA equivalence at unchanged arithmetic order; two saved batches, not a population speed benchmark.'))


if __name__=='__main__':
    if sys.argv[1:]==['--worker']:worker(read(OUT/f'{PREFIX}-registration.json'))
    else:
        assert sys.argv[1:]==['--run']
        launch(Path(__file__).resolve(),PREFIX,dict(
            scope='Two complete 78-model banks, linear weights; two paired old/new repetitions on each original last-update batch.'),
            cap=10_000_000,seconds=1800)
