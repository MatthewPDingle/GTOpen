"""Retained-data transport equivalence; no native executable or fit is run."""
import os
os.environ.update(PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import ast
import json
from pathlib import Path
import shutil
import time
from types import SimpleNamespace
import numpy as np
import psutil
import stack_context_parallel_continuation_v2 as run
from stack_context_river_transport_resume_v1 import generate,retained_write
from stack_context_current_policy_v1 import CurrentPolicy
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS
from weighted_deal_binding_v1 import DealWeightGeneration
from stack_context_cycle_archive_v1 import read,sha
from owned_columnar_evaluation_archive_v1 import durable,encoded

legacy=run.legacy;NAME='stack-context-river-transport-resume-check-v1'
ROOT=Path('S:/GTOpen-research')/NAME


def scientific_loop(path):
    module=ast.parse(path.read_text(encoding='utf-8'))
    fn=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='generate')
    loop=next(n for n in fn.body if isinstance(n,ast.For) and ast.unparse(n.target)=='offset')
    # Only policy-array file transport differs inside the original maths loop.
    loop.body=[n for n in loop.body if not (isinstance(n,ast.With) or
        isinstance(n,ast.If) and ast.unparse(n.test)=='pp.exists()')]
    return ast.dump(loop,include_attributes=False)


def main():
    began=time.monotonic();psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    run.torch.set_num_threads(1)
    original=Path(__file__).with_name('stack_context_river_transport_v1.py')
    candidate=Path(__file__).with_name('stack_context_river_transport_resume_v1.py')
    assert scientific_loop(original)==scientific_loop(candidate)
    assert not ROOT.exists();ROOT.mkdir()
    durable(ROOT/'archive-owner.json',encoded(dict(format=1,token=NAME,purpose='new-research-scratch-v1')))
    spec=read(legacy.REG);legacy.verify(spec['inputs'])
    audit_path=legacy.OUT/'stack-context-parallel-interruption-audit-v1-result.json';audit=read(audit_path)
    inputs={str(p):sha(p) for p in (Path(__file__),original,candidate,legacy.REG,audit_path)}
    durable(legacy.OUT/(NAME+'-attempt.json'),encoded(dict(unix=time.time(),inputs=inputs,
        retained_data_only=True,native_executables_invoked=False,new_fits=False,maximum_seconds=1200)))
    cases=[]
    for arm in ('A-baseline','B-relative'):
        rt=run.runtime_for(arm,spec,read(legacy.OUT/'stack-context-population-v1-result.json'))
        cfg=spec['arms'][arm]['config'];key=rt['registry'].fit_contexts[0];source=rt['registry'].source(key)
        raw=Path(audit['arms'][arm]['raw']);metric=read(raw/'metrics.json');used=metric['used_model']
        model_source=legacy.pipeline.storage.read_object(legacy.STORE/arm/'objects',used).decode()
        engine=CurrentPolicy(json.loads(model_source),rt['registry'],context_sha256=key,resources=rt['resources'])
        weights=PhysicalDeals(source,mode='full_deck',seed=0).weights
        entry=[{tuple(map(int,p)):float(w) for p,w in zip(PAIRS,row)} for row in weights]
        batch=raw/key/'batch-000';saved=batch/'conditional'
        expected={r['path']:r['sha256'] for r in audit['files']}
        for p in saved.iterdir():assert sha(p)==expected[str(p)]
        args=dict(queries=read(batch/'queries.json'),updates=read(batch/'updates.json'),
            policies=read(batch/'policies.json'),trace=read(batch/'action-trace.json'),
            generation=DealWeightGeneration(read(raw/key/'source-generation.json'),source),start=0,
            iteration=metric['completed_cycles'],policy_id=used['sha256'],case_id=read(batch/'batch.json')['batch_id'],
            engine=engine,entry=entry,executable=legacy.ROOT/'target/release/examples/hu_river_two_stage_stream_v1.exe',
            context_path=rt['inputs'][key]['context_path'],guard=lambda:None)
        original_overlay,original_evidence=read(saved/'overlay.json'),read(saved/'evidence.json')
        # Read-only recomputation of complete target math, reusing all native bytes.
        overlay,evidence=generate(**args,folder=saved,expected=expected,
            write=lambda p,v:retained_write(p,v,expected=expected,allow_missing=False))
        assert overlay==original_overlay and evidence==original_evidence
        for p in saved.iterdir():assert sha(p)==expected[str(p)]
        # Model interruption after a complete chunk plus only the next immutable
        # request. Missing outputs are supplied by their retained native bytes,
        # never an executable or fresh scientific target calculation.
        dest=ROOT/arm;dest.mkdir();retained={}
        for p in saved.iterdir():
            if p.name.startswith('chunk-000') or p.name=='chunk-001-history-request.json':
                target=dest/p.name;shutil.copyfile(p,target);retained[str(target)]=sha(target)
        outputs={p.read_bytes():(p.with_name(p.name.replace('-request.json','-native.json'))).read_bytes()
            for p in saved.glob('*-request.json')}
        calls=[]
        def cached_native(request):
            assert request in outputs,'Attempted a different native request'
            calls.append(__import__('hashlib').sha256(request).hexdigest())
            return SimpleNamespace(stdout=outputs[request],stderr=b'',returncode=0)
        overlay,evidence=generate(**args,folder=dest,expected=retained,allow_missing=True,native_runner=cached_native,
            write=lambda p,v:retained_write(p,v,expected=retained,allow_missing=True))
        assert overlay==original_overlay and evidence==original_evidence
        assert all(sha(p)==h for p,h in retained.items())
        assert all((dest/p.name).read_bytes()==p.read_bytes() for p in saved.iterdir())
        cases.append(dict(arm=arm,complete_readback_equal=True,interrupted_transport_bytes_equal=True,
            deterministic_requests_reused=len(calls),native_executables_invoked=0))
        print(json.dumps(cases[-1]),flush=True)
    for p,h in inputs.items():assert sha(p)==h
    assert not run.torch.cuda.is_initialized()
    value=dict(passed=True,complete=True,seconds=time.monotonic()-began,inputs=inputs,cases=cases,
        target_math_ast_unchanged=True,new_native_calls=0,new_target_draws=0,new_fits=0,
        partial_cycle_runner_qualified=False)
    durable(legacy.OUT/(NAME+'-result.json'),encoded(value));print(json.dumps(value),flush=True)


if __name__=='__main__':main()
