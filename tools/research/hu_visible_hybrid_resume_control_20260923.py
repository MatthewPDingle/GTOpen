"""Resume trajectory and unchanged-loop checks; no training or strategy selection."""
import ast
import json
import os
from pathlib import Path
import numpy as np
from reboot_research_idle_v1 import idle
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from sampled_visible_hybrid_checkpoint_v1 import restore_checkpoint
from sampled_visible_hybrid_policy_v1 import probabilities
from sampled_allin_protocol_v3 import AllinCache

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
TD=ROOT/'tools/research'
OLD='sampled-visible-hybrid-trial-pilot-v1'


def iteration_loop(text):
    worker=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='worker')
    return next(n for n in worker.body if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='iteration')


def main():
    assert idle()
    os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
    import torch
    torch.set_num_threads(2); torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    original=TD/'hu_visible_hybrid_trial_pilot_20260923.py'
    resumed=TD/'hu_visible_hybrid_resume_pilot_20260923.py'
    normalized=resumed.read_text().replace('range(start_iteration+1,config','range(1,config').replace('{TRAJECTORY_PREFIX}','{PREFIX}')
    assert ast.dump(iteration_loop(original.read_text()))==ast.dump(iteration_loop(normalized))
    unchanged=[]
    for part in ('evaluation','evaluation_review','btn_evaluation','btn_review','comparison'):
        before=TD/f'hu_visible_hybrid_trial_{part}_20260923.py'
        after=TD/f'hu_visible_hybrid_resume_{part}_20260923.py'
        expected=before.read_text().replace('sampled-visible-hybrid-trial','sampled-visible-hybrid-resume').replace('hu_visible_hybrid_trial_','hu_visible_hybrid_resume_').replace('from loopback_research_validation import idle','from reboot_research_idle_v1 import idle')
        assert after.read_text()==expected,part
        unchanged.append(part)
    regpath=OUT/f'{OLD}-registration.json';reg=json.loads(regpath.read_text())
    for p,h in reg['inputs'].items():assert sha(p)==h,p
    store=Path(reg['store']);latest=json.loads((store/'latest.json').read_text())
    cfg=latest['config']
    assert cfg['torch_version']==torch.__version__ and cfg['numpy_version']==np.__version__ and cfg['device_name']==torch.cuda.get_device_name()
    context=(OUT/'bb-context-candidate.json').read_text()
    restored=restore_checkpoint(store/'checkpoint-objects',latest['checkpoint'],context_source=context,config=cfg)
    assert restored['completed_iterations']==48
    cache=AllinCache.from_review(OUT/'sampled-physical-allin-training-cache-v1-independent-review.json')
    evidence={str(p):sha(p) for p in [Path(__file__),original,resumed,regpath,store/'latest.json',TD/'reboot_research_idle_v1.py',TD/'visible_hybrid_resume_support_v1.py']}
    max_error=0.;observations=0
    for chunk in range(8):
        assert idle()
        part=store/'iteration-0049'/f'batch-{chunk:02d}'
        expected=json.loads((part/'batch.json').read_text())
        batch=dict(format=2,batch_id=f'{OLD}-iteration-49-batch-{chunk}',query_limit=cfg['query_limit'],
            seed=int(restored['action_rng'].integers(0,2**63)),deals=restored['sampler'].sample(cfg['deals_per_subbatch'])['deals'])
        assert cache.batch(batch)==expected,chunk
        evidence[str(part/'batch.json')]=sha(part/'batch.json')
        if chunk==0:
            qpath=part/'queries.json';ppath=part/'policies.json'
            queries=json.loads(qpath.read_text());expected_policy=json.loads(ppath.read_text())
            actual,covered=probabilities(queries,restored['next_model_document'],'cuda')
            wanted=np.asarray([p['probabilities'] for p in expected_policy['policies']])
            max_error=float(np.max(np.abs(actual-wanted)));assert max_error<1e-12
            observations=len(wanted);evidence.update({str(p):sha(p) for p in [qpath,ppath]})
    for p,h in evidence.items():assert sha(p)==h,p
    result=dict(passed=True,checkpoint=latest['checkpoint'],completed_iterations=48,
        replayed_next_deals=512,replayed_next_action_seeds=8,policy_observations=observations,
        maximum_policy_error=max_error,training_loop_ast_unchanged=True,
        evaluation_scripts_unchanged_except_paths_and_empty_session_guard=unchanged,
        inputs=evidence,production_modified=False,
        scope='Reboot continuation preserves original next 512 deals/action seeds and saved first-batch CUDA probabilities. No neural fitting, new training, or quality evaluation.')
    save(OUT/'sampled-visible-hybrid-resume-control-v1-result.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='inputs'}))


if __name__=='__main__':main()
