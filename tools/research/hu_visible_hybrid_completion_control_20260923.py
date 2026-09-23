"""Check bounded completion preserves the stopped trajectory and evaluation."""
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

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
TD = ROOT/'tools/research'
OLD = 'sampled-visible-hybrid-resume-pilot-v1'


def iteration_loop(text):
    worker = next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == 'worker')
    return next(n for n in worker.body if isinstance(n, ast.For) and isinstance(n.target, ast.Name) and n.target.id == 'iteration')


def main():
    assert idle()
    assert not (OUT/'sampled-visible-hybrid-completion-control-v1-result.json').exists()
    os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
    import torch
    torch.set_num_threads(2); torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False
    original = TD/'hu_visible_hybrid_resume_pilot_20260923.py'
    completion = TD/'hu_visible_hybrid_completion_pilot_20260923.py'
    assert ast.dump(iteration_loop(original.read_text())) == ast.dump(iteration_loop(completion.read_text()))
    unchanged = []
    paths = [Path(__file__), original, completion, TD/'visible_hybrid_completion_support_v1.py']
    for part in ('evaluation', 'evaluation_review', 'btn_evaluation', 'btn_review', 'comparison'):
        before = TD/f'hu_visible_hybrid_resume_{part}_20260923.py'
        after = TD/f'hu_visible_hybrid_completion_{part}_20260923.py'
        expected = before.read_text().replace('sampled-visible-hybrid-resume', 'sampled-visible-hybrid-completion').replace('hu_visible_hybrid_resume_', 'hu_visible_hybrid_completion_')
        assert after.read_text() == expected, part
        unchanged.append(part); paths.extend((before, after))
    regpath = OUT/f'{OLD}-registration.json'; reg = json.loads(regpath.read_text())
    for p, h in reg['inputs'].items():
        assert sha(p) == h, p
    statpath = OUT/f'{OLD}-status.json'; stat = json.loads(statpath.read_text())
    assert stat['state'] == 'stopped' and stat['error'] == 'Execution deadline'
    store = Path(reg['store']); latest = json.loads((store/'latest.json').read_text())
    completed = latest['completed_iterations']; assert 72 <= completed < 78
    reviewpath = OUT/f'{OLD}-prefix-{completed:04d}-review.json'; review = json.loads(reviewpath.read_text())
    assert review['passed'] and not review['terminal_complete'] and review['checkpoint'] == latest['checkpoint']
    assert review['source_registration_sha256'] == sha(regpath)
    cfg = latest['config']
    assert cfg['torch_version'] == torch.__version__ and cfg['numpy_version'] == np.__version__ and cfg['device_name'] == torch.cuda.get_device_name()
    context = (OUT/'bb-context-candidate.json').read_text()
    restored = restore_checkpoint(store/'checkpoint-objects', latest['checkpoint'], context_source=context, config=cfg)
    assert restored['completed_iterations'] == completed
    cache = AllinCache.from_review(OUT/'sampled-physical-allin-training-cache-v1-independent-review.json')
    paths.extend((regpath, statpath, reviewpath, store/'latest.json', TD/'reboot_research_idle_v1.py', OUT/'VISIBLE-HYBRID-TIME-CAP-CONTINGENCY.md'))
    evidence = {str(p): sha(p) for p in paths}
    maximum_error = 0.; observations = 0; batches = 0
    for chunk in range(cfg['subbatches_per_iteration']):
        part = store/f'iteration-{completed+1:04d}'/f'batch-{chunk:02d}'
        path = part/'batch.json'
        if not path.exists():
            break
        assert idle()
        expected_batch = json.loads(path.read_text())
        batch = dict(format=2, batch_id=f'sampled-visible-hybrid-trial-pilot-v1-iteration-{completed+1}-batch-{chunk}',
            query_limit=cfg['query_limit'], seed=int(restored['action_rng'].integers(0, 2**63)),
            deals=restored['sampler'].sample(cfg['deals_per_subbatch'])['deals'])
        assert cache.batch(batch) == expected_batch, chunk
        evidence[str(path)] = sha(path); batches += 1
        if chunk == 0:
            qpath, ppath = part/'queries.json', part/'policies.json'
            queries = json.loads(qpath.read_text()); profile = json.loads(ppath.read_text())
            actual, _ = probabilities(queries, restored['next_model_document'], 'cuda')
            expected_policy = np.asarray([p['probabilities'] for p in profile['policies']])
            maximum_error = float(np.max(abs(actual-expected_policy))); assert maximum_error < 1e-12
            observations = len(actual)
            evidence.update({str(p): sha(p) for p in (qpath, ppath)})
    assert batches > 0 and observations > 0
    for p, h in evidence.items():
        assert sha(p) == h, p
    result = dict(passed=True, checkpoint=latest['checkpoint'], completed_iterations=completed,
        replayed_next_deals=batches*cfg['deals_per_subbatch'], replayed_next_action_seeds=batches,
        policy_observations=observations, maximum_policy_error=maximum_error,
        training_loop_ast_unchanged=True, evaluation_scripts_unchanged_except_paths=unchanged,
        inputs=evidence, original_cap_passed=False, production_modified=False,
        scope='Exact recovery of all saved interrupted-next-update chance/action draws and first-batch CUDA probabilities; unchanged training loop and original evaluation design. No fitting or strategic evaluation.')
    save(OUT/'sampled-visible-hybrid-completion-control-v1-result.json', result)
    print(json.dumps({k:v for k,v in result.items() if k != 'inputs'}))


if __name__ == '__main__':
    main()
