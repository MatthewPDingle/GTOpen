"""Reuse frozen policy-transfer checks without modifying their implementation."""
import importlib.util
import sys
from types import SimpleNamespace
import continuation_policy_transfer as original

study=original.study
OUT=original.BASE/'policy-transfer-optimized-20260916'


def selection(name):
    assert name in ['N16','N17','N20']
    model_dir=original.BASE/'shrunk-residual-20260916'
    gpu=original.BASE/({'N16':'shrunk-mixed-gpu-20260916','N17':'pair-reductions-20260916','N20':'full-precision-20260916'}[name])
    accuracy=study.read(model_dir/'evaluation.json');timing=study.read(gpu/'timing.json')
    assert accuracy['accuracy_screen_passed'] and timing['within_runtime_target']
    assert study.read(gpu/'oracle-check.json')['passed']
    manifest=study.read(gpu/'manifest.json')
    assert manifest['candidate_sha256']==accuracy['candidate_sha256']==study.pilot.sha(model_dir/'candidate.json')
    for path,sha in manifest['files'].items():assert study.pilot.sha(study.ROOT/path)==sha,path
    arm='candidate' if name in ['N16','N20'] else min(['double','mixed'],key=lambda v:timing['median_seconds_per_iteration'][v])
    variant=timing['variant'] if name in ['N16','N20'] else arm
    return model_dir,gpu,arm,gpu/variant/'interface.cu'


def include_adapter(path,value):
    files=[study.ROOT/'tools/research/continuation_policy_transfer_optimized.py',
        original.OUT/'README.md',OUT/'README.md']
    extra={str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in files}
    if path.name=='protocol-freeze.json':value['files'].update(extra)
    elif path.name=='manifest.json':
        value['inputs'].update(extra)
        signed=study.signed({k:v for k,v in value.items() if k!='id'})
        value.clear();value.update(signed)
    return value


def adapter():
    spec=importlib.util.spec_from_file_location('_optimized_policy_transfer',original.__file__)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.OUT=OUT;module.selection=selection;module.study=SimpleNamespace(**study.__dict__)
    module.study.freeze=lambda path,value:study.freeze(path,include_adapter(path,value))
    prior_guard=module.require_idle
    def guard():
        prior_guard()
        for p in module.queue.processes():
            if p['ProcessId']!=module.os.getpid() and p['Name'].lower() in ['python.exe','pythonw.exe']:
                assert not any(t in (p['CommandLine'] or '').lower() for t in ['continuation_policy_transfer_optimized.py run',
                    'continuation_pair_reductions.py oracle','continuation_pair_reductions.py benchmark']), 'Another optimized GPU controller is active'
    module.require_idle=guard
    return module


if __name__=='__main__':getattr(adapter(),sys.argv[1])(sys.argv[2])
