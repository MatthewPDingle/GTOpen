"""Small end-to-end exact-initial CPU fixture, safe beside GPU training."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',CUDA_VISIBLE_DEVICES='-1')
from pathlib import Path
import time
import psutil
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from exact_initial_wider_inputs_v1 import admitted
from exact_initial_hybrid_policy_v1 import ExactInitialCpuBank64
from wider_root_evaluation_v2 import run
from wider_root_readback_v2 import review
from reboot_research_idle_v1 import idle

PREFIX='exact-initial-wider-cpu-control-v1'
STORE=Path('T:/GTOpen-research')/PREFIX


def main():
    started=time.monotonic()
    def guard():
        assert time.monotonic()-started<600 and idle()
        assert psutil.virtual_memory().available>20_000_000_000 and psutil.disk_usage('T:/').free>40_000_000_000
    guard();assert not STORE.exists()
    data=admitted(control=True)
    assert data['count']==2 and data['control_only']
    bank=ExactInitialCpuBank64(data['models'],completed_iterations=2,weights_by_player=data['weights'],**data['bank_args'])
    inputs=data['inputs']
    paths=[Path(__file__),*[ROOT/'tools/research'/n for n in (
        'exact_initial_wider_inputs_v1.py','exact_initial_hybrid_policy_v1.py',
        'wider_root_evaluation_v2.py','wider_root_readback_v2.py',
        'sampled_conditional_root_evaluation_v1.py','sampled_visible_hybrid_cpu64_v1.py')],
        ROOT/'target/release/examples/hu_sampled_bank_bridge.exe',
        ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe']
    inputs.update({str(p):sha(p) for p in paths})
    cfg=dict(id=PREFIX,train_seed=354041,test_seed=354042,per_class=2,test_deals=128,
        batch_size=16,minimum_training_deals=1,family_alpha=.025)
    rp=OUT/f'{PREFIX}-registration.json';assert not rp.exists()
    save(rp,dict(inputs=inputs,config=cfg,store=str(STORE),exact=data['exact'],
        checkpoint=data['checkpoint'],cache_sha256=data['cache'].sha256,
        prior_response_path=str(data['prior_response_path']),prior_response_sha256=data['prior_response_sha256'],
        maximum_seconds=600,control_only=True,gpu_used=False,production_modified=False,
        scope='Two-model fixture native transport plus scalar six-alternative audit. No active pilot models or poker-strength selection.'))
    result=run(data['context_path'],bank,data['cache'],data['exact'],cfg,STORE,guard,
        prior_response_path=data['prior_response_path'])
    audit=review(data['context_path'],STORE,cfg,data['exact'],data['cache'].sha256,guard,
        prior_response_path=data['prior_response_path'])
    assert result['complete'] and audit['passed'] and audit['intervals_reconstructed']==6
    assert result['training_deals']==338 and result['test_deals']==128
    for p,h in inputs.items():guard();assert sha(p)==h,p
    save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(rp),
        result_sha256=sha(STORE/'result.json'),independent_readback=audit,
        seconds=time.monotonic()-started,control_only=True,gpu_used=False,production_modified=False,
        accuracy_qualified=False))
    print(dict(passed=True,seconds=time.monotonic()-started,independent_readback=audit),flush=True)


if __name__=='__main__':main()
