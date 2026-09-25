"""Compare reference and captured full fits on both original final reservoirs."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',CUBLAS_WORKSPACE_CONFIG=':4096:8')
import json
from pathlib import Path
import sys
import time
import numpy as np
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import sha,save
from hu_action_integrated_exact_20260925 import bank_args
from action_integrated_checkpoint_v1 import restore_checkpoint
from sampled_visible_hybrid_checkpoint_v1 import read_object
from sampled_visible_hybrid_fit_bulk_v1 import fit as reference
from sampled_visible_gradient_graph_fit_v1 import fit as candidate
from hu_paired_continuation_support_20260925 import setup_cuda,guard_for,launch

PREFIX='cuda-gradient-graph-control-v1'


def worker(reg):
    import torch
    setup_cuda();guard=guard_for(reg);guard();started=time.monotonic()
    t=reg['trials'][1];trial=read(t['result']);cfg=trial['config']
    assert torch.__version__==cfg['torch_version'] and np.__version__==cfg['numpy_version']
    assert torch.cuda.get_device_name()==cfg['device_name']
    objects=Path(trial['store'])/'objects';source=(OUT/'bb-context-candidate.json').read_text()
    state=restore_checkpoint(objects,trial['final_checkpoint'],config=cfg,**bank_args(source))
    metric=read(Path(trial['store'])/'iteration-0078/metrics.json')
    expected=json.loads(read_object(objects,metric['next_model']))['exact_model']['base_model']['networks']
    rows=[]
    for player,reservoir in enumerate(state['reservoirs']):
        records={}
        # Alternate order by player; this is one pair each, not a broad timing claim.
        order=[('reference',reference),('graph',candidate)]
        if player==1:order.reverse()
        for label,fn in order:
            guard();torch.cuda.reset_peak_memory_stats();before=time.monotonic()
            net,metrics=fn(reservoir,seed=cfg['fit_seed_base']+78*200003+player,
                steps=cfg['fit_steps'],device='cuda',chunk_size=cfg['chunk_size'],
                guard=guard,learning_rate=cfg['learning_rate'])
            elapsed=time.monotonic()-before
            assert net==expected[player],f'{label} player {player}: network differs from frozen full fit'
            excluded={'scope','setup_seconds','optimizer_seconds','graph_capture_seconds'}
            assert {k:v for k,v in metrics.items() if k not in excluded}=={k:v for k,v in metric['fits'][player].items() if k not in excluded}
            records[label]=dict(metrics=metrics,wall_seconds=elapsed,weights_identical=True,
                nontiming_metrics_identical=True,peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                peak_reserved_bytes=torch.cuda.max_memory_reserved())
            print(json.dumps(dict(player=player,method=label,seconds=elapsed,weights_identical=True)),flush=True)
        rows.append(dict(player=player,methods=records))
    for path,digest in reg['inputs'].items():guard();assert sha(path)==digest,path
    save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(OUT/f'{PREFIX}-registration.json'),
        players=rows,seconds=time.monotonic()-started,production_modified=False,accuracy_qualified=False,
        scope='One paired full reference/graph fit for each saved final reservoir, both compared exactly to historical weights; not a fresh learning trial or whole-training speed benchmark.'))


if __name__=='__main__':
    if sys.argv[1:]==['--worker']:worker(read(OUT/f'{PREFIX}-registration.json'))
    else:
        assert sys.argv[1:]==['--run']
        assert read(OUT/'paired-continuation-v1-status.json')['state']=='complete'
        assert read(OUT/'paired-continuation-v1-independent-review.json')['passed']
        launch(Path(__file__).resolve(),PREFIX,dict(
            extra_inputs=[str(OUT/'paired-continuation-v1-status.json'),str(OUT/'paired-continuation-v1-independent-review.json')],
            scope='Fixed two-player final-step exact replay. Graph captures gradients only, unchanged Adam; no adoption if any weight or nontiming fit metric differs.'),
            cap=10_000_000,seconds=1800)
