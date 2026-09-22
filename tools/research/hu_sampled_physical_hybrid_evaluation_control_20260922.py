"""CPU-only preflight of the hybrid evaluation adapter and unchanged test loop."""
import ast
import json
import math
from pathlib import Path
import time
import numpy as np
import psutil
from loopback_research_validation import idle
from sampled_batch_model_v1 import predict
from sampled_physical_hybrid_evaluation_v1 import HybridCpuBank
from sampled_physical_root_evaluation_v1 import ROOT, sha, save

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'


def main():
    import torch
    torch.set_num_threads(2)
    started = time.monotonic()
    def guard():
        assert idle() and time.monotonic()-started < 120
        assert psutil.virtual_memory().available >= 20_000_000_000
    guard()
    regpath = OUT/'sampled-physical-hybrid-gpu-control-v1-registration.json'
    reg = json.loads(regpath.read_text())
    for p,h in reg['inputs'].items(): assert sha(p) == h,p
    queries = json.loads(Path(reg['query_fixture']).read_text())
    models = json.loads(Path(reg['models']).read_text())
    source = queries['context_source']; obs = queries['observations']
    bank = HybridCpuBank(models,context_source=source)
    actual,support = bank.average(queries,guard=guard)
    policies = []
    for model in models:
        guard()
        _,p = predict(obs,model['networks'],'cpu')
        tables = [None if t is None else {(int(r['hi']),int(r['lo'])):r for r in t['rows']}
                  for t in model['preflop_tables']]
        for i,o in enumerate(obs):
            table = tables[o['actor']]
            if o['phase'] == 0 and table is not None and (int(o['hi']),int(o['lo'])) in table:
                scores = np.asarray(table[int(o['hi']),int(o['lo'])]['mean_regret'])
                positive = np.maximum(scores,0.)
                if positive.sum() > 0: p[i] = positive/positive.sum()
                else:
                    p[i] = 0.; p[i,int(np.argmax(scores[:o['n']]))] = 1.
        policies.append(p)
    expected = np.zeros_like(actual); expected_support = []
    for i,o in enumerate(obs):
        weights = [math.prod(p[ancestor,action] for ancestor,action,n in o['own_history'])
                   for p in policies]
        total = math.fsum(weights); expected_support.append(total)
        if total:
            for a in range(4): expected[i,a] = math.fsum(w*p[i,a] for w,p in zip(weights,policies))/total
        else: expected[i,:o['n']] = 1/o['n']
    error = float(np.max(np.abs(expected-actual)))
    support_error = float(np.max(np.abs(np.asarray(expected_support)-support)))
    assert error < 1e-12 and support_error < 1e-12
    rejected = 0
    for bad in ([],models[::-1],[dict(models[0],format=1)],models[1:]):
        try: HybridCpuBank(bad,context_source=source)
        except ValueError: rejected += 1
    assert rejected == 4
    original = (ROOT/'tools/research/sampled_physical_root_evaluation_cuda_v1.py').read_text()
    hybrid = (ROOT/'tools/research/sampled_physical_hybrid_evaluation_v1.py').read_text()
    original_run = original[original.index('def run(registration, folder, guard):'):]
    expected_run = original_run.replace(
        "verify_bank(objects, checkpoint['completed_iterations'], checkpoint['played_bank'], checkpoint['next_model'])",
        "verify_bank(objects, checkpoint['completed_iterations'], checkpoint['played_bank'], checkpoint['next_model'], context_source=source)")
    expected_run = expected_run.replace(
        "bank = CudaBank((model_document(objects, ref)['networks'] for ref in played),\n                    [[1.] * len(played)] * 2, models_per_chunk=8, guard=guard)",
        "bank = HybridCudaBank((model_document(objects, ref, context_source=source) for ref in played),\n                    [[1.] * len(played)] * 2, context_source=source, models_per_chunk=8, guard=guard)")
    hybrid_run = hybrid[hybrid.index('def run(registration, folder, guard):'):]
    assert ast.dump(ast.parse(expected_run)) == ast.dump(ast.parse(hybrid_run))
    paths = [Path(__file__),regpath,Path(reg['query_fixture']),Path(reg['models']),
             *[ROOT/'tools/research'/n for n in ('sampled_physical_hybrid_evaluation_v1.py',
               'sampled_physical_root_evaluation_cuda_v1.py','sampled_physical_preflop_table_v1.py',
               'sampled_physical_hybrid_checkpoint_v1.py','sampled_batch_model_v1.py')]]
    save(OUT/'sampled-physical-hybrid-evaluation-v1-adapter-control.json',dict(
        passed=True,inputs={str(p):sha(p) for p in paths},observations=len(obs),
        maximum_policy_error=error,maximum_support_error=support_error,
        invalid_banks_rejected=rejected,protocol_loop_unchanged_except_explicit_hybrid_bank=True,
        seconds=time.monotonic()-started,production_modified=False,
        scope='Existing synthetic fixture, equal-weight CPU adapter compared with scalar own-reach reconstruction. AST equality verifies the fixed evaluation protocol remains unchanged except explicit hybrid bank loading. No GPU execution, new chance stream or strength result.'))
    print(json.dumps(dict(passed=True,observations=len(obs),policy_error=error,support_error=support_error)))


if __name__ == '__main__': main()
