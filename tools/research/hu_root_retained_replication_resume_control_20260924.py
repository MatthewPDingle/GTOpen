"""Validate the saved next random stream and CUDA policy before recovery."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',CUBLAS_WORKSPACE_CONFIG=':4096:8')
import ast
import json
import time
from pathlib import Path
import numpy as np
import torch
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read,load_complete_cache
from preflop_allin_matrix_v1 import AllinMatrix
from root_retained_checkpoint_v1 import restore_checkpoint
from root_retained_policy_v1 import probabilities
from root_retained_training_v1 import first_action_view
from reboot_research_idle_v1 import idle


def main():
    start=time.monotonic()
    lock=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
    other=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
    assert idle() and not lock.exists() and not other.exists()
    result_path=OUT/'root-retained-replication-resume-control-v1-result.json'
    assert not result_path.exists()
    audit_path=OUT/'root-retained-replication-prefix-v1-independent-review.json'
    audit=read(audit_path)
    assert audit['passed'] and audit['completed_updates']==5 and not audit['terminal_complete']
    old=ROOT/'tools/research/hu_root_retained_replication_20260924.py'
    new=ROOT/'tools/research/hu_root_retained_replication_resume_20260924.py'
    def update_loop(path):
        tree=ast.parse(path.read_text())
        return next(n for n in ast.walk(tree) if isinstance(n,ast.For) and
            isinstance(n.target,ast.Name) and n.target.id=='iteration')
    before,after=update_loop(old),update_loop(new)
    assert after.iter.args[0].value==6 and before.iter.args[0].value==1
    after.iter.args[0].value=1
    after.body=[n for n in after.body if not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Call)
        and isinstance(n.value.func,ast.Name) and n.value.func.id=='durable_iteration')]
    assert ast.dump(before)==ast.dump(after)
    reg_path=OUT/'root-retained-replication-v1-registration.json'
    reg=read(reg_path);store=Path(reg['store'])
    cfg_path=OUT/'root-retained-replication-v1-environment.json';cfg=read(cfg_path)
    cfg_match=torch.__version__==cfg['torch_version'] and np.__version__==cfg['numpy_version']
    assert cfg_match and torch.cuda.get_device_name()==cfg['device_name']
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    cp=OUT/'bb-context-candidate.json';mp=OUT/'preflop-allin-matrix-control-v1-matrix.json'
    source=cp.read_text();catalog=Path(reg['catalog']).read_text();matrix=AllinMatrix(read(mp),source)
    args=dict(context_source=source,catalog_source=catalog,matrix_sha256=sha(mp),entry_mass=matrix.btn_mass)
    ref=read(store/'checkpoint-0005.json')
    state=restore_checkpoint(store/'objects',ref,config=cfg,**args)
    cache=load_complete_cache();inputs=dict(reg['inputs'])
    inputs.update({str(p):sha(p) for p in [Path(__file__),old,new,reg_path,cfg_path,audit_path,
        ROOT/'tools/research/root_retained_replication_resume_support_v1.py',store/'checkpoint-0005.json']})
    with lock.open('x') as f:f.write(str(os.getpid()))
    try:
        maximum=0.;observations=0
        for chunk in range(8):
            assert idle() and time.monotonic()-start<600
            assert torch.cuda.mem_get_info()[0]>=3_000_000_000
            part=store/'iteration-0006'/f'batch-{chunk:02d}'
            bp=part/'batch.json';expected=read(bp)
            actual=cache.batch(dict(format=2,batch_id=f'root-retained-replication-v1-iteration-6-batch-{chunk}',
                query_limit=cfg['query_limit'],seed=int(state['action_rng'].integers(0,2**63)),
                deals=state['sampler'].sample(64)['deals']))
            assert actual==expected,chunk
            inputs[str(bp)]=sha(bp)
            if chunk==0:
                qp,pp=part/'queries.json',part/'policies.json'
                q=first_action_view(read(qp),json.loads(source)['nodes'][0]['children'][3]+1)
                p,_=probabilities(q,state['next_model_document'],device='cuda',catalog_source=catalog,
                    matrix_sha256=sha(mp),entry_mass=matrix.btn_mass)
                expected=np.asarray([r['probabilities'] for r in read(pp)['policies']])
                maximum=float(np.max(abs(p-expected)));assert maximum<1e-12
                observations=len(p);inputs.update({str(qp):sha(qp),str(pp):sha(pp)})
        for p,h in inputs.items():assert sha(ROOT/p)==h,p
        save(result_path,dict(passed=True,checkpoint=ref,completed_iterations=5,
            next_action_stream_verified=True,replayed_next_deals=512,replayed_next_action_seeds=8,
            observations=observations,maximum_policy_error=maximum,update_loop_ast_unchanged=True,
            inputs=inputs,seconds=time.monotonic()-start,production_modified=False,
            scope='Restart continuity only: no refit, no new candidate or accuracy evidence.'))
        print(json.dumps(dict(passed=True,maximum_policy_error=maximum,replayed_deals=512,observations=observations)))
    finally:
        assert lock.read_text().strip()==str(os.getpid());lock.unlink()


if __name__=='__main__':main()
